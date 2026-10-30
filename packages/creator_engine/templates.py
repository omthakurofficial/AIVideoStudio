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
        "music_style": "lofi_documentary (76 BPM cinematic orchestral strings & war drums)",
        "default_aspect": "16:9",
        "sample_topics": [
            "Why the Strait of Hormuz is the World's Most Dangerous Chokepoint",
            "The Geographic Curse of South America's Mountain Spine",
            "The Lithium Triangle: Who Controls the Next Century of Energy"
        ]
    },
    {
        "id": "podcast_avatar",
        "name": "Podcast to 2D/3D Cartoon Avatar",
        "category": "Interviews, Shows & Animation",
        "badge": "🎙️ Podcast & Cartoon",
        "reference_channels": "Joe Rogan Animated, Lex Fridman Shorts, Modern Wisdom Clips",
        "description": "Speaker converted to 2D/3D animated cartoon character with reactive emotional acting: laughing squint, shocked jaw drop, fist pump, split-screen PIP.",
        "colors": {
            "bg": "#18141f",
            "accent": "#a855f7",
            "secondary": "#ec4899",
            "highlight": "#22c55e",
            "panel": "#261e33"
        },
        "typography": {
            "display": "Bangers, Comic Sans, Impact, sans-serif",
            "body": "Inter, sans-serif",
            "accent": "Caveat, cursive"
        },
        "visual_elements": [
            "Character Avatar with Synchronized Mouth Flap Vowels",
            "Facial Expressions: [LAUGH], [SHOCKED], [SKEPTICAL], [EXCITED]",
            "Split-Screen Host & Guest Podcast Studio PIP Layout",
            "Comic Book Action Callout Bubbles with Wham/Pow SFX",
            "Floating Illustrated Thought Bubbles & Animated B-Roll Cutaways"
        ],
        "music_style": "playful_cartoon (110 BPM energetic bounce with comical pops and boings)",
        "default_aspect": "9:16",
        "sample_topics": [
            "Lex Fridman & Elon Musk: The Craziest Reality About Alien Civilizations",
            "Andrew Huberman: The 10-Minute Morning Routine That Changes Your Brain",
            "Joe Rogan: Why We Can Never Truly Trust Deepfakes Again"
        ]
    },
    {
        "id": "saas_tech_3d",
        "name": "Modern Dark SaaS & Cloud 3D Architecture",
        "category": "Developer & Enterprise Tech",
        "badge": "⚡ Dark SaaS Tech",
        "reference_channels": "Fireship, Theo - t3.gg, ByteByteGo, Primeagen",
        "description": "Void black (#050508), cyan laser (#38bdf8), 3D isometric cloud microservices, sub-millisecond speedometer dials, glowing terminal commands.",
        "colors": {
            "bg": "#050508",
            "accent": "#00f0ff",
            "secondary": "#7000ff",
            "highlight": "#30d158",
            "panel": "#0d0e15"
        },
        "typography": {
            "display": "Space Grotesk, sans-serif",
            "body": "Fira Code, monospace",
            "accent": "JetBrains Mono, monospace"
        },
        "visual_elements": [
            "3D Isometric Server & Database Cluster with Glowing Packet Flows",
            "Interactive macOS Terminal Window with Typewriter Shell Output",
            "Sub-Millisecond Cold Start Speedometer (0ms -> 45ms)",
            "Docker / Kubernetes Container Pod Namespace Pills",
            "Blinding White Flash Transition into Cyberpunk HUD"
        ],
        "music_style": "cyberpunk_synthwave (124 BPM driving synthwave with analog bassline)",
        "default_aspect": "16:9",
        "sample_topics": [
            "Why Kubernetes is Overkill for 95% of Companies",
            "How Discord Scaled to 11 Million Concurrent Voice Users with Elixir",
            "Postgres vs DynamoDB: The Hidden Cost Trap at 10,000 QPS"
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
            "bg": "#09090b",
            "accent": "#ffd60a",
            "secondary": "#ff3b30",
            "highlight": "#30d158",
            "panel": "#141418"
        },
        "typography": {
            "display": "Anton, Impact, sans-serif",
            "body": "Inter, sans-serif",
            "accent": "Instrument Serif, serif"
        },
        "visual_elements": [
            "Brutalist Giant Slammed Kinetic Typography (90px - 140px)",
            "Heavy Red Rubber Stamp: [ EXCUSES OBSOLETE ] or [ DEPRECATED ]",
            "30-Day Habit Streak Grid with Plateau of Latent Potential Highlight",
            "99% Quitter Statistic Counter Locking at 35.0s with Screen Shake",
            "3-Point Checklist with Animated Green Checkmarks and Golden CTA Card"
        ],
        "music_style": "lofi_documentary (84 BPM warm piano, gritty sub-bass & vinyl crackle)",
        "default_aspect": "9:16",
        "sample_topics": [
            "Why 99% of People Quit Right Before Success (The 30-Day Wall)",
            "The 20-Minute Dopamine Reset That Restores Total Focus",
            "Outwork Your Self-Doubt: The Psychology of Doing the Boring Work"
        ]
    },
    {
        "id": "true_crime",
        "name": "True Crime & Mystery Case Files",
        "category": "Mystery & Crime Investigations",
        "badge": "🕵️ True Crime & Mystery",
        "reference_channels": "JCS - Criminal Psychology, Coffeehouse Crime, Explore With Us",
        "description": "Cork investigation murder board with red connecting threads, polaroid photo drops, redacted FBI case files, flashlight circular mask, cassette SFX.",
        "colors": {
            "bg": "#0a0706",
            "accent": "#dc2626",
            "secondary": "#d4af37",
            "highlight": "#f5f5f4",
            "panel": "#171210"
        },
        "typography": {
            "display": "Special Elite, Courier, monospace",
            "body": "Inter, sans-serif",
            "accent": "Playfair Display, serif"
        },
        "visual_elements": [
            "Cork Pin Board with Red String Connecting Suspect Evidence",
            "Polaroid Photo Drop Animation with Angled 12-deg Tilt & Pushpin",
            "Redacted Top-Secret Dossier with Black Highlighter Bars",
            "Flashlight Vignette Mask Illuminating Clues in Darkness",
            "Audio Cassette Tape Waveform Reel Turning with Tape Hiss SFX"
        ],
        "music_style": "lofi_documentary (68 BPM dark atmospheric ambient drone & eerie ticking)",
        "default_aspect": "16:9",
        "sample_topics": [
            "The Mystery of Room 1046: The Unsolved Midnight Visitor",
            "The Psychology of Interrogation: How Detectives Spot the Subtle Tell",
            "The Digital Footprint That Solved an Unsolvable 20-Year Cold Case"
        ]
    },
    {
        "id": "science_tech",
        "name": "Deep Science & Quantum Tech",
        "category": "STEM, Physics & Biology",
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
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete CapCut/DaVinci-grade production blueprint and multi-AI prompt."""
        niche = NICHE_BY_ID.get(niche_id, TOP_10_NICHES[0])

        # Word count pacing based on 150 WPM
        wpm = 150
        target_words = int((target_duration_s / 60.0) * wpm)
        scene_count = max(4, min(30, int(math.ceil(target_duration_s / 10.0))))
        words_per_scene = max(18, int(target_words / scene_count))

        # Scene outline matrix
        scenes: List[Dict[str, Any]] = []
        cur_t = 0.0
        dur_per_scene = target_duration_s / scene_count

        archetype_roles = [
            ("Hook & High-Stakes Intrigue", "SLAM, RED_STRIKE, SERIF_ACCENT"),
            ("The Underlying Problem & Friction", "3D_MOCKUP, RED_BLOAT, SHAKE"),
            ("The Paradigm Shift / Mechanism", "ISOMETRIC_FLOW, GREEN_GLOW, COUNTER"),
            ("Real-World Proof & Data Benchmark", "ROLLING_STAT, SPEED_TIMER, CHECKMARKS"),
            ("Flat Rejection of Obsolete Ways", "RUBBER_STAMP, DEPRECATED, FLASH"),
            ("Final Breakthrough & Master Takeaway", "GOLDEN_CTA, 3_POINT_CHECKLIST, ORBIT")
        ]

        for i in range(scene_count):
            role_idx = i % len(archetype_roles)
            role_title, choreo = archetype_roles[role_idx]
            st = round(cur_t, 1)
            en = round(min(target_duration_s, cur_t + dur_per_scene), 1)
            cur_t = en

            scenes.append({
                "scene_number": i + 1,
                "title": f"Scene {i+1:02d}: {role_title}",
                "start_s": st,
                "end_s": en,
                "duration_s": round(en - st, 1),
                "target_word_count": words_per_scene,
                "narration_guidance": f"Spoken at {wpm} WPM with human inflection. Focus on {topic} for {niche['name']}.",
                "character_acting": "None" if niche_id != "podcast_avatar" else ("[LAUGH] & fist pump" if i % 2 == 0 else "[SHOCKED] jaw drop"),
                "visual_choreography": choreo,
                "broll_layers": niche["visual_elements"][i % len(niche["visual_elements"])],
                "camera_move": "Punch zoom (a: 0.08) + screen shake" if i == 0 else "Slow continuous cinematic push (z: 1.05)",
                "transition_out": "Whip Pan Right" if i % 2 == 0 else "RGB Glitch / White Flash",
                "sound_effects": ["[SFX: slam]", "[SFX: boom]", "[SFX: shimmer]"][i % 3]
            })

        # Generate Portable Multimodal AI Prompt for ChatGPT / Gemini / Claude
        portable_prompt = self._build_portable_prompt(
            topic=topic,
            niche=niche,
            target_duration_s=target_duration_s,
            aspect_ratio=aspect_ratio,
            target_words=target_words,
            scenes=scenes
        )

        # Generate Standalone Runnable HTML5 Player Code
        standalone_html = self._generate_standalone_html(
            topic=topic,
            niche=niche,
            target_duration_s=target_duration_s,
            aspect_ratio=aspect_ratio,
            scenes=scenes
        )

        return {
            "status": "success",
            "project_title": topic,
            "niche": niche,
            "target_duration_s": target_duration_s,
            "target_word_count": target_words,
            "aspect_ratio": aspect_ratio,
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
        scenes: List[Dict[str, Any]]
    ) -> str:
        """Construct a complete, ready-to-paste AI Prompt for Gemini, ChatGPT, or Claude."""
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
    f"## Scene {s['scene_number']:02d}: {s['title']}\n"
    f"- Timing: {s['start_s']}s – {s['end_s']}s (~{s['target_word_count']} words)\n"
    f"- Spoken Narration: \"[Write punchy human words here]\"\n"
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
        """Generate a complete, self-contained HTML5 animation player document."""
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600;700;800;900&display=swap">
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
    <div class="player-title">{topic[:35]}...</div>
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
let audioCtx = null;
let osc = null;

function ezOut(t) {{ return 1 - Math.pow(1 - Math.max(0, Math.min(1, t)), 3); }}

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

  // Current Scene Index
  let curScene = SCENES[0];
  for (const s of SCENES) {{ if (t >= s.start_s) curScene = s; }}

  // Header Chrome
  cx.fillStyle = ACCENT;
  cx.fillRect(IS_VERT ? 60 : 50, IS_VERT ? 140 : 40, 10, 10);
  cx.font = '700 ' + (IS_VERT ? 22 : 18) + 'px "Inter", sans-serif';
  cx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  cx.fillText('{niche["name"].upper()} · SCENE 0' + curScene.scene_number, IS_VERT ? 80 : 70, IS_VERT ? 150 : 49);

  // Animated Kinetic Title Card
  const sceneT = t - curScene.start_s;
  const animProg = ezOut(sceneT / 0.5);
  const scale = 1.35 - 0.35 * animProg;

  cx.save();
  const centerY = IS_VERT ? H * 0.42 : H * 0.45;
  cx.translate(W / 2, centerY);
  cx.scale(scale, scale);

  cx.font = '900 ' + (IS_VERT ? 76 : 84) + 'px "Anton", Impact, sans-serif';
  cx.textAlign = 'center';
  cx.fillStyle = '#f4f1ea';
  cx.shadowColor = 'rgba(0,0,0,0.8)';
  cx.shadowBlur = 30;

  // Split title into 2 lines if needed
  const titleParts = curScene.title.split(': ');
  const mainLabel = titleParts[1] ? titleParts[1].toUpperCase() : curScene.title.toUpperCase();
  cx.fillText(mainLabel, 0, -20);

  // Subtitle / Action choreo
  cx.font = 'italic 700 ' + (IS_VERT ? 36 : 40) + 'px "Instrument Serif", Georgia, serif';
  cx.fillStyle = ACCENT;
  cx.shadowColor = ACCENT;
  cx.shadowBlur = 20;
  cx.fillText(curScene.broll_layers || '{niche["visual_elements"][0]}', 0, 50);
  cx.restore();

  // Bottom Pill Card
  const pillY = IS_VERT ? H * 0.72 : H * 0.82;
  const pillW = Math.min(W - 120, 680);
  cx.fillStyle = 'rgba(20, 20, 28, 0.9)';
  cx.strokeStyle = ACCENT;
  cx.lineWidth = 1.5;
  cx.beginPath();
  cx.roundRect(W / 2 - pillW / 2, pillY - 30, pillW, 60, 14);
  cx.fill(); cx.stroke();

  cx.font = '700 ' + (IS_VERT ? 22 : 20) + 'px "Inter", sans-serif';
  cx.fillStyle = '#ffffff';
  cx.textAlign = 'center';
  cx.fillText('⚡ ' + (curScene.visual_choreography || 'KINETIC SLAM & CAMERA ORBIT'), W / 2, pillY + 7);
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
