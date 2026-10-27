"""Versioned storyboard contract (schema_version = 1).

TIME MODEL
  * All times are seconds (float). Scene-relative times (animation `at`, camera `at`, on-screen text `at`) start at 0
    at the first frame of the scene and must lie within [0, scene duration].
  * Video timeline start of scene N = sum(duration of scenes 1..N-1). Scenes never overlap; a transition's duration is
    spent inside the *end* of the outgoing scene, so total video length = sum(scene durations).
  * `estimated_duration` is a planning estimate. After narration exists, `timing.narration_audio_s` records the real audio
    length and `duration` is revised from it (see timeline.revise_durations_from_audio); estimates are never assumed final.
"""
from __future__ import annotations
import re
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = 1

VisualType = Literal["animated_diagram", "architecture", "map", "chart", "timeline", "icons_labels", "footage",
                     "screenshot", "ui_demo", "layered_motion", "hybrid"]
ElementKind = Literal["node", "service_node", "icon", "label", "callout", "box", "group", "arrow", "route", "packet",
                      "chart_bar", "chart_line", "map_region", "map_marker", "timeline_marker", "text", "image", "footage"]
RelKind = Literal["connects", "contains", "flows_to", "compares", "depends_on", "precedes"]
AnimAction = Literal["appear", "disappear", "fade_in", "fade_out", "move", "highlight", "pulse", "draw", "flow",
                     "scale", "type_text", "grow"]
CameraMove = Literal["static", "pan", "zoom_in", "zoom_out", "focus"]
TransitionType = Literal["cut", "fade", "dissolve", "wipe", "slide"]
AssetKind = Literal["stock_video", "stock_image", "user_asset", "generated_graphic"]
SceneStatus = Literal["planned", "approved", "rendering", "rendered", "failed"]

ID_RE = r"^[a-z][a-z0-9_]{0,40}$"


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VisualElement(_M):
    id: str = Field(pattern=ID_RE, description="Unique within the scene; animations and relationships refer to it.")
    kind: ElementKind
    label: str = Field(default="", max_length=80)
    props: dict[str, Any] = Field(default_factory=dict, description="Primitive-specific options (icon, color, value, x/y hints).")


class Relationship(_M):
    source: str
    target: str
    kind: RelKind
    label: str = Field(default="", max_length=80)


class AnimationStep(_M):
    id: str = Field(pattern=ID_RE)
    at: float = Field(ge=0, description="Seconds from scene start.")
    duration: float = Field(gt=0, le=60)
    action: AnimAction
    targets: list[str] = Field(min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="", max_length=200)


class CameraInstruction(_M):
    at: float = Field(ge=0)
    duration: float = Field(gt=0, le=60)
    move: CameraMove
    target: str | None = None
    amount: float | None = Field(default=None, description="Zoom factor (e.g. 1.3) or pan distance as a fraction of frame.")


class OnScreenText(_M):
    text: str = Field(min_length=1, max_length=140)
    at: float = Field(ge=0)
    duration: float = Field(gt=0, le=60)
    element_id: str | None = None


class AssetRequirement(_M):
    id: str = Field(pattern=ID_RE)
    kind: AssetKind
    query: str = Field(default="", max_length=160, description="Search phrase for stock media or description of the asset.")
    orientation: Literal["landscape", "portrait", "any"] = "any"
    required: bool = False
    status: Literal["pending", "found", "missing", "provided"] = "pending"
    justification: str = Field(default="", max_length=200, description="What visual information this adds that animation cannot.")


class Transition(_M):
    type: TransitionType = "cut"
    duration: float = Field(default=0.0, ge=0, le=3)


class SceneTiming(_M):
    unit: Literal["seconds"] = "seconds"
    scene_relative: Literal[True] = True
    narration_audio_s: float | None = Field(default=None, ge=0, description="Measured narration length; None until audio exists.")
    revised_from_audio: bool = False


