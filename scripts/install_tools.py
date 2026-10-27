#!/usr/bin/env python3
"""Cross-platform EffectCraft & FilmCraft installer and SHA-256 verifier for Linux (x86_64) and Windows (x64)."""
from __future__ import annotations
import argparse, hashlib, os, platform, shutil, tarfile, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"

RELEASES = {
    "effectcraft": {
        "version": "0.17.0",
        "base_url": "https://github.com/storytold/effectcraft/releases/download/v0.17.0",
        "linux": "effectcraft-0.17.0-linux-x86_64.tar.gz",
        "windows": "effectcraft-0.17.0-windows-x64-portable.zip",
    },
    "filmcraft": {
        "version": "0.13.0",
        "base_url": "https://github.com/storytold/filmcraft/releases/download/v0.13.0",
        "linux": "filmcraft-0.13.0-linux-x86_64.tar.gz",
        "windows": "filmcraft-0.13.0-windows-x64-portable.zip",
    },
}


def _platform_key(override: str | None = None) -> str:
    if override:
        return override
    sys_name = platform.system().lower()
    if "windows" in sys_name or os.name == "nt":
        return "windows"
    return "linux"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "AIVideoStudio-ToolInstaller/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
        shutil.copyfileobj(resp, out)


def _fetch_expected_sha256(base_url: str, filename: str) -> str | None:
    try:
        req = urllib.request.Request(f"{base_url}/SHA256SUMS.txt", headers={"User-Agent": "AIVideoStudio-ToolInstaller/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", errors="replace")
        for line in text.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[-1].lstrip("*") == filename:
                return parts[0].lower()
    except Exception:
        return None
    return None


def _find_cli(tool: str, plat: str) -> Path | None:
    exe = f"{tool}-cli" + (".exe" if plat == "windows" else "")
    tdir = TOOLS_DIR / tool
    if not tdir.is_dir():
        return None
    for hit in sorted(tdir.rglob(exe)):
        if hit.is_file():
            return hit
    return None


def install_tool(tool: str, plat: str, force: bool = False) -> Path:
    existing = _find_cli(tool, plat)
    if existing and not force:
        print(f"[{tool}] already installed: {existing}")
        return existing

    spec = RELEASES[tool]
    archive_name = spec[plat]
    url = f"{spec['base_url']}/{archive_name}"
    tdir = TOOLS_DIR / tool
    tdir.mkdir(parents=True, exist_ok=True)
    archive_path = tdir / archive_name

    print(f"[{tool}] downloading {url} ...")
    _download(url, archive_path)
    expected = _fetch_expected_sha256(spec["base_url"], archive_name)
    actual = _sha256_file(archive_path)
    if expected and actual != expected:
        archive_path.unlink(missing_ok=True)
        raise RuntimeError(f"SHA-256 mismatch for {archive_name}: expected {expected}, got {actual}")
    print(f"[{tool}] SHA-256 verified: {actual[:16]}...")

    if archive_name.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(tdir)
    elif archive_name.endswith(".zip"):
        extract_sub = tdir / archive_name[:-4]
        extract_sub.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(extract_sub)

    cli = _find_cli(tool, plat)
    if not cli:
        raise RuntimeError(f"Extracted {archive_name}, but could not locate {tool}-cli binary under {tdir}")
    if plat != "windows":
        cli.chmod(cli.stat().st_mode | 0o111)
    print(f"[{tool}] ready at {cli}")
    return cli


def main() -> None:
    ap = argparse.ArgumentParser(description="Install or verify EffectCraft and FilmCraft CLI binaries.")
    ap.add_argument("--platform", choices=["linux", "windows"], default=None, help="Override target platform")
    ap.add_argument("--verify-only", action="store_true", help="Only check whether binaries are already present")
    ap.add_argument("--force", action="store_true", help="Re-download even if already installed")
    args = ap.parse_args()

    plat = _platform_key(args.platform)
    for tool in ("effectcraft", "filmcraft"):
        if args.verify_only:
            cli = _find_cli(tool, plat)
            if not cli:
                raise SystemExit(f"Missing {tool}-cli for {plat} under {TOOLS_DIR / tool}")
            print(f"[{tool}] verified: {cli}")
        else:
            install_tool(tool, plat, force=args.force)


if __name__ == "__main__":
    main()
