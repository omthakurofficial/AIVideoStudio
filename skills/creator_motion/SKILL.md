---
id: creator_motion
name: Creator Motion Graphics (Kinetic Type & 3D Style)
badge: CREATOR MOTION
reference_style: Nafay 3D / Business Creator / Kinetic Typography
description: >
  High-retention, code-driven kinetic typography on near-black editing suite, word-by-word expo-eased slams,
  Instrument Serif italic yellow emotional accents, 3D perspective mockups (drawYaw), rolling counters with white flash booms,
  and tactile rubber stamps. Pure Canvas + Web Audio SFX + Kokoro neural TTS with 0 cloud tokens.
references_urls:
  - https://github.com/omthakurofficial/AIVideoStudio
triggers: [kinetic, creator, typography, 3d_mockup, nafay, slam, rubber_stamp, tech, explain, architecture, shorts, reels, fast]
priority: 10
render:
  visual_style: creator-dark
  aspect_ratio: "both"
  allowed_visual_types: [kinetic_slam, 3d_yaw_mockup, rolling_counter, rubber_stamp, speed_timer, summary_checklist]
  allowed_element_kinds: [statement_caps, serif_accent, pill_card, strike_line, stamp_badge, code_window, metric_number]
  layout:
    max_elements_per_scene: 8
    min_statement_font_px: 80
    min_label_font_px: 24
    key_metric_font_px: 180
  pacing:
    words_per_minute: 150
    words_per_second: 2.5
    scene_interval_s: [4.0, 6.0]
  camera:
    punch_zooms: true
    screen_shake: true
    transitions: [whip, glitch, flash, whipV]
---

# Creator Motion Graphics — Master Locked Skill (`SKILL.md`)

> **For ChatGPT, Gemini, and Claude:**
> When the user gives you a topic (e.g., *"Kubernetes Architecture"*, *"Why Postgres Won"*, *"How Docker Works"*), a target duration (**1 to 5 minutes**), and an optional **Style Version (`v1`, `v2`, `v3`)**, follow this Master Locked Protocol.

---

## ⏱️ 1. Duration & Pacing Matrix (1 to 5 Minutes)

Neural TTS (**Kokoro-82M**) speaks at exactly **150 Words Per Minute (`2.5 spoken words per second`)**.
Every scene in this engine runs for **4.5 to 6.0 seconds** ($\approx 22 - 26\text{ spoken words}$ per scene) to sustain peak viral retention.

| Video Duration | Total Spoken Words | Scene Count | Words Per Scene | Story Arc Structure |
| :--- | :--- | :--- | :--- | :--- |
| **1 Minute (60s)** | **140 – 150 words** | **6 scenes** | 22 – 25 words | Hook ➔ Problem ➔ Mechanism ➔ Metric ➔ Rejection ➔ Takeaway |
| **2 Minutes (120s)** | **280 – 300 words** | **12 scenes** | 23 – 26 words | Hook ➔ 2 Problems ➔ 3 Deep Mechanism Dives ➔ 2 Benchmarks ➔ Rejection ➔ 3 Takeaways |
| **3 Minutes (180s)** | **420 – 450 words** | **18 scenes** | 23 – 26 words | Hook ➔ System Breakdown ➔ 6 Micro-Mechanics ➔ Real-world Failure Case ➔ Solution ➔ Final Framework |
| **4 Minutes (240s)** | **560 – 600 words** | **24 scenes** | 23 – 26 words | Full Masterclass: History ➔ 8 Architectural Pillars ➔ Tradeoffs ➔ Live Benchmark ➔ Deployment Checklist |
| **5 Minutes (300s)** | **700 – 750 words** | **30 scenes** | 23 – 26 words | Complete Deep-Dive Documentary with 5 distinct thematic acts (6 scenes per act) |

---

## 🎨 2. Master Locked Style Versions (Easily Switchable)

The user can choose or swap the style version anytime by stating `--style v1`, `--style v2`, `--style v3`, or `--style v4`:

### `Style v1: Creator Kinetic 3D` (Ground Truth Default)
- **Background**: Near-black `#09090b` with slow warm/cool radial glows and 24fps film grain.
- **Statement Typography**: `Anton` / `Bebas Neue` in massive condensed caps (`#f4f1ea`).
- **Emotional Accent**: `Instrument Serif` italic in glowing creator yellow (`#ffd60a`). Maximum 1 per line.
- **Numbers & Metrics**: Glowing neon green (`#30d158`).
- **Wrong Ideas / Flat Rejection**: Tactical red (`#ff3b30`) with tactile procedural rubber stamp.
- **3D Mockups**: Tilted browser/console windows (`drawYaw` angle $\pm 10^\circ$).

