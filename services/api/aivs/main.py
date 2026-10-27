"""FastAPI app: projects, jobs, health. Business logic lives in store/worker/services."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import load_settings, Settings
from .db import connect, migrate
from .store import Store, TERMINAL_STATES
from .worker import Worker
from .models import ProjectCreate, ScriptUpdate, RESOLUTIONS
from .health import health


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    def new_store() -> Store:
        return Store(connect(settings.db_path), settings.projects_dir)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.projects_dir.mkdir(parents=True, exist_ok=True)
        store = new_store()
        migrate(store.conn)
        store.recover_interrupted()
        worker = Worker(new_store)
        worker.start()
        # Re-queue jobs that were queued but never started.
        for j in store.list_jobs(limit=1000):
            if j["state"] == "queued":
                worker.submit(j["id"])
        app.state.store, app.state.worker, app.state.settings = store, worker, settings
        yield

    app = FastAPI(title="AIVideoStudio API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"])

    def store() -> Store:
        return app.state.store

    @app.get("/api/health")
    def get_health(aws: bool = False):
        return health(settings, include_aws=aws)

    @app.post("/api/projects", status_code=201)
    def create_project(body: ProjectCreate):
        p = store().create_project(body.title, body.script, body.settings.model_dump())
        w, h = RESOLUTIONS[body.settings.aspect_ratio]
        p["output"] = {"width": w, "height": h, "fps": body.settings.fps}
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
        p["script"] = store().workspace(pid).read_script()
        return p

    @app.put("/api/projects/{pid}/script")
    def put_script(pid: str, body: ScriptUpdate):
        _project(pid)
        store().set_script(pid, body.script)
        return {"ok": True, "chars": len(body.script)}

    @app.post("/api/projects/{pid}/jobs/analyze", status_code=202)
    def start_analysis(pid: str):
        _project(pid)
        job = store().create_job(pid, "analyze_script")
        app.state.worker.submit(job["id"])
        return job

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


def app_factory() -> FastAPI:  # uvicorn --factory aivs.main:app_factory
    return create_app()
