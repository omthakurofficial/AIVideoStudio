"""Scene -> EffectCraft operations. The Director chooses primitives and animation steps; this module deterministically
lays them out and translates them into verified EffectCraft commands (see docs/phase4-engines.md for what was verified).

Supported rich visual primitives:
  * 2D Cartographic Map Canvas (`map_region`, `map_marker`, or `visual_type == "map"`): 2D terrain/country silhouettes,
    river corridors, lat/lon graticule grid, compass rose, scale bar, glowing 2D territory zones, and radar pins.
  * Illustrated 2D Vector Icons (`icon` & card badges): multi-shape 2D vector illustrations (rainclouds, flood waves,
    mountain peaks, warning triangles, rescue cross, city skyline, security shield, database/server racks).
  * Stock Media Picture-in-Picture Compositing: real Pexels, Pixabay, and Wikimedia Commons photos/videos composited
    onto the rendered scene with source attribution."""
from __future__ import annotations
import json, math, subprocess
from dataclasses import dataclass, field
from pathlib import Path
from ..storyboard.schema import Scene, VisualElement
from .effectcraft import EffectCraftAdapter
from .mcp_client import EngineError
from .visual_layers import render_element_sprite, render_real_map_scene_assets, render_stage_backdrop

PALETTES = {
    "clean-technical": dict(
        bg="#0b1021", stage="#121b36", card="#192549", grid="#263868", glow="#1d4ed8",
        node="#3b82f6", text="#f8fafc", muted="#94a3b8", accent="#fbbf24", line="#60a5fa",
        panel="#1e293b", shadow="#050811", land="#1b2d4f", terrain="#243b67", water="#0ea5e9",
    ),
    "dark-neon": dict(
        bg="#070712", stage="#111029", card="#19163b", grid="#2e2666", glow="#6d28d9",
        node="#8b5cf6", text="#f5f3ff", muted="#c4b5fd", accent="#00f5d4", line="#2dd4bf",
        panel="#1e1b4b", shadow="#030308", land="#1a1740", terrain="#252059", water="#06b6d4",
    ),
    "light-minimal": dict(
        bg="#f1f5f9", stage="#e2e8f0", card="#ffffff", grid="#cbd5e1", glow="#93c5fd",
        node="#2563eb", text="#0f172a", muted="#475569", accent="#f59e0b", line="#3b82f6",
        panel="#f8fafc", shadow="#cbd5e1", land="#cbd5e1", terrain="#94a3b8", water="#0284c7",
    ),
    "cloudxberry": dict(
        bg="#ffffff", stage="#f8fafc", card="#ffffff", grid="#f1f5f9", glow="#38bdf8",
        node="#ff9900", text="#0f172a", muted="#64748b", accent="#7c3aed", line="#0ea5e9",
        panel="#ffffff", shadow="#e2e8f0", land="#f1f5f9", terrain="#e2e8f0", water="#38bdf8",
    ),
    "studio-white": dict(
        bg="#ffffff", stage="#f8fafc", card="#ffffff", grid="#f1f5f9", glow="#38bdf8",
        node="#ff9900", text="#0f172a", muted="#64748b", accent="#7c3aed", line="#0ea5e9",
        panel="#ffffff", shadow="#e2e8f0", land="#f1f5f9", terrain="#e2e8f0", water="#38bdf8",
    ),
    "warm-documentary": dict(
        bg="#1a2233", stage="#222c40", card="#2d3748", grid="#3d4960", glow="#f59e0b",
        node="#ea580c", text="#fef3c7", muted="#cbd5e1", accent="#fbbf24", line="#38bdf8",
        panel="#222c40", shadow="#0a0e17", land="#27241d", terrain="#363128", water="#0284c7",
    ),
}
CONNECTOR, PACKET = ("arrow", "route"), ("packet",)
RANK_EDGES = ("connects", "flows_to", "precedes", "depends_on", "contains")


def _hex(c, default):
    if isinstance(c, str) and len(c) == 7 and c.startswith("#"):
        try:
            int(c[1:], 16)
            return c
        except ValueError:
            pass
    return default


@dataclass
class Placed:
    el: VisualElement
    x: float
    y: float
    w: float
    h: float


