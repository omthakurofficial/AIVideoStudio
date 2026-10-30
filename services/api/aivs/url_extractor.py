"""AI Video Studio V2 — Universal URL & Reference Media Deconstructor.

Extracts deep metadata, titles, descriptions, and full word-level transcripts
from YouTube Shorts, YouTube Videos, and web articles so that generated
scripts and visual choreography 100% match the actual source content.
"""
from __future__ import annotations

import html
import json
import logging
import re
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger("aivs.url_extractor")


def is_url(text: str) -> bool:
    """Check if the given text contains or is a valid HTTP/HTTPS URL."""
    if not text:
        return False
    return bool(re.search(r"https?://[^\s]+", text.strip()))


def extract_url_from_text(text: str) -> Optional[str]:
    """Find the first HTTP/HTTPS URL in the string."""
    m = re.search(r"https?://[^\s\"'>]+", text)
    return m.group(0) if m else None


def deconstruct_youtube_url(url: str) -> Dict[str, Any]:
    """Extract complete metadata, title, channel, description, and transcript from a YouTube URL."""
    clean_url = url.split("?si=")[0]  # Remove tracking parameter if present

    result: Dict[str, Any] = {
        "is_url": True,
        "platform": "youtube",
        "url": clean_url,
        "title": "",
        "channel": "",
        "duration_s": 0,
        "view_count": 0,
        "description": "",
        "transcript": "",
        "key_facts": [],
        "suggested_niche": "vox_explainer"
    }

    # 1. First attempt: yt-dlp metadata & subtitle extraction (fast and comprehensive)
    try:
        import yt_dlp
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            result["title"] = info.get("title") or ""
            result["channel"] = info.get("channel") or info.get("uploader") or ""
            result["duration_s"] = int(info.get("duration") or 0)
            result["view_count"] = int(info.get("view_count") or 0)
            result["description"] = info.get("description") or ""

            # Attempt to fetch English or Hindi subtitles
            subs = info.get("subtitles") or info.get("automatic_captions") or {}
            target_langs = ["en-orig", "en", "hi-orig", "hi"]
            for lang in target_langs:
                if lang in subs:
                    formats = subs[lang]
                    json3_url = next((f["url"] for f in formats if f.get("ext") == "json3"), None)
                    vtt_url = next((f["url"] for f in formats if f.get("ext") == "vtt"), None)
                    target_url = json3_url or vtt_url or (formats[0]["url"] if formats else None)
                    if target_url:
                        try:
                            req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0"})
                            with urllib.request.urlopen(req, timeout=8) as resp:
                                content = resp.read().decode("utf-8", errors="ignore")
                                if "json" in target_url:
                                    d = json.loads(content)
                                    words = []
                                    for ev in d.get("events", []):
                                        for s in ev.get("segs", []):
                                            if "utf8" in s and s["utf8"].strip():
                                                words.append(s["utf8"])
                                    result["transcript"] = " ".join(words).replace("\n", " ").strip()
                                else:
                                    # Strip VTT timestamps
                                    clean_text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", "", content)
                                    clean_text = re.sub(r"<[^>]+>", "", clean_text)
                                    result["transcript"] = " ".join(clean_text.split())
                                if result["transcript"]:
                                    break
                        except Exception as e:
                            logger.warning(f"Failed to fetch subtitle {lang}: {e}")
    except Exception as e:
        logger.warning(f"yt-dlp extraction fallback: {e}")

    # 2. Fallback to oEmbed + direct page scraping if yt-dlp was incomplete
    if not result["title"] or not result["description"]:
        try:
            oembed_url = f"https://www.youtube.com/oembed?url={clean_url}&format=json"
            req = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if not result["title"]:
                    result["title"] = data.get("title", "")
                if not result["channel"]:
                    result["channel"] = data.get("author_name", "")
        except Exception:
            pass

        try:
            req2 = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req2, timeout=8) as resp2:
                page = resp2.read().decode("utf-8", errors="ignore")
                if not result["title"]:
                    m_title = re.search(r"<title>(.*?)</title>", page)
                    if m_title:
                        result["title"] = m_title.group(1).replace(" - YouTube", "").strip()

                desc_match = re.search(r"\"shortDescription\":\"(.*?)\"", page)
                if desc_match:
                    raw_desc = desc_match.group(1).encode().decode("unicode_escape", errors="ignore")
                    result["description"] = html.unescape(raw_desc)
                elif not result["description"]:
                    m_desc = re.search(r"<meta\s+name=[\"\x27]description[\"\x27]\s+content=[\"\x27](.*?)[\"\x27]", page, re.I)
                    if m_desc:
                        result["description"] = html.unescape(m_desc.group(1))
        except Exception as e:
            logger.warning(f"Raw page scraping fallback failed: {e}")

    # 3. Extract core facts and determine best niche
    full_text = f"{result['title']} {result['description']} {result['transcript']}".lower()

    if any(k in full_text for k in ["rare earth", "china", "india", "geopolitic", "treaty", "military", "warfare", "chokepoint", "sanction", "map"]):
        result["suggested_niche"] = "geopolitics_maps"
    elif any(k in full_text for k in ["stock", "crypto", "inflation", "wealth", "invest", "market", "billionaire", "money"]):
        result["suggested_niche"] = "finance_wealth"
    elif any(k in full_text for k in ["algorithm", "youtube", "retention", "hook", "mrbeast", "ctr", "thumbnail"]):
        result["suggested_niche"] = "youtube_growth"
    elif any(k in full_text for k in ["quantum", "physics", "atom", "dna", "biology", "space", "telescope"]):
        result["suggested_niche"] = "science_tech"
    elif any(k in full_text for k in ["saas", "cloud", "code", "software", "api", "developer", "aws", "docker"]):
        result["suggested_niche"] = "saas_tech_3d"
    elif any(k in full_text for k in ["stoic", "discipline", "mindset", "motivation", "grind", "huberman", "goggins"]):
        result["suggested_niche"] = "mindset_motivation"
    else:
        result["suggested_niche"] = "vox_explainer"

    # Extract salient facts/bullet points
    sentences = re.split(r"[.!?]\s+", result["description"])
    salient = [s.strip() for s in sentences if len(s.strip()) > 20 and not s.strip().startswith("http")][:5]
    result["key_facts"] = salient

    return result


