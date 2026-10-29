"""Top 5 Video Niche Category / Plugin System for AIVideoStudio.

Each niche plugin defines:
  - Visual style preset & color palette
  - Director storyboard planning rules (how scenes, maps, cartoon sprites, icons, charts, and stock cutouts are planned)
  - Ready-to-run 30s-60s production sample scripts modeled after the reference YouTube channels:
    1. Geopolitics & Map Atlas (MirAtlas60 / GeoGlobeTales / Real GeoJSON Country Borders + Satellite Map)
    2. Vox Documentary Explainer (AEffecto / Vox Archival Paper + Highlighter Sweeps + Photo Cutouts)
    3. Story & Cartoon Explainer (Louisiana Deal / Oversimplified 2D Cartoon Characters + Shaded Relief Map)
    4. Finance & YouTube Growth (Nion Anarchy / DecodingYT Neon-Green Growth Charts + Glass KPI Cards)
    5. Tech & Cloud Architecture (Cloud X Berry / Fireship Crisp SVG Service Tiles + Animated Pipelines)
"""
from __future__ import annotations

_BUILTIN_NICHES: list[dict] = [
    {
        "id": "geopolitics_map",
        "name": "Geopolitics & Real Map Atlas",
        "badge": "MAP + GEOJSON",
        "reference_style": "MirAtlas60 / GeoGlobeTales / Johnny Harris",
        "default_visual_style": "warm-documentary",
        "default_aspect_ratio": "16:9",
        "description": "Real satellite & shaded-relief map tiles, exact GeoJSON country/river polygons (Nepal, India, China, Chile, USA, France), glowing borders, vertical callout pins, and 2D cutouts.",
        "director_rules": (
            "NICHE PLUGIN: GEOPOLITICS & REAL MAP ATLAS.\n"
            "- Every geographic scene MUST use `visual_type: 'map'` and include `map_region` elements with real country/region labels "
            "(e.g. 'Nepal', 'Kathmandu Valley', 'Koshi River Basin', 'India', 'China', 'Chile', 'United States', 'Louisiana', 'France') "
            "and `map_marker` elements for key cities, timezones (e.g. 'UTC+5:45'), or river barrages.\n"
            "- Pair `map_region` with `icon` or `callout` elements for flags, elevation/rainfall metrics, and border callouts.\n"
            "- Use `camera_instructions` with `focus` and `zoom_in` to fly into the highlighted country border and river basin."
        ),
        "sample_title": "Nepal Monsoon Floods & Himalayan Geography (2D Atlas Documentary)",
        "sample_topic": "Why Nepal's steep Himalayan river basins and Kathmandu Valley face extreme monsoon flash floods, mapped across the Bagmati and Sapta Koshi corridors.",
        "sample_script": (
            "Sandwiched between India and China, Nepal rises from flat southern plains to the tallest peaks on Earth in less than two hundred kilometers. "
            "When record late-monsoon cloudbursts strike the Mahabharat range, over three hundred millimeters of rain funnels directly into the bowl-shaped Kathmandu Valley. "
            "Within hours, the Bagmati and Bishnumati rivers surge four meters above danger level, inundating riverside neighborhoods and highways. "
            "Further east, the massive Sapta Koshi basin collects torrential runoff from seven Himalayan tributaries, forcing all fifty-six barrage gates open as helicopter and raft teams race to rescue stranded communities."
        ),
    },
    {
        "id": "vox_documentary",
        "name": "Vox Documentary Explainer",
        "badge": "VOX ARCHIVAL",
        "reference_style": "Vox / AEffecto Editorial Cutout Style",
        "default_visual_style": "light-minimal",
        "default_aspect_ratio": "16:9",
        "description": "Textured vintage archival paper & grid backdrop, yellow highlighter marker sweeps behind serif/mono headlines, white-bordered photo cutouts with drop shadows, and curved arrows.",
        "director_rules": (
            "NICHE PLUGIN: VOX DOCUMENTARY EXPLAINER.\n"
            "- Design scenes like a Vox editorial investigation on textured archival paper.\n"
            "- Use `title_card` and `callout` elements for bold highlighter-swept headlines and dated archival evidence quotes.\n"
            "- Include `map_region`, `chart_bar`, and `icon` elements connected by `arrow` relationships so the renderer draws curved editorial arrows and white-bordered photo cutouts.\n"
            "- Always include specific `asset_requests` queries so real documentary photography is composited in a tilted white-bordered Polaroid/cutout frame."
        ),
        "sample_title": "How Nepal's 15-Minute Timezone & River Geography Shape South Asia (Vox Style)",
        "sample_topic": "A Vox-style visual investigation into why Nepal sits on a unique UTC+5:45 timezone and how its Himalayan topography shapes monsoon hydrology.",
        "sample_script": (
            "Look closely at a map of South Asia and you will notice something unusual about Nepal. "
            "While India runs on UTC plus five thirty and China runs on UTC plus eight, Nepal split the difference in nineteen eighty-six to create its own fifteen-minute offset: UTC plus five forty-five, anchored to Mount Gauri Shankar. "
            "That same extreme Himalayan geography controls the region's water: eighty percent of Nepal's annual rainfall arrives in just three monsoon months, carving deep gorges from Kathmandu to the Koshi plains."
        ),
    },
    {
        "id": "story_cartoon",
        "name": "Story & History Cartoon Explainer",
        "badge": "2D CARTOON + MAP",
        "reference_style": "Louisiana $15M Deal / Oversimplified Style",
        "default_visual_style": "warm-documentary",
        "default_aspect_ratio": "9:16",
        "description": "Real shaded-relief map or illustrated stage + expressive 2D cartoon characters (diplomats, Napoleon, rescue crews, ships, citizens) + territory polygons and action callouts.",
        "director_rules": (
            "NICHE PLUGIN: STORY & HISTORY CARTOON EXPLAINER.\n"
            "- Combine `map_region` territory polygons (e.g. 'United States', 'Louisiana Territory', 'France', 'United Kingdom', 'Nepal') "
            "with expressive 2D character/prop `icon` and `card` elements (e.g. 'Diplomat Ship', 'Napoleon', 'Treaty Scroll', 'Rescue Helicopter', 'Inflatable Raft', 'Citizen').\n"
            "- Use punchy `on_screen_text` banners and `pulse`/`highlight` animations as each character or territory enters the story."
        ),
        "sample_title": "How America Bought Louisiana: Napoleon's $15M Deal",
        "sample_topic": "How Thomas Jefferson's diplomats sailed to France expecting only New Orleans, and walked away with 828,000 square miles of Louisiana Territory from Napoleon for $15 million.",
        "sample_script": (
            "In eighteen oh three, the young United States had a huge problem: France controlled New Orleans and the mouth of the Mississippi River. "
            "President Thomas Jefferson sent diplomats across the Atlantic with a simple mission: offer Napoleon ten million dollars just to buy the port of New Orleans. "
            "But Napoleon needed cash fast for an impending war with Britain, so he shocked the Americans with a counter-offer: take the entire Louisiana Territory for fifteen million dollars. "
            "With one stroke of a pen, America doubled in size for less than four cents an acre."
        ),
    },
    {
        "id": "finance_growth",
        "name": "Finance, Business & YouTube Growth",
        "badge": "NEON CHARTS + KPI",
        "reference_style": "Nion Anarchy / DecodingYT / Financial Analytics",
        "default_visual_style": "dark-neon",
        "default_aspect_ratio": "16:9",
        "description": "Dark carbon dot-grid backdrop, full-canvas glowing neon-green (#00FF44) exponential growth line & bar charts, floating glassmorphic KPI cards (Views ↑ 820K, $15M), and creator/cash cutouts.",
        "director_rules": (
            "NICHE PLUGIN: FINANCE, BUSINESS & YOUTUBE GROWTH.\n"
            "- Every scene should feature quantitative `chart_bar`, `card`, and `callout` elements with explicit numeric `value` props (e.g. 25, 48, 76, 98) and metric labels (e.g. 'Views ↑ 820K', '78.6K ↑ Subscribers', '$15M Revenue', '3.8x ROI').\n"
            "- Use `visual_type: 'chart'` or `visual_type: 'comparison'` so the renderer draws the full-canvas glowing neon-green trajectory line chart and glassmorphic KPI cards."
        ),
        "sample_title": "How Faceless Data Channels Scale to 820K Views in 30 Days",
        "sample_topic": "Breakdown of the retention curve, niche selection, and compounding RPM economics behind high-growth faceless documentary channels in 2026.",
        "sample_script": (
            "Why do some faceless documentary channels explode to eight hundred and twenty thousand views in thirty days while others stall at zero? "
            "First, they target high-RPM niches like geopolitics, cloud architecture, and macro finance where advertisers pay twelve to twenty-five dollars per thousand views. "
            "Second, they engineer the first eight seconds with a visual map or live growth chart that holds seventy-eight percent viewer retention. "
            "By compounding three data-driven uploads a week, subscriber velocity crosses seventy-eight thousand and turns a simple script pipeline into a scalable media asset."
        ),
    },
    {
        "id": "tech_architecture",
        "name": "Tech, Cloud & AI Architecture",
        "badge": "SVG CLOUD TILES",
        "reference_style": "Cloud X Berry / Fireship Systems Style",
        "default_visual_style": "clean-technical",
        "default_aspect_ratio": "16:9",
        "description": "Dark technical grid, real crisp SVG vector service icons inside vibrant rounded tiles (AWS Lambda, S3, EC2, RDS, Route53, Kubernetes, Docker, AI), gradient-underlined headlines, and animated packet flows.",
        "director_rules": (
            "NICHE PLUGIN: TECH, CLOUD & AI ARCHITECTURE.\n"
            "- Use `visual_type: 'architecture'` or `visual_type: 'process_flow'`.\n"
            "- Populate scenes with crisp technical `icon`, `node`, and `card` elements named after real services (e.g. 'Route 53 DNS', 'API Gateway', 'AWS Lambda', 'Amazon S3', 'Amazon RDS', 'Kubernetes Cluster', 'Docker Container', 'IAM Security Shield') connected by `arrow` and `packet` elements.\n"
            "- Animate data packets flowing along routes using `draw` and `flow` actions."
        ),
        "sample_title": "AWS Cloud Architecture Will Finally Make Sense in 45 Seconds",
        "sample_topic": "How Route 53, CloudFront, API Gateway, AWS Lambda, Amazon RDS, and S3 work together in a production serverless cloud architecture.",
        "sample_script": (
            "If AWS feels overwhelming with over two hundred services, you only need six core building blocks to understand ninety percent of cloud architecture. "
            "Every user request starts at Route fifty-three DNS and hits CloudFront at the edge before passing through IAM security and API Gateway. "
            "From there, serverless AWS Lambda functions execute your business logic in milliseconds without managing a single server. "
            "Structured transactions persist in Amazon RDS while static media and backups stream directly into Amazon S3."
        ),
    },
]

