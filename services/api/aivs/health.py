"""Real dependency checks: each entry is produced by actually running the tool, never assumed."""
from __future__ import annotations
import shutil, subprocess
from .config import Settings


def _run(cmd: list[str], timeout=15) -> tuple[bool, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or r.stderr).strip().splitlines()
        return r.returncode == 0, (out[0] if out else "")
    except FileNotFoundError:
        return False, "not found"
    except subprocess.TimeoutExpired:
        return False, "timed out"


def check_tools(s: Settings) -> dict:
    res = {}
    for key, cmd, fix in [
        ("ffmpeg", [s.ffmpeg, "-version"], "Install FFmpeg (Linux: sudo apt install ffmpeg; Windows: winget install Gyan.FFmpeg)."),
        ("ffprobe", [s.ffprobe, "-version"], "Installed together with FFmpeg."),
        ("effectcraft", [s.effectcraft_cli, "--version"], "Run scripts/install_tools.py to download EffectCraft."),
        ("filmcraft", [s.filmcraft_cli, "--version"], "Run scripts/install_tools.py to download FilmCraft."),
    ]:
        ok, detail = _run(cmd)
        res[key] = {"ok": ok, "detail": detail, **({} if ok else {"fix": fix})}
    return res


def check_aws(s: Settings) -> dict:
    """Verifies credentials via STS without exposing identity details or secrets."""
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        return {"ok": False, "detail": "boto3 not installed"}
    try:
        sess = boto3.Session()
        region = s.aws_region or sess.region_name
        sess.client("sts", region_name=region).get_caller_identity()
        return {"ok": True, "detail": "credentials valid", "region": region}
    except (BotoCoreError, ClientError) as e:
        return {"ok": False, "detail": type(e).__name__, "fix": "Configure AWS credentials (aws configure) or set AWS_* env vars."}


def health(s: Settings, include_aws: bool = False) -> dict:
    tools = check_tools(s)
    out = {"api": {"ok": True}, "tools": tools}
    if include_aws:
        out["aws"] = check_aws(s)
    out["ok"] = all(t["ok"] for t in tools.values())
    return out
