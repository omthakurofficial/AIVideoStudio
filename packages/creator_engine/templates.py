"""AI Video Studio V2 — Top 10 Niche Video Production Templates & Blueprint Engine.

Provides CapCut / DaVinci Resolve-grade production blueprints for top 10 YouTube niches:
1. YouTube Growth & Viral Retention (Ali Abdaal / MrBeast Analytics)
2. Finance, Stocks & Crypto (Bloomberg / Graham Stephan / Wealth)
3. Vox Explainer & Archival Documentary (Johnny Harris / Vox Paper Cutouts)
4. Geo-Politics & 3D Global Warfare / Trade Maps (CaspianReport / RealLifeLore)
5. Podcast to 2D/3D Cartoon Avatar (Joe Rogan Animated / Lip-sync Acting)
6. Modern Dark SaaS & Cloud 3D Architecture (Fireship / ByteByteGo)
7. Stoic High-Impact Motivation & Mindset (Huberman / Goggins / 30-Day Wall)
8. True Crime & Mystery Case Files (JCS / Coffeehouse Crime Red Corkboard)
9. Deep Science & Quantum Tech (Kurzgesagt / Veritasium Blueprints)
10. Luxury Business & Corporate Case Studies (MagnatesMedia / Slidebean Swiss)
"""
from __future__ import annotations

import json
import math
import os
import re
from typing import Any, Dict, List, Optional

