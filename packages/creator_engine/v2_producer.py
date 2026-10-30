"""AI Video Studio V2 — Universal Multimodal Video Generator & Voice Synthesizer.

Handles:
1. Multi-voice Neural Speech Synthesis (Kokoro Local + Indian Male/Female + Nepali Male/Female + Global)
2. Word-level karaoke caption timestamps extraction
3. Procedural film audio score generation (tech, lofi, orchestral, ambient, cartoon)
4. Dynamic sidechain ducking & MP3 encoding
5. Niche-specific visual animation choreography generation (Vox paper cutouts, Bloomberg terminal charts, 3D Geo maps, 2D avatar)
6. Full local MP4 rendering with headless Chromium + FFmpeg
7. URL & Media Reference Ingestion (YouTube, Shorts, Reels, TikTok, Podcasts, PDFs)
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf

from packages.creator_engine.audio import find_kokoro_python, synthesize_narration, duck_and_mix
from packages.creator_engine.music_composer import master_film_audio_bus
from packages.creator_engine.renderer import render_html_to_mp4
from packages.creator_engine.templates import TOP_10_NICHES, NICHE_BY_ID, synthesize_topic_scenes

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPORTS_DIR = REPO_ROOT / "exports" / "v2_studio"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


async def synthesize_voice_audio(
    text: str,
    voice_id: str,
    out_wav: Path,
) -> Tuple[float, List[Dict[str, Any]]]:
    """Synthesize speech using either Kokoro Local Neural or Microsoft Edge TTS with word timestamps."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    if voice_id.startswith("kokoro:"):
        v_name = voice_id.replace("kokoro:", "")
        res = synthesize_narration(text, str(out_wav), voice=v_name)
        return float(res["duration_s"]), res["words"]

    # Edge TTS (Indian, Nepali, Global)
    import edge_tts
    comm = edge_tts.Communicate(text, voice_id, boundary="WordBoundary")
    words_out: List[Dict[str, Any]] = []
    mp3_tmp = out_wav.with_suffix(".mp3")

    with open(mp3_tmp, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                st = round(chunk["offset"] / 1e7, 3)
                du = round(max(0.05, chunk["duration"] / 1e7), 3)
                words_out.append({"word": chunk["text"], "start_s": st, "end_s": round(st + du, 3)})

    # Convert MP3 to 48kHz WAV via ffmpeg
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3_tmp), "-ar", "48000", "-ac", "2", str(out_wav)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )

    data, sr = sf.read(str(out_wav))
    dur = float(len(data) / sr)
    return dur, words_out


def build_live_v2_html_player(
    project_title: str,
    niche_id: str,
    target_duration_s: int,
    aspect_ratio: str,
    scenes: List[Dict[str, Any]],
    words_timings: List[Dict[str, Any]],
    audio_base64: str,
    html_file_path: str = "",
    master_wav_path: str = "",
) -> str:
    """Generate high-retention, niche-specialized HTML5 canvas animation with embedded audio and real kinetic motion."""
    niche = NICHE_BY_ID.get(niche_id, TOP_10_NICHES[0])
    is_vert = aspect_ratio == "9:16"
    w = 1080 if is_vert else 1280
    h = 1920 if is_vert else 720
    aspect_css = "9 / 16" if is_vert else "16 / 9"

    colors = niche["colors"]
    bg_col = colors["bg"]
    accent_col = colors["accent"]
    sec_col = colors["secondary"]
    hi_col = colors["highlight"]

    # Format word timings into clean karaoke captions with preserved spacing
    clean_words = [w_item for w_item in words_timings if w_item.get("word", "").strip() not in [".", ",", "!", "?", ":", ";"]]
    captions: List[Dict[str, Any]] = []
    if clean_words:
        curr = [clean_words[0]]
        for w_item in clean_words[1:]:
            gap = w_item["start_s"] - curr[-1]["end_s"]
            if len(curr) >= 4 or gap > 0.4:
                st = curr[0]["start_s"]
                en = max(curr[-1]["end_s"], st + 0.35)
                captions.append({
                    "start": round(st, 3),
                    "end": round(en, 3),
                    "words": [{"word": x["word"].upper(), "start": x["start_s"], "end": x["end_s"]} for x in curr]
                })
                curr = [w_item]
            else:
                curr.append(w_item)
        if curr:
            st = curr[0]["start_s"]
            en = max(curr[-1]["end_s"], st + 0.35)
            captions.append({
                "start": round(st, 3),
                "end": round(en, 3),
                "words": [{"word": x["word"].upper(), "start": x["start_s"], "end": x["end_s"]} for x in curr]
            })

    captions_json = json.dumps(captions)
    scenes_json = json.dumps(scenes)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{project_title} — {niche['badge']}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600;700;800;900&family=Space+Grotesk:wght@700&display=swap">
