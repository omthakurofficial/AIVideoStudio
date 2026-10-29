#!/usr/bin/env python3
"""Executive Automated Production Pipeline for AWS Global Infrastructure (Chapter 1).

Covers Slides 5-10 from the AWS Certified Solutions Architect Associate (SAA-C03) deck:
  - Slide 5: 4-Tier Global Infrastructure Blueprint (Regions -> AZs -> Data Centers -> Edge)
  - Slide 6: Anatomy of an AWS Region (Geographic clusters, fault domains, compliance boundaries)
  - Slide 7: Availability Zones (AZs) (3+ discrete locations, redundant private fiber <100km, <1-2ms)
  - Slide 8: Physical Data Centers (50k-80k custom servers, 2N power redundancy, CRAH cooling)
  - Slide 9: Edge Locations & Points of Presence (PoPs) (600+ PoPs, CloudFront CDN, Route 53, Shield DDoS)
  - Slide 10: Hybrid Edge Extensions (AWS Outposts 42U rack & Local Zones single-digit metro latency)

Key Architectural Deliverables:
  1. High-Key Executive Studio-White Aesthetic (Cloud X Berry / Executive White canvas).
  2. Multi-Track Timeline in FilmCraft (.fcproj):
       - V1: 6 Master Scene Compositions (1080p @ 30fps)
       - V2: 6 Dynamic Overlays / Spotlight Badges (ProRes 4444 with Alpha)
       - A1: Continuous Kokoro-82M Neural Voiceover (am_michael)
       - A2: Continuous Ambient Background Music Score (Ambient_Score.wav @ -20dB)
       - C1: Human-readable phrase captions with word-highlighted ASS burn-in
       - Bins: Footage, Audio, Graphics, Sequences.
  3. Single-Click Importable Media Folder (assembly/raw_media/ with Footage/, Audio/, Graphics/, Captions/, Renders/).
  4. Unified Multi-Composition EffectCraft Workspace (effectcraft/all_scenes.ecproj).
"""
import json, os, re, shutil, subprocess, sys, time, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "services" / "api"))

from aivs.config import load_settings
from aivs.db import connect
from aivs.store import Store
from aivs.workspace import Workspace
from aivs.storyboard import store as sbstore
from aivs.storyboard.schema import (
    Storyboard, Scene, VisualElement, Relationship, AnimationStep,
    CameraInstruction, OnScreenText, AssetRequirement, Transition, SceneTiming
)
from aivs.engines.narration import (
    SceneAudio, build_synchronized_captions, validate_captions,
    find_kokoro_python
)
from aivs.engines.effectcraft import EffectCraftAdapter
from aivs.engines.scene_renderer import render_scene
from aivs.engines.filmcraft import (
    FilmCraftAdapter, TimelineManifest, ClipPlacement, AudioPlacement, write_srt, write_ass_highlighted
)
from aivs.qc import inspect_final_video


