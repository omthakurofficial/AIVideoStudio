"""Lightweight in-process worker: one background thread draining queued jobs sequentially."""
from __future__ import annotations
import threading, queue, traceback
from .store import Store
from .analysis import analyze_script


class Worker:
    def __init__(self, store_factory):
        self._factory = store_factory
        self._q: queue.Queue[str] = queue.Queue()
        self._cancel: set[str] = set()
        self._t = threading.Thread(target=self._run, daemon=True, name="aivs-worker")

    def start(self):
        self._t.start()

    def submit(self, job_id: str):
        self._q.put(job_id)

    def cancel(self, job_id: str):
        self._cancel.add(job_id)

    def _run(self):
        store: Store = self._factory()  # own connection for this thread
        while True:
            jid = self._q.get()
            try:
                self._execute(store, jid)
            except Exception as e:  # never let the worker die
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
        else:
            raise ValueError(f"Unknown job kind '{job['kind']}'")
