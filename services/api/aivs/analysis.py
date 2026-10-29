"""Deterministic script analysis, format detection, inline visual-hint extraction, and automatic duration/aspect calculation."""
from __future__ import annotations
import re
from pathlib import Path

WPM = 150

SUPPORTED_SCRIPT_FORMATS = [
    {
        "id": "plain_paragraphs",
        "name": "Plain Narration Paragraphs",
        "description": "Write spoken narration separated by blank lines. Each paragraph becomes a scene and the AI Director automatically plans diagrams and animations from meaning.",
        "example": "Every time a developer pushes code, a CI pipeline wakes up...\n\nNext, Kubernetes pulls that image and schedules it onto worker nodes...",
    },
    {
        "id": "structured_scenes_with_visual_hints",
        "name": "Scene Headings + [Visual: ...] Hints",
        "description": "Use '## Scene N: Title' headings and '[Visual: ...]' brackets to guide the visual style while keeping spoken narration clean (headings and brackets are never spoken aloud by TTS).",
        "example": "## Scene 1: Mutual TLS\n[Visual: Two microservice nodes exchanging certificate badges]\nEvery microservice proves its identity using mutual TLS before a packet is accepted.",
    },
    {
        "id": "topic_only",
        "name": "Topic-to-Script (AI Drafted)",
        "description": "Leave the script blank and enter a topic—AIVideoStudio drafts a multi-scene narration script automatically before producing the video.",
        "example": "Topic: How Redis cache-aside and database read replicas scale high-traffic APIs",
    },
]

SAMPLE_SCRIPTS_META = [
    {
        "id": "nepal_flood_documentary",
        "title": "Recent Nepal Monsoon Floods: 2D Map & River Basin Documentary",
        "file": "examples/nepal_flood_documentary.md",
        "aspect_ratio": "16:9",
        "visual_style": "warm-documentary",
        "category": "16:9 Non-Tech 2D Map & Stock Media Documentary",
    },
    {
        "id": "zero_trust_9x16",
        "title": "Zero-Trust mTLS Security (9:16 Vertical Short)",
        "file": "examples/zero_trust_9x16.md",
        "aspect_ratio": "9:16",
        "visual_style": "dark-neon",
        "category": "9:16 Vertical Explainer (Headings + [Visual] Hints)",
    },
    {
        "id": "devops_30s",
        "title": "DevOps CI/CD to Kubernetes Self-Healing",
        "file": "examples/devops_30s.md",
        "aspect_ratio": "16:9",
        "visual_style": "clean-technical",
        "category": "16:9 Landscape (Plain Paragraphs)",
    },
    {
        "id": "rag_pipeline_35s",
        "title": "How RAG Grounds LLMs with Vector Search",
        "file": "examples/rag_pipeline_35s.md",
        "aspect_ratio": "16:9",
        "visual_style": "clean-technical",
        "category": "16:9 Landscape (Headings + [Visual] Hints)",
    },
    {
        "id": "cloud_networking_75s",
        "title": "Global Cloud Architecture: DNS to Canary Rollback",
        "file": "examples/cloud_networking_75s.md",
        "aspect_ratio": "16:9",
        "visual_style": "dark-neon",
        "category": "16:9 Deep-Dive Documentary (6 Scenes)",
    },
]


def _parse_block(raw_block: str) -> tuple[str | None, list[str], str]:
    """Extract optional scene heading, inline [Visual: ...] hints, and clean spoken narration from a paragraph block."""
    heading: str | None = None
    hints: list[str] = []
    nar_lines: list[str] = []

    for line in raw_block.splitlines():
        s = line.strip()
        if not s:
            continue
        m_head = re.match(r"^(?:#{1,4}\s*|Scene\s+\d+\s*[:\-]\s*)(.+)$", s, flags=re.IGNORECASE)
        if m_head and not nar_lines:
            heading = m_head.group(1).strip()
            continue
        # Extract inline [Visual: ...] or (Visual: ...) cues
        for m_vis in re.finditer(r"\[(?:Visual|Animation|Show|Diagram|Style)\s*:\s*([^\]]+)\]", s, flags=re.IGNORECASE):
            hints.append(m_vis.group(1).strip())
        s_clean = re.sub(r"\[(?:Visual|Animation|Show|Diagram|Style)\s*:\s*[^\]]+\]", "", s, flags=re.IGNORECASE).strip()
        if s_clean:
            nar_lines.append(s_clean)

    narration = " ".join(nar_lines).strip()
    return heading, hints, narration


