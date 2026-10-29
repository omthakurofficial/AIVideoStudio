#!/usr/bin/env python3
"""Complete Multi-Scene Creator Motion Graphics Generator for Docker Containers.

Features:
- 7 Dynamic scenes synchronized to Kokoro neural voiceover:
  1. sceneHook: "STOP DEPLOYING VIRTUAL MACHINES" + red strike + yellow serif italic accent
  2. sceneVMStack: 3D tilted VM stack diagram with 4GB guest OS bloat and 60s boot warnings
  3. sceneKernelSharing: 3D browser/engine mockup (drawYaw) with namespaces & cgroups
  4. sceneFastContainers: Sub-100ms speedometer (85ms) + 3 container cards popping with overshoot
  5. sceneRollingStat: 90% glowing green counter locking with white flash, boom, and highlighter swipe
  6. sceneMonolithStamp: "MONOLITHIC INFRASTRUCTURE" with tactile [ DEPRECATED ] rubber stamp
  7. sceneTakeaway: 3-point checklist cards and gold CTA
- Dual 16:9 Landscape (1280x720) & 9:16 Vertical Shorts (1080x1920) with safe margins
- Word-by-word karaoke pop-in captions
- Embedded Base64 master audio (voice + ducked 122 BPM tech beat)
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

OUT_DIR = Path("/home/omthakur/Downloads/AIVideoStudio/exports/creator_motion_docker_containers")
WORDS_JSON = OUT_DIR / "voiceover_words.json"
AUDIO_MP3 = OUT_DIR / "master_audio.mp3"
ART_DIR = Path("/home/omthakur/.gemini/antigravity/brain/7ab7d57d-d84c-4ab6-a5eb-fe9859973ff2")

words = json.loads(WORDS_JSON.read_text(encoding="utf-8"))

# Generate 2-3 word pop-in karaoke captions
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


def generate_player(is_vertical: bool) -> str:
    width = 1080 if is_vertical else 1280
    height = 1920 if is_vertical else 720
    aspect = "9 / 16" if is_vertical else "16 / 9"
    mode_name = "9:16 Shorts / Reels" if is_vertical else "16:9 Landscape Social"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Docker Containers — {mode_name}</title>
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
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.35);
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
    <h1 class="name">Docker <em>Architecture</em> Masterclass</h1>
    <span class="badge">{mode_name}</span>
  </div>

  <div class="stage">
    <canvas id="stage" width="{width}" height="{height}"></canvas>
  </div>

  <div class="bar">
    <button class="btn" id="playBtn">Play</button>
    <input type="range" class="scrub" id="scrubber" min="0" max="32.65" step="0.01" value="0">
    <div class="time" id="timeDisp">00:00 / 00:32</div>
  </div>
</div>

<audio id="masterAudio" preload="auto" src="{audio_base64}"></audio>

<script>
const DURATION = 32.65;
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

// =================================== MATH HELPERS ===================================
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
    s = (s ^ (s << 13)) >>> 0;
    s = (s ^ (s >>> 17)) >>> 0;
    s = (s ^ (s << 5)) >>> 0;
    const f = () => {{ s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }};
    f.in = (a, b) => a + (b - a) * f();
    return f;
  }},
  noise1(seed) {{
    const r = CM.rng(seed);
    const table = Array.from({{ length: 256 }}, () => r() * 2 - 1);
    return (x) => {{
      const i = Math.floor(x) & 255, f = x - Math.floor(x), u = f * f * (3 - 2 * f);
      return (1 - u) * table[i] + u * table[(i + 1) & 255];
    }};
  }},
  layer(w, h) {{
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    return c;
  }}
}};

const {{ clamp, lerp, span, rng, noise1, ez }} = CM;
const C = {{
  bg: '#09090b',
  ink: '#f4f1ea',
  dim: '#8e8d94',
  panel: '#151518',
  line: '#26262e',
  accent: '#ffd60a',
  green: '#30d158',
  red: '#ff3b30',
  cyan: '#38bdf8',
  orange: '#ff9900'
}};

const disp = (px) => `${{px}}px "Anton", Impact, sans-serif`;
const inter = (px, w = 600) => `${{w}} ${{px}}px "Inter", sans-serif`;
const serif = (px) => `italic ${{px}}px "Instrument Serif", Georgia, serif`;

// =================================== TIMELINES & CUTS ===================================
const TL = {{
  hook: {{ w1: [0.25, 0.54], w2: [0.95, 1.48], strike: 1.90, shift: 2.10, single: 2.50, service: 3.31 }},
  stack: {{ pill: 4.50, app: 5.20, os: 6.20, bloat: 7.20, boot: 8.50 }},
  engine: {{ pill: 10.90, daemon: 11.40, pid: 12.00, net: 13.00, cgroups: 14.00 }},
  speed: {{ pill: 15.60, timer: 16.00, c1: 17.00, c2: 17.80, c3: 18.60 }},
  metric: {{ roll: [20.60, 22.80], lock: 22.80, label: 23.20, swipe: 24.50 }},
  stamp: {{ mono: 27.80, strike: 28.50, stamp: 28.85 }},
  take: {{ check1: 30.40, check2: 30.90, check3: 31.40, gold: 31.90 }}
}};

const CUTS = [
  {{ t: 4.20, d: 0.28, type: 'whip', dir: 1 }},
  {{ t: 10.70, d: 0.24, type: 'glitch' }},
  {{ t: 15.40, d: 0.26, type: 'whipV', dir: 1 }},
  {{ t: 20.40, d: 0.16, type: 'flash' }},
  {{ t: 27.60, d: 0.24, type: 'glitch' }},
  {{ t: 30.30, d: 0.26, type: 'whip', dir: -1 }}
];

const PUNCH = [
  {{ t: 0.25, a: 0.04 }}, {{ t: 1.48, a: 0.09 }}, {{ t: 3.31, a: 0.05 }},
  {{ t: 7.20, a: 0.06 }}, {{ t: 12.00, a: 0.05 }}, {{ t: 16.00, a: 0.05 }},
  {{ t: 22.80, a: 0.18, k: 1.6 }}, {{ t: 28.85, a: 0.12 }}, {{ t: 31.90, a: 0.08 }}
];

const SHAKE = [
  {{ t: 1.48, a: 8 }}, {{ t: 7.20, a: 7 }}, {{ t: 22.80, a: 22, k: 6 }},
  {{ t: 28.85, a: 18 }}, {{ t: 31.90, a: 9 }}
];

// =================================== DRAWING PRIMITIVES ===================================
const word = (s, t, font, color, extra) => Object.assign({{ s, t, font, color: color || C.ink }}, extra || {{}});
function measure(c, it) {{ c.font = it.font; return c.measureText(it.s).width; }}
function row(c, items, x, y, gap, align = 'center') {{
  let tot = 0; items.forEach((it) => {{ it.w = measure(c, it); tot += it.w; }}); tot += gap * (items.length - 1);
  let cxCoord = align === 'center' ? x - tot / 2 : x;
  items.forEach((it) => {{ it.x = cxCoord; it.cx = cxCoord + it.w / 2; it.y = y; cxCoord += it.w + gap; }});
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

function drawYaw(c, src, cxCoord, cyCoord, w, h, yaw, alpha) {{
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
function stampLayer(text, color) {{
  if (STAMP) return STAMP;
  STAMP = CM.layer(420, 200); const x = STAMP.getContext('2d');
  x.strokeStyle = color; x.lineWidth = 12; rr(x, 10, 10, 400, 180, 20); x.stroke();
  x.fillStyle = color; x.font = disp(110); x.textAlign = 'center'; x.textBaseline = 'middle'; x.letterSpacing = '5px';
  x.fillText(text, 210, 105);
  x.globalCompositeOperation = 'destination-out'; const r = rng('stamp' + text);
  for (let i = 0; i < 400; i++) {{ x.globalAlpha = r.in(0.3, 1); x.beginPath(); x.arc(r() * 420, r() * 200, r.in(0.8, 3.0), 0, 7); x.fill(); }}
  return STAMP;
}}

// =================================== BACKGROUND & FINISHING ===================================
function background(c, t) {{
  c.fillStyle = C.bg; c.fillRect(0, 0, W, HH);
  const glow = (x, y, r, col) => {{ const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, HH); }};
  glow(W * 0.25, HH * 0.25, 650, 'rgba(56, 189, 248, 0.05)');
  glow(W * 0.8, HH * 0.75, 650, 'rgba(48, 209, 88, 0.045)');

  // Grid
  c.save(); c.strokeStyle = 'rgba(244,241,234,0.025)'; c.lineWidth = 1; c.beginPath();
  const off = (t * 10) % 80;
  for (let x = -off; x < W; x += 80) {{ c.moveTo(x, 0); c.lineTo(x, HH); }}
  for (let y = -off * 0.5; y < HH; y += 80) {{ c.moveTo(0, y); c.lineTo(W, y); }}
  c.stroke(); c.restore();
}}

function finishing(c, t) {{
  // Vignette
  const vig = c.createRadialGradient(W / 2, HH / 2, Math.min(W, HH) * 0.45, W / 2, HH / 2, Math.max(W, HH) * 0.85);
  vig.addColorStop(0, 'rgba(0,0,0,0)');
  vig.addColorStop(1, 'rgba(0,0,0,0.65)');
  c.fillStyle = vig;
  c.fillRect(0, 0, W, HH);
}}

function chrome(c, t) {{
  const a = span(t, 4.3, 4.7) * (1 - span(t, 30.1, 30.5));
  if (a <= 0) return;
  c.save(); c.globalAlpha = a;
  const topY = IS_VERTICAL ? 180 : 48;
  const leftX = IS_VERTICAL ? 70 : 64;
  c.fillStyle = C.cyan; c.fillRect(leftX, topY, 10, 10);
  c.font = inter(IS_VERTICAL ? 24 : 26, 700); c.letterSpacing = '3px'; c.fillStyle = C.dim; c.textBaseline = 'middle';
  c.fillText('DOCKER · CONTAINER ARCHITECTURE', leftX + 22, topY + 6);
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
  group.words.forEach(w => {{
    w.w = c.measureText(w.word).width;
    totalW += w.w;
  }});
  totalW += gap * (group.words.length - 1);

  const padX = IS_VERTICAL ? 28 : 22, padY = IS_VERTICAL ? 14 : 10;
  const pillH = fontSize + padY * 2;
  const pillW = totalW + padX * 2;
  c.fillStyle = 'rgba(12, 12, 16, 0.88)';
  c.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  c.lineWidth = 1.5;
  rr(c, W / 2 - pillW / 2, y - pillH / 2, pillW, pillH, 16);
  c.fill(); c.stroke();

  let curX = W / 2 - totalW / 2;
  group.words.forEach(w => {{
    const isActive = t >= w.start && t <= w.end;
    const wasActive = t > w.end;

    c.save();
    c.translate(curX + w.w / 2, y);
    if (isActive) {{
      c.scale(1.15, 1.15);
      c.fillStyle = '#ffd60a';
      c.shadowColor = 'rgba(255, 214, 10, 0.7)';
      c.shadowBlur = 18;
    }} else if (wasActive) {{
      c.fillStyle = '#f4f1ea';
    }} else {{
      c.fillStyle = 'rgba(244, 241, 234, 0.5)';
    }}
    c.textAlign = 'center';
    c.fillText(w.word, 0, 0);
    c.restore();

    curX += w.w + gap;
  }});
  c.restore();
}}

// =================================== SCENE DEFINITIONS ===================================

// Scene 0: Hook (0.00s - 4.20s)
function sceneHook(c, t) {{
  const H = TL.hook;
  const sy = IS_VERTICAL ? 520 : 200;
  const gapY = IS_VERTICAL ? 140 : 110;
  const sh = lerp(0, -40, ez.inout3(span(t, H.shift, H.shift + 0.3)));

  const r1 = [word('STOP', H.w1[0], disp(IS_VERTICAL ? 120 : 110), C.ink), word('DEPLOYING', H.w1[1], disp(IS_VERTICAL ? 120 : 110), C.ink)];
  const r2 = [word('VIRTUAL', H.w2[0], disp(IS_VERTICAL ? 150 : 140), C.red), word('MACHINES.', H.w2[1], disp(IS_VERTICAL ? 150 : 140), C.ink)];
  row(c, r1, W / 2, sy + sh, 24);
  const b2 = row(c, r2, W / 2, sy + gapY + sh, 26);

  const dimA = 1 - 0.6 * span(t, H.strike, H.strike + 0.18);
  r1.forEach(it => slam(c, it, t, {{ alpha: dimA }}));
  r2.forEach(it => slam(c, it, t, {{ alpha: dimA, from: 1.6 }}));
  strike(c, b2.x0 - 24, b2.x0 + b2.w + 24, sy + gapY + sh, span(t, H.strike, H.strike + 0.16), C.red, 16);

  if (t >= H.single) {{
    const r3 = [
      word('just for a', H.single, inter(IS_VERTICAL ? 40 : 36, 600), C.dim, {{ base: 'alphabetic' }}),
      word('single service.', H.service, serif(IS_VERTICAL ? 104 : 92), C.accent, {{ base: 'alphabetic' }})
    ];
    row(c, r3, W / 2, sy + gapY * 2.1, 20);
    slam(c, r3[0], t, {{ from: 1.15 }});
    slam(c, r3[1], t, {{ from: 1.6, glow: 'rgba(255,214,10,0.4)', glowBlur: 40 }});
  }}
}}

// Scene 1: VM Stack Diagram (4.20s - 10.70s)
let VM_CARD = null;
function getVMCard() {{
  if (VM_CARD) return VM_CARD;
  VM_CARD = CM.layer(IS_VERTICAL ? 740 : 700, IS_VERTICAL ? 540 : 420);
  const x = VM_CARD.getContext('2d');
  const w = VM_CARD.width, h = VM_CARD.height;

  // Background
  x.fillStyle = 'rgba(18, 18, 22, 0.95)';
  x.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  x.lineWidth = 2;
  rr(x, 10, 10, w - 20, h - 20, 18);
  x.fill(); x.stroke();

  // Architecture Layers Stack
  const layers = [
    {{ name: 'Application & Runtime', col: '#38bdf8', sub: 'Single Process' }},
    {{ name: 'GUEST OPERATING SYSTEM', col: '#ff3b30', sub: '4 GB RAM Bloat · Full Kernel · Daemons' }},
    {{ name: 'Hypervisor (Type-2 / VM)', col: '#8e8d94', sub: 'Virtualization Layer' }},
    {{ name: 'Host Hardware & OS', col: '#484852', sub: 'Physical Server' }}
  ];

  let curY = 32;
  const lh = (h - 64) / 4 - 8;
  layers.forEach((l, i) => {{
    x.fillStyle = (i === 1) ? 'rgba(255, 59, 48, 0.18)' : 'rgba(255, 255, 255, 0.04)';
    x.strokeStyle = l.col;
    x.lineWidth = (i === 1) ? 2.5 : 1.5;
    rr(x, 30, curY, w - 60, lh, 10);
    x.fill(); x.stroke();

    x.fillStyle = l.col;
    x.font = '800 22px "Inter", sans-serif';
    x.fillText(l.name, 50, curY + lh / 2 - 4);

    x.fillStyle = '#8e8d94';
    x.font = '600 14px "Inter", sans-serif';
    x.fillText(l.sub, 50, curY + lh / 2 + 18);

    curY += lh + 8;
  }});
  return VM_CARD;
}}

function sceneVMStack(c, t) {{
  const cy = IS_VERTICAL ? HH * 0.42 : HH * 0.48;
  const yaw = lerp(0.18, -0.05, ez.out3(span(t, 4.2, 10.7)));
  const card = getVMCard();
  drawYaw(c, card, W / 2, cy, card.width, card.height, yaw, 1.0);

  // Red Bloat Badge Warning
  if (t >= TL.stack.bloat) {{
    const u = span(t, TL.stack.bloat, TL.stack.bloat + 0.25);
    const s = ez.outBack(u);
    c.save();
    c.translate(W / 2 + (IS_VERTICAL ? 0 : 260), cy + (IS_VERTICAL ? 320 : -120));
    c.scale(s, s);
    c.fillStyle = 'rgba(255, 59, 48, 0.95)';
    rr(c, -160, -28, 320, 56, 12);
    c.fill();
    c.fillStyle = '#ffffff';
    c.font = '800 18px "Inter", sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('⚠ 4096 MB MEMORY OVERHEAD', 0, 0);
    c.restore();
  }}

  // 60-Second Cold Boot Pill
  if (t >= TL.stack.boot) {{
    const u = span(t, TL.stack.boot, TL.stack.boot + 0.25);
    const s = ez.outBack(u);
    c.save();
    c.translate(W / 2 - (IS_VERTICAL ? 0 : 260), cy + (IS_VERTICAL ? 390 : 120));
    c.scale(s, s);
    c.fillStyle = 'rgba(20, 20, 26, 0.92)';
    c.strokeStyle = '#ff3b30';
    c.lineWidth = 2;
    rr(c, -150, -26, 300, 52, 12);
    c.fill(); c.stroke();
    c.fillStyle = '#ff3b30';
    c.font = '800 18px "Inter", sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('⏱ COLD BOOT: 60 SECONDS', 0, 0);
    c.restore();
  }}
}}

// Scene 2: Docker Shared Kernel (10.70s - 15.40s)
let DOCKER_ENGINE = null;
function getDockerEngine() {{
  if (DOCKER_ENGINE) return DOCKER_ENGINE;
  DOCKER_ENGINE = CM.layer(IS_VERTICAL ? 740 : 720, IS_VERTICAL ? 540 : 420);
  const x = DOCKER_ENGINE.getContext('2d');
  const w = DOCKER_ENGINE.width, h = DOCKER_ENGINE.height;

  // Window frame
  x.fillStyle = 'rgba(18, 18, 24, 0.95)';
  x.strokeStyle = 'rgba(56, 189, 248, 0.35)';
  x.lineWidth = 2;
  rr(x, 10, 10, w - 20, h - 20, 18);
  x.fill(); x.stroke();

  // Traffic lights
  x.fillStyle = '#ff5f56'; x.beginPath(); x.arc(36, 34, 7, 0, 7); x.fill();
  x.fillStyle = '#ffbd2e'; x.beginPath(); x.arc(58, 34, 7, 0, 7); x.fill();
  x.fillStyle = '#27c93f'; x.beginPath(); x.arc(80, 34, 7, 0, 7); x.fill();

  x.fillStyle = '#8e8d94';
  x.font = '600 14px "Inter", sans-serif';
  x.fillText('docker://daemon/namespaces-control-plane', 115, 38);

  // 3 Isolated Namespace Pills
  const ns = [
    {{ title: 'PID Namespace', desc: 'Process tree isolation (PID 1)' }},
    {{ title: 'NET Namespace', desc: 'Virtual network bridge interface' }},
    {{ title: 'cgroups (Control Groups)', desc: 'Strict CPU & RAM hardware limits' }}
  ];

  let curY = 80;
  const nh = (h - 180) / 3;
  ns.forEach(item => {{
    x.fillStyle = 'rgba(56, 189, 248, 0.08)';
    x.strokeStyle = 'rgba(56, 189, 248, 0.3)';
    x.lineWidth = 1.5;
    rr(x, 30, curY, w - 60, nh, 12);
    x.fill(); x.stroke();

    x.fillStyle = '#38bdf8';
    x.font = '800 20px "Inter", sans-serif';
    x.fillText('⚡ ' + item.title, 50, curY + nh / 2 - 4);

    x.fillStyle = '#f4f1ea';
    x.font = '500 14px "Inter", sans-serif';
    x.fillText(item.desc, 50, curY + nh / 2 + 18);
    curY += nh + 10;
  }});

  // Shared Base Host Kernel
  x.fillStyle = 'rgba(48, 209, 88, 0.15)';
  x.strokeStyle = '#30d158';
  x.lineWidth = 2;
  rr(x, 30, h - 68, w - 60, 48, 10);
  x.fill(); x.stroke();
  x.fillStyle = '#30d158';
  x.font = '800 17px "Inter", sans-serif';
  x.textAlign = 'center';
  x.fillText('✓ SHARED HOST LINUX KERNEL (ZERO GUEST OS OVERHEAD)', w / 2, h - 38);

  return DOCKER_ENGINE;
}}

function sceneKernelSharing(c, t) {{
  const cy = IS_VERTICAL ? HH * 0.42 : HH * 0.48;
  const yaw = lerp(-0.15, 0.08, ez.out3(span(t, 10.7, 15.4)));
  const card = getDockerEngine();
  drawYaw(c, card, W / 2, cy, card.width, card.height, yaw, 1.0);
}}

// Scene 3: Fast Containers Sub-100ms (15.40s - 20.40s)
function sceneFastContainers(c, t) {{
  const sy = IS_VERTICAL ? 420 : 180;

  // Header Title
  const r1 = [word('LIGHTWEIGHT', 15.4, disp(IS_VERTICAL ? 96 : 84), C.cyan), word('CONTAINERS', 15.7, disp(IS_VERTICAL ? 96 : 84), C.ink)];
  row(c, r1, W / 2, sy, 20);
  r1.forEach(it => slam(c, it, t));

  // Rolling Millisecond Speedometer
  const tProg = ez.out3(span(t, 16.0, 18.2));
  const ms = Math.round(lerp(0, 85, tProg));

  const cy = sy + (IS_VERTICAL ? 220 : 150);
  c.save();
  c.translate(W / 2, cy);
  c.font = '900 ' + (IS_VERTICAL ? 120 : 100) + 'px "Anton", sans-serif';
  c.fillStyle = C.green;
  c.shadowColor = 'rgba(48, 209, 88, 0.6)';
  c.shadowBlur = 30;
  c.textAlign = 'center';
  c.fillText(ms + ' MS', 0, 0);

  c.font = 'italic 700 ' + (IS_VERTICAL ? 42 : 36) + 'px "Instrument Serif", serif';
  c.fillStyle = C.accent;
  c.fillText('Cold Spin-Up Speed', 0, IS_VERTICAL ? 65 : 55);
  c.restore();

  // 3 Popping Container Cards
  const cards = [
    {{ name: 'nginx:alpine', t: 17.0, time: '12ms' }},
    {{ name: 'node:api', t: 17.8, time: '45ms' }},
    {{ name: 'redis:cache', t: 18.6, time: '28ms' }}
  ];

  const cardW = IS_VERTICAL ? 700 : 260;
  const cardH = IS_VERTICAL ? 68 : 90;
  const startY = cy + (IS_VERTICAL ? 160 : 120);

  cards.forEach((cd, i) => {{
    if (t < cd.t) return;
    const u = span(t, cd.t, cd.t + 0.25);
    const s = ez.outBack(u);

    const cxC = IS_VERTICAL ? W / 2 : (W / 2 - 290 + i * 290);
    const cyC = IS_VERTICAL ? startY + i * 86 : startY;

    c.save();
    c.translate(cxC, cyC);
    c.scale(s, s);

    c.fillStyle = 'rgba(20, 20, 26, 0.95)';
    c.strokeStyle = 'rgba(56, 189, 248, 0.35)';
    c.lineWidth = 1.5;
    rr(c, -cardW / 2, -cardH / 2, cardW, cardH, 12);
    c.fill(); c.stroke();

    c.fillStyle = '#38bdf8';
    c.font = '800 20px "Inter", sans-serif';
    c.textAlign = 'center';
    c.fillText('📦 ' + cd.name, 0, -8);

    c.fillStyle = '#30d158';
    c.font = '700 15px "Inter", sans-serif';
    c.fillText('Active · ' + cd.time, 0, 16);
    c.restore();
  }});
}}

// Scene 4: 90% Rolling Counter & White Flash (20.40s - 27.60s)
function sceneRollingStat(c, t) {{
  const sy = IS_VERTICAL ? 460 : 200;

  const prog = ez.out3(span(t, TL.metric.roll[0], TL.metric.roll[1]));
  const count = Math.round(90 * prog);

  c.save();
  c.translate(W / 2, sy);
  c.font = '900 ' + (IS_VERTICAL ? 220 : 180) + 'px "Anton", sans-serif';
  c.fillStyle = C.green;
  c.shadowColor = 'rgba(48, 209, 88, 0.65)';
  c.shadowBlur = 45;
  c.textAlign = 'center';
  c.textBaseline = 'middle';
  c.fillText(count + '%', 0, 0);
  c.restore();

  // Accent Line
  const r1 = [word('LESS', 22.8, disp(IS_VERTICAL ? 88 : 78), C.ink), word('MEMORY', 23.1, disp(IS_VERTICAL ? 88 : 78), C.ink), word('OVERHEAD', 23.4, disp(IS_VERTICAL ? 88 : 78), C.accent)];
  row(c, r1, W / 2, sy + (IS_VERTICAL ? 160 : 130), 20);
  r1.forEach(it => slam(c, it, t));

  // Dev to Prod Parity Badge
  if (t >= 24.5) {{
    const u = span(t, 24.5, 24.8);
    const s = ez.outBack(u);
    c.save();
    c.translate(W / 2, sy + (IS_VERTICAL ? 280 : 220));
    c.scale(s, s);
    c.fillStyle = 'rgba(255, 214, 10, 0.15)';
    c.strokeStyle = '#ffd60a';
    c.lineWidth = 2;
    rr(c, -200, -30, 400, 60, 14);
    c.fill(); c.stroke();
    c.fillStyle = '#ffd60a';
    c.font = '800 22px "Inter", sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('⚡ DEV TO PROD PARITY', 0, 0);
    c.restore();
  }}
}}

// Scene 5: Monolithic Stamp Rejection (27.60s - 30.30s)
function sceneMonolithStamp(c, t) {{
  const sy = IS_VERTICAL ? 520 : 240;

  const r1 = [word('MONOLITHIC', 27.8, disp(IS_VERTICAL ? 120 : 110), C.red), word('INFRASTRUCTURE', 28.1, disp(IS_VERTICAL ? 120 : 110), C.ink)];
  const b = row(c, r1, W / 2, sy, 22);
  r1.forEach(it => slam(c, it, t));
  strike(c, b.x0 - 20, b.x0 + b.w + 20, sy, span(t, 28.4, 28.6), C.red, 18);

  // Big tactile rubber stamp slamming down
  if (t >= TL.stamp.stamp) {{
    const u = span(t, TL.stamp.stamp, TL.stamp.stamp + 0.16);
    const s = lerp(2.2, 1.0, ez.outExpo(u));
    const stamp = stampLayer('DEPRECATED', C.red);
    c.save();
    c.translate(W / 2, sy + 30);
    c.rotate(-0.16);
    c.scale(s, s);
    c.globalAlpha = Math.min(1, u * 4);
    c.drawImage(stamp, -stamp.width / 2, -stamp.height / 2);
    c.restore();
  }}
}}

// Scene 6: Creator Takeaway (30.30s - 32.65s)
function sceneTakeaway(c, t) {{
  const sy = IS_VERTICAL ? 420 : 180;

  const r1 = [word('CONTAINERIZE', 30.3, disp(IS_VERTICAL ? 104 : 96), C.cyan), word('YOUR STACK', 30.7, disp(IS_VERTICAL ? 104 : 96), C.ink)];
  row(c, r1, W / 2, sy, 24);
  r1.forEach(it => slam(c, it, t));

  const items = [
    {{ text: 'Instant Sub-100ms Spin-Up', t: TL.take.check1 }},
    {{ text: '90% Memory Overhead Reduction', t: TL.take.check2 }},
    {{ text: 'Identical Dev & Production Parity', t: TL.take.check3 }}
  ];

  let curY = sy + (IS_VERTICAL ? 140 : 110);
  items.forEach(it => {{
    if (t < it.t) return;
    const u = span(t, it.t, it.t + 0.22);
    const s = ez.outBack(u);
    c.save();
    c.translate(W / 2, curY);
    c.scale(s, s);
    c.fillStyle = 'rgba(255, 255, 255, 0.05)';
    c.strokeStyle = '#30d158';
    c.lineWidth = 1.5;
    rr(c, -260, -26, 520, 52, 12);
    c.fill(); c.stroke();

    c.fillStyle = '#30d158';
    c.font = '800 20px "Inter", sans-serif';
    c.textAlign = 'left';
    c.textBaseline = 'middle';
    c.fillText('✓  ' + it.text, -230, 0);
    c.restore();
    curY += IS_VERTICAL ? 80 : 66;
  }});
}}

// =================================== CAMERA & COMPOSITOR ===================================
function getCamera(t) {{
  let z = 1.0, dx = 0, dy = 0;
  for (const p of PUNCH) {{
    const d = t - p.t;
    if (d >= 0 && d < 0.4) {{
      const e = d < 0.06 ? ez.out3(d / 0.06) : Math.exp(-(d - 0.06) * (p.k || 3.0));
      z += p.a * e;
    }}
  }}
  for (const s of SHAKE) {{
    const d = t - s.t;
    if (d >= 0 && d < 0.8) {{
      const e = s.a * Math.exp(-d * (s.k || 7.0));
      dx += (rng('sx' + Math.floor(t * 30))() * 2 - 1) * e;
      dy += (rng('sy' + Math.floor(t * 30))() * 2 - 1) * e;
    }}
  }}
  return {{ z, dx, dy }};
}}

const SCENES = [
  sceneHook, sceneVMStack, sceneKernelSharing,
  sceneFastContainers, sceneRollingStat, sceneMonolithStamp, sceneTakeaway
];

function getSceneIndex(t) {{
  let idx = 0;
  for (const cut of CUTS) {{
    if (t >= cut.t) idx++;
  }}
  return Math.min(idx, SCENES.length - 1);
}}

function renderScene(t) {{
  background(cx, t);

  const cam = getCamera(t);
  cx.save();
  cx.translate(W / 2 + cam.dx, HH / 2 + cam.dy);
  cx.scale(cam.z, cam.z);
  cx.translate(-W / 2, -HH / 2);

  // Check scene cut transition
  let inCut = false;
  for (const cut of CUTS) {{
    if (t >= cut.t - cut.d / 2 && t <= cut.t + cut.d / 2) {{
      inCut = true;
      const u = (t - (cut.t - cut.d / 2)) / cut.d;
      if (cut.type === 'whip') {{
        const offX = lerp(0, -W * cut.dir, ez.inout3(u));
        cx.save();
        cx.translate(offX, 0);
        SCENES[getSceneIndex(cut.t - 0.1)](cx, t);
        cx.restore();

        cx.save();
        cx.translate(offX + W * cut.dir, 0);
        SCENES[getSceneIndex(cut.t + 0.1)](cx, t);
        cx.restore();
      }} else if (cut.type === 'flash') {{
        SCENES[getSceneIndex(t)](cx, t);
        const flashA = 1 - Math.abs(u - 0.5) * 2;
        cx.fillStyle = `rgba(255, 255, 255, ${{flashA * 0.9}})`;
        cx.fillRect(0, 0, W, HH);
      }} else {{ // glitch
        SCENES[getSceneIndex(t)](cx, t);
        cx.fillStyle = `rgba(56, 189, 248, 0.25)`;
        cx.fillRect(0, (rng(t)() * HH), W, 20);
      }}
      break;
    }}
  }}

  if (!inCut) {{
    const sIdx = getSceneIndex(t);
    SCENES[sIdx](cx, t);
  }}

  cx.restore();

  // White flash on 90% lock
  if (t >= 22.8 && t <= 23.4) {{
    const fa = (1 - (t - 22.8) / 0.6) * 0.7;
    cx.fillStyle = `rgba(255, 255, 255, ${{fa}})`;
    cx.fillRect(0, 0, W, HH);
  }}

  // Chrome & Captions
  chrome(cx, t);
  drawCaptions(cx, t);
  finishing(cx, t);
}}

// =================================== PLAYBACK TRANSPORT ===================================
let isPlaying = false;
let animReq = null;

function updateUI(t) {{
  scrubber.value = t;
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  timeDisp.textContent = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}} / 00:32`;
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
  audio.play().catch(e => console.warn(e));
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

seek(0);
</script>
</body>
</html>"""


# Generate HTML files
html_16x9 = generate_player(is_vertical=False)
html_9x16 = generate_player(is_vertical=True)

(OUT_DIR / "docker_containers_16x9_social.html").write_text(html_16x9, encoding="utf-8")
(OUT_DIR / "docker_containers_9x16_shorts.html").write_text(html_9x16, encoding="utf-8")
(ART_DIR / "docker_containers_16x9_social.html").write_text(html_16x9, encoding="utf-8")
(ART_DIR / "docker_containers_9x16_shorts.html").write_text(html_9x16, encoding="utf-8")

print("Generated full multi-scene 16:9 & 9:16 HTML players for Docker Containers!")
