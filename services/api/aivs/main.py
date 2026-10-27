"""FastAPI app: projects, storyboards, production pipeline, scene review, quality reports, exports, and health."""
from __future__ import annotations
import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError
from .config import load_settings, Settings, REPO_ROOT
from .db import connect, migrate
from .store import Store, TERMINAL_STATES
from .worker import Worker
from .models import ProjectCreate, ScriptUpdate, RESOLUTIONS
from .health import health
from .director import Director
from .storyboard import Storyboard, store as sbstore
from .analysis import analyze_script, load_sample_scripts, SUPPORTED_SCRIPT_FORMATS


class TopicRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    target_duration_s: int = Field(default=30, ge=10, le=900)


class SceneRegenerateRequest(BaseModel):
    visual_correction: str | None = Field(default=None, max_length=500)
    visual_type: str | None = None
    visual_description: str | None = Field(default=None, max_length=900)


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

    app = FastAPI(title="AIVideoStudio API", version="0.2.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"])

    def store() -> Store:
        return app.state.store

    @app.get("/api/health")
    def get_health(aws: bool = False):
        return health(settings, include_aws=aws)

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
        return store().list_projects()

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
            store().workspace(pid).write_json("reports/script_generation.json", {
                "model_id": usage.model_id, "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens, "latency_s": usage.latency_s
            })
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
        # Carry over rendered_scenes checkpoint from the most recent production job so approved scenes are reused
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
        out: dict = {"workspace_path": str(ws.root)}
        for name in ("quality_report", "director_usage", "caption_validation", "asset_discovery", "script_analysis"):
            f = ws.root / "reports" / f"{name}.json"
            if f.is_file():
                out[name] = json.loads(f.read_text(encoding="utf-8"))
        mf = ws.root / "manifest.json"
        if mf.is_file():
            out["manifest"] = json.loads(mf.read_text(encoding="utf-8"))
        return out

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
        return store().list_jobs(project_id)

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

    return app


def app_factory() -> FastAPI:
    return create_app()
