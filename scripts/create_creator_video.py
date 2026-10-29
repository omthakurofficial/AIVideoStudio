#!/usr/bin/env python3
"""Unified CLI for the Creator Motion Graphics Engine.

Generates broadcast-quality, viral kinetic motion graphics videos with zero cloud token cost.
Synthesizes local Kokoro neural narration, 122 BPM tech beats with dynamic sidechain ducking,
and outputs both interactive HTML5 players and 1080p/4K MP4 videos.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from packages.creator_engine.audio import duck_and_mix, synthesize_narration, synthesize_tech_beat
from packages.creator_engine.generator import build_player_html, generate_caption_groups
from packages.creator_engine.renderer import render_html_to_mp4


DEFAULT_SAMPLE_SCRIPTS = {
    "docker": (
        "Stop deploying entire virtual machines just to run a single service. "
        "Traditional VMs carry full guest operating systems, massive memory overhead, and minute-long cold boots. "
        "Docker changes everything by sharing the host Linux kernel through namespaces and cgroups. "
        "Processes run isolated in lightweight containers that spin up in under one hundred milliseconds. "
        "Ninety percent less memory overhead, zero guest OS bloat, and identical environments from local dev to production. "
        "Stop running monolithic infrastructure. Containerize your stack today."
    ),
    "kubernetes": (
        "Managing fifty microservices manually is a guaranteed recipe for 3 AM production outages. "
        "When an instance crashes or traffic surges ten times overnight, manual restarts fail. "
        "Enter Kubernetes: the automated container orchestration control plane. "
        "It constantly compares your desired state against reality. "
        "If a pod dies, Kubernetes reschedules it. If traffic spikes, it autoscales horizontally across nodes. "
        "Self-healing infrastructure with zero manual firefighting. Deploy declaratively."
    ),
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()


def main():
    parser = argparse.ArgumentParser(description="Create a Creator Motion Graphics video locally.")
    parser.add_argument("--topic", type=str, required=True, help="Topic name, e.g. 'Docker Containers'")
    parser.add_argument("--script", type=str, default="", help="Custom narration text or path to .txt file")
    parser.add_argument("--voice", type=str, default="am_adam", help="Kokoro voice (am_adam, am_michael, af_bella, etc.)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier")
    parser.add_argument("--format", type=str, choices=["16:9", "9:16", "both"], default="both", help="Output aspect ratio format")
    parser.add_argument("--out-dir", type=str, default="", help="Directory to save output assets")
    parser.add_argument("--no-render", action="store_true", help="Skip headless MP4 video render, generating HTML players only")

    args = parser.parse_args()

    topic = args.topic.strip()
    topic_slug = slugify(topic)

    # Determine script text
    script_text = args.script.strip()
    if script_text and os.path.exists(script_text):
        script_text = Path(script_text).read_text(encoding="utf-8").strip()

    if not script_text:
        # Check defaults
        key = next((k for k in DEFAULT_SAMPLE_SCRIPTS if k in topic_slug), None)
        if key:
            script_text = DEFAULT_SAMPLE_SCRIPTS[key]
        else:
            script_text = (
                f"Welcome to the masterclass on {topic}. "
                "Most teams struggle with outdated legacy architecture that slows down development and increases failures. "
                "By embracing modern engineering principles, you unlock deterministic deployments and ninety-nine percent uptime. "
                "Automate everything, verify continuously, and build scalable systems that last."
            )

    out_dir = Path(args.out_dir) if args.out_dir else ROOT_DIR / "exports" / f"creator_motion_{topic_slug}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"🎬 CREATOR MOTION GRAPHICS ENGINE: {topic.upper()}")
    print(f"📁 Output Directory: {out_dir}")
    print(f"🎙️ Voice: {args.voice} (speed: {args.speed})")
    print(f"{'='*70}\n")

    # Step 1: Synthesize Narration via Kokoro
    print("▶ Stage 1/5: Synthesizing local neural voiceover (Kokoro-82M)...")
    vo_wav = str(out_dir / "voiceover.wav")
    vo_res = synthesize_narration(script_text, vo_wav, voice=args.voice, speed=args.speed)
    duration_s = vo_res["duration_s"]
    words = vo_res["words"]
    print(f"✓ Voiceover complete: {duration_s:.2f}s, {len(words)} timed words.")

    words_json_path = out_dir / "voiceover_words.json"
    words_json_path.write_text(json.dumps(words, indent=2), encoding="utf-8")

    # Step 2: Synthesize 122 BPM Tech Beat
    print("\n▶ Stage 2/5: Synthesizing dynamic 122 BPM creator tech beat...")
    beat_wav = str(out_dir / "tech_beat.wav")
    synthesize_tech_beat(duration_s + 2.0, beat_wav, bpm=122.0)
    print("✓ Beat synthesis complete.")

    # Step 3: Dynamic Sidechain Ducking
    print("\n▶ Stage 3/5: Computing audio envelope & dynamic sidechain ducking...")
    master_wav = str(out_dir / "master_audio.wav")
    duck_and_mix(vo_wav, beat_wav, master_wav, duck_gain=0.22, swell_gain=0.60)
    master_mp3 = str(out_dir / "master_audio.mp3")
    print(f"✓ Master audio mixed and ducked: {master_wav}")

    # Step 4: Generate Standalone HTML Players
    print("\n▶ Stage 4/5: Generating responsive HTML5 Canvas players...")
    captions = generate_caption_groups(words, max_words=3)

    formats = ["16:9", "9:16"] if args.format == "both" else [args.format]
    html_files = {}

    for fmt in formats:
        is_vert = (fmt == "9:16")
        suffix = "9x16_shorts" if is_vert else "16x9_social"
        html_path = out_dir / f"{topic_slug}_{suffix}.html"
        html_content = build_player_html(
            topic=topic,
            duration_s=duration_s,
            captions=captions,
            audio_mp3_path=master_mp3,
            is_vertical=is_vert,
        )
        html_path.write_text(html_content, encoding="utf-8")
        html_files[fmt] = str(html_path)
        print(f"✓ Created {fmt} HTML player: {html_path.name} ({len(html_content)/1024:.1f} KB)")

    # Step 5: Headless Render to MP4
    if not args.no_render:
        print("\n▶ Stage 5/5: Rendering MP4 videos with Headless Chromium & FFmpeg...")
        for fmt, h_path in html_files.items():
            is_vert = (fmt == "9:16")
            suffix = "9x16_shorts" if is_vert else "16x9_social"
            out_mp4 = str(out_dir / f"{topic_slug}_{suffix}.mp4")
            w, h = (1080, 1920) if is_vert else (1280, 720)
            render_html_to_mp4(h_path, master_wav, out_mp4, width=w, height=h, fps=30)
            print(f"✓ Rendered: {Path(out_mp4).name}")
    else:
        print("\n(Skipping MP4 render due to --no-render flag)")

    print(f"\n{'='*70}")
    print("🎉 ALL PRODUCTION ASSETS COMPLETED!")
    for fmt, h_path in html_files.items():
        print(f"  • {fmt} Player: file://{h_path}")
        if not args.no_render:
            mp4_name = Path(h_path).with_suffix(".mp4").name
            print(f"  • {fmt} Video:  file://{out_dir / mp4_name}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
