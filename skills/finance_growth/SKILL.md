---
id: finance_growth
name: Finance, Business & YouTube Growth
badge: NEON CHARTS + KPI
reference_style: Nion Anarchy / DecodingYT / financial analytics
description: >
  Dark carbon dot-grid, full-canvas neon-green growth curve, glass KPI cards with explicit numbers that count up
  on the spoken figure.
triggers: [views, subscriber, rpm, profit, revenue, stock market, portfolio, roi, monetiz, growth, inflation, gdp, salary, million, billion]
priority: 7
render:
  visual_style: dark-neon
  aspect_ratio: "16:9"
  backdrop: neon_chart
  allowed_visual_types: [chart, icons_labels, animated_diagram, hybrid]
  allowed_element_kinds: [chart_bar, chart_line, card, callout, title_card, label, icon, text, arrow]
  layout:
    max_elements_per_scene: 8
    require_position_hints: false
    min_gap_px: 28
  reveal:
    beat_sync: true
    lead_s: 0.08
    max_simultaneous_entrances: 2
  camera:
    max_zoom: 1.20
    allow_focus: true
    allow_pan: false
    idle_push_in: 1.04
  stock_card:
    enabled: true
    position: bottom_left
    max_seconds: 4.0
  captions:
    font_size: 44
    max_words_per_line: 6
sample:
  title: How Faceless Data Channels Scale to 820K Views in 30 Days
  topic: Retention curve, niche selection and RPM economics behind high-growth faceless channels.
  script: >-
    Why do some faceless documentary channels explode to eight hundred and twenty thousand views in thirty days
    while others stall at zero? First, they target high-RPM niches like geopolitics, cloud architecture, and macro
    finance where advertisers pay twelve to twenty-five dollars per thousand views. Second, they engineer the first
    eight seconds with a visual map or live growth chart that holds seventy-eight percent viewer retention. By
    compounding three data-driven uploads a week, subscriber velocity crosses seventy-eight thousand and turns a
    simple script pipeline into a scalable media asset.
---
# Finance, Business & YouTube Growth

Every number spoken must appear on screen at the moment it is spoken, as a KPI `card` or `chart_bar` with an
explicit numeric `value` prop and a unit label ("820K views", "$12–25 RPM", "78 % retention").

## Rules
- Max 3 KPI cards per scene, arranged in a row (16:9) or column (9:16); the chart owns the background.
- Bars `grow` from 0 to value on the spoken figure; line charts `draw`.
- Up = neon green, down = red; never more than two accent colours.
- `visual_type: comparison` is not in the schema — use `chart` with two bar groups for comparisons.

## Motion vocabulary
KPI card `appear` + `type_text` count-up (0.8–1.4 s) · bar `grow` 0.8 s · trend line `draw` 1.5 s · emphasis
`pulse` on the winning metric · camera `zoom_in` ≤1.2 on the final number.
