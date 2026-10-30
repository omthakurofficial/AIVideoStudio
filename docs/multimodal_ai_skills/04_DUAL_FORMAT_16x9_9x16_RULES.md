# 📱 04 · Dual-Format (16:9 & 9:16) Master Safe Zone Guide

> **Attach this file to ChatGPT, Gemini, or Claude.**
> Enforces strict pixel-perfect safe margins so graphics, text, characters, and captions never get cut off on YouTube, TikTok, Instagram Reels, or YouTube Shorts.

---

## 📐 Dual-Format Dimensions & Canvas Specs

| Format | Resolution | Aspect Ratio | Target Platforms | Key Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **16:9 Landscape** | `1280 x 720` or `1920 x 1080` | `16 : 9` | YouTube, Web, LinkedIn, Twitter/X | Cinematic layout, horizontal split screens, broad 3D yaw |
| **9:16 Vertical** | `1080 x 1920` | `9 : 16` | TikTok, Instagram Reels, YouTube Shorts | Vertical safe-zone clearance, centered eye-level focus |

---

## 🚨 9:16 Mobile Vertical UI Safe Zone Map

Mobile apps overlay intrusive UI icons (like button, comments, share, username, sound discs) that cover almost **40% of the screen**. Any text or prop placed in these red zones is completely invisible to viewers.

```
+------------------------------------------+ (Y = 0)
| ❌ TOP RESTRICTED ZONE (0 - 280px)       |  <-- App search bar, sound pills, close button
+------------------------------------------+ (Y = 280px)
|                                  | ❌    |
|   ✅ GOLDEN SAFE ACTION ZONE     | RIGHT |
|                                  | ICONS |  <-- Like, Comment, Share,
|   • Statement Caps (Y: 420px)    | ZONE  |      Bookmark, Remix icons
|   • 3D Mockup / Avatar (Y: 750px)| (880- |      (X: 880px to 1080px)
|   • Rolling Counter (Y: 1050px)  | 1080) |
|   • Karaoke Captions (Y: 1380px) |       |
|                                  |       |
+------------------------------------------+ (Y = 1480px)
| ❌ BOTTOM RESTRICTED ZONE (1480 - 1920px)|  <-- Username, caption description,
+------------------------------------------+      soundtrack marquee, buy buttons
```

### Strict Coordinates for 9:16 (1080 x 1920)
- **Top Safe Clearance**: Start content below `Y = 280px`.
- **Bottom Safe Clearance**: End all critical content above `Y = 1460px`.
- **Right Safe Margin**: Keep text and critical buttons to the left of `X = 860px`.
- **Karaoke Caption Placement**: **Eye-level** at `Y = 1380px` (centered at `X = 540px`, max width `780px`).
- **Hero Statement Placement**: Centered at `Y = 460px`.
- **3D Mockup / Character Center**: Centered at `Y = 820px`.

---

## 🖥️ 16:9 Landscape (1280 x 720) Coordinates
- **Top Chrome Header**: `left: 64px, top: 48px`.
- **Left Margin**: `64px`.
- **Right Margin**: `W - 64px` (`1216px`).
- **Hero Statement Placement**: Centered at `Y = 220px`.
- **3D Mockup / Character Center**: Centered at `Y = 380px` (or split-screen at `X = 380px` & `X = 900px`).
- **Karaoke Caption Placement**: Centered at `Y = 650px` (pad `24px` from bottom edge).

---

## 🔤 Responsive Font Sizing Matrix

To maintain readability across both phones and desktop monitors:

| Element Type | 16:9 Landscape (`1280x720`) | 9:16 Vertical Shorts (`1080x1920`) |
| :--- | :--- | :--- |
| **Big Statement Caps (`Anton`)** | `100px – 130px` | `110px – 150px` |
| **Yellow Accent Phrase (`Instrument Serif`)** | `54px – 64px` | `60px – 72px` |
| **Supporting Subtitle / Rule Line** | `28px – 34px` | `36px – 44px` |
| **3D Mockup Label / Pill Badge** | `18px – 24px` | `24px – 32px` |
| **Rolling Number Hero (`90%`, `99%`)** | `180px – 220px` | `200px – 240px` |
| **Karaoke Captions (`Inter 800`)** | `34px – 38px` | `44px – 48px` |
