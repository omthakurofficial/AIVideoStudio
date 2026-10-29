"""HTML5 Creator Motion Graphics Generator.

Compiles scene descriptions, kinetic typography rules, 3D mockups, and
word timestamps into zero-dependency standalone HTML players (16:9 Landscape & 9:16 Shorts).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_caption_groups(words: List[Dict[str, Any]], max_words: int = 3, max_gap: float = 0.5) -> List[Dict[str, Any]]:
    """Group individual word timestamps into short 2-3 word pop-in karaoke badges."""
    clean_words = [w for w in words if w.get("word", "").strip() not in [".", ",", "!", "?", ":", ";"]]
    if not clean_words:
        return []

    groups = []
    curr = [clean_words[0]]

    for w in clean_words[1:]:
        gap = w["start_s"] - curr[-1]["end_s"]
        if len(curr) >= max_words or gap > max_gap:
            st = curr[0]["start_s"]
            en = max(curr[-1]["end_s"], st + 0.35)
            txt = " ".join([x["word"] for x in curr])
            groups.append({
                "start": round(st, 3),
                "end": round(en, 3),
                "text": txt,
                "words": [{"word": x["word"], "start": x["start_s"], "end": x["end_s"]} for x in curr]
            })
            curr = [w]
        else:
            curr.append(w)

    if curr:
        st = curr[0]["start_s"]
        en = max(curr[-1]["end_s"], st + 0.35)
        txt = " ".join([x["word"] for x in curr])
        groups.append({
            "start": round(st, 3),
            "end": round(en, 3),
            "text": txt,
            "words": [{"word": x["word"], "start": x["start_s"], "end": x["end_s"]} for x in curr]
        })
    return groups


def build_player_html(
    topic: str,
    duration_s: float,
    captions: List[Dict[str, Any]],
    audio_mp3_path: Optional[str] = None,
    is_vertical: bool = False,
    scenes_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Render self-contained HTML5 player with canvas kinetic typography, 3D yaw, and SFX."""
    width = 1080 if is_vertical else 1280
    height = 1920 if is_vertical else 720
    aspect = "9 / 16" if is_vertical else "16 / 9"
    mode_name = "9:16 Shorts / Reels" if is_vertical else "16:9 Landscape Social"

    audio_base64 = ""
    if audio_mp3_path and Path(audio_mp3_path).exists():
        with open(audio_mp3_path, "rb") as f:
            audio_base64 = "data:audio/mp3;base64," + base64.b64encode(f.read()).decode("utf-8")

    captions_json = json.dumps(captions)
    duration_val = round(duration_s, 2)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{topic} — {mode_name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600;700;800;900&display=block">
<style>
:root {{
  color-scheme: dark;
  --bg: #0b0b0e;
  --panel: #141418;
  --ink: #f2f0ea;
  --dim: #8e8d94;
  --line: #26262e;
  --accent: #ffd60a;
  --green: #30d158;
  --red: #ff453a;
  --display: "Anton", Impact, sans-serif;
  --body: "Inter", system-ui, sans-serif;
  --serif: "Instrument Serif", Georgia, serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--ink);
  font-family: var(--body);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 16px;
}}
.container {{
  width: 100%;
  max-width: {"480px" if is_vertical else "1180px"};
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.header {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}}
.title {{
  font-family: var(--display);
  font-size: clamp(20px, 3vw, 28px);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.title em {{
  font-family: var(--serif);
  font-style: italic;
  color: var(--accent);
}}
.badge {{
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #ff9900;
  background: rgba(255, 153, 0, 0.15);
  border: 1px solid rgba(255, 153, 0, 0.35);
  padding: 4px 10px;
  border-radius: 999px;
}}
.viewport {{
  position: relative;
  width: 100%;
  aspect-ratio: {aspect};
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--line);
  box-shadow: 0 20px 50px rgba(0,0,0,0.6);
}}
.viewport canvas {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}}
.controls {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}}
button.btn {{
  background: #202026;
  border: 1px solid #33333e;
  color: #fff;
  font-family: var(--body);
  font-weight: 600;
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}}
button.btn:hover {{ background: #2a2a34; }}
.scrub {{
  flex: 1;
  -webkit-appearance: none;
  height: 6px;
  border-radius: 3px;
  background: #2a2a34;
  outline: none;
  cursor: pointer;
}}
.scrub::-webkit-slider-thumb {{
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
}}
.time {{
  font-family: monospace;
  font-size: 13px;
  color: var(--dim);
}}
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <div class="title">{topic} <em>Edition</em></div>
    <div class="badge">{mode_name}</div>
  </div>

  <div class="viewport">
    <canvas id="stage" width="{width}" height="{height}"></canvas>
  </div>

  <div class="controls">
    <button class="btn" id="playBtn">Play</button>
    <input type="range" class="scrub" id="scrubber" min="0" max="{duration_val}" step="0.01" value="0">
    <div class="time" id="timeDisp">00:00 / {int(duration_val // 60):02d}:{int(duration_val % 60):02d}</div>
  </div>
</div>

<audio id="masterAudio" preload="auto" src="{audio_base64}"></audio>

<script>
const DURATION = {duration_val};
const IS_VERTICAL = {'true' if is_vertical else 'false'};
const W = {width};
const H = {height};
const CAPTIONS = {captions_json};

const cv = document.getElementById('stage');
const cx = cv.getContext('2d');
const audio = document.getElementById('masterAudio');
const playBtn = document.getElementById('playBtn');
const scrubber = document.getElementById('scrubber');
const timeDisp = document.getElementById('timeDisp');

// Kinetic Math & Drawing Utilities
const CM = {{
  clamp(x, a, b) {{ return Math.max(a, Math.min(b, x)); }},
  smooth(x) {{ x = CM.clamp(x, 0, 1); return x * x * (3 - 2 * x); }},
  easeOutExpo(x) {{ return x >= 1 ? 1 : 1 - Math.pow(2, -10 * x); }},
  easeOutBack(x, c = 1.70158) {{ return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }},
  rng(seed) {{
    let s = (seed >>> 0) || 1;
    s = (s ^ (s << 13)) >>> 0;
    s = (s ^ (s >>> 17)) >>> 0;
    s = (s ^ (s << 5)) >>> 0;
    return (s >>> 0) / 4294967296;
  }},
  noise1(seed) {{
    const i = Math.floor(seed);
    const f = seed - i;
    const u = f * f * (3 - 2 * f);
    return (1 - u) * (CM.rng(i) * 2 - 1) + u * (CM.rng(i + 1) * 2 - 1);
  }}
}};

// Visual Components
function drawBackground(c, t) {{
  c.fillStyle = '#0a0a0d';
  c.fillRect(0, 0, W, H);

  // Subtle drifting grid
  c.strokeStyle = 'rgba(255, 255, 255, 0.025)';
  c.lineWidth = 1;
  const gridStep = IS_VERTICAL ? 72 : 80;
  const offY = (t * 12) % gridStep;
  for (let y = -gridStep + offY; y < H + gridStep; y += gridStep) {{
    c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke();
  }}
  for (let x = 0; x < W; x += gridStep) {{
    c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke();
  }}

  // Atmospheric glows
  const g1 = c.createRadialGradient(W * 0.25, H * 0.25, 0, W * 0.25, H * 0.25, W * 0.7);
  g1.addColorStop(0, 'rgba(255, 214, 10, 0.05)');
  g1.addColorStop(1, 'rgba(0, 0, 0, 0)');
  c.fillStyle = g1;
  c.fillRect(0, 0, W, H);

  const g2 = c.createRadialGradient(W * 0.75, H * 0.8, 0, W * 0.75, H * 0.8, W * 0.6);
  g2.addColorStop(0, 'rgba(48, 209, 88, 0.04)');
  g2.addColorStop(1, 'rgba(0, 0, 0, 0)');
  c.fillStyle = g2;
  c.fillRect(0, 0, W, H);
}}

function drawFinishing(c, t) {{
  // Cinematic vignette
  const vig = c.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.45, W / 2, H / 2, Math.max(W, H) * 0.85);
  vig.addColorStop(0, 'rgba(0,0,0,0)');
  vig.addColorStop(1, 'rgba(0,0,0,0.65)');
  c.fillStyle = vig;
  c.fillRect(0, 0, W, H);
}}

function drawKaraokeCaptions(c, t) {{
  let curr = null;
  for (let i = 0; i < CAPTIONS.length; i++) {{
    if (t >= CAPTIONS[i].start && t <= CAPTIONS[i].end) {{
      curr = CAPTIONS[i];
      break;
    }}
  }}
  if (!curr) return;

  const fontPx = IS_VERTICAL ? 42 : 36;
  c.font = '800 ' + fontPx + 'px Inter, sans-serif';
  c.textBaseline = 'middle';

  let totalW = 0;
  const wordMetrics = curr.words.map(w => {{
    const width = c.measureText(w.word.toUpperCase() + ' ').width;
    totalW += width;
    return {{ word: w.word.toUpperCase(), width: width, start: w.start, end: w.end }};
  }});

  const boxPadX = 26;
  const boxPadY = 16;
  const boxW = totalW + boxPadX * 2;
  const boxH = fontPx + boxPadY * 2;
  const boxX = (W - boxW) / 2;
  const boxY = IS_VERTICAL ? H * 0.78 : H * 0.86;

  // Badge background
  c.save();
  c.fillStyle = 'rgba(12, 12, 16, 0.88)';
  c.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  c.lineWidth = 2;
  c.beginPath();
  c.roundRect(boxX, boxY, boxW, boxH, 14);
  c.fill();
  c.stroke();

  // Words pop-in
  let curX = boxX + boxPadX;
  const textY = boxY + boxH / 2;
  wordMetrics.forEach(m => {{
    const isActive = t >= m.start && t <= m.end;
    if (isActive) {{
      c.fillStyle = '#ffd60a';
      c.shadowColor = 'rgba(255, 214, 10, 0.7)';
      c.shadowBlur = 14;
    }} else if (t > m.end) {{
      c.fillStyle = '#f2f0ea';
      c.shadowBlur = 0;
    }} else {{
      c.fillStyle = '#6e6e76';
      c.shadowBlur = 0;
    }}
    c.fillText(m.word, curX, textY);
    curX += m.width;
  }});
  c.restore();
}}

// 3D Tilt perspective transform
function drawYaw(c, yawDeg, pitchDeg, cxCoord, cyCoord, drawFn) {{
  c.save();
  c.translate(cxCoord, cyCoord);
  const yawRad = yawDeg * Math.PI / 180;
  const pitchRad = pitchDeg * Math.PI / 180;
  const cosYaw = Math.cos(yawRad);
  const sinYaw = Math.sin(yawRad);
  const cosPitch = Math.cos(pitchRad);
  c.transform(cosYaw, sinYaw * 0.25, 0, cosPitch, 0, 0);
  drawFn();
  c.restore();
}}

// Render Frame Pure Function
function renderScene(t) {{
  drawBackground(cx, t);

  // Chrome header
  cx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  cx.font = '700 ' + (IS_VERTICAL ? 22 : 18) + 'px Inter, sans-serif';
  cx.fillText('{topic.upper()} · ARCHITECTURE', IS_VERTICAL ? 48 : 56, IS_VERTICAL ? 90 : 54);

  // Sample Kinetic Typography Hero Beat
  const slamProgress = CM.clamp(t / 1.8, 0, 1);
  const slamScale = 1.0 + (1.0 - CM.easeOutExpo(slamProgress)) * 0.8;
  const slamAlpha = CM.clamp(slamProgress * 3.0, 0, 1);

  cx.save();
  cx.translate(W / 2, IS_VERTICAL ? H * 0.38 : H * 0.44);
  cx.scale(slamScale, slamScale);
  cx.globalAlpha = slamAlpha;

  cx.textAlign = 'center';
  cx.textBaseline = 'middle';
  cx.font = '900 ' + (IS_VERTICAL ? 104 : 112) + 'px Anton, sans-serif';
  cx.fillStyle = '#f2f0ea';
  cx.fillText('{topic.upper()}', 0, -50);

  cx.font = 'italic 700 ' + (IS_VERTICAL ? 54 : 58) + 'px "Instrument Serif", serif';
  cx.fillStyle = '#ffd60a';
  cx.fillText('Production Masterclass', 0, 36);
  cx.restore();

  // Overlay Karaoke captions
  drawKaraokeCaptions(cx, t);

  // Finishing pass (vignette + grain)
  drawFinishing(cx, t);
}}

// Playback Logic
let isPlaying = false;
let animReq = null;

function updateUI(t) {{
  scrubber.value = t;
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  const dm = Math.floor(DURATION / 60);
  const ds = Math.floor(DURATION % 60);
  timeDisp.textContent = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}} / ${{String(dm).padStart(2,'0')}}:${{String(ds).padStart(2,'0')}}`;
}}

function loop() {{
  if (!isPlaying) return;
  const t = audio.currentTime;
  renderScene(t);
  updateUI(t);
  if (t >= DURATION) {{
    pause();
    seek(0);
    return;
  }}
  animReq = requestAnimationFrame(loop);
}}

function play() {{
  isPlaying = true;
  playBtn.textContent = 'Pause';
  audio.play().catch(e => console.warn('Audio play error:', e));
  animReq = requestAnimationFrame(loop);
}}

function pause() {{
  isPlaying = false;
  playBtn.textContent = 'Play';
  audio.pause();
  if (animReq) cancelAnimationFrame(animReq);
}}

function seek(t) {{
  audio.currentTime = t;
  renderScene(t);
  updateUI(t);
}}

window.seek = seek;
window.DURATION = DURATION;

playBtn.addEventListener('click', () => isPlaying ? pause() : play());
scrubber.addEventListener('input', (e) => seek(parseFloat(e.target.value)));

// Initial Render
seek(0);
</script>
</body>
</html>"""