class Scene(_M):
    id: str = Field(pattern=r"^s\d{2,3}$")
    order: int = Field(ge=1)
    narration_text: str = Field(min_length=1)
    estimated_duration: float = Field(gt=0, le=180)
    learning_objective: str = Field(min_length=1, max_length=300)
    key_message: str = Field(min_length=1, max_length=200)
    visual_type: VisualType
    visual_description: str = Field(min_length=1, max_length=900)
    visual_elements: list[VisualElement] = Field(default_factory=list)
    element_relationships: list[Relationship] = Field(default_factory=list)
    animation_sequence: list[AnimationStep] = Field(default_factory=list)
    timing: SceneTiming = Field(default_factory=SceneTiming)
    camera_instructions: list[CameraInstruction] = Field(default_factory=list)
    on_screen_text: list[OnScreenText] = Field(default_factory=list)
    asset_requirements: list[AssetRequirement] = Field(default_factory=list)
    transition: Transition = Field(default_factory=Transition)
    quality_checks: list[str] = Field(default_factory=list, description="Things QC should verify for this scene.")
    status: SceneStatus = "planned"
    director_notes: str = Field(default="", max_length=400, description="Why this visual treatment was chosen; link to neighbouring scenes.")

    @property
    def duration(self) -> float:
        a = self.timing.narration_audio_s
        return a if (a is not None and self.timing.revised_from_audio) else self.estimated_duration

    @model_validator(mode="after")
    def _refs(self) -> "Scene":
        ids = [e.id for e in self.visual_elements]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.id}: duplicate visual element ids: {sorted({i for i in ids if ids.count(i) > 1})}")
        known = set(ids)
        err = []
        for r in self.element_relationships:
            for end in (r.source, r.target):
                if end not in known:
                    err.append(f"relationship {r.source}->{r.target} references unknown element '{end}'")
        steps = [a.id for a in self.animation_sequence]
        if len(steps) != len(set(steps)):
            err.append("duplicate animation step ids")
        kinds = {e.id: e.kind for e in self.visual_elements}
        for e in self.visual_elements:
            if e.kind in ("arrow", "route"):
                f, t = e.props.get("from"), e.props.get("to")
                if f not in known or t not in known or f == t:
                    err.append(f"{e.kind} '{e.id}' must have props.from and props.to naming two different element ids in this scene (got {f!r}, {t!r})")
                elif kinds[f] in ("arrow", "route", "packet") or kinds[t] in ("arrow", "route", "packet"):
                    err.append(f"{e.kind} '{e.id}' must connect non-connector elements")
        d = self.duration
        for a in self.animation_sequence:
            for t in a.targets:
                if t not in known:
                    err.append(f"animation {a.id} targets unknown element '{t}'")
            if a.action == "flow":
                r = a.params.get("route")
                if r not in known or kinds.get(r) not in ("arrow", "route"):
                    err.append(f"flow animation {a.id} needs params.route naming an arrow/route element id (got {r!r})")
                for t in a.targets:
                    if kinds.get(t) != "packet":
                        err.append(f"flow animation {a.id} may only target packet elements ('{t}' is {kinds.get(t)})")
            if a.at + a.duration > d + 0.05:
                err.append(f"animation {a.id} ends at {a.at + a.duration:.1f}s, after scene end {d:.1f}s")
        for c in self.camera_instructions:
            if c.target and c.target not in known:
                err.append(f"camera target '{c.target}' is unknown")
            if c.at + c.duration > d + 0.05:
                err.append(f"camera move ends after scene end ({c.at + c.duration:.1f}s > {d:.1f}s)")
        for t in self.on_screen_text:
            if t.element_id and t.element_id not in known:
                err.append(f"on_screen_text element_id '{t.element_id}' is unknown")
            if t.at + t.duration > d + 0.05:
                err.append(f"on_screen_text '{t.text[:20]}' ends after scene end")
        if self.transition.duration > d:
            err.append("transition longer than scene")
        if err:
            raise ValueError(f"{self.id}: " + "; ".join(err))
        return self


class DirectorOutput(_M):
    """What the AI Director returns (server adds versioning/provenance)."""
    title: str = Field(max_length=120)
    scenes: list[Scene] = Field(min_length=1, max_length=120)


class Storyboard(_M):
    schema_version: Literal[1] = 1
    project_id: str
    title: str
    revision: int = Field(default=1, ge=1)
    approved: bool = False
    created_by: dict[str, Any] = Field(default_factory=dict, description="Provider/model provenance.")
    scenes: list[Scene] = Field(min_length=1)

    @model_validator(mode="after")
    def _order(self) -> "Storyboard":
        orders = [s.order for s in self.scenes]
        if orders != list(range(1, len(orders) + 1)):
            raise ValueError(f"scene order must be 1..N in sequence, got {orders}")
        ids = [s.id for s in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate scene ids")
        return self


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())