def layout(scene: Scene, W: int, H: int) -> tuple[dict[str, Placed], float]:
    """Returns placements (centre x,y and size in px) and the global size factor used."""
    u = min(W, H) / 1080.0
    items = [e for e in scene.visual_elements if e.kind not in CONNECTOR + PACKET]
    ids = [e.id for e in items]
    edges: list[tuple[str, str]] = []
    for r in scene.element_relationships:
        if r.kind in RANK_EDGES and r.source in ids and r.target in ids:
            edges.append((r.target, r.source) if r.kind == "depends_on" else (r.source, r.target))
    for e in scene.visual_elements:
        if e.kind in CONNECTOR:
            edges.append((e.props["from"], e.props["to"]))
    adj: dict[str, list[str]] = {i: [] for i in ids}
    for a, b in edges:
        if a in adj and b in ids and b not in adj[a]:
            adj[a].append(b)
    # break cycles via DFS, then longest-path ranks
    state: dict[str, int] = {}
    dag: dict[str, list[str]] = {i: [] for i in ids}

    def dfs(n):
        state[n] = 1
        for m in adj[n]:
            if state.get(m) == 1:
                continue
            dag[n].append(m)
            if m not in state:
                dfs(m)
        state[n] = 2

    indeg = {i: 0 for i in ids}
    for a, b in edges:
        if b in indeg and a != b:
            indeg[b] += 1
    for i in [i for i in ids if indeg[i] == 0] + ids:
        if i not in state:
            dfs(i)
    rank = {i: 0 for i in ids}
    changed = True
    for _ in range(len(ids) + 1):
        changed = False
        for a in ids:
            for b in dag[a]:
                if rank[b] < rank[a] + 1:
                    rank[b] = rank[a] + 1
                    changed = True
        if not changed:
            break
    connected = {i for a, b in edges for i in (a, b)}
    iso = [i for i in ids if i not in connected]
    maxr = max([rank[i] for i in connected], default=-1)
    for idx, i in enumerate(iso):
        rank[i] = (maxr + 1 + idx) if connected else idx
    # hints
    hint = {e.id: (e.props.get("x"), e.props.get("y")) for e in items}
    has_valid_hint = {
        e.id: all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in hint[e.id])
        for e in items
    }
    landscape = W >= H
    base_w, base_h = 250 * u, 118 * u
    top, bottom = (0.20 * H, 0.78 * H) if landscape else (0.16 * H, 0.73 * H)

    def _build_dag_layout(target_items: list[VisualElement]) -> tuple[dict[str, Placed], float]:
        nranks = (max([rank[e.id] for e in target_items], default=-1) + 1) or 1
        groups: dict[int, list[VisualElement]] = {}
        for e in target_items:
            groups.setdefault(rank[e.id], []).append(e)
        cell_main = base_w * 1.32 if landscape else base_h * 2.15
        avail_main = (W * 0.88) if landscape else (bottom - top)
        max_main = max(1, int(avail_main // cell_main))
        lines = math.ceil(nranks / max_main)
        cols = min(nranks, max_main)
        cell_w = (avail_main / max(1, cols)) if landscape else (bottom - top) / max(1, cols)
        tallest = max((len(v) for v in groups.values()), default=1)
        band = ((bottom - top) / lines) if landscape else (W * 0.88 / lines)
        cross_cell = (base_h * 1.65) if landscape else (base_w * 1.18)
        s_cross = band / (tallest * cross_cell) if tallest else 1.0
        s_main = (avail_main / cols) / cell_main
        sc = max(0.45, min(s_cross, max(1.0, min(1.32, s_main))))
        out: dict[str, Placed] = {}
        for r, els in groups.items():
            line, pos = divmod(r, max_main)
            for k, e in enumerate(els):
                n = len(els)
                pw = e.props.get("width") or e.props.get("w")
                ph = e.props.get("height") or e.props.get("h")
                if isinstance(pw, (int, float)) and isinstance(ph, (int, float)) and 0 < pw <= 1.0 and 0 < ph <= 1.0:
                    w, h = float(pw) * W, float(ph) * H
                elif e.kind == "icon":
                    w, h = 210 * u * sc, 155 * u * sc
                elif e.kind == "map_marker":
                    w, h = 120 * u * sc, 120 * u * sc
                elif e.kind == "map_region":
                    w, h = 290 * u * sc, 138 * u * sc
                elif e.kind in ("box", "card"):
                    arch = e.props.get("archetype", "").lower()
                    low = f"{e.id} {e.label}".lower()
                    if arch == "datacenter" or any(k in low for k in ("datacenter", "data center", "server rack", "facility")):
                        w, h = min(1100.0 * u, W * 0.65), min(720.0 * u, H * 0.72)
                    elif arch == "tooling_gateways" or any(k in low for k in ("gateways", "access gateway", "console cli sdk")):
                        w, h = min(1720.0 * u, W * 0.92), min(700.0 * u, H * 0.70)
                    elif arch == "comparison" or any(k in low for k in ("capex", "opex", "economics", "comparison")):
                        w, h = min(1680.0 * u, W * 0.90), min(700.0 * u, H * 0.70)
                    elif arch == "region_topology" or any(k in low for k in ("region and az", "availability zone", "anatomy of a region")):
                        w, h = min(1720.0 * u, W * 0.92), min(710.0 * u, H * 0.70)
                    else:
                        bw = min(360.0 * u * sc, cell_w * 0.82 if landscape else 360.0 * u * sc)
                        w, h = bw, 220.0 * u * sc
                elif e.kind == "service_node":
                    bw = min(340.0 * u * sc, cell_w * 0.82 if landscape else 340.0 * u * sc)
                    w, h = bw, 190.0 * u * sc
                elif e.kind == "callout":
                    arch = e.props.get("archetype", "").lower()
                    if arch == "pill" or any(k in f"{e.id} {e.label}".lower() for k in ("power", "network", "cooling", "latency", "sla")):
                        w, h = 310.0 * u, 72.0 * u
                    else:
                        lbl_len = max(len(e.label or ""), 1)
                        callout_w = max(180.0, min(420.0, lbl_len * 14.0 + 48.0))
                        w, h = callout_w * u * sc, 80 * u * sc
                elif e.kind == "title_card":
                    lbl_len = max(len(e.label or ""), 1)
                    card_w = max(320.0, min(540.0, lbl_len * 15.0 + 60.0))
                    w, h = card_w * u * sc, 110 * u * sc
                elif e.kind in ("label", "text"):
                    w, h = 280 * u * sc, 52 * u * sc
                elif e.kind == "chart_bar":
                    w, h = 76 * u * sc, (64 + 240 * float(e.props.get("value", 0.5) if isinstance(e.props.get("value", 0.5), (int, float)) else 0.5)) * u * sc
                elif e.kind == "timeline_marker":
                    w, h = 230 * u * sc, 145 * u * sc
                else:
                    w, h = (base_w * sc, base_h * sc)
                if landscape:
                    x = W * 0.06 + (W * 0.88) * (pos + 0.5) / cols
                    y = top + band * line + band * (k + 0.5) / n
                else:
                    y = top + (bottom - top) * (pos + 0.5) / cols
                    x = W * 0.06 + band * line + band * (k + 0.5) / n if lines > 1 else W * 0.06 + (W * 0.88) * (k + 0.5) / n
                out[e.id] = Placed(e, x, y, w, h)
        return out, sc

    auto = [e for e in items if not has_valid_hint[e.id]]
    placed, s = _build_dag_layout(auto if auto else items)
    if len(auto) < len(items):
        placed = dict(placed) if auto else {}
        for e in items:
            if has_valid_hint[e.id]:
                hx, hy = hint[e.id]
                pw = e.props.get("width") or e.props.get("w")
                ph = e.props.get("height") or e.props.get("h")
                if isinstance(pw, (int, float)) and isinstance(ph, (int, float)) and 0 < pw <= 1.0 and 0 < ph <= 1.0:
                    w, h = float(pw) * W, float(ph) * H
                elif e.kind == "icon":
                    w, h = 210 * u * s, 155 * u * s
                elif e.kind == "map_marker":
                    w, h = 120 * u * s, 120 * u * s
                elif e.kind == "map_region":
                    w, h = 290 * u * s, 138 * u * s
                elif e.kind in ("box", "card"):
                    arch = e.props.get("archetype", "").lower()
                    low = f"{e.id} {e.label}".lower()
                    if arch == "hierarchy_stack" or any(k in low for k in ("hierarchy", "4-tier", "blueprint", "global infrastructure overview")):
                        w, h = min(1720.0 * u, W * 0.92), min(710.0 * u, H * 0.70)
                    elif arch == "datacenter" or any(k in low for k in ("datacenter", "data center", "server rack", "facility")):
                        w, h = min(1100.0 * u, W * 0.65), min(720.0 * u, H * 0.72)
                    elif arch == "tooling_gateways" or any(k in low for k in ("gateways", "access gateway", "console cli sdk")):
                        w, h = min(1720.0 * u, W * 0.92), min(700.0 * u, H * 0.70)
                    elif arch == "comparison" or any(k in low for k in ("capex", "opex", "economics", "comparison")):
                        w, h = min(1680.0 * u, W * 0.90), min(700.0 * u, H * 0.70)
                    elif arch == "region_topology" or any(k in low for k in ("region and az", "availability zone", "anatomy of a region")):
                        w, h = min(1720.0 * u, W * 0.92), min(710.0 * u, H * 0.70)
                    elif arch == "edge_network" or any(k in low for k in ("edge locations", "points of presence", "pops", "cloudfront", "route 53", "ddos")):
                        w, h = min(1720.0 * u, W * 0.92), min(710.0 * u, H * 0.70)
                    elif arch == "hybrid_outposts" or any(k in low for k in ("hybrid edge", "outposts", "local zones", "42u rack")):
                        w, h = min(1720.0 * u, W * 0.92), min(710.0 * u, H * 0.70)
                    else:
                        w, h = 360.0 * u * s, 220.0 * u * s
                elif e.kind == "service_node":
                    w, h = 340.0 * u * s, 190.0 * u * s
                elif e.kind == "callout":
                    arch = e.props.get("archetype", "").lower()
                    if arch == "pill" or any(k in f"{e.id} {e.label}".lower() for k in ("power", "network", "cooling", "latency", "sla")):
                        w, h = 310.0 * u, 72.0 * u
                    else:
                        lbl_len = max(len(e.label or ""), 1)
                        callout_w = max(180.0, min(420.0, lbl_len * 14.0 + 48.0))
                        w, h = callout_w * u * s, 80 * u * s
                elif e.kind == "title_card":
                    lbl_len = max(len(e.label or ""), 1)
                    card_w = max(320.0, min(540.0, lbl_len * 15.0 + 60.0))
                    w, h = card_w * u * s, 110 * u * s
                elif e.kind in ("label", "text"):
                    w, h = 280 * u * s, 52 * u * s
                elif e.kind == "timeline_marker":
                    w, h = 230 * u * s, 145 * u * s
                else:
                    w, h = (base_w * s, base_h * s)
                if w >= W * 0.5 or e.props.get("archetype"):
                    x = float(hx) * W
                    y = float(hy) * H
                else:
                    pad_x = max(w * 0.52, W * 0.08)
                    pad_top = top + h * 0.52
                    pad_bot = bottom - h * 0.52
                    x = pad_x + float(hx) * max(1.0, W - 2 * pad_x)
                    y = pad_top + float(hy) * max(1.0, pad_bot - pad_top)
                placed[e.id] = Placed(e, x, y, w, h)

    # Universal collision repulsion & boundary clamping for all elements
    plist = list(placed.values())
    for _ in range(12):
        shifted = False
        for i in range(len(plist)):
            for j in range(i + 1, len(plist)):
                a, b = plist[i], plist[j]
                if a.w >= W * 0.5 or b.w >= W * 0.5 or a.el.props.get("archetype") or b.el.props.get("archetype"):
                    continue
                is_nesting = (
                    (a.el.kind in ("icon", "map_marker") and b.el.kind == "group") or
                    (b.el.kind in ("icon", "map_marker") and a.el.kind == "group")
                )
                if is_nesting:
                    continue
                min_dx = (a.w + b.w) * 0.50 + 20 * u
                min_dy = (a.h + b.h) * 0.50 + 16 * u
                dx = b.x - a.x
                dy = b.y - a.y
                if abs(dx) < min_dx and abs(dy) < min_dy:
                    if abs(dx) >= abs(dy) or abs(dx) > 1.0:
                        nudge = (min_dx - abs(dx)) * (0.55 if dx >= 0 else -0.55)
                        b.x = max(b.w * 0.52 + W * 0.04, min(W * 0.96 - b.w * 0.52, b.x + nudge))
                        a.x = max(a.w * 0.52 + W * 0.04, min(W * 0.96 - a.w * 0.52, a.x - nudge))
                    else:
                        nudge = (min_dy - abs(dy)) * (0.55 if dy >= 0 else -0.55)
                        b.y = max(top + b.h * 0.52, min(bottom - b.h * 0.52, b.y + nudge))
                        a.y = max(top + a.h * 0.52, min(bottom - a.h * 0.52, a.y - nudge))
                    shifted = True
        if not shifted:
            break
    return placed, s


class Track:
    """Keyframe track with hold semantics; avoids overlapping/zero-length segments."""
    def __init__(self, init, fps: float):
        self.keys: list[tuple[float, object]] = []
        self.init = init
        self.fps = fps

    def cur(self):
        return self.keys[-1][1] if self.keys else self.init

    def to(self, t0: float, t1: float, v):
        if not self.keys:
            self.keys.append((0.0, self.init))
        last_t = self.keys[-1][0]
        t0 = max(t0, last_t)
        t1 = max(t1, t0 + 1.0 / self.fps)
        if t0 > last_t + 1e-6:
            self.keys.append((t0, self.cur()))
        elif t0 == last_t and len(self.keys) == 1 and t0 == 0.0:
            pass
        self.keys.append((round(t1, 4), v))


@dataclass
class SceneBuild:
    steps: list[dict]
    layers: dict[str, list[str]]
    warnings: list[str]
    placements: dict


class SceneCompiler:
    def __init__(self, scene: Scene, W: int, H: int, fps: float, style: str = "clean-technical", out_dir: Path | None = None, profile: dict | None = None):
        self.scene, self.W, self.H, self.fps = scene, W, H, fps
        self.style = style
        self.out_dir = out_dir
        self.profile = profile or {}
        self.pal = PALETTES.get(style, PALETTES["clean-technical"])
        self.u = min(W, H) / 1080.0
        self.steps: list[dict] = []
        self.layers: dict[str, list[str]] = {}
        self.warn: list[str] = []
        self.tracks: dict[tuple[str, str], Track] = {}
        self.pos: dict[str, tuple[float, float]] = {}
        self.imported_pos: dict[str, tuple[float, float]] = {}
        self.map_element_layers: dict[str, dict] = {}

    # ---- helpers
    def _add(self, cmd, params):
        self.steps.append({"command": cmd, "params": params})
        return len(self.steps)

    def _own(self, eid, name):
        self.layers.setdefault(eid, []).append(name)

    def track(self, lname, prop, init):
        return self.tracks.setdefault((lname, prop), Track(init, self.fps))

    def _text(self, eid, name, text, x, y, size, color, w=None, justify="center"):
        w = w or 260 * self.u
        self._add("layer.newText", {
            "text": text, "name": name, "size": size, "fill": color,
            "justify": justify, "box": [x - w / 2, y - size * 0.72, w, size * 2.6],
        })
        self._own(eid, name)

    def _is_map_scene(self) -> bool:
        if self.scene.visual_type == "map":
            return True
        if any(e.kind in ("map_region", "map_marker") for e in self.scene.visual_elements):
            return True
        return False

    def compile(self) -> SceneBuild:
        sc, pal, u = self.scene, self.pal, self.u
        placed, s = layout(sc, self.W, self.H)
        self.placed = placed
        for eid, p in placed.items():
            self.pos[eid] = (p.x, p.y)
        els = {e.id: e for e in sc.visual_elements}
        entrance: dict[str, float] = {}
        for a in sc.animation_sequence:
            if a.action in ("appear", "fade_in", "draw", "flow", "grow", "type_text"):
                for t in a.targets:
                    entrance[t] = min(entrance.get(t, 1e9), a.at)

        has_only_disappear = bool(sc.animation_sequence) and not entrance and all(
            a.action in ("disappear", "fade_out") for a in sc.animation_sequence
        )
        owner = sc.animation_sequence[0].targets[0] if (has_only_disappear and sc.animation_sequence[0].targets) else None
        # 0) Rich ambient stage backdrop (+ Real GeoJSON/Satellite 2D Map Canvas when applicable)
        if self.out_dir is not None and self._is_map_scene():
            try:
                map_assets = render_real_map_scene_assets(sc, self.out_dir, self.W, self.H, self.style)
                mb = Path(map_assets["map_base"]).resolve()
                self._add("file.import", {"paths": [str(mb)], "addToComp": True})
                self._own(owner or "__stage", mb.name)
                self.imported_pos[mb.name] = (self.W / 2, self.H / 2)
                cp = map_assets.get("country_primary")
                if cp:
                    cp_path = Path(cp).resolve()
                    self._add("file.import", {"paths": [str(cp_path)], "addToComp": True})
                    self._own(owner or "__stage", cp_path.name)
                    self.imported_pos[cp_path.name] = (self.W / 2, self.H / 2)
                self.map_element_layers = map_assets.get("element_layers") or {}
                for eid, info in self.map_element_layers.items():
                    self.pos[eid] = (info["cx"], info["cy"])
                    if eid in placed:
                        placed[eid].x, placed[eid].y = info["cx"], info["cy"]
            except Exception as exc:
                self.warn.append(f"real map fallback: {exc}")
                self._backdrop(has_only_disappear, owner)
                self._map_board(owner or "__stage")
        elif self.out_dir is not None:
            try:
                st_png = Path(render_stage_backdrop(sc, self.out_dir, self.W, self.H, self.style)).resolve()
                self._add("file.import", {"paths": [str(st_png)], "addToComp": True})
                self._own(owner or "__stage", st_png.name)
                self.imported_pos[st_png.name] = (self.W / 2, self.H / 2)
            except Exception:
                self._backdrop(has_only_disappear, owner)
        else:
            self._backdrop(has_only_disappear, owner)
            if self._is_map_scene():
                self._map_board(owner or "__stage")
        # 1) connectors (bottom)
        for e in sc.visual_elements:
            if e.kind in CONNECTOR:
                self._connector(e, placed)
        # 2) nodes
        for e in sc.visual_elements:
            if e.kind in CONNECTOR + PACKET or e.id not in placed:
                continue
            self._node(placed[e.id], s)
        # 3) packets
        for e in sc.visual_elements:
            if e.kind in PACKET:
                nm_glow = f"{e.id}__glow"
                nm = f"{e.id}__dot"
                col = _hex(e.props.get("color"), pal["accent"])
                self._add("layer.newShape", {"kind": "ellipse", "name": nm_glow, "size": [32 * u, 32 * u], "fill": col, "position": [-100, -100]})
                self._own(e.id, nm_glow)
                self._add("layer.newShape", {"kind": "ellipse", "name": nm, "size": [16 * u, 16 * u], "fill": "#ffffff", "stroke": col, "strokeWidth": 4 * u, "position": [-100, -100]})
                self._own(e.id, nm)
        # 4) overlays
        self._overlays()
        # 5) camera rig (parenting) must precede keyframes
        rig = self._camera_rig(placed, has_only_disappear)
        # 6) animations
        for e in sc.visual_elements:
            for ln in self.layers.get(e.id, []):
                if e.id in entrance:
                    self._init_hidden(ln)
        for a in sorted(sc.animation_sequence, key=lambda x: x.at):
            self._animate(a, els)
        self._emit_tracks()
        if rig is not None:
            self._camera_keys(rig)
        return SceneBuild(
            self.steps, self.layers, self.warn,
            {k: [round(v.x), round(v.y), round(v.w), round(v.h)] for k, v in placed.items()},
        )

    def _backdrop(self, tie_to_disappear: bool, disappear_target: str | None):
        pal, u, W, H = self.pal, self.u, self.W, self.H
        owner = disappear_target if (tie_to_disappear and disappear_target) else "__stage"
        landscape = W >= H
        stage_w = W * (0.91 if landscape else 0.90)
        stage_h = H * (0.61 if landscape else 0.59)
        stage_cy = H * (0.49 if landscape else 0.445)

        g1 = "bg__glow1"
        self._add("layer.newShape", {"kind": "ellipse", "name": g1, "size": [W * 0.52, H * 0.52], "fill": pal["glow"], "position": [W * 0.22, H * 0.34]})
        self.track(g1, "transform/opacity", 14.0)
        self._own(owner, g1)

        g2 = "bg__glow2"
        self._add("layer.newShape", {"kind": "ellipse", "name": g2, "size": [W * 0.46, H * 0.46], "fill": pal["accent"], "position": [W * 0.78, H * 0.68]})
        self.track(g2, "transform/opacity", 9.0)
        self._own(owner, g2)

        st_shadow = "bg__stage_shadow"
        self._add("layer.newShape", {"kind": "rounded", "name": st_shadow, "size": [stage_w, stage_h], "fill": pal["shadow"], "position": [W / 2 + 8 * u, stage_cy + 10 * u]})
        self.track(st_shadow, "transform/opacity", 48.0)
        self._own(owner, st_shadow)

        st = "bg__stage"
        self._add("layer.newShape", {
            "kind": "rounded", "name": st, "size": [stage_w, stage_h],
            "fill": pal["stage"], "stroke": pal["grid"], "strokeWidth": 2.5 * u,
            "position": [W / 2, stage_cy],
        })
        self.track(st, "transform/opacity", 82.0)
        self._own(owner, st)

        for idx, frac in enumerate((-0.18, 0.18), 1):
            gl = f"bg__grid_{idx}"
            self._add("layer.newShape", {
                "kind": "rect", "name": gl, "size": [stage_w * 0.92, max(1.5, 1.8 * u)],
                "fill": pal["grid"], "position": [W / 2, stage_cy + stage_h * frac],
            })
            self.track(gl, "transform/opacity", 28.0)
            self._own(owner, gl)

    def _map_board(self, owner: str):
        """Render a 2D cartographic map canvas with lat/lon grid, 2D country/terrain zones, river basins, compass rose, and scale bar."""
        pal, u, W, H = self.pal, self.u, self.W, self.H
        landscape = W >= H
        stage_w = W * (0.91 if landscape else 0.90)
        stage_h = H * (0.61 if landscape else 0.59)
        cx, cy = W / 2, H * (0.49 if landscape else 0.445)

        # Vertical meridian lines for 2D map graticule
        for idx, frac in enumerate((-0.30, -0.10, 0.10, 0.30), 1):
            ml = f"map__meridian_{idx}"
            self._add("layer.newShape", {
                "kind": "rect", "name": ml, "size": [max(1.5, 1.6 * u), stage_h * 0.90],
                "fill": pal["grid"], "position": [cx + stage_w * frac, cy],
            })
            self.track(ml, "transform/opacity", 24.0)
            self._own(owner, ml)

        # 2D Country / Basin Silhouette (elongated Himalayan-to-Terai stepped polygon approximation)
        land_outer = "map__land_outer"
        self._add("layer.newShape", {
            "kind": "rounded", "name": land_outer,
            "size": [stage_w * 0.78, stage_h * 0.64],
            "fill": pal.get("land", "#1b2d4f"), "stroke": pal["line"], "strokeWidth": 2.5 * u,
            "position": [cx, cy + stage_h * 0.02],
        })
        self._add("prop.set", {"layer": land_outer, "path": "transform/rotation", "value": -6.0})
        self.track(land_outer, "transform/opacity", 48.0)
        self._own(owner, land_outer)

        # High Himalayan Ridge Zone (North belt)
        ridge = "map__himalaya_belt"
        self._add("layer.newShape", {
            "kind": "rounded", "name": ridge,
            "size": [stage_w * 0.74, stage_h * 0.22],
            "fill": pal.get("terrain", "#243b67"), "stroke": "#93c5fd", "strokeWidth": 1.8 * u,
            "position": [cx + stage_w * 0.01, cy - stage_h * 0.16],
        })
        self._add("prop.set", {"layer": ridge, "path": "transform/rotation", "value": -6.0})
        self.track(ridge, "transform/opacity", 42.0)
        self._own(owner, ridge)

        # Middle Hills & Valley Basin Contour
        basin = "map__valley_contour"
        self._add("layer.newShape", {
            "kind": "ellipse", "name": basin,
            "size": [stage_w * 0.44, stage_h * 0.34],
            "fill": pal.get("terrain", "#243b67"), "stroke": pal["accent"], "strokeWidth": 2.0 * u,
            "position": [cx - stage_w * 0.02, cy + stage_h * 0.02],
        })
        self.track(basin, "transform/opacity", 32.0)
        self._own(owner, basin)

        # 2D River Corridors (Bagmati / Koshi / Narayani hydrographic channels)
        rivers = [
            ("map__river_main", cx - stage_w * 0.14, cy - stage_h * 0.12, stage_w * 0.34, 6.5 * u, 28.0),
            ("map__river_east", cx + stage_w * 0.12, cy - stage_h * 0.08, stage_w * 0.32, 7.5 * u, 36.0),
            ("map__river_south", cx + stage_w * 0.02, cy + stage_h * 0.16, stage_w * 0.48, 8.0 * u, -4.0),
        ]
        for rname, rx, ry, rlen, rth, rang in rivers:
            self._add("layer.newShape", {
                "kind": "rounded", "name": rname, "size": [rlen, rth],
                "fill": pal.get("water", "#0ea5e9"), "position": [rx, ry],
            })
            self._add("prop.set", {"layer": rname, "path": "transform/rotation", "value": rang})
            self.track(rname, "transform/opacity", 44.0)
            self._own(owner, rname)

        # Compass Rose (Top-Right of 2D Map Stage)
        comp_x = cx + stage_w * 0.41
        comp_y = cy - stage_h * 0.38
        comp_ring = "map__compass_ring"
        self._add("layer.newShape", {
            "kind": "ellipse", "name": comp_ring, "size": [54 * u, 54 * u],
            "fill": pal["card"], "stroke": pal["accent"], "strokeWidth": 2.2 * u,
            "position": [comp_x, comp_y],
        })
        self.track(comp_ring, "transform/opacity", 88.0)
        self._own(owner, comp_ring)
        self._text(owner, "map__compass_n", "N ▲", comp_x, comp_y + 3 * u, 16 * u, pal["accent"], w=50 * u)

        # 2D Map Scale Bar & Coordinate Tag (Bottom-Left of Map Stage)
        sc_x = cx - stage_w * 0.36
        sc_y = cy + stage_h * 0.42
        sc_bar = "map__scale_bar"
        self._add("layer.newShape", {
            "kind": "rect", "name": sc_bar, "size": [110 * u, 4 * u],
            "fill": pal["text"], "position": [sc_x, sc_y],
        })
        self.track(sc_bar, "transform/opacity", 75.0)
        self._own(owner, sc_bar)
        self._text(owner, "map__scale_txt", "2D CARTOGRAPHIC VIEW  •  100 KM", sc_x + 70 * u, sc_y - 14 * u, 13 * u, pal["muted"], w=280 * u)

    def _draw_vector_icon(self, eid: str, label: str, icon_hint: str, cx: float, cy: float, r: float, accent_col: str):
        """Draw multi-shape 2D SVG-style vector illustrations inside icon badges."""
        u = self.u
        key = f"{label} {icon_hint} {eid}".lower()

        if any(w in key for w in ("rain", "cloud", "monsoon", "storm", "weather")):
            # Cloud + 3 raindrops
            c1 = f"{eid}__vec_cloud"
            self._add("layer.newShape", {"kind": "rounded", "name": c1, "size": [r * 1.15, r * 0.56], "fill": "#ffffff", "position": [cx, cy - r * 0.12]})
            self._own(eid, c1)
            for idx, dx in enumerate((-0.28, 0.0, 0.28), 1):
                dr = f"{eid}__vec_drop{idx}"
                self._add("layer.newShape", {"kind": "ellipse", "name": dr, "size": [r * 0.16, r * 0.30], "fill": "#38bdf8", "position": [cx + r * dx, cy + r * 0.34]})
                self._own(eid, dr)
            return True

        if any(w in key for w in ("flood", "river", "water", "koshi", "bagmati", "inundat", "surge", "wave", "dam", "barrage")):
            # 3 layered flood waves
            for idx, (dy, col) in enumerate(((-0.22, "#bae6fd"), (0.04, "#38bdf8"), (0.30, "#0284c7")), 1):
                wv = f"{eid}__vec_wave{idx}"
                self._add("layer.newShape", {"kind": "rounded", "name": wv, "size": [r * 1.18, r * 0.20], "fill": col, "position": [cx, cy + r * dy]})
                self._own(eid, wv)
            return True

        if any(w in key for w in ("mountain", "himalaya", "nepal", "slope", "landslide", "terrain", "valley", "ridge")):
            # Twin mountain peaks (rotated squares)
            p1 = f"{eid}__vec_peak1"
            self._add("layer.newShape", {"kind": "rect", "name": p1, "size": [r * 0.72, r * 0.72], "fill": "#e2e8f0", "position": [cx - r * 0.16, cy + r * 0.12]})
            self._add("prop.set", {"layer": p1, "path": "transform/rotation", "value": 45.0})
            self._own(eid, p1)
            p2 = f"{eid}__vec_peak2"
            self._add("layer.newShape", {"kind": "rect", "name": p2, "size": [r * 0.56, r * 0.56], "fill": "#94a3b8", "position": [cx + r * 0.24, cy + r * 0.20]})
            self._add("prop.set", {"layer": p2, "path": "transform/rotation", "value": 45.0})
            self._own(eid, p2)
            return True

        if any(w in key for w in ("rescue", "relief", "hospital", "medical", "aid", "helicopter", "emergency", "life")):
            # Emergency rescue cross
            h_bar = f"{eid}__vec_cross_h"
            v_bar = f"{eid}__vec_cross_v"
            self._add("layer.newShape", {"kind": "rounded", "name": h_bar, "size": [r * 0.96, r * 0.30], "fill": "#ffffff", "position": [cx, cy]})
            self._own(eid, h_bar)
            self._add("layer.newShape", {"kind": "rounded", "name": v_bar, "size": [r * 0.30, r * 0.96], "fill": "#ffffff", "position": [cx, cy]})
            self._own(eid, v_bar)
            return True

        if any(w in key for w in ("alert", "warn", "danger", "hazard", "damage", "loss", "crisis", "risk")):
            # Hazard diamond + exclamation bar
            dm = f"{eid}__vec_ warn_dm"
            self._add("layer.newShape", {"kind": "rect", "name": dm, "size": [r * 0.82, r * 0.82], "fill": "#fbbf24", "position": [cx, cy]})
            self._add("prop.set", {"layer": dm, "path": "transform/rotation", "value": 45.0})
            self._own(eid, dm)
            ex = f"{eid}__vec_warn_ex"
            self._add("layer.newShape", {"kind": "rect", "name": ex, "size": [r * 0.16, r * 0.46], "fill": "#0f172a", "position": [cx, cy - r * 0.06]})
            self._own(eid, ex)
            return True

        if any(w in key for w in ("city", "kathmandu", "capital", "home", "house", "building", "road", "bridge", "urban")):
            # 3 urban skyline towers
            for idx, (dx, bh) in enumerate(((-0.28, 0.56), (0.0, 0.88), (0.28, 0.68)), 1):
                tw = f"{eid}__vec_bldg{idx}"
                self._add("layer.newShape", {"kind": "rect", "name": tw, "size": [r * 0.24, r * bh], "fill": "#ffffff", "position": [cx + r * dx, cy + r * (0.44 - bh / 2)]})
                self._own(eid, tw)
            return True

        if any(w in key for w in ("shield", "tls", "mtls", "security", "auth", "policy", "zero_trust", "cert")):
            sh1 = f"{eid}__vec_shield_o"
            sh2 = f"{eid}__vec_shield_i"
            self._add("layer.newShape", {"kind": "rounded", "name": sh1, "size": [r * 0.84, r * 0.98], "fill": "#ffffff", "position": [cx, cy]})
            self._own(eid, sh1)
            self._add("layer.newShape", {"kind": "rounded", "name": sh2, "size": [r * 0.52, r * 0.64], "fill": accent_col, "position": [cx, cy]})
            self._own(eid, sh2)
            return True

        if any(w in key for w in ("server", "db", "database", "cluster", "kube", "pod", "vector", "cache", "storage")):
            for idx, dy in enumerate((-0.26, 0.0, 0.26), 1):
                rk = f"{eid}__vec_rack{idx}"
                self._add("layer.newShape", {"kind": "rounded", "name": rk, "size": [r * 0.94, r * 0.20], "fill": "#ffffff", "position": [cx, cy + r * dy]})
                self._own(eid, rk)
            return True

        return False

    def _init_hidden(self, ln):
        t = self.tracks.setdefault((ln, "transform/opacity"), Track(0.0, self.fps))
        t.init = 0.0
        if not t.keys:
            t.keys.append((0.0, 0.0))

    # ---- primitives
    def _node(self, p: Placed, s: float):
        e, pal, u = p.el, self.pal, self.u
        color = _hex(e.props.get("color"), pal["node"])
        lab = e.label or e.id.replace("_", " ")
        fs = max(14, 24 * u * s)

        if e.id in self.map_element_layers:
            info = self.map_element_layers[e.id]
            mp_path = Path(info["path"]).resolve()
            self._add("file.import", {"paths": [str(mp_path)], "addToComp": True})
            self._own(e.id, mp_path.name)
            self.imported_pos[mp_path.name] = (self.W / 2, self.H / 2)
            return

        is_box_card = e.kind == "box" and e.id != "timeline_base" and "timeline" not in e.id
        can_be_sprite = (e.kind not in ("chart_bar", "group", "map_region", "map_marker", "label", "text")) and (e.kind != "box" or is_box_card)
        if self.out_dir is not None and can_be_sprite:
            try:
                sp_path = Path(render_element_sprite(e, p.w, p.h, u, self.style, self.out_dir)).resolve()
                self._add("file.import", {"paths": [str(sp_path)], "addToComp": True})
                self._add("prop.set", {"layer": sp_path.name, "path": "transform/position", "value": [p.x, p.y, 0.0]})
                self._own(e.id, sp_path.name)
                self.imported_pos[sp_path.name] = (p.x, p.y)
                return
            except Exception as exc:
                self.warn.append(f"sprite fallback for {e.id}: {exc}")

        if e.id == "timeline_base" or "timeline_track" in e.id or (e.kind == "box" and "timeline" in e.id):
            # Crisp sleek horizontal timeline axis rail
            rail_h = max(4.0, 6.0 * u)
            rail = f"{e.id}__rail"
            self._add("layer.newShape", {
                "kind": "rounded", "name": rail, "size": [p.w, rail_h],
                "fill": pal.get("grid", "#3d4960"), "stroke": pal.get("accent", "#fbbf24"), "strokeWidth": 1.5 * u,
                "position": [p.x, p.y],
            })
            self._own(e.id, rail)
            return

        if e.kind == "map_region":
            # 2D Cartographic Flood/Territory Polygon Zone
            zone_glow = f"{e.id}__glow"
            self._add("layer.newShape", {
                "kind": "ellipse", "name": zone_glow, "size": [p.w * 1.24, p.h * 1.24],
                "fill": color, "position": [p.x, p.y],
            })
            self.track(zone_glow, "transform/opacity", 28.0)
            self._own(e.id, zone_glow)

            zone_poly = f"{e.id}__shape"
            self._add("layer.newShape", {
                "kind": "rounded", "name": zone_poly, "size": [p.w, p.h],
                "fill": color, "stroke": "#ffffff", "strokeWidth": 3 * u,
                "position": [p.x, p.y],
            })
            self.track(zone_poly, "transform/opacity", 62.0)
            self._own(e.id, zone_poly)

            # Inner contour ring
            inner = f"{e.id}__ring"
            self._add("layer.newShape", {
                "kind": "ellipse", "name": inner, "size": [p.w * 0.72, p.h * 0.62],
                "fill": False, "stroke": pal["accent"], "strokeWidth": 2.2 * u,
                "position": [p.x, p.y],
            })
            self._own(e.id, inner)

            tag = str(e.props.get("subtitle") or "2D MAP ZONE").upper()[:20]
            self._text(e.id, f"{e.id}__sub", tag, p.x, p.y - p.h * 0.16, max(11, fs * 0.56), "#ffffff", w=p.w * 0.90)
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + p.h * 0.12, fs * 0.92, "#ffffff", w=p.w * 0.92)
            return

        if e.kind == "map_marker":
            # 2D Cartographic Radar Pin + Concentric Ripple Rings
            r_outer = f"{e.id}__glow"
            self._add("layer.newShape", {
                "kind": "ellipse", "name": r_outer, "size": [p.w * 1.48, p.w * 1.48],
                "fill": False, "stroke": color, "strokeWidth": 2.5 * u, "position": [p.x, p.y],
            })
            self.track(r_outer, "transform/opacity", 45.0)
            self._own(e.id, r_outer)

            r_mid = f"{e.id}__ring"
            self._add("layer.newShape", {
                "kind": "ellipse", "name": r_mid, "size": [p.w * 1.15, p.w * 1.15],
                "fill": False, "stroke": pal["accent"], "strokeWidth": 3 * u, "position": [p.x, p.y],
            })
            self._own(e.id, r_mid)

            pin = f"{e.id}__badge"
            self._add("layer.newShape", {
                "kind": "ellipse", "name": pin, "size": [p.w * 0.76, p.w * 0.76],
                "fill": color, "stroke": "#ffffff", "strokeWidth": 3 * u, "position": [p.x, p.y],
            })
            self._own(e.id, pin)

            core = f"{e.id}__core"
            self._add("layer.newShape", {
                "kind": "ellipse", "name": core, "size": [p.w * 0.28, p.w * 0.28],
                "fill": "#ffffff", "position": [p.x, p.y],
            })
            self._own(e.id, core)

            pill_w = min(max(p.w * 2.2, len(lab) * fs * 0.58 + 32 * u), p.w * 2.8)
            pill_h = max(30 * u, fs * 1.55)
            pill_y = p.y + p.w * 0.58 + pill_h * 0.52
            pill = f"{e.id}__pill"
            self._add("layer.newShape", {
                "kind": "rounded", "name": pill, "size": [pill_w, pill_h],
                "fill": pal["card"], "stroke": pal["accent"], "strokeWidth": 2.2 * u, "position": [p.x, pill_y],
            })
            self._own(e.id, pill)
            self._text(e.id, f"{e.id}__lab", lab, p.x, pill_y + fs * 0.12, fs * 0.86, pal["text"], w=pill_w * 0.94)
            return

        if e.kind == "icon":
            mono = (str(e.props.get("icon") or lab)[:2]).upper()
            sh = f"{e.id}__shadow"
            self._add("layer.newShape", {"kind": "ellipse", "name": sh, "size": [p.w * 1.06, p.w * 1.06], "fill": pal["shadow"], "position": [p.x + 5 * u, p.y + 7 * u]})
            self._own(e.id, sh)

            ring = f"{e.id}__ring"
            self._add("layer.newShape", {"kind": "ellipse", "name": ring, "size": [p.w * 1.18, p.w * 1.18], "fill": False, "stroke": color, "strokeWidth": 3 * u, "position": [p.x, p.y]})
            self._own(e.id, ring)

            name = f"{e.id}__badge"
            self._add("layer.newShape", {"kind": "ellipse", "name": name, "size": [p.w, p.w], "fill": color, "stroke": "#ffffff", "strokeWidth": 2.5 * u, "position": [p.x, p.y]})
            self._own(e.id, name)

            drew_vec = self._draw_vector_icon(e.id, lab, str(e.props.get("icon") or ""), p.x, p.y, p.w * 0.46, color)
            if not drew_vec:
                self._text(e.id, f"{e.id}__mono", mono, p.x, p.y + fs * 0.14, max(13, p.w * 0.35), "#ffffff", w=p.w)

            pill_w = min(max(p.w * 2.1, len(lab) * fs * 0.58 + 28 * u), p.w * 2.7)
            pill_h = max(28 * u, fs * 1.55)
            pill_y = p.y + p.w * 0.58 + pill_h * 0.52
            pill = f"{e.id}__pill"
            self._add("layer.newShape", {"kind": "rounded", "name": pill, "size": [pill_w, pill_h], "fill": pal["card"], "stroke": color, "strokeWidth": 2 * u, "position": [p.x, pill_y]})
            self._own(e.id, pill)
            self._text(e.id, f"{e.id}__lab", lab, p.x, pill_y + fs * 0.12, fs * 0.86, pal["text"], w=pill_w * 0.94)

        elif e.kind in ("label", "text"):
            pill = f"{e.id}__pill"
            self._add("layer.newShape", {"kind": "rounded", "name": pill, "size": [p.w, p.h], "fill": pal["card"], "stroke": pal["grid"], "strokeWidth": 2 * u, "position": [p.x, p.y]})
            self._own(e.id, pill)
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + fs * 0.12, fs * 1.0, _hex(e.props.get("color"), pal["text"]), w=p.w * 0.92)

        elif e.kind == "chart_bar":
            track_bg = f"{e.id}__track"
            self._add("layer.newShape", {"kind": "rounded", "name": track_bg, "size": [p.w * 1.16, p.h + 16 * u], "fill": pal["card"], "stroke": pal["grid"], "strokeWidth": 2 * u, "position": [p.x, p.y]})
            self._own(e.id, track_bg)

            name = f"{e.id}__bar"
            self._add("layer.newShape", {"kind": "rect", "name": name, "size": [p.w, p.h], "fill": color, "position": [p.x, p.y + p.h / 2]})
            self._add("prop.set", {"layer": name, "path": "contents/group/contents/rect/position", "value": [0, -p.h / 2]})
            self._own(e.id, name)

            val_raw = e.props.get("value", "")
            if isinstance(val_raw, (int, float)):
                pct = f"{int(round(val_raw * 100))}%" if val_raw <= 1.0 else str(val_raw)
                self._text(e.id, f"{e.id}__val", pct, p.x, p.y - p.h / 2 - fs * 0.9, fs * 0.82, pal["accent"], w=p.w * 2.5)
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + p.h / 2 + fs * 1.15, fs * 0.88, pal["text"], w=p.w * 3.0)

        else:
            outline = e.kind in ("box", "group")
            shape = {"rect": "rect", "circle": "ellipse"}.get(str(e.props.get("shape")), "rounded")
            sz = [p.w, p.h] if shape != "ellipse" else [p.h, p.h]

            sh = f"{e.id}__shadow"
            self._add("layer.newShape", {"kind": shape, "name": sh, "size": sz, "fill": pal["shadow"], "position": [p.x + 6 * u, p.y + 8 * u]})
            self._own(e.id, sh)

            name = f"{e.id}__shape"
            prm = {"kind": shape, "name": name, "size": sz, "position": [p.x, p.y]}
            if outline:
                prm.update({"fill": pal["stage"], "stroke": color, "strokeWidth": 4 * u})
            elif e.kind == "callout":
                prm.update({"fill": pal["card"], "stroke": pal["accent"], "strokeWidth": 3.5 * u})
            else:
                prm.update({"fill": pal["card"], "stroke": color, "strokeWidth": 3.5 * u})
            self._add("layer.newShape", prm)
            self._own(e.id, name)

            if outline:
                box_lab = (e.label or "").strip() or e.id.replace("_", " ").title()
                if box_lab and e.id != "timeline_base" and p.h >= 80 * u:
                    hbar = f"{e.id}__hbar"
                    bar_h = max(34 * u, p.h * 0.20)
                    self._add("layer.newShape", {
                        "kind": "rounded", "name": hbar,
                        "size": [p.w - 6 * u, bar_h],
                        "fill": color,
                        "position": [p.x, p.y - p.h / 2 + bar_h / 2 + 3 * u],
                    })
                    self._own(e.id, hbar)
                    self._text(e.id, f"{e.id}__lab", box_lab.upper()[:24], p.x, p.y - p.h / 2 + bar_h * 0.58, max(13, fs * 0.76), "#ffffff", w=p.w * 0.90)
            elif shape != "ellipse":
                hbar = f"{e.id}__hbar"
                bar_h = max(8 * u, p.h * 0.14)
                self._add("layer.newShape", {
                    "kind": "rounded", "name": hbar,
                    "size": [p.w - 14 * u, bar_h],
                    "fill": pal["accent"] if e.kind == "callout" else color,
                    "position": [p.x, p.y - p.h / 2 + bar_h * 0.85],
                })
                self._own(e.id, hbar)

                badge_d = min(p.h * 0.42, 42 * u)
                bx = p.x - p.w * 0.34
                by = p.y + p.h * 0.06
                bdg = f"{e.id}__badge"
                self._add("layer.newShape", {
                    "kind": "ellipse", "name": bdg, "size": [badge_d, badge_d],
                    "fill": color, "position": [bx, by],
                })
                self._own(e.id, bdg)
                drew_vec = self._draw_vector_icon(e.id, lab, str(e.props.get("icon") or ""), bx, by, badge_d * 0.46, color)
                if not drew_vec:
                    mono = (str(e.props.get("icon") or lab)[:2]).upper()
                    self._text(e.id, f"{e.id}__mono", mono, bx, by + badge_d * 0.08, max(11, badge_d * 0.40), "#ffffff", w=badge_d * 1.2)

                kind_tag = str(e.props.get("subtitle") or e.kind.replace("_", " ")).upper()[:18]
                tx = p.x + p.w * 0.08
                tw = p.w * 0.72
                self._text(e.id, f"{e.id}__sub", kind_tag, tx, p.y - p.h * 0.11, max(10, fs * 0.52), pal["muted"], w=tw)
                self._text(e.id, f"{e.id}__lab", lab, tx, p.y + p.h * 0.16, fs * 0.88, pal["text"], w=tw)
            else:
                self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + fs * 0.15, fs * 0.92, pal["text"], w=p.w * 0.90)

    def _endpoints(self, a: str, b: str):
        (ax, ay), (bx, by) = self.pos[a], self.pos[b]
        pa, pb = self.placed[a], self.placed[b]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1.0

        def clip(pl, sign):
            hw, hh = pl.w / 2 + 10 * self.u, (pl.h / 2 + 10 * self.u)
            if pl.el.kind in ("icon", "map_marker"):
                hw = pl.w / 2 + 12 * self.u
                hh = (pl.w / 2 + 40 * self.u) if (sign * dy > 0) else (pl.w / 2 + 12 * self.u)
            tx = hw / abs(dx) * d if dx else 1e9
            ty = hh / abs(dy) * d if dy else 1e9
            return min(tx, ty)

        ca, cb = clip(pa, 1), clip(pb, -1)
        sx, sy = ax + dx / d * ca, ay + dy / d * ca
        ex, ey = bx - dx / d * cb, by - dy / d * cb
        return (sx, sy), (ex, ey)

    def _connector(self, e: VisualElement, placed):
        f, t = e.props["from"], e.props["to"]
        if f not in placed or t not in placed:
            self.warn.append(f"connector '{e.id}' skipped: endpoint not placed")
            return
        (sx, sy), (ex, ey) = self._endpoints(f, t)
        L = math.hypot(ex - sx, ey - sy)
        ang = math.degrees(math.atan2(ey - sy, ex - sx))
        th = 5.5 * self.u
        col = _hex(e.props.get("color"), self.pal["line"])
        if e.props.get("style") == "dashed":
            self.warn.append(f"connector '{e.id}': dashed style drawn as solid line")

        seg_len = max(L - 6 * self.u, 2)
        glow, ln, hd = f"{e.id}__glow", f"{e.id}__line", f"{e.id}__head"
        self._add("layer.newShape", {"kind": "rect", "name": glow, "size": [seg_len, th * 2.2], "fill": self.pal["glow"], "position": [sx, sy]})
        self._add("prop.set", {"layer": glow, "path": "contents/group/contents/rect/position", "value": [seg_len / 2, 0]})
        self._add("prop.set", {"layer": glow, "path": "transform/rotation", "value": ang})
        self._own(e.id, glow)

        self._add("layer.newShape", {"kind": "rect", "name": ln, "size": [seg_len, th], "fill": col, "position": [sx, sy]})
        self._add("prop.set", {"layer": ln, "path": "contents/group/contents/rect/position", "value": [seg_len / 2, 0]})
        self._add("prop.set", {"layer": ln, "path": "transform/rotation", "value": ang})
        self._own(e.id, ln)

        pa_dot = f"{e.id}__porta"
        self._add("layer.newShape", {"kind": "ellipse", "name": pa_dot, "size": [11 * self.u, 11 * self.u], "fill": self.pal["accent"], "position": [sx, sy]})
        self._own(e.id, pa_dot)

        self._add("layer.newShape", {"kind": "rect", "name": hd, "size": [17 * self.u, 17 * self.u], "fill": self.pal["accent"], "position": [ex, ey]})
        self._add("prop.set", {"layer": hd, "path": "transform/rotation", "value": ang + 45})
        self._own(e.id, hd)

        pulse = f"{e.id}__pulse"
        self._add("layer.newShape", {"kind": "ellipse", "name": pulse, "size": [14 * self.u, 14 * self.u], "fill": "#ffffff", "stroke": self.pal["accent"], "strokeWidth": 3 * self.u, "position": [sx, sy]})
        self._own(e.id, pulse)

        self.route = getattr(self, "route", {})
        self.route[e.id] = ((sx, sy), (ex, ey))

    def _overlays(self):
        pal, u = self.pal, self.u
        active: list[tuple[float, float]] = []
        for i, t in enumerate(self.scene.on_screen_text):
            # If a visual_element title_card already renders this exact headline text, skip duplicate OST banner
            if any(e.kind == "title_card" and (e.label or "").strip().lower() == t.text.strip().lower() for e in self.scene.visual_elements):
                continue
            slot = sum(1 for (a, b) in active if a < t.at + t.duration and t.at < b)
            active.append((t.at, t.at + t.duration))
            eid = f"ost{i}"
            bg_nm = f"ost{i}__bg"
            nm = f"ost{i}__txt"
            y = 0.075 * self.H + slot * 68 * u
            fs = 31 * u if self.W >= self.H else 27 * u
            pill_w = min(self.W * 0.92, max(380 * u, len(t.text) * fs * 0.68 + 96 * u))
            pill_h = max(54 * u, fs * 1.85)
            self._add("layer.newShape", {
                "kind": "rounded", "name": bg_nm, "size": [pill_w, pill_h],
                "fill": pal["card"], "stroke": pal["accent"], "strokeWidth": 2.5 * u,
                "position": [self.W / 2, y],
            })
            self._own(eid, bg_nm)
            self._text(eid, nm, t.text, self.W / 2, y + fs * 0.12, fs, pal["text"], w=pill_w * 0.96)
            for layer_nm, max_op in ((bg_nm, 94.0), (nm, 100.0)):
                tr = self.track(layer_nm, "transform/opacity", 0.0)
                if not tr.keys:
                    tr.keys.append((0.0, 0.0))
                tr.to(t.at, t.at + 0.25, max_op)
                tr.to(max(t.at + 0.25, t.at + t.duration - 0.25), t.at + t.duration, 0.0)

    # ---- animation
    def _animate(self, a, els):
        d = max(a.duration, 1 / self.fps)
        t0, t1 = a.at, a.at + d
        for tid in a.targets:
            lays = self.layers.get(tid, [])
            if not lays:
                self.warn.append(f"animation {a.id}: target '{tid}' has no drawable layers")
                continue
            kind = els[tid].kind if tid in els else "node"
            for ln in lays:
                op = lambda: self.track(ln, "transform/opacity", 100.0)
                sc = lambda: self.track(ln, "transform/scale", [100.0, 100.0, 100.0])
                if a.action in ("appear", "fade_in"):
                    target_op = 45.0 if ln.endswith("__glow") else (60.0 if ln.endswith("__shadow") else (65.0 if (kind == "map_region" and ln.endswith("__shape")) else 100.0))
                    op().to(t0, t0 + (0.06 if a.action == "appear" else min(0.35, d)), target_op)
                    if ln.endswith(("__shape", "__badge", "__ring")) or ln.startswith(("sprite_", "map_el_")):
                        pop_tr = self.track(ln, "transform/scale", [82.0, 82.0, 100.0] if ln.startswith("map_el_") else [78.0, 78.0, 100.0])
                        t_mid = round(t0 + max(0.08, d * 0.65), 4)
                        pop_tr.to(t0, t_mid, [103.0, 103.0, 100.0] if ln.startswith("map_el_") else [105.0, 105.0, 100.0])
                        pop_tr.to(t_mid, max(t_mid + 0.05, t1), [100.0, 100.0, 100.0])
                elif a.action in ("disappear", "fade_out"):
                    op().to(t0, t0 + (0.05 if a.action == "disappear" else d), 0.0)
                elif a.action == "type_text":
                    op().to(t0, t1, 100.0)
                    self.warn.append(f"animation {a.id}: type_text rendered as fade-in")
                elif a.action == "draw":
                    if kind in CONNECTOR:
                        if ln.endswith(("__line", "__glow")):
                            op().to(t0, t0 + 0.001, 35.0 if ln.endswith("__glow") else 100.0)
                            self.track(ln, "transform/scale", [0.0, 100.0, 100.0]).to(t0, t1, [100.0, 100.0, 100.0])
                        elif ln.endswith("__porta"):
                            op().to(t0, min(t1, t0 + 0.12), 100.0)
                        elif ln.endswith("__pulse"):
                            rt = getattr(self, "route", {}).get(tid)
                            if rt:
                                (sx, sy), (ex, ey) = rt
                                p_start = round(min(t1, t0 + d * 0.35), 3)
                                p_end = round(min(self.scene.duration - 0.05, p_start + max(0.45, d * 0.9)), 3)
                                if p_end > p_start + 0.1:
                                    pos = self.track(ln, "transform/position", [sx, sy, 0.0])
                                    pos.to(p_start, p_end, [ex, ey, 0.0])
                                    op().to(p_start, p_start + 0.02, 100.0)
                                    op().to(max(p_start + 0.05, p_end - 0.05), p_end, 0.0)
                        else:
                            op().to(max(t0, t1 - 0.15), t1, 100.0)
                    else:
                        op().to(t0, t1, 100.0)
                        self.warn.append(f"animation {a.id}: draw on a non-connector '{tid}' rendered as fade-in")
                elif a.action in ("highlight", "pulse"):
                    cyc = 2 if a.action == "pulse" else 1
                    amp = 114.0 if a.action == "highlight" else 108.0
                    for k in range(cyc):
                        s0 = t0 + d * k / cyc
                        s1 = t0 + d * (k + 1) / cyc
                        sc().to(s0, (s0 + s1) / 2, [amp, amp, 100.0])
                        sc().to((s0 + s1) / 2, s1, [100.0, 100.0, 100.0])
                elif a.action == "scale":
                    f = float(a.params.get("factor", 1.2)) * 100
                    sc().to(t0, t1, [f, f, 100.0])
                elif a.action == "grow":
                    op().to(t0, t0 + 0.05, 100.0)
                    if kind == "chart_bar" and ln.endswith("__bar"):
                        self.track(ln, "transform/scale", [100.0, 0.0, 100.0]).to(t0, t1, [100.0, 100.0, 100.0])
                elif a.action == "move":
                    x = a.params.get("x")
                    y = a.params.get("y")
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        px, py = self._base_pos(ln)
                        self.track(ln, "transform/position", [px, py, 0.0]).to(
                            t0, t1,
                            [x * self.W + (px - self.pos.get(tid, (px, py))[0]), y * self.H + (py - self.pos.get(tid, (px, py))[1]), 0.0],
                        )
                    else:
                        self.warn.append(f"animation {a.id}: move needs numeric params x,y (fractions of frame)")
                elif a.action == "flow":
                    self._flow(a, tid, lays, t0, t1)
                    break

    def _base_pos(self, ln):
        if ln in self.imported_pos:
            return self.imported_pos[ln]
        for st in self.steps:
            p = st["params"]
            if p.get("name") == ln and "position" in p:
                return tuple(p["position"])
        return (0.0, 0.0)

    def _flow(self, a, pid, lays, t0, t1):
        route = a.params["route"]
        rt = getattr(self, "route", {}).get(route)
        if not rt:
            self.warn.append(f"flow {a.id}: route '{route}' not drawn")
            return
        (sx, sy), (ex, ey) = rt
        for ln in lays:
            pos = self.track(ln, "transform/position", [sx, sy, 0.0])
            op = self.track(ln, "transform/opacity", 0.0)
            if not op.keys:
                op.keys.append((0.0, 0.0))
            pos.to(t0, t1, [ex, ey, 0.0])
            max_op = 45.0 if ln.endswith("__glow") else 100.0
            op.to(t0, t0 + 0.001, max_op)
            op.to(t1, t1 + 0.001, 0.0)

    def _emit_tracks(self):
        for (ln, prop), tr in self.tracks.items():
            keys = tr.keys
            if len(keys) <= 1:
                if prop == "transform/opacity" and tr.init == 100.0:
                    continue
                self._add("prop.set", {"layer": ln, "path": prop, "value": tr.init if not keys else keys[0][1]})
                continue
            if prop == "transform/position":
                self._add("prop.set", {"layer": ln, "path": prop, "value": keys[0][1]})
            for tm, v in keys:
                self._add("prop.addKey", {"layer": ln, "path": prop, "time": tm, "value": v})

    # ---- camera
    def _camera_rig(self, placed, has_only_disappear: bool = False):
        if has_only_disappear:
            return None
        moves = [c for c in self.scene.camera_instructions if c.move != "static"]
        self._add("layer.newNull", {"name": "camera_rig"})
        cx, cy = self.W / 2, self.H / 2
        anchor = [cx, cy, 0.0]
        self._add("prop.set", {"layer": "camera_rig", "path": "transform/anchor", "value": anchor})
        self._add("prop.set", {"layer": "camera_rig", "path": "transform/position", "value": anchor})
        names = [n for lst in (v for k, v in self.layers.items() if not k.startswith("ost")) for n in lst]
        if names:
            self._add("layer.setParent", {"layers": names, "parent": "camera_rig", "compensate": True})
        return moves

    def _camera_keys(self, moves):
        cx, cy = self.W / 2, self.H / 2
        rig_pos = Track([cx, cy, 0.0], self.fps)
        rig_sc = Track([100.0, 100.0, 100.0], self.fps)
        cam_cfg = (self.profile or {}).get("camera", {})
        idle_push = float(cam_cfg.get("idle_push_in", 1.04))
        max_zoom = float(cam_cfg.get("max_zoom", 1.26))
        allow_focus = bool(cam_cfg.get("allow_focus", True))
        allow_pan = bool(cam_cfg.get("allow_pan", True))

        if not moves:
            # Subtle continuous studio push-in from skill lock (e.g. 104%) so no scene ever feels static
            rig_sc.to(0.0, max(0.5, self.scene.duration), [idle_push * 100, idle_push * 100, 100.0])
        for c in moves:
            t0, t1 = c.at, c.at + c.duration
            raw_amt = c.amount or 1.18
            # Dynamic camera punch: clamped to skill lock max_zoom and layout span limits
            amt = min(max_zoom, max(0.88, raw_amt if raw_amt > 1.05 else 1.18))
            if self.placed:
                min_left_rel = min(p.x - p.w / 2 - cx for p in self.placed.values())
                max_right_rel = max(p.x + p.w / 2 - cx for p in self.placed.values())
                min_top_rel = min(p.y - p.h / 2 - cy for p in self.placed.values())
                max_bottom_rel = max(p.y + p.h / 2 - cy for p in self.placed.values())
                span_x = max_right_rel - min_left_rel
                span_y = max_bottom_rel - min_top_rel
                if span_x > 0:
                    amt = min(amt, max(1.02, (self.W * 0.90) / span_x))
                if span_y > 0:
                    amt = min(amt, max(1.02, (self.H * 0.88) / span_y))

            if c.move in ("zoom_in", "focus"):
                rig_sc.to(t0, t1, [amt * 100, amt * 100, 100.0])
            elif c.move == "zoom_out":
                out_amt = min(0.92, max(0.82, 1.0 / (raw_amt if raw_amt > 1.05 else 1.18)))
                rig_sc.to(t0, t1, [out_amt * 100, out_amt * 100, 100.0])

            # Viewport safety boundaries under current camera zoom scale amt
            if self.placed:
                allowed_dx_min = self.W * 0.06 - cx - min_left_rel * amt
                allowed_dx_max = self.W * 0.94 - cx - max_right_rel * amt
                allowed_dy_min = self.H * 0.06 - cy - min_top_rel * amt
                allowed_dy_max = self.H * 0.94 - cy - max_bottom_rel * amt

                if allowed_dx_min > allowed_dx_max:
                    dx_limit_min = dx_limit_max = 0.0
                else:
                    dx_limit_min = min(0.0, allowed_dx_min)
                    dx_limit_max = max(0.0, allowed_dx_max)

                if allowed_dy_min > allowed_dy_max:
                    dy_limit_min = dy_limit_max = 0.0
                else:
                    dy_limit_min = min(0.0, allowed_dy_min)
                    dy_limit_max = max(0.0, allowed_dy_max)
            else:
                dx_limit_min, dx_limit_max = -self.W * 0.05, self.W * 0.05
                dy_limit_min, dy_limit_max = -self.H * 0.05, self.H * 0.05

            if c.move == "focus" and allow_focus and c.target in self.pos:
                tx, ty = self.pos[c.target]
                raw_dx = (cx - tx) * 0.35
                raw_dy = (cy - ty) * 0.35
                dx = max(dx_limit_min, min(dx_limit_max, raw_dx))
                dy = max(dy_limit_min, min(dy_limit_max, raw_dy))
                rig_pos.to(t0, t1, [cx + dx, cy + dy, 0.0])
            elif c.move == "pan" and allow_pan:
                if c.target and c.target in self.pos:
                    tx, ty = self.pos[c.target]
                    raw_dx = (cx - tx) * 0.30
                else:
                    pan_val = c.amount if c.amount is not None else 0.04
                    raw_dx = pan_val * self.W * 0.12
                dx = max(dx_limit_min, min(dx_limit_max, raw_dx))
                rig_pos.to(t0, t1, [cx + dx, cy, 0.0])
        for prop, tr in (("transform/position", rig_pos), ("transform/scale", rig_sc)):
            if len(tr.keys) <= 1:
                self._add("prop.set", {"layer": "camera_rig", "path": prop, "value": tr.init})
                continue
            for tm, v in tr.keys:
                self._add("prop.addKey", {"layer": "camera_rig", "path": prop, "time": tm, "value": v})


