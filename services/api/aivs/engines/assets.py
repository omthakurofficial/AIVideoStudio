"""Stock media discovery (official Pexels & Pixabay APIs) + local cache + user asset management.

Rules enforced:
  * Never invent stock URLs. Only query official endpoints when PEXELS_API_KEY or PIXABAY_API_KEY is present in env.
  * Record asset ID, provider, source page URL, and licence/attribution terms (note: Pexels/Pixabay licences permit
    free use with restrictions—e.g. no standalone redistribution, no trademark endorsement—never claim unrestricted use).
  * Cache downloaded files by provider+id in data/asset_cache/ and validate usability with ffprobe/Pillow.
  * When keys are absent or search returns no match, report clearly and fall back to custom motion graphics.
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
        self.pexels_key = os.environ.get("PEXELS_API_KEY", "").strip()
        self.pixabay_key = os.environ.get("PIXABAY_API_KEY", "").strip()

    def resolve_for_storyboard(self, sb: Storyboard, ws: Workspace, log=lambda m: None) -> tuple[Storyboard, list[DiscoveredAsset]]:
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
                    rel = self._download_and_validate(hit, ws)
                    return DiscoveredAsset(req.id, scene_id, "found", rel, "pexels", hit["id"], hit["page_url"], PEXELS_LICENCE, "Downloaded and validated from Pexels")
            except Exception as e:
                log(f"Pexels search failed for '{req.query}': {e}")

        if self.pixabay_key:
            try:
                hit = self._search_pixabay(req)
                if hit:
                    rel = self._download_and_validate(hit, ws)
                    return DiscoveredAsset(req.id, scene_id, "found", rel, "pixabay", hit["id"], hit["page_url"], PIXABAY_LICENCE, "Downloaded and validated from Pixabay")
            except Exception as e:
                log(f"Pixabay search failed for '{req.query}': {e}")

        reason = "No PEXELS_API_KEY or PIXABAY_API_KEY configured" if not (self.pexels_key or self.pixabay_key) else f"No matching stock media for '{req.query}'"
        log(f"Scene {scene_id} ({req.id}): {reason}; using custom motion graphics.")
        return DiscoveredAsset(req.id, scene_id, "fallback_animation", None, None, None, None, None, f"{reason}; using custom motion graphics.")

    def _search_pexels(self, req: AssetRequirement) -> dict | None:
        headers = {"Authorization": self.pexels_key}
        orient = {"landscape": "landscape", "portrait": "portrait"}.get(req.orientation)
        params: dict[str, str | int] = {"query": req.query, "per_page": 3}
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
                    files = sorted(v.get("video_files", []), key=lambda x: abs((x.get("width") or 0) - 1920))
                    if files and files[0].get("link"):
                        return {"provider": "pexels", "id": str(v["id"]), "kind": "video", "ext": ".mp4",
                                "download_url": files[0]["link"], "page_url": v.get("url"), "licence": PEXELS_LICENCE}
            else:
                r = client.get("https://api.pexels.com/v1/search", headers=headers, params=params)
                if r.status_code == 429:
                    raise EngineError("Pexels API rate limit reached.", retryable=True)
                r.raise_for_status()
                photos = r.json().get("photos", [])
                if photos and photos[0].get("src", {}).get("large2x"):
                    p = photos[0]
                    return {"provider": "pexels", "id": str(p["id"]), "kind": "image", "ext": ".jpg",
                            "download_url": p["src"]["large2x"], "page_url": p.get("url"), "licence": PEXELS_LICENCE}
        return None

    def _search_pixabay(self, req: AssetRequirement) -> dict | None:
        params: dict[str, str | int] = {"key": self.pixabay_key, "q": req.query, "per_page": 3, "safesearch": "true"}
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

    def _download_and_validate(self, hit: dict, ws: Workspace) -> str:
        cache_name = f"{hit['provider']}_{hit['id']}{hit['ext']}"
        cached = self.cache_dir / cache_name
        if not cached.is_file() or cached.stat().st_size == 0:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                r = client.get(hit["download_url"])
                r.raise_for_status()
                cached.write_bytes(r.content)
        # Validate file usability
        if hit["kind"] == "video":
            probe(cached, self.ffprobe)
        else:
            from PIL import Image
            Image.open(cached).verify()
        dest_rel = f"assets/{cache_name}"
        dest = ws.root / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file():
            shutil.copy2(cached, dest)
        ws.add_asset(dest_rel, f"stock_{hit['kind']}", {
            "provider": hit["provider"],
            "external_id": hit["id"],
            "source_url": hit["page_url"],
            "licence": hit["licence"],
        })
        return dest_rel
