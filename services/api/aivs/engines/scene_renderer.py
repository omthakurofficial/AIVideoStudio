"""Scene -> EffectCraft operations. The Director chooses primitives and animation steps; this module deterministically
lays them out and translates them into verified EffectCraft commands (see docs/phase4-engines.md for what was verified).

Limitations (recorded as warnings on every affected render, never hidden):
  * icons are colour-coded labelled badges (no brand logos); dashed arrow style is drawn solid;
  * type_text is rendered as a fade-in; footage/image/map elements are not drawn here (placeholder node + warning)."""
from __future__ import annotations
import json, math
from dataclasses import dataclass, field
from pathlib import Path
from ..storyboard.schema import Scene, VisualElement
from .effectcraft import EffectCraftAdapter
from .mcp_client import EngineError

PALETTES = {
    "clean-technical": dict(bg="#0f1220", node="#2f6bff", text="#ffffff", muted="#9aa3c7", accent="#ffb347", line="#7f8fc4", panel="#1b2347"),
    "dark-neon": dict(bg="#07070f", node="#7a2cff", text="#f4f0ff", muted="#a99ccf", accent="#00f5d4", line="#00b8a2", panel="#171233"),
    "light-minimal": dict(bg="#f4f6fb", node="#2563eb", text="#111827", muted="#6b7280", accent="#f59e0b", line="#64748b", panel="#e2e8f0"),
}
CONNECTOR, PACKET = ("arrow", "route"), ("packet",)
UNSUPPORTED = ("footage", "image", "map_region", "map_marker")
RANK_EDGES = ("connects", "flows_to", "precedes", "depends_on", "contains")


def _hex(c, default):
    if isinstance(c, str) and len(c) == 7 and c.startswith("#"):
        try: int(c[1:], 16); return c
        except ValueError: pass
    return default


@dataclass
class Placed:
    el: VisualElement
    x: float; y: float; w: float; h: float