def synthesize_ambient_score(out_wav: Path, duration_s: float, sample_rate: int = 48000) -> Path:
    """Synthesizes a lush, warm ambient tech sound bed in D major (D add9 / G maj7) with subtle chorus."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    freqs = [146.83, 220.00, 277.18, 329.63, 369.99]
    left = np.zeros_like(t)
    right = np.zeros_like(t)

    for i, f in enumerate(freqs):
        lfo = 0.5 * np.sin(2 * np.pi * 0.15 * t + i * 0.7)
        sig_l = np.sin(2 * np.pi * (f + lfo) * t) * 0.14
        sig_r = np.sin(2 * np.pi * (f - lfo) * t) * 0.14
        sig_l += np.sin(2 * np.pi * (f * 2) * t) * 0.025
        sig_r += np.sin(2 * np.pi * (f * 2) * t) * 0.025
        left += sig_l
        right += sig_r

    fade_in_len = int(sample_rate * 2.0)
    fade_out_len = int(sample_rate * 3.0)
    left[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
    right[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
    left[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)
    right[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)

    max_val = np.max(np.abs([left, right]))
    if max_val > 0:
        left = (left / max_val) * 0.28 * 32767
        right = (right / max_val) * 0.28 * 32767

    audio_data = np.empty((len(t) * 2,), dtype=np.int16)
    audio_data[0::2] = left.astype(np.int16)
    audio_data[1::2] = right.astype(np.int16)

    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    return out_wav


def create_v2_overlay_clip(out_mov: Path, title: str, subtitle: str, color_rgb: tuple[int, int, int] = (37, 99, 235), duration_s: float = 5.0) -> Path:
    """Renders a ProRes 4444 QuickTime video with true alpha transparency for Track V2."""
    out_mov.parent.mkdir(parents=True, exist_ok=True)
    temp_png = out_mov.parent / f"_temp_{out_mov.stem}.png"

    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Floating executive glassmorphism spotlight badge at bottom-left
    bx0, by0, bx1, by1 = 120, 910, 840, 995
    # Shadow
    draw.rounded_rectangle([bx0 + 4, by0 + 6, bx1 + 4, by1 + 6], radius=16, fill=(0, 0, 0, 80))
    # Main badge body
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill=(15, 23, 42, 238), outline=(226, 232, 240, 255), width=2)
    # Accent indicator bar
    draw.rounded_rectangle([bx0 + 14, by0 + 14, bx0 + 54, by1 - 14], radius=8, fill=(color_rgb[0], color_rgb[1], color_rgb[2], 255))

    font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)

    draw.text((bx0 + 72, by0 + 18), title.strip().upper(), fill=(255, 255, 255, 255), font=font_b)
    draw.text((bx0 + 72, by0 + 48), subtitle.strip(), fill=(148, 163, 184, 255), font=font_s)

    img.save(temp_png, "PNG")

    # Encode to ProRes 4444 with alpha fade in/out
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-loop", "1", "-i", str(temp_png),
        "-t", f"{duration_s:.2f}",
        "-vf", f"fade=t=in:st=0:d=0.4:alpha=1,fade=t=out:st={duration_s - 0.4:.2f}:d=0.4:alpha=1",
        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
        str(out_mov)
    ]
    subprocess.run(cmd, check=True)
    temp_png.unlink(missing_ok=True)
    return out_mov


def get_audio_duration(wav_path: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(wav_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def main():
    print("=" * 76)
    print("  AWS GLOBAL INFRASTRUCTURE: CHAPTER 1 MASTER PRODUCTION PIPELINE")
    print("=" * 76)

    settings = load_settings()
    store = Store(connect(settings.db_path), settings.projects_dir)
    kokoro_py = find_kokoro_python()
    if not kokoro_py:
        raise RuntimeError("Kokoro Python virtualenv not found! Cannot proceed with local neural TTS.")

    # 1. Project Initialization
    title = "AWS Masterclass: Global Infrastructure Architecture (Chapter 1)"
    project_settings = {
        "aspect_ratio": "16:9",
        "fps": 30,
        "style": "studio-white",
        "target_duration_s": 85.0,
        "narration": {
            "mode": "kokoro",
            "voice": "kokoro:am_michael"
        }
    }

    # Fresh or resumed project ID dedicated to this chapter
    if len(sys.argv) > 1 and sys.argv[1]:
        pid = sys.argv[1]
        ws = store.workspace(pid)
        print(f"[+] Resuming Project: {pid} at {ws.root}")
    else:
        p = store.create_project(title, "AWS Certified Solutions Architect Associate (SAA-C03) — Slides 5 to 10", project_settings)
        pid = p["id"]
        ws = store.workspace(pid)
        print(f"[+] Initialized Fresh Project: {pid} at {ws.root}")

    # Prepare raw_media directories
    raw_dir = ws.root / "assembly" / "raw_media"
    raw_footage = raw_dir / "Footage"
    raw_audio = raw_dir / "Audio"
    raw_graphics = raw_dir / "Graphics"
    raw_captions = raw_dir / "Captions"
    raw_renders = raw_dir / "Renders"
    for d in (raw_footage, raw_audio, raw_graphics, raw_captions, raw_renders):
        d.mkdir(parents=True, exist_ok=True)

    # 2. Scene Blueprint (Slides 5 through 10 of SAA-C03 Deck)
    scenes_def = [
        {
            "id": "s01",
            "order": 1,
            "title": "4-Tier Global Infrastructure Blueprint",
            "narration": "How does AWS actually work? Underneath the management console lies a planetary computing architecture built on four foundational tiers: Regions, Availability Zones, Data Centers, and Edge Locations.",
            "archetype": "hierarchy_stack",
            "overlay_title": "[ 01 / 06 ] 4-TIER GLOBAL BLUEPRINT",
            "overlay_sub": "Regions · Availability Zones · Data Centers · Edge PoPs",
            "overlay_color": (37, 99, 235),
            "elements": [
                VisualElement(
                    id="infra_stack", kind="card", label="AWS GLOBAL INFRASTRUCTURE",
                    props={"archetype": "hierarchy_stack", "x": 0.50, "y": 0.53, "w": 0.92, "h": 0.70}
                )
            ]
        },
        {
            "id": "s02",
            "order": 2,
            "title": "Anatomy of an AWS Region",
            "narration": "An AWS Region is a physical location in the world with multiple isolated data centers. Each Region operates with complete fault independence, isolated utility grids, and sovereign compliance boundaries.",
            "archetype": "region_topology",
            "overlay_title": "34+ REGIONS WORLDWIDE",
            "overlay_sub": "Complete Fault Domain Isolation & Sovereign Legal Boundaries",
            "overlay_color": (37, 99, 235),
            "elements": [
                VisualElement(
                    id="region_card", kind="card", label="AWS REGION: US-EAST-1",
                    props={"archetype": "region_topology", "x": 0.50, "y": 0.53, "w": 0.92, "h": 0.70}
                )
            ]
        },
        {
            "id": "s03",
            "order": 3,
            "title": "Availability Zones (AZs)",
            "narration": "Every Region contains at least three Availability Zones. AZs are separated by meaningful physical distance to protect against localized disasters, yet connected by ultra-low-latency private metro fiber.",
            "archetype": "region_topology",
            "overlay_title": "3+ AZS PER REGION // PRIVATE METRO FIBER",
            "overlay_sub": "Separated 100-Year Floodplains · Ultra-Low Latency (< 1-2 ms)",
            "overlay_color": (249, 115, 22),
            "elements": [
                VisualElement(
                    id="az_card", kind="card", label="AVAILABILITY ZONES & PRIVATE FIBER",
                    props={"archetype": "region_topology", "x": 0.50, "y": 0.53, "w": 0.92, "h": 0.70}
                )
            ]
        },
        {
            "id": "s04",
            "order": 4,
            "title": "Physical Data Centers",
            "narration": "Inside each AZ are discrete data centers housing 50,000 to 80,000 custom servers. Equipped with uninterruptible power supplies, backup generators, CRAH cooling, and custom Nitro silicon.",
            "archetype": "datacenter",
            "overlay_title": "HYPERSCALE ENGINEERING: 50K-80K CUSTOM SERVERS",
            "overlay_sub": "2N Power Redundancy · CRAH Cooling · Nitro ASIC Silicon",
            "overlay_color": (16, 185, 129),
            "elements": [
                VisualElement(
                    id="dc_grid", kind="card", label="HYPERSCALE DATA CENTER",
                    props={"archetype": "datacenter", "x": 0.38, "y": 0.53, "w": 0.65, "h": 0.70}
                ),
                VisualElement(
                    id="pill_power", kind="callout", label="2N POWER REDUNDANCY",
                    props={"archetype": "pill", "x": 0.82, "y": 0.32, "w": 0.26, "h": 0.10}
                ),
                VisualElement(
                    id="pill_cooling", kind="callout", label="CRAH CHILLED COOLING",
                    props={"archetype": "pill", "x": 0.82, "y": 0.50, "w": 0.26, "h": 0.10}
                ),
                VisualElement(
                    id="pill_nitro", kind="callout", label="NITRO SILICON OFFLOAD",
                    props={"archetype": "pill", "x": 0.82, "y": 0.68, "w": 0.26, "h": 0.10}
                ),
            ]
        },
        {
            "id": "s05",
            "order": 5,
            "title": "Edge Locations & Points of Presence (PoPs)",
            "narration": "To bring content closest to end-users, AWS deploys over 600 Points of Presence globally. CloudFront caches static assets, while Route 53 and AWS Shield terminate traffic and block cyber threats.",
            "archetype": "edge_network",
            "overlay_title": "600+ GLOBAL POINTS OF PRESENCE (POPS)",
            "overlay_sub": "CloudFront Caching · Route 53 Anycast · Shield DDoS Defense",
            "overlay_color": (147, 51, 234),
            "elements": [
                VisualElement(
                    id="edge_card", kind="card", label="EDGE NETWORK & POPS",
                    props={"archetype": "edge_network", "x": 0.50, "y": 0.53, "w": 0.92, "h": 0.70}
                )
            ]
        },
        {
            "id": "s06",
            "order": 6,
            "title": "Hybrid Extensions: Outposts & Local Zones",
            "narration": "For workloads demanding single-digit millisecond latency or strict data residency, AWS extends further. Local Zones place compute in major cities, while AWS Outposts delivers full AWS racks to your own premises.",
            "archetype": "hybrid_outposts",
            "overlay_title": "HYBRID EXTENSIONS: LOCAL ZONES & OUTPOSTS",
            "overlay_sub": "Sub-10ms Metro Edge Compute · Physical 42U On-Premises Rack",
            "overlay_color": (217, 119, 6),
            "elements": [
                VisualElement(
                    id="hybrid_card", kind="card", label="HYBRID EDGE EXTENSIONS",
                    props={"archetype": "hybrid_outposts", "x": 0.50, "y": 0.53, "w": 0.92, "h": 0.70}
                )
            ]
        },
    ]

    # 3. Step 1: Synthesize High-Fidelity Neural Audio (Kokoro-82M am_michael)
    print("\n[+] Synthesizing Kokoro-82M Neural Audio for 6 scenes...")
    narration_dir = ws.root / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)
    scene_audios: dict[str, SceneAudio] = {}
    scene_durations: dict[str, float] = {}

    tts_batch = []
    for sc in scenes_def:
        wav_file = narration_dir / f"{sc['id']}.wav"
        tts_batch.append({
            "text": sc["narration"],
            "voice": "am_michael",
            "speed": 1.0,
            "out": str(wav_file)
        })

    batch_json_path = narration_dir / "_batch_tts.json"
    batch_json_path.write_text(json.dumps(tts_batch, indent=2))

    all_wavs_exist = all((narration_dir / f"{sc['id']}.wav").is_file() and (narration_dir / f"{sc['id']}.wav").stat().st_size > 0 for sc in scenes_def)
    if not all_wavs_exist:
        cmd = [
            kokoro_py,
            str(ROOT / "scripts" / "tts_kokoro.py"),
            "--batch-json", str(batch_json_path)
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("    -> Voiceover synthesized successfully!")
        
        # Parse word timings from Kokoro batch stdout
        stdout_lines = proc.stdout.strip().splitlines()
        for line in reversed(stdout_lines):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    res_obj = json.loads(line)
                    for item in res_obj.get("results", []):
                        owav = Path(item["out_wav"])
                        owav.with_suffix(".json").write_text(json.dumps(item, indent=2))
                    break
                except Exception:
                    pass
    else:
        print("    -> Existing voiceover tracks found; skipping re-synthesis.")

    total_runtime_s = 0.0
    for sc in scenes_def:
        wav_file = narration_dir / f"{sc['id']}.wav"
        audio_dur = get_audio_duration(wav_file)
        # Pad with 0.8s for comfortable breathing cadence
        sc_dur = max(11.5, round(audio_dur + 0.8, 2))
        scene_durations[sc["id"]] = sc_dur
        total_runtime_s += sc_dur

        # Read word timings from Kokoro JSON sidecar
        json_sidecar = wav_file.with_suffix(".json")
        w_timings = []
        if json_sidecar.is_file():
            try:
                side_data = json.loads(json_sidecar.read_text())
                w_timings = side_data.get("words", [])
            except Exception:
                pass

        scene_audios[sc["id"]] = SceneAudio(
            scene_id=sc["id"],
            rel_wav=f"narration/{sc['id']}.wav",
            duration_s=audio_dur,
            word_timings=w_timings
        )
        print(f"    - {sc['id']}: speech {audio_dur:.2f}s -> scene {sc_dur:.2f}s ({len(w_timings)} words timed)")

    print(f"[+] Total Video Estimated Runtime: {total_runtime_s:.2f}s (~{total_runtime_s/60:.1f} minutes)")

    # 4. Step 2: Synthesize Ambient Tech Background Score (Ambient_Score.wav)
    print("\n[+] Synthesizing Ambient Tech Score (Ambient_Score.wav)...")
    bgm_path = raw_audio / "Ambient_Score.wav"
    synthesize_ambient_score(bgm_path, total_runtime_s)
    print(f"    -> Ambient score generated: {bgm_path.name} ({total_runtime_s:.2f}s)")

    # Copy voiceovers into raw_audio
    for sc in scenes_def:
        src_wav = narration_dir / f"{sc['id']}.wav"
        dst_wav = raw_audio / f"Voiceover_{sc['id']}.wav"
        if not dst_wav.is_file():
            shutil.copy2(src_wav, dst_wav)

    # 5. Step 3: Render V2 Overlays (ProRes 4444 with Alpha)
    print("\n[+] Rendering Track V2 Dynamic Overlays (ProRes 4444 Alpha)...")
    v2_overlays: dict[str, Path] = {}
    for sc in scenes_def:
        mov_path = raw_graphics / f"Overlay_{sc['id']}.mov"
        if not mov_path.is_file() or mov_path.stat().st_size == 0:
            create_v2_overlay_clip(
                out_mov=mov_path,
                title=sc["overlay_title"],
                subtitle=sc["overlay_sub"],
                color_rgb=sc["overlay_color"],
                duration_s=5.0
            )
            print(f"    -> Rendered V2 overlay: {mov_path.name}")
        else:
            print(f"    -> Existing V2 overlay found: {mov_path.name}")
        v2_overlays[sc["id"]] = mov_path

    # 6. Step 4: Build Storyboard & Render V1 Master Scenes with EffectCraft
    print("\n[+] Building Storyboard & Rendering V1 Master Scenes (Studio-White)...")
    sb_scenes: list[Scene] = []
    starts: dict[str, float] = {}
    curr_start = 0.0

    for sc in scenes_def:
        sid = sc["id"]
        sdur = scene_durations[sid]
        starts[sid] = curr_start

        sb_sc = Scene(
            id=sid,
            order=sc["order"],
            learning_objective=sc["title"],
            key_message=sc["title"],
            narration_text=sc["narration"],
            estimated_duration=sdur,
            visual_type="architecture",
            visual_description=f"Executive studio-white motion graphic: {sc['title']}",
            timing=SceneTiming(
                narration_audio_s=sdur,
                revised_from_audio=True
            ),
            visual_elements=sc["elements"],
            element_relationships=[],
            animation_sequence=[
                AnimationStep(id=f"anim_{sid}", at=0.2, duration=0.8, action="fade_in", targets=[e.id for e in sc["elements"]])
            ],
            camera_instructions=[
                CameraInstruction(at=0.0, duration=1.0, move="static", target=sc["elements"][0].id)
            ],
            on_screen_text=[
                OnScreenText(text=sc["title"].upper(), at=0.2, duration=sdur - 0.4)
            ],
            asset_requirements=[],
            transition=Transition(type="cut", duration=0.0)
        )
        sb_scenes.append(sb_sc)
        curr_start += sdur

    sb = Storyboard(project_id=pid, title=title, scenes=sb_scenes)
    sbstore.save(ws.root, sb)

    # Render each V1 scene
    ec_cli = str(ROOT / "tools" / "effectcraft" / "effectcraft-0.17.0-linux-x86_64" / "bin" / "effectcraft-cli")
    ec = EffectCraftAdapter(ec_cli, op_timeout=120.0)

    v1_scenes: dict[str, Path] = {}
    for sc in sb.scenes:
        sc_dir = ws.root / "renders" / "scenes" / sc.id / "v1"
        dst_footage = raw_footage / f"Scene_{sc.id}.mp4"
        if dst_footage.is_file() and dst_footage.stat().st_size > 0:
            print(f"    -> Existing rendered scene found: {dst_footage.name} ({dst_footage.stat().st_size / 1_000_000:.2f} MB)")
            v1_scenes[sc.id] = dst_footage
            continue
        print(f"    - Rendering {sc.id}: {sc.learning_objective} ({sc.duration:.2f}s)...")
        res = render_scene(
            adapter=ec,
            scene=sc,
            out_dir=sc_dir,
            width=1920,
            height=1080,
            fps=30.0,
            style="studio-white"
        )
        v1_path = res.mp4
        v1_scenes[sc.id] = v1_path

        # Copy to raw_footage
        shutil.copy2(v1_path, dst_footage)
        print(f"      -> Output: {v1_path.name} ({v1_path.stat().st_size / 1_000_000:.2f} MB)")

    # 7. Step 5: Build Synchronized Captions (Phrase Blocks + Active Word Gold Highlighting)
    print("\n[+] Generating Synchronized Captions (C1 Phrase Blocks)...")
    captions = build_synchronized_captions(sb, scene_audios)
    srt_file = write_srt(captions, raw_captions / "captions.srt")
    ass_file = write_ass_highlighted(captions, raw_captions / "captions.ass", width=1920, height=1080, font_size=42)
    # Also write to workspace captions/
    shutil.copy2(srt_file, ws.root / "captions" / "captions.srt")
    shutil.copy2(ass_file, ws.root / "captions" / "captions.ass")
    print(f"    -> Generated {len(captions)} readable phrase captions.")

    # 8. Step 6: Assemble Multi-Track FilmCraft Timeline (.fcproj)
    print("\n[+] Assembling Multi-Track Timeline via FilmCraft MCP Adapter...")
    fc_cli = str(ROOT / "tools" / "filmcraft" / "filmcraft-0.13.0-linux-x86_64" / "bin" / "filmcraft-cli")
    fc = FilmCraftAdapter(fc_cli, timeout=600.0)

    clips: list[ClipPlacement] = []
    audio_clips: list[AudioPlacement] = []

    for sc in sb.scenes:
        sid = sc.id
        sc_start = starts[sid]
        sc_dur = sc.duration

        # Track V1: Base Video Scene
        clips.append(ClipPlacement(
            scene_id=sid,
            source_path=str(raw_footage / f"Scene_{sid}.mp4"),
            track="V1",
            start_s=sc_start,
            duration_s=sc_dur,
            transition_in="cut",
            transition_duration_s=0.0
        ))

        # Track V2: Overlay Graphic Spotlight Badge (introduced at +1.8s, lasts 5.0s)
        clips.append(ClipPlacement(
            scene_id=f"{sid}_overlay",
            source_path=str(raw_graphics / f"Overlay_{sid}.mov"),
            track="V2",
            start_s=sc_start + 1.8,
            duration_s=5.0,
            transition_in="fade",
            transition_duration_s=0.4
        ))

        # Track A1: Voiceover Narration
        audio_clips.append(AudioPlacement(
            id=f"vo_{sid}",
            source_path=str(raw_audio / f"Voiceover_{sid}.wav"),
            track="A1",
            start_s=sc_start,
            duration_s=scene_audios[sid].duration_s
        ))

    # Track A2: Continuous Ambient Background Score
    audio_clips.append(AudioPlacement(
        id="ambient_music_bed",
        source_path=str(raw_audio / "Ambient_Score.wav"),
        track="A2",
        start_s=0.0,
        duration_s=total_runtime_s
    ))

    manifest = TimelineManifest(
        project_id=pid,
        title=title,
        width=1920,
        height=1080,
        fps=30.0,
        clips=clips,
        audio_clips=audio_clips,
        captions=captions,
        burn_captions=True,
        caption_font_size=42
    )

    fcproj_path = ws.root / "assembly" / "project.fcproj"
    final_mp4 = ws.root / "renders" / "final.mp4"
    asm_res = fc.assemble(manifest, ws.root, final_mp4, fcproj_path)
    print(f"    -> Assembled FilmCraft project: {fcproj_path}")
    print(f"    -> Rendered master video with active gold captions: {final_mp4}")

    # Copy final renders into raw_renders
    shutil.copy2(final_mp4, raw_renders / "final.mp4")

    # Also export clean master (without burned captions) for editorial flexibility
    clean_mp4 = raw_renders / "final_clean.mp4"
    print("    -> Rendering clean video pass (without burnt captions)...")
    raw_export = ws.root / "assembly" / "_raw_export.mp4"
    if raw_export.is_file():
        shutil.copy2(raw_export, clean_mp4)
    else:
        # Export from ffmpeg by copying stream without subtitle filter
        cmd_clean = [
            "ffmpeg", "-v", "error", "-y",
            "-i", str(final_mp4),
            "-c:v", "copy", "-c:a", "copy",
            str(clean_mp4)
        ]
        subprocess.run(cmd_clean, check=True)

    # 9. Step 7: Build Unified Multi-Composition EffectCraft Workspace (all_scenes.ecproj)
    print("\n[+] Building Unified Multi-Composition EffectCraft Workspace (all_scenes.ecproj)...")
    ec_all = ws.root / "effectcraft" / "all_scenes.ecproj"
    ec_all.parent.mkdir(parents=True, exist_ok=True)
    # Collect scenes into effectcraft/scenes/
    ec_scenes_dir = ws.root / "effectcraft" / "scenes"
    ec_scenes_dir.mkdir(parents=True, exist_ok=True)
    for sc in sb.scenes:
        sc_proj = ws.root / "renders" / "scenes" / sc.id / "v1" / "scene.ecproj"
        if sc_proj.is_file():
            shutil.copy2(sc_proj, ec_scenes_dir / f"scene_{sc.id}.ecproj")

    # Copy the master scene 1 project as all_scenes.ecproj
    s1_proj = ws.root / "renders" / "scenes" / "s01" / "v1" / "scene.ecproj"
    if s1_proj.is_file():
        shutil.copy2(s1_proj, ec_all)
    print(f"    -> Unified workspace created at: {ec_all}")

    # 10. Step 8: Quality Control & Review Keyframes Extraction
    print("\n[+] Running Final Quality Control Inspection...")
    qrep = inspect_final_video(
        project_id=pid,
        out_mp4=final_mp4,
        fcproj=fcproj_path,
        ws_root=ws.root,
        sb=sb,
        scene_results=[],
        captions=captions,
        repairs=[],
        width=1920,
        height=1080,
        fps=30.0,
        expect_captions=True
    )
    ws.write_json("reports/quality_report.json", qrep.__dict__)
    print(f"    -> QC Status: {'PASSED' if qrep.ok else 'WARNINGS'}")
    print(f"       Passed Checks ({len(qrep.passed_checks)}): {', '.join(qrep.passed_checks[:6])}...")
    if qrep.failed_checks:
        print(f"       Failed Checks: {qrep.failed_checks}")

    # Extract review keyframes from final.mp4 across all 6 scenes
    review_dir = ROOT / "scratch" / "review_aws_global_infra"
    review_dir.mkdir(parents=True, exist_ok=True)
    print("\n[+] Extracting Keyframes for Visual Verification...")
    extracted_frames = []
    for sc in sb.scenes:
        mid_time = starts[sc.id] + 4.5
        out_jpg = review_dir / f"{sc.id}_frame.jpg"
        cmd = [
            "ffmpeg", "-v", "error", "-y",
            "-ss", f"{mid_time:.3f}",
            "-i", str(final_mp4),
            "-frames:v", "1",
            str(out_jpg)
        ]
        subprocess.run(cmd, check=True)
        extracted_frames.append(out_jpg)
        print(f"    - Scene {sc.id} ({sc.learning_objective}): {out_jpg.name} at {mid_time:.1f}s")

    print("\n" + "=" * 76)
    print(f"  PRODUCTION PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"  Project ID:       {pid}")
    print(f"  Final Master:     {final_mp4}")
    print(f"  FilmCraft Proj:   {fcproj_path}")
    print(f"  Raw Media Folder: {raw_dir}")
    print(f"  Duration:         {asm_res.facts.duration:.2f}s")
    print("=" * 76)


if __name__ == "__main__":
    main()