<style>
:root {{
  color-scheme: dark;
  --bg: {bg_col};
  --accent: {accent_col};
  --sec: {sec_col};
  --hi: {hi_col};
  --panel: #111116;
  --line: #22222c;
  --text: #f4f1ea;
  --dim: #8e8d98;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 100%;
  height: 100%;
  background: #000;
  color: var(--text);
  font-family: "Inter", system-ui, sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}
.stage-wrap {{
  flex: 1;
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #040406;
  overflow: hidden;
}}
canvas#stage {{
  max-width: 100%;
  max-height: calc(100vh - 65px);
  aspect-ratio: {aspect_css};
  object-fit: contain;
  display: block;
  box-shadow: 0 20px 60px rgba(0,0,0,0.95);
  background: #000;
}}
:fullscreen, :-webkit-full-screen {{
  width: 100vw !important;
  height: 100vh !important;
  background: #000 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}}
:fullscreen canvas#stage, :-webkit-full-screen canvas#stage {{
  max-width: 100vw !important;
  max-height: 100vh !important;
  aspect-ratio: {aspect_css} !important;
}}
.controls-bar {{
  height: 65px;
  background: rgba(14, 14, 20, 0.98);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--line);
  display: flex;
  align-items: center;
  padding: 0 18px;
  gap: 12px;
  z-index: 50;
}}
button.ctrl-btn {{
  background: var(--accent);
  color: #000;
  border: 0;
  font-weight: 800;
  padding: 9px 18px;
  border-radius: 7px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: transform 0.1s ease;
  white-space: nowrap;
}}
button.ctrl-btn:hover {{ transform: scale(1.04); }}
button.render-action-btn {{
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff;
  border: 0;
  font-weight: 800;
  padding: 8px 16px;
  border-radius: 7px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}}
button.render-action-btn:hover {{ opacity: 0.92; }}
button.icon-btn {{
  background: #20202a;
  color: #fff;
  border: 1px solid var(--line);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}}
