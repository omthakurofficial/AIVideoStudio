#!/usr/bin/env python3
"""
Generator and Headless Batch Renderer for AWS Cloud IAM in Creator Motion Graphics Style.
Produces both 16:9 Landscape and 9:16 Mobile Vertical Social Media Edits:
- Synchronized Neural Voiceover Narration
- Millisecond Pop-In Karaoke Captions (Inter 800 with active glow)
- Fixed text overrides, non-colliding layout, safe-zone bounding
- High-bitrate H.264 MP4 with mixed stereo sound effects & voiceover
"""
import os
import sys
import json
import base64
import time
import subprocess
import numpy as np
import wave
from playwright.sync_api import sync_playwright

OUT_DIR = "/home/omthakur/Downloads/AIVideoStudio/exports/creator_motion_aws_iam"
VOICEOVER_JSON = os.path.join(OUT_DIR, "voiceover_words.json")
VOICEOVER_WAV = os.path.join(OUT_DIR, "voiceover_narration.wav")
VOICEOVER_MP3 = os.path.join(OUT_DIR, "voiceover_narration.mp3")

with open(VOICEOVER_JSON) as f:
    raw_words = json.load(f)["words"]

with open(VOICEOVER_MP3, "rb") as f:
    vo_b64 = base64.b64encode(f.read()).decode("ascii")

# Group words into natural caption chunks (2 to 4 words per group)
caption_groups = []
current_chunk = []
for i, w in enumerate(raw_words):
    current_chunk.append(w)
    # Natural break points
    is_punct = w["word"].endswith((".", "?", "!", ":"))
    is_chunk_full = len(current_chunk) >= 4
    is_next_pause = False
    if i < len(raw_words) - 1:
        if raw_words[i+1]["start"] - w["end"] > 0.35:
            is_next_pause = True

    if is_punct or is_chunk_full or is_next_pause or i == len(raw_words) - 1:
        caption_groups.append({
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"],
            "words": current_chunk
        })
        current_chunk = []

print(f"Generated {len(caption_groups)} natural caption groups.")