def layout(scene: Scene, W: int, H: int) -> tuple[dict[str, Placed], float]:
    """Returns placements (centre x,y and size in px) and the global size factor used."""
    u = (min(W, H) / 1080.0)
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
    state: dict[str, int] = {}; dag: dict[str, list[str]] = {i: [] for i in ids}
    def dfs(n):
        state[n] = 1
        for m in adj[n]:
            if state.get(m) == 1: continue
            dag[n].append(m)
            if m not in state: dfs(m)
        state[n] = 2
    indeg = {i: 0 for i in ids}
    for a, b in edges:
        if b in indeg and a != b: indeg[b] += 1
    for i in [i for i in ids if indeg[i] == 0] + ids:
        if i not in state: dfs(i)
    rank = {i: 0 for i in ids}
    changed = True
    for _ in range(len(ids) + 1):
        changed = False
        for a in ids:
            for b in dag[a]:
                if rank[b] < rank[a] + 1: rank[b] = rank[a] + 1; changed = True
        if not changed: break
    connected = {i for a, b in edges for i in (a, b)}
    iso = [i for i in ids if i not in connected]
    maxr = max([rank[i] for i in connected], default=-1)
    for i in iso:
        rank[i] = maxr + 1 if connected else 0
    # hints
    hint = {e.id: (e.props.get("x"), e.props.get("y")) for e in items}
    auto = [e for e in items if not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in hint[e.id])]
    nranks = (max([rank[e.id] for e in auto], default=-1) + 1) or 1
    landscape = W >= H
    base_w, base_h = 230 * u, 110 * u
    top, bottom = 0.16 * H, 0.80 * H  # reserve bottom 20% for caption safe area
    placed: dict[str, Placed] = {}
    groups: dict[int, list[VisualElement]] = {}
    for e in auto: groups.setdefault(rank[e.id], []).append(e)
    cell_main = base_w * 1.30 if landscape else base_h * 2.1
    avail_main = (W * 0.94) if landscape else (bottom - top)
    max_main = max(1, int(avail_main // cell_main))
    lines = math.ceil(nranks / max_main)
    cols = min(nranks, max_main)
    tallest = max((len(v) for v in groups.values()), default=1)
    band = ((bottom - top) / lines) if landscape else (W * 0.94 / lines)
    cross_cell = (base_h * 1.55) if landscape else (base_w * 1.12)
    s_cross = band / (tallest * cross_cell) if tallest else 1.0
    s_main = (avail_main / cols) / cell_main
    s = max(0.45, min(s_cross, max(1.0, min(1.5, s_main))))  # shrink when crowded, grow up to 1.5x when there is room
    for r, els in groups.items():
        line, pos = divmod(r, max_main)
        for k, e in enumerate(els):
            n = len(els)
            w, h = (base_w * s, base_h * s)
            if e.kind == "icon": w = h = 92 * u * s
            elif e.kind in ("label", "text"): w, h = 300 * u * s, 50 * u * s
            elif e.kind == "chart_bar": w, h = 70 * u * s, (60 + 260 * float(e.props.get("value", 0.5) if isinstance(e.props.get("value", 0.5), (int, float)) else 0.5)) * u * s
            if landscape:
                x = W * 0.03 + (W * 0.94) * (pos + 0.5) / cols
                y = top + band * line + band * (k + 0.5) / n
            else:
                y = top + (bottom - top) * (pos + 0.5) / cols
                x = W * 0.03 + band * line + band * (k + 0.5) / n if lines > 1 else W * 0.03 + (W * 0.94) * (k + 0.5) / n
            placed[e.id] = Placed(e, x, y, w, h)
    for e in items:
        if e.id not in placed:
            hx, hy = hint[e.id]
            w, h = (base_w * s, base_h * s) if e.kind != "icon" else (92 * u * s, 92 * u * s)
            placed[e.id] = Placed(e, hx * W, hy * H, w, h)
    return placed, s


class Track:
    """Keyframe track with hold semantics; avoids overlapping/zero-length segments."""
    def __init__(self, init, fps: float):
        self.keys: list[tuple[float, object]] = []; self.init = init; self.fps = fps
    def cur(self): return self.keys[-1][1] if self.keys else self.init
    def to(self, t0: float, t1: float, v):
        if not self.keys: self.keys.append((0.0, self.init))
        last_t = self.keys[-1][0]
        t0 = max(t0, last_t); t1 = max(t1, t0 + 1.0 / self.fps)
        if t0 > last_t + 1e-6: self.keys.append((t0, self.cur()))
        elif t0 == last_t and len(self.keys) == 1 and t0 == 0.0: pass
        self.keys.append((round(t1, 4), v))


@dataclass
class SceneBuild:
    steps: list[dict]
    layers: dict[str, list[str]]
    warnings: list[str]
    placements: dict


class SceneCompiler:
    def __init__(self, scene: Scene, W: int, H: int, fps: float, style: str = "clean-technical"):
        self.scene, self.W, self.H, self.fps = scene, W, H, fps
        self.pal = PALETTES.get(style, PALETTES["clean-technical"])
        self.u = min(W, H) / 1080.0
        self.steps: list[dict] = []; self.layers: dict[str, list[str]] = {}; self.warn: list[str] = []
        self.tracks: dict[tuple[str, str], Track] = {}
        self.pos: dict[str, tuple[float, float]] = {}

    # ---- helpers
    def _add(self, cmd, params): self.steps.append({"command": cmd, "params": params}); return len(self.steps)
    def _own(self, eid, name): self.layers.setdefault(eid, []).append(name)
    def track(self, lname, prop, init):
        return self.tracks.setdefault((lname, prop), Track(init, self.fps))
    def _text(self, eid, name, text, x, y, size, color, w=None):
        w = w or 260 * self.u
        self._add("layer.newText", {"text": text, "name": name, "size": size, "fill": color, "justify": "center", "box": [x - w / 2, y - size * 0.7, w, size * 2.6]})
        self._own(eid, name)

    def compile(self) -> SceneBuild:
        sc, pal, u = self.scene, self.pal, self.u
        placed, s = layout(sc, self.W, self.H)
        self.placed = placed
        for eid, p in placed.items(): self.pos[eid] = (p.x, p.y)
        els = {e.id: e for e in sc.visual_elements}
        entrance: dict[str, float] = {}
        for a in sc.animation_sequence:
            if a.action in ("appear", "fade_in", "draw", "flow", "grow", "type_text"):
                for t in a.targets: entrance[t] = min(entrance.get(t, 1e9), a.at)
        # 1) connectors (bottom)
        for e in sc.visual_elements:
            if e.kind in CONNECTOR: self._connector(e, placed)
        # 2) nodes
        for e in sc.visual_elements:
            if e.kind in CONNECTOR + PACKET or e.id not in placed: continue
            self._node(placed[e.id], s)
        # 3) packets
        for e in sc.visual_elements:
            if e.kind in PACKET:
                nm = f"{e.id}__dot"
                self._add("layer.newShape", {"kind": "ellipse", "name": nm, "size": [20 * u, 20 * u], "fill": _hex(e.props.get("color"), pal["accent"]), "position": [-100, -100]}); self._own(e.id, nm)
        # 4) overlays
        self._overlays()
        # 5) camera rig (parenting) must precede keyframes
        rig = self._camera_rig(placed)
        # 6) animations
        for e in sc.visual_elements:
            for ln in self.layers.get(e.id, []):
                if e.id in entrance: self._init_hidden(ln)
        for a in sorted(sc.animation_sequence, key=lambda x: x.at):
            self._animate(a, els)
        self._emit_tracks()
        if rig: self._camera_keys(rig)
        return SceneBuild(self.steps, self.layers, self.warn, {k: [round(v.x), round(v.y), round(v.w), round(v.h)] for k, v in placed.items()})

    def _init_hidden(self, ln):
        t = self.tracks.setdefault((ln, "transform/opacity"), Track(0.0, self.fps)); t.init = 0.0
        if not t.keys: t.keys.append((0.0, 0.0))

    # ---- primitives
    def _node(self, p: Placed, s: float):
        e, pal, u = p.el, self.pal, self.u
        color = _hex(e.props.get("color"), pal["node"])
        lab = e.label or e.id.replace("_", " ")
        fs = max(14, 26 * u * s)
        if e.kind in UNSUPPORTED:
            self.warn.append(f"element '{e.id}' ({e.kind}) is not drawn by the motion-graphics engine; shown as a labelled placeholder")
        if e.kind == "icon":
            name = f"{e.id}__badge"; mono = (str(e.props.get("icon") or lab)[:2]).upper()
            self._add("layer.newShape", {"kind": "ellipse", "name": name, "size": [p.w, p.w], "fill": color, "position": [p.x, p.y]}); self._own(e.id, name)
            self._text(e.id, f"{e.id}__mono", mono, p.x, p.y + fs * 0.15, max(12, p.w * 0.36), "#ffffff", w=p.w)
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + p.w / 2 + fs * 1.0, fs * 0.9, pal["text"], w=p.w * 2.6)
        elif e.kind in ("label", "text"):
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y, fs * 1.1, _hex(e.props.get("color"), pal["text"]), w=p.w)
        elif e.kind == "chart_bar":
            name = f"{e.id}__bar"
            self._add("layer.newShape", {"kind": "rect", "name": name, "size": [p.w, p.h], "fill": color, "position": [p.x, p.y + p.h / 2]})
            self._add("prop.set", {"layer": name, "path": "contents/group/contents/rect/position", "value": [0, -p.h / 2]}); self._own(e.id, name)
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + p.h / 2 + fs * 1.1, fs * 0.9, pal["text"], w=p.w * 3)
        else:
            outline = e.kind in ("box", "group")
            name = f"{e.id}__shape"; shape = {"rect": "rect", "circle": "ellipse"}.get(str(e.props.get("shape")), "rounded")
            prm = {"kind": shape, "name": name, "size": [p.w, p.h] if shape != "ellipse" else [p.h, p.h], "position": [p.x, p.y]}
            if outline: prm.update({"fill": False, "stroke": color, "strokeWidth": 4 * u})
            elif e.kind == "callout": prm.update({"fill": pal["panel"], "stroke": pal["accent"], "strokeWidth": 3 * u})
            else: prm["fill"] = color
            self._add("layer.newShape", prm); self._own(e.id, name)
            self._text(e.id, f"{e.id}__lab", lab, p.x, p.y + fs * 0.15, fs, pal["text"], w=p.w * 0.92)

    def _endpoints(self, a: str, b: str):
        (ax, ay), (bx, by) = self.pos[a], self.pos[b]
        pa, pb = self.placed[a], self.placed[b]
        dx, dy = bx - ax, by - ay; d = math.hypot(dx, dy) or 1.0
        def clip(pl, sign):
            hw, hh = pl.w / 2 + 8 * self.u, (pl.h / 2 + 8 * self.u)
            if pl.el.kind == "icon":
                hw = pl.w / 2 + 8 * self.u
                hh = (pl.w / 2 + 34 * self.u) if (sign * dy > 0) else (pl.w / 2 + 8 * self.u)
            tx = hw / abs(dx) * d if dx else 1e9; ty = hh / abs(dy) * d if dy else 1e9
            return min(tx, ty)
        ca, cb = clip(pa, 1), clip(pb, -1)
        sx, sy = ax + dx / d * ca, ay + dy / d * ca
        ex, ey = bx - dx / d * cb, by - dy / d * cb
        return (sx, sy), (ex, ey)

    def _connector(self, e: VisualElement, placed):
        f, t = e.props["from"], e.props["to"]
        if f not in placed or t not in placed:
            self.warn.append(f"connector '{e.id}' skipped: endpoint not placed"); return
        (sx, sy), (ex, ey) = self._endpoints(f, t)
        L = math.hypot(ex - sx, ey - sy); ang = math.degrees(math.atan2(ey - sy, ex - sx)); th = 5 * self.u
        col = _hex(e.props.get("color"), self.pal["line"])
        if e.props.get("style") == "dashed":
            self.warn.append(f"connector '{e.id}': dashed style drawn as solid line")
        ln, hd = f"{e.id}__line", f"{e.id}__head"
        self._add("layer.newShape", {"kind": "rect", "name": ln, "size": [max(L - 6 * self.u, 2), th], "fill": col, "position": [sx, sy]})
        self._add("prop.set", {"layer": ln, "path": "contents/group/contents/rect/position", "value": [max(L - 6 * self.u, 2) / 2, 0]})
        self._add("prop.set", {"layer": ln, "path": "transform/rotation", "value": ang}); self._own(e.id, ln)
        self._add("layer.newShape", {"kind": "rect", "name": hd, "size": [16 * self.u, 16 * self.u], "fill": col, "position": [ex, ey]})
        self._add("prop.set", {"layer": hd, "path": "transform/rotation", "value": ang + 45}); self._own(e.id, hd)
        self.route = getattr(self, "route", {}); self.route[e.id] = ((sx, sy), (ex, ey))

    def _overlays(self):
        pal, u = self.pal, self.u
        active: list[tuple[float, float]] = []
        for i, t in enumerate(self.scene.on_screen_text):
            slot = sum(1 for (a, b) in active if a < t.at + t.duration and t.at < b)
            active.append((t.at, t.at + t.duration))
            nm = f"ost{i}__txt"; y = 0.075 * self.H + slot * 62 * u
            self._text(f"ost{i}", nm, t.text, self.W / 2, y, 44 * u, pal["text"], w=self.W * 0.9)
            tr = self.track(nm, "transform/opacity", 0.0)
            if not tr.keys: tr.keys.append((0.0, 0.0))
            tr.to(t.at, t.at + 0.3, 100.0); tr.to(max(t.at + 0.3, t.at + t.duration - 0.3), t.at + t.duration, 0.0)

    # ---- animation
    def _animate(self, a, els):
        d = max(a.duration, 1 / self.fps); t0, t1 = a.at, a.at + d
        for tid in a.targets:
            lays = self.layers.get(tid, [])
            if not lays: self.warn.append(f"animation {a.id}: target '{tid}' has no drawable layers"); continue
            kind = els[tid].kind
            for ln in lays:
                op = lambda: self.track(ln, "transform/opacity", 100.0)
                sc = lambda: self.track(ln, "transform/scale", [100.0, 100.0, 100.0])
                if a.action in ("appear", "fade_in"): op().to(t0, t0 + (0.05 if a.action == "appear" else d), 100.0)
                elif a.action in ("disappear", "fade_out"): op().to(t0, t0 + (0.05 if a.action == "disappear" else d), 0.0)
                elif a.action == "type_text":
                    op().to(t0, t1, 100.0); self.warn.append(f"animation {a.id}: type_text rendered as fade-in")
                elif a.action == "draw":
                    if kind in CONNECTOR:
                        if ln.endswith("__line"):
                            op().to(t0, t0 + 0.001, 100.0)
                            self.track(ln, "transform/scale", [0.0, 100.0, 100.0]).to(t0, t1, [100.0, 100.0, 100.0])
                        else: op().to(max(t0, t1 - 0.15), t1, 100.0)
                    else: op().to(t0, t1, 100.0); self.warn.append(f"animation {a.id}: draw on a non-connector '{tid}' rendered as fade-in")
                elif a.action in ("highlight", "pulse"):
                    cyc = 2 if a.action == "pulse" else 1; amp = 118.0 if a.action == "highlight" else 108.0
                    for k in range(cyc):
                        s0 = t0 + d * k / cyc; s1 = t0 + d * (k + 1) / cyc
                        sc().to(s0, (s0 + s1) / 2, [amp, amp, 100.0]); sc().to((s0 + s1) / 2, s1, [100.0, 100.0, 100.0])
                elif a.action == "scale":
                    f = float(a.params.get("factor", 1.2)) * 100; sc().to(t0, t1, [f, f, 100.0])
                elif a.action == "grow":
                    op().to(t0, t0 + 0.05, 100.0)
                    if kind == "chart_bar" and ln.endswith("__bar"): self.track(ln, "transform/scale", [100.0, 0.0, 100.0]).to(t0, t1, [100.0, 100.0, 100.0])
                elif a.action == "move":
                    x = a.params.get("x"); y = a.params.get("y")
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        px, py = self._base_pos(ln)
                        self.track(ln, "transform/position", [px, py, 0.0]).to(t0, t1, [x * self.W + (px - self.pos.get(tid, (px, py))[0]), y * self.H + (py - self.pos.get(tid, (px, py))[1]), 0.0])
                    else: self.warn.append(f"animation {a.id}: move needs numeric params x,y (fractions of frame)")
                elif a.action == "flow":
                    self._flow(a, tid, ln, t0, t1)
                    break

    def _draw_line(self, ln, t0, t1):
        tr = self.track(ln, "transform/scale", [0.0, 100.0, 100.0]); tr.to(t0, t1, [100.0, 100.0, 100.0])

    def _base_pos(self, ln):
        for st in self.steps:
            p = st["params"]
            if p.get("name") == ln and "position" in p: return tuple(p["position"])
        return (0.0, 0.0)

    def _flow(self, a, pid, ln, t0, t1):
        route = a.params["route"]; rt = getattr(self, "route", {}).get(route)
        if not rt: self.warn.append(f"flow {a.id}: route '{route}' not drawn"); return
        (sx, sy), (ex, ey) = rt
        pos = self.track(ln, "transform/position", [sx, sy, 0.0]); op = self.track(ln, "transform/opacity", 0.0)
        if not op.keys: op.keys.append((0.0, 0.0))
        pos.to(t0, t1, [ex, ey, 0.0])  # starts hidden at the route start: no off-screen jump, so no curved spatial interpolation
        op.to(t0, t0 + 0.001, 100.0); op.to(t1, t1 + 0.001, 0.0)

    def _emit_tracks(self):
        for (ln, prop), tr in self.tracks.items():
            keys = tr.keys
            if len(keys) <= 1:
                if prop == "transform/opacity" and tr.init == 100.0: continue
                self._add("prop.set", {"layer": ln, "path": prop, "value": tr.init if not keys else keys[0][1]}); continue
            if prop == "transform/position":
                self._add("prop.set", {"layer": ln, "path": prop, "value": keys[0][1]})
            for tm, v in keys:
                self._add("prop.addKey", {"layer": ln, "path": prop, "time": tm, "value": v})

    # ---- camera
    def _camera_rig(self, placed):
        moves = [c for c in self.scene.camera_instructions if c.move != "static"]
        if not moves: return None
        self._add("layer.newNull", {"name": "camera_rig"})
        names = [n for lst in (v for k, v in self.layers.items() if not k.startswith("ost")) for n in lst]
        self._add("layer.setParent", {"layers": names, "parent": "camera_rig", "compensate": False})
        return moves

    def _camera_keys(self, moves):
        cx, cy = self.W / 2, self.H / 2
        rig_pos = Track([cx, cy, 0.0], self.fps); rig_sc = Track([100.0, 100.0, 100.0], self.fps)
        first = moves[0]
        ax, ay = (self.pos[first.target] if first.target in self.pos else (cx, cy))
        anchor = [ax, ay, 0.0] if first.move == "focus" else [cx, cy, 0.0]
        self._add("prop.set", {"layer": "camera_rig", "path": "transform/anchor", "value": anchor})
        rig_pos.init = list(anchor)
        for c in moves:
            t0, t1 = c.at, c.at + c.duration; amt = c.amount or 1.3
            if c.move in ("zoom_in", "focus"): rig_sc.to(t0, t1, [amt * 100, amt * 100, 100.0])
            elif c.move == "zoom_out": rig_sc.to(t0, t1, [100.0, 100.0, 100.0])
            if c.move == "focus": rig_pos.to(t0, t1, [cx, cy, 0.0])
            if c.move == "pan": rig_pos.to(t0, t1, [rig_pos.cur()[0] + (c.amount or 0.1) * self.W, rig_pos.cur()[1], 0.0])
        for prop, tr in (("transform/position", rig_pos), ("transform/scale", rig_sc)):
            if len(tr.keys) <= 1:
                self._add("prop.set", {"layer": "camera_rig", "path": prop, "value": tr.init}); continue
            for tm, v in tr.keys: self._add("prop.addKey", {"layer": "camera_rig", "path": prop, "time": tm, "value": v})


