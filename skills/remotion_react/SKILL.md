---
id: remotion_react
name: Remotion React Video
badge: REACT COMPOSITION
reference_style: Remotion / Programmatic Video
description: >
  Frame-accurate programmatic video compositions built with React, declarative JSX timelines,
  spring physics, interpolate keyframing, and component-driven kinetic layouts.
references_urls:
  - "https://github.com/remotion-dev/skills"
triggers: [remotion, react, jsx, component, spring, interpolate, composition, sequence, programmatic, frame, usecurrentframe, usevideoconfig, canvas, motion]
priority: 9
render:
  visual_style: clean-technical
  aspect_ratio: "16:9"
  backdrop: tech_grid
  allowed_visual_types: [architecture, animated_diagram, icons_labels, hybrid, chart]
  allowed_element_kinds: [service_node, node, icon, card, callout, title_card, label, box, group, arrow, route, packet, chart_bar]
  layout:
    max_elements_per_scene: 10
    require_position_hints: false
    min_gap_px: 28
  reveal:
    beat_sync: true
    lead_s: 0.10
    max_simultaneous_entrances: 2
  camera:
    max_zoom: 1.20
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
  title: Declarative Programmatic Video with Remotion in 40 Seconds
  topic: How Remotion uses React components, spring physics, and frame-accurate scheduling to build videos with code.
  script: >-
    In modern web video production, Remotion bridges the gap between software engineering and motion design.
    Instead of editing in Premiere, you write declarative React components with frame-by-frame precision.
    The useCurrentFrame hook drives deterministic animation curves, while the spring function adds organic
    momentum to entering elements. Every composition renders headless in CI/CD, outputting pristine broadcast
    MP4 videos directly from TypeScript.
director_references: [references/remotion-rules.md]
---
# Remotion React Video

This skill crafts declarative, developer-centric explainer videos modeling Remotion's React-based video architecture.

## Core Rules
- Treat each beat as an isolated React `<Sequence>` with strict start and end frame bounds.
- Use `spring()`-inspired physics for UI node entrances: crisp snap-in with minimal overshoot.
- Feature technical cards and service nodes with clean syntax and metric callouts (`< 16 ms`, `60 FPS`).
- Keep backgrounds dark or clean-grid with glowing neon accents to match modern frontend developer aesthetics.
