---
id: tech_architecture
name: Tech, Cloud & AI Architecture
badge: SVG CLOUD TILES
reference_style: Cloud X Berry / ByteByteGo / Fireship
description: >
  Dark technical grid, crisp service tiles (Route 53, API Gateway, Lambda, S3, RDS, Kubernetes), orthogonal
  connectors and glowing packets that travel the request path in the order the narration describes it.
references_urls:
  - "https://youtu.be/LPJ1zHDC0Ck"
  - "https://youtu.be/gjCBASA-1as"
  - "https://github.com/Vincentwei1021/anything2explainer"
  - "https://github.com/Vincentwei1021/video-shotcraft"
triggers: [aws, lambda, kubernetes, docker, microservice, api gateway, cloud, database, s3, ec2, server, cache, latency, request, load balancer, queue, rag, llm, api, cdn, dns, code, pipeline, repository, deploy, deployed, build, testing, test, software, devops, git, ci/cd]
priority: 9
render:
  visual_style: clean-technical
  aspect_ratio: "16:9"
  backdrop: tech_grid
  allowed_visual_types: [architecture, animated_diagram, icons_labels, chart, hybrid]
  allowed_element_kinds: [service_node, node, icon, card, callout, title_card, label, box, group, arrow, route, packet, chart_bar]
  layout:
    max_elements_per_scene: 12
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
    idle_push_in: 1.03
  stock_card:
    enabled: false
    position: none
    max_seconds: 4.0
  captions:
    font_size: 42
    max_words_per_line: 6
sample:
  title: AWS Cloud Architecture Will Finally Make Sense in 45 Seconds
  topic: How Route 53, CloudFront, API Gateway, Lambda, RDS and S3 work together in a serverless architecture.
  script: >-
    If AWS feels overwhelming with over two hundred services, you only need six core building blocks to understand
    ninety percent of cloud architecture. Every user request starts at Route fifty-three DNS and hits CloudFront at
    the edge before passing through IAM security and API Gateway. From there, serverless AWS Lambda functions execute
    your business logic in milliseconds without managing a single server. Structured transactions persist in Amazon
    RDS while static media and backups stream directly into Amazon S3.
director_references: [references/tech-rules.md]
---
# Tech, Cloud & AI Architecture

The diagram is built **left→right in request order** (top→bottom in 9:16). The viewer should be able to trace the
path of one request with the sound off.

## Rules
- Each service = `service_node` (or `icon`) labelled with its real name ("API Gateway", "AWS Lambda"). Tiles are
  colour-coded by layer: edge/DNS purple, security red, compute orange, storage green, database blue.
- Relationships are `flows_to` + an `arrow` with `from`/`to`. Draw the arrow (`draw`) only after both tiles are
  visible; then send a `packet` along it (`flow`, params.route = arrow id).
- Group tiers with `group` boxes ("Edge", "Compute", "Data") — at most 3 groups per scene.
- Layout is automatic from relationships (DAG ranks) — do NOT add x/y unless you need a specific asymmetry.
- Use a `chart_bar` or `callout` for numbers ("< 50 ms", "200+ services") — one per scene.
- One **hero** per scene (the service being explained) gets `highlight`; supporting tiles stay dim.

## Motion vocabulary (from anything2explainer / video-shotcraft, mapped to our actions)
| Intent | action | duration |
|---|---|---|
| tile entrance (SoftIn) | `appear` | 0.3 s, stagger 0.07 s per tile |
| connector draw-on | `draw` | 0.6–0.9 s |
| request travelling | `flow` packet | 1.0–2.0 s, repeat per hop |
| hero emphasis | `highlight` then `pulse` (peak 1.11×) | 1.0 s |
| state change | `scale` / `fade_out` of old tile | 0.3–0.4 s |

Light budget per frame: 1 hero glow + ≤1 accent glow. Camera: `focus` follows the packet's current hop; `static`
on the summary diagram.
