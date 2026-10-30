#!/usr/bin/env python3
"""Complete Multi-Scene Non-Tech Inspiration Video Generator: The 30-Day Wall.

Demonstrates how non-tech motivational content maps into the Creator Motion Graphics engine:
- Scene 1: Hook ("MOST PEOPLE GIVE UP") + Red Strike + Yellow Serif Accent
- Scene 2: 3D Habit Calendar Mockup (drawYaw) with Plateau of Latent Potential
- Scene 3: 32° Temperature Phase Change & Ice Melting
- Scene 4: Stored Potential Breakthrough (Kinetic Slams)
- Scene 5: 99% Quitter Counter + White Flash Boom + Outlast the Silence Highlighter
- Scene 6: Red Rubber Stamp Rejection [ EXCUSES OBSOLETE ] + 3-Point Checklist + Golden CTA
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

OUT_DIR = Path("/home/omthakur/Downloads/AIVideoStudio/exports/creator_motion_30day_wall")
WORDS_JSON = OUT_DIR / "voiceover_words.json"
AUDIO_MP3 = OUT_DIR / "master_audio.mp3"
ART_DIR = Path("/home/omthakur/.gemini/antigravity/brain/7ab7d57d-d84c-4ab6-a5eb-fe9859973ff2")

words = json.loads(WORDS_JSON.read_text(encoding="utf-8"))

# Generate clean pop-in karaoke captions
clean_words = [w for w in words if w.get("word", "").strip() not in [".", ",", "!", "?", ":", ";"]]
captions = []
curr = [clean_words[0]]
for w in clean_words[1:]:
    gap = w["start_s"] - curr[-1]["end_s"]
    if len(curr) >= 3 or gap > 0.4:
        st = curr[0]["start_s"]
        en = max(curr[-1]["end_s"], st + 0.35)
        captions.append({
            "start": round(st, 3),
            "end": round(en, 3),
            "words": [{"word": x["word"].upper(), "start": x["start_s"], "end": x["end_s"]} for x in curr]
        })
        curr = [w]
    else:
        curr.append(w)
if curr:
    st = curr[0]["start_s"]
    en = max(curr[-1]["end_s"], st + 0.35)
    captions.append({
        "start": round(st, 3),
        "end": round(en, 3),
        "words": [{"word": x["word"].upper(), "start": x["start_s"], "end": x["end_s"]} for x in curr]
    })

captions_json = json.dumps(captions)
audio_base64 = "data:audio/mp3;base64," + base64.b64encode(AUDIO_MP3.read_bytes()).decode("utf-8")


def generate_html(is_vertical: bool) -> str:
    width = 1080 if is_vertical else 1280
    height = 1920 if is_vertical else 720
    aspect = "9 / 16" if is_vertical else "16 / 9"
    mode_name = "9:16 Shorts / Reels" if is_vertical else "16:9 Landscape Social"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>The 30-Day Wall — {mode_name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600;700;800;900&display=block">
<style>
:root {{
  color-scheme: dark;
  --bg: #09090b;
  --panel: #131316;
  --ink: #f4f1ea;
  --dim: #8e8d94;
  --line: #26262e;
  --accent: #ffd60a;
  --green: #30d158;
  --red: #ff3b30;
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
.wrap {{
  width: 100%;
  max-width: {"460px" if is_vertical else "1180px"};
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.top {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}}
.name {{
  font-family: var(--display);
  font-size: clamp(20px, 3.5vw, 30px);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.name em {{
  font-family: var(--serif);
  font-style: italic;
  color: var(--accent);
}}
.badge {{
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #ffd60a;
  background: rgba(255, 214, 10, 0.15);
  border: 1px solid rgba(255, 214, 10, 0.35);
  padding: 4px 10px;
  border-radius: 999px;
}}
.stage {{
  position: relative;
  width: 100%;
  aspect-ratio: {aspect};
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--line);
  box-shadow: 0 25px 60px rgba(0,0,0,0.7);
}}
.stage canvas {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}}
.bar {{
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
  font: 600 13px var(--body);
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
  background: #26262e;
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

<div class="wrap">
  <div class="top">
    <h1 class="name">The 30-Day <em>Wall</em> Masterclass</h1>
    <span class="badge">{mode_name}</span>
  </div>

  <div class="stage">
    <canvas id="stage" width="{width}" height="{height}"></canvas>
  </div>

  <div class="bar">
    <button class="btn" id="playBtn">Play</button>
    <input type="range" class="scrub" id="scrubber" min="0" max="49.4" step="0.01" value="0">
    <div class="time" id="timeDisp">00:00 / 00:49</div>
  </div>
</div>

<audio id="masterAudio" preload="auto" src="{audio_base64}"></audio>

<script>
const DURATION = 49.4;
const IS_VERTICAL = {'true' if is_vertical else 'false'};
const W = {width};
const HH = {height};
const CAPTIONS = {captions_json};

const cv = document.getElementById('stage');
const cx = cv.getContext('2d');
const audio = document.getElementById('masterAudio');
const playBtn = document.getElementById('playBtn');
const scrubber = document.getElementById('scrubber');
const timeDisp = document.getElementById('timeDisp');

// Math helpers
const CM = {{
  clamp(x, a = 0, b = 1) {{ return Math.max(a, Math.min(b, x)); }},
  lerp(a, b, t) {{ return a + (b - a) * t; }},
  span(t, a, b) {{ return a === b ? (t >= a ? 1 : 0) : CM.clamp((t - a) / (b - a)); }},
  ez: {{
    out3(x) {{ x = CM.clamp(x); return 1 - Math.pow(1 - x, 3); }},
    inout3(x) {{ x = CM.clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }},
    outExpo(x) {{ return x >= 1 ? 1 : 1 - Math.pow(2, -10 * x); }},
    outBack(x, c = 1.70158) {{ return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }}
  }},
  rng(seed) {{
    let s = (typeof seed === 'string' ? seed.split('').reduce((a, b) => (a << 5) - a + b.charCodeAt(0), 0) : seed) >>> 0 || 1;
    s = (s ^ (s << 13)) >>> 0; s = (s ^ (s >>> 17)) >>> 0; s = (s ^ (s << 5)) >>> 0;
    const f = () => {{ s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }};
    f.in = (a, b) => a + (b - a) * f();
    return f;
  }},
  layer(w, h) {{
    const c = document.createElement('canvas'); c.width = w; c.height = h; return c;
  }}
}};

const {{ clamp, lerp, span, rng, ez }} = CM;
const C = {{
  bg: '#09090b', ink: '#f4f1ea', dim: '#8e8d94', panel: '#151518',
  line: '#26262e', accent: '#ffd60a', green: '#30d158', red: '#ff3b30', cyan: '#38bdf8'
}};

const disp = (px) => `${{px}}px "Anton", Impact, sans-serif`;
const inter = (px, w = 600) => `${{w}} ${{px}}px "Inter", sans-serif`;
const serif = (px) => `italic ${{px}}px "Instrument Serif", Georgia, serif`;

const CUTS = [
  {{ t: 7.2, d: 0.28, type: 'whip', dir: 1 }},
  {{ t: 15.5, d: 0.24, type: 'glitch' }},
  {{ t: 23.8, d: 0.26, type: 'whipV', dir: 1 }},
  {{ t: 32.5, d: 0.16, type: 'flash' }},
  {{ t: 41.0, d: 0.24, type: 'glitch' }}
];

const PUNCH = [
  {{ t: 0.25, a: 0.04 }}, {{ t: 2.1, a: 0.09 }}, {{ t: 6.2, a: 0.06 }},
  {{ t: 18.0, a: 0.05 }}, {{ t: 22.8, a: 0.08 }}, {{ t: 35.2, a: 0.18, k: 1.6 }},
  {{ t: 43.0, a: 0.12 }}, {{ t: 47.5, a: 0.08 }}
];

const SHAKE = [
  {{ t: 2.1, a: 8 }}, {{ t: 22.8, a: 8 }}, {{ t: 35.2, a: 22, k: 6 }},
  {{ t: 43.0, a: 18 }}
];

const word = (s, t, font, color, extra) => Object.assign({{ s, t, font, color: color || C.ink }}, extra || {{}});
function measure(c, it) {{ c.font = it.font; return c.measureText(it.s).width; }}
function row(c, items, x, y, gap, align = 'center') {{
  let tot = 0; items.forEach(it => {{ it.w = measure(c, it); tot += it.w; }}); tot += gap * (items.length - 1);
  let cxCoord = align === 'center' ? x - tot / 2 : x;
  items.forEach(it => {{ it.x = cxCoord; it.cx = cxCoord + it.w / 2; it.y = y; cxCoord += it.w + gap; }});
  return {{ x0: align === 'center' ? x - tot / 2 : x, w: tot }};
}}

function slam(c, it, t, o = {{}}) {{
  if (t < it.t) return;
  const u = span(t, it.t, it.t + (o.dur || 0.2)), e = ez.outExpo(u), s = lerp(o.from || 1.45, 1, e);
  c.save(); c.translate(it.cx, it.y); c.scale(s, s);
  c.globalAlpha = (o.alpha == null ? 1 : o.alpha) * Math.min(1, u * 3.5);
  if (u < 1 && !o.noBlur) {{ const b = (1 - e) * 8; if (b > 0.5) c.filter = `blur(${{b.toFixed(1)}}px)`; }}
  c.font = it.font; c.textAlign = 'center'; c.textBaseline = it.base || 'middle';
  if (o.glow) {{ c.shadowColor = o.glow; c.shadowBlur = o.glowBlur || 35; }}
  c.fillStyle = o.color || it.color; c.fillText(it.s, 0, 0);
  c.restore();
}}

function strike(c, x0, x1, y, p, col = C.red, w = 14) {{
  if (p <= 0) return; const e = ez.out3(clamp(p)), x = lerp(x0, x1, e);
  c.save(); c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.shadowColor = col; c.shadowBlur = 12;
  c.beginPath(); c.moveTo(x0, y); c.lineTo(x, y - 6); c.stroke(); c.restore();
}}

function rr(c, x, y, w, h, r) {{ c.beginPath(); c.roundRect(x, y, w, h, r); }}

function drawYaw(c, src, cxCoord, cyCoord, w, h, yaw, alpha = 1.0) {{
  const f = 1500, cs = Math.cos(yaw), sn = Math.sin(yaw);
  const proj = (x) => {{ const X = x * cs, Z = x * sn, k = f / (f + Z); return {{ x: cxCoord + X * k, k }}; }};
  const L = proj(-w / 2), R = proj(w / 2);
  c.save(); c.globalAlpha = alpha;
  const sw = 4;
  for (let sx = 0; sx < src.width; sx += sw) {{
    const p0 = proj((sx / src.width - 0.5) * w), p1 = proj(((sx + sw) / src.width - 0.5) * w), hh = (h * (p0.k + p1.k)) / 2;
    c.drawImage(src, sx, 0, sw, src.height, p0.x, cyCoord - hh / 2, p1.x - p0.x + 0.8, hh);
  }}
  c.restore();
}}

let STAMP = null;
function getStampLayer(text, color) {{
  if (STAMP) return STAMP;
  STAMP = CM.layer(420, 200); const x = STAMP.getContext('2d');
  x.strokeStyle = color; x.lineWidth = 12; rr(x, 10, 10, 400, 180, 20); x.stroke();
  x.fillStyle = color; x.font = disp(110); x.textAlign = 'center'; x.textBaseline = 'middle'; x.letterSpacing = '5px';
  x.fillText(text, 210, 105);
  x.globalCompositeOperation = 'destination-out'; const r = rng('stamp' + text);
  for (let i = 0; i < 400; i++) {{ x.globalAlpha = r.in(0.3, 1); x.beginPath(); x.arc(r() * 420, r() * 200, r.in(0.8, 3.0), 0, 7); x.fill(); }}
  return STAMP;
}}

function background(c, t) {{
  c.fillStyle = C.bg; c.fillRect(0, 0, W, HH);
  const glow = (x, y, r, col) => {{ const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, HH); }};
  glow(W * 0.25, HH * 0.25, 650, 'rgba(255, 214, 10, 0.055)');
  glow(W * 0.8, HH * 0.75, 650, 'rgba(48, 209, 88, 0.045)');

  c.save(); c.strokeStyle = 'rgba(244,241,234,0.025)'; c.lineWidth = 1; c.beginPath();
  const off = (t * 8) % 80;
  for (let x = -off; x < W; x += 80) {{ c.moveTo(x, 0); c.lineTo(x, HH); }}
  for (let y = -off * 0.5; y < HH; y += 80) {{ c.moveTo(0, y); c.lineTo(W, y); }}
  c.stroke(); c.restore();
}}

function finishing(c, t) {{
  const vig = c.createRadialGradient(W / 2, HH / 2, Math.min(W, HH) * 0.45, W / 2, HH / 2, Math.max(W, HH) * 0.85);
  vig.addColorStop(0, 'rgba(0,0,0,0)'); vig.addColorStop(1, 'rgba(0,0,0,0.65)');
  c.fillStyle = vig; c.fillRect(0, 0, W, HH);
}}

function chrome(c, t) {{
  const a = span(t, 7.3, 7.7) * (1 - span(t, 47.0, 47.5));
  if (a <= 0) return;
  c.save(); c.globalAlpha = a;
  const topY = IS_VERTICAL ? 180 : 48;
  const leftX = IS_VERTICAL ? 70 : 64;
  c.fillStyle = C.accent; c.fillRect(leftX, topY, 10, 10);
  c.font = inter(IS_VERTICAL ? 24 : 26, 700); c.letterSpacing = '3px'; c.fillStyle = C.dim; c.textBaseline = 'middle';
  c.fillText('MINDSET · THE 30-DAY WALL', leftX + 22, topY + 6);
  c.restore();
}}

function drawCaptions(c, t) {{
  const group = CAPTIONS.find(g => t >= g.start - 0.05 && t <= g.end + 0.35);
  if (!group) return;

  const y = IS_VERTICAL ? HH * 0.74 : HH - 65;
  const fontSize = IS_VERTICAL ? 46 : 34;
  const gap = IS_VERTICAL ? 14 : 12;

  c.save();
  c.font = `800 ${{fontSize}}px "Inter", sans-serif`;
  c.textBaseline = 'middle';

  let totalW = 0;
  group.words.forEach(w => {{ w.w = c.measureText(w.word).width; totalW += w.w; }});
  totalW += gap * (group.words.length - 1);

  const padX = IS_VERTICAL ? 28 : 22, padY = IS_VERTICAL ? 14 : 10;
  const pillH = fontSize + padY * 2;
  const pillW = totalW + padX * 2;
  c.fillStyle = 'rgba(12, 12, 16, 0.88)'; c.strokeStyle = 'rgba(255, 255, 255, 0.15)'; c.lineWidth = 1.5;
  rr(c, W / 2 - pillW / 2, y - pillH / 2, pillW, pillH, 16);
  c.fill(); c.stroke();

  let curX = W / 2 - totalW / 2;
  group.words.forEach(w => {{
    const isActive = t >= w.start && t <= w.end;
    const wasActive = t > w.end;
    c.save(); c.translate(curX + w.w / 2, y);
    if (isActive) {{
      c.scale(1.15, 1.15); c.fillStyle = '#ffd60a'; c.shadowColor = 'rgba(255, 214, 10, 0.7)'; c.shadowBlur = 18;
    }} else if (wasActive) {{
      c.fillStyle = '#f4f1ea';
    }} else {{
      c.fillStyle = 'rgba(244, 241, 234, 0.5)';
    }}
    c.textAlign = 'center'; c.fillText(w.word, 0, 0); c.restore();
    curX += w.w + gap;
  }});
  c.restore();
}}

// =================================== SCENES ===================================

// Scene 1: Hook (0.0s - 7.2s)
function sceneHook(c, t) {{
  if (IS_VERTICAL) {{
    // 9:16 Mobile Vertical Layout (Strict Safe Zones: Left/Right > 120px padding)
    const sy = 440;
    const r1 = [word('MOST PEOPLE', 0.25, disp(84), C.ink)];
    const r2 = [word('GIVE UP', 0.9, disp(84), C.ink)];
    const r3 = [word('RIGHT BEFORE', 1.8, disp(90), C.red)];
    const r4 = [word('SUCCESS.', 2.4, disp(90), C.ink)];

    row(c, r1, W / 2, sy, 0);
    row(c, r2, W / 2, sy + 95, 0);
    const b3 = row(c, r3, W / 2, sy + 205, 0);
    const b4 = row(c, r4, W / 2, sy + 300, 0);

    const dimA = 1 - 0.6 * span(t, 3.2, 3.5);
    r1.forEach(it => slam(c, it, t, {{ alpha: dimA }}));
    r2.forEach(it => slam(c, it, t, {{ alpha: dimA }}));
    r3.forEach(it => slam(c, it, t, {{ alpha: dimA, from: 1.5 }}));
    r4.forEach(it => slam(c, it, t, {{ alpha: dimA, from: 1.5 }}));

    strike(c, b3.x0 - 24, b3.x0 + b3.w + 24, sy + 205, span(t, 3.2, 3.5), C.red, 16);
    strike(c, b4.x0 - 24, b4.x0 + b4.w + 24, sy + 300, span(t, 3.2, 3.5), C.red, 16);

    if (t >= 4.2) {{
      const sub1 = [word('they hit what psychologists call', 4.2, inter(28, 600), C.dim, {{ base: 'middle' }})];
      const sub2 = [word('the thirty-day wall.', 5.5, serif(78), C.accent, {{ base: 'middle' }})];
      row(c, sub1, W / 2, sy + 430, 0);
      row(c, sub2, W / 2, sy + 510, 0);
      slam(c, sub1[0], t, {{ from: 1.15 }});
      slam(c, sub2[0], t, {{ from: 1.6, glow: 'rgba(255,214,10,0.5)', glowBlur: 40 }});
    }}
  }} else {{
    // 16:9 Landscape Layout
    const sy = 200;
    const r1 = [word('MOST PEOPLE', 0.25, disp(110), C.ink), word('GIVE UP', 1.0, disp(110), C.ink)];
    const r2 = [word('RIGHT BEFORE', 1.8, disp(120), C.red), word('SUCCESS.', 2.4, disp(120), C.ink)];
    row(c, r1, W / 2, sy, 24);
    const b2 = row(c, r2, W / 2, sy + 110, 26);

    const dimA = 1 - 0.6 * span(t, 3.2, 3.5);
    r1.forEach(it => slam(c, it, t, {{ alpha: dimA }}));
    r2.forEach(it => slam(c, it, t, {{ alpha: dimA, from: 1.6 }}));
    strike(c, b2.x0 - 24, b2.x0 + b2.w + 24, sy + 110, span(t, 3.2, 3.5), C.red, 16);

    if (t >= 4.2) {{
      const r3 = [
        word('they hit what psychologists call', 4.2, inter(34, 600), C.dim, {{ base: 'alphabetic' }}),
        word('the thirty-day wall.', 5.5, serif(92), C.accent, {{ base: 'alphabetic' }})
      ];
      row(c, r3, W / 2, sy + 220, 20);
      slam(c, r3[0], t, {{ from: 1.15 }});
      slam(c, r3[1], t, {{ from: 1.6, glow: 'rgba(255,214,10,0.4)', glowBlur: 40 }});
    }}
  }}
}}

// Scene 2: 3D Habit Calendar Mockup (7.2s - 15.5s)
let HABIT_CARD = null;
function getHabitCard() {{
  if (HABIT_CARD) return HABIT_CARD;
  HABIT_CARD = CM.layer(IS_VERTICAL ? 740 : 700, IS_VERTICAL ? 540 : 420);
  const x = HABIT_CARD.getContext('2d');
  const w = HABIT_CARD.width, h = HABIT_CARD.height;
  x.fillStyle = 'rgba(18, 18, 24, 0.95)'; x.strokeStyle = 'rgba(255, 214, 10, 0.35)'; x.lineWidth = 2;
  rr(x, 10, 10, w - 20, h - 20, 18); x.fill(); x.stroke();

  x.fillStyle = '#ffd60a'; x.font = '800 24px "Inter", sans-serif';
  x.fillText('📅 30-DAY HABIT STREAK TRACKER', 40, 50);

  // 30 day grid
  const cellW = (w - 80) / 7, cellH = (h - 180) / 5;
  for (let day = 1; day <= 30; day++) {{
    const row = Math.floor((day - 1) / 7), col = (day - 1) % 7;
    const cxP = 40 + col * cellW, cyP = 85 + row * cellH;
    if (day <= 21) {{
      x.fillStyle = 'rgba(255, 59, 48, 0.15)'; x.strokeStyle = '#ff3b30';
    }} else if (day <= 29) {{
      x.fillStyle = 'rgba(255, 214, 10, 0.15)'; x.strokeStyle = '#ffd60a';
    }} else {{
      x.fillStyle = 'rgba(48, 209, 88, 0.25)'; x.strokeStyle = '#30d158';
    }}
    x.lineWidth = 1.5; rr(x, cxP, cyP, cellW - 8, cellH - 8, 8); x.fill(); x.stroke();
    x.fillStyle = '#f4f1ea'; x.font = '700 16px "Inter", sans-serif';
    x.textAlign = 'center'; x.fillText(day, cxP + (cellW - 8) / 2, cyP + (cellH - 8) / 2 + 5);
  }}

  // Warning pill
  x.fillStyle = 'rgba(255, 59, 48, 0.9)'; rr(x, 40, h - 65, w - 80, 45, 10); x.fill();
  x.fillStyle = '#ffffff'; x.font = '800 16px "Inter", sans-serif'; x.textAlign = 'center';
  x.fillText('⚠ THE PLATEAU OF LATENT POTENTIAL (DAY 1 - 29)', w / 2, h - 37);

  return HABIT_CARD;
}}

function sceneHabit(c, t) {{
  const cy = IS_VERTICAL ? HH * 0.42 : HH * 0.48;
  const yaw = lerp(0.18, -0.05, ez.out3(span(t, 7.2, 15.5)));
  const card = getHabitCard();
  drawYaw(c, card, W / 2, cy, card.width, card.height, yaw, 1.0);
}}

// Scene 3: 32° Ice Cube Phase Change (15.5s - 23.8s)
function sceneIceCube(c, t) {{
  if (IS_VERTICAL) {{
    const sy = 400;
    const r1 = [word('THE ICE CUBE', 15.5, disp(82), C.cyan)];
    const r2 = [word('PHASE CHANGE', 16.2, disp(82), C.ink)];
    row(c, r1, W / 2, sy, 0);
    row(c, r2, W / 2, sy + 90, 0);
    r1.forEach(it => slam(c, it, t));
    r2.forEach(it => slam(c, it, t));

    const tProg = ez.out3(span(t, 17.5, 22.5));
    const temp = Math.round(lerp(25, 32, tProg));

    const cy = sy + 250;
    c.save(); c.translate(W / 2, cy);
    c.font = '900 120px "Anton", sans-serif';
    c.fillStyle = (temp >= 32) ? C.green : C.accent;
    c.shadowColor = (temp >= 32) ? 'rgba(48, 209, 88, 0.6)' : 'rgba(255, 214, 10, 0.6)';
    c.shadowBlur = 35;
    c.textAlign = 'center';
    c.fillText(temp + '° FAHRENHEIT', 0, 0);

    c.font = 'italic 700 36px "Instrument Serif", serif';
    c.fillStyle = C.ink;
    c.fillText((temp >= 32) ? '⚡ Radical Phase Change Begins!' : 'Heating room with zero visible change...', 0, 70);
    c.restore();
  }} else {{
    const sy = 180;
    const r1 = [word('THE ICE CUBE', 15.5, disp(84), C.cyan), word('PHASE CHANGE', 16.2, disp(84), C.ink)];
    row(c, r1, W / 2, sy, 20); r1.forEach(it => slam(c, it, t));

    const tProg = ez.out3(span(t, 17.5, 22.5));
    const temp = Math.round(lerp(25, 32, tProg));

    const cy = sy + 150;
    c.save(); c.translate(W / 2, cy);
    c.font = '900 110px "Anton", sans-serif';
    c.fillStyle = (temp >= 32) ? C.green : C.accent;
    c.shadowColor = (temp >= 32) ? 'rgba(48, 209, 88, 0.6)' : 'rgba(255, 214, 10, 0.6)';
    c.shadowBlur = 35;
    c.textAlign = 'center';
    c.fillText(temp + '° FAHRENHEIT', 0, 0);

    c.font = 'italic 700 36px "Instrument Serif", serif';
    c.fillStyle = C.ink;
    c.fillText((temp >= 32) ? '⚡ Radical Phase Change Begins!' : 'Heating room with zero visible change...', 0, 60);
    c.restore();
  }}
}}

// Scene 4: Stored Energy (23.8s - 32.5s)
function sceneEnergy(c, t) {{
  if (IS_VERTICAL) {{
    const sy = 430;
    const r1 = [word('THE STRUGGLE', 24.0, disp(82), C.ink)];
    const r2 = [word('WAS NOT WASTED.', 24.8, disp(82), C.accent)];
    row(c, r1, W / 2, sy, 0);
    row(c, r2, W / 2, sy + 95, 0);
    r1.forEach(it => slam(c, it, t));
    r2.forEach(it => slam(c, it, t));

    const r3 = [word('IT WAS STORED', 27.5, disp(78), C.cyan)];
    const r4 = [word('POTENTIAL.', 28.2, disp(78), C.green)];
    row(c, r3, W / 2, sy + 220, 0);
    row(c, r4, W / 2, sy + 305, 0);
    r3.forEach(it => slam(c, it, t));
    r4.forEach(it => slam(c, it, t));
  }} else {{
    const sy = 200;
    const r1 = [word('THE STRUGGLE', 24.0, disp(90), C.ink), word('WAS NOT WASTED.', 24.8, disp(90), C.accent)];
    row(c, r1, W / 2, sy, 20); r1.forEach(it => slam(c, it, t));

    const r2 = [word('IT WAS STORED', 27.5, disp(78), C.cyan), word('POTENTIAL.', 28.2, disp(78), C.green)];
    row(c, r2, W / 2, sy + 110, 20); r2.forEach(it => slam(c, it, t));
  }}
}}

// Scene 5: 99% Quitter Counter & White Flash (32.5s - 41.0s)
function sceneQuitter(c, t) {{
  if (IS_VERTICAL) {{
    const sy = 430;
    const count = Math.round(99 * ez.out3(span(t, 32.8, 35.2)));

    c.save(); c.translate(W / 2, sy);
    c.font = '900 180px "Anton", sans-serif'; c.fillStyle = C.green;
    c.shadowColor = 'rgba(48, 209, 88, 0.65)'; c.shadowBlur = 45; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(count + '%', 0, 0); c.restore();

    const r1 = [word('QUIT RIGHT AT', 35.2, disp(76), C.ink)];
    const r2 = [word('DAY TWENTY-NINE.', 36.0, disp(76), C.accent)];
    row(c, r1, W / 2, sy + 140, 0);
    row(c, r2, W / 2, sy + 225, 0);
    r1.forEach(it => slam(c, it, t));
    r2.forEach(it => slam(c, it, t));

    if (t >= 37.5) {{
      const s = ez.outBack(span(t, 37.5, 37.8));
      c.save(); c.translate(W / 2, sy + 330); c.scale(s, s);
      c.fillStyle = 'rgba(255, 214, 10, 0.15)'; c.strokeStyle = '#ffd60a'; c.lineWidth = 2;
      rr(c, -200, -30, 400, 60, 14); c.fill(); c.stroke();
      c.fillStyle = '#ffd60a'; c.font = '800 22px "Inter", sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText('⚡ OUTLAST THE SILENCE', 0, 0); c.restore();
    }}
  }} else {{
    const sy = 200;
    const count = Math.round(99 * ez.out3(span(t, 32.8, 35.2)));

    c.save(); c.translate(W / 2, sy);
    c.font = '900 180px "Anton", sans-serif'; c.fillStyle = C.green;
    c.shadowColor = 'rgba(48, 209, 88, 0.65)'; c.shadowBlur = 45; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(count + '%', 0, 0); c.restore();

    const r1 = [word('QUIT RIGHT AT', 35.2, disp(78), C.ink), word('DAY TWENTY-NINE.', 36.0, disp(78), C.accent)];
    row(c, r1, W / 2, sy + 130, 20); r1.forEach(it => slam(c, it, t));

    if (t >= 37.5) {{
      const s = ez.outBack(span(t, 37.5, 37.8));
      c.save(); c.translate(W / 2, sy + 220); c.scale(s, s);
      c.fillStyle = 'rgba(255, 214, 10, 0.15)'; c.strokeStyle = '#ffd60a'; c.lineWidth = 2;
      rr(c, -200, -30, 400, 60, 14); c.fill(); c.stroke();
      c.fillStyle = '#ffd60a'; c.font = '800 22px "Inter", sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText('⚡ OUTLAST THE SILENCE', 0, 0); c.restore();
    }}
  }}
}}

// Scene 6: Stamp & Final Push (41.0s - 49.4s)
function sceneStamp(c, t) {{
  const sy = IS_VERTICAL ? 400 : 160;
  const r1 = [word('EXCUSES & DOUBT', 41.2, disp(IS_VERTICAL ? 110 : 96), C.red)];
  const b = row(c, r1, W / 2, sy, 22); r1.forEach(it => slam(c, it, t));
  strike(c, b.x0 - 20, b.x0 + b.w + 20, sy, span(t, 42.4, 42.7), C.red, 18);

  if (t >= 43.0) {{
    const u = span(t, 43.0, 43.25);
    const s = lerp(2.2, 1.0, ez.outExpo(u));
    const stamp = getStampLayer('OBSOLETE', C.red);
    c.save(); c.translate(W / 2, sy + 30); c.rotate(-0.14); c.scale(s, s);
    c.globalAlpha = Math.min(1, u * 4);
    c.drawImage(stamp, -stamp.width / 2, -stamp.height / 2);
    c.restore();
  }}

  // 3 Checkmarks
  const items = [
    {{ text: 'Embrace the Boring Chapters', t: 44.5 }},
    {{ text: 'Trust the Daily Grind', t: 45.8 }},
    {{ text: 'Break the 30-Day Wall', t: 47.0 }}
  ];
  let curY = sy + (IS_VERTICAL ? 200 : 150);
  items.forEach(it => {{
    if (t < it.t) return;
    const s = ez.outBack(span(t, it.t, it.t + 0.22));
    c.save(); c.translate(W / 2, curY); c.scale(s, s);
    c.fillStyle = 'rgba(255, 255, 255, 0.05)'; c.strokeStyle = '#30d158'; c.lineWidth = 1.5;
    rr(c, -260, -26, 520, 52, 12); c.fill(); c.stroke();
    c.fillStyle = '#30d158'; c.font = '800 20px "Inter", sans-serif'; c.textAlign = 'left'; c.textBaseline = 'middle';
    c.fillText('✓  ' + it.text, -230, 0); c.restore();
    curY += IS_VERTICAL ? 80 : 64;
  }});
}}

// =================================== COMPOSITOR ===================================
const SCENES = [sceneHook, sceneHabit, sceneIceCube, sceneEnergy, sceneQuitter, sceneStamp];

function getSceneIndex(t) {{
  let idx = 0; for (const cut of CUTS) if (t >= cut.t) idx++;
  return Math.min(idx, SCENES.length - 1);
}}

function getCamera(t) {{
  let z = 1.0, dx = 0, dy = 0;
  for (const p of PUNCH) {{
    const d = t - p.t;
    if (d >= 0 && d < 0.4) z += p.a * (d < 0.06 ? ez.out3(d / 0.06) : Math.exp(-(d - 0.06) * (p.k || 3.0)));
  }}
  for (const s of SHAKE) {{
    const d = t - s.t;
    if (d >= 0 && d < 0.8) {{
      const e = s.a * Math.exp(-d * 7.0);
      dx += (rng('sx' + Math.floor(t * 30))() * 2 - 1) * e;
      dy += (rng('sy' + Math.floor(t * 30))() * 2 - 1) * e;
    }}
  }}
  return {{ z, dx, dy }};
}}

function renderScene(t) {{
  background(cx, t);
  const cam = getCamera(t);
  cx.save();
  cx.translate(W / 2 + cam.dx, HH / 2 + cam.dy); cx.scale(cam.z, cam.z); cx.translate(-W / 2, -HH / 2);

  let inCut = false;
  for (const cut of CUTS) {{
    if (t >= cut.t - cut.d / 2 && t <= cut.t + cut.d / 2) {{
      inCut = true;
      const u = (t - (cut.t - cut.d / 2)) / cut.d;
      if (cut.type === 'whip') {{
        const offX = lerp(0, -W * cut.dir, ez.inout3(u));
        cx.save(); cx.translate(offX, 0); SCENES[getSceneIndex(cut.t - 0.1)](cx, t); cx.restore();
        cx.save(); cx.translate(offX + W * cut.dir, 0); SCENES[getSceneIndex(cut.t + 0.1)](cx, t); cx.restore();
      }} else if (cut.type === 'flash') {{
        SCENES[getSceneIndex(t)](cx, t);
        const flashA = 1 - Math.abs(u - 0.5) * 2;
        cx.fillStyle = `rgba(255, 255, 255, ${{flashA * 0.9}})`; cx.fillRect(0, 0, W, HH);
      }} else {{
        SCENES[getSceneIndex(t)](cx, t);
        cx.fillStyle = `rgba(255, 214, 10, 0.25)`; cx.fillRect(0, (rng(t)() * HH), W, 20);
      }}
      break;
    }}
  }}

  if (!inCut) SCENES[getSceneIndex(t)](cx, t);
  cx.restore();

  if (t >= 35.2 && t <= 35.8) {{
    const fa = (1 - (t - 35.2) / 0.6) * 0.7;
    cx.fillStyle = `rgba(255, 255, 255, ${{fa}})`; cx.fillRect(0, 0, W, HH);
  }}

  chrome(cx, t);
  drawCaptions(cx, t);
  finishing(cx, t);
}}

let isPlaying = false;
let animReq = null;

function updateUI(t) {{
  scrubber.value = t;
  const m = Math.floor(t / 60), s = Math.floor(t % 60);
  timeDisp.textContent = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}} / 00:49`;
}}

function loop() {{
  if (!isPlaying) return;
  const t = audio.currentTime;
  renderScene(t); updateUI(t);
  if (t >= DURATION) {{ pause(); seek(0); return; }}
  animReq = requestAnimationFrame(loop);
}}

function play() {{
  isPlaying = true; playBtn.textContent = 'Pause';
  audio.play().catch(e => console.warn(e));
  animReq = requestAnimationFrame(loop);
}}

function pause() {{
  isPlaying = false; playBtn.textContent = 'Play';
  audio.pause();
  if (animReq) cancelAnimationFrame(animReq);
}}

function seek(t) {{
  audio.currentTime = t;
  renderScene(t); updateUI(t);
}}

window.seek = seek;
window.DURATION = DURATION;

playBtn.addEventListener('click', () => isPlaying ? pause() : play());
scrubber.addEventListener('input', (e) => seek(parseFloat(e.target.value)));

seek(0);
</script>
</body>
</html>"""


# Generate HTML files
html_16x9 = generate_html(is_vertical=False)
html_9x16 = generate_html(is_vertical=True)

(OUT_DIR / "30day_wall_16x9_social.html").write_text(html_16x9, encoding="utf-8")
(OUT_DIR / "30day_wall_9x16_shorts.html").write_text(html_9x16, encoding="utf-8")
(ART_DIR / "30day_wall_16x9_social.html").write_text(html_16x9, encoding="utf-8")
(ART_DIR / "30day_wall_9x16_shorts.html").write_text(html_9x16, encoding="utf-8")

print("Generated full multi-scene 16:9 & 9:16 HTML players for 30-Day Wall Motivation!")
