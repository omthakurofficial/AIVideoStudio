"""Lightweight in-process worker draining queued jobs sequentially with checkpoint persistence."""
from __future__ import annotations
import threading, queue, traceback
from .store import Store
from .analysis import analyze_script
from .providers import ProviderError
from .storyboard import store as sbstore
from .director import DirectorError
from .pipeline import ProductionPipeline
from .pricing import record_token_usage


class Worker:
    def __init__(self, store_factory, director_factory=None, settings=None):
        self._factory = store_factory
        self._director_factory = director_factory
        self._settings = settings
        self._q: queue.Queue[str] = queue.Queue()
        self._cancel: set[str] = set()
        self._t = threading.Thread(target=self._run, daemon=True, name="aivs-worker")

    def start(self):
        self._t.start()

    def submit(self, job_id: str):
        self._cancel.discard(job_id)
        self._q.put(job_id)

    def cancel(self, job_id: str):
        self._cancel.add(job_id)

    def _run(self):
        store: Store = self._factory()
        while True:
            jid = self._q.get()
            try:
                self._execute(store, jid)
            except Exception as e:
                store.update_job(jid, state="failed", error=f"{type(e).__name__}: {e}")
                store.log(jid, "error", traceback.format_exc(limit=5))

    def _execute(self, store: Store, jid: str):
        job = store.get_job(jid)
        if not job or job["state"] != "queued":
            return
        if jid in self._cancel:
            store.update_job(jid, state="cancelled")
            return
        if job["kind"] == "analyze_script":
            store.update_job(jid, state="analyzing", current_step="Reading script", progress_done=0, progress_total=2)
            store.log(jid, "info", "Reading script.md")
            script = store.workspace(job["project_id"]).read_script()
            if not script.strip():
                raise ValueError("The project script is empty. Add a script, then run analysis again.")
            store.update_job(jid, current_step="Analyzing paragraphs", progress_done=1)
            result = analyze_script(script)
            store.workspace(job["project_id"]).write_json("reports/script_analysis.json", result)
            store.update_job(jid, state="completed", progress_done=2, current_step="Done", checkpoint={"report": "reports/script_analysis.json"})
            store.log(jid, "info", f"Analyzed {result['paragraph_count']} paragraphs, {result['total_words']} words")
        elif job["kind"] == "plan_storyboard":
            self._plan_storyboard(store, job)
        elif job["kind"] in ("produce_video", "regenerate_scene"):
            self._produce_video(store, job)
        else:
            raise ValueError(f"Unknown job kind '{job['kind']}'")

    def _plan_storyboard(self, store: Store, job: dict):
        jid, pid = job["id"], job["project_id"]
        ws, project = store.workspace(pid), store.get_project(pid)
        script = ws.read_script()
        if not script.strip():
            raise ValueError("The project script is empty. Add a script, then plan the storyboard again.")
        if self._director_factory is None:
            raise ValueError("No AI provider is configured for storyboard planning.")
        store.update_job(jid, state="planning", current_step="AI Director is planning scenes", progress_done=0, progress_total=3)
        store.log(jid, "info", "Script analysis (deterministic)")
        ws.write_json("reports/script_analysis.json", analyze_script(script))
        store.update_job(jid, progress_done=1, current_step="Waiting for AI Director")
        try:
            director = self._director_factory()
            sb, rep = director.plan(pid, script, project["settings"], log=lambda m: store.log(jid, "info", m))
        except (ProviderError, DirectorError) as e:
            usage = getattr(getattr(e, "report", None), "__dict__", None)
            if usage:
                ws.write_json("reports/director_usage.json", {**usage, "outcome": "failed"})
            hint = " The deterministic features of the app still work; retry when the provider is available." if getattr(e, "retryable", False) else ""
            raise ValueError(str(e) + hint)
        store.update_job(jid, progress_done=2, current_step="Saving storyboard")
        if project["settings"]["approval_mode"] == "automatic":
            sb = sb.model_copy(update={"approved": True})
        sb = sbstore.save(ws.root, sb, bump=True)
        ws.write_json("reports/director_usage.json", {**rep.__dict__, "outcome": "ok", "revision": sb.revision})
        record_token_usage(ws.root, "storyboard_planning", rep.model_id, rep.input_tokens, rep.output_tokens, rep.latency_s, rep.attempts)
        store.log(jid, "info", f"Storyboard r{sb.revision}: {len(sb.scenes)} scenes; tokens in/out {rep.input_tokens}/{rep.output_tokens}; {rep.attempts} attempt(s)")
        if sb.approved:
            store.update_job(jid, state="completed", progress_done=3, current_step="Storyboard ready (auto-approved)", checkpoint={"storyboard_revision": sb.revision})
        else:
            store.update_job(jid, state="awaiting_approval", progress_done=3, current_step="Waiting for your approval", checkpoint={"storyboard_revision": sb.revision})

    def _produce_video(self, store: Store, job: dict):
        if not self._settings:
            from .config import load_settings
            self._settings = load_settings()
        pipe = ProductionPipeline(self._settings, self._director_factory)
        ckpt = job.get("checkpoint") or {}
        force_ids = set(ckpt.get("force_scene_ids") or ())
        pipe.run_production(
            store, job,
            is_cancelled=lambda: job["id"] in self._cancel,
            force_scene_ids=force_ids,
        )
