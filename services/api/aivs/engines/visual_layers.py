"""High-resolution visual layer generator for AIVideoStudio.

Generates broadcast-grade transparent PNG layers imported directly into EffectCraft compositions via `file.import`:
  1. Real Cartographic Satellite/Relief Maps (`Esri World Imagery` tiles cached in `data/geo_cache/tiles/`)
     + Real GeoJSON Country & Region Polygons (`data/geo_cache/world_countries.geojson` + Nominatim hi-res polygons)
     + Real River Corridors + MirAtlas60/GeoGlobeTales Vertical Pointer Callout Pins.
  2. Vox Documentary Archival Paper Backdrop, Marker Highlighter Banners & Tilted White-Bordered Photo Cutouts.
  3. Story & History 2D Illustrated Cartoon Characters & Props (Louisiana Deal / Oversimplified / Disaster Rescue style).
  4. Finance & YouTube Growth Neon-Green (`#00FF44`) Exponential Trajectory Line Charts & Glassmorphic KPI Cards.
  5. Tech & Cloud Architecture Crisp Vector Service Tiles (AWS Lambda, S3, EC2, RDS, Route53, IAM, Kubernetes, Docker, AI).
"""
from __future__ import annotations
import json, math, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from ..config import REPO_ROOT
from .flags import detect_country, draw_country_flag, render_flag_shield_sprite

GEO_CACHE_DIR = REPO_ROOT / "data" / "geo_cache"
TILE_CACHE_DIR = GEO_CACHE_DIR / "tiles"

# Known geographic bounding boxes [lon_min, lat_min, lon_max, lat_max] for instant framing
KNOWN_BBOXES: dict[str, tuple[float, float, float, float]] = {
    "nepal": (79.4, 25.7, 88.8, 31.0),
    "nepal_india": (75.2, 23.8, 89.8, 31.8),
    "kathmandu": (84.8, 27.2, 86.0, 28.1),
    "bagmati": (84.6, 26.7, 86.2, 28.1),
    "koshi": (85.8, 26.2, 88.3, 28.4),
    "sapta koshi": (85.8, 26.2, 88.3, 28.4),
    "south asia": (68.0, 8.0, 97.0, 36.0),
    "india": (68.0, 7.5, 97.5, 36.0),
    "china": (73.5, 18.0, 135.0, 53.5),
    "chile": (-76.5, -56.0, -66.0, -17.0),
    "louisiana": (-108.0, 25.0, -70.0, 49.5),
    "united states": (-125.0, 24.0, -66.0, 50.0),
    "usa": (-125.0, 24.0, -66.0, 50.0),
    "new orleans": (-96.0, 27.0, -84.0, 35.0),
    "france": (-5.5, 41.0, 10.0, 51.5),
    "europe": (-11.0, 36.0, 32.0, 60.0),
    "united kingdom": (-9.0, 49.5, 2.5, 59.5),
}

# Real geographic coordinates for major rivers & basins (lon, lat polyline vertices)
REAL_RIVERS: dict[str, list[tuple[float, float]]] = {
    "bagmati": [(85.43, 27.81), (85.35, 27.73), (85.31, 27.68), (85.29, 27.55), (85.38, 27.32), (85.45, 27.05), (85.52, 26.75)],
    "bishnumati": [(85.35, 27.79), (85.31, 27.72), (85.30, 27.69)],
    "trishuli_narayani": [(85.18, 28.20), (84.88, 27.85), (84.42, 27.68), (84.12, 27.52), (83.85, 27.35)],
    "sapta_koshi": [(86.85, 27.95), (87.15, 27.35), (87.16, 26.92), (86.95, 26.52), (86.80, 26.15)],
    "sun_koshi": [(85.88, 27.78), (86.18, 27.42), (86.58, 27.18), (87.12, 26.92)],
    "arun": [(87.35, 27.85), (87.25, 27.35), (87.16, 26.92)],
    "tamor": [(87.85, 27.65), (87.55, 27.18), (87.16, 26.92)],
    "karnali": [(81.25, 29.65), (81.45, 29.10), (81.30, 28.65), (81.22, 28.15)],
    "mississippi": [(-95.2, 47.2), (-91.5, 43.5), (-90.2, 38.6), (-90.1, 35.1), (-91.4, 31.0), (-90.1, 29.9), (-89.2, 29.1)],
}

# Real sub-region polygon approximations (lon, lat) when a scene highlights a valley/basin/territory inside a country
SUBREGION_POLYGONS: dict[str, list[tuple[float, float]]] = {
    "kathmandu valley": [(85.18, 27.78), (85.28, 27.83), (85.46, 27.79), (85.54, 27.69), (85.48, 27.58), (85.32, 27.56), (85.20, 27.64)],
    "bagmati": [(85.10, 27.82), (85.45, 27.82), (85.62, 27.35), (85.60, 26.75), (85.22, 26.75), (85.12, 27.35)],
    "koshi": [(85.85, 27.95), (87.95, 27.85), (88.05, 26.65), (86.85, 26.38), (86.35, 26.85), (85.85, 27.45)],
    "sapta koshi": [(85.85, 27.95), (87.95, 27.85), (88.05, 26.65), (86.85, 26.38), (86.35, 26.85), (85.85, 27.45)],
    "mahabharat": [(80.5, 28.9), (83.5, 28.1), (85.5, 27.6), (87.9, 27.1), (87.9, 26.75), (85.4, 27.2), (83.3, 27.7), (80.4, 28.5)],
    "louisiana territory": [
        (-90.1, 29.9), (-92.2, 31.2), (-94.0, 33.5), (-96.5, 36.5), (-100.0, 37.5),
        (-103.0, 40.0), (-106.5, 43.5), (-111.0, 46.5), (-113.0, 49.0), (-95.2, 49.0),
        (-93.5, 46.5), (-91.2, 43.0), (-90.2, 38.6), (-89.5, 35.0), (-90.8, 31.0),
    ],
}

# Real city/landmark coordinates (lon, lat)
KNOWN_COORDS: dict[str, tuple[float, float]] = {
    "kathmandu": (85.3240, 27.7172),
    "delhi": (77.2090, 28.6139),
    "new delhi": (77.2090, 28.6139),
    "kalapani": (80.93, 30.22),
    "lipulekh": (81.04, 30.24),
    "birgunj": (84.88, 27.01),
    "raxaul": (84.85, 26.98),
    "sunauli": (83.47, 27.50),
    "bhairahawa": (83.45, 27.50),
    "himalayas": (85.0, 28.8),
    "bagmati": (85.33, 27.67),
    "bishnumati": (85.30, 27.71),
    "koshi": (86.95, 26.52),
    "sapta koshi": (86.95, 26.52),
    "barrage": (86.92, 26.52),
    "pokhara": (83.9856, 28.2096),
    "everest": (86.9250, 27.9881),
    "gauri shankar": (86.3350, 27.9530),
    "utc+5:45": (85.3240, 27.7172),
    "nepal": (84.1240, 28.3949),
    "india": (78.9629, 22.5937),
    "china": (92.0, 31.5),
    "new orleans": (-90.0715, 29.9511),
    "louisiana": (-99.5, 41.5),
    "paris": (2.3522, 48.8566),
    "france": (2.2137, 46.2276),
    "santiago": (-70.6693, -33.4489),
    "chile": (-71.5430, -35.6751),
}


def _font(size: int, bold: bool = True, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"]
        if mono
        else (
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            ]
            if bold
            else [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
        )
    )
    for p in candidates:
        if Path(p).is_file():
            try:
                return ImageFont.truetype(p, max(10, int(size)))
            except Exception:
                pass
    return ImageFont.load_default()


