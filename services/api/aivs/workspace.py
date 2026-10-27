"""Filesystem project workspace + provenance manifest. Paths are relative inside manifests (portable)."""
from __future__ import annotations
import json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path

SUBDIRS = ["assets", "narration", "scenes", "renders", "captions", "assembly", "reports"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


class Workspace:
    def __init__(self, root: Path):
        self.root = root

    def create(self, project: dict, script: str) -> None:
        for d in SUBDIRS:
            (self.root / d).mkdir(parents=True, exist_ok=True)
        self.write_project(project)
        self.write_script(script)
        if not (self.root / "manifest.json").exists():
            atomic_write(self.root / "manifest.json", json.dumps({"version": 1, "assets": []}, indent=2))

    def write_project(self, project: dict) -> None:
        atomic_write(self.root / "project.json", json.dumps(project, indent=2))

    def write_script(self, script: str) -> None:
        atomic_write(self.root / "script.md", script)

    def read_script(self) -> str:
        p = self.root / "script.md"
        return p.read_text(encoding="utf-8") if p.is_file() else ""

    def write_json(self, rel: str, data: dict) -> None:
        atomic_write(self.root / rel, json.dumps(data, indent=2))

    def add_asset(self, rel_path: str, kind: str, provenance: dict) -> None:
        mf = self.root / "manifest.json"
        m = json.loads(mf.read_text(encoding="utf-8"))
        m["assets"] = [a for a in m["assets"] if a["path"] != rel_path]
        m["assets"].append({"path": rel_path, "kind": kind, "created_at": now(), "provenance": provenance})
        atomic_write(mf, json.dumps(m, indent=2))
