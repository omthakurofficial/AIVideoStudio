"""Portable configuration. All paths are resolved relative to the repo root unless overridden by env."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    projects_dir: Path
    db_path: Path
    tools_dir: Path
    effectcraft_cli: str
    filmcraft_cli: str
    ffmpeg: str
    ffprobe: str
    aws_region: str
    cors_origins: tuple[str, ...]


def _exe(name: str) -> str:
    return name + (".exe" if os.name == "nt" else "")


def _find_tool(env_var: str, tool: str) -> str:
    """Explicit env var wins, then tools/<tool>/**/bin/<tool>-cli under the repo, then PATH name."""
    if os.environ.get(env_var):
        return os.environ[env_var]
    base = REPO_ROOT / "tools" / tool
    if base.is_dir():
        for hit in sorted(base.rglob(_exe(f"{tool}-cli"))):
            return str(hit)
    return _exe(f"{tool}-cli")


def load_settings() -> Settings:
    _load_dotenv(REPO_ROOT / ".env")
    data = Path(os.environ.get("AIVS_DATA_DIR", REPO_ROOT / "data")).resolve()
    projects = Path(os.environ.get("AIVS_PROJECTS_DIR", REPO_ROOT / "projects")).resolve()
    return Settings(
        data_dir=data,
        projects_dir=projects,
        db_path=data / "aivs.sqlite3",
        tools_dir=REPO_ROOT / "tools",
        effectcraft_cli=_find_tool("AIVS_EFFECTCRAFT_CLI", "effectcraft"),
        filmcraft_cli=_find_tool("AIVS_FILMCRAFT_CLI", "filmcraft"),
        ffmpeg=os.environ.get("AIVS_FFMPEG", "ffmpeg"),
        ffprobe=os.environ.get("AIVS_FFPROBE", "ffprobe"),
        aws_region=os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", ""),
        cors_origins=tuple(os.environ.get("AIVS_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")),
    )