button.icon-btn:hover {{ background: #2a2a38; }}
input.scrubber {{
  flex: 1;
  accent-color: var(--accent);
  cursor: pointer;
  height: 6px;
}}
.time-disp {{
  font-size: 13px;
  font-weight: 700;
  color: #cbd5e1;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}}
.badge-pill {{
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  background: rgba(255, 214, 10, 0.15);
  color: var(--accent);
  border: 1px solid var(--accent);
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
}}
</style>
</head>
<body>

<div class="stage-wrap" id="stageWrap">
  <canvas id="stage" width="{w}" height="{h}"></canvas>
</div>

<div class="controls-bar">
  <button class="ctrl-btn" id="playBtn">▶ Play</button>
  <input type="range" class="scrubber" id="scrubber" min="0" max="{target_duration_s}" step="0.05" value="0">
  <div class="time-disp" id="timeDisp">00:00 / {f'{target_duration_s//60:02d}:{target_duration_s%60:02d}'}</div>
  <span class="badge-pill">{niche['badge']} · {aspect_ratio}</span>
  <button class="render-action-btn" id="renderMp4Btn">⚡ Render Local MP4</button>
  <button class="icon-btn" id="fsBtn" title="Toggle Fullscreen">⛶ Fullscreen</button>
</div>

<audio id="masterAudio" preload="auto" src="{audio_base64}"></audio>

<script>
window.DURATION = {target_duration_s};
window.HTML_FILE_PATH = "{html_file_path}";
window.MASTER_WAV_PATH = "{master_wav_path}";
window.ASPECT_RATIO = "{aspect_ratio}";

const IS_VERT = {'true' if is_vert else 'false'};
const W = {w};
const H = {h};
const NICHE_ID = '{niche_id}';
const ACCENT = '{accent_col}';
const SEC = '{sec_col}';
const HI = '{hi_col}';
const BG = '{bg_col}';
const SCENES = {scenes_json};
const CAPTIONS = {captions_json};

const cv = document.getElementById('stage');
const cx = cv.getContext('2d');
const audio = document.getElementById('masterAudio');
const playBtn = document.getElementById('playBtn');
const scrubber = document.getElementById('scrubber');
const timeDisp = document.getElementById('timeDisp');
const fsBtn = document.getElementById('fsBtn');
const stageWrap = document.getElementById('stageWrap');
const renderMp4Btn = document.getElementById('renderMp4Btn');

let isPlaying = false;
let animReq = null;
let lastTimestamp = 0;
let fallbackTime = 0;

function clamp(x, a = 0, b = 1) {{ return Math.max(a, Math.min(b, x)); }}
function ezOut(t) {{ t = clamp(t); return 1 - Math.pow(1 - t, 3); }}
function ezIn(t) {{ t = clamp(t); return t * t * t; }}
function ezBack(t, c = 1.70158) {{ t = clamp(t); return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); }}

function wrapLines(ctx, text, maxW) {{
  const words = text.split(' ');
  const lines = [];
  let cur = words[0];
  for (let i = 1; i < words.length; i++) {{
    const w = words[i];
    const testW = ctx.measureText(cur + ' ' + w).width;
    if (testW <= maxW) {{
      cur += ' ' + w;
    }} else {{
      lines.push(cur);
      cur = w;
    }}
  }}
  lines.push(cur);
  return lines;
}}

// --------------------------------------------------------------------------
// 10 UNIQUE NICHE BACKGROUND RENDERERS
// --------------------------------------------------------------------------
function drawBackground(c, t) {{
  c.fillStyle = BG;
  c.fillRect(0, 0, W, H);

  if (NICHE_ID === 'youtube_growth') {{
    c.strokeStyle = 'rgba(255, 0, 0, 0.04)';
    c.lineWidth = 1;
    for (let x = 0; x < W; x += 70) {{ c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); }}
    for (let y = 0; y < H; y += 70) {{ c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); }}
    const g = c.createRadialGradient(W / 2, H * 0.45, 20, W / 2, H * 0.45, W * 0.6);
    g.addColorStop(0, 'rgba(255, 0, 0, 0.08)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);
  }}
  else if (NICHE_ID === 'vox_explainer' || NICHE_ID === 'geopolitics_maps') {{
    // Archival Paper / Map Texture + Subtle Ruled Lines & Halftone Grain
    c.fillStyle = 'rgba(245, 242, 235, 0.04)';
    c.fillRect(0, 0, W, H);
    c.strokeStyle = 'rgba(255, 214, 0, 0.045)';
    c.lineWidth = 1;
    for (let y = 30; y < H; y += 45) {{
      c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke();
    }}
  }}
  else if (NICHE_ID === 'finance_wealth') {{
    c.strokeStyle = 'rgba(0, 230, 118, 0.04)';
    c.lineWidth = 1;
    for (let x = 0; x < W; x += 80) {{ c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); }}
    for (let y = 0; y < H; y += 60) {{ c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); }}
    for (let i = 0; i < 14; i++) {{
      const cxPos = 60 + i * (W / 14);
      const isUp = (i + Math.floor(t * 1.5)) % 2 === 0;
      c.fillStyle = isUp ? 'rgba(0, 230, 118, 0.12)' : 'rgba(255, 82, 82, 0.12)';
      c.fillRect(cxPos, H * 0.42 + Math.sin(i + t) * 45, 12, 55);
    }}
  }}
  else if (NICHE_ID === 'podcast_avatar') {{
    c.strokeStyle = 'rgba(236, 72, 153, 0.05)';
    c.lineWidth = 1.5;
    for (let x = 0; x < W; x += 90) {{
      for (let y = 0; y < H; y += 90) {{
        c.strokeRect(x + 10, y + 10, 70, 70);
      }}
    }}
    c.fillStyle = 'rgba(239, 68, 68, 0.8)';
    c.font = '800 14px "Inter", sans-serif';
    c.fillText('● ON AIR STUDIO', W - 140, IS_VERT ? 240 : 45);
  }}
  else if (NICHE_ID === 'saas_tech_3d') {{
    c.strokeStyle = 'rgba(56, 189, 248, 0.05)';
    c.lineWidth = 1;
    for (let x = 0; x < W; x += 60) {{ c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); }}
    for (let y = 0; y < H; y += 60) {{ c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); }}
    c.fillStyle = 'rgba(56, 189, 248, 0.04)';
    c.font = '12px monospace';
    c.fillText('> deploy_cluster --scale=infinite --region=global', 40, IS_VERT ? 250 : 50);
  }}
  else if (NICHE_ID === 'mindset_motivation') {{
    c.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    c.lineWidth = 1;
    for (let x = 0; x < W; x += 120) {{ c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); }}
    c.strokeStyle = 'rgba(239, 68, 68, 0.18)';
    c.lineWidth = 2;
    c.beginPath();
    const hY = H * 0.5;
    c.moveTo(0, hY);
    for (let x = 0; x < W; x += 20) {{
      const bump = Math.sin((x - t * 180) * 0.04) > 0.8 ? -40 : 0;
      c.lineTo(x, hY + bump);
    }}
    c.stroke();
  }}
  else {{
    const g = c.createRadialGradient(W / 2, H * 0.4, 40, W / 2, H * 0.4, Math.max(W, H) * 0.75);
    g.addColorStop(0, 'rgba(212, 175, 55, 0.07)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    c.fillStyle = g; c.fillRect(0, 0, W, H);
  }}
}}