@dataclass
class RenderedScene:
    mp4: Path
    project: Path
    warnings: list[str]
    layers: int
    steps: int
    facts: object


def _composite_stock_asset(mp4: Path, scene: Scene, out_dir: Path, width: int, height: int, fps: float,
                           ffmpeg: str = "ffmpeg", profile: dict | None = None) -> str | None:
    """If the workspace has a discovered stock image or video for this scene, composite a framed documentary picture-in-picture card."""
    stock_cfg = (profile or {}).get("stock_card", {})
    if stock_cfg and not stock_cfg.get("enabled", True):
        return None
    pos_mode = stock_cfg.get("position", "auto")
    if pos_mode == "none":
        return None

    ws_root = out_dir.parent.parent
    disc_file = ws_root / "reports" / "asset_discovery.json"
    if not disc_file.is_file():
        return None
    try:
        disc_data = json.loads(disc_file.read_text(encoding="utf-8")).get("assets", [])
    except Exception:
        return None

    asset_info = next(
        (a for a in disc_data if a.get("scene_id") == scene.id and a.get("status") in ("found", "provided") and a.get("local_rel_path")),
        None,
    )
    if not asset_info:
        return None
    asset_path = ws_root / asset_info["local_rel_path"]
    if not asset_path.is_file():
        return None

    card_w = int(width * (0.24 if width >= height else 0.40))
    card_h = int(card_w * 0.58)
    pad = int(min(width, height) * 0.035)

    # Position locked by skill or varied per scene
    if pos_mode == "top_right":
        ox, oy = width - card_w - pad, pad
    elif pos_mode == "bottom_right":
        ox, oy = width - card_w - pad, height - card_h - pad - int(70 * (min(width, height) / 1080.0))
    elif pos_mode == "bottom_left":
        ox, oy = pad, height - card_h - pad - int(70 * (min(width, height) / 1080.0))
    elif pos_mode == "top_left":
        ox, oy = pad, pad
    else:  # auto
        sc_order = getattr(scene, "order", 1) or 1
        if sc_order % 3 == 1:
            ox, oy = width - card_w - pad, pad  # Top Right
        elif sc_order % 3 == 2:
            ox, oy = width - card_w - pad, height - card_h - pad - int(70 * (min(width, height) / 1080.0))  # Bottom Right
        else:
            ox, oy = pad, height - card_h - pad - int(70 * (min(width, height) / 1080.0))  # Bottom Left
    prov_label = str(asset_info.get("provider") or "stock").upper()
    dur = round(scene.duration, 3)

    # Create a framed PNG card using Pillow for clean rounded border + provider badge
    try:
        from PIL import Image, ImageDraw, ImageFont
        if asset_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            src_img = Image.open(asset_path).convert("RGB")
        else:
            # Extract a representative frame from stock video
            frm_tmp = out_dir / "_stock_frame.jpg"
            subprocess.run([ffmpeg, "-y", "-ss", "0.5", "-i", str(asset_path), "-frames:v", "1", str(frm_tmp)],
                           capture_output=True, timeout=15)
            if not frm_tmp.is_file():
                return None
            src_img = Image.open(frm_tmp).convert("RGB")

        src_img = src_img.resize((card_w, card_h), Image.Resampling.LANCZOS)
        # Vox / Documentary White-Bordered Editorial Cutout Frame with Drop Shadow
        border_w = 10
        bottom_h = 38
        fw, fh = card_w + border_w * 2 + 12, card_h + border_w + bottom_h + 12
        framed = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(framed, "RGBA")
        draw.rounded_rectangle([8, 10, fw - 2, fh - 2], radius=8, fill=(0, 0, 0, 155))
        draw.rounded_rectangle([0, 0, fw - 12, fh - 12], radius=8, fill=(248, 250, 252, 252), outline=(251, 191, 36, 255), width=2)
        framed.paste(src_img, (border_w, border_w))
        draw.rectangle([border_w, card_h + border_w + 4, border_w + 8, card_h + border_w + 26], fill=(234, 88, 12, 255))
        draw.text((border_w + 14, card_h + border_w + 8), f"ARCHIVAL FOOTAGE | {prov_label}", fill=(15, 23, 42, 255))
        card_png = out_dir / "_stock_card.png"
        framed.save(card_png, format="PNG")

        comp_mp4 = out_dir / "_scene_composited.mp4"
        max_sec = float(((profile or {}).get("stock_card") or {}).get("max_seconds", 5.5))
        pip_dur = min(max(2.5, dur - 2.0), max_sec)
        st_out = round(0.8 + pip_dur, 2)
        filter_str = f"[1:v]fade=t=in:st=0.8:d=0.4:alpha=1,fade=t=out:st={st_out}:d=0.5:alpha=1[pip];[0:v][pip]overlay={ox}:{oy}:shortest=1[v]"
        cmd = [
            ffmpeg, "-y",
            "-i", str(mp4),
            "-loop", "1", "-t", str(dur), "-i", str(card_png),
            "-filter_complex", filter_str,
            "-map", "[v]", "-map", "0:a?",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fps), "-t", str(dur),
            str(comp_mp4),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and comp_mp4.is_file() and comp_mp4.stat().st_size > 0:
            comp_mp4.replace(mp4)
            return f"Composited stock media card ({prov_label}: {asset_info['local_rel_path']})"
    except Exception:
        return None
    return None


