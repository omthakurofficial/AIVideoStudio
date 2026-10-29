# HyperFrames Architecture & Rendering Rules

## 1. Deterministic Frame Seeking
- HyperFrames never records live screen captures. Instead, the renderer pauses the global timeline and seeks to exact timestamps: `tl.seek(t)`.
- All CSS animations must be driven via seekable GSAP tweens rather than `@keyframes` to guarantee 0 dropped frames.

## 2. DOM Component Blueprint
- Organize visual elements into semantic containers:
  - `.hero-container`: primary subject card or graphic
  - `.callout-dock`: floating stat pills and metric chips
  - `.connector-layer`: SVG paths with dashed stroke offsets
- Use CSS variables (`var(--accent)`, `var(--panel-bg)`) to keep visual themes consistent across scenes.

## 3. Performance & Asset Preloading
- All local SVGs, fonts, and images must be fully loaded before frame 0 rendering begins (`document.fonts.ready`).