def _rgb(hex_str: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = (hex_str or "#3b82f6").lstrip("#")
    if len(h) != 6:
        h = "3b82f6"
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    except Exception:
        return (59, 130, 246, alpha)


# ---------------------------------------------------------------------------
# 1. REAL CARTOGRAPHIC SATELLITE / RELIEF MAP + EXACT GEOJSON POLYGONS
# ---------------------------------------------------------------------------

def _lonlat_to_tile_xy(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    lat = max(-85.0511, min(85.0511, lat))
    n = 2.0 ** zoom
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def _fetch_tile(z: int, x: int, y: int) -> Image.Image | None:
    TILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    n = 2 ** z
    x_wrapped = x % n
    if y < 0 or y >= n:
        return None
    cache_file = TILE_CACHE_DIR / f"esri_sat_{z}_{y}_{x_wrapped}.jpg"
    if cache_file.is_file() and cache_file.stat().st_size > 200:
        try:
            return Image.open(cache_file).convert("RGB")
        except Exception:
            pass
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x_wrapped}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AIVideoStudio/2.0 (Cartographic Engine)"})
        raw = urllib.request.urlopen(req, timeout=6).read()
        cache_file.write_bytes(raw)
        return Image.open(cache_file).convert("RGB")
    except Exception:
        return None


def _load_world_countries() -> list[dict]:
    path = GEO_CACHE_DIR / "world_countries.geojson"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8")).get("features", [])
        except Exception:
            pass
    return []


def _load_nepal_hires() -> dict | None:
    path = GEO_CACHE_DIR / "nepal_hires.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data and isinstance(data, list) and "geojson" in data[0]:
                return data[0]["geojson"]
        except Exception:
            pass
    return None


def _find_country_geojson(query_text: str) -> tuple[str, dict] | None:
    low = (query_text or "").lower()
    if "nepal" in low:
        hi = _load_nepal_hires()
        if hi:
            return ("Nepal", hi)
    features = _load_world_countries()
    aliases = {
        "usa": "united states of america",
        "united states": "united states of america",
        "uk": "united kingdom",
        "britain": "united kingdom",
    }
    for k, v in aliases.items():
        if re.search(rf"\b{re.escape(k)}\b", low):
            low = f"{low} {v}"
    for feat in features:
        name = str(feat.get("properties", {}).get("name", ""))
        if name and name.lower() in low:
            return (name, feat["geometry"])
    return None


def _detect_scene_bbox(scene, W: int, H: int) -> tuple[float, float, float, float, str]:
    blob = " ".join([
        getattr(scene, "key_message", "") or getattr(scene, "title", "") or "",
        getattr(scene, "narration_text", "") or getattr(scene, "narration_segment", "") or "",
        getattr(scene, "visual_description", "") or getattr(scene, "visual_prompt", "") or "",
        *(f"{e.label} {e.props.get('subtitle', '')}" for e in scene.visual_elements),
    ]).lower()

    primary_country = "Nepal"
    bbox = KNOWN_BBOXES["nepal"]
    if ("nepal" in blob or "kathmandu" in blob) and ("india" in blob or "delhi" in blob):
        bbox = KNOWN_BBOXES["nepal_india"]
        primary_country = "Nepal & India"
    elif any(w in blob for w in ("louisiana", "new orleans", "napoleon", "jefferson", "mississippi")):
        if "france" in blob and "louisiana" not in blob:
            bbox = KNOWN_BBOXES["france"]
            primary_country = "France"
        else:
            bbox = KNOWN_BBOXES["louisiana"]
            primary_country = "United States"
    elif "chile" in blob or "santiago" in blob or "andes" in blob:
        bbox = KNOWN_BBOXES["chile"]
        primary_country = "Chile"
    elif any(w in blob for w in ("nepal", "kathmandu", "bagmati", "koshi", "bishnumati", "himalaya", "monsoon")):
        bbox = KNOWN_BBOXES["nepal"]
        primary_country = "Nepal"
    else:
        for k, b in KNOWN_BBOXES.items():
            if k in blob:
                bbox = b
                primary_country = k.title()
                break

    # Adjust bounding box aspect ratio to match W:H in Web Mercator space
    lon_min, lat_min, lon_max, lat_max = bbox
    lon_span = max(1.0, lon_max - lon_min)
    lat_span = max(0.8, lat_max - lat_min)
    cx = (lon_min + lon_max) / 2.0
    cy = (lat_min + lat_max) / 2.0
    cos_lat = max(0.35, math.cos(math.radians(cy)))
    target_aspect = W / float(H)
    cur_aspect = (lon_span * cos_lat) / lat_span
    if cur_aspect < target_aspect:
        lon_span = (lat_span * target_aspect) / cos_lat
    else:
        lat_span = (lon_span * cos_lat) / target_aspect
    # Add 18% breathing margin around country
    lon_span *= 1.18
    lat_span *= 1.18
    return (cx - lon_span / 2.0, cy - lat_span / 2.0, cx + lon_span / 2.0, cy + lat_span / 2.0, primary_country)


class MapProjector:
    """Projects (lon, lat) <-> pixel (x, y) on the stitched satellite canvas."""
    def __init__(self, bbox: tuple[float, float, float, float], W: int, H: int, zoom: int):
        self.lon_min, self.lat_min, self.lon_max, self.lat_max = bbox
        self.W, self.H, self.zoom = W, H, zoom
        self.tx0, self.ty0 = _lonlat_to_tile_xy(self.lon_min, self.lat_max, zoom)
        self.tx1, self.ty1 = _lonlat_to_tile_xy(self.lon_max, self.lat_min, zoom)

    def to_px(self, lon: float, lat: float) -> tuple[float, float]:
        tx, ty = _lonlat_to_tile_xy(lon, lat, self.zoom)
        u = (tx - self.tx0) / max(1e-6, self.tx1 - self.tx0)
        v = (ty - self.ty0) / max(1e-6, self.ty1 - self.ty0)
        return (u * self.W, v * self.H)


def _iter_geojson_rings(geom: dict) -> list[list[tuple[float, float]]]:
    gtype = geom.get("type", "")
    coords = geom.get("coordinates", [])
    rings: list[list[tuple[float, float]]] = []
    if gtype == "Polygon":
        for ring in coords:
            rings.append([(float(pt[0]), float(pt[1])) for pt in ring])
    elif gtype == "MultiPolygon":
        for poly in coords:
            for ring in poly:
                rings.append([(float(pt[0]), float(pt[1])) for pt in ring])
    return rings


def render_real_map_scene_assets(scene, out_dir: Path, W: int, H: int, style: str = "warm-documentary") -> dict:
    """Renders:
      1. `map_base.png`: Stitched real Esri World Imagery satellite map + neighbor country borders + real river corridors + graticule + scale bar.
      2. `country_primary.png`: Exact high-resolution GeoJSON polygon of the primary country (e.g. Nepal 🇳🇵) with glowing fill + crisp white border.
      3. Per-element `poly_<id>.png` or `pin_<id>.png` for every `map_region` and `map_marker` in the scene.
    """
    assets_dir = out_dir / "layers"
    assets_dir.mkdir(parents=True, exist_ok=True)
    lon_min, lat_min, lon_max, lat_max, primary_country = _detect_scene_bbox(scene, W, H)

    # Choose optimal tile zoom level (usually 6 or 7 for Nepal/countries, 4 or 5 for continents)
    lon_span = lon_max - lon_min
    if lon_span <= 4.0:
        zoom = 8
    elif lon_span <= 14.0:
        zoom = 6
    elif lon_span <= 35.0:
        zoom = 5
    else:
        zoom = 4

    proj = MapProjector((lon_min, lat_min, lon_max, lat_max), W, H, zoom)

    # 1. Stitch real Esri World Imagery satellite tiles
    tx_start = int(math.floor(proj.tx0))
    tx_end = int(math.floor(proj.tx1))
    ty_start = int(math.floor(proj.ty0))
    ty_end = int(math.floor(proj.ty1))

    grid_w = max(1, tx_end - tx_start + 1) * 256
    grid_h = max(1, ty_end - ty_start + 1) * 256
    mosaic = Image.new("RGB", (grid_w, grid_h), (14, 28, 48))

    fetched_any = False
    for ty in range(ty_start, ty_end + 1):
        for tx in range(tx_start, tx_end + 1):
            tile = _fetch_tile(zoom, tx, ty)
            if tile is not None:
                mosaic.paste(tile, ((tx - tx_start) * 256, (ty - ty_start) * 256))
                fetched_any = True

    crop_x0 = int((proj.tx0 - tx_start) * 256)
    crop_y0 = int((proj.ty0 - ty_start) * 256)
    crop_x1 = max(crop_x0 + 64, int((proj.tx1 - tx_start) * 256))
    crop_y1 = max(crop_y0 + 64, int((proj.ty1 - ty_start) * 256))
    base_img = mosaic.crop((crop_x0, crop_y0, crop_x1, crop_y1)).resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")

    # Apply subtle cinematic contrast/grading so glowing polygons and labels pop like MirAtlas60 & Vox
    overlay = Image.new("RGBA", (W, H), (8, 15, 28, 58 if fetched_any else 0))
    base_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(base_img, "RGBA")

    u = min(W, H) / 1080.0

    # Draw subtle cartographic graticule grid lines + degree labels
    lon_step = 2.0 if lon_span <= 16 else (5.0 if lon_span <= 45 else 10.0)
    lat_step = 1.0 if (lat_max - lat_min) <= 10 else (2.0 if (lat_max - lat_min) <= 25 else 5.0)
    f_small = _font(int(15 * u), bold=True, mono=True)

    cur_lon = math.ceil(lon_min / lon_step) * lon_step
    while cur_lon < lon_max:
        px, _ = proj.to_px(cur_lon, (lat_min + lat_max) / 2)
        draw.line([(px, 0), (px, H)], fill=(148, 163, 184, 38), width=1)
        deg_lbl = f"{abs(cur_lon):.0f}°{'E' if cur_lon >= 0 else 'W'}"
        draw.text((px + 6, H - int(28 * u)), deg_lbl, fill=(203, 213, 225, 145), font=f_small)
        cur_lon += lon_step

    cur_lat = math.ceil(lat_min / lat_step) * lat_step
    while cur_lat < lat_max:
        _, py = proj.to_px((lon_min + lon_max) / 2, cur_lat)
        draw.line([(0, py), (W, py)], fill=(148, 163, 184, 38), width=1)
        deg_lbl = f"{abs(cur_lat):.0f}°{'N' if cur_lat >= 0 else 'S'}"
        draw.text((int(14 * u), py - int(20 * u)), deg_lbl, fill=(203, 213, 225, 145), font=f_small)
        cur_lat += lat_step

    # Draw neighboring country borders from world_countries.geojson in subtle slate-white
    world_feats = _load_world_countries()
    for feat in world_feats:
        cname = str(feat.get("properties", {}).get("name", ""))
        for ring in _iter_geojson_rings(feat.get("geometry", {})):
            pts = [proj.to_px(lon, lat) for lon, lat in ring]
            if any(0 <= x <= W and 0 <= y <= H for x, y in pts) and len(pts) >= 3:
                draw.line(pts + [pts[0]], fill=(226, 232, 240, 110), width=max(2, int(2 * u)))

    # Draw real river corridors (Bagmati, Sapta Koshi, Narayani, Karnali, Mississippi) if inside bbox
    for rname, rpts in REAL_RIVERS.items():
        px_pts = [proj.to_px(lon, lat) for lon, lat in rpts]
        if any(0 <= x <= W and 0 <= y <= H for x, y in px_pts):
            draw.line(px_pts, fill=(14, 165, 233, 115), width=max(6, int(10 * u)), joint="curve")
            draw.line(px_pts, fill=(125, 211, 252, 235), width=max(3, int(4 * u)), joint="curve")

    # Draw subtle neighbor country watermarks (e.g. INDIA, CHINA / TIBET) when viewing Nepal
    f_neighbor = _font(int(24 * u), bold=True)
    if primary_country == "Nepal":
        ix, iy = proj.to_px(82.5, 26.15)
        cx_p, cy_p = proj.to_px(85.5, 29.85)
        draw.text((ix, iy), "INDIA", fill=(255, 255, 255, 130), font=f_neighbor)
        draw.text((cx_p, cy_p), "CHINA (TIBET)", fill=(255, 255, 255, 130), font=f_neighbor)

    # Compass rose & cartographic scale bar in bottom-left
    cx_comp, cy_comp = int(68 * u), int(H - 72 * u)
    r_comp = int(28 * u)
    draw.ellipse([cx_comp - r_comp, cy_comp - r_comp, cx_comp + r_comp, cy_comp + r_comp], fill=(15, 23, 42, 210), outline=(251, 191, 36, 220), width=2)
    draw.polygon([(cx_comp, cy_comp - r_comp + 5), (cx_comp - 7, cy_comp), (cx_comp + 7, cy_comp)], fill=(251, 191, 36, 255))
    draw.text((cx_comp - 5, cy_comp - r_comp - int(18 * u)), "N", fill=(251, 191, 36, 255), font=f_small)

    map_base_path = assets_dir / "map_base.png"
    base_img.save(map_base_path, format="PNG")

    # 2. Render primary country high-res GeoJSON border layer (MirAtlas60 style glowing country polygon!)
    primary_poly_path = None
    target_countries = ["Nepal", "India"] if primary_country == "Nepal & India" else [primary_country]
    poly_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(poly_layer, "RGBA")
    gdraw = ImageDraw.Draw(glow_layer, "RGBA")

    country_badge_pos = None
    for cidx, ctarget in enumerate(target_countries):
        country_hit = _find_country_geojson(ctarget)
        if not country_hit:
            continue
        cname, geom = country_hit
        # MirAtlas60 style: Distinctive color palettes per nation
        if ctarget.lower() == "nepal":
            fill_rgba = (220, 38, 38, 95)  # Crimson tint
            glow_rgba = (251, 146, 60, 220) # Amber glow
            border_rgba = (255, 255, 255, 255)
        elif ctarget.lower() == "india":
            fill_rgba = (19, 136, 8, 75)   # Green/Saffron tint
            glow_rgba = (255, 153, 51, 210) # Saffron glow
            border_rgba = (254, 240, 138, 255)
        else:
            fill_rgba = (29, 78, 216, 125)
            glow_rgba = (56, 189, 248, 210)
            border_rgba = (255, 255, 255, 255)

        all_x, all_y = [], []
        for ring in _iter_geojson_rings(geom):
            pts = [proj.to_px(lon, lat) for lon, lat in ring]
            if len(pts) >= 3:
                for x, y in pts:
                    all_x.append(x)
                    all_y.append(y)
                gdraw.polygon(pts, fill=fill_rgba)
                gdraw.line(pts + [pts[0]], fill=glow_rgba, width=max(8, int(14 * u)), joint="curve")
                pdraw.polygon(pts, fill=fill_rgba)
                pdraw.line(pts + [pts[0]], fill=border_rgba, width=max(3, int(4.5 * u)), joint="curve")

    # Re-draw rivers inside the highlighted countries so Bagmati & Sapta Koshi gleam on top
    for rname, rpts in REAL_RIVERS.items():
        px_pts = [proj.to_px(lon, lat) for lon, lat in rpts]
        if any(0 <= x <= W and 0 <= y <= H for x, y in px_pts):
            pdraw.line(px_pts, fill=(14, 165, 233, 180), width=max(5, int(8 * u)), joint="curve")
            pdraw.line(px_pts, fill=(186, 230, 253, 255), width=max(2, int(3.5 * u)), joint="curve")

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=max(4, int(9 * u))))
    merged_country = Image.alpha_composite(glow_layer, poly_layer)

    # Draw Country Title + Flag Badges
    cdraw = ImageDraw.Draw(merged_country, "RGBA")
    f_country = _font(int(26 * u), bold=True)
    for ctarget in target_countries:
        c_code = detect_country(ctarget)
        if ctarget.lower() == "nepal":
            cent_x, cent_y = proj.to_px(83.2, 28.5)
        elif ctarget.lower() == "india":
            cent_x, cent_y = proj.to_px(80.5, 26.2)
        else:
            cent_x, cent_y = proj.to_px(*KNOWN_COORDS.get(ctarget.lower(), (84.1, 28.3)))

        lbl = ctarget.upper()
        bbox_txt = cdraw.textbbox((0, 0), lbl, font=f_country)
        tw, th = bbox_txt[2] - bbox_txt[0], bbox_txt[3] - bbox_txt[1]
        fw_badge = int(32 * u) if c_code else 0
        fh_badge = int(22 * u)
        bx0 = cent_x - (tw + fw_badge) / 2 - 16 * u
        by0 = cent_y - th / 2 - 10 * u
        bx1 = cent_x + (tw + fw_badge) / 2 + 16 * u
        by1 = cent_y + th / 2 + 10 * u
        cdraw.rounded_rectangle([bx0, by0, bx1, by1], radius=int(10 * u), fill=(15, 23, 42, 235), outline=(251, 191, 36, 255), width=max(2, int(2.5 * u)))
        if c_code:
            draw_country_flag(cdraw, c_code, bx0 + int(10 * u), cent_y - fh_badge / 2, fw_badge, fh_badge)
            cdraw.text((bx0 + fw_badge + int(16 * u), cent_y - th / 2 - 2 * u), lbl, fill=(255, 255, 255, 255), font=f_country)
        else:
            cdraw.text((cent_x - tw / 2, cent_y - th / 2 - 2 * u), lbl, fill=(255, 255, 255, 255), font=f_country)
        country_badge_pos = (cent_x, cent_y)

    primary_poly_path = assets_dir / "country_primary.png"
    merged_country.save(primary_poly_path, format="PNG")

    # 3. Render per-element sub-region polygons (`map_region`) and MirAtlas60/GeoGlobeTales vertical pointer pins (`map_marker`)
    element_layers: dict[str, dict] = {}
    used_pin_positions: list[tuple[float, float]] = [country_badge_pos] if country_badge_pos else []

    for idx, el in enumerate(scene.visual_elements):
        low_lbl = f"{el.label} {el.props.get('subtitle', '')}".lower()
        if el.kind == "map_region":
            # Check if this map_region matches a specific sub-region or another country
            sub_pts = None
            for k, poly_lonlat in SUBREGION_POLYGONS.items():
                if k in low_lbl:
                    sub_pts = [proj.to_px(lon, lat) for lon, lat in poly_lonlat]
                    break
            if sub_pts is None:
                c_hit = _find_country_geojson(low_lbl)
                if c_hit and c_hit[0].lower() != primary_country.lower():
                    rings = _iter_geojson_rings(c_hit[1])
                    if rings:
                        sub_pts = [proj.to_px(lon, lat) for lon, lat in max(rings, key=len)]

            reg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rdraw = ImageDraw.Draw(reg_img, "RGBA")
            c_rgba = _rgb(el.props.get("color") or ("#ef4444" if any(w in low_lbl for w in ("flood", "danger", "inundat", "surge", "risk")) else "#f59e0b"), 145)
            stroke_rgba = _rgb(el.props.get("color") or "#fbbf24", 255)

            if sub_pts and len(sub_pts) >= 3:
                rdraw.polygon(sub_pts, fill=c_rgba)
                rdraw.line(sub_pts + [sub_pts[0]], fill=(255, 255, 255, 245), width=max(3, int(3.5 * u)), joint="curve")
                cx_r = sum(p[0] for p in sub_pts) / len(sub_pts)
                cy_r = sum(p[1] for p in sub_pts) / len(sub_pts)
                _draw_atlas_callout(rdraw, cx_r, cy_r, el.label, str(el.props.get("subtitle") or ""), stroke_rgba, u, W, H, idx, used_pin_positions)
            elif el.label.strip().lower() == primary_country.lower():
                # Primary country is already highlighted by country_primary.png; no duplicate oval needed
                cx_r, cy_r = proj.to_px(*KNOWN_COORDS.get(primary_country.lower(), (84.1, 28.3)))
            else:
                # Place at explicit coordinates, known coordinates, or spread cleanly across country
                raw_lon = el.props.get("lon") or el.props.get("longitude")
                raw_lat = el.props.get("lat") or el.props.get("latitude")
                if raw_lon is not None and raw_lat is not None:
                    lon_c, lat_c = float(raw_lon), float(raw_lat)
                else:
                    lon_c, lat_c = KNOWN_COORDS.get("kathmandu", (85.32, 27.71))
                    for k, coord in KNOWN_COORDS.items():
                        if k in low_lbl:
                            lon_c, lat_c = coord
                            break
                cx_r, cy_r = proj.to_px(lon_c, lat_c)
                rx, ry = int(85 * u), int(52 * u)
                rdraw.ellipse([cx_r - rx, cy_r - ry, cx_r + rx, cy_r + ry], fill=c_rgba, outline=stroke_rgba, width=max(3, int(3.5 * u)))
                _draw_atlas_callout(rdraw, cx_r, cy_r, el.label, str(el.props.get("subtitle") or ""), stroke_rgba, u, W, H, idx, used_pin_positions)

            p_out = assets_dir / f"map_el_{el.id}_layer.png"
            reg_img.save(p_out, format="PNG")
            element_layers[el.id] = {"path": p_out, "full_canvas": True, "cx": cx_r, "cy": cy_r}

        elif el.kind == "map_marker":
            raw_lon = el.props.get("lon") or el.props.get("longitude")
            raw_lat = el.props.get("lat") or el.props.get("latitude")
            if raw_lon is not None and raw_lat is not None:
                lon_c, lat_c = float(raw_lon), float(raw_lat)
            else:
                lon_c, lat_c = None, None
                for k, coord in KNOWN_COORDS.items():
                    if k in low_lbl:
                        lon_c, lat_c = coord
                        break
            if lon_c is not None and lat_c is not None:
                cx_m, cy_m = proj.to_px(lon_c, lat_c)
            else:
                # Default to Kathmandu / central Nepal with slight offset per index
                cx_m, cy_m = proj.to_px(85.32 + (idx - 1) * 0.85, 27.71 - (idx % 2) * 0.45)

            pin_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            pdraw = ImageDraw.Draw(pin_img, "RGBA")
            accent_rgba = _rgb(el.props.get("color") or "#fbbf24", 255)
            _draw_atlas_callout(pdraw, cx_m, cy_m, el.label, str(el.props.get("subtitle") or ""), accent_rgba, u, W, H, idx + 2, used_pin_positions)
            p_out = assets_dir / f"map_el_{el.id}_layer.png"
            pin_img.save(p_out, format="PNG")
            element_layers[el.id] = {"path": p_out, "full_canvas": True, "cx": cx_m, "cy": cy_m}

    return {
        "map_base": map_base_path,
        "country_primary": primary_poly_path,
        "element_layers": element_layers,
        "primary_country": primary_country,
    }