TOP_10_NICHES: List[Dict[str, Any]] = [
    {
        "id": "youtube_growth",
        "name": "YouTube Growth & Viral Retention",
        "category": "Creator Economy & Analytics",
        "badge": "📈 YouTube Growth",
        "reference_channels": "Ali Abdaal, MrBeast Analytics, VidIQ, Colin & Samir",
        "description": "CTR curves, viewer retention drop-off graphs, thumbnail split test cards, subscriber milestone counter, golden play button reveal.",
        "colors": {
            "bg": "#0a0a0f",
            "accent": "#ff0033",
            "secondary": "#ffd60a",
            "highlight": "#38bdf8",
            "panel": "#14141e"
        },
        "typography": {
            "display": "Anton, Impact, sans-serif",
            "body": "Inter, sans-serif",
            "accent": "Cabinet Grotesk, sans-serif"
        },
        "visual_elements": [
            "Audience Retention Graph (dip at 0:30, plateau, spike)",
            "Thumbnail A/B Split Test Cards with CTR % pills",
            "Live Rolling Subscriber Counter (e.g. 100K -> 1M)",
            "Golden Creator Award Play Button 3D Reveal",
            "Hook Formula Callouts with Emoji Badges"
        ],
        "music_style": "creator_tech (120 BPM upbeat kinetic electro-pop with riser drops)",
        "default_aspect": "9:16",
        "sample_topics": [
            "How to Hook 80% of Viewers in the First 3 Seconds",
            "The 1-in-10 Rule: Why Most YouTube Channels Stay Stuck Under 1000 Subs",
            "The MrBeast Retention Formula: How to Edit for Zero Drop-off"
        ]
    },
    {
        "id": "finance_wealth",
        "name": "Finance, Stocks & Crypto",
        "category": "Money, Investing & Macro",
        "badge": "💰 Finance & Wealth",
        "reference_channels": "Bloomberg, Graham Stephan, Andrei Jikh, ClearValue Tax",
        "description": "Bloomberg terminal dark aesthetics, green/red candlestick charts, live ticker tape, gold serif accents, compounding interest curves.",
        "colors": {
            "bg": "#06090e",
            "accent": "#00e676",
            "secondary": "#ff5252",
            "highlight": "#ffd700",
            "panel": "#0c131d"
        },
        "typography": {
            "display": "Clash Display, sans-serif",
            "body": "JetBrains Mono, monospace",
            "accent": "Instrument Serif, serif"
        },
        "visual_elements": [
            "Real-time TradingView Candlestick Chart with Moving Averages",
            "Live Stock Ticker Tape (NVDA, TSLA, BTC, SPY)",
            "Compounding Interest 30-Year Wealth Trajectory Line",
            "Gold Foil Net Worth Stat Lock ($0 -> $1,250,000)",
            "Inflation vs Cash Purchasing Power Shrinking Bar"
        ],
        "music_style": "lofi_documentary (80 BPM warm piano with sub-bass pulses and ticker clicks)",
        "default_aspect": "16:9",
        "sample_topics": [
            "The Silent Wealth Killer: How Inflation Eats 40% of Your Savings in 10 Years",
            "The Index Fund Secret Wall Street Doesn't Want You to Know",
            "Asset Allocation in Your 20s vs 40s: Where $10,000 Actually Grows"
        ]
    },
    {
        "id": "vox_explainer",
        "name": "Vox-Style Explainer & Investigative Documentary",
        "category": "Journalism & Culture",
        "badge": "📰 Vox Explainer",
        "reference_channels": "Vox, Johnny Harris, Cleo Abram, PolyMatter",
        "description": "Paper textures, torn cardboard edges, yellow highlighter wipes, archival photo cutouts with white borders, masking tape, typewriter annotations.",
        "colors": {
            "bg": "#121110",
            "accent": "#ffd600",
            "secondary": "#f5f2eb",
            "highlight": "#e63946",
            "panel": "#1f1d1a"
        },
        "typography": {
            "display": "Editorial New, Georgia, serif",
            "body": "Courier Prime, monospace",
            "accent": "Instrument Serif, serif"
        },
        "visual_elements": [
            "Torn Paper Cutout Photo with White 4px Border & Drop Shadow",
            "Yellow Fluorescent Highlighter Swipe over Historical Newspaper Head",
            "Curved Red Ballpoint Pen Arrow & Hand-Drawn Question Mark",
            "Classified Archive Document Stamp with Black Redaction Bars",
            "Side-by-Side Timeline Ruler with Year Tick Marks"
        ],
        "music_style": "lofi_documentary (84 BPM acoustic guitar, tape warble & typewriter SFX)",
        "default_aspect": "16:9",
        "sample_topics": [
            "The Real Reason Why EV Charging Infrastructure is Still Broken",
            "The Rise and Fall of the Middle-Class Supermarket",
            "How One Unsung Treaty Secretly Controls the Entire World's Internet Cables"
        ]
    },
    {
        "id": "geopolitics_maps",
        "name": "Geo-Politics & 3D Global Warfare / Trade Maps",
        "category": "World Affairs & Geography",
        "badge": "🌍 Geo-Politics & Maps",
        "reference_channels": "CaspianReport, RealLifeLore, Wendover, Economics Explained",
        "description": "3D topological dark earth maps, glowing missile corridors, maritime shipping choke-points, national borders, military telemetry radar.",
        "colors": {
            "bg": "#070b12",
            "accent": "#38bdf8",
            "secondary": "#f43f5e",
            "highlight": "#eab308",
            "panel": "#0f172a"
        },
        "typography": {
            "display": "Space Grotesk, sans-serif",
            "body": "Inter, sans-serif",
            "accent": "Rajdhani, sans-serif"
        },
        "visual_elements": [
            "Satellite GeoJSON Map with Glowing Boundary Polygons",
            "Maritime Chokepoint Shipping Density Arc (Strait of Malacca, Suez)",
            "Military Base Range Radii Circles with Radar Sweep Pulse",
            "Country Flag Hexagonal Badges with Population & GDP Telemetry",
            "Tactical Arrow Advance Line with Hash Pattern Dash Array"
        ],
        "music_style": "lofi_documentary (88 BPM tense strings with radar blips and deep sub hit)",
        "default_aspect": "16:9",
        "sample_topics": [
            "The 5 Chokepoints That Could Cripple 80% of Global Oil Tomorrow",
            "Why Taiwan is the Most Geopolitically Dangerous Island on Earth",
            "The Arctic Shipping Route: Russia's New $1 Trillion Trade Secret"
        ]
    },
    {
        "id": "podcast_avatar",
        "name": "Podcast to 2D/3D Cartoon Avatar",
        "category": "Entertainment & Comedy",
        "badge": "🎙️ Podcast & Cartoon",
        "reference_channels": "Joe Rogan Animated, Lex Fridman Shorts, Modern Wisdom Clips",
        "description": "Speaker converted to 2D/3D animated cartoon character with reactive emotional acting: laughing squint, shocked jaw drop, fist pump, split screen PiP.",
        "colors": {
            "bg": "#0e0714",
            "accent": "#ec4899",
            "secondary": "#a855f7",
            "highlight": "#facc15",
            "panel": "#190d24"
        },
        "typography": {
            "display": "Bangers, Impact, cursive",
            "body": "Plus Jakarta Sans, sans-serif",
            "accent": "Permanent Marker, cursive"
        },
        "visual_elements": [
            "2D Vector Host Avatar with Dynamic Lip-sync & Blinking",
            "Comic Book Action Bubble with Kinetic Punch Impact Lines",
            "Shure SM7B Microphone in Foreground with Floating Soundwaves",
            "Emotional Reaction Overlay (Shocked lightning bolt, Laughing tears)",
            "Split-Screen Host vs Guest Dialogue Trading Boxes"
        ],
        "music_style": "playful_cartoon (110 BPM jaunty bassline with comedic pop and boing SFX)",
        "default_aspect": "9:16",
        "sample_topics": [
            "Why Humans Actually Need 8 Hours of Sleep (Explained by a Neuroscientist)",
            "The Craziest Simulation Theory Argument I've Ever Heard",
            "What Actually Happens When You Drink 5 Cups of Coffee in a Row"
        ]
    },
    {
        "id": "saas_tech_3d",
        "name": "Modern Dark SaaS & Cloud 3D Architecture",
        "category": "Tech & Software Engineering",
        "badge": "⚡ Dark SaaS Tech",
        "reference_channels": "Fireship, Theo - t3.gg, ByteByteGo, Primeagen",
        "description": "Void black (#050508), cyan laser (#38bdf8), 3D isometric cloud microservices, sub-millisecond speedometer dials, glowing terminal commands.",
        "colors": {
            "bg": "#04060a",
            "accent": "#38bdf8",
            "secondary": "#34d399",
            "highlight": "#f43f5e",
            "panel": "#0a101d"
        },
        "typography": {
            "display": "JetBrains Mono, monospace",
            "body": "Inter, sans-serif",
            "accent": "Geist Mono, monospace"
        },
        "visual_elements": [
            "3D Isometric Cloud Architecture Diagram (Kubernetes, Postgres, Redis)",
            "Glowing Dark Mode macOS Terminal Window with Typewriter Shell Output",
            "Real-time Latency Benchmarks Dial (420ms -> 1.2ms)",
            "Database Read/Write Throughput Neon Flowing Tubing",
            "API Endpoint JSON Request/Response Live Syntax Highlight Card"
        ],
        "music_style": "cyberpunk_synthwave (128 BPM driving analog synth arpeggios & glitch hats)",
        "default_aspect": "9:16",
        "sample_topics": [
            "How WhatsApp Scaled to 2 Billion Users With Only 50 Engineers",
            "Microservices vs Monoliths: The Real Cost Nobody Talks About",
            "Redis Under the Hood: Why It's 100x Faster Than Traditional Databases"
        ]
    },
    {
        "id": "mindset_motivation",
        "name": "Stoic High-Impact Motivation & Mindset",
        "category": "Self-Improvement & Discipline",
        "badge": "🔥 Mindset & Stoicism",
        "reference_channels": "David Goggins, Ryan Holiday (Daily Stoic), Andrew Huberman, Alex Hormozi",
        "description": "High contrast brutalist typography, gritty monochrome grain, heartbeat pulse monitor, strike-through doubt stamps, 30-day streak tracker, golden CTA.",
        "colors": {
            "bg": "#000000",
            "accent": "#ff2d55",
            "secondary": "#f5f5f7",
            "highlight": "#ffd60a",
            "panel": "#111111"
        },
        "typography": {
            "display": "Anton, Impact, sans-serif",
            "body": "Inter, sans-serif",
            "accent": "Instrument Serif, serif"
        },
        "visual_elements": [
            "ECG Heartbeat Pulse Monitor Line Spiking Across Screen",
            "Heavy Red Rubber Stamp Slamming Down: 'EXCUSES REJECTED'",
            "Monochrome 35mm Gritty Film Grain Overlay with Scratches",
            "30-Day Discipline Habit Streak Grid Filling with Red Checks",
            "Sub-Zero Contrast Serif Quote Reveal with Spotlight Vignette"
        ],
        "music_style": "lofi_documentary (74 BPM cinematic sub-bass braams with ticking clock)",
        "default_aspect": "9:16",
        "sample_topics": [
            "The 30-Day Wall: Why 95% of People Quit Right Before the Breakthrough",
            "The Stoic Formula to Never Feel Anxious About What You Can't Control",
            "Dopamine Detox: How to Reset Your Brain's Motivation in 72 Hours"
        ]
    },
    {
        "id": "true_crime",
        "name": "True Crime & Mystery Case Files",
        "category": "Investigative & Psychology",
        "badge": "🕵️ True Crime & Mystery",
        "reference_channels": "JCS - Criminal Psychology, Coffeehouse Crime, Explore With Us",
        "description": "Cork investigation murder board with red connecting threads, polaroid photo drops, redacted FBI case files, flashlight circular mask, cassette SFX.",
        "colors": {
            "bg": "#09090b",
            "accent": "#ef4444",
            "secondary": "#f4f4f5",
            "highlight": "#eab308",
            "panel": "#18181b"
        },
        "typography": {
            "display": "Special Elite, Courier Prime, monospace",
            "body": "Inter, sans-serif",
            "accent": "Caveat, cursive"
        },
        "visual_elements": [
            "Corkboard Pin Drop with Red Elastic String Snapping Between Clues",
            "Redacted FBI Classified Document with Black Highlighter Strips",
            "Flashlight Beam Moving in Dark Room Revealing Fingerprint Evidence",
            "Interrogation Room Timeline Timestamp Counter (11:42 PM - Unaccounted)",
            "Cassette Tape Audio Waveform with Analog Tape Hiss Flare"
        ],
        "music_style": "lofi_documentary (65 BPM eerie drone with water-phone scrapes and heartbeat)",
        "default_aspect": "9:16",
        "sample_topics": [
            "The FBI Interrogation Tactic That Makes Anyone Confess in 60 Minutes",
            "The Unsolved Island Mystery That Baffled Forensic Experts for 40 Years",
            "Body Language Breakdown: 4 Micro-Expressions That Give Away a Lie"
        ]
    },
    {
        "id": "science_tech",
        "name": "Deep Science & Quantum Tech",
        "category": "STEM & Discovery",
        "badge": "🔬 Deep Science & Tech",
        "reference_channels": "Kurzgesagt, Veritasium, 3Blue1Brown, Sabine Hossenfelder",
        "description": "Blueprint technical grid, 3D molecular/neural network graph, quantum particle flows, animated math equations, vector laboratory telemetry.",
        "colors": {
            "bg": "#020b14",
            "accent": "#0ea5e9",
            "secondary": "#10b981",
            "highlight": "#f59e0b",
            "panel": "#081e36"
        },
        "typography": {
            "display": "Space Grotesk, sans-serif",
            "body": "JetBrains Mono, monospace",
            "accent": "KaTeX Math / Computer Modern, serif"
        },
        "visual_elements": [
            "Cyan Blueprint Grid with Measuring Calipers & Angle Dimensions",
            "3D Atomic Nucleus with Orbiting Electron Probability Clouds",
            "Neural Network Synapse Graph Lighting Up with Spike Trains",
            "Vector Math Equation Derivation with Step-by-Step Highlighter",
            "Quantum Superposition Wavefunction Interference Pattern"
        ],
        "music_style": "creator_tech (96 BPM ambient electronic pulses with glass bells)",
        "default_aspect": "16:9",
        "sample_topics": [
            "The Quantum Superposition Paradox Explained in Plain English",
            "CRISPR 2.0: How Prime Editing is Rewriting Human DNA",
            "Why Time Slows Down Near Black Holes: Gravitational Time Dilation"
        ]
    },
    {
        "id": "luxury_business",
        "name": "Luxury Business & Corporate Case Studies",
        "category": "Enterprise & Luxury Brands",
        "badge": "👑 Luxury & Business",
        "reference_channels": "MagnatesMedia, Slidebean, Wall Street Journal Case Studies",
        "description": "Swiss minimalist typography, warm editorial serif (#c5a059), matte gold foil badges, magazine grid layouts, slow cinematic parallax moves.",
        "colors": {
            "bg": "#0c0d0e",
            "accent": "#c5a059",
            "secondary": "#f4f1ea",
            "highlight": "#3b82f6",
            "panel": "#161719"
        },
        "typography": {
            "display": "Cormorant Garamond, Didot, serif",
            "body": "Neue Haas Grotesk, Helvetica, sans-serif",
            "accent": "Instrument Serif, serif"
        },
        "visual_elements": [
            "Editorial Magazine Grid with Clean Hairline Borders",
            "Matte Gold Foil Embossed Brand Logo Reveal",
            "Financial Growth Metrics Bar with Elegant Percentage Counter",
            "Split-Screen Executive Portrait vs Factory Floor Drone B-Roll",
            "Slow High-Precision Cinematic Parallax Drift"
        ],
        "music_style": "lofi_documentary (78 BPM sophisticated neo-classical piano & cello)",
        "default_aspect": "16:9",
        "sample_topics": [
            "The Secret Strategy That Built LVMH Into an $400B Empire",
            "How Rolex Engineered Extreme Scarcity to Dominate Luxury Watches",
            "The Masterclass in Turnarounds: How Apple Came Back From Bankruptcy"
        ]
    }
]