def render_scene(adapter: EffectCraftAdapter, scene: Scene, out_dir: Path, width: int, height: int, fps: float,
                 style: str = "clean-technical", ffprobe: str = "ffprobe", profile: dict | None = None) -> RenderedScene:
    """Compile + build + save + render + verify one scene into out_dir (caller supplies a versioned directory)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    comp = SceneCompiler(scene, width, height, fps, style, out_dir=out_dir, profile=profile)
    build = comp.compile()
    dur = round(scene.duration, 3)
    proj, mp4 = out_dir / "scene.ecproj", out_dir / "scene.mp4"
    (out_dir / "build_plan.json").write_text(json.dumps({
        "scene": scene.id, "steps": len(build.steps), "placements": build.placements,
        "warnings": build.warnings,
    }, indent=1), encoding="utf-8")
    with adapter.session() as s:
        s.new_comp(scene.id, width, height, fps, dur, PALETTES.get(style, PALETTES["clean-technical"])["bg"])
        for i in range(0, len(build.steps), 400):
            s.batch(build.steps[i:i + 400], label=f"{scene.id} build")
        s.save(proj)
    facts = adapter.render(proj, scene.id, mp4, width, height, fps, dur, ffprobe)
    comp_note = _composite_stock_asset(mp4, scene, out_dir, width, height, fps, profile=profile)
    if comp_note:
        build.warnings.append(comp_note)
    return RenderedScene(mp4, proj, build.warnings, sum(len(v) for v in build.layers.values()), len(build.steps), facts)