def _draw_atlas_callout(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    title: str,
    subtitle: str,
    accent_rgba: tuple[int, int, int, int],
    u: float,
    W: int,
    H: int,
    slot_idx: int,
    used_positions: list[tuple[float, float]],
) -> None:
    """Draws a MirAtlas60 / Vox style glowing target ring at (cx, cy) + vertical/angled pointer line + crisp callout card."""
    # Target radar rings at exact geographic point
    r_outer = int(20 * u)
    r_inner = int(8 * u)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=(accent_rgba[0], accent_rgba[1], accent_rgba[2], 70), outline=(255, 255, 255, 230), width=max(2, int(2 * u)))
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=accent_rgba, outline=(15, 23, 42, 255), width=max(2, int(2 * u)))

    f_title = _font(int(22 * u), bold=True)
    f_sub = _font(int(16 * u), bold=False)
    t_str = (title or "LOCATION").strip()
    s_str = (subtitle or "").strip()

    tb = draw.textbbox((0, 0), t_str, font=f_title)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    sw, sh = 0, 0
    if s_str:
        sb = draw.textbbox((0, 0), s_str, font=f_sub)
        sw, sh = sb[2] - sb[0], sb[3] - sb[1]

    c_flag = detect_country(f"{t_str} {s_str}")
    flag_w = int(32 * u) if c_flag else 0
    box_w = max(tw + flag_w + int(12 * u), sw) + int(36 * u)
    box_h = th + (sh + int(10 * u) if s_str else 0) + int(22 * u)

    # Choose callout box position above or below (cx, cy), avoiding collisions
    offsets = [
        (0, -int(95 * u)),
        (int(110 * u), -int(85 * u)),
        (-int(110 * u), -int(85 * u)),
        (0, int(95 * u)),
        (int(120 * u), int(85 * u)),
        (-int(120 * u), int(85 * u)),
    ]
    dx, dy = offsets[slot_idx % len(offsets)]
    bx = max(box_w / 2 + 20 * u, min(W - box_w / 2 - 20 * u, cx + dx))
    by = max(box_h / 2 + 95 * u, min(H - box_h / 2 - 140 * u, cy + dy))

    for ux, uy in used_positions:
        if abs(bx - ux) < box_w * 0.85 and abs(by - uy) < box_h * 1.1:
            by = max(box_h / 2 + 95 * u, min(H - box_h / 2 - 140 * u, by + (box_h + 24 * u) * (1 if by < H / 2 else -1)))

    used_positions.append((bx, by))

    # Pointer stem line from (cx, cy) to callout card
    draw.line([(cx, cy), (bx, by)], fill=(255, 255, 255, 235), width=max(2, int(3 * u)))

    x0, y0 = bx - box_w / 2, by - box_h / 2
    x1, y1 = bx + box_w / 2, by + box_h / 2
    # Shadow + dark slate card + yellow/accent left stripe
    draw.rounded_rectangle([x0 + 4 * u, y0 + 6 * u, x1 + 4 * u, y1 + 6 * u], radius=int(10 * u), fill=(0, 0, 0, 160))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=int(10 * u), fill=(15, 23, 42, 242), outline=accent_rgba, width=max(2, int(2.5 * u)))
    draw.rounded_rectangle([x0, y0, x0 + int(8 * u), y1], radius=int(4 * u), fill=accent_rgba)

    draw.text((x0 + int(18 * u), y0 + int(9 * u)), t_str, fill=(255, 255, 255, 255), font=f_title)
    if c_flag:
        fx = x0 + int(18 * u) + tw + int(8 * u)
        fy = y0 + int(10 * u)
        draw_country_flag(draw, c_flag, fx, fy, int(26 * u), int(18 * u))
    if s_str:
        draw.text((x0 + int(18 * u), y0 + int(13 * u) + th), s_str, fill=(251, 191, 36, 255), font=f_sub)


# ---------------------------------------------------------------------------
# 2. NICHE STAGE BACKDROPS (VOX PAPER, FINANCE NEON CHART, TECH CLOUD GRID)
# ---------------------------------------------------------------------------

def render_stage_backdrop(scene, out_dir: Path, W: int, H: int, style: str) -> Path:
    """Renders a rich full-canvas backdrop tailored to the scene's style and visual_type."""
    assets_dir = out_dir / "layers"
    assets_dir.mkdir(parents=True, exist_ok=True)
    u = min(W, H) / 1080.0
    vtype = getattr(scene, "visual_type", None) or "concept"
    s_title = getattr(scene, "key_message", "") or getattr(scene, "title", "") or "SCENE"
    s_narr = getattr(scene, "narration_text", "") or getattr(scene, "narration_segment", "") or ""
    s_desc = getattr(scene, "visual_description", "") or getattr(scene, "visual_prompt", "") or ""
    blob = f"{s_title} {s_narr} {s_desc}".lower()

    img = Image.new("RGBA", (W, H), (11, 16, 33, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    if style in ("cloudxberry", "studio-white") or (style in ("clean-technical", "architecture") and any(k in blob for k in ("cloud", "aws", "data center", "server", "architecture", "region", "console", "cli", "sdk"))):
        # CLOUD X BERRY / BYTEBYTEGO / EXECUTIVE STUDIO-WHITE STAGE (Reference: yt_LPJ1zHDC0Ck @ 74s)
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img, "RGBA")
        step = int(48 * u)
        for x in range(step // 2, W, step):
            for y in range(step // 2, H, step):
                draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(226, 232, 240, 220))

        # Top Header Zone: Topic Headline with colored accent bar
        f_title = _font(int(38 * u), bold=True)
        title_txt = (s_title or "CLOUD ARCHITECTURE").strip()
        draw.text((int(70 * u), int(48 * u)), title_txt, fill=(15, 23, 42, 255), font=f_title)
        tb = draw.textbbox((int(70 * u), int(48 * u)), title_txt, font=f_title)
        acc_w = min(int(160 * u), max(int(60 * u), (tb[2] - tb[0]) // 3))
        draw.rounded_rectangle([int(70 * u), int(98 * u), int(70 * u) + acc_w, int(104 * u)], radius=int(3 * u), fill=(124, 58, 237, 255))

        # Top-right Chapter Progress Pill
        pill_w, pill_h = int(300 * u), int(46 * u)
        pill_x, pill_y = W - int(70 * u) - pill_w, int(48 * u)
        draw.rounded_rectangle([pill_x + 2, pill_y + 3, pill_x + pill_w + 2, pill_y + pill_h + 3], radius=int(23 * u), fill=(0, 0, 0, 16))
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=int(23 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=2)
        
        sc_num = getattr(scene, "id", "s01").replace("s", "")
        sc_num_str = f"{int(sc_num):02d}" if sc_num.isdigit() else "01"
        draw.rounded_rectangle([pill_x + int(6 * u), pill_y + int(6 * u), pill_x + int(56 * u), pill_y + pill_h - int(6 * u)], radius=int(17 * u), fill=(124, 58, 237, 255))
        f_tag = _font(int(16 * u), bold=True)
        draw.text((pill_x + int(16 * u), pill_y + int(13 * u)), sc_num_str, fill=(255, 255, 255, 255), font=f_tag)

        f_total = _font(int(16 * u), bold=True)
        draw.text((pill_x + int(66 * u), pill_y + int(13 * u)), "/ 15", fill=(100, 116, 139, 255), font=f_total)

        dots_start_x = pill_x + int(115 * u)
        cur_idx = int(sc_num) if sc_num.isdigit() else 1
        for d in range(8):
            dx = dots_start_x + d * int(21 * u)
            dot_color = (124, 58, 237, 255) if (d + 1) * 2 <= cur_idx else (203, 213, 225, 255)
            dw = int(12 * u) if (d + 1) * 2 <= cur_idx else int(8 * u)
            draw.rounded_rectangle([dx, pill_y + int(19 * u), dx + dw, pill_y + int(27 * u)], radius=int(4 * u), fill=dot_color)

    elif style == "light-minimal" or "vox" in blob:
        # VOX ARCHIVAL EDITORIAL PAPER + BLUEPRINT GRID (Reference: yt_tbXmAGw-qMM.jpg)
        img = Image.new("RGBA", (W, H), (239, 235, 224, 255))
        draw = ImageDraw.Draw(img, "RGBA")
        step = int(48 * u)
        for x in range(0, W, step):
            draw.line([(x, 0), (x, H)], fill=(203, 198, 184, 110), width=1)
        for y in range(0, H, step):
            draw.line([(0, y), (W, y)], fill=(203, 198, 184, 110), width=1)
        # Editorial top rule & vintage corner marks
        draw.line([(int(60 * u), int(52 * u)), (W - int(60 * u), int(52 * u))], fill=(30, 41, 59, 180), width=2)
        f_ed = _font(int(15 * u), bold=True, mono=True)
        draw.text((int(64 * u), int(26 * u)), f"ARCHIVE DOSSIER // {s_title.upper()[:48]}", fill=(71, 85, 105, 220), font=f_ed)

    elif (style == "dark-neon" and vtype == "chart") or (vtype == "chart" and any(w in blob for w in ("views", "subscriber", "rpm", "growth"))):
        # FINANCE & YOUTUBE GROWTH FULL-CANVAS NEON CHART BACKDROP (Reference: yt_9yXNBbf3TW0.jpg & yt_FioWlQQG2fU.jpg)
        img = Image.new("RGBA", (W, H), (6, 11, 10, 255))
        draw = ImageDraw.Draw(img, "RGBA")
        # Subtle carbon dot grid
        step = int(42 * u)
        for x in range(step // 2, W, step):
            for y in range(step // 2, H, step):
                draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(34, 197, 94, 48))
        # Horizontal analytics grid lines
        for frac in (0.25, 0.45, 0.65, 0.82):
            yy = int(H * frac)
            draw.line([(int(70 * u), yy), (W - int(70 * u), yy)], fill=(30, 58, 47, 120), width=1)
        # Full-canvas glowing neon-green (#00FF44) exponential trajectory curve across the background
        curve_pts = [
            (int(W * 0.06), int(H * 0.82)),
            (int(W * 0.22), int(H * 0.76)),
            (int(W * 0.38), int(H * 0.71)),
            (int(W * 0.54), int(H * 0.58)),
            (int(W * 0.70), int(H * 0.44)),
            (int(W * 0.84), int(H * 0.27)),
            (int(W * 0.94), int(H * 0.16)),
        ]
        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer, "RGBA")
        poly_fill = curve_pts + [(int(W * 0.94), int(H * 0.86)), (int(W * 0.06), int(H * 0.86))]
        gdraw.polygon(poly_fill, fill=(0, 255, 68, 34))
        gdraw.line(curve_pts, fill=(0, 255, 68, 190), width=max(8, int(14 * u)), joint="curve")
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=max(6, int(12 * u))))
        img = Image.alpha_composite(img, glow_layer)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.line(curve_pts, fill=(0, 255, 102, 255), width=max(4, int(5 * u)), joint="curve")
        for px, py in curve_pts[1:]:
            draw.ellipse([px - int(7 * u), py - int(7 * u), px + int(7 * u), py + int(7 * u)], fill=(0, 255, 102, 255), outline=(255, 255, 255, 255), width=2)

    else:
        # CLEAN-TECHNICAL / CLOUD ARCHITECTURE / WARM DOCUMENTARY STAGE (Reference: yt_LPJ1zHDC0Ck.jpg)
        bg_rgba = (28, 35, 51, 255) if style == "warm-documentary" else (9, 13, 26, 255)
        grid_rgba = (245, 158, 11, 28) if style == "warm-documentary" else (59, 130, 246, 36)
        img = Image.new("RGBA", (W, H), bg_rgba)
        draw = ImageDraw.Draw(img, "RGBA")
        step = int(56 * u)
        for x in range(0, W, step):
            draw.line([(x, 0), (x, H)], fill=grid_rgba, width=1)
        for y in range(0, H, step):
            draw.line([(0, y), (W, y)], fill=grid_rgba, width=1)
        # Subtle center radial spotlight
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        gd.ellipse([int(W * 0.16), int(H * 0.10), int(W * 0.84), int(H * 0.90)],
                   fill=(245, 158, 11, 52) if style == "warm-documentary" else (37, 99, 235, 42))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=max(20, int(55 * u))))
        img = Image.alpha_composite(img, glow)

    out_path = assets_dir / "stage_backdrop.png"
    img.save(out_path, format="PNG")
    return out_path


