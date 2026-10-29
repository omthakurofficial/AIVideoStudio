---
id: vox_documentary
name: Vox Documentary Explainer
badge: VOX ARCHIVAL
reference_style: Vox / Stav Zilber / rom1trs paper-collage editorial
description: >
  Textured archival paper + blueprint grid, highlighter-swept headlines, white-bordered photo cut-outs with drop
  shadows, curved editorial arrows. Beat-driven: a hook in ≤3 s, a visual change every 3–5 s.
references_urls:
  - https://youtu.be/DceFrd65KUg
  - https://github.com/Alisa0808/vox-director
  - https://github.com/Anil-matcha/vox-ai-motion-graphics-generator
triggers: [why, how, history, investigation, explained, evidence, archive, actually, policy, economy, decade, percent]
priority: 5
render:
  visual_style: light-minimal
  aspect_ratio: "16:9"
  backdrop: vox_paper
  allowed_visual_types: [animated_diagram, map, chart, timeline, icons_labels, layered_motion, hybrid]
  allowed_element_kinds: [title_card, callout, card, icon, label, text, map_region, map_marker, chart_bar, chart_line, timeline_marker, arrow, route, image, box, node]
  layout:
    max_elements_per_scene: 10
    require_position_hints: false
    min_gap_px: 40
  reveal:
    beat_sync: true
    lead_s: 0.12
    max_simultaneous_entrances: 1
  camera:
    max_zoom: 1.22
    allow_focus: true
    allow_pan: true
    idle_push_in: 1.05
  stock_card:
    enabled: true
    position: auto
    max_seconds: 5.0
  captions:
    font_size: 42
    max_words_per_line: 6
sample:
  title: How Nepal's 15-Minute Timezone & River Geography Shape South Asia (Vox Style)
  topic: A Vox-style visual investigation into why Nepal sits on a unique UTC+5:45 timezone.
  script: >-
    Look closely at a map of South Asia and you will notice something unusual about Nepal. While India runs on UTC
    plus five thirty and China runs on UTC plus eight, Nepal split the difference in nineteen eighty-six to create
    its own fifteen-minute offset: UTC plus five forty-five, anchored to Mount Gauri Shankar. That same extreme
    Himalayan geography controls the region's water: eighty percent of Nepal's annual rainfall arrives in just three
    monsoon months, carving deep gorges from Kathmandu to the Koshi plains.
director_references: [references/beat-layer.md]
---
# Vox Documentary Explainer

Adapted from the **vox-director** skill (story layer = `references/beat-layer.md`, look layer =
`references/prompt-guide.md`). Our renderer is deterministic motion graphics, not AI image→video, so the "poster"
of each beat is built from editorial primitives instead of a generated collage image.

## Story layer (must follow)
- Pick an **arc** that fits the topic: `timeline` (history), `how_it_works` (explainer), `myth_buster`,
  `man_in_hole` (transformation), `pas`/`bab` (ads). State it in the first scene's `director_notes`.
- **Scene 1 = hook in ≤3 s**: a `title_card` with a bold claim / surprising stat / direct question (≤5 words).
  Hook patterns: surprising_stat · direct_question · mistake_callout · outcome_tease.
- **Cadence:** something visibly changes every 3–5 s. A scene longer than 8 s needs ≥2 internal beats
  (a wide establishing layout, then a detail emphasis — `camera focus` on one element).
- **Ending:** hard cut on the payoff, or a loop-close mirroring scene 1's headline.

## Look layer (translated to our primitives)
- One **headline** per scene: `title_card` (the renderer draws a highlighter sweep behind it). ≤5 words, quoted
  facts only.
- **Evidence** = `callout` with a dated subtitle ("1986 · Govt. decree") or a stock image request (renders as a
  tilted white-bordered cut-out). Request specific archival queries in `asset_requirements`.
- **Arrows are curved editorial arrows** (`arrow` with `from`/`to`) — use them to point from evidence to the claim.
- Palette travels across scenes to carry mood (sepia → bold → resolution); keep one accent colour per scene.
- Never 3D, never photoreal UI chrome; flat paper, print grain, drop shadows.

## Locks
- 1 entrance at a time (Vox reveals one idea per beat), ≤7 elements, explicit `x`,`y` everywhere.
- Text never overlaps text: headline band y≤0.18, captions band y≥0.85, cards in between.

## Motion vocabulary
| Intent | action | notes |
|---|---|---|
| headline slam | `appear` on title_card | scale-pop overshoot, 0.5 s |
| highlighter sweep | `highlight` | left→right, 0.6 s |
| evidence drop-in | `fade_in` + `move` | slide ≤120 px, 0.5–0.7 s |
| connect claim | `draw` arrow | 0.8–1.2 s |
| count-up stat | `type_text` on a number label | 0.8–1.5 s |
| exit | `fade_out` | reach 0 before the cut |

Camera moves (one per scene, vary across adjacent scenes): `zoom_in` push, `focus` on evidence, `pan` across a
timeline, `static` on the payoff.