### `Style v2: Cyberpunk Neon SaaS` (Dark Tech Futuristic)
- **Background**: Void black `#050508` with electric cyan/magenta glowing grid.
- **Statement Typography**: `Syne 800` or `Space Grotesk` in pure white (`#ffffff`).
- **Emotional Accent**: `Fraunces` italic in neon cyan laser (`#00f0ff`).
- **Numbers & Metrics**: Laser purple/emerald (`#a855f7`).
- **Rejection**: Neon crimson (`#ff0055`) with holographic `[ DENIED ]` glitch tag.

### `Style v3: Minimalist Paper Explainer` (Vox / Editorial Clean)
- **Background**: Warm textured off-white `#f8f9fa` with subtle newsprint grain.
- **Statement Typography**: `Inter Black 900` or `Clash Display` in dark ink (`#111827`).
- **Emotional Accent**: `Newsreader Serif` italic in warm amber highlighter (`#f59e0b`).
- **Numbers & Metrics**: Forest green (`#059669`).
- **Rejection**: Carmine red (`#dc2626`) with physical red ink stamp.

### `Style v4: Deep Terminal CRT` (Hardcore Hacker / Systems)
- **Background**: CRT dark green/black `#040d06` with scanlines and phosphor bloom.
- **Statement Typography**: `JetBrains Mono 800` or `Silkscreen` in bright phosphor green (`#22c55e`).
- **Emotional Accent**: `VT323` italic in phosphor amber (`#fbbf24`).
- **Numbers & Metrics**: Bright cyan (`#06b6d4`).
- **Rejection**: High-voltage red (`#ef4444`) with ASCII `[ CRITICAL_FAIL ]` banner.

---

## 🛠️ 3. Master Locked Motion & Visual Syntax

Every scene generated by ChatGPT/Gemini must map narration to these exact visual syntax tags:

1. **`[SLAM: WORDS]`**: Massive caps slamming in one at a time, starting blurred and large, settling with expo-ease.
2. **`[SERIF_ACCENT: italic phrase]`**: The one emotional or soft phrase set in Instrument Serif italic accent color.
3. **`[STRIKE: wrong phrase]`**: Dynamic red strikethrough line sweeping across the obsolete idea.
4. **`[3D_YAW: mockup_name, angle]`**: 3D tilted card/dashboard/browser window with isolated feature pills.
5. **`[SPEED_TIMER: target_ms]`**: High-speed rolling timer (e.g. `0ms ➔ 85ms`) in neon green.
6. **`[ROLLING_STAT: start% -> target%]`**: Rolling counter that locks with a white screen flash, screen shake, and boom sound.
7. **`[RUBBER_STAMP: WORD]`**: Heavy tactile rubber stamp slamming down with dust burst and camera shake (`[ DEPRECATED ]`, `[ EXPOSED ]`, `[ FATAL ]`).
8. **`[CHECKLIST: item1 | item2 | item3]`**: 3-point checkmark badge cards popping with overshoot (`ez.outBack`).
9. **`[SFX: cue]`**: `slam`, `boom`, `shimmer`, `stamp`, `whoosh`, `glitch`, `marker`, `pop`, `click`.

---

## 📋 4. Locked Output Schema for ChatGPT / Gemini

When generating, ChatGPT/Gemini **must output this exact clean structure**:

```markdown
# [Project Title]
- Topic: [Topic]
- Target Duration: [Duration] ([Word Count] Spoken Words)
- Style Version: [Style Version: v1 / v2 / v3 / v4]
- Voice: am_adam (speed 1.0)
- Aspect Ratios: 16:9 Landscape & 9:16 Shorts

---

## Scene 01: [Scene Title]
- Timing: [0.0s - 5.0s] (23 words)
- Narration: "[Exact spoken words to be voiced by Kokoro TTS]"
- Visual Choreography:
  - [SLAM: "KEY STATEMENT"] (Font: Display Caps)
  - [STRIKE: "OBSOLETE CONCEPT"]
  - [SERIF_ACCENT: "the emotional takeaway"]
- 3D Props / Mockups: [None / 3D Console drawYaw / Architecture Stack]
- Camera Move: [Punch zoom on "KEY STATEMENT" + subtle screen shake]
- Transition Out: [Whip Pan Right / RGB Glitch / White Flash / Whip Vertical]
- Sound Effects: [SFX: slam on word 1, SFX: strike on word 3, SFX: pop on accent]

[Repeat for Scene 02 through Scene N]
```