# ---------------------------------------------------------------------------
# 3. 2D CARTOON CHARACTERS, REAL VECTOR TECH TILES & EDITORIAL CARDS
# ---------------------------------------------------------------------------

def render_element_sprite(el, w_px: float, h_px: float, u: float, style: str, out_dir: Path) -> Path:
    """Renders a crisp transparent PNG sprite for an icon, 2D cartoon character, tech tile, KPI card, or Vox callout."""
    assets_dir = out_dir / "layers"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Give icons room for their badge + label pill underneath
    if el.kind == "icon":
        cw = max(220, int(w_px), len(el.label or "") * int(12 * u) + int(40 * u))
        ch = max(160, int(h_px))
    elif el.kind == "title_card":
        cw = max(420, int(w_px + 40 * u), len(el.label or "") * int(16 * u) + int(60 * u))
        ch = max(130, int(h_px + 24 * u))
    elif el.kind == "timeline_marker":
        cw = max(240, int(w_px), len(el.label or "") * int(13 * u) + int(48 * u))
        ch = max(150, int(h_px))
    else:
        cw = max(260, int(w_px + 36 * u), len(el.label or "") * int(14 * u) + int(54 * u))
        ch = max(130, int(h_px + 28 * u))

    low = f"{el.label} {el.props.get('icon', '')} {el.props.get('subtitle', '')} {el.id}".lower()
    arch = el.props.get("archetype", "").lower()
    accent_hex = el.props.get("color") or ("#f59e0b" if style == "warm-documentary" else ("#00ff66" if style == "dark-neon" else "#3b82f6"))
    accent = _rgb(accent_hex, 255)

    # Expand canvas dimensions for executive studio archetypes
    if arch == "datacenter" or (el.kind in ("card", "box") and any(k in low for k in ("datacenter", "data center", "server rack", "facility"))):
        cw = max(cw, int(1050 * u))
        ch = max(ch, int(720 * u))
    elif arch == "tooling_gateways" or (el.kind in ("card", "box") and any(k in low for k in ("gateways", "access gateway", "console cli sdk"))):
        cw = max(cw, int(1720 * u))
        ch = max(ch, int(700 * u))
    elif arch == "comparison" or (el.kind in ("card", "box") and any(k in low for k in ("capex", "opex", "economics", "comparison"))):
        cw = max(cw, int(1680 * u))
        ch = max(ch, int(700 * u))
    elif arch == "region_topology" or (el.kind in ("card", "box") and any(k in low for k in ("region and az", "availability zone", "anatomy of a region"))):
        cw = max(cw, int(1720 * u))
        ch = max(ch, int(710 * u))
    elif el.kind == "callout" and (arch == "pill" or any(k in low for k in ("power", "network", "cooling", "latency", "sla"))):
        cw = max(cw, int(310 * u))
        ch = max(ch, int(72 * u))
    elif el.kind == "icon" and (arch == "squircle" or any(k in low for k in ("amazon", "microsoft", "google", "apple", "brand"))):
        cw = max(cw, int(130 * u))
        ch = max(ch, int(160 * u))

    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    from .studio_archetypes import (
        draw_datacenter_grid, draw_tooling_mockups, draw_comparison_split,
        draw_region_topology, draw_squircle_brand, draw_callout_pill,
        draw_hierarchy_stack, draw_edge_network_map, draw_hybrid_outposts
    )

    if arch == "hierarchy_stack" or (el.kind in ("card", "box") and any(k in low for k in ("hierarchy", "4-tier", "blueprint", "global infrastructure overview"))):
        draw_hierarchy_stack(draw, img, cw, ch, el, u, style)
    elif arch == "datacenter" or (el.kind in ("card", "box") and any(k in low for k in ("datacenter", "data center", "server rack", "facility"))):
        draw_datacenter_grid(draw, img, cw, ch, el, u, style)
    elif arch == "tooling_gateways" or (el.kind in ("card", "box") and any(k in low for k in ("gateways", "access gateway", "console cli sdk"))):
        draw_tooling_mockups(draw, img, cw, ch, el, u, style)
    elif arch == "comparison" or (el.kind in ("card", "box") and any(k in low for k in ("capex", "opex", "economics", "comparison"))):
        draw_comparison_split(draw, img, cw, ch, el, u, style)
    elif arch == "region_topology" or (el.kind in ("card", "box") and any(k in low for k in ("region and az", "availability zone", "anatomy of a region"))):
        draw_region_topology(draw, img, cw, ch, el, u, style)
    elif arch == "edge_network" or (el.kind in ("card", "box") and any(k in low for k in ("edge locations", "points of presence", "pops", "cloudfront", "route 53", "ddos"))):
        draw_edge_network_map(draw, img, cw, ch, el, u, style)
    elif arch == "hybrid_outposts" or (el.kind in ("card", "box") and any(k in low for k in ("hybrid edge", "outposts", "local zones", "42u rack"))):
        draw_hybrid_outposts(draw, img, cw, ch, el, u, style)
    elif el.kind == "icon" and (arch == "squircle" or any(k in low for k in ("amazon", "microsoft", "google", "apple", "brand"))):
        draw_squircle_brand(draw, img, cw, ch, el.label, low, u, style)
    elif el.kind == "callout" and (arch == "pill" or any(k in low for k in ("power", "network", "cooling", "latency", "sla"))):
        draw_callout_pill(draw, img, cw, ch, el.label, low, u, style)
    elif el.kind == "icon":
        _draw_icon_or_cartoon_sprite(draw, cw, ch, el.label, str(el.props.get("subtitle") or ""), low, accent, u, style)
    elif el.kind == "title_card":
        _draw_title_card_sprite(draw, cw, ch, el.label, str(el.props.get("subtitle") or ""), accent, u, style)
    elif el.kind == "callout":
        _draw_callout_sprite(draw, cw, ch, el.label, str(el.props.get("subtitle") or ""), accent, u, style)
    else:
        _draw_rich_card_sprite(draw, cw, ch, el, low, accent, u, style)

    out_path = assets_dir / f"sprite_{el.id}_layer.png"
    img.save(out_path, format="PNG")
    return out_path


