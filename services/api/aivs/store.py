"""Project + job persistence (SQLite) with workspace files as the source of large data."""
from __future__ import annotations
import json, sqlite3, uuid
from pathlib import Path
from .workspace import Workspace, now

ACTIVE_STATES = ("queued", "analyzing", "planning", "awaiting_approval", "generating_assets", "generating_narration",
                 "rendering_scenes", "assembling", "quality_check")
TERMINAL_STATES = ("completed", "failed", "cancelled")


class Store:
    def __init__(self, conn: sqlite3.Connection, projects_dir: Path):
        self.conn, self.projects_dir = conn, projects_dir

    def workspace(self, project_id: str) -> Workspace:
        return Workspace(self.projects_dir / project_id)

    # ---- projects
    def create_project(self, title: str, script: str, settings: dict) -> dict:
        pid = uuid.uuid4().hex[:12]
        t = now()
        self.conn.execute("INSERT INTO projects VALUES (?,?,?,?,?,?)", (pid, title, "draft", json.dumps(settings), t, t))
        p = self.get_project(pid)
        self.workspace(pid).create(p, script)
        return p

    def _row_project(self, r) -> dict:
        return {"id": r["id"], "title": r["title"], "status": r["status"], "settings": json.loads(r["settings_json"]),
                "created_at": r["created_at"], "updated_at": r["updated_at"]}

    def get_project(self, pid: str) -> dict | None:
        r = self.conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
        return self._row_project(r) if r else None

    def list_projects(self) -> list[dict]:
        return [self._row_project(r) for r in self.conn.execute("SELECT * FROM projects ORDER BY created_at DESC")]

    def set_script(self, pid: str, script: str) -> None:
        self.workspace(pid).write_script(script)
        self.conn.execute("UPDATE projects SET updated_at=? WHERE id=?", (now(), pid))

    # ---- jobs
    def create_job(self, pid: str, kind: str) -> dict:
        jid = uuid.uuid4().hex[:12]
        t = now()
        self.conn.execute("INSERT INTO jobs (id,project_id,kind,state,created_at,updated_at) VALUES (?,?,?,?,?,?)",
                          (jid, pid, kind, "queued", t, t))
        return self.get_job(jid)

    def get_job(self, jid: str) -> dict | None:
        r = self.conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["checkpoint"] = json.loads(d.pop("checkpoint_json")) if d["checkpoint_json"] else None
        return d

    def list_jobs(self, pid: str | None = None, limit: int = 100) -> list[dict]:
        q, a = "SELECT id FROM jobs", ()
        if pid:
            q, a = q + " WHERE project_id=?", (pid,)
        ids = [r["id"] for r in self.conn.execute(q + " ORDER BY created_at DESC LIMIT ?", a + (limit,))]
        return [self.get_job(i) for i in ids]

    def update_job(self, jid: str, **f) -> None:
        if "checkpoint" in f:
            f["checkpoint_json"] = json.dumps(f.pop("checkpoint"))
        f["updated_at"] = now()
        cols = ", ".join(f"{k}=?" for k in f)
        self.conn.execute(f"UPDATE jobs SET {cols} WHERE id=?", (*f.values(), jid))

    def log(self, jid: str, level: str, message: str) -> None:
        self.conn.execute("INSERT INTO job_logs (job_id,ts,level,message) VALUES (?,?,?,?)", (jid, now(), level, message))

    def job_logs(self, jid: str) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT ts,level,message FROM job_logs WHERE job_id=? ORDER BY id", (jid,))]

    def recover_interrupted(self) -> int:
        """Jobs left in an active state by a previous process cannot still be running: mark them failed (resumable)."""
        cur = self.conn.execute(
            f"UPDATE jobs SET state='failed', error='Interrupted by application restart. Retry the job to resume from its checkpoint.', updated_at=? "
            f"WHERE state IN ({','.join('?' * len(ACTIVE_STATES))})", (now(), *ACTIVE_STATES))
        return cur.rowcount
