import json, subprocess
from pathlib import Path
import pytest
from aivs.config import load_settings
from aivs.storyboard import Scene
from aivs.engines.mcp_client import EngineError
from aivs.engines.effectcraft import EffectCraftAdapter
from aivs.engines.scene_renderer import render_scene
from aivs.engines.filmcraft import (
    FilmCraftAdapter, TimelineManifest, ClipPlacement, AudioPlacement, CaptionEntry
)
from aivs.engines.media import extract_frame, frame_stats, frames_differ


@pytest.fixture(scope="module")
def settings():
    return load_settings()


def test_capability_discovery(settings):
    ec = EffectCraftAdapter(settings.effectcraft_cli)
    fc = FilmCraftAdapter(settings.filmcraft_cli, settings.ffmpeg, settings.ffprobe)
    ec_caps = ec.discover()
    fc_caps = fc.discover()
    assert ec_caps.ok and ec_caps.version.startswith("0.17")
    assert fc_caps.ok and fc_caps.version.startswith("0.13")


def test_effectcraft_render_and_filmcraft_assembly(settings, tmp_path):
    ec = EffectCraftAdapter(settings.effectcraft_cli)
    fc = FilmCraftAdapter(settings.filmcraft_cli, settings.ffmpeg, settings.ffprobe)

    sc1 = Scene.model_validate({
        "id": "s01", "order": 1,
        "narration_text": "Developer pushes code to CI pipeline.",
        "estimated_duration": 2.0,
        "learning_objective": "Show CI trigger",
        "key_message": "Push starts build",
        "visual_type": "animated_diagram",
        "visual_description": "Developer icon connects to CI node with a moving packet.",
        "visual_elements": [
            {"id": "dev", "kind": "icon", "label": "Developer", "props": {"icon": "DE", "color": "#4A90E2"}},
            {"id": "ci", "kind": "service_node", "label": "CI Pipeline", "props": {"color": "#F5A623"}},
            {"id": "ar", "kind": "route", "label": "", "props": {"from": "dev", "to": "ci"}},
            {"id": "pkt", "kind": "packet", "label": "", "props": {"color": "#ffd166"}},
        ],
        "element_relationships": [{"source": "dev", "target": "ci", "kind": "flows_to"}],
        "animation_sequence": [
            {"id": "a1", "at": 0.0, "duration": 0.4, "action": "fade_in", "targets": ["dev", "ci"]},
            {"id": "a2", "at": 0.4, "duration": 0.5, "action": "draw", "targets": ["ar"]},
            {"id": "a3", "at": 0.9, "duration": 0.9, "action": "flow", "targets": ["pkt"], "params": {"route": "ar"}},
        ],
        "on_screen_text": [{"text": "CI Pipeline Trigger", "at": 0.1, "duration": 1.8}],
    })

    sc2 = Scene.model_validate({
        "id": "s02", "order": 2,
        "narration_text": "Metrics bar chart compares latency.",
        "estimated_duration": 2.0,
        "learning_objective": "Compare before and after",
        "key_message": "Latency drops",
        "visual_type": "chart",
        "visual_description": "Two chart bars grow and camera focuses.",
        "visual_elements": [
            {"id": "b1", "kind": "chart_bar", "label": "Before", "props": {"value": 0.9, "color": "#ff6b6b"}},
            {"id": "b2", "kind": "chart_bar", "label": "After", "props": {"value": 0.35, "color": "#3ecf8e"}},
        ],
        "element_relationships": [{"source": "b1", "target": "b2", "kind": "compares"}],
        "animation_sequence": [
            {"id": "g1", "at": 0.0, "duration": 0.8, "action": "grow", "targets": ["b1", "b2"]},
            {"id": "h1", "at": 1.0, "duration": 0.8, "action": "highlight", "targets": ["b2"]},
        ],
        "camera_instructions": [{"at": 0.8, "duration": 1.0, "move": "zoom_in", "amount": 1.15}],
    })

    r1 = render_scene(ec, sc1, tmp_path / "scenes" / "s01", 640, 360, 30, ffprobe=settings.ffprobe)
    r2 = render_scene(ec, sc2, tmp_path / "scenes" / "s02", 640, 360, 30, ffprobe=settings.ffprobe)
    assert r1.project.is_file() and r2.project.is_file()
    assert r1.facts.frames == 60 and r2.facts.frames == 60

    # Verify animation actually changes pixels over time
    f_early = extract_frame(r1.mp4, 0.2, tmp_path / "f0.png", settings.ffmpeg)
    f_late = extract_frame(r1.mp4, 1.4, tmp_path / "f1.png", settings.ffmpeg)
    assert frame_stats(f_late, 1.4).nonbackground_fraction > 0.02
    assert frames_differ(f_early, f_late) > 0.5

    # Assemble via FilmCraft with captions burned in
    manifest = TimelineManifest(
        project_id="p_test",
        title="Engine Test",
        width=640, height=360, fps=30.0,
        clips=[
            ClipPlacement(scene_id="s01", source_path="scenes/s01/scene.mp4", start_s=0.0, duration_s=2.0),
            ClipPlacement(scene_id="s02", source_path="scenes/s02/scene.mp4", start_s=2.0, duration_s=2.0),
        ],
        captions=[
            CaptionEntry(index=1, start_s=0.2, end_s=1.8, text="Developer pushes code to CI pipeline."),
            CaptionEntry(index=2, start_s=2.2, end_s=3.8, text="Metrics bar chart compares latency."),
        ],
        burn_captions=True,
    )
    out = fc.assemble(manifest, tmp_path, tmp_path / "renders" / "final.mp4", tmp_path / "assembly" / "proj.fcproj")
    assert out.output_mp4.is_file()
    assert out.project_fcproj.is_file()
    assert out.manifest_path.is_file()
    assert out.srt_path and out.srt_path.is_file()
    assert out.facts.width == 640 and out.facts.height == 360
    assert out.facts.has_audio and abs(out.facts.duration - 4.0) < 0.15


def test_filmcraft_missing_clip_raises_actionable_error(settings, tmp_path):
    fc = FilmCraftAdapter(settings.filmcraft_cli, settings.ffmpeg, settings.ffprobe)
    manifest = TimelineManifest(
        project_id="p_err", title="Err", width=640, height=360, fps=30.0,
        clips=[ClipPlacement(scene_id="s01", source_path="scenes/missing.mp4", start_s=0.0, duration_s=2.0)],
    )
    with pytest.raises(EngineError, match="Missing video clip"):
        fc.assemble(manifest, tmp_path, tmp_path / "out.mp4", tmp_path / "p.fcproj")
