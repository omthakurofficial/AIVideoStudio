# Remotion Development & Architecture Rules

## 1. Frame-Accurate Timing
- Every animation must derive strictly from the current frame index: `frame / fps`.
- Never use `Date.now()` or `setTimeout()` inside animation loops; use `interpolate()` with clamped ranges.

## 2. Spring Physics
- Use `spring({ frame, fps, config: { damping: 12, mass: 0.5, stiffness: 100 } })` for organic entrances.
- Entrance animations should complete within 12-18 frames (~0.4-0.6 seconds) to maintain brisk pacing.

## 3. Composition Structuring
- Organize complex videos into nested `<Series>` and `<Sequence>` components with clear z-index layering.
