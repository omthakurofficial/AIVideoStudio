"""Storyboard persistence in the project workspace: storyboard.json + storyboard_history/rNNN.json."""
from __future__ import annotations
import json
from pathlib import Path
from ..workspace import atomic_write
from .schema import Storyboard
from .migrate import load_storyboard


def path(root: Path) -> Path:
    return root / "storyboard.json"


def load(root: Path) -> Storyboard | None:
    p = path(root)
    if not p.is_file():
        return None
    raw = json.loads(p.read_text(encoding="utf-8"))
    sb, changed = load_storyboard(raw)
    if changed:  # keep the pre-migration file, then re-save at the current version
        hist = root / "storyboard_history"
        hist.mkdir(exist_ok=True)
        atomic_write(hist / f"pre_migration_v{raw['schema_version']}.json", json.dumps(raw, indent=2))
        save(root, sb, bump=False)
    return sb


def save(root: Path, sb: Storyboard, bump: bool = True) -> Storyboard:
    cur = path(root)
    if bump and cur.is_file():
        prev = json.loads(cur.read_text(encoding="utf-8"))
        sb = sb.model_copy(update={"revision": prev.get("revision", 0) + 1})
    hist = root / "storyboard_history"
    hist.mkdir(exist_ok=True)
    atomic_write(hist / f"r{sb.revision:03d}.json", sb.model_dump_json(indent=2))
    atomic_write(cur, sb.model_dump_json(indent=2))
    return sb