def _draw_icon_or_cartoon_sprite(
    draw: ImageDraw.ImageDraw, cw: int, ch: int, title: str, subtitle: str, low: str,
    accent: tuple[int, int, int, int], u: float, style: str
) -> None:
    """Draws either:
      - An expressive 2D illustrated cartoon character/prop (Napoleon, Diplomat Ship, Helicopter, Rescue Boat, Citizen, Rainstorm)
      - Or a Cloud X Berry style vibrant rounded 3D-beveled tech service tile (AWS Lambda, S3, EC2, RDS, Kubernetes, Shield).
    """
    cx = cw / 2.0
    cy = ch * 0.39
    r = min(cw, ch) * 0.28

    # Shadow under tile
    draw.rounded_rectangle([cx - r + 4, cy - r + 6, cx + r + 4, cy + r + 6], radius=int(r * 0.36), fill=(0, 0, 0, 150))

    # Determine tile background color by archetype
    if any(k in low for k in ("lambda", "aws", "compute", "ec2", "function")):
        tile_bg = (234, 88, 12, 245)
        tile_border = (253, 186, 116, 255)
    elif any(k in low for k in ("route", "dns", "53")):
        tile_bg = (147, 51, 234, 245)
        tile_border = (216, 180, 254, 255)
    elif any(k in low for k in ("cloudfront", "cdn")):
        tile_bg = (168, 85, 247, 245)
        tile_border = (233, 213, 255, 255)
    elif any(k in low for k in ("api", "gateway")):
        tile_bg = (2, 132, 199, 245)
        tile_border = (125, 211, 252, 255)
    elif any(k in low for k in ("client", "laptop", "browser", "terminal", "device")) or (
        any(k in low for k in ("user", "citizen", "person", "creator", "team")) and style in ("clean-technical", "dark-neon")
    ):
        tile_bg = (15, 23, 42, 245)
        tile_border = (56, 189, 248, 255)
    elif any(k in low for k in ("s3", "storage", "bucket", "green", "profit", "cash", "dollar", "money", "growth")):
        tile_bg = (22, 163, 74, 245)
        tile_border = (134, 239, 172, 255)
    elif any(k in low for k in ("rds", "database", "sql", "kubernetes", "docker", "container", "river", "water", "rain", "monsoon", "koshi", "bagmati")):
        tile_bg = (37, 99, 235, 245)
        tile_border = (147, 197, 253, 255)
    elif any(k in low for k in ("warn", "alert", "danger", "flood", "siren", "iam", "security", "shield", "rescue", "helicopter", "emergency")):
        tile_bg = (220, 38, 38, 245)
        tile_border = (252, 165, 165, 255)
    else:
        tile_bg = (30, 41, 59, 245)
        tile_border = accent

    draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=int(r * 0.36), fill=tile_bg, outline=tile_border, width=max(3, int(3.5 * u)))
    # Top glossy highlight inside tile
    draw.rounded_rectangle([cx - r + 5, cy - r + 5, cx + r - 5, cy - r * 0.15], radius=int(r * 0.28), fill=(255, 255, 255, 32))

    # Draw crisp 2D cartoon illustration or vector icon inside [cx - r, cy - r, cx + r, cy + r]
    c_detected = detect_country(low)
    if c_detected and any(k in low for k in ("flag", "nepal", "india", "country", "nation", "border", "kathmandu", "delhi")):
        # Authentic National Flag Badge
        if c_detected == "nepal":
            fw, fh = r * 1.15, r * 1.35
            draw_country_flag(draw, "nepal", cx - fw / 2, cy - fh / 2, fw, fh)
        elif c_detected == "india":
            fw, fh = r * 1.45, r * 1.05
            draw_country_flag(draw, "india", cx - fw / 2, cy - fh / 2, fw, fh)
        else:
            fw, fh = r * 1.40, r * 1.05
            draw_country_flag(draw, c_detected, cx - fw / 2, cy - fh / 2, fw, fh)

    elif any(k in low for k in ("treaty", "scroll", "agreement", "pact")):
        # Golden Historical Treaty Scroll with Red Wax Seal
        sw, sh = r * 1.25, r * 1.20
        sx0, sy0 = cx - sw / 2, cy - sh / 2
        draw.polygon([(sx0, sy0), (sx0 + sw, sy0), (sx0 + sw * 0.90, sy0 + sh), (sx0 + sw * 0.10, sy0 + sh)],
                     fill=(254, 243, 199, 255), outline=(217, 119, 6, 255), width=max(2, int(2.5 * u)))
        # Text script lines on parchment
        for dy in (-sh * 0.22, -sh * 0.05, sh * 0.12):
            draw.line([(cx - sw * 0.30, cy + dy), (cx + sw * 0.30, cy + dy)], fill=(180, 83, 9, 220), width=max(2, int(2.5 * u)))
        # Red royal wax seal in bottom corner
        draw.ellipse([cx + sw * 0.12, cy + sh * 0.18, cx + sw * 0.38, cy + sh * 0.44], fill=(220, 38, 38, 255), outline=(251, 191, 36, 255), width=2)

    elif any(k in low for k in ("himalaya", "everest", "mountain", "peak", "range")):
        # Majestic Snow-Capped Alpine Mountain Peaks
        # Back peak (Everest)
        draw.polygon([(cx - r * 0.70, cy + r * 0.50), (cx - r * 0.10, cy - r * 0.60), (cx + r * 0.50, cy + r * 0.50)], fill=(30, 58, 138, 240))
        draw.polygon([(cx - r * 0.10, cy - r * 0.60), (cx - r * 0.28, cy - r * 0.22), (cx + r * 0.08, cy - r * 0.22)], fill=(255, 255, 255, 255))
        # Front peak (Kanchenjunga)
        draw.polygon([(cx - r * 0.20, cy + r * 0.50), (cx + r * 0.30, cy - r * 0.40), (cx + r * 0.75, cy + r * 0.50)], fill=(14, 116, 144, 240))
        draw.polygon([(cx + r * 0.30, cy - r * 0.40), (cx + r * 0.15, cy - r * 0.12), (cx + r * 0.45, cy - r * 0.12)], fill=(255, 255, 255, 255))
        # Ice glint
        draw.line([(cx - r * 0.65, cy + r * 0.50), (cx + r * 0.70, cy + r * 0.50)], fill=(56, 189, 248, 255), width=max(2, int(3 * u)))

    elif any(k in low for k in ("river", "koshi", "bagmati", "rapids", "wave")):
        # Flowing Himalayan River Currents with Water Droplets
        for dy, col in ((-r * 0.25, (186, 230, 253, 255)), (0.0, (56, 189, 248, 255)), (r * 0.25, (2, 132, 199, 255))):
            pts = [(cx - r * 0.65, cy + dy), (cx - r * 0.20, cy + dy - r * 0.15), (cx + r * 0.20, cy + dy + r * 0.15), (cx + r * 0.65, cy + dy)]
            draw.line(pts, fill=col, width=max(3, int(4 * u)), joint="curve")
        draw.ellipse([cx - r * 0.15, cy - r * 0.45, cx - r * 0.05, cy - r * 0.35], fill=(224, 242, 254, 255))
        draw.ellipse([cx + r * 0.25, cy - r * 0.35, cx + r * 0.35, cy - r * 0.25], fill=(224, 242, 254, 255))

    elif any(k in low for k in ("temple", "pagoda", "sacred", "shrine", "pilgrim")):
        # 3-Tier Nepalese Pagoda Temple with Golden Finial
        # Lower roof
        draw.polygon([(cx - r * 0.65, cy + r * 0.20), (cx, cy - r * 0.05), (cx + r * 0.65, cy + r * 0.20)], fill=(217, 119, 6, 255), outline=(251, 191, 36, 255), width=2)
        # Middle roof
        draw.polygon([(cx - r * 0.48, cy - r * 0.10), (cx, cy - r * 0.30), (cx + r * 0.48, cy - r * 0.10)], fill=(180, 83, 9, 255), outline=(251, 191, 36, 255), width=2)
        # Top roof & spire
        draw.polygon([(cx - r * 0.30, cy - r * 0.35), (cx, cy - r * 0.52), (cx + r * 0.30, cy - r * 0.35)], fill=(146, 64, 14, 255), outline=(251, 191, 36, 255), width=2)
        draw.line([(cx, cy - r * 0.52), (cx, cy - r * 0.72)], fill=(251, 191, 36, 255), width=max(3, int(4 * u)))
        draw.ellipse([cx - r * 0.08, cy - r * 0.78, cx + r * 0.08, cy - r * 0.64], fill=(251, 191, 36, 255))
        # Pillars
        draw.rectangle([cx - r * 0.35, cy + r * 0.20, cx + r * 0.35, cy + r * 0.52], fill=(69, 26, 3, 255))
        draw.rectangle([cx - r * 0.12, cy + r * 0.28, cx + r * 0.12, cy + r * 0.52], fill=(251, 191, 36, 255))

    elif any(k in low for k in ("truck", "trade", "cargo", "freight", "transport", "commerce")):
        # Commercial Trade Cargo Truck
        # Cargo container
        draw.rounded_rectangle([cx - r * 0.65, cy - r * 0.30, cx + r * 0.15, cy + r * 0.30], radius=4, fill=(16, 185, 129, 255), outline=(255, 255, 255, 255), width=2)
        draw.line([(cx - r * 0.40, cy - r * 0.30), (cx - r * 0.40, cy + r * 0.30)], fill=(5, 150, 105, 255), width=2)
        draw.line([(cx - r * 0.15, cy - r * 0.30), (cx - r * 0.15, cy + r * 0.30)], fill=(5, 150, 105, 255), width=2)
        # Cab
        draw.polygon([(cx + r * 0.15, cy - r * 0.30), (cx + r * 0.50, cy - r * 0.15), (cx + r * 0.62, cy + r * 0.05), (cx + r * 0.62, cy + r * 0.30), (cx + r * 0.15, cy + r * 0.30)],
                     fill=(245, 158, 11, 255), outline=(255, 255, 255, 255), width=2)
        # Windshield
        draw.polygon([(cx + r * 0.20, cy - r * 0.24), (cx + r * 0.46, cy - r * 0.12), (cx + r * 0.52, cy + r * 0.02), (cx + r * 0.20, cy + r * 0.02)], fill=(186, 230, 253, 255))
        # Wheels
        for wx in (-r * 0.45, -r * 0.15, r * 0.42):
            draw.ellipse([cx + wx - r * 0.14, cy + r * 0.24, cx + wx + r * 0.14, cy + r * 0.52], fill=(15, 23, 42, 255), outline=(203, 213, 225, 255), width=2)

    elif any(k in low for k in ("hydropower", "clean energy", "turbine", "energy", "clean")):
        # Clean Energy Water Turbine & Electricity Spark
        draw.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], fill=(5, 150, 105, 240), outline=(52, 211, 153, 255), width=max(3, int(4 * u)))
        # Turbine curved blades
        for i in range(6):
            ang = math.radians(i * 60)
            bx0 = cx + r * 0.18 * math.cos(ang)
            by0 = cy + r * 0.18 * math.sin(ang)
            bx1 = cx + r * 0.48 * math.cos(ang + 0.35)
            by1 = cy + r * 0.48 * math.sin(ang + 0.35)
            draw.line([(bx0, by0), (bx1, by1)], fill=(209, 250, 229, 255), width=max(2, int(3 * u)))
        # Center golden electric bolt
        draw.polygon([(cx - r * 0.12, cy - r * 0.38), (cx + r * 0.18, cy - r * 0.08), (cx - r * 0.02, cy - r * 0.05),
                      (cx + r * 0.10, cy + r * 0.38), (cx - r * 0.18, cy + r * 0.08), (cx + r * 0.02, cy + r * 0.05)],
                     fill=(250, 204, 21, 255))

    elif any(k in low for k in ("scale", "balance", "diplomat", "respect", "justice")):
        # Golden Diplomatic Balance Scale
        # Central pillar & fulcrum
        draw.line([(cx, cy - r * 0.55), (cx, cy + r * 0.52)], fill=(251, 191, 36, 255), width=max(3, int(4 * u)))
        draw.line([(cx - r * 0.32, cy + r * 0.52), (cx + r * 0.32, cy + r * 0.52)], fill=(251, 191, 36, 255), width=max(3, int(4 * u)))
        # Horizontal crossbeam
        draw.line([(cx - r * 0.55, cy - r * 0.35), (cx + r * 0.55, cy - r * 0.35)], fill=(251, 191, 36, 255), width=max(3, int(4 * u)))
        # Left pan (Kathmandu)
        draw.line([(cx - r * 0.55, cy - r * 0.35), (cx - r * 0.65, cy)], fill=(203, 213, 225, 230), width=1)
        draw.line([(cx - r * 0.55, cy - r * 0.35), (cx - r * 0.45, cy)], fill=(203, 213, 225, 230), width=1)
        draw.arc([cx - r * 0.70, cy - r * 0.10, cx - r * 0.40, cy + r * 0.20], 0, 180, fill=(251, 191, 36, 255), width=3)
        # Right pan (New Delhi)
        draw.line([(cx + r * 0.55, cy - r * 0.35), (cx + r * 0.45, cy)], fill=(203, 213, 225, 230), width=1)
        draw.line([(cx + r * 0.55, cy - r * 0.35), (cx + r * 0.65, cy)], fill=(203, 213, 225, 230), width=1)
        draw.arc([cx + r * 0.40, cy - r * 0.10, cx + r * 0.70, cy + r * 0.20], 0, 180, fill=(251, 191, 36, 255), width=3)

    elif any(k in low for k in ("timeline", "marker", "year", "1950", "2015", "2026")):
        # Chronological Milestone Seal
        yr = "1950" if "1950" in low else ("2015" if "2015" in low else ("2026" if "2026" in low else "YEAR"))
        badge_bg = (217, 119, 6, 255) if yr == "1950" else ((220, 38, 38, 255) if yr == "2015" else (5, 150, 105, 255))
        draw.ellipse([cx - r * 0.60, cy - r * 0.60, cx + r * 0.60, cy + r * 0.60], fill=badge_bg, outline=(255, 255, 255, 255), width=max(3, int(3.5 * u)))
        f_yr = _font(int(r * 0.45), bold=True)
        tb_yr = draw.textbbox((0, 0), yr, font=f_yr)
        draw.text((cx - (tb_yr[2] - tb_yr[0]) / 2, cy - (tb_yr[3] - tb_yr[1]) / 2), yr, fill=(255, 255, 255, 255), font=f_yr)

    elif any(k in low for k in ("helicopter", "chopper", "airlift")):
        # 2D Illustrated Rescue Helicopter
        draw.line([(cx - r * 0.72, cy - r * 0.52), (cx + r * 0.72, cy - r * 0.52)], fill=(255, 255, 255, 255), width=max(3, int(4 * u)))
        draw.line([(cx, cy - r * 0.52), (cx, cy - r * 0.25)], fill=(255, 255, 255, 255), width=max(3, int(3 * u)))
        draw.line([(cx - r * 0.75, cy), (cx - r * 0.2, cy)], fill=(254, 240, 138, 255), width=max(4, int(5 * u)))
        draw.ellipse([cx - r * 0.35, cy - r * 0.28, cx + r * 0.52, cy + r * 0.28], fill=(254, 240, 138, 255), outline=(15, 23, 42, 255), width=2)
        draw.pieslice([cx + r * 0.02, cy - r * 0.24, cx + r * 0.48, cy + r * 0.20], -70, 70, fill=(56, 189, 248, 255))
        draw.line([(cx - r * 0.25, cy + r * 0.45), (cx + r * 0.45, cy + r * 0.45)], fill=(255, 255, 255, 255), width=max(3, int(3 * u)))

    elif any(k in low for k in ("raft", "boat", "ship", "sail", "navy")):
        # 2D Illustrated Sailing Ship / Rescue Raft on waves
        draw.polygon([(cx - r * 0.62, cy + r * 0.12), (cx + r * 0.62, cy + r * 0.12), (cx + r * 0.42, cy + r * 0.48), (cx - r * 0.42, cy + r * 0.48)],
                     fill=(251, 146, 60, 255), outline=(255, 255, 255, 255), width=2)
        draw.polygon([(cx, cy - r * 0.62), (cx, cy + r * 0.05), (cx + r * 0.48, cy + r * 0.05)], fill=(255, 255, 255, 255))
        draw.polygon([(cx - r * 0.06, cy - r * 0.52), (cx - r * 0.06, cy + r * 0.05), (cx - r * 0.44, cy + r * 0.05)], fill=(226, 232, 240, 240))
        draw.line([(cx - r * 0.65, cy + r * 0.58), (cx + r * 0.65, cy + r * 0.58)], fill=(125, 211, 252, 255), width=max(3, int(4 * u)))

    elif any(k in low for k in ("client", "laptop", "browser", "terminal", "device")) or (
        any(k in low for k in ("user", "citizen", "person", "creator", "team")) and style in ("clean-technical", "dark-neon")
    ):
        # Sleek Modern Technical Client Terminal / Laptop & Browser (replaces cartoon in technical scenes)
        # Screen frame
        draw.rounded_rectangle([cx - r * 0.65, cy - r * 0.48, cx + r * 0.65, cy + r * 0.28], radius=int(6 * u), fill=(15, 23, 42, 255), outline=tile_border, width=2)
        # Inner display
        draw.rectangle([cx - r * 0.55, cy - r * 0.38, cx + r * 0.55, cy + r * 0.20], fill=(2, 6, 23, 255))
        # Browser header dots (red, yellow, green)
        draw.ellipse([cx - r * 0.46, cy - r * 0.32, cx - r * 0.38, cy - r * 0.24], fill=(239, 68, 68, 255))
        draw.ellipse([cx - r * 0.32, cy - r * 0.32, cx - r * 0.24, cy - r * 0.24], fill=(245, 158, 11, 255))
        draw.ellipse([cx - r * 0.18, cy - r * 0.32, cx - r * 0.10, cy - r * 0.24], fill=(34, 197, 94, 255))
        # Terminal prompt text >_ HTTP
        f_term = _font(int(r * 0.30), bold=True)
        draw.text((cx - r * 0.40, cy - r * 0.10), ">_ HTTP", fill=(56, 189, 248, 255), font=f_term)
        # Laptop base stand
        draw.polygon([(cx - r * 0.40, cy + r * 0.28), (cx + r * 0.40, cy + r * 0.28), (cx + r * 0.55, cy + r * 0.48), (cx - r * 0.55, cy + r * 0.48)], fill=(51, 65, 85, 255))
        draw.rectangle([cx - r * 0.15, cy + r * 0.44, cx + r * 0.15, cy + r * 0.48], fill=(148, 163, 184, 255))

    elif any(k in low for k in ("napoleon", "emperor", "general", "diplomat", "jefferson", "citizen", "person", "people", "creator", "user", "team", "crew")):
        # 2D Illustrated Cartoon Character (Oversimplified / Louisiana Deal style head + hat + torso)
        # Torso / coat
        coat_color = (29, 78, 216, 255) if "napoleon" in low or "diplomat" in low else (249, 115, 22, 255)
        draw.pieslice([cx - r * 0.52, cy + r * 0.05, cx + r * 0.52, cy + r * 0.95], 180, 360, fill=coat_color, outline=(255, 255, 255, 255), width=2)
        # Head
        hr = r * 0.30
        draw.ellipse([cx - hr, cy - r * 0.42, cx + hr, cy + r * 0.18], fill=(254, 215, 170, 255), outline=(15, 23, 42, 255), width=2)
        # Expressive eyes
        draw.ellipse([cx - hr * 0.45, cy - r * 0.20, cx - hr * 0.20, cy - r * 0.05], fill=(15, 23, 42, 255))
        draw.ellipse([cx + hr * 0.20, cy - r * 0.20, cx + hr * 0.45, cy - r * 0.05], fill=(15, 23, 42, 255))
        # Bicorn hat or rescue helmet
        draw.polygon([(cx - r * 0.56, cy - r * 0.34), (cx, cy - r * 0.72), (cx + r * 0.56, cy - r * 0.34)],
                     fill=(15, 23, 42, 255) if "napoleon" in low else (250, 204, 21, 255), outline=(251, 191, 36, 255), width=2)

    elif any(k in low for k in ("route", "dns", "53")):
        # Crisp Route 53 Globe with Lat/Lon & Routing Arrows
        draw.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], outline=(255, 255, 255, 255), width=max(2, int(2.5 * u)))
        draw.line([(cx - r * 0.55, cy), (cx + r * 0.55, cy)], fill=(255, 255, 255, 210), width=max(1, int(1.8 * u)))
        draw.line([(cx, cy - r * 0.55), (cx, cy + r * 0.55)], fill=(255, 255, 255, 210), width=max(1, int(1.8 * u)))
        draw.ellipse([cx - r * 0.28, cy - r * 0.55, cx + r * 0.28, cy + r * 0.55], outline=(255, 255, 255, 200), width=max(1, int(1.6 * u)))

    elif any(k in low for k in ("cloudfront", "cdn")):
        # CloudFront Edge Distribution Waves
        draw.arc([cx - r * 0.58, cy - r * 0.58, cx + r * 0.58, cy + r * 0.58], -45, 45, fill=(255, 255, 255, 255), width=max(2, int(2.5 * u)))
        draw.arc([cx - r * 0.36, cy - r * 0.36, cx + r * 0.36, cy + r * 0.36], -45, 45, fill=(255, 255, 255, 255), width=max(2, int(2.5 * u)))
        draw.ellipse([cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16], fill=(255, 255, 255, 255))
        draw.arc([cx - r * 0.36, cy - r * 0.36, cx + r * 0.36, cy + r * 0.36], 135, 225, fill=(255, 255, 255, 255), width=max(2, int(2.5 * u)))
        draw.arc([cx - r * 0.58, cy - r * 0.58, cx + r * 0.58, cy + r * 0.58], 135, 225, fill=(255, 255, 255, 255), width=max(2, int(2.5 * u)))

    elif any(k in low for k in ("api", "gateway")):
        # API Gateway Ingress Router
        draw.polygon([(cx - r * 0.52, cy + r * 0.45), (cx - r * 0.52, cy - r * 0.25), (cx, cy - r * 0.58), (cx + r * 0.52, cy - r * 0.25), (cx + r * 0.52, cy + r * 0.45)],
                     outline=(255, 255, 255, 255), width=max(2, int(2.5 * u)))
        draw.ellipse([cx - r * 0.18, cy - r * 0.08, cx + r * 0.18, cy + r * 0.28], fill=(255, 255, 255, 255))

    elif any(k in low for k in ("rain", "cloud", "monsoon", "storm", "deluge", "weather")):
        # 2D Cloudburst + Raindrops + Lightning
        draw.ellipse([cx - r * 0.62, cy - r * 0.38, cx - r * 0.05, cy + r * 0.12], fill=(241, 245, 249, 255))
        draw.ellipse([cx - r * 0.32, cy - r * 0.58, cx + r * 0.32, cy + r * 0.08], fill=(255, 255, 255, 255))
        draw.ellipse([cx + r * 0.05, cy - r * 0.35, cx + r * 0.62, cy + r * 0.12], fill=(226, 232, 240, 255))
        draw.rectangle([cx - r * 0.48, cy - r * 0.12, cx + r * 0.48, cy + r * 0.12], fill=(255, 255, 255, 255))
        for dx in (-0.36, 0.0, 0.36):
            draw.line([(cx + r * dx, cy + r * 0.22), (cx + r * (dx - 0.12), cy + r * 0.56)], fill=(56, 189, 248, 255), width=max(3, int(4 * u)))

    elif any(k in low for k in ("lambda", "serverless", "function")):
        # Crisp AWS Lambda λ Symbol
        f_lam = _font(int(r * 1.25), bold=True)
        tb = draw.textbbox((0, 0), "λ", font=f_lam)
        draw.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - r * 0.12), "λ", fill=(255, 255, 255, 255), font=f_lam)

    elif any(k in low for k in ("database", "rds", "sql", "s3", "storage", "bucket")):
        # 3-Tier Database / Storage Cylinder
        for dy in (-r * 0.34, 0.0, r * 0.34):
            draw.rounded_rectangle([cx - r * 0.52, cy + dy - r * 0.13, cx + r * 0.52, cy + dy + r * 0.13],
                                   radius=int(6 * u), fill=(255, 255, 255, 235), outline=(15, 23, 42, 255), width=2)
            draw.ellipse([cx - r * 0.38, cy + dy - r * 0.05, cx - r * 0.24, cy + dy + r * 0.05], fill=tile_bg)

    elif any(k in low for k in ("shield", "security", "iam", "auth", "firewall")):
        draw.polygon([
            (cx, cy - r * 0.58), (cx + r * 0.52, cy - r * 0.36), (cx + r * 0.44, cy + r * 0.18),
            (cx, cy + r * 0.62), (cx - r * 0.44, cy + r * 0.18), (cx - r * 0.52, cy - r * 0.36),
        ], fill=(255, 255, 255, 245), outline=(251, 191, 36, 255), width=max(2, int(3 * u)))

    elif any(k in low for k in ("warn", "alert", "danger", "risk", "siren")):
        draw.polygon([(cx, cy - r * 0.58), (cx - r * 0.58, cy + r * 0.48), (cx + r * 0.58, cy + r * 0.48)],
                     fill=(250, 204, 21, 255), outline=(255, 255, 255, 255), width=max(2, int(3 * u)))
        f_bang = _font(int(r * 0.85), bold=True)
        draw.text((cx - r * 0.12, cy - r * 0.25), "!", fill=(15, 23, 42, 255), font=f_bang)

    else:
        # Mountain / River / Tech Hexagon Crest
        draw.polygon([(cx - r * 0.62, cy + r * 0.42), (cx - r * 0.12, cy - r * 0.48), (cx + r * 0.38, cy + r * 0.42)], fill=(255, 255, 255, 240))
        draw.polygon([(cx - r * 0.05, cy + r * 0.42), (cx + r * 0.32, cy - r * 0.28), (cx + r * 0.65, cy + r * 0.42)], fill=(203, 213, 225, 230))
        draw.line([(cx - r * 0.55, cy + r * 0.54), (cx + r * 0.55, cy + r * 0.54)], fill=(56, 189, 248, 255), width=max(3, int(4 * u)))

    # Crisp label pill underneath the tile
    f_lbl = _font(int(18 * u), bold=True)
    lbl = (title or "ITEM").strip()[:26]
    tb = draw.textbbox((0, 0), lbl, font=f_lbl)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    pw = min(cw - 8, tw + int(28 * u))
    ph = th + int(16 * u)
    py0 = cy + r + int(10 * u)
    draw.rounded_rectangle([cx - pw / 2, py0, cx + pw / 2, py0 + ph], radius=int(ph / 2), fill=(15, 23, 42, 240), outline=tile_border, width=2)
    draw.text((cx - tw / 2, py0 + int(6 * u)), lbl, fill=(255, 255, 255, 255), font=f_lbl)


