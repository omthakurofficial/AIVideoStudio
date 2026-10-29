"""Stock media discovery (official Pexels, Pixabay & Wikimedia Commons Open-Web APIs) + local cache + user asset management.

Rules enforced:
  * Never invent stock URLs. Query official Pexels, Pixabay, and Wikimedia Commons APIs.
  * Record asset ID, provider, source page URL, and licence/attribution terms (note: Pexels/Pixabay/Wikimedia licences permit
    free use with attribution/restrictions—never claim unrestricted use).
  * Cache downloaded files by provider+id in data/asset_cache/ and validate usability with ffprobe/Pillow.
  * When search returns no match, report clearly and fall back to custom motion graphics.
"""
from __future__ import annotations
import hashlib, json, os, shutil
from dataclasses import dataclass
from pathlib import Path
import httpx
from ..storyboard.schema import Storyboard, AssetRequirement
from ..workspace import Workspace
from .media import probe
from .mcp_client import EngineError

PEXELS_LICENCE = "Pexels License (https://www.pexels.com/license/): free to use with modifications; do not sell unaltered copies or imply endorsement by depicted people/brands."
PIXABAY_LICENCE = "Pixabay Content License (https://pixabay.com/service/license-summary/): free for commercial/non-commercial use; standalone redistribution and misleading trademark/person use prohibited."
WIKIMEDIA_LICENCE = "Wikimedia Commons Open-Web License (CC-BY / CC-BY-SA / Public Domain — see source URL for exact file attribution)."


@dataclass
class DiscoveredAsset:
    req_id: str
    scene_id: str
    status: str  # "found" | "provided" | "fallback_animation"
    local_rel_path: str | None
    provider: str | None
    external_id: str | None
    source_url: str | None
    licence: str | None
    note: str


