---
id: story_cartoon
name: Story & History Cartoon Explainer
badge: 2D CARTOON + MAP
reference_style: Oversimplified / Louisiana $15M Deal
description: >
  Shaded-relief map or illustrated stage + expressive 2D cartoon characters (diplomats, kings, ships, citizens),
  territory polygons and punchy action callouts. Characters act; text is minimal.
references_urls:
  - https://youtube.com/shorts/xtxTJJBtuww
triggers: [napoleon, louisiana, jefferson, empire, century, treaty, king, queen, war of, cartoon, emperor, dynasty, colony, revolution, diplomat]
priority: 8
render:
  visual_style: warm-documentary
  aspect_ratio: "9:16"
  backdrop: auto
  allowed_visual_types: [map, icons_labels, timeline, layered_motion, hybrid]
  allowed_element_kinds: [map_region, map_marker, icon, card, callout, title_card, label, arrow, route, packet, timeline_marker, box, node]
  layout:
    max_elements_per_scene: 10
    require_position_hints: false
    min_gap_px: 36
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
    font_size: 46
    max_words_per_line: 5
sample:
  title: "How America Bought Louisiana: Napoleon's $15M Deal"
  topic: How Jefferson's diplomats expected New Orleans and walked away with the whole Louisiana Territory.
  script: >-
    In eighteen oh three, the young United States had a huge problem: France controlled New Orleans and the mouth
    of the Mississippi River. President Thomas Jefferson sent diplomats across the Atlantic with a simple mission:
    offer Napoleon ten million dollars just to buy the port of New Orleans. But Napoleon needed cash fast for an
    impending war with Britain, so he shocked the Americans with a counter-offer: take the entire Louisiana Territory
    for fifteen million dollars. With one stroke of a pen, America doubled in size for less than four cents an acre.
---
# Story & History Cartoon Explainer

Characters carry the story. Every scene has a **protagonist icon** (a character: diplomat, king, citizen, ship) that
does something on the narration verb: arrives (`move`), argues (`pulse`), signs (`highlight` on a treaty scroll),
leaves (`fade_out`).

## Rules
- Characters are `icon` elements with descriptive labels ("Napoleon", "US Diplomat", "Treaty Scroll"); the renderer
  draws a matching 2D cartoon sprite. Max 2 characters facing each other per scene (x≈0.30 and x≈0.70).
- Territories are `map_region`s that change colour on the narration word (`highlight`), not new boxes.
- Money / goods / ships travel as `packet` with `flow` along a `route`.
- One punchline `callout` per scene (≤4 words, e.g. "$15 MILLION!") placed above the characters (y≈0.22).
- No stock photos (disabled): this style is fully illustrated.

## Vertical 9:16 layout
Headline y 0.10–0.18 · map/stage y 0.20–0.62 · characters y 0.62–0.74 · captions start y 0.82.

## Motion vocabulary
character entrance `appear` (pop) · walk/sail `move` 1.5–3 s · reaction `pulse` 0.8 s · territory flip `highlight`
1 s · money transfer `flow` 2 s · exit `fade_out`. Camera: `focus` on the speaking character; `zoom_out` for the
"reveal the whole territory" payoff.
