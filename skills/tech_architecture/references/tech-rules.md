# Tech Diagram & Executive Motion Design Rules

Distilled from `skills/_vendor/anything2explainer/motion-vocabulary.md` + Cloud X Berry / ByteByteGo executive references:

## 1. Visual Archetypes & Rich Components (Never Use Single Generic Cards)
Every technical scene MUST be planned using one of the 6 dynamic visual archetypes:
1. **Facility & Server Rack Grid** (`archetype="datacenter"`):
   - Multi-rack server warehouse with realistic blinking status LEDs and ventilation grills.
   - Use for physical data centers, co-location, server hardware.
2. **Tooling & Access Mockups** (`archetype="tooling_gateways"`):
   - Tri-pane application windows: Web Browser (AWS Console), Dark Terminal (AWS CLI with prompt), VS Code (Python Boto3 SDK).
   - Use for developer tools, APIs, CLIs, SDKs, and deployment walkthroughs.
3. **Comparative Scale / Matrix** (`archetype="comparison"`):
   - Two-column split comparing On-Premises (CapEx) vs Cloud (OpEx), Monolith vs Microservices.
   - Feature rows with contrast tags (red constraints vs green elastic benefits).
4. **Topology & Infrastructure Map** (`archetype="region_topology"`):
   - Master Region container holding 3 isolated Availability Zones linked by low-latency (<1ms) private fiber.
   - Use for global infrastructure, regions, AZ fault tolerance, and multi-region replication.
5. **Squircle Entity Stacks** (`kind="icon"`, `variant="squircle"`):
   - Apple/macOS superellipse cards with diffuse drop shadows for providers (Amazon, Microsoft, Google, AWS, Docker, Kubernetes).
6. **Feature Callout Pills** (`kind="callout"`, `archetype="pill"`):
   - Floating horizontal pills with colored icon boxes (Power, Network, Cooling, SLA, Zero Trust).

## 2. Multi-Zone Spatial Layout Grid
Never drop a single box in the center of the screen. Compose each scene across 4 distinct zones:
- **Top Bar**: Scene Topic title with accent bar on left; Chapter Progress Pill (`01 / 15`) on right.
- **Left Column**: Entity/Brand squircle badges or contextual anchor.
- **Hero Center Stage**: The primary archetype (Server Grid, Region Map, Comparison, or Tooling Mockup).
- **Right Column**: Staggered feature callouts or metric pills.
- **Bottom Band**: Word-highlighted subtitles with clean vertical clearance.

## 3. Motion Timing & Staggered Entrances
- Entrances: SoftIn (opacity 25%→100%, rise 10px, ~8 frames) for all text and small tiles.
- Left entity stack: Stagger by ~8 frames per brand (0.0s, 0.3s, 0.6s).
- Center hero: Expands or pops at 1.0s.
- Right callouts: Pop in sync with the exact spoken words in narration.
- Connectors grow from source to destination end.
- Light budget: Clean high-key studio white canvas with subtle diffuse drop shadows. Glow only on active hero element.
