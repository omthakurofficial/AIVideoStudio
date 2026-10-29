#!/usr/bin/env python3
"""Start API (port 8000) and web UI (port 3000) together. Works on Linux and Windows.
Usage: python scripts/dev.py"""
import os, subprocess, sys, signal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PY = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PNPM = "pnpm.cmd" if os.name == "nt" else "pnpm"


def main() -> int:
    py = str(VENV_PY) if VENV_PY.exists() else sys.executable
    api = subprocess.Popen([py, "-m", "uvicorn", "--reload", "--factory", "aivs.main:app_factory", "--host", "127.0.0.1", "--port", "8000"],
                           cwd=ROOT / "services" / "api")
    web = subprocess.Popen([PNPM, "dev"], cwd=ROOT / "apps" / "web")
    print("\nAPI: http://127.0.0.1:8000/docs   UI: http://localhost:3000   (Ctrl+C to stop)\n")
    try:
        api.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for p in (api, web):
            if p.poll() is None:
                p.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
