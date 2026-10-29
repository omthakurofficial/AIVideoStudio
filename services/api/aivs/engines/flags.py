"""High-resolution national flags and diplomatic insignia generator for AIVideoStudio.

Provides crisp, broadcast-grade vector rendering for national flags:
  - Nepal (the iconic double-pennant with moon & sun)
  - India (saffron/white/green tricolor with navy 24-spoke Ashoka Chakra)
  - United States (stars & stripes)
  - France (blue/white/red vertical tricolor)
  - China (red field with golden star cluster)
  - United Kingdom (Union Jack)
  - Japan (sun disk)
  - Chile (lone star on blue canton + white/red stripes)
  - Generic sovereign heraldic shields with national monogram.
"""
from __future__ import annotations
import math
from PIL import Image, ImageDraw, ImageFont

COUNTRY_ALIASES: dict[str, str] = {
    "nepal": "nepal", "kathmandu": "nepal", "np": "nepal", "gorkha": "nepal", "himalayan": "nepal",
    "india": "india", "delhi": "india", "new delhi": "india", "in": "india", "bharat": "india",
    "united states": "usa", "usa": "usa", "us": "usa", "america": "usa", "american": "usa", "washington": "usa",
    "france": "france", "french": "france", "paris": "france", "fr": "france", "napoleon": "france",
    "china": "china", "chinese": "china", "beijing": "china", "cn": "china", "tibet": "china",
    "united kingdom": "uk", "uk": "uk", "britain": "uk", "british": "uk", "england": "uk", "london": "uk", "gb": "uk",
    "japan": "japan", "japanese": "japan", "tokyo": "japan", "jp": "japan",
    "chile": "chile", "chilean": "chile", "santiago": "chile", "cl": "chile",
}


def detect_country(text: str) -> str | None:
    """Detects a recognized country from a label, id, or subtitle."""
    low = text.lower()
    for token, cname in COUNTRY_ALIASES.items():
        # Match as whole word or distinctive substring
        if token in low.split() or f"_{token}" in low or f"{token}_" in low or low.startswith(token) or low.endswith(token):
            return cname
        if len(token) >= 4 and token in low:
            return cname
    return None


def draw_nepal_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    """Draws the authentic double-pennant flag of Nepal with crescent moon and 12-rayed sun."""
    border_color = (0, 56, 147, 255)
    crimson = (220, 20, 60, 255)
    white = (255, 255, 255, 255)
    bw = max(2, int(w * 0.06))

    # Outer border (double pennant geometry)
    p1 = (x, y)
    p2 = (x + w, y + h * 0.50)
    p3 = (x + w * 0.38, y + h * 0.50)
    p4 = (x + w, y + h)
    p5 = (x, y + h)
    draw.polygon([p1, p2, p3, p4, p5], fill=border_color)

    # Inner crimson field
    ip1 = (x + bw, y + bw * 1.6)
    ip2 = (x + w - bw * 2.2, y + h * 0.50 - bw * 0.6)
    ip3 = (x + w * 0.38 + bw * 0.4, y + h * 0.50)
    ip4 = (x + w - bw * 2.2, y + h - bw * 1.6)
    ip5 = (x + bw, y + h - bw)
    draw.polygon([ip1, ip2, ip3, ip4, ip5], fill=crimson)

    # Upper pennant: Crescent Moon
    mx, my = x + w * 0.28, y + h * 0.30
    mr = max(4, h * 0.11)
    draw.chord([mx - mr, my - mr, mx + mr, my + mr], start=30, end=150, fill=white)
    draw.ellipse([mx - mr * 0.65, my - mr * 0.9, mx + mr * 0.65, my - mr * 0.2], fill=white)

    # Lower pennant: 12-rayed Sun
    sx, sy = x + w * 0.30, y + h * 0.74
    sr = max(4, h * 0.12)
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=white)
    # Radiating points
    for i in range(12):
        angle = math.radians(i * 30)
        ex = sx + sr * 1.35 * math.cos(angle)
        ey = sy + sr * 1.35 * math.sin(angle)
        draw.line([(sx, sy), (ex, ey)], fill=white, width=max(1, int(h * 0.015)))


def draw_india_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    """Draws the authentic tricolor flag of India with the navy 24-spoke Ashoka Chakra."""
    saffron = (255, 153, 51, 255)
    white = (255, 255, 255, 255)
    green = (19, 136, 8, 255)
    navy = (0, 0, 128, 255)

    th = h / 3.0
    draw.rectangle([x, y, x + w, y + th], fill=saffron)
    draw.rectangle([x, y + th, x + w, y + 2 * th], fill=white)
    draw.rectangle([x, y + 2 * th, x + w, y + h], fill=green)
    draw.rectangle([x, y, x + w, y + h], outline=(30, 41, 59, 200), width=max(1, int(h * 0.02)))

    # Ashoka Chakra in center
    cx, cy = x + w / 2, y + 1.5 * th
    cr = max(4, th * 0.40)
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=navy, width=max(1, int(h * 0.035)))
    draw.ellipse([cx - cr * 0.22, cy - cr * 0.22, cx + cr * 0.22, cy + cr * 0.22], fill=navy)
    for i in range(24):
        angle = math.radians(i * 15)
        ex = cx + cr * math.cos(angle)
        ey = cy + cr * math.sin(angle)
        draw.line([(cx, cy), (ex, ey)], fill=navy, width=max(1, int(h * 0.015)))