def analyze_script(script: str) -> dict:
    raw_blocks = [p.strip() for p in re.split(r"\n\s*\n", script or "") if p.strip()]
    out = []
    clean_paragraphs: list[str] = []
    visual_hints: list[str] = []
    has_headings = False
    has_visual_brackets = False

    for p in raw_blocks:
        heading, hints, narration = _parse_block(p)
        if heading:
            has_headings = True
        if hints:
            has_visual_brackets = True
        if not narration:
            continue
        idx = len(out) + 1
        words = len(re.findall(r"\S+", narration))
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", narration) if s]
        est_s = round(words / WPM * 60, 1)
        out.append({
            "index": idx,
            "words": words,
            "sentences": len(sentences),
            "estimated_seconds": est_s,
            "preview": narration[:80],
            "heading": heading,
            "visual_hint": "; ".join(hints) if hints else None,
            "narration": narration,
        })
        clean_paragraphs.append(narration)
        if heading or hints:
            parts = [f"Scene {idx}"]
            if heading:
                parts.append(f"({heading})")
            if hints:
                parts.append(": " + "; ".join(hints))
            visual_hints.append("".join(parts))

    total_words = sum(x["words"] for x in out)
    est_seconds = round(total_words / WPM * 60, 1)
    auto_target_s = max(10, int(round(total_words / 2.4))) if total_words > 0 else 30

    if has_visual_brackets and has_headings:
        detected_format = "structured_scenes_with_visual_hints"
    elif has_visual_brackets:
        detected_format = "inline_visual_hints"
    elif has_headings:
        detected_format = "heading_segmented"
    else:
        detected_format = "plain_paragraphs"

    max_para_words = max((x["words"] for x in out), default=0)
    if 0 < total_words <= 90 and len(out) <= 4 and max_para_words <= 36:
        rec_aspect = "9:16"
        aspect_reason = f"Concise {len(out)}-scene script ({total_words} words, ~{auto_target_s}s) fits 9:16 vertical or 16:9 landscape."
    else:
        rec_aspect = "16:9"
        aspect_reason = f"Multi-node technical script ({len(out)} scenes, {total_words} words, ~{auto_target_s}s) suits 16:9 widescreen diagrams."

    return {
        "paragraph_count": len(out),
        "total_words": total_words,
        "estimated_seconds": est_seconds,
        "recommended_target_duration_s": auto_target_s,
        "assumed_wpm": WPM,
        "detected_format": detected_format,
        "recommended_aspect_ratio": rec_aspect,
        "aspect_reason": aspect_reason,
        "clean_narration": "\n\n".join(clean_paragraphs),
        "visual_hints": visual_hints,
        "paragraphs": out,
        "auto_settings": {
            "target_duration_s": auto_target_s,
            "aspect_ratio": rec_aspect,
            "narration": {"mode": "generate", "voice": "kokoro:am_michael"},
            "captions": {"enabled": True, "font_size": 38},
            "approval_mode": "automatic",
        },
        "supported_formats": SUPPORTED_SCRIPT_FORMATS,
    }


def load_sample_scripts(repo_root: Path) -> list[dict]:
    from .niches import list_niches
    items: list[dict] = []
    for niche in list_niches():
        raw = niche["sample_script"]
        analysis = analyze_script(raw)
        items.append({
            "id": f"niche_{niche['id']}",
            "title": niche["sample_title"],
            "niche_category": niche["id"],
            "aspect_ratio": niche["default_aspect_ratio"],
            "visual_style": niche["default_visual_style"],
            "category": f"{niche['badge']} • {niche['name']}",
            "script": raw,
            "analysis": {
                "scene_count": analysis["paragraph_count"],
                "total_words": analysis["total_words"],
                "estimated_seconds": analysis["estimated_seconds"],
                "recommended_target_duration_s": analysis["recommended_target_duration_s"],
                "detected_format": analysis["detected_format"],
            },
        })
    for meta in SAMPLE_SCRIPTS_META:
        fpath = repo_root / meta["file"]
        if not fpath.is_file():
            continue
        raw = fpath.read_text(encoding="utf-8").strip()
        analysis = analyze_script(raw)
        items.append({
            **meta,
            "script": raw,
            "analysis": {
                "scene_count": analysis["paragraph_count"],
                "total_words": analysis["total_words"],
                "estimated_seconds": analysis["estimated_seconds"],
                "recommended_target_duration_s": analysis["recommended_target_duration_s"],
                "detected_format": analysis["detected_format"],
            },
        })
    return items