def _draw_title_card_sprite(
    draw: ImageDraw.ImageDraw, cw: int, ch: int, title: str, subtitle: str,
    accent: tuple[int, int, int, int], u: float, style: str
) -> None:
    """Draws a Vox Highlighter Banner or Cloud X Berry Gradient-Underlined Headline Card."""
    pad = int(10 * u)
    is_vox = style == "light-minimal"
    bg = (254, 240, 138, 248) if is_vox else (15, 23, 42, 240)
    fg = (15, 23, 42, 255) if is_vox else (255, 255, 255, 255)
    sub_fg = (51, 65, 85, 255) if is_vox else (251, 191, 36, 255)

    draw.rounded_rectangle([pad + 4, pad + 6, cw - pad + 4, ch - pad + 6], radius=int(14 * u), fill=(0, 0, 0, 145))
    draw.rounded_rectangle([pad, pad, cw - pad, ch - pad], radius=int(14 * u), fill=bg, outline=accent, width=max(2, int(3 * u)))
    draw.rounded_rectangle([pad, pad, pad + int(10 * u), ch - pad], radius=int(4 * u), fill=accent)

    f_t = _font(int(26 * u), bold=True)
    f_s = _font(int(17 * u), bold=False)
    t_str = (title or "").strip()[:38]
    s_str = (subtitle or "").strip()[:54]
    draw.text((pad + int(24 * u), pad + int(18 * u)), t_str, fill=fg, font=f_t)
    if s_str:
        draw.text((pad + int(24 * u), pad + int(56 * u)), s_str, fill=sub_fg, font=f_s)


def _draw_callout_sprite(
    draw: ImageDraw.ImageDraw, cw: int, ch: int, title: str, subtitle: str,
    accent: tuple[int, int, int, int], u: float, style: str
) -> None:
    """Draws a punchy single-purpose metric/stat callout pill or milestone badge."""
    pad = int(6 * u)
    is_vox = style == "light-minimal"
    is_warm = style == "warm-documentary"
    bg = (255, 255, 255, 252) if (is_vox or is_warm) else (17, 24, 39, 248)
    fg = (15, 23, 42, 255) if (is_vox or is_warm) else (255, 255, 255, 255)
    sub_fg = (71, 85, 105, 255) if (is_vox or is_warm) else (148, 163, 184, 255)

    # Outer drop shadow
    draw.rounded_rectangle([pad + 3, pad + 4, cw - pad + 3, ch - pad + 4], radius=int(10 * u), fill=(0, 0, 0, 130))
    # Body pill
    draw.rounded_rectangle([pad, pad, cw - pad, ch - pad], radius=int(10 * u), fill=bg, outline=accent, width=max(2, int(2.5 * u)))
    # Left accent bar
    draw.rounded_rectangle([pad, pad, pad + int(8 * u), ch - pad], radius=int(3 * u), fill=accent)

    f_t = _font(max(13, int(18 * u)), bold=True)
    t_str = (title or "").strip()[:36]
    s_str = (subtitle or "").strip()[:48]

    if "125" in t_str.lower() and "b" in t_str.lower():
        # DevZoneX Kinetic Stat Typography (Giant 125 in white + B in orange)
        draw.rounded_rectangle([pad, pad, cw - pad, ch - pad], radius=int(14 * u), fill=(10, 15, 26, 240), outline=(255, 110, 38, 220), width=max(2, int(2.5 * u)))
        f_huge = _font(max(26, int(38 * u)), bold=True)
        tb1 = draw.textbbox((0, 0), "125", font=f_huge)
        w1 = tb1[2] - tb1[0]
        tb2 = draw.textbbox((0, 0), "B", font=f_huge)
        w2 = tb2[2] - tb2[0]
        start_x = (cw - (w1 + w2)) / 2
        draw.text((start_x, pad + int(4 * u)), "125", fill=(255, 255, 255, 255), font=f_huge)
        draw.text((start_x + w1, pad + int(4 * u)), "B", fill=(255, 110, 38, 255), font=f_huge)
        f_sub = _font(max(9, int(11 * u)), bold=False)
        sub_txt = s_str or "BILLION PARAMETERS · MOE"
        draw.text((pad + int(24 * u), ch - pad - int(18 * u)), sub_txt, fill=(148, 163, 184, 255), font=f_sub)
        return

    if "gguf" in (t_str + s_str).lower():
        # GGUF Model File Card with progress bar and size badge
        draw.rounded_rectangle([pad, pad, cw - pad, ch - pad], radius=int(12 * u), fill=(13, 17, 28, 245), outline=(255, 110, 38, 220), width=max(2, int(2.5 * u)))
        draw.rounded_rectangle([pad + int(8 * u), pad + int(8 * u), pad + int(34 * u), ch - pad - int(8 * u)], radius=int(3 * u), fill=(255, 110, 38, 255))
        draw.text((pad + int(10 * u), pad + int(14 * u)), "GGUF", fill=(255, 255, 255, 255), font=_font(max(7, int(7.5 * u)), bold=True))
        f_mono = _font(max(9, int(11 * u)), bold=True)
        draw.text((pad + int(40 * u), pad + int(8 * u)), t_str[:32], fill=(241, 245, 249, 255), font=f_mono)
        draw.rounded_rectangle([pad + int(40 * u), pad + int(28 * u), cw - pad - int(76 * u), pad + int(33 * u)], radius=int(2 * u), fill=(255, 110, 38, 255))
        f_sz = _font(max(11, int(15 * u)), bold=True)
        draw.text((cw - pad - int(70 * u), pad + int(12 * u)), s_str or "56.8 GB", fill=(255, 255, 255, 255), font=f_sz)
        return

    if s_str:
        draw.text((pad + int(18 * u), pad + int(8 * u)), t_str, fill=fg, font=f_t)
        f_s = _font(max(10, int(12 * u)), bold=False)
        draw.text((pad + int(18 * u), pad + int(32 * u)), s_str, fill=sub_fg, font=f_s)
    else:
        tb = draw.textbbox((0, 0), t_str, font=f_t)
        th = tb[3] - tb[1]
        draw.text((pad + int(18 * u), (ch - th) / 2 - int(2 * u)), t_str, fill=fg, font=f_t)