@dataclass
class RenderedScene:
    mp4: Path
    project: Path
    warnings: list[str]
    layers: int
    steps: int
    facts: object


def render_scene(adapter: EffectCraftAdapter, scene: Scene, out_dir: Path, width: int, height: int, fps: float,
                 style: str = "clean-technical", ffprobe: str = "ffprobe") -> RenderedScene:
    """Compile + build + save + render + verify one scene into out_dir (caller supplies a versioned directory)."""
    comp = SceneCompiler(scene, width, height, fps, style)
    build = comp.compile()
    dur = round(scene.duration, 3)
    proj, mp4 = out_dir / "scene.ecproj", out_dir / "scene.mp4"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "build_plan.json").write_text(json.dumps({"scene": scene.id, "steps": len(build.steps), "placements": build.placements,
                                                         "warnings": build.warnings}, indent=1), encoding="utf-8")
    with adapter.session() as s:
        s.new_comp(scene.id, width, height, fps, dur, PALETTES.get(style, PALETTES["clean-technical"])["bg"])
        for i in range(0, len(build.steps), 400):  # bounded batch size
            s.batch(build.steps[i:i + 400], label=f"{scene.id} build")
        s.save(proj)
    facts = adapter.render(proj, scene.id, mp4, width, height, fps, dur, ffprobe)
    return RenderedScene(mp4, proj, build.warnings, sum(len(v) for v in build.layers.values()), len(build.steps), facts)
