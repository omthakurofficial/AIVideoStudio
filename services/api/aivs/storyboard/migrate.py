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


def load_storyboard(data: dict) -> tuple[Storyboard, bool]:
    data, changed = migrate_data(data)
    return Storyboard.model_validate(data), changed
