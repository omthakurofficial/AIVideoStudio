---
id: geopolitics_map
name: Geopolitics & Real Map Atlas
badge: MAP + GEOJSON
reference_style: Johnny Harris / MirAtlas60 / GeoGlobeTales
description: >
  Real satellite / shaded-relief basemap, exact GeoJSON borders, glowing country fill, pins that sit on
  true coordinates and callouts that never cover each other. One idea per beat, revealed when spoken.
references_urls:
  - "https://youtu.be/6oZ9fdM0n50"
  - "https://github.com/remotion-dev/skills"
triggers: [border, map, country, river, himalaya, nepal, india, china, territory, region, capital, geography, flood, monsoon, kathmandu, delhi, valley, basin, km]
priority: 10
render:
  visual_style: warm-documentary
  aspect_ratio: "16:9"
  backdrop: map
  allowed_visual_types: [map, timeline, icons_labels, hybrid, animated_diagram]
  allowed_element_kinds: [map_region, map_marker, icon, callout, card, arrow, route, packet, timeline_marker, box, label, node]
  layout:
    max_elements_per_scene: 10
    require_position_hints: false
    min_gap_px: 32
  reveal:
    beat_sync: true
    lead_s: 0.10
    max_simultaneous_entrances: 2
  camera:
    max_zoom: 1.18
    allow_focus: true
    allow_pan: true
    idle_push_in: 1.04
  stock_card:
    enabled: true
    position: top_right
    max_seconds: 4.5
  captions:
    font_size: 44
    max_words_per_line: 6
sample:
  title: Nepal Monsoon Floods & Himalayan Geography (2D Atlas Documentary)
  topic: Why Nepal's steep Himalayan river basins and Kathmandu Valley face extreme monsoon flash floods.
  script: >-
    Sandwiched between India and China, Nepal rises from flat southern plains to the tallest peaks on Earth in less
    than two hundred kilometers. When record late-monsoon cloudbursts strike the Mahabharat range, over three hundred
    millimeters of rain funnels directly into the bowl-shaped Kathmandu Valley. Within hours, the Bagmati and
    Bishnumati rivers surge four meters above danger level, inundating riverside neighborhoods and highways. Further
    east, the massive Sapta Koshi basin collects torrential runoff from seven Himalayan tributaries, forcing all
    fifty-six barrage gates open as helicopter and raft teams race to rescue stranded communities.
director_references: [references/map-rules.md]
---
# Geopolitics & Real Map Atlas

The map IS the story. A viewer with the sound off must understand each beat from what is lit up on the map.

## Scene grammar
1. **Establish (beat 1, ≤3 s):** `map_region` for the primary country fades in first, neighbours second. Hook text
   in `on_screen_text` (≤5 words).
2. **Locate:** each place named in the narration gets ONE `map_marker` with real `lat`/`lon` props
   (e.g. Kathmandu 27.7172/85.3240, New Delhi 28.6139/77.2090, Kalapani 30.22/80.93). Never rely on the label to
   guess coordinates. A marker appears on the word that names it.
3. **Connect:** relationships between places are `route`/`arrow` with `from`/`to` and a `draw` action — the line
   draws over 1.5–2.5 s *after* both endpoints are visible.
4. **Explain:** at most one `callout` or `card` at a time; it must sit in empty ocean / sky / off-country space,
   never on top of a pin. Use `x`,`y` hints in the outer 25 % of the frame (left column x≤0.22 or right column
   x≥0.78) so the country stays clear.
5. **Payoff:** last beat removes clutter (`fade_out` older callouts) and zooms ≤1.18× on the subject.

## Locks the renderer enforces
- Explicit `x`,`y` on every non-connector element; `lat`/`lon` on every marker and on icons that represent a place.
- ≤8 elements per scene, ≤2 entrances at the same instant, nothing but the base regions at t=0.
- Stock photo picture-in-picture sits **top-right** for ≤4.5 s; never place callouts in the top-right quadrant
  (x>0.70 and y<0.35) of a scene that has a stock asset request.

## Typography
- Country names: uppercase, bold, inside a dark pill with gold stroke — rendered automatically from `map_region`.
- Marker callouts: title (≤3 words) + subtitle (≤4 words, a fact, e.g. "Capital of Nepal"). No enums, no ids,
  no placeholder text like "TIMELINE MARKER".
- On-screen headline: one short banner per idea, ≤5 words, never repeating the caption verbatim.

## Motion vocabulary (pick from these, don't invent)
| Intent | action | duration |
|---|---|---|
| region reveal | `fade_in` | 1.0–1.5 s |
| pin drop | `appear` (renderer adds scale-pop 78→105→100 %) | 0.6–0.8 s |
| connection | `draw` on route/arrow | 1.5–2.5 s |
| movement of goods/people | `flow` packet along route | 2–4 s |
| emphasis | `pulse` / `highlight` | 1.2–2.0 s, max 1 per beat |
| exit | `fade_out` | 0.4–0.6 s |

Camera: `focus` on the marker being discussed, or `zoom_in` ≤1.18. Never pan and zoom in the same beat.
