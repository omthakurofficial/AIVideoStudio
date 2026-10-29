# GSAP Motion Best Practices

## 1. Transform Over Layout
- Animate `x`, `y`, `scale`, and `rotation` instead of `top`, `left`, `width`, or `height` to prevent browser reflow.
- Use `autoAlpha` (combining `opacity` and `visibility`) for clean fade-in reveals.

## 2. Sequencing & Labels
- Group related tweens into nested timelines with relative timing offsets (`"<+=0.1"`).
- Keep entrance durations crisp: 0.35s to 0.65s for nodes, 0.2s stagger offsets between sibling elements.