# The built-in list above is only a fallback: the source of truth is `<repo>/skills/*/SKILL.md` (see aivs.skills).


def list_niches() -> list[dict]:
    """Skill-backed niche list (re-read when any SKILL.md changes); falls back to the built-in list."""
    from .skills import load_skills
    try:
        skills = load_skills()
    except Exception:
        skills = []
    return [s.as_niche() for s in skills] if skills else list(_BUILTIN_NICHES)


NICHE_CATEGORIES: list[dict] = list_niches()


def get_niche(niche_id: str | None) -> dict:
    items = list_niches()
    for n in items:
        if n["id"] == niche_id:
            return n
    return items[0]


def detect_niche_from_text(text: str, style: str = "") -> str:
    """Automatically infer the best niche/skill: skill `triggers` first, then the legacy keyword rules."""
    from .skills import detect_skill
    try:
        hit = detect_skill(text)
    except Exception:
        hit = None
    return hit or _legacy_detect(text, style)


def _legacy_detect(text: str, style: str = "") -> str:
    """Legacy keyword routing used when no skills directory is available."""
    low = (text or "").lower()
    if any(w in low for w in ("aws", "lambda", "kubernetes", "docker", "microservice", "api gateway", "cloud", "database", "s3", "ec2", "server")):
        return "tech_architecture"
    if any(w in low for w in ("views", "subscriber", "rpm", "profit", "revenue", "stock market", "portfolio", "roi", "channel ideas", "monetiz")):
        return "finance_growth"
    if any(w in low for w in ("napoleon", "louisiana", "jefferson", "empire", "century", "treaty", "king", "war of", "cartoon")):
        return "story_cartoon"
    if style == "light-minimal" or any(w in low for w in ("vox", "archival", "editorial", "timezone", "15 minutes ahead")):
        return "vox_documentary"
    if any(w in low for w in ("nepal", "kathmandu", "koshi", "bagmati", "flood", "monsoon", "himalaya", "india", "china", "chile", "border", "map", "river", "basin", "geography")):
        return "geopolitics_map"
    return "geopolitics_map"