def _draw_rich_card_sprite(
    draw: ImageDraw.ImageDraw, cw: int, ch: int, el, low: str,
    accent: tuple[int, int, int, int], u: float, style: str
) -> None:
    """Draws a premium 2-column Explainer Card with authentic vector icons, category headers, and structured bullet chips."""
    pad = int(8 * u)
    is_vox = style == "light-minimal"
    is_fin = style == "dark-neon" or el.kind == "chart_bar" or isinstance(el.props.get("value"), (int, float))
    is_warm = style == "warm-documentary"

    # 1. Resolve Archetype, Theme Colors, Default Subtitle, and Feature Bullet Chips
    c_detected = None
    for c in ("india", "nepal", "china", "bhutan", "bangladesh", "usa", "france"):
        if c in low:
            c_detected = c
            break

    if c_detected and any(k in low for k in ("utc", "time", "zone", "standard", "country", "nation", "meridian", "india", "nepal", "china")):
        if c_detected == "india":
            archetype = "india"
            header_color = (71, 85, 105, 255)
            border = (100, 116, 139, 255)
            default_sub = "Indian Standard Time (IST)"
            default_bullets = ["Meridian: 82.5° E (Mirzapur)", "Covers 1.4 Billion People"]
        elif c_detected == "nepal":
            archetype = "nepal"
            header_color = (217, 119, 6, 255)
            border = (251, 191, 36, 255)
            default_sub = "Nepal Time (NPT)"
            default_bullets = ["Meridian: 86.0° E (Gauri Shankar)", "+15 Min Offset from India"]
        elif c_detected == "china":
            archetype = "china"
            header_color = (185, 28, 28, 255)
            border = (248, 113, 113, 255)
            default_sub = "China Standard Time (CST)"
            default_bullets = ["Single National Time Zone", "Spans 5 Geographic Zones"]
        else:
            archetype = c_detected
            header_color = (30, 58, 138, 255)
            border = (96, 165, 250, 255)
            default_sub = f"{c_detected.title()} National Entity"
            default_bullets = ["Sovereign Territory", "Diplomatic Partner"]

    elif any(k in low for k in ("lambda", "serverless", "function")):
        archetype = "lambda"
        header_color = (234, 88, 12, 255)
        border = (253, 186, 116, 255)
        default_sub = "Serverless Compute"
        default_bullets = ["Sub-50ms Cold Starts", "Auto-scales to Zero"]

    elif any(k in low for k in ("s3", "storage", "bucket")):
        archetype = "s3"
        header_color = (16, 185, 129, 255)
        border = (134, 239, 172, 255)
        default_sub = "Object Storage Service"
        default_bullets = ["99.999999999% Durability", "Unlimited Scale & Storage"]

    elif any(k in low for k in ("route", "dns", "53")):
        archetype = "route53"
        header_color = (147, 51, 234, 255)
        border = (216, 180, 254, 255)
        default_sub = "Global DNS & Traffic Router"
        default_bullets = ["100% SLA Availability", "Latency-based Anycast"]

    elif any(k in low for k in ("cloudfront", "cdn", "edge")):
        archetype = "cloudfront"
        header_color = (168, 85, 247, 255)
        border = (233, 213, 255, 255)
        default_sub = "Content Delivery Network"
        default_bullets = ["300+ Global Edge Pops", "DDoS Shield Integration"]

    elif any(k in low for k in ("iam", "security", "auth", "role")):
        archetype = "iam"
        header_color = (220, 38, 38, 255)
        border = (252, 165, 165, 255)
        default_sub = "Identity & Access Management"
        default_bullets = ["Fine-grained RBAC Roles", "Zero-Trust Authorization"]

    elif any(k in low for k in ("api", "gateway", "rest", "ingress")):
        archetype = "apigateway"
        header_color = (2, 132, 199, 255)
        border = (125, 211, 252, 255)
        default_sub = "Managed API Ingress"
        default_bullets = ["REST & WebSocket Endpoints", "Built-in Rate Throttling"]

    elif any(k in low for k in ("rds", "database", "sql", "postgres", "mysql")):
        archetype = "rds"
        header_color = (37, 99, 235, 255)
        border = (147, 197, 253, 255)
        default_sub = "Managed Relational Database"
        default_bullets = ["Multi-AZ Fault Tolerance", "Automated Daily Backups"]

    elif any(k in low for k in ("ec2", "instance", "virtual server", "compute")):
        archetype = "ec2"
        header_color = (249, 115, 22, 255)  # AWS Orange
        border = (253, 186, 116, 255)
        default_sub = "Elastic Compute Cloud"
        default_bullets = ["On-Demand Virtual Machines", "Elastic Auto-Scaling"]

    elif any(k in low for k in ("datacenter", "data center", "facility", "hardware")):
        archetype = "datacenter"
        header_color = (71, 85, 105, 255)  # Slate Steel
        border = (148, 163, 184, 255)
        default_sub = "Tier-4 Physical Facility"
        default_bullets = ["Biometric Security & Cages", "Redundant Backup Power"]

    elif any(k in low for k in ("cli", "terminal", "command line", "bash")):
        archetype = "cli"
        header_color = (15, 23, 42, 255)  # Dark Terminal
        border = (34, 197, 94, 255)  # Terminal Green
        default_sub = "AWS Command Line Interface"
        default_bullets = ["Direct API Scripting", "CloudShell & Terminal Ready"]

    elif any(k in low for k in ("sdk", "code", "boto3", "api programmatic")):
        archetype = "sdk"
        header_color = (2, 132, 199, 255)  # Sky Cyan
        border = (125, 211, 252, 255)
        default_sub = "Software Development Kit"
        default_bullets = ["Python, JS, Java & Go", "Native API Abstraction"]

    elif any(k in low for k in ("outpost", "local zone", "hybrid", "on-prem")):
        archetype = "outpost"
        header_color = (13, 148, 136, 255)  # Teal
        border = (94, 234, 212, 255)
        default_sub = "Hybrid Edge Deployment"
        default_bullets = ["Sub-10ms Metro Latency", "Physical 42U Server Rack"]

    elif any(k in low for k in ("tekbay", "trainer", "architect", "certification", "saa-c03")):
        archetype = "tekbay"
        header_color = (234, 88, 12, 255)  # TekBay Orange
        border = (254, 215, 170, 255)
        default_sub = "AWS Certified SAA-C03"
        default_bullets = ["Lead Trainer: Om Thakur", "Enterprise DevOps & Cloud"]

    elif any(k in low for k in ("qwen", "125b", "moe", "gyro")):
        archetype = "qwen"
        header_color = (255, 110, 38, 255)  # DevZoneX Orange
        border = (254, 215, 170, 255)
        default_sub = "125B Parameters · Sparse MoE"
        default_bullets = ["Qwen3.8-Flash-Next (Gyro-S)", "Active Experts: 2 per Token"]

    elif any(k in low for k in ("strata", "inference engine")):
        archetype = "strata"
        header_color = (16, 185, 129, 255)  # Mint Emerald
        border = (167, 243, 208, 255)
        default_sub = "High-Throughput Inference Engine"
        default_bullets = ["Runs 125B on Free T4 GPUs", "Local & Cloud API Endpoints"]

    elif any(k in low for k in ("kaggle", "tesla", "t4", "free gpu")):
        archetype = "kaggle"
        header_color = (32, 190, 255, 255)  # Kaggle Cyan Blue
        border = (186, 230, 253, 255)
        default_sub = "Free Cloud GPU Environment"
        default_bullets = ["2x NVIDIA Tesla T4 (30 GB)", "30 Hours/Week Quota"]

    elif any(k in low for k in ("opencode", "ide", "agent")):
        archetype = "opencode"
        header_color = (139, 92, 246, 255)  # Neon Violet
        border = (221, 214, 254, 255)
        default_sub = "AI Coding Agent Environment"
        default_bullets = ["Connected via Secure API", "Zero Local GPU Needed"]

    elif any(k in low for k in ("tunnel", "cloudflare", "workflow")):
        archetype = "tunnel"
        header_color = (245, 158, 11, 255)  # Amber
        border = (253, 230, 138, 255)
        default_sub = "Authenticated HTTPS Tunnel"
        default_bullets = ["Cloudflare Quick Tunnel", "Zero Port Forwarding"]

    elif any(k in low for k in ("river", "koshi", "bagmati", "water")):
        archetype = "river"
        header_color = (2, 132, 199, 255)
        border = (56, 189, 248, 255)
        default_sub = "Himalayan Basins • Flows to Ganges"
        default_bullets = ["Originates in High Glaciers", "Key Irrigation Lifeline"]

    elif any(k in low for k in ("culture", "family", "temple", "bond", "sacred")):
        archetype = "culture"
        header_color = (217, 119, 6, 255)
        border = (251, 191, 36, 255)
        default_sub = "Kinship & Ancient Pilgrimages"
        default_bullets = ["Shared Temple Sanctuaries", "Generational Family Ties"]

    elif any(k in low for k in ("trade", "truck", "commerce", "economic", "market")):
        archetype = "trade"
        header_color = (5, 150, 105, 255)
        border = (52, 211, 153, 255)
        default_sub = "Open Commerce • Transit to Sea"
        default_bullets = ["Kolkata Port Access", "Vital Cross-border Goods"]

    elif "1950" in low or ("treaty" in low and "peace" in low):
        archetype = "treaty"
        header_color = (217, 119, 6, 255)
        border = (251, 191, 36, 255)
        default_sub = "Peace & Friendship Foundation"
        default_bullets = ["Free Movement of Citizens", "Equal National Treatment"]

    elif "2015" in low or "blockade" in low:
        archetype = "blockade"
        header_color = (220, 38, 38, 255)
        border = (248, 113, 113, 255)
        default_sub = "Border Blockade & Fuel Crisis"
        default_bullets = ["5-Month Transit Halt", "Severe Supply Shortages"]

    elif "2026" in low or "hydro" in low or "energy" in low:
        archetype = "energy"
        header_color = (5, 150, 105, 255)
        border = (52, 211, 153, 255)
        default_sub = "Clean Energy & Hydro Export"
        default_bullets = ["10,000 MW Target Export", "Regional Power Grid Link"]

    elif any(k in low for k in ("border", "checkpoint", "visa-free", "crossing")):
        archetype = "border"
        header_color = (220, 38, 38, 255)
        border = (248, 113, 113, 255)
        default_sub = "1,770 km Visa-Free Movement"
        default_bullets = ["Passport-free Travel", "Unfettered Citizen Transit"]

    elif el.kind == "timeline_marker":
        archetype = "timeline"
        header_color = (217, 119, 6, 255)
        border = (251, 191, 36, 255)
        yr = el.props.get("year")
        default_sub = f"Milestone Year {yr}" if yr else "Historical Turning Point"
        default_bullets = ["Strategic Realignment", "Key Bilateral Milestone"]

    else:
        archetype = "generic"
        if sum(accent[:3]) > 680:
            header_color = (30, 41, 59, 255)
            border = accent
        else:
            header_color = accent
            border = accent
        if is_vox or is_warm:
            default_sub = "Historical & Geographic Evidence"
            default_bullets = ["Archival Documentation", "Verified Primary Source"]
        else:
            default_sub = "Core Infrastructure Node"
            default_bullets = ["High-Throughput Engine", "Production-Grade Scalability"]

    # 2. Extract subtitle and bullets from el.props if provided
    s_raw = el.props.get("subtitle") or el.props.get("desc") or el.props.get("description")
    s_str = str(s_raw if s_raw is not None else default_sub).strip()[:42]

    bullets = el.props.get("bullets") or el.props.get("metrics") or el.props.get("points") or default_bullets
    if isinstance(bullets, str):
        bullets = [bullets]
    bullets = [str(b).strip()[:32] for b in bullets if str(b).strip()][:2]
    while len(bullets) < 2:
        bullets.append("Verified System Status")

    # 3. Card Base Styling
    bg = (255, 255, 255, 252) if (is_vox or is_warm) else ((10, 22, 18, 245) if is_fin else (17, 24, 39, 248))
    sub_fg = (30, 41, 59, 255) if (is_vox or is_warm) else ((0, 255, 102, 255) if is_fin else (241, 245, 249, 255))
    pill_bg = (226, 232, 240, 255) if (is_vox or is_warm) else (31, 41, 55, 255)
    pill_txt = (51, 65, 85, 255) if (is_vox or is_warm) else (156, 163, 175, 255)

    # Outer Drop Shadow
    draw.rounded_rectangle([pad + 3, pad + 5, cw - pad + 3, ch - pad + 5], radius=int(12 * u), fill=(0, 0, 0, 140))
    # Main Card Body
    draw.rounded_rectangle([pad, pad, cw - pad, ch - pad], radius=int(12 * u), fill=bg, outline=border, width=max(2, int(2.5 * u)))

    # Thematic Top Header Banner
    header_h = max(int(36 * u), int(ch * 0.24))
    draw.rounded_rectangle([pad, pad, cw - pad, pad + header_h], radius=int(12 * u), fill=header_color)
    draw.rectangle([pad, pad + header_h - int(8 * u), cw - pad, pad + header_h], fill=header_color)

    # Title in Header Banner
    f_t = _font(max(13, int(17 * u)), bold=True)
    t_str = (el.label or "CARD").strip().upper()[:28]
    draw.text((pad + int(14 * u), pad + int(8 * u)), t_str, fill=(255, 255, 255, 255), font=f_t)

    # 4. Body Area: Left Icon Disc
    body_h = ch - pad - header_h
    icx = pad + int(46 * u)
    icy = pad + header_h + int(body_h * 0.48)
    ir = min(int(34 * u), int(body_h * 0.38))

    disc_bg = (241, 245, 249, 255) if (is_vox or is_warm) else (30, 41, 59, 255)
    draw.ellipse([icx - ir, icy - ir, icx + ir, icy + ir], fill=disc_bg, outline=border, width=max(1, int(2 * u)))

    # Draw authentic vector icon graphic inside disc
    if archetype == "india":
        draw_country_flag(draw, "india", icx - int(22 * u), icy - int(15 * u), int(44 * u), int(30 * u))
    elif archetype == "nepal":
        draw_country_flag(draw, "nepal", icx - int(18 * u), icy - int(22 * u), int(36 * u), int(44 * u))
    elif archetype == "china":
        draw_country_flag(draw, "china", icx - int(22 * u), icy - int(15 * u), int(44 * u), int(30 * u))
    elif archetype == "lambda":
        f_lam = _font(int(ir * 1.15), bold=True)
        tb = draw.textbbox((0, 0), "λ", font=f_lam)
        draw.text((icx - (tb[2] - tb[0]) / 2, icy - (tb[3] - tb[1]) / 2 - int(2 * u)), "λ", fill=(249, 115, 22, 255), font=f_lam)
    elif archetype == "s3":
        for dy in (-int(9 * u), 0, int(9 * u)):
            draw.rounded_rectangle([icx - int(17 * u), icy + dy - int(4 * u), icx + int(17 * u), icy + dy + int(4 * u)],
                                   radius=int(3 * u), fill=(16, 185, 129, 255))
    elif archetype == "rds":
        for dy in (-int(9 * u), 0, int(9 * u)):
            draw.rounded_rectangle([icx - int(17 * u), icy + dy - int(4 * u), icx + int(17 * u), icy + dy + int(4 * u)],
                                   radius=int(3 * u), fill=(59, 130, 246, 255))
            draw.ellipse([icx - int(13 * u), icy + dy - int(2 * u), icx - int(9 * u), icy + dy + int(2 * u)], fill=(34, 197, 94, 255))
    elif archetype == "route53":
        draw.ellipse([icx - int(16 * u), icy - int(16 * u), icx + int(16 * u), icy + int(16 * u)], outline=(168, 85, 247, 255), width=max(2, int(2.2 * u)))
        draw.line([(icx - int(16 * u), icy), (icx + int(16 * u), icy)], fill=(168, 85, 247, 255), width=max(1, int(1.6 * u)))
        draw.line([(icx, icy - int(16 * u)), (icx, icy + int(16 * u))], fill=(168, 85, 247, 255), width=max(1, int(1.6 * u)))
        draw.ellipse([icx - int(8 * u), icy - int(16 * u), icx + int(8 * u), icy + int(16 * u)], outline=(168, 85, 247, 255), width=max(1, int(1.6 * u)))
    elif archetype == "cloudfront":
        draw.arc([icx - int(17 * u), icy - int(17 * u), icx + int(17 * u), icy + int(17 * u)], -45, 45, fill=(168, 85, 247, 255), width=max(2, int(2.2 * u)))
        draw.arc([icx - int(10 * u), icy - int(10 * u), icx + int(10 * u), icy + int(10 * u)], -45, 45, fill=(168, 85, 247, 255), width=max(2, int(2.2 * u)))
        draw.ellipse([icx - int(4 * u), icy - int(4 * u), icx + int(4 * u), icy + int(4 * u)], fill=(255, 255, 255, 255))
        draw.arc([icx - int(10 * u), icy - int(10 * u), icx + int(10 * u), icy + int(10 * u)], 135, 225, fill=(168, 85, 247, 255), width=max(2, int(2.2 * u)))
        draw.arc([icx - int(17 * u), icy - int(17 * u), icx + int(17 * u), icy + int(17 * u)], 135, 225, fill=(168, 85, 247, 255), width=max(2, int(2.2 * u)))
    elif archetype == "iam":
        draw.polygon([
            (icx, icy - int(16 * u)), (icx + int(14 * u), icy - int(8 * u)), (icx + int(11 * u), icy + int(6 * u)),
            (icx, icy + int(17 * u)), (icx - int(11 * u), icy + int(6 * u)), (icx - int(14 * u), icy - int(8 * u)),
        ], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=max(1, int(1.8 * u)))
        draw.ellipse([icx - int(3 * u), icy - int(5 * u), icx + int(3 * u), icy + int(1 * u)], fill=(255, 255, 255, 255))
        draw.line([(icx, icy + int(1 * u)), (icx, icy + int(9 * u))], fill=(255, 255, 255, 255), width=max(1, int(2 * u)))
    elif archetype == "apigateway":
        draw.polygon([(icx - int(15 * u), icy + int(12 * u)), (icx - int(15 * u), icy - int(6 * u)), (icx, icy - int(16 * u)), (icx + int(15 * u), icy - int(6 * u)), (icx + int(15 * u), icy + int(12 * u))],
                     outline=(2, 132, 199, 255), width=max(2, int(2.2 * u)))
        draw.ellipse([icx - int(5 * u), icy - int(2 * u), icx + int(5 * u), icy + int(8 * u)], fill=(56, 189, 248, 255))
    elif archetype == "river":
        for dy in (-int(7 * u), 0, int(7 * u)):
            draw.line([(icx - int(16 * u), icy + dy - int(2.5 * u)), (icx - int(5 * u), icy + dy + int(2.5 * u)), (icx + int(5 * u), icy + dy - int(2.5 * u)), (icx + int(16 * u), icy + dy + int(2.5 * u))],
                      fill=(2, 132, 199, 255), width=max(2, int(2.5 * u)))
    elif archetype == "culture":
        draw.polygon([(icx, icy - int(16 * u)), (icx + int(14 * u), icy - int(5 * u)), (icx - int(14 * u), icy - int(5 * u))], fill=(217, 119, 6, 255))
        draw.rectangle([icx - int(9 * u), icy - int(5 * u), icx + int(9 * u), icy + int(14 * u)], fill=(251, 191, 36, 255))
        draw.rectangle([icx - int(3 * u), icy + int(2 * u), icx + int(3 * u), icy + int(14 * u)], fill=(15, 23, 42, 255))
    elif archetype == "trade":
        draw.rectangle([icx - int(16 * u), icy - int(9 * u), icx + int(5 * u), icy + int(7 * u)], fill=(5, 150, 105, 255))
        draw.polygon([(icx + int(5 * u), icy - int(4 * u)), (icx + int(15 * u), icy), (icx + int(15 * u), icy + int(7 * u)), (icx + int(5 * u), icy + int(7 * u))], fill=(16, 185, 129, 255))
        draw.ellipse([icx - int(11 * u), icy + int(5 * u), icx - int(5 * u), icy + int(12 * u)], fill=(15, 23, 42, 255))
        draw.ellipse([icx + int(5 * u), icy + int(5 * u), icx + int(11 * u), icy + int(12 * u)], fill=(15, 23, 42, 255))
    elif archetype == "treaty":
        draw.rounded_rectangle([icx - int(12 * u), icy - int(16 * u), icx + int(12 * u), icy + int(16 * u)], radius=int(3 * u), fill=(254, 240, 138, 255), outline=(217, 119, 6, 255), width=2)
        draw.line([(icx - int(7 * u), icy - int(8 * u)), (icx + int(7 * u), icy - int(8 * u))], fill=(180, 83, 9, 255), width=1)
        draw.line([(icx - int(7 * u), icy - int(3 * u)), (icx + int(7 * u), icy - int(3 * u))], fill=(180, 83, 9, 255), width=1)
        draw.line([(icx - int(7 * u), icy + int(2 * u)), (icx + int(3 * u), icy + int(2 * u))], fill=(180, 83, 9, 255), width=1)
        draw.ellipse([icx - int(3 * u), icy + int(7 * u), icx + int(3 * u), icy + int(13 * u)], fill=(220, 38, 38, 255))
    elif archetype == "energy":
        draw.polygon([(icx, icy - int(16 * u)), (icx - int(10 * u), icy), (icx, icy), (icx - int(5 * u), icy + int(16 * u)), (icx + int(10 * u), icy - int(2 * u)), (icx + int(2 * u), icy - int(2 * u))],
                     fill=(250, 204, 21, 255), outline=(217, 119, 6, 255), width=1)
    elif archetype == "qwen":
        # 7-fold polygon AI neural node in DevZoneX orange
        pts = [
            (icx, icy - int(16 * u)), (icx + int(12 * u), icy - int(7 * u)),
            (icx + int(15 * u), icy + int(6 * u)), (icx + int(6 * u), icy + int(16 * u)),
            (icx - int(6 * u), icy + int(16 * u)), (icx - int(15 * u), icy + int(6 * u)),
            (icx - int(12 * u), icy - int(7 * u))
        ]
        draw.polygon(pts, fill=(255, 110, 38, 255), outline=(255, 255, 255, 240), width=max(1, int(1.8 * u)))
        draw.ellipse([icx - int(5 * u), icy - int(5 * u), icx + int(5 * u), icy + int(5 * u)], fill=(255, 255, 255, 255))
    elif archetype == "strata":
        # 3 horizontal strata layers in vibrant mint emerald
        for dy, col in ((-int(8 * u), (52, 211, 153, 255)), (0, (16, 185, 129, 255)), (int(8 * u), (5, 150, 105, 255))):
            draw.rounded_rectangle([icx - int(16 * u), icy + dy - int(3 * u), icx + int(16 * u), icy + dy + int(3 * u)], radius=int(2 * u), fill=col)
    elif archetype == "kaggle":
        # Stylized Kaggle K vector with cyan and mint bars
        draw.rectangle([icx - int(14 * u), icy - int(15 * u), icx - int(8 * u), icy + int(15 * u)], fill=(32, 190, 255, 255))
        draw.polygon([(icx - int(7 * u), icy), (icx + int(13 * u), icy - int(15 * u)), (icx + int(7 * u), icy - int(15 * u)), (icx - int(7 * u), icy - int(5 * u))], fill=(32, 190, 255, 255))
        draw.polygon([(icx - int(7 * u), icy), (icx + int(14 * u), icy + int(15 * u)), (icx + int(8 * u), icy + int(15 * u)), (icx - int(7 * u), icy + int(5 * u))], fill=(46, 229, 157, 255))
    elif archetype == "opencode":
        # Terminal window mockup with violet prompt
        draw.rounded_rectangle([icx - int(16 * u), icy - int(14 * u), icx + int(16 * u), icy + int(14 * u)], radius=int(3 * u), fill=(15, 23, 42, 255), outline=(139, 92, 246, 255), width=max(1, int(1.8 * u)))
        draw.ellipse([icx - int(12 * u), icy - int(9 * u), icx - int(9 * u), icy - int(6 * u)], fill=(239, 68, 68, 255))
        draw.ellipse([icx - int(7 * u), icy - int(9 * u), icx - int(4 * u), icy - int(6 * u)], fill=(234, 179, 8, 255))
        draw.text((icx - int(11 * u), icy - int(3 * u)), ">_", fill=(196, 181, 253, 255), font=_font(max(9, int(10 * u)), bold=True))
    elif archetype == "tunnel":
        # Cloudflare cloud + lock badge
        draw.ellipse([icx - int(14 * u), icy - int(5 * u), icx, icy + int(8 * u)], fill=(245, 158, 11, 255))
        draw.ellipse([icx - int(6 * u), icy - int(12 * u), icx + int(10 * u), icy + int(6 * u)], fill=(245, 158, 11, 255))
        draw.ellipse([icx + int(4 * u), icy - int(5 * u), icx + int(15 * u), icy + int(8 * u)], fill=(245, 158, 11, 255))
        draw.rounded_rectangle([icx - int(4 * u), icy + int(2 * u), icx + int(4 * u), icy + int(10 * u)], radius=int(2 * u), fill=(255, 255, 255, 255))
        draw.arc([icx - int(3 * u), icy - int(2 * u), icx + int(3 * u), icy + int(3 * u)], 180, 0, fill=(255, 255, 255, 255), width=max(1, int(1.5 * u)))
    elif archetype == "ec2":
        # AWS EC2 compute box with dual CPU cores
        draw.rounded_rectangle([icx - int(15 * u), icy - int(13 * u), icx + int(15 * u), icy + int(13 * u)], radius=int(3 * u), fill=(249, 115, 22, 255))
        draw.rounded_rectangle([icx - int(10 * u), icy - int(8 * u), icx - int(2 * u), icy + int(8 * u)], radius=int(2 * u), fill=(255, 255, 255, 255))
        draw.rounded_rectangle([icx + int(2 * u), icy - int(8 * u), icx + int(10 * u), icy + int(8 * u)], radius=int(2 * u), fill=(255, 255, 255, 255))
        for pin_y in (-int(6 * u), 0, int(6 * u)):
            draw.line([(icx - int(17 * u), icy + pin_y), (icx - int(15 * u), icy + pin_y)], fill=(253, 186, 116, 255), width=2)
            draw.line([(icx + int(15 * u), icy + pin_y), (icx + int(17 * u), icy + pin_y)], fill=(253, 186, 116, 255), width=2)
    elif archetype == "datacenter":
        # Server rack tower with LED indicator lights
        draw.rounded_rectangle([icx - int(13 * u), icy - int(16 * u), icx + int(13 * u), icy + int(16 * u)], radius=int(3 * u), fill=(30, 41, 59, 255), outline=(148, 163, 184, 255), width=max(1, int(1.8 * u)))
        for dy in (-int(9 * u), -int(3 * u), int(3 * u), int(9 * u)):
            draw.line([(icx - int(9 * u), icy + dy), (icx + int(4 * u), icy + dy)], fill=(100, 116, 139, 255), width=max(1, int(1.5 * u)))
            draw.ellipse([icx + int(7 * u), icy + dy - int(1.5 * u), icx + int(10 * u), icy + dy + int(1.5 * u)], fill=(34, 197, 94, 255))
    elif archetype == "cli":
        # Dark terminal with green command prompt
        draw.rounded_rectangle([icx - int(15 * u), icy - int(13 * u), icx + int(15 * u), icy + int(13 * u)], radius=int(3 * u), fill=(15, 23, 42, 255), outline=(34, 197, 94, 255), width=max(1, int(1.8 * u)))
        draw.text((icx - int(11 * u), icy - int(8 * u)), "$ aws", fill=(34, 197, 94, 255), font=_font(max(8, int(8.5 * u)), bold=True))
        draw.rectangle([icx - int(11 * u), icy + int(3 * u), icx + int(10 * u), icy + int(5 * u)], fill=(148, 163, 184, 255))
    elif archetype == "sdk":
        # Code brackets { } in vibrant cyan
        draw.text((icx - int(12 * u), icy - int(12 * u)), "{", fill=(56, 189, 248, 255), font=_font(max(16, int(18 * u)), bold=True))
        draw.text((icx + int(3 * u), icy - int(12 * u)), "}", fill=(56, 189, 248, 255), font=_font(max(16, int(18 * u)), bold=True))
        draw.ellipse([icx - int(3 * u), icy - int(2 * u), icx + int(3 * u), icy + int(4 * u)], fill=(255, 255, 255, 255))
    elif archetype == "outpost":
        # 42U rack grid inside facility
        draw.rounded_rectangle([icx - int(14 * u), icy - int(15 * u), icx + int(14 * u), icy + int(15 * u)], radius=int(3 * u), fill=(13, 148, 136, 255))
        draw.rectangle([icx - int(10 * u), icy - int(11 * u), icx + int(10 * u), icy - int(7 * u)], fill=(204, 251, 241, 255))
        draw.rectangle([icx - int(10 * u), icy - int(3 * u), icx + int(10 * u), icy + int(1 * u)], fill=(204, 251, 241, 255))
        draw.rectangle([icx - int(10 * u), icy + int(5 * u), icx + int(10 * u), icy + int(9 * u)], fill=(204, 251, 241, 255))
    elif archetype == "tekbay":
        # TekBay star/shield emblem in orange
        draw.polygon([
            (icx, icy - int(16 * u)), (icx + int(14 * u), icy - int(6 * u)), (icx + int(10 * u), icy + int(11 * u)),
            (icx, icy + int(16 * u)), (icx - int(10 * u), icy + int(11 * u)), (icx - int(14 * u), icy - int(6 * u))
        ], fill=(234, 88, 12, 255), outline=(254, 215, 170, 255), width=max(1, int(1.8 * u)))
        draw.text((icx - int(9 * u), icy - int(7 * u)), "AWS", fill=(255, 255, 255, 255), font=_font(max(8, int(8.5 * u)), bold=True))
    else:
        draw.ellipse([icx - int(12 * u), icy - int(12 * u), icx + int(12 * u), icy + int(12 * u)], outline=border, width=max(1, int(2 * u)))
        draw.ellipse([icx - int(5 * u), icy - int(5 * u), icx + int(5 * u), icy + int(5 * u)], fill=border)

    # 5. Body Area: Right Subtitle & Bullet Chips
    tx = pad + int(96 * u)
    f_sub = _font(max(11, int(13 * u)), bold=True)
    draw.text((tx, pad + header_h + int(10 * u)), s_str, fill=sub_fg, font=f_sub)

    f_pill = _font(max(9, int(11 * u)), bold=False)
    for idx, b in enumerate(bullets):
        py = pad + header_h + int(33 * u) + idx * int(24 * u)
        pill_w = max(int(100 * u), cw - tx - pad - int(12 * u))
        draw.rounded_rectangle([tx, py, tx + pill_w, py + int(18 * u)], radius=int(5 * u), fill=pill_bg)
        # Theme indicator dot
        draw.ellipse([tx + int(6 * u), py + int(6 * u), tx + int(12 * u), py + int(12 * u)], fill=header_color)
        draw.text((tx + int(16 * u), py + int(2.5 * u)), b, fill=pill_txt, font=f_pill)

    # Bottom subtle accent strip
    bx0 = pad + int(14 * u)
    bx1 = cw - pad - int(14 * u)
    by = ch - pad - int(6 * u)
    draw.rounded_rectangle([bx0, by - int(1.5 * u), bx1, by + int(1.5 * u)], radius=int(1.5 * u), fill=header_color)