def deconstruct_article_url(url: str) -> Dict[str, Any]:
    """Extract title and paragraphs from a general article or blog URL."""
    result: Dict[str, Any] = {
        "is_url": True,
        "platform": "web_article",
        "url": url,
        "title": "",
        "description": "",
        "transcript": "",
        "key_facts": [],
        "suggested_niche": "vox_explainer"
    }
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            m_title = re.search(r"<title>(.*?)</title>", content, re.I)
            if m_title:
                result["title"] = html.unescape(m_title.group(1)).strip()

            m_desc = re.search(r"<meta\s+name=[\"\x27]description[\"\x27]\s+content=[\"\x27](.*?)[\"\x27]", content, re.I)
            if m_desc:
                result["description"] = html.unescape(m_desc.group(1)).strip()

            # Extract h1, h2, or main paragraphs
            paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", content, re.I | re.DOTALL)
            clean_paras = []
            for p in paragraphs:
                txt = re.sub(r"<[^>]+>", "", p).strip()
                if len(txt) > 40:
                    clean_paras.append(txt)
            result["transcript"] = " ".join(clean_paras[:8])
            result["key_facts"] = clean_paras[:4]
    except Exception as e:
        logger.warning(f"Article deconstruction error: {e}")

    return result


def deconstruct_reference_media(text_or_url: str) -> Dict[str, Any]:
    """Universal ingress: inspects text or URL and returns deep deconstructed facts and context."""
    extracted_url = extract_url_from_text(text_or_url)
    if not extracted_url:
        return {
            "is_url": False,
            "platform": "raw_concept",
            "topic": text_or_url.strip(),
            "title": text_or_url.strip()[:60],
            "description": text_or_url.strip(),
            "transcript": "",
            "key_facts": [],
            "suggested_niche": "youtube_growth"
        }

    # Check platform
    if "youtube.com" in extracted_url or "youtu.be" in extracted_url:
        info = deconstruct_youtube_url(extracted_url)
    else:
        info = deconstruct_article_url(extracted_url)

    info["raw_input"] = text_or_url
    return info
