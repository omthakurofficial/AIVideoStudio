"""Headless Chromium + FFmpeg High-Speed Video Renderer.

Captures frames via Canvas `toDataURL` at ~40-60 FPS directly into an FFmpeg MJPEG pipe.
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright


def render_html_to_mp4(
    html_path: str,
    audio_wav_path: str,
    out_mp4: str,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
) -> str:
    """Render an interactive HTML canvas file to an MP4 video with synced audio."""
    html_abs = Path(html_path).resolve().as_uri()
    out_path = Path(out_mp4).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[Renderer] Starting high-speed render: {width}x{height} @ {fps}fps -> {out_path.name}")
    start_time = time.time()

    chrome_bin = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
    launch_kwargs = {"args": ["--allow-file-access-from-files", "--disable-web-security"], "headless": True}
    if chrome_bin:
        launch_kwargs["executable_path"] = chrome_bin

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(html_abs, wait_until="networkidle")
        page.wait_for_timeout(1000)

        duration = page.evaluate("() => window.DURATION || 30.0")
        total_frames = int(round(duration * fps))
        print(f"[Renderer] Timeline Duration: {duration:.2f}s ({total_frames} total frames)")

        # Spin up FFmpeg process accepting MJPEG stream
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-r", str(fps),
            "-i", "-",
            "-i", str(Path(audio_wav_path).resolve()),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_path),
        ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        for f in range(total_frames):
            t = f / float(fps)
            data_url = page.evaluate("""(time) => {
                window.seek(time);
                return document.getElementById("stage").toDataURL("image/jpeg", 0.92);
            }""", t)

            header, b64_data = data_url.split(",", 1)
            proc.stdin.write(base64.b64decode(b64_data))

            if f % 150 == 0 or f == total_frames - 1:
                progress = (f + 1) / total_frames * 100
                fps_render = (f + 1) / max(0.1, time.time() - start_time)
                print(f"[Renderer] Frame {f+1:4d}/{total_frames} ({progress:5.1f}%) · {t:5.2f}s · {fps_render:4.1f} fps")

        proc.stdin.close()
        proc.wait()
        browser.close()

    elapsed_total = time.time() - start_time
    file_size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[Renderer] ✅ Complete: {out_path.name} ({file_size_mb:.2f} MB) in {elapsed_total:.1f}s")
    return str(out_path)
