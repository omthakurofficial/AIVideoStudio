"""FastAPI app: projects, storyboards, production pipeline, scene review, quality reports, exports, settings, and health."""
from __future__ import annotations
import io, json, tempfile, zipfile
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, ValidationError
from .config import load_settings, Settings, REPO_ROOT
from .db import connect, migrate
from .store import Store, TERMINAL_STATES
from .worker import Worker
from .models import ProjectCreate, ScriptUpdate, RESOLUTIONS
from .health import health, verify_engines_mcp
from .director import Director
from .storyboard import Storyboard, store as sbstore
from .analysis import analyze_script, load_sample_scripts, SUPPORTED_SCRIPT_FORMATS
from .pricing import ARCHITECTURE_LAYERS, BEDROCK_MODEL_CATALOG, OFFICIAL_PRICING_LINKS, record_token_usage, get_project_token_report
from .niches import list_niches
from .engines.narration import AVAILABLE_VOICES


class TopicRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    target_duration_s: int = Field(default=30, ge=10, le=900)


class SceneRegenerateRequest(BaseModel):
    visual_correction: str | None = Field(default=None, max_length=500)
    visual_type: str | None = None
    visual_description: str | None = Field(default=None, max_length=900)


class SceneUpdateRequest(BaseModel):
    narration_text: str | None = None
    visual_description: str | None = None
    visual_type: str | None = None
    estimated_duration: float | None = Field(default=None, ge=1.0, le=120.0)
    key_message: str | None = None
    learning_objective: str | None = None
    on_screen_text: list[dict] | None = None
    status: str | None = None


class V2TemplateGenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=1500)
    niche_id: str = Field(default="youtube_growth")
    target_duration_s: int = Field(default=60, ge=15, le=600)
    aspect_ratio: str = Field(default="9:16")
    mode: str = Field(default="master_auto")
    custom_instructions: str | None = None


DEFAULT_USER_SETTINGS = {
    "theme": "dark",
    "accent_color": "blue",
    "default_aspect_ratio": "16:9",
    "default_fps": 30,
    "default_visual_style": "clean-technical",
    "default_approval_mode": "automatic",
    "default_voice": "kokoro:am_michael",
    "captions_enabled": True,
    "caption_font_size": 44,
    "caption_style": "pop_words",
}


def _classify_file(rel: str) -> str:
    ext = Path(rel).suffix.lower()
    if ext in (".mp4", ".mov", ".webm", ".mkv"):
        return "video"
    if ext in (".wav", ".mp3", ".m4a", ".ogg"):
        return "audio"
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        return "image"
    if ext in (".ecproj", ".fcproj"):
        return "project"
    if ext == ".json":
        return "json"
    if ext in (".srt", ".vtt", ".md", ".txt", ".log"):
        return "text"
    return "binary"