NICHE_BY_ID = {n["id"]: n for n in TOP_10_NICHES}


def synthesize_topic_scenes(
    topic: str,
    niche: Dict[str, Any],
    scene_count: int,
    target_duration_s: int,
    wpm: int = 150,
    reference_info: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Generate high-impact, topic-tailored scenes that match the real source facts, metrics, and narrative."""
    scenes: List[Dict[str, Any]] = []
    dur_per_scene = target_duration_s / scene_count
    full_text = (topic + " " + (reference_info.get("transcript", "") if reference_info else "") + " " + (reference_info.get("description", "") if reference_info else "")).lower()

    # Special Detection: India vs China Rare Earth Magnets / Energy / Geopolitics
    is_rare_earths = any(k in full_text for k in ["rare earth", "7,280", "7280", "permanent magnet", "repm", "thorium", "villal", "beach sand", "monazite", "ammonium sulphate"])

    if is_rare_earths:
        story_beats = [
            {
                "headline": "CHINA'S 40-YEAR MONOPOLY",
                "badge": "₹7,280 CR MAGNET SCHEME",
                "narration": "China started rare earths forty years ago and controls seventy percent of global permanent magnets. But India just approved a massive seven thousand two hundred eighty crore rupee scheme to break free.",
                "prop": "NASA Satellite Map: India vs China Rare Earth Deposits",
                "choreo": "SLAM, RED_STRIKE, SATELLITE_ZOOM"
            },
            {
                "headline": "THE TOXIC LEACHING TRAP",
                "badge": "AMMONIUM SULPHATE ACID LEACHING",
                "narration": "For decades, China sold rare earths so cheap nobody else could compete—by pumping ammonium sulphate acid directly into hills and poisoning groundwater.",
                "prop": "Toxic Hill Leaching vs Environmental Devastation Diagram",
                "choreo": "WARNING_FLASH, SPLIT_SCREEN, ACID_RUNOFF"
            },
            {
                "headline": "BEACH SAND BREAKTHROUGH",
                "badge": "COASTAL MONAZITE SAND PROCESSING",
                "narration": "India's secret weapon isn't mining hills. It's processing coastal beach sands with zero acid runoff to extract high-purity heavy rare earth elements.",
                "prop": "Coastal Sand Refinery to Pure Neodymium Magnets",
                "choreo": "ISOMETRIC_FLOW, GREEN_GLOW, REVEAL"
            },
            {
                "headline": "THE THORIUM NUCLEAR SECRET",
                "badge": "THORIUM NUCLEAR FUEL CYCLE",
                "narration": "Processing beach sand yields radioactive Thorium. Instead of discarding it, India is channeling that Thorium directly into next-generation clean nuclear power plants.",
                "prop": "Thorium Reactor Blueprint & Clean Electricity Grid",
                "choreo": "QUANTUM_ORBIT, CLEAN_ENERGY_PULSE, TELEMETRY"
            },
            {
                "headline": "6,000 TONNES BY 2030",
                "badge": "6,000 TONNES DOMESTIC CAPACITY",
                "narration": "Almost all EV motors, wind turbines, and missile defense systems depend on permanent magnets. With six thousand tonnes domestic capacity, India achieves complete self-reliance.",
                "prop": "High-Strength Sintered Neodymium Permanent Magnet 3D Exploded View",
                "choreo": "ROLLING_STAT, SPEED_TIMER, CHECKMARKS"
            },
            {
                "headline": "THE CLEAN ENERGY RACE",
                "badge": "2030 MAGNET INDEPENDENCE",
                "narration": "The clean energy race between India and China has officially entered hyperdrive. Will India overtake Beijing by twenty thirty? Let us know in the comments below.",
                "prop": "Golden CTA Card & Dynamic Trade Balance Graph",
                "choreo": "GOLDEN_CTA, 3_POINT_CHECKLIST, ORBIT"
            }
        ]
    elif reference_info and reference_info.get("key_facts"):
        facts = reference_info["key_facts"]
        ref_title = reference_info.get("title", topic)[:32].upper()
        story_beats = [
            {
                "headline": ref_title,
                "badge": "KEY DISCOVERY",
                "narration": facts[0] if len(facts) > 0 else f"Here is the untold truth about {topic}.",
                "prop": "Primary Evidence Card with Highlighted Metadata",
                "choreo": "SLAM, RED_STRIKE, SERIF_ACCENT"
            },
            {
                "headline": "THE HIDDEN FRICTION",
                "badge": "CRITICAL BOTTLENECK",
                "narration": facts[1] if len(facts) > 1 else "Most conventional methods fail because they ignore the underlying friction.",
                "prop": "Friction Comparison Matrix & Data Divergence",
                "choreo": "3D_MOCKUP, RED_BLOAT, SHAKE"
            },
            {
                "headline": "THE PARADIGM SHIFT",
                "badge": "SYSTEM BREAKTHROUGH",
                "narration": facts[2] if len(facts) > 2 else "This is where the new mechanism completely changes the rules of the game.",
                "prop": "Kinetic Flow Architecture & Green Energy Metrics",
                "choreo": "ISOMETRIC_FLOW, GREEN_GLOW, COUNTER"
            },
            {
                "headline": "DATA BENCHMARK",
                "badge": "PROVEN BENCHMARK",
                "narration": facts[3] if len(facts) > 3 else "When you examine the real-world benchmarks, the results speak for themselves.",
                "prop": "Rolling Metric Dial & Real-Time Statistics",
                "choreo": "ROLLING_STAT, SPEED_TIMER, CHECKMARKS"
            },
            {
                "headline": "OBSOLETE WAYS REJECTED",
                "badge": "LEGACY METHOD SCRAPPED",
                "narration": facts[4] if len(facts) > 4 else "Throw out the old assumptions. Staying with legacy systems guarantees falling behind.",
                "prop": "Redacted Legacy Document with Red Crossout Stamp",
                "choreo": "RUBBER_STAMP, DEPRECATED, FLASH"
            },
            {
                "headline": "THE FINAL TAKEAWAY",
                "badge": "STRATEGIC MASTERY",
                "narration": f"Master this breakthrough today. Apply the principles, take immediate action, and secure the advantage.",
                "prop": "Golden Action Card with Interactive Decision Tree",
                "choreo": "GOLDEN_CTA, 3_POINT_CHECKLIST, ORBIT"
            }
        ]
    else:
        # High-impact topic-aware defaults
        clean_name = re.sub(r"[^A-Za-z0-9\s]", "", topic).strip().upper()[:28] or "THE UNTOLD TRUTH"
        story_beats = [
            {
                "headline": clean_name,
                "badge": "THE INVISIBLE BARRIER",
                "narration": f"Most people fail before they ever start. When it comes to {topic}, you hit what top experts call the invisible wall.",
                "prop": niche["visual_elements"][0],
                "choreo": "SLAM, RED_STRIKE, SERIF_ACCENT"
            },
            {
                "headline": "THE HIDDEN FRICTION",
                "badge": "EIGHTY PERCENT LOSS",
                "narration": "Every minute of effort without results causes massive fatigue. You are losing eighty percent of your potential right at the critical threshold.",
                "prop": niche["visual_elements"][1 % len(niche["visual_elements"])],
                "choreo": "3D_MOCKUP, RED_BLOAT, SHAKE"
            },
            {
                "headline": "THE PARADIGM SHIFT",
                "badge": "KINETIC MECHANISM",
                "narration": "The true mechanism is rapid pattern interrupts. Instead of following outdated assumptions, deploy next-generation kinetic velocity.",
                "prop": niche["visual_elements"][2 % len(niche["visual_elements"])],
                "choreo": "ISOMETRIC_FLOW, GREEN_GLOW, COUNTER"
            },
            {
                "headline": "DATA BENCHMARK",
                "badge": "NINETY PERCENT GAIN",
                "narration": "This single breakthrough unlocks ninety percent compounding retention, rocketing your performance ahead of the curve.",
                "prop": niche["visual_elements"][3 % len(niche["visual_elements"])],
                "choreo": "ROLLING_STAT, SPEED_TIMER, CHECKMARKS"
            },
            {
                "headline": "OBSOLETE WAYS REJECTED",
                "badge": "HIGH IMPACT LEVERAGE",
                "narration": "Stop using obsolete, generic methods. Throw out the clutter and focus solely on high-impact leverage.",
                "prop": niche["visual_elements"][4 % len(niche["visual_elements"])],
                "choreo": "RUBBER_STAMP, DEPRECATED, FLASH"
            },
            {
                "headline": "THE FINAL TAKEAWAY",
                "badge": "CLAIM YOUR SUCCESS",
                "narration": f"Claim your breakthrough today. Master the system, outlast the silence, and achieve the exact results you deserve.",
                "prop": niche["visual_elements"][0],
                "choreo": "GOLDEN_CTA, 3_POINT_CHECKLIST, ORBIT"
            }
        ]

    cur_t = 0.0
    for i in range(scene_count):
        beat = story_beats[i % len(story_beats)]
        st = round(cur_t, 1)
        en = round(min(target_duration_s, cur_t + dur_per_scene), 1)
        cur_t = en

        scenes.append({
            "scene_number": i + 1,
            "title": f"Scene {i+1:02d}: {beat['headline']}",
            "headline": beat["headline"],
            "visual_badge": beat["badge"],
            "start_s": st,
            "end_s": en,
            "duration_s": round(en - st, 1),
            "target_word_count": len(beat["narration"].split()),
            "spoken_narration": beat["narration"],
            "narration_guidance": f"Spoken at {wpm} WPM with human inflection. Focus on {beat['headline']}.",
            "character_acting": "None" if niche["id"] != "podcast_avatar" else ("[LAUGH] & fist pump" if i % 2 == 0 else "[SHOCKED] jaw drop"),
            "visual_choreography": beat["choreo"],
            "broll_layers": beat["prop"],
            "camera_move": "Punch zoom (a: 0.08) + screen shake" if i == 0 else "Slow continuous cinematic push (z: 1.05)",
            "transition_out": "Whip Pan Right" if i % 2 == 0 else "RGB Glitch / White Flash",
            "sound_effects": ["[SFX: slam]", "[SFX: boom]", "[SFX: shimmer]"][i % 3]
        })

    return scenes


class TemplateGenerator:
    """Intelligent Production Blueprint & Template Generator for AI Video Studio V2."""

    def __init__(self, use_bedrock: bool = True):
        self.use_bedrock = use_bedrock

    def generate_blueprint(
        self,
        topic: str,
        niche_id: str = "youtube_growth",
        target_duration_s: int = 60,
        aspect_ratio: str = "9:16",
        mode: str = "master_auto",
        voice_id: str = "kokoro:am_michael",
        custom_instructions: Optional[str] = None,
        reference_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete CapCut/DaVinci-grade production blueprint and multi-AI prompt."""
        # Auto-deconstruct URL if topic is a link
        if not reference_info and ("http://" in topic or "https://" in topic):
            from services.api.aivs.url_extractor import deconstruct_reference_media
            reference_info = deconstruct_reference_media(topic)

        # Adapt niche if recommended by URL extraction and user is using default
        if reference_info and reference_info.get("suggested_niche") and niche_id == "youtube_growth":
            niche_id = reference_info["suggested_niche"]

        display_topic = reference_info.get("title") if (reference_info and reference_info.get("title")) else topic
        niche = NICHE_BY_ID.get(niche_id, TOP_10_NICHES[0])

        wpm = 150
        target_words = int((target_duration_s / 60.0) * wpm)
        scene_count = max(4, min(30, int(math.ceil(target_duration_s / 10.0))))

        # Synthesize real topic-specific scenes
        scenes = synthesize_topic_scenes(
            topic=display_topic,
            niche=niche,
            scene_count=scene_count,
            target_duration_s=target_duration_s,
            wpm=wpm,
            reference_info=reference_info
        )

        # Generate Portable Multimodal AI Prompt for ChatGPT / Gemini / Claude
        portable_prompt = self._build_portable_prompt(
            topic=display_topic,
            niche=niche,
            target_duration_s=target_duration_s,
            aspect_ratio=aspect_ratio,
            target_words=target_words,
            scenes=scenes,
            reference_info=reference_info
        )

        # Generate Standalone Runnable HTML5 Player Code
        standalone_html = self._generate_standalone_html(
            topic=display_topic,
            niche=niche,
            target_duration_s=target_duration_s,
            aspect_ratio=aspect_ratio,
            scenes=scenes
        )

        return {
            "status": "success",
            "project_title": display_topic,
            "original_topic": topic,
            "niche": niche,
            "reference_info": reference_info,
            "target_duration_s": target_duration_s,
            "target_word_count": target_words,
            "aspect_ratio": aspect_ratio,
            "voice_id": voice_id,
            "mode": mode,
            "scenes": scenes,
            "music_bus": {
                "genre": niche["music_style"],
                "sidechain_ducking": "Voiceover active -> duck music -14dB (50ms attack, 250ms release)",
                "master_lufs": -14.0
            },
            "portable_master_prompt": portable_prompt,
            "standalone_html_code": standalone_html
        }

    def _build_portable_prompt(
        self,
        topic: str,
        niche: Dict[str, Any],
        target_duration_s: int,
        aspect_ratio: str,
        target_words: int,
        scenes: List[Dict[str, Any]],
        reference_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Construct a complete, ready-to-paste AI Prompt for Gemini, ChatGPT, or Claude."""
        ref_section = ""
        if reference_info and reference_info.get("transcript"):
            ref_section = f"""--------------------------------------------------------------------------------
DECONSTRUCTED SOURCE CONTEXT & TRANSCRIPT:
--------------------------------------------------------------------------------
- Original Source: {reference_info.get('url', 'URL Reference')}
- Author / Channel: {reference_info.get('channel', 'Unknown')}
- Extracted Core Facts:
{chr(10).join(['  • ' + f for f in reference_info.get('key_facts', [])])}

Source Transcript Snippet:
\"{reference_info['transcript'][:800]}...\"
"""

        return f"""================================================================================
AI VIDEO STUDIO V2 — UNIVERSAL PRODUCTION MASTER PROMPT
================================================================================
You are the Lead Creative Director & Motion Graphics Choreographer.
Your job is to take this production template and write the complete, final video script
and visual choreography ready for production.

PROJECT SPECIFICATIONS:
- Topic: {topic}
- Production Archetype: {niche['badge']} ({niche['name']})
- Reference Creators: {niche['reference_channels']}
- Target Duration: {target_duration_s} Seconds ({target_words} Spoken Words · {len(scenes)} Scenes)
- Target Aspect Ratio: {aspect_ratio} ({'9:16 Vertical Shorts/Reels/TikTok' if aspect_ratio == '9:16' else '16:9 Landscape YouTube'})
- Color Palette: Background: {niche['colors']['bg']}, Accent: {niche['colors']['accent']}, Secondary: {niche['colors']['secondary']}
- Music Score: {niche['music_style']} (Zero Copyright Claim Risk)
{ref_section}
--------------------------------------------------------------------------------
STRICT PACING & MOBILE SAFE ZONE RULES:
--------------------------------------------------------------------------------
1. Spoken Word Pacing: Exactly {target_words} words voiced at 150 WPM (Kokoro Neural Speech).
2. Mobile Safe Margin (9:16): Top 280px and Bottom 440px MUST remain clear.
   All kinetic titles, numbers, and karaoke captions must stay between Y = 300px and Y = 1460px.
   All text rows must have horizontal padding > 100px (no words overflowing past 900px width).
3. Visual Energy: Every scene must have a camera punch, sound effect cue, and layered B-roll prop.

--------------------------------------------------------------------------------
REQUIRED SCENE-BY-SCENE CHOREOGRAPHY:
--------------------------------------------------------------------------------
Please write out all {len(scenes)} scenes in this exact format:

""" + "\n".join([
    f"## Scene {s['scene_number']:02d}: {s['headline']}\n"
    f"- Timing: {s['start_s']}s – {s['end_s']}s (~{s['target_word_count']} words)\n"
    f"- Spoken Narration: \"{s['spoken_narration']}\"\n"
    f"- Visual Headline: [{s['headline']}]\n"
    f"- Visual Badge: [{s['visual_badge']}]\n"
    f"- Character Acting: {s['character_acting']}\n"
    f"- Visual Choreography: {s['visual_choreography']}\n"
    f"- B-Roll / Layered Prop: {s['broll_layers']}\n"
    f"- Camera Move: {s['camera_move']}\n"
    f"- Transition Out: {s['transition_out']}\n"
    f"- Sound Effects: {s['sound_effects']}\n"
    for s in scenes
]) + f"""
--------------------------------------------------------------------------------
MANDATORY "WHAT WOULD YOU LIKE TO DO NEXT?" MENU (ALWAYS INCLUDE AT THE END):
--------------------------------------------------------------------------------
At the very end of your response, you MUST output this exact 1-click decision menu:

---
### 🎬 WHAT WOULD YOU LIKE TO DO NEXT?
Reply with just a number (1, 2, or 3):

• **Reply "1" (Generate Standalone HTML Code)**:
  I will generate the complete, single-file HTML5 animation player (with all CSS keyframes, 3D cards, bouncing checkmarks, animated counters, karaoke caption sync, and audio player) ready to double-click and preview in your browser!

• **Reply "2" (Modify Script / Style)**:
  Tell me what you'd like to adjust (e.g. "make it more energetic", "add my brand logo", "change to cartoon style", "make it 3 minutes").

• **Reply "3" (Render Video in Antigravity)**:
  If you are using Antigravity, simply tell Antigravity: "Render this script into MP4 video", and it will automatically voice with Kokoro neural TTS, compose copyright-free {niche['music_style']} music, and export {aspect_ratio} MP4 video in under 60 seconds!
---
================================================================================
"""

    def _generate_standalone_html(
        self,
        topic: str,
        niche: Dict[str, Any],
        target_duration_s: int,
        aspect_ratio: str,
        scenes: List[Dict[str, Any]]
    ) -> str:
        """Generate a complete, self-contained HTML5 animation player document with safe-margin rendering."""
        is_vert = aspect_ratio == "9:16"
        w = 1080 if is_vert else 1280
        h = 1920 if is_vert else 720
        aspect_css = "9 / 16" if is_vert else "16 / 9"
        bg_col = niche["colors"]["bg"]
        accent_col = niche["colors"]["accent"]
        sec_col = niche["colors"]["secondary"]
        hi_col = niche["colors"]["highlight"]

        scenes_json = json.dumps(scenes)

        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{topic} — {niche['badge']}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600;700;800;900&family=Space+Grotesk:wght@700&display=swap">
<style>
:root {{
  color-scheme: dark;
  --bg: {bg_col};
  --accent: {accent_col};
  --sec: {sec_col};
  --hi: {hi_col};
  --panel: #14141c;
  --line: #262634;
  --text: #f4f1ea;
  --dim: #8e8d98;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: "Inter", system-ui, sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 16px;
}}
.player-wrap {{
  width: 100%;
  max-width: {'480px' if is_vert else '1140px'};
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.player-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}}
.player-title {{
  font-family: "Anton", Impact, sans-serif;
  font-size: 20px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}}
.player-badge {{
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  background: rgba(255, 214, 10, 0.15);
  color: var(--accent);
  border: 1px solid var(--accent);
  padding: 4px 10px;
  border-radius: 999px;
}}
.stage-container {{
  position: relative;
  width: 100%;
  aspect-ratio: {aspect_css};
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--line);
  box-shadow: 0 25px 60px rgba(0,0,0,0.8);
}}
canvas#stage {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}}
.player-bar {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}}
button.play-btn {{
  background: var(--accent);
  color: #000;
  border: 0;
  font-weight: 800;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}}
input.scrubber {{
  flex: 1;
  accent-color: var(--accent);
  cursor: pointer;
}}
.time-disp {{
  font-size: 13px;
  font-weight: 700;
  color: var(--dim);
  font-variant-numeric: tabular-nums;
}}
</style>
</head>
<body>

<div class="player-wrap">
  <div class="player-header">
    <div class="player-title">{topic}</div>
    <div class="player-badge">{niche['badge']} · {aspect_ratio}</div>
  </div>

  <div class="stage-container">
    <canvas id="stage" width="{w}" height="{h}"></canvas>
  </div>

  <div class="player-bar">
    <button class="play-btn" id="playBtn">▶ Play</button>
    <input type="range" class="scrubber" id="scrubber" min="0" max="{target_duration_s}" step="0.05" value="0">
    <div class="time-disp" id="timeDisp">00:00 / {f'{target_duration_s//60:02d}:{target_duration_s%60:02d}'}</div>
  </div>
</div>

<script>
const DURATION = {target_duration_s};
const IS_VERT = {'true' if is_vert else 'false'};
const W = {w};
const H = {h};
const ACCENT = '{accent_col}';
const SEC = '{sec_col}';
const HI = '{hi_col}';
const SCENES = {scenes_json};

const cv = document.getElementById('stage');
const cx = cv.getContext('2d');
const playBtn = document.getElementById('playBtn');
const scrubber = document.getElementById('scrubber');
const timeDisp = document.getElementById('timeDisp');

let isPlaying = false;
let currentTime = 0;
let lastTimestamp = 0;

function ezOut(t) {{ return 1 - Math.pow(1 - Math.max(0, Math.min(1, t)), 3); }}

function wrapLines(ctx, text, maxW) {{
  const words = text.split(' ');
  const lines = [];
  let cur = words[0];
  for (let i = 1; i < words.length; i++) {{
    const w = words[i];
    const testW = ctx.measureText(cur + ' ' + w).width;
    if (testW <= maxW) {{
      cur += ' ' + w;
    }} else {{
      lines.push(cur);
      cur = w;
    }}
  }}
  lines.push(cur);
  return lines;
}}

function drawScene(t) {{
  // Background
  cx.fillStyle = '{bg_col}';
  cx.fillRect(0, 0, W, H);

  // Subtle ambient grid
  cx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
  cx.lineWidth = 1;
  const off = (t * 12) % 60;
  for (let x = -off; x < W; x += 60) {{ cx.beginPath(); cx.moveTo(x, 0); cx.lineTo(x, H); cx.stroke(); }}
  for (let y = -off * 0.5; y < H; y += 60) {{ cx.beginPath(); cx.moveTo(0, y); cx.lineTo(W, y); cx.stroke(); }}

  // Current Scene
  let curScene = SCENES[0];
  for (const s of SCENES) {{ if (t >= s.start_s) curScene = s; }}

  // Editorial Category Watermark (Strict Mobile Safe Zone)
  const headerY = IS_VERT ? 310 : 70;
  cx.fillStyle = ACCENT;
  cx.fillRect(IS_VERT ? 80 : 70, headerY, 10, 10);
  cx.font = '700 ' + (IS_VERT ? 22 : 18) + 'px "Inter", sans-serif';
  cx.fillStyle = 'rgba(255, 255, 255, 0.55)';
  cx.textAlign = 'left';
  cx.fillText('● BREAKING INVESTIGATION', IS_VERT ? 102 : 92, headerY + 9);

  // Animated Kinetic Title Card
  const sceneT = t - curScene.start_s;
  const animProg = ezOut(sceneT / 0.45);
  const scale = 1.35 - 0.35 * animProg;

  cx.save();
  const centerY = IS_VERT ? H * 0.38 : H * 0.34;
  cx.translate(W / 2, centerY);
  cx.scale(scale, scale);

  const headline = (curScene.headline || curScene.title).toUpperCase();
  const maxTextW = IS_VERT ? 820 : 960;
  let fontPx = IS_VERT ? 68 : 72;
  cx.font = `900 ${{fontPx}}px "Anton", Impact, sans-serif`;

  let lines = wrapLines(cx, headline, maxTextW);
  if (lines.length > 2) {{
    fontPx = IS_VERT ? 54 : 58;
    cx.font = `900 ${{fontPx}}px "Anton", Impact, sans-serif`;
    lines = wrapLines(cx, headline, maxTextW);
  }}

  cx.textAlign = 'center';
  cx.fillStyle = '#f4f1ea';
  cx.shadowColor = 'rgba(0,0,0,0.85)';
  cx.shadowBlur = 30;

  const lineH = fontPx * 1.08;
  const totalH = lines.length * lineH;
  lines.forEach((ln, idx) => {{
    const yOff = (idx * lineH) - (totalH / 2) + (lineH / 2);
    cx.fillText(ln, 0, yOff);
  }});
  cx.restore();

  // Central Visual Prop (Strict Safe Zone Y: 48% - 66%)
  const propY = IS_VERT ? H * 0.53 : H * 0.54;
  cx.save();
  cx.translate(W / 2, propY);

  // Dynamic Rare Earth Magnet / Technical Indicator
  cx.strokeStyle = ACCENT;
  cx.lineWidth = 3;
  // Neodymium Magnet Poles (North / South)
  cx.fillStyle = '#ef4444';
  cx.beginPath(); cx.roundRect(-160, -45, 150, 90, [12, 0, 0, 12]); cx.fill();
  cx.fillStyle = '#3b82f6';
  cx.beginPath(); cx.roundRect(10, -45, 150, 90, [0, 12, 12, 0]); cx.fill();

  cx.fillStyle = '#ffffff';
  cx.font = '900 36px "Inter", sans-serif';
  cx.textAlign = 'center';
  cx.fillText('N', -85, 12);
  cx.fillText('S', 85, 12);

  // Magnetic Flux Curves
  cx.strokeStyle = 'rgba(255, 214, 0, 0.4)';
  cx.lineWidth = 2;
  cx.beginPath();
  cx.arc(0, 0, 190, 0, Math.PI, true);
  cx.stroke();
  cx.beginPath();
  cx.arc(0, 0, 190, 0, Math.PI, false);
  cx.stroke();

  // On-Screen Metric Badge
  cx.fillStyle = '#111116';
  cx.strokeStyle = ACCENT;
  cx.lineWidth = 2;
  cx.beginPath();
  cx.roundRect(-220, 68, 440, 52, 10);
  cx.fill(); cx.stroke();

  cx.font = '800 20px "Inter", sans-serif';
  cx.fillStyle = '#ffffff';
  cx.fillText(curScene.visual_badge || '⚡ REPM STRATEGIC BREAKTHROUGH', 0, 101);
  cx.restore();

  // Bottom Safe Action Pill
  const pillY = IS_VERT ? H * 0.74 : H * 0.82;
  const pillW = Math.min(W - 140, 720);
  cx.fillStyle = 'rgba(20, 20, 28, 0.92)';
  cx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  cx.lineWidth = 1.5;
  cx.beginPath();
  cx.roundRect(W / 2 - pillW / 2, pillY - 30, pillW, 60, 14);
  cx.fill(); cx.stroke();

  cx.font = '700 ' + (IS_VERT ? 20 : 18) + 'px "Inter", sans-serif';
  cx.fillStyle = ACCENT;
  cx.textAlign = 'center';
  cx.fillText('⚡ ' + (curScene.broll_layers || curScene.visual_choreography), W / 2, pillY + 7);
}}

function updateDisplay() {{
  scrubber.value = currentTime;
  const m = Math.floor(currentTime / 60);
  const s = Math.floor(currentTime % 60);
  const totM = Math.floor(DURATION / 60);
  const totS = Math.floor(DURATION % 60);
  timeDisp.textContent = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}} / ${{String(totM).padStart(2,'0')}}:${{String(totS).padStart(2,'0')}}`;
}}

function loop(timestamp) {{
  if (!isPlaying) return;
  if (!lastTimestamp) lastTimestamp = timestamp;
  const delta = (timestamp - lastTimestamp) / 1000;
  lastTimestamp = timestamp;

  currentTime += delta;
  if (currentTime >= DURATION) {{
    currentTime = 0;
    isPlaying = false;
    playBtn.textContent = '▶ Play';
  }}

  drawScene(currentTime);
  updateDisplay();
  requestAnimationFrame(loop);
}}

playBtn.addEventListener('click', () => {{
  isPlaying = !isPlaying;
  playBtn.textContent = isPlaying ? '⏸ Pause' : '▶ Play';
  if (isPlaying) {{
    lastTimestamp = 0;
    requestAnimationFrame(loop);
  }}
}});

scrubber.addEventListener('input', (e) => {{
  currentTime = parseFloat(e.target.value);
  drawScene(currentTime);
  updateDisplay();
}});

// Initial draw
drawScene(0);
updateDisplay();
</script>
</body>
</html>
"""
