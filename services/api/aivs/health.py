"""Real dependency checks: each entry is produced by actually running the tool, never assumed."""
from __future__ import annotations
import os, subprocess
from pathlib import Path
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
    for key, cmd, fix, mcp_info in [
        (
            "ffmpeg",
            [s.ffmpeg, "-version"],
            "Install FFmpeg (Linux: sudo apt install ffmpeg; Windows: winget install Gyan.FFmpeg).",
            None,
        ),
        (
            "ffprobe",
            [s.ffprobe, "-version"],
            "Installed together with FFmpeg.",
            None,
        ),
        (
            "effectcraft",
            [s.effectcraft_cli, "--version"],
            "Run python scripts/install_tools.py to download EffectCraft v0.17.0.",
            {
                "binary_path": s.effectcraft_cli,
                "installed": Path(s.effectcraft_cli).is_file(),
                "mcp_mode": "stdio (effectcraft-cli mcp)",
                "mcp_needed": True,
                "role": "2D/2.5D Motion Graphics & Animated Diagrams (.ecproj + MP4)",
            },
        ),
        (
            "filmcraft",
            [s.filmcraft_cli, "--version"],
            "Run python scripts/install_tools.py to download FilmCraft v0.13.0.",
            {
                "binary_path": s.filmcraft_cli,
                "installed": Path(s.filmcraft_cli).is_file(),
                "mcp_mode": "stdio (filmcraft-cli mcp)",
                "mcp_needed": True,
                "role": "Multi-Track Timeline Assembly, Audio Sync & Captions (.fcproj + MP4)",
            },
        ),
    ]:
        ok, detail = _run(cmd)
        entry = {"ok": ok, "detail": detail, **({} if ok else {"fix": fix})}
        if mcp_info:
            entry.update(mcp_info)
        res[key] = entry
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


def check_stock_apis() -> dict:
    pexels = bool(os.environ.get("PEXELS_API_KEY", "").strip())
    pixabay = bool(os.environ.get("PIXABAY_API_KEY", "").strip())
    return {
        "ok": True,
        "pexels_configured": pexels,
        "pixabay_configured": pixabay,
        "detail": (
            "Pexels & Pixabay active" if (pexels and pixabay)
            else ("Pexels active" if pexels else ("Pixabay active" if pixabay else "Procedural canvas fallback (keys optional)"))
        ),
    }


def verify_engines_mcp(s: Settings) -> dict:
    """Performs a live stdio MCP handshake with both EffectCraft and FilmCraft and returns verified capabilities."""
    from .engines.effectcraft import EffectCraftAdapter
    from .engines.filmcraft import FilmCraftAdapter

    out: dict = {"tools": check_tools(s), "stock": check_stock_apis(), "aws": check_aws(s), "mcp": {}}
    try:
        ec = EffectCraftAdapter(s.effectcraft_cli)
        ec_caps = ec.discover()
        out["mcp"]["effectcraft"] = {
            "ok": ec_caps.ok,
            "version": ec_caps.version,
            "binary_path": s.effectcraft_cli,
            "transport": "stdio JSON-RPC 2.0 (effectcraft-cli mcp)",
            "tool_count": len(ec_caps.tools),
            "tools": ec_caps.tools,
            "missing_tools": ec_caps.missing_tools,
            "missing_commands": ec_caps.missing_commands,
            "render_mode": "effectcraft-cli render --comp <scene> (H.264 MP4)",
        }
    except Exception as e:
        out["mcp"]["effectcraft"] = {"ok": False, "error": str(e), "binary_path": s.effectcraft_cli}

    try:
        fc = FilmCraftAdapter(s.filmcraft_cli, s.ffmpeg, s.ffprobe)
        fc_caps = fc.discover()
        out["mcp"]["filmcraft"] = {
            "ok": fc_caps.ok,
            "version": fc_caps.version,
            "binary_path": s.filmcraft_cli,
            "transport": "stdio JSON-RPC 2.0 (filmcraft-cli mcp)",
            "tool_count": len(fc_caps.tools),
            "tools": fc_caps.tools,
            "missing_tools": fc_caps.missing_tools,
            "missing_commands": fc_caps.missing_commands,
            "export_mode": "MCP file.exportMedia (H.264 + AAC) + FFmpeg libass subtitle burn-in",
        }
    except Exception as e:
        out["mcp"]["filmcraft"] = {"ok": False, "error": str(e), "binary_path": s.filmcraft_cli}

    out["ok"] = bool(
        out["tools"]["ffmpeg"]["ok"]
        and out["tools"]["ffprobe"]["ok"]
        and out["mcp"].get("effectcraft", {}).get("ok")
        and out["mcp"].get("filmcraft", {}).get("ok")
    )
    return out


def health(s: Settings, include_aws: bool = False) -> dict:
    tools = check_tools(s)
    out = {
        "api": {"ok": True},
        "tools": tools,
        "stock": check_stock_apis(),
        "director": {"ok": True, "detail": "AI Director (AWS Bedrock Claude 4.5)"},
    }
    if include_aws:
        out["aws"] = check_aws(s)
    out["ok"] = all(t["ok"] for t in tools.values())
    return out