class AssetManager:
    def __init__(self, cache_dir: Path, ffprobe: str = "ffprobe", timeout: float = 20.0):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ffprobe = ffprobe
        self.timeout = timeout
        self._refresh_keys()

    def _refresh_keys(self):
        self.pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY", "").strip()

    def resolve_for_storyboard(self, sb: Storyboard, ws: Workspace, log=lambda m: None) -> tuple[Storyboard, list[DiscoveredAsset]]:
        self._refresh_keys()
        results: list[DiscoveredAsset] = []
        sb_data = sb.model_dump()
        for sc in sb_data["scenes"]:
            for req in sc.get("asset_requirements", []):
                r = AssetRequirement.model_validate(req)
                res = self._resolve_one(sc["id"], r, ws, log)
                req["status"] = "found" if res.status in ("found", "provided") else "missing"
                results.append(res)
        ws.write_json("reports/asset_discovery.json", {"assets": [r.__dict__ for r in results]})
        return Storyboard.model_validate(sb_data), results

    def _resolve_one(self, scene_id: str, req: AssetRequirement, ws: Workspace, log) -> DiscoveredAsset:
        if req.kind == "user_asset":
            cand = ws.root / "assets" / req.query if req.query else None
            if cand and cand.is_file():
                return DiscoveredAsset(req.id, scene_id, "provided", f"assets/{cand.name}", "user", req.id, None, "User-supplied asset", "Verified user asset")
            return DiscoveredAsset(req.id, scene_id, "fallback_animation", None, None, None, None, None,
                                   f"User asset '{req.query}' not found in assets/; using animated visual instead.")

        if req.kind == "generated_graphic":
            return DiscoveredAsset(req.id, scene_id, "found", None, "effectcraft", req.id, None, "Generated locally", "Rendered via EffectCraft primitives")

        if not req.query.strip():
            return DiscoveredAsset(req.id, scene_id, "fallback_animation", None, None, None, None, None, "Empty search query; using animated visual.")

        if self.pexels_key:
            try:
                hit = self._search_pexels(req)
                if hit:
                    rel = self._download_and_validate(hit, ws, scene_id)
                    return DiscoveredAsset(req.id, scene_id, "found", rel, "pexels", hit["id"], hit["page_url"], PEXELS_LICENCE, "Downloaded and validated from Pexels")
            except Exception as e:
                log(f"Pexels search failed for '{req.query}': {e}")

        if self.pixabay_key:
            try:
                hit = self._search_pixabay(req)
                if hit:
                    rel = self._download_and_validate(hit, ws, scene_id)
                    return DiscoveredAsset(req.id, scene_id, "found", rel, "pixabay", hit["id"], hit["page_url"], PIXABAY_LICENCE, "Downloaded and validated from Pixabay")
            except Exception as e:
                log(f"Pixabay search failed for '{req.query}': {e}")

        # Open-Web Wikimedia Commons fallback for maps, geographical imagery, and documentary photography
        try:
            hit = self._search_wikimedia(req)
            if hit:
                rel = self._download_and_validate(hit, ws, scene_id)
                return DiscoveredAsset(req.id, scene_id, "found", rel, "wikimedia", hit["id"], hit["page_url"], hit["licence"], "Downloaded and validated from Wikimedia Commons")
        except Exception as e:
            log(f"Wikimedia search failed for '{req.query}': {e}")

        reason = "No PEXELS_API_KEY or PIXABAY_API_KEY configured" if not (self.pexels_key or self.pixabay_key) else f"No matching stock media for '{req.query}'"
        log(f"Scene {scene_id} ({req.id}): {reason}; using custom motion graphics.")
        return DiscoveredAsset(req.id, scene_id, "fallback_animation", None, None, None, None, None, f"{reason}; using custom motion graphics.")

    def _search_pexels(self, req: AssetRequirement) -> dict | None:
        headers = {"Authorization": self.pexels_key}
        orient = {"landscape": "landscape", "portrait": "portrait"}.get(req.orientation)
        params: dict[str, str | int] = {"query": req.query, "per_page": 4}
        if orient:
            params["orientation"] = orient
        with httpx.Client(timeout=self.timeout) as client:
            if req.kind == "stock_video":
                r = client.get("https://api.pexels.com/videos/search", headers=headers, params=params)
                if r.status_code == 429:
                    raise EngineError("Pexels API rate limit reached.", retryable=True)
                r.raise_for_status()
                videos = r.json().get("videos", [])
                for v in videos:
                    files = sorted(v.get("video_files", []), key=lambda x: abs((x.get("width") or 0) - 1280))
                    if files and files[0].get("link"):
                        return {"provider": "pexels", "id": str(v["id"]), "kind": "video", "ext": ".mp4",
                                "download_url": files[0]["link"], "page_url": v.get("url"), "licence": PEXELS_LICENCE}
            else:
                r = client.get("https://api.pexels.com/v1/search", headers=headers, params=params)
                if r.status_code == 429:
                    raise EngineError("Pexels API rate limit reached.", retryable=True)
                r.raise_for_status()
                photos = r.json().get("photos", [])
                if photos:
                    p = photos[0]
                    src = p.get("src", {})
                    dl = src.get("large2x") or src.get("large") or src.get("original")
                    if dl:
                        return {"provider": "pexels", "id": str(p["id"]), "kind": "image", "ext": ".jpg",
                                "download_url": dl, "page_url": p.get("url"), "licence": PEXELS_LICENCE}
        return None

    def _search_pixabay(self, req: AssetRequirement) -> dict | None:
        params: dict[str, str | int] = {"key": self.pixabay_key, "q": req.query, "per_page": 4, "safesearch": "true"}
        with httpx.Client(timeout=self.timeout) as client:
            if req.kind == "stock_video":
                r = client.get("https://pixabay.com/api/videos/", params=params)
                r.raise_for_status()
                hits = r.json().get("hits", [])
                if hits:
                    v = hits[0]
                    med = v.get("videos", {}).get("medium") or v.get("videos", {}).get("small")
                    if med and med.get("url"):
                        return {"provider": "pixabay", "id": str(v["id"]), "kind": "video", "ext": ".mp4",
                                "download_url": med["url"], "page_url": v.get("pageURL"), "licence": PIXABAY_LICENCE}
            else:
                r = client.get("https://pixabay.com/api/", params=params)
                r.raise_for_status()
                hits = r.json().get("hits", [])
                if hits and hits[0].get("largeImageURL"):
                    p = hits[0]
                    return {"provider": "pixabay", "id": str(p["id"]), "kind": "image", "ext": ".jpg",
                            "download_url": p["largeImageURL"], "page_url": p.get("pageURL"), "licence": PIXABAY_LICENCE}
        return None

    def _search_wikimedia(self, req: AssetRequirement) -> dict | None:
        headers = {"User-Agent": "AIVideoStudio/1.0 (https://github.com/aivideostudio; local-educational-studio)"}
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {req.query}",
            "gsrnamespace": "6",
            "gsrlimit": "5",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|dimensions",
            "iiurlwidth": "1280",
            "format": "json",
        }
        with httpx.Client(timeout=self.timeout, headers=headers) as client:
            r = client.get("https://commons.wikimedia.org/w/api.php", params=params)
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                ii_list = page.get("imageinfo") or []
                if not ii_list:
                    continue
                ii = ii_list[0]
                dl = ii.get("thumburl") or ii.get("url")
                if not dl or dl.lower().endswith((".svg", ".gif", ".tif", ".tiff", ".pdf")):
                    continue
                ext_meta = ii.get("extmetadata") or {}
                lic_short = (ext_meta.get("LicenseShortName") or {}).get("value", "CC / Public Domain")
                return {
                    "provider": "wikimedia",
                    "id": str(page_id),
                    "kind": "image",
                    "ext": ".jpg",
                    "download_url": dl,
                    "page_url": ii.get("descriptionurl") or f"https://commons.wikimedia.org/?curid={page_id}",
                    "licence": f"{WIKIMEDIA_LICENCE} [{lic_short}]",
                }
        return None

    def _download_and_validate(self, hit: dict, ws: Workspace, scene_id: str | None = None) -> str:
        cache_name = f"{hit['provider']}_{hit['id']}{hit['ext']}"
        cached = self.cache_dir / cache_name
        headers = {"User-Agent": "AIVideoStudio/1.0 (https://github.com/aivideostudio; local-educational-studio)"}
        if not cached.is_file() or cached.stat().st_size == 0:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
                r = client.get(hit["download_url"])
                r.raise_for_status()
                cached.write_bytes(r.content)
        # Validate file usability & normalize images to clean RGB JPEG
        if hit["kind"] == "video":
            probe(cached, self.ffprobe)
        else:
            from PIL import Image
            img = Image.open(cached)
            img.verify()
            img2 = Image.open(cached).convert("RGB")
            img2.save(cached, format="JPEG", quality=92)
        dest_rel = f"assets/{cache_name}"
        dest = ws.root / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file():
            shutil.copy2(cached, dest)
        ws.add_asset(dest_rel, f"stock_{hit['kind']}", {
            "provider": hit["provider"],
            "external_id": hit["id"],
            "scene_id": scene_id,
            "source_url": hit["page_url"],
            "licence": hit["licence"],
        })
        return dest_rel