// --------------------------------------------------------------------------
// DYNAMIC KINETIC SCENE RENDERER (NO INTERNAL DEBUG LABELS)
// --------------------------------------------------------------------------
function drawKineticScene(c, t) {{
  let curScene = SCENES[0];
  for (const s of SCENES) {{ if (t >= s.start_s) curScene = s; }}

  const sceneT = t - curScene.start_s;
  const punchZoom = 1.0 + (sceneT < 0.35 ? 0.08 * (1 - sceneT / 0.35) : 0);

  c.save();
  c.translate(W / 2, H / 2);
  c.scale(punchZoom, punchZoom);
  c.translate(-W / 2, -H / 2);

  // 1. Subtle Category Watermark (Strict Safe Zones Y: 300px - 1460px)
  const headerY = IS_VERT ? 310 : 70;
  c.fillStyle = ACCENT;
  c.fillRect(IS_VERT ? 80 : 70, headerY, 10, 10);
  c.font = '700 ' + (IS_VERT ? 22 : 18) + 'px "Inter", sans-serif';
  c.fillStyle = 'rgba(255, 255, 255, 0.55)';
  c.textAlign = 'left';
  c.fillText('● BREAKING INVESTIGATION', IS_VERT ? 102 : 92, headerY + 9);

  // 2. Multi-line Kinetic Headline (Zero Overflow Guarantee)
  const titleY = IS_VERT ? H * 0.38 : H * 0.34;
  const animProgress = ezOut(sceneT / 0.45);
  const titleScale = 1.35 - 0.35 * animProgress;

  c.save();
  c.translate(W / 2, titleY);
  c.scale(titleScale, titleScale);

  const headline = (curScene.headline || curScene.title).toUpperCase();
  const maxTextW = IS_VERT ? 820 : 960;
  let fontPx = IS_VERT ? 68 : 72;
  c.font = `900 ${{fontPx}}px "Anton", Impact, sans-serif`;

  let lines = wrapLines(c, headline, maxTextW);
  if (lines.length > 2) {{
    fontPx = IS_VERT ? 54 : 58;
    c.font = `900 ${{fontPx}}px "Anton", Impact, sans-serif`;
    lines = wrapLines(c, headline, maxTextW);
  }}

  c.textAlign = 'center';
  c.fillStyle = '#f4f1ea';
  c.shadowColor = 'rgba(0,0,0,0.85)';
  c.shadowBlur = 30;

  const lineH = fontPx * 1.08;
  const totalH = lines.length * lineH;
  lines.forEach((ln, idx) => {{
    const yOff = (idx * lineH) - (totalH / 2) + (lineH / 2);
    c.fillText(ln, 0, yOff);
  }});
  c.restore();

  // 3. Dynamic Visual Props & Topic-Adaptive Graphics (Safe Zone Y: 48% - 66%)
  const propY = IS_VERT ? H * 0.53 : H * 0.54;
  c.save();
  c.translate(W / 2, propY);

  if (NICHE_ID === 'podcast_avatar') {{
    // 2D/3D Animated Cartoon Avatar Character
    const bounce = Math.sin(t * 8) * 6;
    const isMouthOpen = Math.abs(Math.sin(t * 14)) > 0.45;
    const isBlink = (Math.floor(t * 2.5) % 8) === 0;

    // Head
    c.fillStyle = '#ffcc80';
    c.beginPath(); c.arc(0, -25 + bounce, 55, 0, Math.PI * 2); c.fill();
    // Hair
    c.fillStyle = '#263238';
    c.beginPath(); c.arc(0, -55 + bounce, 55, Math.PI, Math.PI * 2); c.fill();

    // Eyes
    c.fillStyle = '#1e293b';
    if (isBlink) {{
      c.fillRect(-24, -30 + bounce, 16, 3);
      c.fillRect(8, -30 + bounce, 16, 3);
    }} else {{
      c.beginPath(); c.arc(-16, -28 + bounce, 7, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.arc(16, -28 + bounce, 7, 0, Math.PI * 2); c.fill();
    }}

    // Mouth
    c.fillStyle = '#b91c1c';
    if (isMouthOpen) {{
      c.beginPath(); c.ellipse(0, -4 + bounce, 12, 10, 0, 0, Math.PI * 2); c.fill();
    }} else {{
      c.fillRect(-10, -6 + bounce, 20, 4);
    }}

    // Body
    c.fillStyle = '#6366f1';
    c.beginPath(); c.roundRect(-60, 40 + bounce, 120, 60, [25, 25, 0, 0]); c.fill();

    // Microphone
    c.fillStyle = '#475569';
    c.fillRect(45, -10 + bounce, 18, 50);
    c.beginPath(); c.arc(54, -20 + bounce, 16, 0, Math.PI * 2); c.fill();
  }}
  else if (NICHE_ID === 'youtube_growth') {{
    // 3D YouTube Thumbnail Mockup + Spiking Retention Curve
    const cardScale = ezBack(sceneT / 0.45);
    c.scale(cardScale, cardScale);
    c.fillStyle = '#18181f';
    c.strokeStyle = '#ff0000';
    c.lineWidth = 3;
    c.beginPath(); c.roundRect(-240, -75, 480, 150, 16); c.fill(); c.stroke();

    c.fillStyle = '#ff0000';
    c.beginPath(); c.roundRect(-210, -50, 80, 56, 12); c.fill();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.moveTo(-178, -32); c.lineTo(-178, -12); c.lineTo(-160, -22); c.fill();

    c.textAlign = 'left';
    c.font = '800 24px "Inter", sans-serif';
    c.fillStyle = '#ffffff';
    c.fillText('RETENTION LOCK: 89.4%', -110, -26);

    c.font = '700 18px "Inter", sans-serif';
    c.fillStyle = '#ffd60a';
    c.fillText('+100K SUBSCRIBERS REVEAL', -110, 8);

    c.strokeStyle = '#30d158'; c.lineWidth = 4;
    c.beginPath();
    c.moveTo(-110, 48);
    c.quadraticCurveTo(0, 55, 120, 25);
    c.stroke();
  }}
  else if (NICHE_ID === 'finance_wealth') {{
    const statVal = Math.round(ezOut(sceneT / 1.5) * 85);
    c.font = '900 ' + (IS_VERT ? 96 : 88) + 'px "Anton", sans-serif';
    c.fillStyle = '#00e676';
    c.shadowColor = 'rgba(0, 230, 118, 0.55)'; c.shadowBlur = 35;
    c.textAlign = 'center';
    c.fillText('+' + statVal + '% COMPOUND', 0, 0);

    c.font = 'italic 700 30px "Instrument Serif", serif';
    c.fillStyle = '#ffd700';
    c.fillText('Alpha Portfolio Benchmark Outperformance', 0, 48);
  }}
  else {{
    const isHistory = curScene.visual_badge && (
      curScene.visual_badge.includes('YEARS') ||
      curScene.visual_badge.includes('SHANG') ||
      curScene.visual_badge.includes('MANDATE') ||
      curScene.visual_badge.includes('QIN') ||
      curScene.visual_badge.includes('DYNASTIC') ||
      curScene.visual_badge.includes('CIVILIZATION')
    );

    if (isHistory) {{
      // Rotating Imperial Mandate Wheel & Great Wall Vector
      const rot = t * 0.8;
      c.save();
      c.rotate(rot * 0.1);
      c.strokeStyle = '#ffd700';
      c.lineWidth = 3;
      c.beginPath(); c.arc(0, 0, 85, 0, Math.PI * 2); c.stroke();
      for (let i = 0; i < 4; i++) {{
        const a = (i * Math.PI) / 2 + rot * 0.1;
        c.beginPath(); c.moveTo(Math.cos(a) * 45, Math.sin(a) * 45); c.lineTo(Math.cos(a) * 85, Math.sin(a) * 85); c.stroke();
      }}
      c.restore();

      // Central Imperial Jade Seal
      c.fillStyle = '#b91c1c';
      c.beginPath(); c.roundRect(-42, -42, 84, 84, 12); c.fill();
      c.strokeStyle = '#ffd700'; c.lineWidth = 2; c.stroke();
      c.fillStyle = '#ffd700';
      c.font = '900 32px sans-serif';
      c.textAlign = 'center';
      c.fillText('天', 0, 11);

      // On-Screen Metric Badge
      c.fillStyle = '#140c10';
      c.strokeStyle = '#e63946';
      c.lineWidth = 2;
      c.beginPath();
      c.roundRect(-230, 68, 460, 52, 10);
      c.fill(); c.stroke();

      c.font = '800 18px "Inter", sans-serif';
      c.fillStyle = '#ffffff';
      c.fillText(curScene.visual_badge || '⚡ 4,000 YEARS OF COLLAPSE & REBIRTH', 0, 101);
    }} else {{
      // Permanent Magnet & High-Tech Geopolitical / Technical Indicator
      c.fillStyle = '#ef4444';
      c.beginPath(); c.roundRect(-160, -45, 150, 90, [12, 0, 0, 12]); c.fill();
      c.fillStyle = '#3b82f6';
      c.beginPath(); c.roundRect(10, -45, 150, 90, [0, 12, 12, 0]); c.fill();

      c.fillStyle = '#ffffff';
      c.font = '900 36px "Inter", sans-serif';
      c.textAlign = 'center';
      c.fillText('N', -85, 12);
      c.fillText('S', 85, 12);

      // Magnetic Flux Curves
      c.strokeStyle = 'rgba(255, 214, 0, 0.4)';
      c.lineWidth = 2;
      c.beginPath(); c.arc(0, 0, 190, 0, Math.PI, true); c.stroke();
      c.beginPath(); c.arc(0, 0, 190, 0, Math.PI, false); c.stroke();

      // On-Screen Metric Badge
      c.fillStyle = '#111116';
      c.strokeStyle = ACCENT;
      c.lineWidth = 2;
      c.beginPath(); c.roundRect(-220, 68, 440, 52, 10); c.fill(); c.stroke();

      c.font = '800 20px "Inter", sans-serif';
      c.fillStyle = '#ffffff';
      c.fillText(curScene.visual_badge || '⚡ REPM STRATEGIC BREAKTHROUGH', 0, 101);
    }}
  }}
  c.restore();

  // 4. Word-by-Word Pop-in Karaoke Captions (Safe Margin Y = 1440px in 9:16)
  drawKaraokeCaptions(c, t);

  c.restore();
}}

function drawKaraokeCaptions(c, t) {{
  const group = CAPTIONS.find(g => t >= g.start - 0.05 && t <= g.end + 0.35);
  if (!group) return;

  const capY = IS_VERT ? H * 0.74 : H - 85;
  const fontSize = IS_VERT ? 44 : 32;
  const gap = IS_VERT ? 14 : 10;

  c.save();
  c.font = `800 ${{fontSize}}px "Inter", sans-serif`;
  c.textBaseline = 'middle';

  let totalW = 0;
  group.words.forEach(w => {{ w.w = c.measureText(w.word).width; totalW += w.w; }});
  totalW += gap * (group.words.length - 1);

  // Background pill
  const pillW = Math.min(W - 120, totalW + (IS_VERT ? 50 : 36));
  const pillH = fontSize + (IS_VERT ? 30 : 20);
  c.fillStyle = 'rgba(10, 10, 14, 0.94)';
  c.strokeStyle = 'rgba(255, 255, 255, 0.16)';
  c.lineWidth = 1.5;
  c.beginPath(); c.roundRect(W / 2 - pillW / 2, capY - pillH / 2, pillW, pillH, 14);
  c.fill(); c.stroke();

  let curX = W / 2 - totalW / 2;
  group.words.forEach(w => {{
    const isActive = t >= w.start && t <= w.end;
    const wasActive = t > w.end;
    c.save();
    c.translate(curX + w.w / 2, capY);
    if (isActive) {{
      c.scale(1.18, 1.18);
      c.fillStyle = ACCENT;
      c.shadowColor = ACCENT;
      c.shadowBlur = 20;
    }} else if (wasActive) {{
      c.fillStyle = '#f4f1ea';
    }} else {{
      c.fillStyle = 'rgba(244, 241, 234, 0.45)';
    }}
    c.textAlign = 'center';
    c.fillText(w.word, 0, 0);
    c.restore();
    curX += w.w + gap;
  }});
  c.restore();
}}

function renderFrame(t) {{
  drawBackground(cx, t);
  drawKineticScene(cx, t);
}}

function updateUI(t) {{
  scrubber.value = t;
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  const totM = Math.floor(window.DURATION / 60);
  const totS = Math.floor(window.DURATION % 60);
  timeDisp.textContent = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}} / ${{String(totM).padStart(2,'0')}}:${{String(totS).padStart(2,'0')}}`;
}}

function play() {{
  isPlaying = true;
  playBtn.textContent = '⏸ Pause';
  lastTimestamp = performance.now();
  audio.play().catch(() => {{}});
  loop();
}}

function pause() {{
  isPlaying = false;
  playBtn.textContent = '▶ Play';
  audio.pause();
  if (animReq) cancelAnimationFrame(animReq);
}}

function loop(timestamp = performance.now()) {{
  if (!isPlaying) return;
  const dt = (timestamp - lastTimestamp) / 1000;
  lastTimestamp = timestamp;

  let t = 0;
  if (audio && !audio.paused && !isNaN(audio.currentTime) && audio.currentTime > 0) {{
    t = audio.currentTime;
    fallbackTime = t;
  }} else {{
    fallbackTime += dt;
    t = fallbackTime;
  }}

  renderFrame(t);
  updateUI(t);

  if (t >= window.DURATION || audio.ended) {{
    pause();
    window.seek(0);
    return;
  }}
  animReq = requestAnimationFrame(loop);
}}

window.seek = function(t) {{
  fallbackTime = t;
  try {{ audio.currentTime = t; }} catch(e) {{}}
  renderFrame(t);
  updateUI(t);
}};

playBtn.addEventListener('click', () => {{
  if (isPlaying) pause();
  else play();
}});

scrubber.addEventListener('input', (e) => {{
  const t = parseFloat(e.target.value);
  window.seek(t);
}});

fsBtn.addEventListener('click', () => {{
  if (!document.fullscreenElement) {{
    stageWrap.requestFullscreen().catch(() => {{}});
  }} else {{
    document.exitFullscreen().catch(() => {{}});
  }}
}});

if (renderMp4Btn) {{
  renderMp4Btn.addEventListener('click', async () => {{
    renderMp4Btn.disabled = true;
    renderMp4Btn.textContent = '⏳ Rendering MP4...';
    try {{
      const res = await fetch('/api/v2/templates/render-mp4', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          html_file: window.HTML_FILE_PATH,
          master_wav: window.MASTER_WAV_PATH,
          aspect_ratio: window.ASPECT_RATIO
        }})
      }});
      const data = await res.json();
      if (data.ok && data.mp4_file) {{
        renderMp4Btn.textContent = '✅ Downloading...';
        const a = document.createElement('a');
        a.href = data.download_url || ('/api/v2/templates/download-video?path=' + encodeURIComponent(data.mp4_file));
        a.download = data.filename || 'video.mp4';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => {{
          renderMp4Btn.textContent = '⚡ Re-Render MP4';
          renderMp4Btn.disabled = false;
        }}, 3000);
      }} else {{
        alert('Rendering failed: ' + (data.detail || JSON.stringify(data)));
        renderMp4Btn.textContent = '⚡ Render Local MP4';
        renderMp4Btn.disabled = false;
      }}
    }} catch(e) {{
      alert('Render request failed: ' + e);
      renderMp4Btn.textContent = '⚡ Render Local MP4';
      renderMp4Btn.disabled = false;
    }}
  }});
}}

// Initial render
renderFrame(0);
updateUI(0);
</script>
</body>
</html>
"""


async def produce_v2_video(
    topic: str,
    niche_id: str = "youtube_growth",
    target_duration_s: int = 60,
    aspect_ratio: str = "9:16",
    voice_id: str = "kokoro:am_michael",
    custom_instructions: Optional[str] = None,
    reference_info: Optional[Dict[str, Any]] = None,
    scenes: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Complete End-to-End Producer: TTS Voiceover + Beat + Karaoke Captions + HTML Player + Local MP4 Render."""
    # Auto-deconstruct URL if topic is a link
    if not reference_info and ("http://" in topic or "https://" in topic):
        from services.api.aivs.url_extractor import deconstruct_reference_media
        reference_info = deconstruct_reference_media(topic)

    # Adapt niche if URL extraction suggested another niche and user didn't customize
    if reference_info and reference_info.get("suggested_niche") and niche_id == "youtube_growth":
        niche_id = reference_info["suggested_niche"]

    display_topic = reference_info.get("title") if (reference_info and reference_info.get("title")) else topic
    niche = NICHE_BY_ID.get(niche_id, TOP_10_NICHES[0])
    safe_slug = re.sub(r"[^a-zA-Z0-9]+", "_", display_topic.lower())[:35].strip("_")
    timestamp = int(time.time())
    proj_dir = EXPORTS_DIR / f"{safe_slug}_{timestamp}"
    proj_dir.mkdir(parents=True, exist_ok=True)

    wpm = 150
    scene_count = max(4, min(30, int(math.ceil(target_duration_s / 10.0))))

    # 1. Pacing & Script Outline
    if not scenes:
        scenes = synthesize_topic_scenes(
            topic=display_topic,
            niche=niche,
            scene_count=scene_count,
            target_duration_s=target_duration_s,
            wpm=wpm,
            reference_info=reference_info
        )

    full_script = " ".join([s["spoken_narration"] for s in scenes])

    # 2. Synthesize Natural Speech Audio
    vocal_wav = proj_dir / "voiceover.wav"
    dur, words_timings = await synthesize_voice_audio(full_script, voice_id, vocal_wav)

    # 3. Master Film Audio Bus (Royalty-Free Procedural Music + Ducking)
    genre_map = {
        "youtube_growth": "creator_tech",
        "finance_wealth": "lofi_documentary",
        "vox_explainer": "lofi_documentary",
        "geopolitics_maps": "lofi_documentary",
        "podcast_avatar": "playful_cartoon",
        "saas_tech_3d": "cyberpunk_synthwave",
        "mindset_motivation": "lofi_documentary",
        "true_crime": "lofi_documentary",
        "science_tech": "creator_tech",
        "luxury_business": "lofi_documentary"
    }
    music_genre = genre_map.get(niche_id, "creator_tech")
    master_wav = proj_dir / "master_audio.wav"
    master_film_audio_bus(
        voice_wav=str(vocal_wav),
        music_genre=music_genre,
        out_wav=str(master_wav)
    )
    master_mp3 = proj_dir / "master_audio.mp3"
    audio_base64 = "data:audio/mp3;base64," + base64.b64encode(master_mp3.read_bytes()).decode("utf-8")

    # 4. Generate Interactive Standalone HTML Player
    html_file = proj_dir / f"{safe_slug}_{aspect_ratio.replace(':', 'x')}_player.html"
    html_content = build_live_v2_html_player(
        project_title=display_topic,
        niche_id=niche_id,
        target_duration_s=target_duration_s,
        aspect_ratio=aspect_ratio,
        scenes=scenes,
        words_timings=words_timings,
        audio_base64=audio_base64,
        html_file_path=str(html_file),
        master_wav_path=str(master_wav),
    )
    html_file.write_text(html_content, encoding="utf-8")

    return {
        "status": "success",
        "project_title": display_topic,
        "niche": niche,
        "reference_info": reference_info,
        "target_duration_s": target_duration_s,
        "aspect_ratio": aspect_ratio,
        "voice_id": voice_id,
        "scenes": scenes,
        "words_timings": words_timings,
        "html_file": str(html_file),
        "html_code": html_content,
        "master_wav": str(master_wav),
        "master_mp3": str(master_mp3),
        "audio_base64": audio_base64,
        "proj_dir": str(proj_dir)
    }