# Generate HTML players for 16:9 and 9:16
def generate_html(is_vertical=False):
    width = 1080 if is_vertical else 1280
    height = 1920 if is_vertical else 720
    aspect = "9 / 16" if is_vertical else "16 / 9"
    max_w = "540px" if is_vertical else "1180px"
    mode_name = "9:16 Vertical (Reels / TikTok / Shorts)" if is_vertical else "16:9 Landscape (YouTube / LinkedIn / X)"
    captions_json_str = json.dumps(caption_groups)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AWS Cloud IAM — {mode_name}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600;700;800&display=block">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0b0b0d;
      --panel: #141417;
      --ink: #f2f0ea;
      --dim: #8d8c93;
      --line: #26262c;
      --accent: #ffd60a;
      --display: "Anton", "Bebas Neue", Impact, sans-serif;
      --body: "Inter", system-ui, sans-serif;
      --serif: "Instrument Serif", Georgia, serif;
    }}
    html, body {{ height: 100%; margin: 0; }}
    body {{
      background: var(--bg); color: var(--ink); font-family: var(--body);
      padding: 16px; box-sizing: border-box;
    }}
    .wrap {{ max-width: {max_w}; margin: 0 auto; display: grid; gap: 12px; }}
    .top {{ display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 14px; }}
    .name {{ font-family: var(--display); font-weight: 400; font-size: clamp(22px, 3.5vw, 32px); letter-spacing: 0.02em; text-transform: uppercase; margin: 0; line-height: 1; }}
    .name em {{ font-family: var(--serif); font-style: italic; text-transform: none; color: var(--accent); font-size: 1.15em; }}
    .meta {{ color: var(--dim); font-size: 13px; margin: 0; }}
    .stage {{
      position: relative; width: 100%; aspect-ratio: {aspect}; background: #000;
      border-radius: 12px; overflow: hidden; border: 1px solid var(--line);
      box-shadow: 0 20px 45px -10px rgba(0,0,0,0.85);
    }}
    .stage canvas {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
    .bar {{
      display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px;
      background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 10px;
    }}
    .bar button {{
      font: 600 13px var(--body); color: var(--ink); background: transparent; border: 1px solid var(--line);
      border-radius: 6px; padding: 7px 12px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
    }}
    .bar button:hover {{ border-color: var(--dim); }}
    .bar button[aria-pressed="true"] {{ background: var(--accent); color: #0b0b0d; border-color: var(--accent); }}
    #play {{ min-width: 76px; justify-content: center; background: var(--ink); color: #0b0b0d; }}
    #scrub {{ flex: 1 1 180px; min-width: 0; accent-color: var(--accent); }}
    #time {{ font: 600 13px var(--body); font-variant-numeric: tabular-nums; color: var(--dim); min-width: 90px; text-align: right; }}
    .badge {{
      display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase;
      padding: 3px 8px; border-radius: 4px; background: rgba(255,214,10,0.15); color: var(--accent);
      border: 1px solid rgba(255,214,10,0.3); margin-bottom: 4px;
    }}
  </style>
</head>
<body>

<div class="wrap">
  <div class="top">
    <div>
      <span class="badge">{mode_name}</span>
      <h1 class="name">AWS Cloud <em>IAM</em> Masterclass</h1>
    </div>
    <p class="meta">38.5 s · Word-Synched Voiceover & Kinetic Captions</p>
  </div>
  <div class="stage">
    <canvas id="stage" width="{width}" height="{height}" aria-label="AWS Cloud IAM video"></canvas>
  </div>
  <div class="bar">
    <button id="play" type="button">Play</button>
    <input id="scrub" type="range" min="0" max="38.5" step="0.01" value="0" aria-label="Scrub timeline">
    <span id="time">0.00 / 38.50</span>
    <button id="sound" type="button" aria-pressed="true">Sound on</button>
    <button id="loop" type="button" aria-pressed="true">Loop</button>
  </div>
</div>

<script>
const IS_VERTICAL = {str(is_vertical).lower()};
const W = {width}, HH = {height};
const DURATION = 38.5;

// Embedded Captions Data
const CAPTIONS = {captions_json_str};

// CM Core Math Helpers
const CM = (() => {{
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, u) => a + (b - a) * u;
  const span = (t, a, b) => clamp((t - a) / (b - a));
  const rotl = (x, k) => (x << k) | (x >>> (32 - k));
  const hash = (s) => {{ s = String(s); let h = 0x9e3779b1; for (let i = 0; i < s.length; i++) {{ h = Math.imul(h ^ s.charCodeAt(i), 0x85ebca6b); h ^= h >>> 13; }} return h >>> 0; }};
  const rng = (seed) => {{
    const s = typeof seed === 'number' ? seed >>> 0 : hash(seed);
    let a = (s ^ 0xa5a5a5a5) >>> 0, b = (Math.imul(s, 0x27d4eb2d) >>> 0) || 1, c = (0x165667b1 ^ s) >>> 0, d = (rotl(s, 7) >>> 0) || 7;
    const r = () => {{ const res = Math.imul(rotl(Math.imul(b, 5), 7), 9) >>> 0; const t = b << 9; c ^= a; d ^= b; b ^= c; a ^= d; c ^= t; d = rotl(d, 11); return res / 4294967296; }};
    for (let i = 0; i < 8; i++) r();
    r.in = (lo, hi) => lo + r() * (hi - lo);
    r.pick = (arr) => arr[(r() * arr.length) | 0];
    return r;
  }};
  const noise1 = (seed) => {{ const r = rng(seed), v = Float32Array.from({{ length: 256 }}, () => r() * 2 - 1); return (x) => {{ const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(v[i & 255], v[(i + 1) & 255], u); }}; }};
  const ez = {{
    out3: (u) => 1 - Math.pow(1 - u, 3),
    in3: (u) => u * u * u,
    inout3: (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2),
    outExpo: (u) => (u >= 1 ? 1 : 1 - Math.pow(2, -10 * u)),
    back: (u, s = 1.7) => (u <= 0 ? 0 : u >= 1 ? 1 : 1 + (s + 1) * Math.pow(u - 1, 3) + s * Math.pow(u - 1, 2)),
    spring: (u) => (u <= 0 ? 0 : u >= 1 ? 1 : 1 - Math.exp(-6 * u) * Math.cos(13 * u)),
  }};
  const layer = (w, h) => {{ const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }};
  return {{ clamp, lerp, span, rng, noise1, ez, layer }};
}})();

// SFX Synthesizer
const SFX = (() => {{
  const SEMI = {{ C: -9, D: -7, E: -5, F: -4, G: -2, A: 0, B: 2 }};
  const hz = (n) => {{ if (typeof n === 'number') return n; const m = /^([A-G])(#|b)?(-?\\d)$/.exec(n); return 440 * Math.pow(2, (SEMI[m[1]] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0) + (+m[3] - 4) * 12) / 12); }};

  function kit(ac, o = {{}}) {{
    const VO = !!o.voiceover, SR = ac.sampleRate, T0 = o.from || 0, base = ac.currentTime + (o.lead || 0);
    const at = (t) => Math.max(ac.currentTime + 0.002, (Math.round((base + (t - T0)) * SR) + 0.3) / SR);
    const skip = (t, dur) => (t + dur <= T0 + 0.005) || (at(t) + dur < ac.currentTime);

    const comp = ac.createDynamicsCompressor();
    comp.threshold.value = -14; comp.knee.value = 6; comp.ratio.value = 4; comp.attack.value = 0.003; comp.release.value = 0.15;
    const master = ac.createGain(); master.gain.value = o.master == null ? (VO ? 0.65 : 0.85) : o.master;
    comp.connect(master); master.connect(o.dest || ac.destination);
    const mk = (g) => {{ const n = ac.createGain(); n.gain.value = g; n.connect(comp); return n; }};
    const bus = {{ fx: mk(VO ? 0.35 : 0.95), music: mk(VO ? 0.18 : 0.62), amb: mk(VO ? 0.20 : 0.4) }};
    const duckIn = ac.createGain(); duckIn.connect(bus.music);
    const DUCKS = [];

    const verb = ac.createConvolver();
    {{ const n = Math.floor(1.5 * SR), ir = ac.createBuffer(2, n, SR);
      for (let ch = 0; ch < 2; ch++) {{ const r = CM.rng('plate' + ch), d = ir.getChannelData(ch); let lp = 0; for (let i = 0; i < n; i++) {{ const u = i / n; lp += (0.7 - 0.5 * u) * ((r() * 2 - 1) - lp); d[i] = lp * Math.pow(1 - u, 2.6) * 0.9; }} }}
      verb.buffer = ir; }}
    const verbIn = ac.createGain(); verbIn.gain.value = 0.8; verbIn.connect(verb); verb.connect(comp);

    const NB = {{}};
    {{ const n = Math.floor(2 * SR);
      for (const kind of ['white', 'pink', 'brown']) {{
        const b = ac.createBuffer(1, n, SR), d = b.getChannelData(0), r = CM.rng('nz' + kind); let b0 = 0, b1 = 0, b2 = 0, br = 0;
        for (let i = 0; i < n; i++) {{ const w = r() * 2 - 1;
          if (kind === 'white') d[i] = w;
          else if (kind === 'pink') {{ b0 = 0.99765 * b0 + w * 0.099; b1 = 0.963 * b1 + w * 0.2965; b2 = 0.57 * b2 + w * 1.0527; d[i] = (b0 + b1 + b2 + w * 0.1848) * 0.18; }}
          else {{ br = (br + 0.02 * w) / 1.02; d[i] = br * 3.4; }} }}
        NB[kind] = b; }} }}

    const ramp = (param, v, t) => {{
      const st = Math.max(ac.currentTime + 0.002, t);
      if (!Array.isArray(v)) {{ param.setValueAtTime(v, st); return; }}
      param.setValueAtTime(v[0][1], st + Math.max(0, v[0][0]));
      for (let i = 1; i < v.length; i++) param.exponentialRampToValueAtTime(Math.max(1e-3, v[i][1]), st + Math.max(0.001, v[i][0]));
    }};
    const env = (g, t, peak, dur, a = 0.004, hold = 0) => {{
      const st = Math.max(ac.currentTime + 0.002, t);
      a = Math.min(a, dur * 0.9); hold = Math.min(hold, dur - a);
      g.gain.setValueAtTime(0, st); g.gain.linearRampToValueAtTime(peak, st + a);
      if (hold > 0) g.gain.setValueAtTime(peak, st + a + hold);
      g.gain.exponentialRampToValueAtTime(1e-4, st + dur); g.gain.setValueAtTime(0, st + dur + 0.002);
    }};
    const level = (p, d) => (p.gain == null ? d : p.gain) * (VO && p.soft ? 0.55 : 1);
    const route = (node, p, t) => {{
      const st = Math.max(ac.currentTime + 0.002, t);
      const pan = ac.createStereoPanner();
      if (Array.isArray(p.pan)) {{ pan.pan.setValueAtTime(p.pan[0], st); pan.pan.linearRampToValueAtTime(p.pan[1], st + (p.dur || 0.2)); }} else pan.pan.value = CM.clamp(p.pan || 0, -1, 1);
      node.connect(pan); pan.connect(p.bus === 'music' ? duckIn : bus[p.bus || 'fx']);
      if (p.verb) {{ const s = ac.createGain(); s.gain.value = p.verb; pan.connect(s); s.connect(verbIn); }}
    }};
    const filt = (p, t) => {{ if (!p.filter) return null; const f = ac.createBiquadFilter(); f.type = p.filter; f.Q.value = p.q == null ? 0.9 : p.q; ramp(f.frequency, p.ff == null ? 1200 : p.ff, t); return f; }};

    function voice(time, p) {{
      const dur = p.dur || 0.2; if (skip(time, dur)) return; const t = at(time);
      const osc = ac.createOscillator(); osc.type = p.type || 'sine';
      ramp(osc.frequency, Array.isArray(p.f) ? p.f.map(([d, v]) => [d, hz(v)]) : hz(p.f || 440), t);
      const g = ac.createGain(); env(g, t, level(p, 0.3), dur, p.a, p.hold);
      const f = filt(p, t); if (f) {{ osc.connect(f); f.connect(g); }} else osc.connect(g);
      route(g, p, t); osc.start(t); osc.stop(t + dur + 0.03);
    }}
    function hiss(time, p) {{
      const dur = p.dur || 0.2; if (skip(time, dur)) return; const t = at(time);
      const src = ac.createBufferSource(); src.buffer = NB[p.color || 'white']; src.loop = true; if (p.rate) src.playbackRate.value = p.rate;
      const g = ac.createGain(); env(g, t, level(p, 0.3), dur, p.a, p.hold);
      const f = filt(p, t); if (f) {{ src.connect(f); f.connect(g); }} else src.connect(g);
      route(g, p, t); src.start(t, CM.rng('off' + time)() * 1.5); src.stop(t + dur + 0.03);
    }}
    function duck(t, depth = 0.5, hold = 0.25) {{ DUCKS.push({{ t, depth, hold }}); }}

    const S = {{
      slam: (t, o) => {{ voice(t, {{ f: [[0, 150], [0.12, 52]], dur: 0.2, gain: 0.42 * o.g, pan: o.pan, soft: o.soft }}); hiss(t, {{ dur: 0.07, filter: 'lowpass', ff: 2600, gain: 0.22 * o.g, pan: o.pan, soft: o.soft }}); hiss(t, {{ dur: 0.012, filter: 'highpass', ff: 5000, gain: 0.12 * o.g, pan: o.pan, soft: o.soft }}); }},
      boom: (t, o) => {{ voice(t, {{ f: [[0, 90], [0.08, 52], [1.6, 34]], dur: 1.7, gain: 0.7 * o.g, a: 0.006, hold: 0.12 }}); hiss(t, {{ color: 'brown', dur: 0.6, filter: 'lowpass', ff: [[0, 600], [0.5, 90]], gain: 0.35 * o.g, verb: 0.3 }}); duck(t, 0.7, 0.35); }},
      pop: (t, o) => {{ const f = o.f || 760; voice(t, {{ f: [[0, f * 1.7], [0.05, f]], dur: 0.08, gain: 0.22 * o.g, pan: o.pan, soft: o.soft }}); hiss(t, {{ dur: 0.01, filter: 'highpass', ff: 4500, gain: 0.08 * o.g, pan: o.pan, soft: o.soft }}); }},
      tick: (t, o) => hiss(t, {{ dur: 0.016, filter: 'bandpass', ff: o.f || 3800, q: 3, gain: 0.32 * o.g, pan: o.pan, soft: o.soft }}),
      click: (t, o) => {{ hiss(t, {{ dur: 0.012, filter: 'bandpass', ff: 3200, q: 2, gain: 0.35 * o.g, pan: o.pan }}); hiss(t + 0.045, {{ dur: 0.01, filter: 'bandpass', ff: 2400, q: 2, gain: 0.22 * o.g, pan: o.pan }}); }},
      whoosh: (t, o) => {{ const d = o.dur || 0.35, dir = o.dir || 1; hiss(t, {{ color: 'pink', dur: d, filter: 'bandpass', ff: [[0, 260], [d * 0.55, o.top || 3200], [d, 520]], q: 0.75, gain: 0.5 * o.g, a: d * 0.55, pan: [-0.7 * dir, 0.7 * dir], verb: 0.12, soft: o.soft }}); hiss(t + d * 0.2, {{ dur: d * 0.6, filter: 'highpass', ff: [[0, 3000], [d * 0.6, 7000]], gain: 0.08 * o.g, a: d * 0.3, pan: [-0.4 * dir, 0.5 * dir], soft: o.soft }}); }},
      riser: (t, o) => {{ const d = o.dur || 0.8; hiss(t, {{ color: 'pink', dur: d, filter: 'bandpass', ff: [[0, 300], [d, 5200]], q: 1.1, gain: 0.32 * o.g, a: d * 0.96, verb: 0.2, soft: o.soft }}); voice(t, {{ type: 'sawtooth', f: [[0, 110], [d, 440]], dur: d, gain: 0.06 * o.g, a: d * 0.95, filter: 'lowpass', ff: [[0, 400], [d, 2400]], soft: o.soft }}); }},
      glitch: (t, o) => {{ const r = CM.rng('gl' + t); for (let i = 0; i < 9; i++) voice(t + i * 0.021, {{ type: 'square', f: 180 + r() * 2200, dur: 0.018, gain: 0.07 * o.g, a: 0.001, hold: 0.012, pan: r() * 1.4 - 0.7 }}); hiss(t, {{ dur: 0.2, filter: 'bandpass', ff: [[0, 4000], [0.2, 900]], q: 0.7, gain: 0.18 * o.g }}); hiss(t + 0.1, {{ dur: 0.05, color: 'brown', gain: 0.25 * o.g }}); }},
      keys: (t, o) => {{ const r = CM.rng('k' + t), end = t + (o.dur || 0.4); for (let x = t; x < end; x += 0.055 + r() * 0.035) {{ hiss(x, {{ dur: 0.014, filter: 'bandpass', ff: 3200 + r() * 900, q: 3, gain: 0.2 * o.g, pan: o.pan, soft: true }}); voice(x, {{ f: 1900 + r() * 300, dur: 0.012, gain: 0.025 * o.g, pan: o.pan, soft: true }}); }} }},
      marker: (t, o) => {{ const d = o.dur || 0.25, r = CM.rng('m' + t); for (let x = 0; x < d; x += 0.022 + r() * 0.012) hiss(t + x, {{ dur: 0.03, filter: 'bandpass', ff: 1700 + r() * 900, q: 1.4, gain: 0.16 * o.g * (0.6 + r() * 0.5), pan: o.pan, soft: o.soft }}); }},
      strike: (t, o) => {{ hiss(t, {{ dur: 0.15, filter: 'bandpass', ff: [[0, 1200], [0.15, 3200]], q: 1.2, gain: 0.3 * o.g, a: 0.02, pan: o.pan }}); }},
      tapeStop: (t, o) => {{ voice(t, {{ type: 'sawtooth', f: [[0, 196], [0.62, 18]], dur: 0.66, gain: 0.22 * o.g, a: 0.004, hold: 0.3, filter: 'lowpass', ff: [[0, 1800], [0.6, 160]] }}); voice(t, {{ f: [[0, 98], [0.62, 12]], dur: 0.66, gain: 0.3 * o.g, a: 0.004, hold: 0.3 }}); hiss(t, {{ color: 'brown', dur: 0.5, filter: 'lowpass', ff: [[0, 900], [0.5, 120]], gain: 0.18 * o.g }}); }},
      stamp: (t, o) => {{ voice(t, {{ f: [[0, 160], [0.18, 48]], dur: 0.28, gain: 0.6 * o.g }}); hiss(t, {{ dur: 0.06, filter: 'bandpass', ff: 1300, q: 1.1, gain: 0.4 * o.g }}); hiss(t + 0.004, {{ dur: 0.014, filter: 'highpass', ff: 4200, gain: 0.25 * o.g }}); }},
      shimmer: (t, o) => {{ ['C6', 'E6', 'G6', 'B6', 'D7', 'E7'].forEach((n, i) => voice(t + i * 0.035, {{ f: n, dur: 0.75, gain: 0.045 * o.g, a: 0.003, verb: 0.45, pan: (i % 2 ? 0.35 : -0.35) }})); }},
      sparkle: (t, o) => {{ const r = CM.rng('sp' + t); for (let i = 0; i < 5; i++) voice(t + i * 0.05, {{ f: 2400 + r() * 2400, dur: 0.25, gain: 0.03 * o.g, a: 0.002, verb: 0.4, pan: r() * 1.2 - 0.6 }}); }},
    }};
    function play(name, t, opts = {{}}) {{ const fn = S[name]; if (!fn) throw new Error('unknown sound ' + name); fn(t, Object.assign({{}}, opts, {{ g: opts.gain == null ? 1 : opts.gain }})); }}

    function music(t0, t1, p = {{}}) {{
      const bpm = p.bpm || 98, step = 60 / bpm / 4, bar = step * 16, g = p.gain == null ? 1 : p.gain;
      const roots = p.roots || ['A1', 'F1', 'C2', 'G1'];
      const pads = p.pads || [['A3', 'C4', 'E4'], ['F3', 'A3', 'C4'], ['C4', 'E4', 'G4'], ['G3', 'B3', 'D4']];
      let bi = 0;
      for (let tb = t0; tb < t1 - 0.05; tb += bar, bi++) {{
        const root = roots[bi % roots.length], pad = pads[bi % pads.length], blen = Math.min(bar, t1 - tb);
        pad.forEach((n, k) => voice(tb, {{ type: 'triangle', f: n, dur: blen + 0.2, gain: 0.03 * g, a: 0.3, hold: blen - 0.5, filter: 'lowpass', ff: 1100, pan: (k - 1) * 0.35, verb: 0.3, bus: 'music' }}));
        for (let s = 0; s < 16; s++) {{
          const ts = tb + s * step; if (ts >= t1 - 0.02) break;
          if (s === 0 || s === 10) {{ voice(ts, {{ f: [[0, 150], [0.09, 46]], dur: 0.32, gain: 0.5 * g, bus: 'music' }}); hiss(ts, {{ dur: 0.012, filter: 'highpass', ff: 3000, gain: 0.05 * g, bus: 'music' }}); }}
          if (s === 4 || s === 12) {{ hiss(ts, {{ dur: 0.16, filter: 'bandpass', ff: 1700, q: 0.8, gain: 0.26 * g, verb: 0.25, bus: 'music' }}); hiss(ts + 0.008, {{ dur: 0.05, filter: 'highpass', ff: 4500, gain: 0.1 * g, bus: 'music' }}); }}
          if (s % 2 === 0) hiss(ts, {{ dur: s % 4 === 2 ? 0.05 : 0.028, filter: 'highpass', ff: 7500, gain: (s % 4 === 2 ? 0.06 : 0.035) * g, bus: 'music' }});
          if ([0, 3, 6, 10, 14].includes(s)) voice(ts, {{ type: 'triangle', f: root, dur: step * 2.6, gain: 0.2 * g, a: 0.006, hold: step, filter: 'lowpass', ff: 380, bus: 'music' }});
        }}
      }}
    }}
    function drone(t0, t1, p = {{}}) {{ const d = t1 - t0, g = p.gain == null ? 1 : p.gain; voice(t0, {{ f: p.note || 'A1', dur: d, gain: 0.12 * g, a: d * 0.4, hold: d * 0.4, bus: 'music' }}); hiss(t0, {{ color: 'pink', dur: d, filter: 'bandpass', ff: 900, q: 0.5, gain: 0.03 * g, a: d * 0.5, hold: d * 0.3, bus: 'amb' }}); }}
    function finish() {{
      DUCKS.sort((a, b) => a.t - b.t);
      for (const e of DUCKS) {{ const s = at(e.t); if (s + e.hold < ac.currentTime) continue; duckIn.gain.setTargetAtTime(1 - e.depth, Math.max(s, ac.currentTime), 0.008); duckIn.gain.setTargetAtTime(1, s + e.hold, 0.14); }}
    }}
    return {{ play, voice, hiss, music, drone, duck, finish, hz, vo: VO }};
  }}
  function live(score, from, opts = {{}}) {{
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    const k = kit(ac, Object.assign({{}}, opts, {{ from: from || 0, lead: 0.04 }})); score(k); k.finish();
    return () => {{ try {{ ac.close(); }} catch (e) {{}} }};
  }}
  async function render(score, dur, sr = 48000, opts = {{}}) {{
    const len = Math.ceil(dur * sr), ac = new OfflineAudioContext(2, len, sr);
    const k = kit(ac, Object.assign({{}}, opts, {{ from: 0 }})); score(k); k.finish();
    const buf = await ac.startRendering(), L = buf.getChannelData(0), R = buf.getChannelData(1), inter = new Float32Array(len * 2);
    let peak = 0; for (let i = 0; i < len; i++) {{ inter[2 * i] = L[i]; inter[2 * i + 1] = R[i]; peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i])); }}
    return {{ inter, peak, sr, frames: len }};
  }}
  return {{ kit, live, render, hz }};
}})();

const {{ clamp, lerp, span, rng, noise1, ez }} = CM;
const C = {{ bg: '#09090a', ink: '#f4f1ea', dim: '#8e8d94', mute: '#3b3b41', panel: '#151518', panel2: '#1d1d21', line: '#2b2b31', hi: '#ffd60a', money: '#3dff8f', red: '#ff3b30', black: '#0b0b0c', cyan: '#38bdf8' }};
const F = {{ disp: '"Anton", "Bebas Neue", Impact, sans-serif', body: '"Inter", system-ui, sans-serif', serif: '"Instrument Serif", Georgia, serif' }};
const disp = (px) => `${{px}}px ${{F.disp}}`, inter = (px, w = 600) => `${{w}} ${{px}}px ${{F.body}}`, serif = (px) => `italic ${{px}}px ${{F.serif}}`;

// Timeline Synchronized with Voiceover Audio Timings
const TL = {{
  D: 38.5,
  hook: {{ w1: [0.09, 0.51], w2: [0.81, 1.00], strike: 1.70, shift: 2.10, use: 2.40, temp: 2.74, cred: 3.28, under: 3.45 }},
  least: {{ pill: 4.55, w: [4.72, 5.01, 5.25], rule: [5.47, 5.72], chips: [6.10, 6.35, 6.60], drop: 7.10, pick: 7.30, ring: 7.60, only: 6.95, arrow: 8.00 }},
  roles: {{ pill: 9.15, w1: [9.35, 9.72, 10.05, 10.38], strike1: 10.90, w2: [11.59, 12.19], br: 10.50, hl: 12.19, sub: 12.58, click: 13.08 }},
  decide: {{ pill: 14.50, w: [14.72, 15.27, 15.95], stack: [15.20, 15.70, 16.20], ring: 16.62, note: 16.62 }},
  wild: {{ w: [19.08, 19.48, 20.00, 20.48], ed: 19.10, type: [19.45, 19.85], strike: [19.85, 20.15], scoped: 21.78, warn: 21.78 }},
  metric: {{ w: [23.82, 24.35, 24.78, 25.37], cnt: [24.10, 25.00], lock: 25.00, sub1: 25.85, sub2: 26.48 }},
  wrong: {{ w1: [27.66, 28.08], w2: [28.59, 28.88], strike: [29.35, 29.50], stamp: 30.48 }},
  take: {{ zero: 32.06, hl: 32.30, w2: [33.69, 33.98, 34.51, 34.74], sub: 35.86, gold: 36.66 }},
}};

const CUTS = [
  {{ t: 4.40, d: 0.28, type: 'whip', dir: 1 }},
  {{ t: 8.95, d: 0.24, type: 'glitch' }},
  {{ t: 14.30, d: 0.26, type: 'whipV', dir: 1 }},
  {{ t: 18.65, d: 0.16, type: 'flash' }},
  {{ t: 23.40, d: 0.22, type: 'whip', dir: 1 }},
  {{ t: 27.25, d: 0.22, type: 'glitch' }},
  {{ t: 31.65, d: 0.26, type: 'whip', dir: -1 }},
];

const PUNCH = [
  {{ t: 0.09, a: 0.03 }}, {{ t: 0.81, a: 0.08 }}, {{ t: 2.74, a: 0.08 }},
  {{ t: 5.47, a: 0.05 }}, {{ t: 7.30, a: 0.06 }},
  {{ t: 11.59, a: 0.04 }}, {{ t: 12.19, a: 0.06 }}, {{ t: 13.08, a: 0.05 }},
  {{ t: 15.95, a: 0.04 }}, {{ t: 16.62, a: 0.08 }},
  {{ t: 19.48, a: 0.05 }}, {{ t: 21.78, a: 0.06 }},
  {{ t: 25.00, a: 0.15, k: 1.6 }},
  {{ t: 30.48, a: 0.10 }}, {{ t: 32.06, a: 0.11 }}, {{ t: 34.74, a: 0.05 }}
];
const SHAKE = [
  {{ t: 0.81, a: 9 }}, {{ t: 2.74, a: 8 }}, {{ t: 7.30, a: 6 }}, {{ t: 13.08, a: 5 }},
  {{ t: 16.62, a: 7 }}, {{ t: 21.78, a: 7 }}, {{ t: 25.00, a: 20, k: 6 }},
  {{ t: 30.48, a: 17 }}, {{ t: 32.06, a: 13 }}
];
const FLASH = [
  {{ t: 0.81, a: 0.18 }}, {{ t: 18.65, a: 0.85 }}, {{ t: 25.00, a: 0.60, col: '61,255,143' }},
  {{ t: 30.48, a: 0.35, col: '255,59,48' }}, {{ t: 32.06, a: 0.25 }}
];
const LEAK = [0.81, 25.00, 32.06];

const percentCount = (t) => Math.round(99 * ez.out3(span(t, TL.metric.cnt[0], TL.metric.cnt[1])));

// Text & Visual Primitives
const word = (s, t, font, color, extra) => Object.assign({{ s, t, font, color: color || C.ink }}, extra || {{}});
function measure(c, it) {{ c.font = it.font; c.letterSpacing = it.track || '0px'; const w = c.measureText(it.s).width; c.letterSpacing = '0px'; return w; }}
function row(c, items, x, y, gap, align = 'center') {{
  let tot = 0; items.forEach((it) => {{ it.w = measure(c, it); tot += it.w; }}); tot += gap * (items.length - 1);
  let cx = align === 'center' ? x - tot / 2 : x;
  items.forEach((it) => {{ it.x = cx; it.cx = cx + it.w / 2; it.y = y; cx += it.w + gap; }});
  return {{ x0: align === 'center' ? x - tot / 2 : x, w: tot }};
}}
function slam(c, it, t, o = {{}}) {{
  if (t < it.t) return;
  const u = span(t, it.t, it.t + (o.dur || 0.2)), e = ez.outExpo(u), s = lerp(o.from || 1.42, 1, e);
  c.save(); c.translate(it.cx, it.y); c.scale(s, s);
  c.globalAlpha = (o.alpha == null ? 1 : o.alpha) * Math.min(1, u * 3.5);
  if (u < 1 && !o.noBlur) {{ const b = (1 - e) * 9; if (b > 0.5) c.filter = `blur(${{b.toFixed(1)}}px)`; }}
  c.font = it.font; c.letterSpacing = it.track || '0px'; c.textAlign = 'center'; c.textBaseline = it.base || 'middle';
  if (o.glow) {{ c.shadowColor = o.glow; c.shadowBlur = o.glowBlur || 40; }}
  c.fillStyle = o.color || it.color; c.fillText(it.s, 0, 0);
  c.restore();
}}
function swipe(c, it, t, t0, dur, o = {{}}) {{
  const p = ez.out3(span(t, t0, t0 + dur)); if (p <= 0) return null;
  const px = parseFloat(/(\\d+)px/.exec(it.font)[1]), h = (o.h || 0.8) * px, pad = o.pad || 18, y = it.y + (o.dy || 0) - h / 2;
  const x = it.x - pad, w = (it.w + pad * 2) * p, r = rng('sw' + t0);
  const path = new Path2D();
  path.moveTo(x + r.in(0, 6), y + r.in(0, 5)); path.lineTo(x + w, y + r.in(-4, 2));
  path.lineTo(x + w + r.in(-5, 3), y + h + r.in(-2, 4)); path.lineTo(x + r.in(2, 8), y + h + r.in(-3, 2)); path.closePath();
  c.save(); c.fillStyle = o.color || C.hi; c.fill(path); c.restore();
  return path;
}}
function slamMarked(c, it, t, path, o = {{}}) {{
  slam(c, it, t, o);
  if (!path) return;
  c.save(); c.clip(path); slam(c, it, t, Object.assign({{}}, o, {{ color: C.black, glow: null }})); c.restore();
}}
function strike(c, x0, x1, y, p, col = C.red, w = 12, tilt = -0.025) {{
  if (p <= 0) return; const e = ez.out3(clamp(p)), x = lerp(x0, x1, e);
  c.save(); c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.shadowColor = col; c.shadowBlur = 12;
  c.beginPath(); c.moveTo(x0, y); c.lineTo(x, y + (x - x0) * tilt); c.stroke(); c.restore();
}}
function scribble(c, cx, cy, rx, ry, p, col, w, seed) {{
  if (p <= 0) return; const n = noise1(seed), N = 96, turns = 1.1, a0 = -2.4, m = Math.max(2, Math.ceil(N * clamp(p)));
  c.save(); c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath();
  for (let i = 0; i <= m; i++) {{ const u = i / N, a = a0 + u * turns * Math.PI * 2, k = 1 + 0.07 * n(u * 5 + seed) + 0.05 * u; const x = cx + Math.cos(a) * rx * k, y = cy + Math.sin(a) * ry * k; i ? c.lineTo(x, y) : c.moveTo(x, y); }}
  c.stroke(); c.restore();
}}
function handArrow(c, p0, q, p1, p, col, w) {{
  if (p <= 0) return; const N = 30, m = Math.max(2, Math.round(N * clamp(p))), pts = [];
  for (let i = 0; i <= m; i++) {{ const u = i / N, v = 1 - u; pts.push([v * v * p0[0] + 2 * v * u * q[0] + u * u * p1[0], v * v * p0[1] + 2 * v * u * q[1] + u * u * p1[1]]); }}
  c.save(); c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); pts.forEach((q2, i) => (i ? c.lineTo(q2[0], q2[1]) : c.moveTo(q2[0], q2[1]))); c.stroke();
  if (p >= 0.92) {{ const a = pts[pts.length - 1], b = pts[pts.length - 4], an = Math.atan2(a[1] - b[1], a[0] - b[0]), hl = 22;
    c.beginPath(); c.moveTo(a[0] - Math.cos(an - 0.55) * hl, a[1] - Math.sin(an - 0.55) * hl); c.lineTo(a[0], a[1]); c.lineTo(a[0] - Math.cos(an + 0.55) * hl, a[1] - Math.sin(an + 0.55) * hl); c.stroke(); }}
  c.restore();
}}
function rr(c, x, y, w, h, r) {{ c.beginPath(); c.roundRect(x, y, w, h, r); }}

// 3D Yaw Projector
function drawYaw(c, src, cx, cy, w, h, yaw, alpha) {{
  const f = 1500, cs = Math.cos(yaw), sn = Math.sin(yaw);
  const proj = (x) => {{ const X = x * cs, Z = x * sn, k = f / (f + Z); return {{ x: cx + X * k, k }}; }};
  const L = proj(-w / 2), R = proj(w / 2);
  c.save(); c.globalAlpha = alpha;
  c.save(); c.filter = 'blur(30px)'; c.fillStyle = 'rgba(0,0,0,0.7)'; c.beginPath();
  c.moveTo(L.x + 20, cy - (h * L.k) / 2 + 50); c.lineTo(R.x + 20, cy - (h * R.k) / 2 + 50); c.lineTo(R.x + 20, cy + (h * R.k) / 2 + 50); c.lineTo(L.x + 20, cy + (h * L.k) / 2 + 50); c.closePath(); c.fill(); c.restore();
  const sw = 3;
  for (let sx = 0; sx < src.width; sx += sw) {{
    const p0 = proj((sx / src.width - 0.5) * w), p1 = proj(((sx + sw) / src.width - 0.5) * w), hh = (h * (p0.k + p1.k)) / 2;
    c.drawImage(src, sx, 0, sw, src.height, p0.x, cy - hh / 2, p1.x - p0.x + 0.7, hh);
  }}
  const g = c.createLinearGradient(L.x, cy - h / 2, R.x, cy + h / 2); g.addColorStop(0, 'rgba(255,255,255,0.10)'); g.addColorStop(0.4, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(0,0,0,0.12)');
  c.fillStyle = g; c.beginPath(); c.moveTo(L.x, cy - (h * L.k) / 2); c.lineTo(R.x, cy - (h * R.k) / 2); c.lineTo(R.x, cy + (h * R.k) / 2); c.lineTo(L.x, cy + (h * L.k) / 2); c.closePath(); c.fill();
  c.restore();
}}

let STAMP = null;
function stampLayer(text, color) {{
  if (STAMP) return STAMP;
  STAMP = CM.layer(360, 190); const x = STAMP.getContext('2d');
  x.strokeStyle = color; x.lineWidth = 10; rr(x, 10, 10, 340, 170, 16); x.stroke();
  x.fillStyle = color; x.font = disp(116); x.textAlign = 'center'; x.textBaseline = 'middle'; x.letterSpacing = '4px'; x.fillText(text, 180, 100);
  x.globalCompositeOperation = 'destination-out'; const r = rng('stamp' + text);
  for (let i = 0; i < 420; i++) {{ x.globalAlpha = r.in(0.3, 1); x.beginPath(); x.arc(r() * 360, r() * 190, r.in(0.6, 2.6), 0, 7); x.fill(); }}
  return STAMP;
}}

// Background, Camera, Finishing
function background(c, t) {{
  c.fillStyle = C.bg; c.fillRect(0, 0, W, HH);
  const glow = (x, y, r, col) => {{ const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, HH); }};
  glow(W * 0.25 + Math.sin(t * 0.35) * 80, HH * 0.3 + Math.cos(t * 0.27) * 40, 620, 'rgba(255,214,10,0.055)');
  glow(W * 0.8 + Math.cos(t * 0.31) * 70, HH * 0.7 + Math.sin(t * 0.22) * 50, 640, 'rgba(90,120,255,0.05)');

  c.save(); c.strokeStyle = 'rgba(244,241,234,0.032)'; c.lineWidth = 1; c.beginPath();
  const off = (t * 8) % 80;
  for (let x = -off; x < W; x += 80) {{ c.moveTo(x, 0); c.lineTo(x, HH); }}
  for (let y = -off * 0.5; y < HH; y += 80) {{ c.moveTo(0, y); c.lineTo(W, y); }}
  c.stroke(); c.restore();

  const red = span(t, 27.5, 27.8) * (1 - span(t, 31.5, 31.7)) * (0.6 + 0.4 * span(t, 29.3, 30.5));
  if (red > 0) glow(W / 2, HH / 2, 800, `rgba(255,40,30,${{0.18 * red}})`);
}}

const NX = noise1(11), NY = noise1(23), NR = noise1(37);
const PUSH = [
  [0, 4.40], [4.68, 8.95], [9.19, 14.30], [14.56, 18.65],
  [18.81, 23.40], [23.62, 27.25], [27.47, 31.65], [31.91, 38.50]
];
function camera(t, si) {{
  let z = 1, dx = 0, dy = 0, rot = 0;
  const [a, b] = PUSH[si] || [0, 38.5]; z *= 1 + 0.035 * ez.inout3(span(t, a, b));
  if (si === 1) z *= 1 + 0.06 * ez.inout3(span(t, TL.least.pick, TL.least.pick + 0.35));
  for (const k of PUNCH) {{ const d = t - k.t; if (d < 0) continue; const e = d < 0.06 ? ez.out3(d / 0.06) : Math.exp(-(d - 0.06) * (k.k || 2.6)); z += k.a * e; }}
  for (const k of SHAKE) {{ const d = t - k.t; if (d < 0 || d > 1.4) continue; const e = k.a * Math.exp(-d * (k.k || 8)); dx += e * NX(t * 34 + k.t * 5); dy += e * NY(t * 37 + k.t * 3); rot += e * 0.0015 * NR(t * 26 + k.t); }}
  const fy = HH / 2;
  return {{ z, dx, dy, rot, fx: W / 2, fy }};
}}
const applyCam = (c, k) => {{ c.translate(W / 2 + k.dx, HH / 2 + k.dy); c.rotate(k.rot); c.scale(k.z, k.z); c.translate(-k.fx, -k.fy); }};

let GRAIN = null;
function grainTiles() {{ if (GRAIN) return GRAIN; GRAIN = []; for (let g = 0; g < 4; g++) {{ const L = CM.layer(256, 256), x = L.getContext('2d'), img = x.createImageData(256, 256), r = rng('grain' + g); for (let i = 0; i < img.data.length; i += 4) {{ const v = 128 + (r() + r() - 1) * 120; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }} x.putImageData(img, 0, 0); GRAIN.push(L); }} return GRAIN; }}
function finishing(c, t) {{
  for (const t0 of LEAK) {{ const u = span(t, t0, t0 + 0.95); if (u <= 0 || u >= 1) continue; const e = Math.sin(Math.PI * u);
    c.save(); c.globalCompositeOperation = 'screen'; const x = lerp(-150, W + 150, ez.out3(u)), g = c.createRadialGradient(x, 120, 0, x, 120, 760);
    g.addColorStop(0, `rgba(255,150,50,${{0.42 * e}})`); g.addColorStop(0.45, `rgba(255,70,40,${{0.16 * e}})`); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, HH); c.restore(); }}
  for (const f of FLASH) {{ const d = t - f.t; if (d < 0 || d > 0.4 || !f.a) continue; c.fillStyle = `rgba(${{f.col || '255,255,255'}},${{f.a * Math.exp(-d * 11)}})`; c.fillRect(0, 0, W, HH); }}
  const v = c.createRadialGradient(W / 2, HH / 2, 260, W / 2, HH / 2, Math.max(W, HH) * 0.7); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)'); c.fillStyle = v; c.fillRect(0, 0, W, HH);
  const fi = Math.floor(t * 24), r = rng(fi + 900), tile = grainTiles()[fi % 4];
  c.save(); c.globalAlpha = 0.07; c.globalCompositeOperation = 'overlay'; const pat = c.createPattern(tile, 'repeat'); pat.setTransform(new DOMMatrix().translateSelf(-r() * 256, -r() * 256)); c.fillStyle = pat; c.fillRect(0, 0, W, HH);
  c.globalAlpha = 0.035; c.globalCompositeOperation = 'source-over'; c.fillRect(0, 0, W, HH); c.restore();
}}

