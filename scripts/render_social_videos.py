#!/usr/bin/env python3
"""
Headless Chrome + FFmpeg Renderer for 16:9 Landscape and 9:16 Mobile Vertical Social Edits.
Muxes:
- 30 FPS Canvas video frames with embedded pop-in karaoke captions
- Synthesized Web Audio SFX (booms, wooshes, marker swipes, glitch, half-time beat)
- High-fidelity Neural Voiceover (Microsoft Edge Neural Guy)
"""
import os
import sys
import time
import base64
import subprocess
import numpy as np
import wave
from playwright.sync_api import sync_playwright

OUT_DIR = "/home/omthakur/Downloads/AIVideoStudio/exports/creator_motion_aws_iam"
VO_WAV = os.path.join(OUT_DIR, "voiceover_narration.wav")
FPS = 30
SAMPLE_RATE = 48000

def render_variant(html_filename, mp4_filename, sfx_wav_filename, width, height):
    html_path = f"file://{os.path.join(OUT_DIR, html_filename)}"
    mp4_path = os.path.join(OUT_DIR, mp4_filename)
    sfx_wav_path = os.path.join(OUT_DIR, sfx_wav_filename)

    print(f"\n=======================================================")
    print(f"🎬 RENDERING VARIANT: {mp4_filename} ({width}x{height})")
    print(f"=======================================================")
    t_start = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(html_path, wait_until="networkidle")
        page.wait_for_timeout(1000)

        duration = page.evaluate("() => window.DURATION")
        total_frames = int(round(duration * FPS))
        print(f"Duration: {duration:.2f}s · Frames: {total_frames} @ {FPS} FPS")

        # 1. Synthesize SFX Audio
        print("🔊 Synthesizing SFX audio via Web Audio API...")
        audio_res = page.evaluate("""async () => {
            const res = await window.SFX.render(window.scoreSound, window.DURATION, 48000, { voiceover: true });
            const bytes = new Uint8Array(res.inter.buffer);
            let binary = '';
            const chunkSize = 0x8000;
            for (let i = 0; i < bytes.length; i += chunkSize) {
                binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
            }
            return {
                b64: btoa(binary),
                peak: res.peak,
                frames: res.frames,
                sr: res.sr
            };
        }""")

        raw_bytes = base64.b64decode(audio_res["b64"])
        floats = np.frombuffer(raw_bytes, dtype=np.float32)
        pcm16 = (np.clip(floats, -1.0, 1.0) * 32767).astype(np.int16)
        with wave.open(sfx_wav_path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm16.tobytes())
        print(f"SFX audio saved: {sfx_wav_path}")

        # 2. Setup FFmpeg Pipeline with Dual Audio Muxing (Master Ducked Beat/VO + Web Audio SFX)
        print("🎥 Piping frames to FFmpeg with dual audio muxing...")
        MASTER_WAV = os.path.join(OUT_DIR, "master_audio_ducked.wav")
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-r", str(FPS),
            "-i", "-",
            "-i", MASTER_WAV,
            "-i", sfx_wav_path,
            "-filter_complex", "[1:a]volume=1.0[master]; [2:a]volume=0.35[sfx]; [master][sfx]amix=inputs=2:duration=first:normalize=0[aout]; [aout]alimiter=limit=0.98[final]",
            "-map", "0:v",
            "-map", "[final]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            mp4_path
        ]

        proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        for i in range(total_frames):
            t = i / float(FPS)
            data_url = page.evaluate("""(time) => {
                window.seek(time);
                return document.getElementById("stage").toDataURL("image/jpeg", 0.90);
            }""", t)

            header, b64_data = data_url.split(",", 1)
            proc.stdin.write(base64.b64decode(b64_data))

            if i % 100 == 0 or i == total_frames - 1:
                pct = (i + 1) / total_frames * 100
                fps_render = (i + 1) / max(0.1, time.time() - t_start)
                print(f"  Frame {i+1:4d}/{total_frames} ({pct:5.1f}%) · {t:5.2f}s · {fps_render:4.1f} fps")

        proc.stdin.close()
        stderr_output = proc.stderr.read().decode("utf-8", errors="ignore")
        proc.wait()
        browser.close()

    elapsed = time.time() - t_start
    if proc.returncode == 0 and os.path.exists(mp4_path):
        size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
        print(f"✅ Rendered {mp4_filename} ({size_mb:.2f} MB) in {elapsed:.1f}s")
        # Copy to artifacts directory as well
        art_dir = "/home/omthakur/.gemini/antigravity/brain/7ab7d57d-d84c-4ab6-a5eb-fe9859973ff2"
        os.system(f"cp {mp4_path} {os.path.join(art_dir, mp4_filename)}")
    else:
        print(f"❌ Error rendering {mp4_filename}:", stderr_output)
        sys.exit(1)

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target in ["16x9", "all"]:
        render_variant("aws_iam_16x9_social.html", "aws_iam_16x9_social.mp4", "sfx_16x9.wav", 1280, 720)

    if target in ["9x16", "all"]:
        render_variant("aws_iam_9x16_shorts.html", "aws_iam_9x16_shorts.mp4", "sfx_9x16.wav", 1080, 1920)

    print("\n🎉 ALL SOCIAL VARIANTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
