---
id: hyperframes
name: HyperFrames HTML & GSAP Video
badge: HTML5 HYPERFRAMES
reference_style: HyperFrames / Web-Code Video
description: >
  Agent-native code-to-video framework using standard HTML, CSS, JavaScript, and seekable GSAP timelines
  for deterministic frame-by-frame rendering of motion graphics and product explainers.
references_urls:
  - "https://github.com/heygen-com/hyperframes"
triggers: [hyperframes, hyperplugin, hyper, html5, web video, seekable, timeline, heygen, dom, css motion, headless, code video]
priority: 9
render:
  visual_style: clean-technical
  aspect_ratio: "16:9"
  backdrop: tech_grid
  allowed_visual_types: [animated_diagram, architecture, icons_labels, hybrid, chart]
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
  title: Agent-Native Code-to-Video with HyperFrames in 40 Seconds
  topic: How HyperFrames converts HTML, modern CSS, and seekable GSAP timelines into deterministic broadcast MP4 videos.
  script: >-
    In next-generation video engineering, HyperFrames treats the entire web browser as a deterministic video camera.
    Instead of proprietary timeline formats, you author motion sequences in standard HTML, CSS, and modern JavaScript.
    Every animation binds to a seekable GSAP timeline, allowing the headless renderer to capture exact, jitter-free
    frames on any hardware. From animated product launch teasers to kinetic UI explainers, HyperFrames delivers
    broadcast MP4 video directly from web code.
director_references: [references/hyperframes-rules.md]
---
# HyperFrames HTML & GSAP Video

This skill crafts web-native motion graphics and explainer videos based on HeyGen's HyperFrames framework (`heygen-com/hyperframes`).

## Core Rules
- Treat each visual scene as an isolated DOM layout composed with CSS Flexbox/Grid and semantic markup.
- Drive all motion through seekable, paused GSAP timelines (`tl.pause()`) indexed by frame time.
- Emphasize structured product cards, feature callouts, and kinetic metric chips with modern CSS styling.
- Ensure all transitions are frame-deterministic: never rely on wall-clock `setInterval` or live CSS animations.
