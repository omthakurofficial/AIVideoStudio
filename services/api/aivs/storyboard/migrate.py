"""Storyboard schema migrations. To change the schema: bump SCHEMA_VERSION, add `MIGRATIONS[old] = fn(dict)->dict`
that returns data at version old+1, and add a fixture test. Files are migrated on load and re-saved at the new version;
the pre-migration file is kept in storyboard_history/."""
from __future__ import annotations
from typing import Callable
from .schema import SCHEMA_VERSION, Storyboard

MIGRATIONS: dict[int, Callable[[dict], dict]] = {}


class SchemaVersionError(ValueError):
    pass


def migrate_data(data: dict, target: int = SCHEMA_VERSION, migrations: dict | None = None) -> tuple[dict, bool]:
    migrations = MIGRATIONS if migrations is None else migrations
    v = data.get("schema_version")
    if not isinstance(v, int):
        raise SchemaVersionError("storyboard has no integer schema_version")
    if v > target:
        raise SchemaVersionError(f"storyboard schema_version {v} is newer than supported {target}; upgrade AIVideoStudio")
    changed = False
    while v < target:
        if v not in migrations:
            raise SchemaVersionError(f"no migration from schema_version {v}")
        data = migrations[v](dict(data))
        v += 1
        data["schema_version"] = v
        changed = True
    return data, changed


def _backfill_connectors(data: dict) -> bool:
    changed = False
    for sc in data.get("scenes", []):
        els = sc.get("visual_elements", [])
        kinds = {e["id"]: e["kind"] for e in els if "id" in e and "kind" in e}
        pairs = [(r["source"], r["target"]) for r in sc.get("element_relationships", [])
                 if r.get("source") in kinds and r.get("target") in kinds and r.get("source") != r.get("target")
                 and kinds.get(r["source"]) not in ("arrow", "route", "packet")
                 and kinds.get(r["target"]) not in ("arrow", "route", "packet")]
        non_conn = [e["id"] for e in els if kinds.get(e.get("id")) not in ("arrow", "route", "packet")]
        idx = 0
        for e in els:
            if e.get("kind") in ("arrow", "route"):
                props = e.setdefault("props", {})
                if props.get("from") not in kinds or props.get("to") not in kinds:
                    if idx < len(pairs):
                        props["from"], props["to"] = pairs[idx]
                        idx += 1
                        changed = True
                    elif len(non_conn) >= 2:
                        props["from"], props["to"] = non_conn[0], non_conn[1]
                        changed = True
    return changed


def load_storyboard(data: dict) -> tuple[Storyboard, bool]:
    data, changed = migrate_data(data)
    if _backfill_connectors(data):
        changed = True
    return Storyboard.model_validate(data), changed
