"""Skill registry: every video archetype (map atlas, Vox editorial, cartoon history, tech architecture, finance growth)
is a folder under `<repo>/skills/<skill-id>/` with a `SKILL.md`:

  * YAML frontmatter  -> machine-readable *locks* (render profile) the pipeline enforces deterministically:
                          allowed visual types / element kinds, element budget, backdrop, stock-card slot, caption size,
                          camera limits, reveal lead time, auto-detect triggers, sample script.
  * Markdown body      -> creative rules the AI Director reads verbatim (typography, what connects to what, how maps /
                          motions / effects must look). Changing a style means editing the SKILL.md, not Python.
  * references/*.md    -> optional deep-dive docs; only files listed in `director_references` are sent to the model.

Adding a new archetype = add a new folder. No code change required.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .storyboard.schema import VisualType, ElementKind

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SKILLS_DIR = REPO_ROOT / "skills"

StockSlot = Literal["auto", "top_right", "bottom_right", "bottom_left", "top_left", "none"]
Backdrop = Literal["auto", "map", "vox_paper", "neon_chart", "tech_grid", "warm_stage"]


class _Locked(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StockCard(_Locked):
    enabled: bool = True
    position: StockSlot = "auto"
    max_seconds: float = Field(default=5.5, gt=0, le=60)


class Captions(_Locked):
    font_size: int = Field(default=44, ge=24, le=72, description="Reference size at 44 = ~32px on 1080p landscape.")
    max_words_per_line: int = Field(default=6, ge=2, le=12)


class Camera(_Locked):
    max_zoom: float = Field(default=1.26, ge=1.0, le=1.6)
    allow_focus: bool = True
    allow_pan: bool = True
    idle_push_in: float = Field(default=1.04, ge=1.0, le=1.15, description="Scale reached when a scene has no camera moves.")


class Layout(_Locked):
    max_elements_per_scene: int = Field(default=10, ge=2, le=20)
    require_position_hints: bool = False
    min_gap_px: int = Field(default=24, ge=0, le=200)


class Reveal(_Locked):
    beat_sync: bool = True
    lead_s: float = Field(default=0.10, ge=0.0, le=1.0, description="Entrance fires this long before the word is spoken.")
    max_simultaneous_entrances: int = Field(default=2, ge=1, le=10)


class RenderProfile(_Locked):
    visual_style: str = "clean-technical"
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    backdrop: Backdrop = "auto"
    allowed_visual_types: list[VisualType] = Field(default_factory=list, description="Empty = all allowed.")
    allowed_element_kinds: list[ElementKind] = Field(default_factory=list, description="Empty = all allowed.")
    layout: Layout = Field(default_factory=Layout)
    reveal: Reveal = Field(default_factory=Reveal)
    camera: Camera = Field(default_factory=Camera)
    stock_card: StockCard = Field(default_factory=StockCard)
    captions: Captions = Field(default_factory=Captions)


class Sample(_Locked):
    title: str = ""
    topic: str = ""
    script: str = ""


class Skill(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,40}$")
    name: str
    description: str = ""
    badge: str = ""
    reference_style: str = ""
    references_urls: list[Any] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    priority: int = 0
    render: RenderProfile = Field(default_factory=RenderProfile)
    sample: Sample = Field(default_factory=Sample)
    director_references: list[str] = Field(default_factory=list)
    # filled by the loader
    body: str = ""
    path: str = ""

    def fingerprint(self) -> str:
        """Stable hash of everything that can change the rendered pixels (used for scene-render cache keys)."""
        raw = json.dumps({"id": self.id, "render": self.render.model_dump()}, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def director_brief(self, max_ref_chars: int = 6000) -> str:
        """Text block injected into the Director prompt: locks first (non-negotiable), then the creative rules."""
        r = self.render
        locks = [
            f"SKILL: {self.name} ({self.id}) — reference: {self.reference_style}",
            "LOCKED CONSTRAINTS (validated after you answer; violations are rejected):",
            f"- visual_type must be one of: {', '.join(r.allowed_visual_types) or 'any'}",
            f"- element kinds allowed: {', '.join(r.allowed_element_kinds) or 'any'}",
            f"- at most {r.layout.max_elements_per_scene} visual_elements per scene (connectors included)",
        ]
        if r.layout.require_position_hints:
            locks.append("- every non-connector element MUST carry props x and y (0-1) so nothing stacks in the centre")
        if r.reveal.beat_sync:
            locks.append(f"- reveal each element when the narration says it (≤{r.reveal.max_simultaneous_entrances} entrances at the same instant); "
                         "never show all elements at t=0")
        parts = ["\n".join(locks), "", "CREATIVE RULES:", self.body.strip()]
        budget = max_ref_chars
        for rel in self.director_references:
            p = Path(self.path) / rel
            if budget <= 0 or not p.is_file():
                continue
            txt = p.read_text(encoding="utf-8")[:budget]
            budget -= len(txt)
            parts += ["", f"REFERENCE ({rel}):", txt]
        return "\n".join(parts)

    def as_niche(self) -> dict:
        """Backward-compatible dict shape used by the API / web UI (`niche_categories`)."""
        return {
            "id": self.id, "name": self.name, "badge": self.badge, "reference_style": self.reference_style,
            "default_visual_style": self.render.visual_style, "default_aspect_ratio": self.render.aspect_ratio,
            "description": self.description, "director_rules": self.body.strip(),
            "sample_title": self.sample.title, "sample_topic": self.sample.topic, "sample_script": self.sample.script,
            "skill_path": self.path, "render_profile": self.render.model_dump(),
        }


_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)


def parse_skill_md(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        raise ValueError(f"{path}: SKILL.md must start with a YAML frontmatter block delimited by ---")
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    meta["body"] = m.group(2)
    meta["path"] = str(path.parent)
    return Skill.model_validate(meta)


def skills_dir() -> Path:
    return Path(os.environ.get("AIVS_SKILLS_DIR") or DEFAULT_SKILLS_DIR)


@lru_cache(maxsize=4)
def _load(dir_str: str, stamp: float) -> tuple[Skill, ...]:
    out: list[Skill] = []
    for p in sorted(Path(dir_str).glob("*/SKILL.md")):
        out.append(parse_skill_md(p))
    ids = [s.id for s in out]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise ValueError(f"duplicate skill ids: {sorted(dup)}")
    return tuple(sorted(out, key=lambda s: (-s.priority, s.id)))


def load_skills() -> list[Skill]:
    """Loads all skills; re-reads automatically when any SKILL.md changes (mtime stamp), so edits apply without restart."""
    d = skills_dir()
    if not d.is_dir():
        return []
    stamp = max((f.stat().st_mtime for f in d.glob("*/**/*") if f.is_file()), default=0.0)
    return list(_load(str(d), stamp))


def get_skill(skill_id: str | None) -> Skill | None:
    skills = load_skills()
    if not skills:
        return None
    for s in skills:
        if s.id == skill_id:
            return s
    return skills[0]


def detect_skill(text: str) -> str | None:
    """Pick the skill whose `triggers` match the script most often (ties -> priority order)."""
    low = (text or "").lower()
    best, best_hits = None, 0
    for s in load_skills():
        hits = sum(low.count(t.lower()) for t in s.triggers)
        if hits > best_hits:
            best, best_hits = s.id, hits
    return best


def check_against_skill(skill: Skill, scenes: list) -> list[str]:
    """Deterministic lock validation of a Director answer. Returned strings are fed back to the model for repair."""
    r = skill.render
    problems: list[str] = []
    for sc in scenes:
        if r.allowed_visual_types and sc.visual_type not in r.allowed_visual_types:
            problems.append(f"Scene {sc.id}: visual_type '{sc.visual_type}' is not allowed by skill {skill.id}; "
                            f"use one of {r.allowed_visual_types}.")
        bad = sorted({e.kind for e in sc.visual_elements if r.allowed_element_kinds and e.kind not in r.allowed_element_kinds})
        if bad:
            problems.append(f"Scene {sc.id}: element kinds {bad} are not allowed by skill {skill.id}; use {r.allowed_element_kinds}.")
        empty_lbls = [e.id for e in sc.visual_elements if e.kind not in ("arrow", "route", "packet") and not (e.label or "").strip()]
        if empty_lbls:
            problems.append(f"Scene {sc.id}: elements {empty_lbls} have empty labels; every visual element must have a clear descriptive label.")
        if len(sc.visual_elements) > r.layout.max_elements_per_scene:
            problems.append(f"Scene {sc.id}: {len(sc.visual_elements)} visual_elements exceeds the skill budget of "
                            f"{r.layout.max_elements_per_scene}; merge or drop the least important ones.")
        if r.layout.require_position_hints:
            missing = [e.id for e in sc.visual_elements if e.kind not in ("arrow", "route", "packet")
                       and not all(isinstance(e.props.get(k), (int, float)) for k in ("x", "y"))]
            if missing:
                problems.append(f"Scene {sc.id}: elements {missing[:6]} need props x,y (0-1) — skill {skill.id} requires explicit placement.")
        if r.reveal.beat_sync and sc.visual_elements:
            entr = {}
            for a in sc.animation_sequence:
                if a.action in ("appear", "fade_in", "draw", "grow", "type_text"):
                    for t in a.targets:
                        entr.setdefault(t, a.at)
            at_zero = [k for k, v in entr.items() if v <= 0.05]
            if len(at_zero) > max(2, r.reveal.max_simultaneous_entrances):
                problems.append(f"Scene {sc.id}: {len(at_zero)} elements appear at t=0 ({at_zero[:5]}); stagger entrances "
                                "to the moment the narration mentions each one.")
    return problems
