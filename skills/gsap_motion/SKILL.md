---
id: gsap_motion
name: GSAP Motion & Kinetic Typography
badge: GSAP TIMELINE
reference_style: GreenSock / Kinetic Motion
description: >
  High-performance GPU-accelerated motion graphics, elastic eases, staggered typography,
  SVG path morphing, and complex multi-step timeline orchestrations.
references_urls:
  - "https://github.com/greensock/gsap-skills"
triggers: [gsap, greensock, tween, timeline, stagger, ease, elastic, kinetic, morph, scrolltrigger, flip, scrub, pin, svg, animation]
priority: 9
render:
  visual_style: dark-neon
  aspect_ratio: "16:9"
  backdrop: neon_chart
  allowed_visual_types: [animated_diagram, architecture, icons_labels, hybrid, chart]
  allowed_element_kinds: [node, icon, card, callout, title_card, label, box, group, arrow, route, packet, chart_bar]
  layout:
    max_elements_per_scene: 10
    require_position_hints: false
    min_gap_px: 28
  reveal:
    beat_sync: true
    lead_s: 0.10
    max_simultaneous_entrances: 2
  camera:
    max_zoom: 1.22
    allow_focus: true
    allow_pan: true
    idle_push_in: 1.04
  stock_card:
    enabled: false
    position: none
    max_seconds: 4.0
  captions:
    font_size: 42
    max_words_per_line: 6
sample:
  title: Mastering High-Performance Web Animation with GSAP
  topic: How GSAP timelines, GPU transforms, and stagger effects orchestrate fluid 60fps motion graphics.
  script: >-
    When building broadcast-grade web animations, GSAP is the industry standard for high-performance motion.
    Its core engine bypasses layout thrashing by animating transform matrices and opacity directly on the GPU.
    With GSAP Timelines, animators chain complex sequences, nesting multi-step tweens with sub-millisecond
    precision. Combined with elastic eases and staggers, static vectors spring to life with fluid cinematic momentum.
director_references: [references/gsap-rules.md]
---
# GSAP Motion & Kinetic Typography

This skill transforms static vectors and technical diagrams into kinetic, rhythm-driven motion sequences inspired by GreenSock.

## Core Rules
- Apply staggered reveals for multi-element groups (e.g. lists, metric chips, service grids).
- Favor bouncy, energetic eases (`back.out(1.7)`, `elastic.out(1, 0.3)`) on hero nodes and metric badges.
- Use high-contrast glowing lines and accent pulses to highlight state changes and data routing.
- Pair kinetic title cards with punchy callouts to keep viewers engaged even on mute.