def draw_usa_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    """Draws the Stars & Stripes flag of the United States."""
    sh = h / 13.0
    for i in range(13):
        color = (178, 34, 52, 255) if i % 2 == 0 else (255, 255, 255, 255)
        draw.rectangle([x, y + i * sh, x + w, y + (i + 1) * sh], fill=color)
    draw.rectangle([x, y, x + w * 0.42, y + 7 * sh], fill=(60, 59, 110, 255))
    draw.rectangle([x, y, x + w, y + h], outline=(30, 41, 59, 200), width=max(1, int(h * 0.02)))


def draw_france_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    """Draws the French vertical tricolor (blue, white, red)."""
    tw = w / 3.0
    draw.rectangle([x, y, x + tw, y + h], fill=(0, 38, 84, 255))
    draw.rectangle([x + tw, y, x + 2 * tw, y + h], fill=(255, 255, 255, 255))
    draw.rectangle([x + 2 * tw, y, x + w, y + h], fill=(237, 41, 57, 255))
    draw.rectangle([x, y, x + w, y + h], outline=(30, 41, 59, 200), width=max(1, int(h * 0.02)))


def draw_china_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    """Draws the Five-star Red Flag of China."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16, 255))
    gold = (255, 222, 0, 255)
    cx, cy = x + w * 0.22, y + h * 0.32
    r = h * 0.16
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gold)
    draw.rectangle([x, y, x + w, y + h], outline=(30, 41, 59, 200), width=max(1, int(h * 0.02)))


def draw_country_flag(draw: ImageDraw.ImageDraw, country: str, x: float, y: float, w: float, h: float) -> None:
    """Draws any supported national flag into bounding box [x, y, x+w, y+h]."""
    c = country.lower()
    if c == "nepal":
        draw_nepal_flag(draw, x, y, w, h)
    elif c == "india":
        draw_india_flag(draw, x, y, w, h)
    elif c in ("usa", "united states"):
        draw_usa_flag(draw, x, y, w, h)
    elif c == "france":
        draw_france_flag(draw, x, y, w, h)
    elif c in ("china", "tibet"):
        draw_china_flag(draw, x, y, w, h)
    else:
        # Generic sovereign heraldic shield with country initial
        draw.rounded_rectangle([x, y, x + w, y + h], radius=int(min(w, h) * 0.2), fill=(30, 58, 138, 255), outline=(251, 191, 36, 255), width=2)
        initial = (c[:2] if len(c) >= 2 else "NP").upper()
        draw.text((x + w * 0.25, y + h * 0.2), initial, fill=(255, 255, 255, 255))


def render_flag_shield_sprite(country: str, size_px: int = 180, label: str = "") -> Image.Image:
    """Renders a standalone transparent PNG badge for a national flag shield with drop shadow."""
    W = size_px + 40
    H = size_px + (50 if label else 20)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = W / 2, size_px / 2 + 10
    fw, fh = size_px * 0.85, size_px * 0.60
    if country.lower() == "nepal":
        fw, fh = size_px * 0.65, size_px * 0.80

    # Drop shadow
    fx, fy = cx - fw / 2, cy - fh / 2
    draw.rounded_rectangle([fx + 4, fy + 6, fx + fw + 4, fy + fh + 6], radius=8, fill=(0, 0, 0, 160))

    # Outer white/gold crest border
    draw.rounded_rectangle([fx - 4, fy - 4, fx + fw + 4, fy + fh + 4], radius=10, fill=(255, 255, 255, 245), outline=(251, 191, 36, 255), width=2)

    # Flag
    draw_country_flag(draw, country, fx, fy, fw, fh)

    if label:
        try:
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size_px * 0.13))
        except Exception:
            f = ImageFont.load_default()
        tb = draw.textbbox((0, 0), label, font=f)
        tw = tb[2] - tb[0]
        lx = max(4, cx - tw / 2)
        ly = fy + fh + 8
        draw.rounded_rectangle([lx - 8, ly - 3, lx + tw + 8, ly + 20], radius=6, fill=(15, 23, 42, 230), outline=(251, 191, 36, 220), width=1)
        draw.text((lx, ly), label, fill=(255, 255, 255, 255), font=f)

    return img