def create_app(settings: Settings | None = None, director_factory=None) -> FastAPI:
    settings = settings or load_settings()

    if director_factory is None:
        def director_factory():
            from .providers import load_model_specs, get_provider
            from .providers.base import load_config
            spec = load_model_specs()["planning"]
            return Director(get_provider(spec.provider, settings.aws_region), spec, load_config()["director"])

    def new_store() -> Store:
        return Store(connect(settings.db_path), settings.projects_dir)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.projects_dir.mkdir(parents=True, exist_ok=True)
        store = new_store()
        migrate(store.conn)
        store.recover_interrupted()
        worker = Worker(new_store, director_factory, settings)
        worker.start()
        for j in store.list_jobs(limit=1000):
            if j["state"] == "queued":
                worker.submit(j["id"])
        app.state.store, app.state.worker, app.state.settings = store, worker, settings
        yield

    app = FastAPI(title="AIVideoStudio API", version="0.3.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"])

    def store() -> Store:
        return app.state.store

    def _user_settings_path() -> Path:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        return settings.data_dir / "user_settings.json"

    def _load_user_settings() -> dict:
        p = _user_settings_path()
        data = dict(DEFAULT_USER_SETTINGS)
        if p.is_file():
            try:
                data.update(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        return data

    @app.get("/api/health")
    def get_health(aws: bool = False):
        return health(settings, include_aws=aws)

    @app.post("/api/engines/verify")
    def verify_engines():
        return verify_engines_mcp(settings)

    @app.get("/api/settings")
    def get_app_settings():
        import os
        from .providers.base import load_config
        cfg = load_config()
        px_key = os.environ.get("PEXELS_API_KEY", "").strip()
        pb_key = os.environ.get("PIXABAY_API_KEY", "").strip()
        return {
            "preferences": _load_user_settings(),
            "models": cfg.get("tasks", {}),
            "model_catalog": BEDROCK_MODEL_CATALOG,
            "architecture_layers": ARCHITECTURE_LAYERS,
            "niche_categories": list_niches(),
            "official_pricing_links": OFFICIAL_PRICING_LINKS,
            "available_voices": AVAILABLE_VOICES,
            "stock_media": {
                "pexels_configured": bool(px_key),
                "pexels_masked": (f"{px_key[:4]}••••••••{px_key[-4:]}" if len(px_key) >= 8 else ("••••" if px_key else "")),
                "pixabay_configured": bool(pb_key),
                "pixabay_masked": (f"{pb_key[:4]}••••••••{pb_key[-4:]}" if len(pb_key) >= 8 else ("••••" if pb_key else "")),
                "wikimedia_enabled": True,
            },
            "director": cfg.get("director", {}),
            "storage": {
                "projects_dir": str(settings.projects_dir),
                "data_dir": str(settings.data_dir),
                "db_path": str(settings.db_path),
            },
            "engines": {
                "effectcraft_cli": settings.effectcraft_cli,
                "filmcraft_cli": settings.filmcraft_cli,
                "ffmpeg": settings.ffmpeg,
                "ffprobe": settings.ffprobe,
                "aws_region": settings.aws_region,
            },
            "health": health(settings, include_aws=True),
        }

    @app.put("/api/settings")
    def update_app_settings(body: dict):
        import os
        from .providers.base import load_config, CONFIG_FILE
        cur = _load_user_settings()
        for k in DEFAULT_USER_SETTINGS:
            if k in body:
                cur[k] = body[k]
        _user_settings_path().write_text(json.dumps(cur, indent=2), encoding="utf-8")

        # Update task AI models in config/models.json if requested
        if isinstance(body.get("task_models"), dict):
            cfg = load_config()
            valid_ids = {m["model_id"] for m in BEDROCK_MODEL_CATALOG}
            for task_name, model_id in body["task_models"].items():
                if task_name in cfg.get("tasks", {}) and model_id in valid_ids:
                    cfg["tasks"][task_name]["model_id"] = model_id
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

        # Update Pexels / Pixabay API keys in .env and os.environ if provided
        env_path = REPO_ROOT / ".env"
        env_lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.is_file() else []
        env_updated = False
        for key_field, env_name in (("pexels_api_key", "PEXELS_API_KEY"), ("pixabay_api_key", "PIXABAY_API_KEY")):
            if key_field in body and isinstance(body[key_field], str):
                val = body[key_field].strip()
                if val and "•" not in val:
                    os.environ[env_name] = val
                    env_lines = [ln for ln in env_lines if not ln.strip().startswith(f"{env_name}=")]
                    env_lines.append(f"{env_name}={val}")
                    env_updated = True
        if env_updated:
            env_path.write_text("\n".join(env_lines) + "\n", encoding="utf-8")

        return {"ok": True, "preferences": cur}

    @app.get("/api/scripts/samples")
    def get_script_samples():
        return {"samples": load_sample_scripts(REPO_ROOT), "supported_formats": SUPPORTED_SCRIPT_FORMATS}

    @app.post("/api/scripts/inspect")
    def inspect_script(body: ScriptUpdate):
        return analyze_script(body.script)

    @app.post("/api/projects", status_code=201)
    def create_project(body: ProjectCreate):
        sdict = body.settings.model_dump()
        if body.script.strip() and "target_duration_s" not in body.settings.model_fields_set:
            sdict["target_duration_s"] = analyze_script(body.script)["recommended_target_duration_s"]
        p = store().create_project(body.title, body.script, sdict)
        w, h = RESOLUTIONS[body.settings.aspect_ratio]
        p["output"] = {"width": w, "height": h, "fps": body.settings.fps}
        p["script_analysis"] = analyze_script(body.script)
        return p

    @app.get("/api/projects")
    def list_projects():
        projs = store().list_projects()
        for p in projs:
            ws_root = settings.projects_dir / p["id"]
            p["has_export"] = (ws_root / "renders" / "final.mp4").is_file() and (ws_root / "reports" / "quality_report.json").is_file()
            prevs = sorted((ws_root / "renders" / "previews").glob("*.png")) if (ws_root / "renders" / "previews").is_dir() else []
            p["thumbnail"] = f"/api/projects/{p['id']}/media/renders/previews/{prevs[0].name}" if prevs else None
            p["token_usage"] = get_project_token_report(ws_root)
        return projs

    def _project(pid: str) -> dict:
        p = store().get_project(pid)
        if not p:
            raise HTTPException(404, f"Project '{pid}' not found")
        w, h = RESOLUTIONS[p["settings"]["aspect_ratio"]]
        p["output"] = {"width": w, "height": h, "fps": p["settings"]["fps"]}
        return p

    @app.get("/api/projects/{pid}")
    def get_project(pid: str):
        p = _project(pid)
        ws = store().workspace(pid)
        p["script"] = ws.read_script()
        p["has_export"] = (ws.root / "renders" / "final.mp4").is_file() and (ws.root / "reports" / "quality_report.json").is_file()
        p["script_analysis"] = analyze_script(p["script"])
        p["token_usage"] = get_project_token_report(ws.root)
        return p

    @app.put("/api/projects/{pid}/script")
    def put_script(pid: str, body: ScriptUpdate):
        _project(pid)
        store().set_script(pid, body.script)
        return {"ok": True, "chars": len(body.script)}

    @app.post("/api/projects/{pid}/generate-script")
    def generate_script_from_topic(pid: str, body: TopicRequest):
        _project(pid)
        target_words = max(35, int(body.target_duration_s * 2.4))
        try:
            from .providers import load_model_specs, get_provider
            spec = load_model_specs()["script"]
            prov = get_provider(spec.provider, settings.aws_region)
            sys_prompt = (
                "Write a clear, concise educational narration script divided into 3 to 5 short paragraphs "
                "(separated by blank lines). Output ONLY the spoken narration paragraphs—no headings, no bullet points, "
                "no stage directions."
            )
            prompt = f"Topic: {body.topic}\nTarget length: approximately {target_words} words ({body.target_duration_s} seconds)."
            text, usage = prov.generate_text(spec, sys_prompt, prompt)
            script = text.strip()
            ws = store().workspace(pid)
            ws.write_json("reports/script_generation.json", {
                "model_id": usage.model_id, "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens, "latency_s": usage.latency_s
            })
            record_token_usage(ws.root, "script_generation", usage.model_id, usage.input_tokens, usage.output_tokens, usage.latency_s, 1)
        except Exception as e:
            raise HTTPException(503, f"Could not generate script from topic: {e}")
        store().set_script(pid, script)
        return {"ok": True, "script": script}

    @app.post("/api/projects/{pid}/jobs/analyze", status_code=202)
    def start_analysis(pid: str):
        _project(pid)
        job = store().create_job(pid, "analyze_script")
        app.state.worker.submit(job["id"])
        return job

    @app.post("/api/projects/{pid}/jobs/storyboard", status_code=202)
    def start_storyboard(pid: str):
        _project(pid)
        job = store().create_job(pid, "plan_storyboard")
        app.state.worker.submit(job["id"])
        return job

    @app.post("/api/projects/{pid}/jobs/produce", status_code=202)
    def start_production(pid: str):
        _project(pid)
        ws = store().workspace(pid)
        sb = sbstore.load(ws.root)
        if sb and not sb.approved:
            sb = sbstore.save(ws.root, sb.model_copy(update={"approved": True}), bump=False)
        prev_ckpt: dict = {}
        for j in store().list_jobs(pid):
            if j["kind"] in ("produce_video", "regenerate_scene") and j.get("checkpoint"):
                prev_ckpt = {"rendered_scenes": j["checkpoint"].get("rendered_scenes", {})}
                break
        job = store().create_job(pid, "produce_video")
        if prev_ckpt:
            store().update_job(job["id"], checkpoint=prev_ckpt)
        app.state.worker.submit(job["id"])
        return store().get_job(job["id"])

    @app.put("/api/projects/{pid}/scenes/{scene_id}")
    def update_scene(pid: str, scene_id: str, body: SceneUpdateRequest):
        _project(pid)
        ws = store().workspace(pid)
        sb = sbstore.load(ws.root)
        if not sb:
            raise HTTPException(404, "No storyboard exists for this project.")
        sb_data = sb.model_dump()
        target = next((s for s in sb_data["scenes"] if s["id"] == scene_id), None)
        if not target:
            raise HTTPException(404, f"Scene '{scene_id}' not found in storyboard.")
        for k, v in body.model_dump(exclude_none=True).items():
            target[k] = v
            if k == "estimated_duration":
                target["timing"]["narration_audio_s"] = None
                target["timing"]["revised_from_audio"] = False
        try:
            sb_valid = Storyboard.model_validate(sb_data)
        except ValidationError as e:
            raise HTTPException(422, [{"where": ".".join(map(str, x["loc"])), "problem": x["msg"]} for x in e.errors()[:10]])
        sb_saved = sbstore.save(ws.root, sb_valid, bump=True)
        return sb_saved.model_dump()

    @app.post("/api/projects/{pid}/scenes/{scene_id}/regenerate", status_code=202)
    def regenerate_scene(pid: str, scene_id: str, body: SceneRegenerateRequest | None = None):
        _project(pid)
        ws = store().workspace(pid)
        sb = sbstore.load(ws.root)
        if not sb:
            raise HTTPException(404, "No storyboard exists for this project.")
        sb_data = sb.model_dump()
        target = next((s for s in sb_data["scenes"] if s["id"] == scene_id), None)
        if not target:
            raise HTTPException(404, f"Scene '{scene_id}' not found in storyboard.")
        if body:
            if body.visual_type:
                target["visual_type"] = body.visual_type
            if body.visual_description:
                target["visual_description"] = body.visual_description
            if body.visual_correction:
                import re as _re
                base_desc = _re.sub(r"\s*\[Correction:.*?\]", "", target["visual_description"]).strip()
                target["visual_description"] = f"{base_desc} [Correction: {body.visual_correction}]"[:900]
                dur = float(target["timing"]["narration_audio_s"] or target["estimated_duration"])
                target["on_screen_text"] = [{"text": body.visual_correction[:80], "at": 0.2, "duration": round(max(1.0, dur - 0.4), 2)}]
        target["status"] = "approved"
        try:
            sb_valid = Storyboard.model_validate(sb_data)
        except ValidationError as e:
            raise HTTPException(422, [{"where": ".".join(map(str, x["loc"])), "problem": x["msg"]} for x in e.errors()[:10]])
        sbstore.save(ws.root, sb_valid, bump=True)

        prev_rendered: dict = {}
        for j in store().list_jobs(pid):
            if j["kind"] in ("produce_video", "regenerate_scene") and j.get("checkpoint"):
                prev_rendered = dict(j["checkpoint"].get("rendered_scenes") or {})
                break
        prev_rendered.pop(scene_id, None)
        job = store().create_job(pid, "regenerate_scene")
        store().update_job(job["id"], checkpoint={"rendered_scenes": prev_rendered, "force_scene_ids": [scene_id]})
        app.state.worker.submit(job["id"])
        return store().get_job(job["id"])

    @app.get("/api/projects/{pid}/storyboard")
    def get_storyboard(pid: str):
        _project(pid)
        sb = sbstore.load(store().workspace(pid).root)
        if not sb:
            raise HTTPException(404, "No storyboard yet. Plan one from the project page.")
        return sb.model_dump()

    @app.put("/api/projects/{pid}/storyboard")
    def put_storyboard(pid: str, body: dict):
        _project(pid)
        root = store().workspace(pid).root
        cur = sbstore.load(root)
        if not cur:
            raise HTTPException(404, "No storyboard to edit.")
        body = {**body, "project_id": pid, "schema_version": 1, "approved": False}
        try:
            sb = Storyboard.model_validate(body)
        except ValidationError as e:
            raise HTTPException(422, [{"where": ".".join(map(str, x["loc"])), "problem": x["msg"]} for x in e.errors()[:20]])
        sb = sbstore.save(root, sb.model_copy(update={"created_by": cur.created_by}))
        return sb.model_dump()

    @app.post("/api/projects/{pid}/storyboard/approve")
    def approve_storyboard(pid: str):
        _project(pid)
        root = store().workspace(pid).root
        sb = sbstore.load(root)
        if not sb:
            raise HTTPException(404, "No storyboard to approve.")
        sb = sbstore.save(root, sb.model_copy(update={"approved": True}), bump=False)
        for j in store().list_jobs(pid):
            if j["kind"] == "plan_storyboard" and j["state"] == "awaiting_approval":
                store().update_job(j["id"], state="completed", current_step="Storyboard approved")
        return sb.model_dump()

    @app.get("/api/projects/{pid}/reports")
    def get_reports(pid: str):
        _project(pid)
        ws = store().workspace(pid)
        out: dict = {"workspace_path": str(ws.root), "token_usage": get_project_token_report(ws.root)}
        for name in ("quality_report", "director_usage", "caption_validation", "asset_discovery", "script_analysis"):
            f = ws.root / "reports" / f"{name}.json"
            if f.is_file():
                out[name] = json.loads(f.read_text(encoding="utf-8"))
        mf = ws.root / "manifest.json"
        if mf.is_file():
            out["manifest"] = json.loads(mf.read_text(encoding="utf-8"))
        return out

    @app.get("/api/projects/{pid}/files")
    def list_project_files(pid: str, preview: str | None = None):
        _project(pid)
        root = store().workspace(pid).root.resolve()
        files = []
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            if "/_qc_" in f"/{rel}" or rel.endswith("_raw_export.mp4"):
                continue
            st = p.stat()
            parts = rel.split("/")
            folder = parts[0] if len(parts) > 1 else "root"
            kind = _classify_file(rel)
            files.append({
                "path": rel,
                "name": p.name,
                "folder": folder,
                "kind": kind,
                "size_bytes": st.st_size,
                "modified_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                "url": f"/api/projects/{pid}/media/{rel}",
            })
        preview_content = None
        if preview:
            target = (root / preview).resolve()
            if target.is_relative_to(root) and target.is_file() and target.stat().st_size <= 250_000:
                try:
                    preview_content = target.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    preview_content = None
        return {"workspace_path": str(root), "files": files, "preview_content": preview_content}

    @app.get("/api/projects/{pid}/export-zip")
    def export_project_zip(pid: str):
        p = _project(pid)
        root = store().workspace(pid).root.resolve()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in sorted(root.rglob("*")):
                if item.is_file() and not item.name.startswith("_"):
                    rel = str(item.relative_to(root)).replace("\\", "/")
                    zf.write(item, arcname=f"{pid}/{rel}")
        buf.seek(0)
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in p["title"])[:40] or pid
        headers = {"Content-Disposition": f'attachment; filename="{safe_title}_{pid}.zip"'}
        return StreamingResponse(buf, media_type="application/zip", headers=headers)

    @app.get("/api/projects/{pid}/media/{rel_path:path}")
    def get_project_media(pid: str, rel_path: str, download: bool = False):
        _project(pid)
        root = store().workspace(pid).root.resolve()
        target = (root / rel_path).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            raise HTTPException(404, f"Media file '{rel_path}' not found")
        headers = {"Cache-Control": "no-store"}
        if download:
            headers["Content-Disposition"] = f'attachment; filename="{target.name}"'
        return FileResponse(target, headers=headers)

    @app.get("/api/jobs")
    def list_jobs(project_id: str | None = None):
        jobs = store().list_jobs(project_id)
        proj_map = {p["id"]: p["title"] for p in store().list_projects()}
        for j in jobs:
            j["project_title"] = proj_map.get(j["project_id"], j["project_id"])
        return jobs

    @app.get("/api/jobs/{jid}")
    def get_job(jid: str):
        j = store().get_job(jid)
        if not j:
            raise HTTPException(404, f"Job '{jid}' not found")
        j["logs"] = store().job_logs(jid)
        return j

    @app.post("/api/jobs/{jid}/cancel")
    def cancel(jid: str):
        j = store().get_job(jid)
        if not j:
            raise HTTPException(404, "Job not found")
        if j["state"] in TERMINAL_STATES:
            raise HTTPException(409, f"Job already {j['state']}")
        app.state.worker.cancel(jid)
        if j["state"] == "queued":
            store().update_job(jid, state="cancelled")
        return store().get_job(jid)

    @app.post("/api/jobs/{jid}/retry", status_code=202)
    def retry(jid: str):
        j = store().get_job(jid)
        if not j:
            raise HTTPException(404, "Job not found")
        if j["state"] not in ("failed", "cancelled"):
            raise HTTPException(409, f"Only failed or cancelled jobs can be retried (state is {j['state']})")
        store().update_job(jid, state="queued", error=None)
        app.state.worker.submit(jid)
        return store().get_job(jid)

    # --------------------------------------------------------------------------
    # AI Video Studio V2 — Top 10 Niche Templates & Master Blueprint Engine
    # --------------------------------------------------------------------------
    @app.get("/api/v2/templates/niches")
    def get_v2_niches():
        from packages.creator_engine.templates import TOP_10_NICHES
        return {"niches": TOP_10_NICHES}

    @app.post("/api/v2/templates/generate")
    def generate_v2_template(req: V2TemplateGenerateRequest):
        from packages.creator_engine.templates import TemplateGenerator
        generator = TemplateGenerator()
        blueprint = generator.generate_blueprint(
            topic=req.topic,
            niche_id=req.niche_id,
            target_duration_s=req.target_duration_s,
            aspect_ratio=req.aspect_ratio,
            mode=req.mode,
            custom_instructions=req.custom_instructions
        )
        return blueprint

    return app


def app_factory() -> FastAPI:
    return create_app()
