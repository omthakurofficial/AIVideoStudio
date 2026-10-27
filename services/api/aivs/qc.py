"""Technical validation, deterministic visual inspection, and targeted scene repair (Section 14)."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from .storyboard.schema import Storyboard, Scene
from .engines.media import probe, extract_frame, frame_stats, frames_differ
from .engines.narration import validate_captions
from .engines.filmcraft import CaptionEntry


@dataclass
class SceneQCResult:
    scene_id: str
    ok: bool
    version: int
    mp4_path: str
    preview_png: str | None
    duration_s: float
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    failure_category: str | None = None  # "storyboard" | "asset" | "animation" | "timing" | "rendering"
    warnings: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    ok: bool
    project_id: str
    output_mp4: str
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    scenes: list[dict] = field(default_factory=list)
    repairs_applied: list[dict] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


STANDARD_LIMITATIONS = [
    "Automated quality control verifies technical stream integrity, timing alignment, layout overlap, non-blank frames, and motion presence; it cannot guarantee pedagogical accuracy or aesthetic appeal.",
    "Icon primitives are rendered as colour-coded monogram badges rather than trademarked third-party logos.",
]


def inspect_rendered_scene(
    scene: Scene, scene_dir: Path, ws_root: Path, width: int, height: int, fps: float,
    version: int = 1, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe",
) -> SceneQCResult:
    mp4 = scene_dir / "scene.mp4"
    ecproj = scene_dir / "scene.ecproj"
    rel_mp4 = str(mp4.relative_to(ws_root)) if mp4.is_relative_to(ws_root) else str(mp4)
    passed: list[str] = []
    failed: list[str] = []
    warnings: list[str] = []
    category: str | None = None

    if not ecproj.is_file() or ecproj.stat().st_size == 0:
        return SceneQCResult(scene.id, False, version, rel_mp4, None, 0.0, passed, ["Editable .ecproj file missing or empty"], "rendering")
    passed.append("ecproj_exists")

    if not mp4.is_file() or mp4.stat().st_size == 0:
        return SceneQCResult(scene.id, False, version, rel_mp4, None, 0.0, passed, ["Scene MP4 missing or empty"], "rendering")
    passed.append("mp4_exists")

    try:
        facts = probe(mp4, ffprobe)
    except Exception as e:
        return SceneQCResult(scene.id, False, version, rel_mp4, None, 0.0, passed, [f"Corrupted MP4 stream: {e}"], "rendering")

    if (facts.width, facts.height) != (width, height):
        failed.append(f"Resolution {facts.width}x{facts.height} != expected {width}x{height}")
        category = category or "rendering"
    else:
        passed.append(f"resolution_{width}x{height}")

    if abs(facts.fps - fps) > 0.05:
        failed.append(f"Frame rate {facts.fps:.2f} != expected {fps}")
        category = category or "rendering"
    else:
        passed.append(f"fps_{int(fps)}")

    expected_dur = scene.duration
    if abs(facts.duration - expected_dur) > max(0.12, 2.0 / fps):
        failed.append(f"Duration {facts.duration:.2f}s != expected {expected_dur:.2f}s")
        category = category or "timing"
    else:
        passed.append("duration_matches_plan")

    # Frame & visual inspection
    prev_dir = ws_root / "renders" / "previews"
    prev_dir.mkdir(parents=True, exist_ok=True)
    t_early = min(0.15, facts.duration * 0.1)
    t_mid = round(facts.duration * 0.55, 2)
    t_late = round(max(t_mid + 0.2, facts.duration * 0.85), 2)

    f_early = scene_dir / "_qc_early.png"
    f_mid = prev_dir / f"{scene.id}.png"
    f_late = scene_dir / "_qc_late.png"
    try:
        extract_frame(mp4, t_early, f_early, ffmpeg)
        extract_frame(mp4, t_mid, f_mid, ffmpeg)
        extract_frame(mp4, t_late, f_late, ffmpeg)
        st_mid = frame_stats(f_mid, t_mid)
        st_late = frame_stats(f_late, t_late)
        best_nonbg = max(st_mid.nonbackground_fraction, st_late.nonbackground_fraction)
        if best_nonbg < 0.008 or max(st_mid.stddev, st_late.stddev) < 3.0:
            failed.append(f"Blank or near-empty visual frame (non-background fraction {best_nonbg:.4f})")
            category = category or "animation"
        else:
            passed.append("visual_elements_visible")

        diff_el = frames_differ(f_early, f_late)
        diff_em = frames_differ(f_early, f_mid)
        if scene.animation_sequence and max(diff_el, diff_em) < 0.05:
            failed.append("Frozen scene: frames at start, middle, and end are identical despite animation sequence")
            category = category or "animation"
        else:
            passed.append("motion_verified")
    except Exception as e:
        failed.append(f"Frame inspection failed: {e}")
        category = category or "rendering"
    finally:
        f_early.unlink(missing_ok=True)
        f_late.unlink(missing_ok=True)

    # Check build_plan warnings and bounding box overlap
    bp = scene_dir / "build_plan.json"
    if bp.is_file():
        bdata = json.loads(bp.read_text(encoding="utf-8"))
        warnings.extend(bdata.get("warnings", []))
        placements = list(bdata.get("placements", {}).items())
        overlaps = 0
        for i in range(len(placements)):
            _, (x1, y1, w1, h1) = placements[i]
            for j in range(i + 1, len(placements)):
                _, (x2, y2, w2, h2) = placements[j]
                if abs(x1 - x2) < (w1 + w2) * 0.42 and abs(y1 - y2) < (h1 + h2) * 0.42:
                    overlaps += 1
        if overlaps == 0:
            passed.append("no_element_overlap")
        else:
            warnings.append(f"{overlaps} element pair(s) placed closely; inspect preview.")

    rel_prev = f"renders/previews/{scene.id}.png" if f_mid.is_file() else None
    return SceneQCResult(scene.id, len(failed) == 0, version, rel_mp4, rel_prev, facts.duration, passed, failed, category, warnings)


def repair_scene_for_retry(scene: Scene, failure_category: str | None, error_msg: str) -> tuple[Scene, str]:
    """Targeted deterministic repair of a scene before re-rendering."""
    d = scene.model_dump()
    dur = scene.duration
    notes: list[str] = []

    # 1. Ensure at least two visible elements exist if the scene had none or failed visual visibility
    non_conn = [e for e in d.get("visual_elements", []) if e["kind"] not in ("arrow", "route", "packet")]
    if not non_conn:
        d["visual_elements"] = [
            {"id": "concept_a", "kind": "service_node", "label": d["key_message"][:28] or "Core Concept", "props": {"color": "#2f6bff"}},
            {"id": "concept_b", "kind": "node", "label": "Outcome", "props": {"color": "#3ecf8e"}},
            {"id": "flow_ab", "kind": "arrow", "label": "", "props": {"from": "concept_a", "to": "concept_b"}},
        ]
        d["element_relationships"] = [{"source": "concept_a", "target": "concept_b", "kind": "flows_to"}]
        non_conn = d["visual_elements"][:2]
        notes.append("populated fallback visual elements")

    # 2. Clamp any out-of-bounds timings
    for a in d.get("animation_sequence", []):
        a["at"] = round(max(0.0, min(dur - 0.3, float(a["at"]))), 2)
        a["duration"] = round(max(0.2, min(dur - a["at"] - 0.05, float(a["duration"]))), 2)

    # 3. If animation failed (blank or frozen), replace animation sequence with a clean progressive reveal + highlight
    if failure_category == "animation" or not d.get("animation_sequence") or "Blank" in error_msg or "Frozen" in error_msg:
        target_ids = [e["id"] for e in non_conn]
        conn_ids = [e["id"] for e in d["visual_elements"] if e["kind"] in ("arrow", "route")]
        seq = [
            {"id": "rep_fade", "at": 0.0, "duration": round(min(0.6, dur * 0.25), 2), "action": "fade_in", "targets": target_ids, "params": {}, "description": "Reveal elements"},
        ]
        if conn_ids:
            seq.append({"id": "rep_draw", "at": round(min(0.5, dur * 0.25), 2), "duration": round(min(0.7, dur * 0.3), 2), "action": "draw", "targets": conn_ids, "params": {}, "description": "Draw connections"})
        seq.append({"id": "rep_pulse", "at": round(dur * 0.55, 2), "duration": round(min(1.0, dur * 0.35), 2), "action": "highlight", "targets": [target_ids[-1]], "params": {}, "description": "Highlight key node"})
        d["animation_sequence"] = seq
        notes.append("replaced animation sequence with verified progressive reveal + highlight")

    # 4. Strip any hint coordinates that caused overlap
    for e in d.get("visual_elements", []):
        if isinstance(e.get("props"), dict):
            e["props"].pop("x", None)
            e["props"].pop("y", None)

    d["status"] = "approved"
    return Scene.model_validate(d), ("; ".join(notes) or f"re-rendering clean build after {failure_category or 'transient'} error")


def inspect_final_video(
    project_id: str, out_mp4: Path, fcproj: Path, ws_root: Path, sb: Storyboard,
    scene_results: list[SceneQCResult], captions: list[CaptionEntry], repairs: list[dict],
    width: int, height: int, fps: float, expect_captions: bool, ffprobe: str = "ffprobe",
) -> QualityReport:
    passed: list[str] = []
    failed: list[str] = []

    if not out_mp4.is_file() or out_mp4.stat().st_size == 0:
        failed.append("Final MP4 file does not exist or is empty")
    else:
        passed.append("final_mp4_exists")

    if not fcproj.is_file() or fcproj.stat().st_size == 0:
        failed.append("Editable FilmCraft project (.fcproj) missing")
    else:
        passed.append("fcproj_preserved")

    expected_total = round(sum(s.duration for s in sb.scenes), 3)
    if out_mp4.is_file():
        facts = probe(out_mp4, ffprobe)
        if (facts.width, facts.height) == (width, height):
            passed.append(f"final_resolution_{width}x{height}")
        else:
            failed.append(f"Final resolution {facts.width}x{facts.height} != {width}x{height}")

        if abs(facts.fps - fps) <= 0.05:
            passed.append(f"final_fps_{int(fps)}")
        else:
            failed.append(f"Final fps {facts.fps} != {fps}")

        if abs(facts.duration - expected_total) <= max(0.25, 4.0 / fps):
            passed.append("final_duration_matches_timeline")
        else:
            failed.append(f"Final video duration {facts.duration:.2f}s != expected {expected_total:.2f}s")

        if facts.has_audio:
            passed.append("audio_stream_present")
            if facts.audio_duration and abs(facts.audio_duration - facts.duration) <= 0.5:
                passed.append("audio_duration_matches_video")
        else:
            failed.append("Final MP4 is missing an audio stream")

    if expect_captions:
        cap_rep = validate_captions(captions, sb, expected_total)
        if cap_rep.ok:
            passed.append(f"captions_validated_{cap_rep.caption_count}_segments")
        else:
            failed.extend(cap_rep.issues)

    for sr in scene_results:
        if not sr.ok:
            failed.append(f"Scene {sr.scene_id} failed QC: {'; '.join(sr.failed_checks)}")

    rel_out = str(out_mp4.relative_to(ws_root)) if out_mp4.is_relative_to(ws_root) else str(out_mp4)
    return QualityReport(
        ok=(len(failed) == 0),
        project_id=project_id,
        output_mp4=rel_out,
        passed_checks=passed,
        failed_checks=failed,
        scenes=[sr.__dict__ for sr in scene_results],
        repairs_applied=repairs,
        limitations=list(STANDARD_LIMITATIONS),
    )
