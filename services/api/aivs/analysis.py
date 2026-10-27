"""Deterministic script analysis (no AI needed): paragraphs/sentences, word counts, rough duration.
Speaking rate is an assumption (150 wpm) and is only an estimate; real narration timing replaces it later."""
from __future__ import annotations
import re

WPM = 150


def analyze_script(script: str) -> dict:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", script) if p.strip()]
    out = []
    for i, p in enumerate(paragraphs, 1):
        words = len(re.findall(r"\S+", p))
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", p) if s]
        out.append({"index": i, "words": words, "sentences": len(sentences),
                    "estimated_seconds": round(words / WPM * 60, 1), "preview": p[:80]})
    total_words = sum(x["words"] for x in out)
    return {"paragraph_count": len(out), "total_words": total_words,
            "estimated_seconds": round(total_words / WPM * 60, 1),
            "assumed_wpm": WPM, "paragraphs": out}