// Chrome: Clean Non-Overlapping Header
function chrome(c, t) {{
  const a = span(t, 4.4, 4.7) * (1 - span(t, 31.5, 31.7));
  if (a <= 0) return;
  c.save(); c.globalAlpha = a;
  const topY = IS_VERTICAL ? 180 : 48;
  const leftX = IS_VERTICAL ? 70 : 64;
  c.fillStyle = C.hi; c.fillRect(leftX, topY, 10, 10);
  c.font = inter(IS_VERTICAL ? 24 : 26, 700); c.letterSpacing = '3px'; c.fillStyle = C.dim; c.textBaseline = 'middle';
  c.fillText('AWS CLOUD IAM · SECURITY FOUNDATION', leftX + 22, topY + 6);
  c.restore();
}}

// Dynamic Word-by-Word Pop-In Karaoke Captions
function drawCaptions(c, t) {{
  const group = CAPTIONS.find(g => t >= g.start - 0.05 && t <= g.end + 0.35);
  if (!group) return;

  const y = IS_VERTICAL ? HH * 0.72 : HH - 65;
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

  // Background Glass Pill
  const padX = IS_VERTICAL ? 28 : 22, padY = IS_VERTICAL ? 14 : 10;
  const pillH = fontSize + padY * 2;
  const pillW = totalW + padX * 2;
  c.fillStyle = 'rgba(12, 12, 16, 0.85)';
  c.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  c.lineWidth = 1.5;
  rr(c, W / 2 - pillW / 2, y - pillH / 2, pillW, pillH, 16);
  c.fill(); c.stroke();

  // Words with active glow
  let curX = W / 2 - totalW / 2;
  group.words.forEach(w => {{
    const isActive = t >= w.start && t <= w.end;
    const wasActive = t > w.end;

    c.save();
    c.translate(curX + w.w / 2, y);
    if (isActive) {{
      c.scale(1.15, 1.15);
      c.fillStyle = '#ffd60a';
      c.shadowColor = 'rgba(255, 214, 10, 0.65)';
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

// =================================== SCENES ===================================

// Scene 0: Hook
function sceneHook(c, t) {{
  const H = TL.hook;
  const sy = IS_VERTICAL ? 460 : 180;
  const gapY = IS_VERTICAL ? 140 : 110;
  const sh = lerp(0, -40, ez.inout3(span(t, H.shift, H.shift + 0.3)));

  const r1 = [word('STOP', H.w1[0], disp(IS_VERTICAL ? 120 : 110), C.ink), word('USING', H.w1[1], disp(IS_VERTICAL ? 120 : 110), C.ink)];
  const r2 = [word('ROOT', H.w2[0], disp(IS_VERTICAL ? 150 : 140), C.red), word('CREDENTIALS.', H.w2[1], disp(IS_VERTICAL ? 150 : 140), C.ink)];
  row(c, r1, W / 2, sy + sh, 24); const b2 = row(c, r2, W / 2, sy + gapY + sh, 26);
  const dimA = 1 - 0.62 * span(t, H.strike, H.strike + 0.18);
  r1.forEach((it) => slam(c, it, t, {{ alpha: dimA }}));
  r2.forEach((it) => slam(c, it, t, {{ alpha: dimA, from: 1.6 }}));
  strike(c, b2.x0 - 24, b2.x0 + b2.w + 24, sy + gapY + sh, span(t, H.strike, H.strike + 0.16), C.red, 16);

  if (t >= H.use) {{
    const r3 = [
      word('use', H.use, inter(IS_VERTICAL ? 44 : 38, 600), C.dim, {{ base: 'alphabetic' }}),
      word('temporary credentials.', H.temp, serif(IS_VERTICAL ? 110 : 96), C.hi, {{ base: 'alphabetic' }})
    ];
    row(c, r3, W / 2, sy + gapY * 2.1, 20);
    slam(c, r3[0], t, {{ from: 1.15 }});
    slam(c, r3[1], t, {{ from: 1.6, glow: 'rgba(255,214,10,0.4)', glowBlur: 45 }});

    const p = span(t, H.under, H.under + 0.25);
    if (p > 0) {{
      const x0 = r3[1].x - 8, x1 = r3[1].x + r3[1].w + 12;
      c.save(); c.strokeStyle = C.hi; c.lineWidth = 9; c.lineCap = 'round'; c.beginPath();
      const n = 24; for (let i = 0; i <= n * p; i++) {{ const u = i / n, x = lerp(x0, x1, u), y = sy + gapY * 2.1 + 32 + Math.sin(u * 3.2) * 5 - u * 5; i ? c.lineTo(x, y) : c.moveTo(x, y); }}
      c.stroke(); c.restore();
    }}
  }}
}}

// Scene 1: Least Privilege
function sceneLeast(c, t) {{
  const S = TL.least;
  const hy = IS_VERTICAL ? 420 : 170;
  const head = [word('THE', S.w[0], disp(IS_VERTICAL ? 84 : 88)), word('GOLDEN', S.w[1], disp(IS_VERTICAL ? 84 : 88)), word('RULE:', S.w[2], disp(IS_VERTICAL ? 84 : 88), C.dim)];
  row(c, head, W / 2, hy, 20); head.forEach((it) => slam(c, it, t));

  const title = [word('LEAST', S.rule[0], disp(IS_VERTICAL ? 120 : 120), C.hi), word('PRIVILEGE.', S.rule[1], disp(IS_VERTICAL ? 120 : 120))];
  row(c, title, W / 2, hy + (IS_VERTICAL ? 110 : 95), 24); title.forEach((it) => slam(c, it, t));

  const chips = [
    {{ name: 'AdministratorAccess', icon: '⚡', chosen: false }},
    {{ name: 'Scoped S3 + DynamoDB', icon: '🔒', chosen: true }},
    {{ name: 'PowerUserAccess', icon: '⚡', chosen: false }}
  ];

  if (IS_VERTICAL) {{
    // Stack chips vertically for 9:16
    const startY = 720, stepY = 135, w = 820, h = 100;
    chips.forEach((chip, i) => {{
      const t0 = S.chips[i]; if (t < t0) return;
      const pop = ez.back(span(t, t0, t0 + 0.32), 2);
      const curY = startY + i * stepY;
      const dimA = chip.chosen ? 1 : 1 - 0.7 * span(t, S.drop, S.drop + 0.18);
      const lit = chip.chosen ? span(t, S.pick, S.pick + 0.12) : 0;

      c.save(); c.translate(W / 2, curY); c.scale(pop, pop); c.globalAlpha = dimA;
      if (lit > 0) {{ c.shadowColor = 'rgba(255,214,10,0.55)'; c.shadowBlur = 40; }}
      c.fillStyle = C.panel; rr(c, -w/2, -h/2, w, h, 16); c.fill();
      c.lineWidth = lit > 0 ? 3 : 1.5; c.strokeStyle = lit > 0 ? C.hi : C.line; rr(c, -w/2, -h/2, w, h, 16); c.stroke();

      c.font = '32px "Inter", sans-serif'; c.fillText(chip.icon, -w/2 + 50, 10);
      c.font = inter(28, 700); c.fillStyle = lit > 0 ? C.ink : C.dim; c.textBaseline = 'middle';
      c.fillText(chip.name, -w/2 + 100, 0);
      c.restore();

      if (!chip.chosen) strike(c, W/2 - w/2 + 20, W/2 + w/2 - 20, curY, span(t, S.drop, S.drop + 0.14), C.red, 6, 0);
    }});
    scribble(c, W / 2, startY + stepY, 430, 68, span(t, S.ring, S.ring + 0.38), C.hi, 6, 8);
    if (t >= S.only) {{
      const it = word('only what it needs.', S.only, serif(64), C.hi, {{ base: 'alphabetic' }});
      row(c, [it], W / 2, 1180, 0); slam(c, it, t);
    }}
  }} else {{
    // Horizontal 3-column for 16:9
    const X = [260, 640, 1020], Y = 430, w = 340, h = 100;
    chips.forEach((chip, i) => {{
      const t0 = S.chips[i]; if (t < t0) return;
      const pop = ez.back(span(t, t0, t0 + 0.32), 2);
      const dimA = chip.chosen ? 1 : 1 - 0.7 * span(t, S.drop, S.drop + 0.18);
      const lit = chip.chosen ? span(t, S.pick, S.pick + 0.12) : 0;

      c.save(); c.translate(X[i], Y); c.scale(pop, pop); c.globalAlpha = dimA;
      if (lit > 0) {{ c.shadowColor = 'rgba(255,214,10,0.55)'; c.shadowBlur = 40; }}
      c.fillStyle = C.panel; rr(c, -w/2, -h/2, w, h, 16); c.fill();
      c.lineWidth = lit > 0 ? 3 : 1.5; c.strokeStyle = lit > 0 ? C.hi : C.line; rr(c, -w/2, -h/2, w, h, 16); c.stroke();

      c.font = '28px "Inter", sans-serif'; c.fillText(chip.icon, -w/2 + 45, 8);
      c.font = inter(22, 700); c.fillStyle = lit > 0 ? C.ink : C.dim; c.textBaseline = 'middle';
      c.fillText(chip.name, -w/2 + 82, 0);
      c.restore();

      if (!chip.chosen) strike(c, X[i] - w/2 + 15, X[i] + w/2 - 15, Y, span(t, S.drop, S.drop + 0.14), C.red, 6, 0);
    }});
    scribble(c, 640, Y, 215, 95, span(t, S.ring, S.ring + 0.38), C.hi, 6, 8);
    if (t >= S.only) {{
      const it = word('only what it needs.', S.only, serif(60), C.hi, {{ base: 'alphabetic' }});
      row(c, [it], 930, 580, 0); slam(c, it, t);
      handArrow(c, [840, 560], [800, 540], [770, 490], span(t, S.arrow, S.arrow + 0.25), C.hi, 5);
    }}
  }}
}}

// Scene 2: Use Roles & 3D Console Mockup
let CONSOLE_LAYER = null;
function getConsoleLayer(t) {{
  if (!CONSOLE_LAYER) CONSOLE_LAYER = CM.layer(780, 480);
  const x = CONSOLE_LAYER.getContext('2d'), bw = 780, bh = 480;
  x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, bw, bh);

  x.fillStyle = '#16161a'; rr(x, 0, 0, bw, bh, 18); x.fill();
  x.strokeStyle = '#2c2c34'; x.lineWidth = 2; rr(x, 0, 0, bw, bh, 18); x.stroke();
  x.fillStyle = '#1f1f26'; rr(x, 0, 0, bw, 48, 18); x.fill();
  ['#ff5f57', '#febc2e', '#28c840'].forEach((col, i) => {{ x.fillStyle = col; x.beginPath(); x.arc(26 + i * 20, 24, 6, 0, 7); x.fill(); }});
  x.fillStyle = '#121215'; rr(x, 110, 10, 480, 28, 14); x.fill();
  x.fillStyle = '#8e8d94'; x.font = inter(15, 600); x.textBaseline = 'middle'; x.fillText('aws.amazon.com/iam/home#/roles/lambda-processor', 130, 24);

  x.fillStyle = '#ffffff'; x.font = disp(38); x.textBaseline = 'alphabetic'; x.fillText('ROLE: lambda-order-processor', 32, 105);
  x.fillStyle = '#8e8d94'; x.font = inter(16, 600); x.fillText('ARN: arn:aws:iam::123456789012:role/lambda-order-processor', 32, 130);

  const cards = [
    {{ title: 'Trust Entity', desc: 'lambda.amazonaws.com', badge: 'Active Trust', col: '#ff9900' }},
    {{ title: 'Permission Policy', desc: 'DynamoDBWriteAndS3GetOnly', badge: 'Scoped Least-Privilege', col: '#38bdf8' }},
    {{ title: 'Security Token Service (STS)', desc: 'sts:AssumeRole · 1 Hour Expiry', badge: 'Auto-Expiring Token', col: '#22c55e' }}
  ];
  cards.forEach((card, i) => {{
    const cy = 155 + i * 95, cw = 716, ch = 80;
    const lift = i === 2 && t > TL.roles.click ? ez.back(span(t, TL.roles.click, TL.roles.click + 0.25), 2) : 0;
    x.save(); x.translate(0, -lift * 4);
    x.fillStyle = '#1b1b22'; rr(x, 32, cy, cw, ch, 12); x.fill();
    x.strokeStyle = lift > 0 ? C.hi : '#2b2b36'; x.lineWidth = lift > 0 ? 2.5 : 1.5; rr(x, 32, cy, cw, ch, 12); x.stroke();

    x.fillStyle = '#ffffff'; x.font = inter(20, 700); x.textBaseline = 'middle'; x.fillText(card.title, 52, cy + 26);
    x.fillStyle = '#8e8d94'; x.font = inter(16, 500); x.fillText(card.desc, 52, cy + 54);

    x.fillStyle = card.col + '22'; x.strokeStyle = card.col; x.lineWidth = 1;
    rr(x, cw - 180, cy + 22, 195, 34, 8); x.fill(); x.stroke();
    x.fillStyle = card.col; x.font = inter(15, 700); x.textAlign = 'center'; x.fillText(card.badge, cw - 82, cy + 39);
    x.textAlign = 'left';
    x.restore();
  }});

  if (t > TL.roles.sub) {{
    const u = ez.inout3(span(t, TL.roles.sub, TL.roles.click - 0.05)), px = lerp(700, 580, u), py = lerp(460, 385, u);
    const ck = t > TL.roles.click ? span(t, TL.roles.click, TL.roles.click + 0.35) : 0;
    if (ck > 0 && ck < 1) {{ x.strokeStyle = `rgba(255,214,10,${{1 - ck}})`; x.lineWidth = 4; x.beginPath(); x.arc(px, py, 10 + 35 * ck, 0, 7); x.stroke(); }}
    x.save(); x.translate(px, py); x.scale(1.4, 1.4); x.fillStyle = '#111'; x.strokeStyle = '#fff'; x.lineWidth = 1.6;
    x.beginPath(); x.moveTo(0, 0); x.lineTo(0, 22); x.lineTo(5.5, 17); x.lineTo(9.5, 26); x.lineTo(13, 24.5); x.lineTo(9, 15.5); x.lineTo(16, 15.5); x.closePath(); x.fill(); x.stroke(); x.restore();
  }}
  return CONSOLE_LAYER;
}}

function sceneRoles(c, t) {{
  const R = TL.roles;
  if (IS_VERTICAL) {{
    // Vertical Layout: Text at top, 3D console centered below
    const l1 = [word('NEVER', R.w1[0], disp(90)), word('IAM', R.w1[1], disp(90)), word('USERS.', R.w1[2], disp(90))];
    const b1 = row(c, l1, W / 2, 420, 16); l1.forEach(it => slam(c, it, t));
    strike(c, b1.x0 - 10, b1.x0 + b1.w + 10, 420, span(t, R.strike1, R.strike1 + 0.16), C.red, 12);

    const l2 = [word('USE', R.w2[0], disp(120)), word('ROLES.', R.w2[1], disp(120), C.hi)];
    row(c, l2, W / 2, 540, 20); slam(c, l2[0], t);
    const path = swipe(c, l2[1], t, R.hl, 0.24, {{ h: 0.82, pad: 16, dy: 4 }});
    slamMarked(c, l2[1], t, path);

    const enter = ez.outExpo(span(t, R.br, R.br + 0.65)), yaw = lerp(-0.35, -0.15, enter);
    if (t > R.br) drawYaw(c, getConsoleLayer(t), W / 2, 920, 680, 420, yaw, Math.min(1, enter * 1.6));
  }} else {{
    // 16:9 Layout: Two Columns (Left: Text, Right: 3D Console)
    const enter = ez.outExpo(span(t, R.br, R.br + 0.65)), yaw = lerp(-0.58, -0.34, enter) + Math.sin(t * 0.9) * 0.015;
    if (t > R.br) drawYaw(c, getConsoleLayer(t), 880 + (1 - enter) * 520, 360 + Math.sin(t * 1.1) * 5, 590, 380, yaw, Math.min(1, enter * 1.6));

    const l1 = [word('NEVER', R.w1[0], disp(92)), word('IAM', R.w1[1], disp(92)), word('USERS.', R.w1[2], disp(92))];
    const b1 = row(c, l1, 72, 230, 18, 'left'); l1.forEach(it => slam(c, it, t));
    strike(c, b1.x0 - 10, b1.x0 + b1.w + 10, 230, span(t, R.strike1, R.strike1 + 0.16), C.red, 12);

    const l2 = [word('USE', R.w2[0], disp(120)), word('ROLES.', R.w2[1], disp(120), C.hi)];
    row(c, l2, 72, 350, 20, 'left'); slam(c, l2[0], t);
    const path = swipe(c, l2[1], t, R.hl, 0.24, {{ h: 0.82, pad: 16, dy: 4 }});
    slamMarked(c, l2[1], t, path);

    if (t > R.sub) {{
      c.save(); const u = ez.out3(span(t, R.sub, R.sub + 0.35)); c.globalAlpha = u;
      c.font = inter(26, 600); c.fillStyle = C.dim; c.textBaseline = 'middle';
      c.fillText('Temporary STS tokens. Zero stored keys.', 76, 440 + (1 - u) * 16); c.restore();
    }}
  }}
}}

// Scene 3: Policy Evaluation
function sceneDecide(c, t) {{
  const D = TL.decide;
  const hy = IS_VERTICAL ? 420 : 160;
  const head = [word('HOW', D.w[0], disp(IS_VERTICAL ? 84 : 88)), word('AWS', D.w[1], disp(IS_VERTICAL ? 84 : 88), C.hi), word('DECIDES:', D.w[2], disp(IS_VERTICAL ? 84 : 88))];
  row(c, head, W / 2, hy, 20); head.forEach(it => slam(c, it, t));

  const stack = [
    {{ num: '01', title: 'EXPLICIT DENY', sub: 'Evaluates first. Overrides everything.', col: C.red, bg: 'rgba(255,59,48,0.12)', border: C.red, stamp: 'OVERRIDE' }},
    {{ num: '02', title: 'EXPLICIT ALLOW', sub: 'Grants access if no explicit deny matches.', col: C.money, bg: 'rgba(61,255,143,0.08)', border: '#22c55e', stamp: 'ALLOWED' }},
    {{ num: '03', title: 'DEFAULT DENY', sub: 'Baseline state. Closed door by default.', col: C.dim, bg: '#18181d', border: C.line, stamp: 'BLOCKED' }}
  ];

  const sy = IS_VERTICAL ? 600 : 255;
  const stepY = IS_VERTICAL ? 160 : 110;
  const sw = IS_VERTICAL ? 860 : 880;
  const sh = IS_VERTICAL ? 120 : 90;

  stack.forEach((st, i) => {{
    const t0 = D.stack[i]; if (t < t0) return;
    const pop = ez.back(span(t, t0, t0 + 0.3), 1.8), y = sy + i * stepY;
    c.save(); c.translate(W / 2, y); c.scale(pop, pop);
    c.fillStyle = st.bg; c.strokeStyle = st.border; c.lineWidth = i === 0 ? 3.5 : 1.5;
    if (i === 0) {{ c.shadowColor = 'rgba(255,59,48,0.4)'; c.shadowBlur = 35; }}
    rr(c, -sw / 2, -sh / 2, sw, sh, 14); c.fill(); c.stroke(); c.shadowBlur = 0;

    c.fillStyle = st.col; c.font = disp(IS_VERTICAL ? 40 : 38); c.textBaseline = 'middle'; c.fillText(st.num, -sw / 2 + 35, 0);
    c.fillStyle = st.col === C.dim ? C.ink : st.col; c.font = disp(IS_VERTICAL ? 38 : 36); c.fillText(st.title, -sw / 2 + 105, -10);
    c.fillStyle = C.dim; c.font = inter(IS_VERTICAL ? 20 : 19, 500); c.fillText(st.sub, -sw / 2 + 105, 20);

    c.fillStyle = st.col; c.strokeStyle = st.col; c.lineWidth = 1.5;
    rr(c, sw / 2 - 180, -20, 150, 40, 8); c.stroke();
    c.font = disp(24); c.textAlign = 'center'; c.fillText(st.stamp, sw / 2 - 105, 0); c.textAlign = 'left';
    c.restore();
  }});

  if (t > D.ring) scribble(c, W / 2, sy, sw * 0.52, sh * 0.65, span(t, D.ring, D.ring + 0.35), C.hi, 6, 12);
  if (t >= D.note) {{
    const note = word('Explicit deny always wins. No exceptions.', D.note, serif(IS_VERTICAL ? 60 : 54), C.hi, {{ base: 'alphabetic' }});
    row(c, [note], W / 2, sy + stepY * 2.8, 0); slam(c, note, t, {{ from: 1.3 }});
  }}
}}

// Scene 4: Wildcards JSON Editor
function sceneWildcards(c, t) {{
  const Wd = TL.wild;
  const hy = IS_VERTICAL ? 420 : 160;
  const head = [word('AVOID', Wd.w[0], disp(IS_VERTICAL ? 84 : 92)), word('WILDCARDS', Wd.w[1], disp(IS_VERTICAL ? 84 : 92), C.red), word('IN', Wd.w[2], disp(IS_VERTICAL ? 84 : 92)), word('PROD.', Wd.w[3], disp(IS_VERTICAL ? 84 : 92))];
  row(c, head, W / 2, hy, 20); head.forEach((it) => slam(c, it, t));

  const enter = ez.outExpo(span(t, Wd.ed, Wd.ed + 0.5));
  if (enter <= 0) return;

  if (IS_VERTICAL) {{
    // Vertical Layout: Editor on top, Scoped Action card directly below
    const ew = 860, eh = 240;
    c.save(); c.translate(W / 2, 670); c.scale(enter, enter);
    c.fillStyle = '#111114'; rr(c, -ew / 2, -eh / 2, ew, eh, 14); c.fill();
    c.strokeStyle = '#272730'; c.lineWidth = 2; rr(c, -ew / 2, -eh / 2, ew, eh, 14); c.stroke();

    const lines = [
      {{ code: '{{ "Effect": "Allow",', col: '#fff' }},
      {{ code: '   "Action": "*",', col: C.red, strikeT: Wd.strike[0] }},
      {{ code: '   "Resource": "*" }}', col: C.red, strikeT: Wd.strike[1] }}
    ];
    c.font = '24px "Inter", monospace';
    lines.forEach((l, i) => {{
      const ly = -eh / 2 + 60 + i * 46;
      c.fillStyle = l.col; c.fillText(l.code, -ew / 2 + 50, ly);
      if (l.strikeT && t > l.strikeT) strike(c, -ew / 2 + 45, -ew / 2 + 280, ly, span(t, l.strikeT, l.strikeT + 0.15), C.red, 4, 0);
    }});
    c.restore();

    if (t > Wd.scoped) {{
      const sp = ez.back(span(t, Wd.scoped, Wd.scoped + 0.3), 1.8);
      c.save(); c.translate(W / 2, 980); c.scale(sp, sp);
      c.fillStyle = '#18241c'; c.strokeStyle = '#22c55e'; c.lineWidth = 2;
      rr(c, -ew / 2, -120, ew, 240, 14); c.fill(); c.stroke();
      c.fillStyle = '#22c55e'; c.font = inter(22, 800); c.fillText('✓ SECURE SCOPED ACTION', -ew / 2 + 40, -75);
      c.font = '22px "Inter", monospace'; c.fillStyle = '#e4e1db';
      c.fillText('"Action": ["s3:GetObject", "dynamodb:PutItem"]', -ew / 2 + 40, -30);
      c.fillText('"Resource": "arn:aws:s3:::app-data/*"', -ew / 2 + 40, 15);
      c.restore();
    }}
  }} else {{
    // 16:9 Layout: Two Columns (Left: JSON, Right: Scoped Action)
    const ew = 940, eh = 360;
    c.save(); c.translate(W / 2, 380); c.scale(enter, enter);
    c.fillStyle = '#111114'; rr(c, -ew / 2, -eh / 2, ew, eh, 16); c.fill();
    c.strokeStyle = '#272730'; c.lineWidth = 2; rr(c, -ew / 2, -eh / 2, ew, eh, 16); c.stroke();

    const lines = [
      {{ code: '{{', col: '#fff' }},
      {{ code: '  "Effect": "Allow",', col: '#38bdf8' }},
      {{ code: '  "Action": "*",', col: C.red, strikeT: Wd.strike[0] }},
      {{ code: '  "Resource": "*"', col: C.red, strikeT: Wd.strike[1] }},
      {{ code: '}}', col: '#fff' }}
    ];
    c.font = '24px "Inter", monospace';
    lines.forEach((l, i) => {{
      const ly = -eh / 2 + 75 + i * 40;
      c.fillStyle = l.col; c.fillText(l.code, -ew / 2 + 50, ly);
      if (l.strikeT && t > l.strikeT) strike(c, -ew / 2 + 45, -ew / 2 + 260, ly, span(t, l.strikeT, l.strikeT + 0.15), C.red, 4, 0);
    }});

    if (t > Wd.scoped) {{
      const sp = ez.back(span(t, Wd.scoped, Wd.scoped + 0.3), 1.8);
      c.save(); c.translate(230, 0); c.scale(sp, sp);
      c.fillStyle = '#18241c'; c.strokeStyle = '#22c55e'; c.lineWidth = 2;
      rr(c, -200, -135, 400, 270, 12); c.fill(); c.stroke();
      c.fillStyle = '#22c55e'; c.font = inter(20, 800); c.fillText('✓ SECURE SCOPED ACTION', -175, -95);
      c.font = '20px "Inter", monospace'; c.fillStyle = '#e4e1db';
      c.fillText('"Action": [', -175, -55);
      c.fillStyle = C.money; c.fillText('  "s3:GetObject",', -175, -20);
      c.fillText('  "dynamodb:PutItem"', -175, 15);
      c.fillStyle = '#e4e1db'; c.fillText(']', -175, 50);
      c.fillText('"Resource": "arn:aws:s3:::app-data/*"', -175, 85);
      c.restore();
    }}
    c.restore();
  }}
}}

// Scene 5: Breach Metric 99%
function sceneBreach(c, t) {{
  const M = TL.metric;
  const hy = IS_VERTICAL ? 440 : 150;
  const head = [word('BREACH', M.w[0], disp(IS_VERTICAL ? 80 : 88)), word('METRIC:', M.w[1], disp(IS_VERTICAL ? 80 : 88), C.dim), word('OVER-PRIVILEGED', M.w[2], disp(IS_VERTICAL ? 80 : 88)), word('KEYS', M.w[3], disp(IS_VERTICAL ? 80 : 88))];
  row(c, head, W / 2, hy, 20); head.forEach((it) => slam(c, it, t));

  if (t > M.cnt[0] - 0.15) {{
    const v = percentCount(t), lk = t > M.lock ? span(t, M.lock, M.lock + 0.4) : 0, pop = 1 + 0.16 * Math.sin(Math.PI * lk) * (lk < 1 ? 1 : 0);
    const cy = IS_VERTICAL ? 760 : 350;
    c.save(); c.translate(W / 2, cy); c.scale(pop, pop);
    c.font = disp(IS_VERTICAL ? 320 : 250); c.textAlign = 'center'; c.textBaseline = 'middle';
    c.shadowColor = `rgba(61,255,143,${{0.35 + 0.4 * (t > M.lock ? Math.exp(-(t - M.lock) * 2) : 0)}})`;
    c.shadowBlur = 80; c.fillStyle = C.money; c.fillText(v + '%', 0, 0);
    c.shadowBlur = 0; c.fillText(v + '%', 0, 0); c.restore();

    const age = t - M.lock;
    if (age > 0 && age < 0.9) {{
      const rr2 = rng('spark99'); c.save(); c.lineCap = 'round';
      for (let i = 0; i < 30; i++) {{
        const an = rr2() * Math.PI * 2, d0 = rr2.in(240, 480) * ez.out3(Math.min(1, age / 0.6)), len = 50 * (1 - age / 0.9);
        c.strokeStyle = i % 3 ? `rgba(61,255,143,${{1 - age / 0.9}})` : `rgba(255,255,255,${{1 - age / 0.9}})`; c.lineWidth = 4;
        c.beginPath(); c.moveTo(W / 2 + Math.cos(an) * d0, cy + Math.sin(an) * d0 * 0.7);
        c.lineTo(W / 2 + Math.cos(an) * (d0 + len), cy + Math.sin(an) * (d0 + len) * 0.7); c.stroke();
      }}
      c.restore();
    }}

    if (t >= M.sub1) {{
      const sub1 = word('of cloud security failures stem from misconfigured credentials', M.sub1, serif(IS_VERTICAL ? 62 : 60), C.ink, {{ base: 'alphabetic' }});
      row(c, [sub1], W / 2, cy + (IS_VERTICAL ? 260 : 170), 0); slam(c, sub1, t, {{ from: 1.4 }});
    }}
  }}
}}

// Scene 6: Wrong Move (Fatal Stamp)
function sceneWrong(c, t) {{
  const X = TL.wrong;
  const hy = IS_VERTICAL ? 460 : 220;
  const gapY = IS_VERTICAL ? 130 : 110;

  const r1 = [word('FIX', X.w1[0], disp(IS_VERTICAL ? 110 : 110)), word('PERMISSIONS', X.w1[1], disp(IS_VERTICAL ? 110 : 110))];
  const r2 = [word('AFTER', X.w2[0], disp(IS_VERTICAL ? 110 : 110)), word('WE', X.w2[1], disp(IS_VERTICAL ? 110 : 110)), word('LAUNCH?', X.w2[2], disp(IS_VERTICAL ? 110 : 110))];
  const b1 = row(c, r1, W / 2, hy, 24), b2 = row(c, r2, W / 2, hy + gapY, 24);
  const dimmed = span(t, X.strike[0], X.strike[0] + 0.2);
  [...r1, ...r2].forEach((it) => slam(c, it, t, {{ color: dimmed > 0.5 ? '#7a7a80' : it.color }}));
  strike(c, b1.x0 - 20, b1.x0 + b1.w + 20, hy, span(t, X.strike[0], X.strike[0] + 0.14), C.red, 15);
  strike(c, b2.x0 - 20, b2.x0 + b2.w + 20, hy + gapY, span(t, X.strike[1], X.strike[1] + 0.14), C.red, 15);

  if (t > X.stamp) {{
    const u = span(t, X.stamp, X.stamp + 0.13), s = lerp(2.4, 1, ez.in3(u));
    const sx = IS_VERTICAL ? W / 2 : 880;
    const sy = IS_VERTICAL ? 880 : 470;
    c.save(); c.translate(sx, sy); c.rotate(-0.16); c.scale(s, s); c.globalAlpha = Math.min(1, u * 3) * 0.95;
    c.drawImage(stampLayer('FATAL.', C.red), -180, -95); c.restore();
  }}
}}

// Scene 7: Takeaway (Zero Trust)
function sceneTake(c, t) {{
  const K = TL.take;
  const hy = IS_VERTICAL ? 440 : 210;
  const v = word('ZERO TRUST.', K.zero, disp(IS_VERTICAL ? 180 : 180), C.ink, {{ track: '4px' }}); row(c, [v], W / 2, hy, 0);
  const path = swipe(c, v, t, K.hl, 0.26, {{ h: 0.85, pad: 26, dy: 6 }});
  slamMarked(c, v, t, path, {{ from: 1.6 }});

  if (IS_VERTICAL) {{
    const r1 = [word('EVERY', K.w2[0], disp(120)), word('SERVICE.', K.w2[1], disp(120))];
    const r2 = [word('EVERY', K.w2[2], disp(120)), word('TIME.', K.w2[3], disp(120), C.hi)];
    row(c, r1, W / 2, hy + 150, 24); row(c, r2, W / 2, hy + 280, 24);
    [...r1, ...r2].forEach(it => slam(c, it, t));
  }} else {{
    const r2 = [word('EVERY', K.w2[0], disp(120)), word('SERVICE.', K.w2[1], disp(120)), word('EVERY', K.w2[2], disp(120)), word('TIME.', K.w2[3], disp(120), C.hi)];
    row(c, r2, W / 2, hy + 140, 24); r2.forEach(it => slam(c, it, t));
  }}

  if (t >= K.gold) {{
    const gold = word('The vault is locked.', K.gold, serif(IS_VERTICAL ? 72 : 62), C.hi, {{ base: 'alphabetic' }});
    row(c, [gold], W / 2, hy + (IS_VERTICAL ? 420 : 280), 0); slam(c, gold, t, {{ from: 1.3, glow: 'rgba(255,214,10,0.5)', glowBlur: 35 }});
  }}
}}

const SCENES = [sceneHook, sceneLeast, sceneRoles, sceneDecide, sceneWildcards, sceneBreach, sceneWrong, sceneTake];

// Compositor
const LA = CM.layer(W, HH), LB = CM.layer(W, HH), LT = CM.layer(W, HH), LR = CM.layer(W, HH), LG = CM.layer(W, HH);
function sceneIndex(t) {{ let i = 0; for (const c of CUTS) if (t >= c.t) i++; return i; }}
function paintScene(c, i, t) {{ c.save(); applyCam(c, camera(t, i)); SCENES[i](c, t); c.restore(); }}
function paintLayer(L, i, t, withBg) {{ const x = L.getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.filter = 'none'; x.clearRect(0, 0, W, HH); if (withBg) background(x, t); paintScene(x, i, t); return L; }}

function explainer(ctx, t) {{
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
  const idx = sceneIndex(t), cut = CUTS.find((c) => t >= c.t && t < c.t + c.d);
  if (!cut) {{ background(ctx, t); paintScene(ctx, idx, t); }}
  else {{
    const u = (t - cut.t) / cut.d, from = idx - 1, to = idx;
    if (cut.type === 'whip' || cut.type === 'whipV') {{
      background(ctx, t);
      const e = ez.inout3(u), vert = cut.type === 'whipV', dir = cut.dir || 1, D = vert ? HH : W, blur = Math.sin(Math.PI * u) * 170;
      paintLayer(LA, from, t, false); paintLayer(LB, to, t, false);
      const T = LT.getContext('2d'); T.setTransform(1, 0, 0, 1, 0, 0); T.clearRect(0, 0, W, HH); T.globalCompositeOperation = 'lighter';
      const N = 8; T.globalAlpha = 1 / N;
      for (let k = 0; k < N; k++) {{ const o = (k / (N - 1) - 0.5) * blur, oa = -e * D * dir + o, ob = (1 - e) * D * dir + o;
        if (vert) {{ T.drawImage(LA, 0, oa); T.drawImage(LB, 0, ob); }} else {{ T.drawImage(LA, oa, 0); T.drawImage(LB, ob, 0); }} }}
      T.globalCompositeOperation = 'source-over'; T.globalAlpha = 1; ctx.drawImage(LT, 0, 0);
    }} else if (cut.type === 'glitch') {{
      paintLayer(LA, u < 0.5 ? from : to, t, true);
      const fi = Math.floor(t * 60), r = rng('g' + fi), off = (8 + r() * 18) * Math.sin(Math.PI * u) * 1.6;
      const tint = (L, col) => {{ const x = L.getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.clearRect(0, 0, W, HH); x.drawImage(LA, 0, 0); x.globalCompositeOperation = 'multiply'; x.fillStyle = col; x.fillRect(0, 0, W, HH); x.globalCompositeOperation = 'source-over'; return L; }};
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, HH); ctx.globalCompositeOperation = 'lighter';
      ctx.drawImage(tint(LR, '#ff0000'), off, 0); ctx.drawImage(tint(LG, '#00ffff'), -off, 0); ctx.globalCompositeOperation = 'source-over';
      for (let k = 0; k < 9; k++) {{ const y = r() * HH, h = 6 + r() * 60, dx = (r() - 0.5) * 140 * Math.sin(Math.PI * u); ctx.drawImage(LA, 0, y, W, h, dx, y, W, h); }}
      if (r() > 0.4) {{ ctx.fillStyle = `rgba(255,255,255,${{0.08 + r() * 0.12}})`; ctx.fillRect(0, r() * HH, W, 2 + r() * 6); }}
    }} else {{
      background(ctx, t); paintScene(ctx, u < 0.5 ? from : to, t);
      ctx.fillStyle = `rgba(255,255,255,${{0.9 * (1 - Math.abs(u * 2 - 1))}})`; ctx.fillRect(0, 0, W, HH);
    }}
  }}
  chrome(ctx, t);
  drawCaptions(ctx, t);
  finishing(ctx, t);
}}

// Sound Score (SFX)
function scoreSound(k) {{
  const H = TL.hook, S = TL.least, R = TL.roles, D = TL.decide, Wd = TL.wild, M = TL.metric, X = TL.wrong, K = TL.take;

  k.drone(0, H.temp + 0.05, {{ gain: 0.9 }});
  k.play('riser', H.temp - 1.15, {{ dur: 1.15, gain: 0.7 }});
  k.music(H.temp, X.strike[0], {{ bpm: 98, gain: 0.85 }});
  k.music(K.zero, TL.D - 0.15, {{ bpm: 98, gain: 0.85 }});

  H.w1.forEach((t) => k.play('slam', t, {{ gain: 0.6 }}));
  k.play('slam', H.w2[0], {{ gain: 0.9 }}); k.play('boom', H.w2[0], {{ gain: 0.5 }});
  k.play('strike', H.strike, {{ gain: 0.8 }});
  k.play('boom', H.temp, {{ gain: 0.9 }}); k.play('slam', H.temp, {{ gain: 0.8 }});
  k.play('marker', H.under, {{ dur: 0.25, gain: 0.6, soft: true }});

  k.play('whoosh', CUTS[0].t - 0.04, {{ dur: 0.36, gain: 0.8, dir: 1 }});
  k.play('pop', S.pill, {{ f: 900, gain: 0.6 }});
  S.w.forEach((t) => k.play('slam', t, {{ gain: 0.5 }}));
  S.chips.forEach((t, i) => k.play('pop', t + 0.05, {{ f: 640 + i * 120, gain: 0.6 }}));
  k.play('strike', S.drop, {{ gain: 0.4 }});
  k.play('slam', S.pick, {{ gain: 0.7 }}); k.play('shimmer', S.pick + 0.02, {{ gain: 0.7 }});
  k.play('marker', S.ring, {{ dur: 0.35, gain: 0.55, soft: true }});

  k.play('glitch', CUTS[1].t, {{ gain: 0.8 }});
  k.play('pop', R.pill, {{ f: 900, gain: 0.6 }});
  R.w1.forEach((t) => k.play('slam', t, {{ gain: 0.55 }}));
  k.play('strike', R.strike1, {{ gain: 0.75 }});
  k.play('whoosh', R.br, {{ dur: 0.5, gain: 0.6, dir: -1 }});
  k.play('marker', R.hl, {{ dur: 0.22, gain: 0.8 }});
  k.play('click', R.click, {{ gain: 0.9 }});

  k.play('whoosh', CUTS[2].t - 0.04, {{ dur: 0.32, gain: 0.8, dir: 1 }});
  k.play('pop', D.pill, {{ f: 900, gain: 0.6 }});
  D.stack.forEach((t) => k.play('slam', t, {{ gain: 0.65 }}));
  k.play('marker', D.ring, {{ dur: 0.32, gain: 0.6, soft: true }});

  k.play('slam', CUTS[3].t + 0.05, {{ gain: 0.85 }});
  Wd.w.forEach((t) => k.play('slam', t, {{ gain: 0.55 }}));
  k.play('keys', Wd.type[0], {{ dur: 0.4, gain: 0.7 }});
  k.play('strike', Wd.strike[0], {{ gain: 0.75 }}); k.play('strike', Wd.strike[1], {{ gain: 0.75 }});
  k.play('pop', Wd.scoped, {{ f: 720, gain: 0.6 }});

  k.play('whoosh', CUTS[4].t - 0.04, {{ dur: 0.32, gain: 0.8, dir: 1 }});
  M.w.forEach((t) => k.play('slam', t, {{ gain: 0.55 }}));
  {{
    let last = -1, prev = percentCount(M.cnt[0] - 0.01);
    for (let t = M.cnt[0]; t < M.lock - 0.02; t += 1 / 240) {{
      const v = percentCount(t);
      if (v !== prev && t - last >= 1 / 12) {{
        k.play('tick', t, {{ f: 2400 + v * 12, gain: 0.5, soft: true }});
        last = t;
      }}
      prev = v;
    }}
  }}
  k.play('riser', M.cnt[0] + 0.1, {{ dur: M.lock - M.cnt[0] - 0.1, gain: 0.75 }});
  k.play('boom', M.lock, {{ gain: 1.2 }}); k.play('slam', M.lock, {{ gain: 0.9 }});
  k.play('shimmer', M.lock + 0.03, {{ gain: 1.0 }}); k.play('sparkle', M.lock + 0.08, {{ gain: 0.8 }});

  k.play('glitch', CUTS[5].t, {{ gain: 0.8 }});
  X.w1.forEach((t) => k.play('slam', t, {{ gain: 0.5 }}));
  X.w2.forEach((t) => k.play('slam', t, {{ gain: 0.5 }}));
  k.play('tapeStop', X.strike[0], {{ gain: 0.85 }});
  k.play('strike', X.strike[0], {{ gain: 0.8 }}); k.play('strike', X.strike[1], {{ gain: 0.8 }});
  k.play('stamp', X.stamp, {{ gain: 1.1 }});

  k.play('whoosh', CUTS[6].t - 0.04, {{ dur: 0.36, gain: 0.8, dir: -1 }});
  k.play('boom', K.zero, {{ gain: 1.0 }}); k.play('slam', K.zero, {{ gain: 0.9 }});
  k.play('marker', K.hl, {{ dur: 0.25, gain: 0.85 }});
  K.w2.forEach((t) => k.play('slam', t, {{ gain: 0.6 }}));
  k.play('shimmer', K.gold, {{ gain: 0.6 }});
}}

// Player Controller
const cvs = document.getElementById('stage'), ctx = cvs.getContext('2d');
window.seek = (t) => explainer(ctx, clamp(t, 0, DURATION));
window.DURATION = DURATION;
window.scoreSound = scoreSound;
window.SFX = SFX;

const ui = {{
  play: document.getElementById('play'),
  scrub: document.getElementById('scrub'),
  time: document.getElementById('time'),
  sound: document.getElementById('sound'),
  loop: document.getElementById('loop')
}};

let T = 0, playing = false, last = 0, soundOn = true, loopOn = true, stopSound = null;
const voAudio = new Audio('data:audio/mp3;base64,{vo_b64}');
voAudio.volume = 1.0;

const fmt = (t) => t.toFixed(2) + ' / ' + DURATION.toFixed(2);
function draw() {{ window.seek(T); ui.scrub.value = T; ui.time.textContent = fmt(T); }}

function startAudio() {{
  stopAudio(); if (!playing) return;
  if (soundOn) {{
    stopSound = SFX.live(scoreSound, T, {{ voiceover: true }});
    try {{
      voAudio.currentTime = T;
      const p = voAudio.play();
      if (p !== undefined) p.catch(() => {{}});
    }} catch (e) {{}}
  }}
}}
function stopAudio() {{
  if (stopSound) {{ stopSound(); stopSound = null; }}
  try {{ voAudio.pause(); }} catch (e) {{}}
}}
function setPlaying(p) {{
  playing = p; ui.play.textContent = p ? 'Pause' : 'Play';
  last = performance.now();
  if (p) startAudio(); else stopAudio();
}}

function tick(now) {{
  if (playing) {{
    T += (now - last) / 1000; last = now;
    if (T >= DURATION) {{
      if (loopOn) {{ T = 0; startAudio(); }}
      else {{ T = DURATION; setPlaying(false); }}
    }}
    draw();
  }}
  requestAnimationFrame(tick);
}}

let hasStarted = false;
ui.play.addEventListener('click', () => {{
  if (!playing && (T >= DURATION || !hasStarted)) {{
    T = 0;
    hasStarted = true;
  }}
  setPlaying(!playing);
}});
ui.scrub.addEventListener('input', () => {{ T = parseFloat(ui.scrub.value); draw(); if (playing) startAudio(); }});
ui.sound.addEventListener('click', () => {{
  soundOn = !soundOn; ui.sound.setAttribute('aria-pressed', soundOn);
  ui.sound.textContent = soundOn ? 'Sound on' : 'Sound off'; if (playing) startAudio();
}});
ui.loop.addEventListener('click', () => {{ loopOn = !loopOn; ui.loop.setAttribute('aria-pressed', loopOn); }});

(async () => {{
  try {{
    await Promise.all(['60px "Anton"', 'italic 60px "Instrument Serif"', '600 30px "Inter"', '700 30px "Inter"', '800 30px "Inter"'].map((f) => document.fonts.load(f, 'AaZz09')));
    await document.fonts.ready;
  }} catch (e) {{}}
  T = 0.81; draw();
  requestAnimationFrame((n) => {{ last = n; tick(n); }});
}})();
</script>
</body>
</html>
"""
    return html_content

# Save both HTML files
path_16x9 = os.path.join(OUT_DIR, "aws_iam_16x9_social.html")
path_9x16 = os.path.join(OUT_DIR, "aws_iam_9x16_shorts.html")

with open(path_16x9, "w") as f:
    f.write(generate_html(is_vertical=False))
print(f"Generated 16:9 HTML: {path_16x9}")

with open(path_9x16, "w") as f:
    f.write(generate_html(is_vertical=True))
print(f"Generated 9:16 HTML: {path_9x16}")

# Also copy to artifacts directory
ART_DIR = "/home/omthakur/.gemini/antigravity/brain/7ab7d57d-d84c-4ab6-a5eb-fe9859973ff2"
with open(os.path.join(ART_DIR, "aws_iam_16x9_social.html"), "w") as f:
    f.write(generate_html(is_vertical=False))
with open(os.path.join(ART_DIR, "aws_iam_9x16_shorts.html"), "w") as f:
    f.write(generate_html(is_vertical=True))
print("Saved artifacts copies.")
