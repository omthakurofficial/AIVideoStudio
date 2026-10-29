---
id: threejs_3d
name: Three.js 3D & WebGL Graphics
badge: 3D WEBGL MESH
reference_style: Three.js / CloudAI-X 3D Canvas
description: >
  Spatial WebGL scenes with 3D wireframe globes, rotating isometric meshes, floating spatial nodes,
  illuminated orbital splines, and camera orbit transitions.
references_urls:
  - "https://github.com/CloudAI-X/threejs-skills"
triggers: [threejs, 3d, webgl, canvas, mesh, globe, sphere, orbit, particle, rotation, spatial, polygon, wireframe, geometry, render3d, isometric]
priority: 8
render:
  visual_style: dark-neon
  aspect_ratio: "16:9"
  backdrop: tech_grid
  allowed_visual_types: [architecture, animated_diagram, icons_labels, hybrid, chart]
  allowed_element_kinds: [service_node, node, icon, card, callout, title_card, label, box, group, arrow, route, packet, chart_bar]
  layout:
    max_elements_per_scene: 10
    require_position_hints: false
    min_gap_px: 32
  reveal:
    beat_sync: true
    lead_s: 0.10
    max_simultaneous_entrances: 2
  camera:
    max_zoom: 1.25
    allow_focus: true
    allow_pan: true
    idle_push_in: 1.05
  stock_card:
    enabled: false
    position: none
    max_seconds: 4.0
  captions:
    font_size: 42
    max_words_per_line: 6
sample:
  title: Understanding 3D Spatial Computing and WebGL in 40 Seconds
  topic: How WebGL renders 3D meshes, vertex shaders, and camera matrices in modern browsers.
  script: >-
    Under the hood of 3D spatial computing, modern WebGL pipelines transform millions of mathematical
    vertices into interactive real-time geometry. First, the vertex shader computes object coordinates
    in spatial 3D world space. Next, fragment shaders calculate lighting models, casting ambient shadows
    and neon specular highlights across the mesh surface. Finally, the camera projection matrix maps
    everything onto your screen at sixty frames per second.
director_references: [references/threejs-rules.md]
---
# Three.js 3D & WebGL Graphics

This skill transforms complex technical or spatial concepts into 3D WebGL-styled explainer videos.

## Rules
- Feature a hero mesh or spatial entity in each scene (`service_node`, `icon`, or `group` labelled clearly).
- Use `arrow` and `route` elements with `packet` flows for data passing through 3D pipeline stages (Vertices -> Shaders -> Screen).
- Emphasize key metrics ("60 FPS", "< 16 ms frame budget") using `callout` or `card` badges.
- Keep typography crisp with high-contrast labels and metric callouts that stay legible even when muted.
