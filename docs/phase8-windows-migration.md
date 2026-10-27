# Phase 8 — Windows + NVIDIA RTX 3060 Migration & Setup Guide

## 1. Portability Architecture
AIVideoStudio was designed from Phase 1 to run identically across the initial Linux desktop environment (AMD Ryzen 5000U, integrated graphics, 14 GiB RAM) and the target Windows environment (NVIDIA RTX 3060):
- **Relative Path Resolution (`services/api/aivs/config.py`)**:
  - `REPO_ROOT` is computed dynamically via `Path(__file__).resolve().parents[3]`.
  - `_find_tool` automatically appends `.exe` when `os.name == "nt"` and searches `tools/<tool>/**/<tool>-cli.exe` before falling back to `PATH` or explicit `AIVS_EFFECTCRAFT_CLI` / `AIVS_FILMCRAFT_CLI` environment variables.
- **Portable Workspace & Database State**:
  - Project metadata (`projects/<id>/project.json`), storyboards (`storyboard.json`), manifests (`manifest.json`), and SQLite job checkpoints (`data/aivs.sqlite3`) store **project-relative POSIX paths** (e.g., `scenes/s01_v1/scene.mp4`, `renders/previews/s01.png`, `renders/final.mp4`).
  - Copying `data/aivs.sqlite3` and `projects/` from Linux to Windows preserves all projects, storyboards, cached narration, rendered scenes, and exports without path rewriting.
- **Windows-Safe FFmpeg Subtitle Filter (`services/api/aivs/engines/filmcraft.py`)**:
  - `_burn_subtitles` executes `ffmpeg` with `cwd=str(srt_path.parent)` and `-vf subtitles=captions.srt:force_style='...'`, avoiding Windows drive-letter colon (`C:\`) escaping issues in `libass` filtergraphs.

## 2. Prerequisites on Windows (RTX 3060)
1. **Python 3.12+** (`winget install Python.Python.3.12`)
2. **Node.js 22 LTS & pnpm** (`winget install OpenJS.NodeJS.LTS` then `corepack enable && corepack prepare pnpm@latest --activate`)
3. **FFmpeg (Full Build with `libass` and `libx264` / `h264_nvenc`)** (`winget install Gyan.FFmpeg`)
4. **AWS Credentials**:
   - Configure `~/.aws/credentials` (`aws configure`) or set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION=ap-southeast-2` in `.env`.

## 3. One-Command Windows Setup
From PowerShell in the repository root (`AIVideoStudio\`):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```
This script:
1. Creates `.venv` and installs locked Python dependencies from `requirements.lock.txt`.
2. Runs `scripts\install_tools.py --platform windows`, which downloads and SHA-256 verifies:
   - `effectcraft-0.17.0-windows-x64-portable.zip` $\rightarrow$ `tools\effectcraft\...\effectcraft-cli.exe`
   - `filmcraft-0.13.0-windows-x64-portable.zip` $\rightarrow$ `tools\filmcraft\...\filmcraft-cli.exe`
3. Installs Next.js dependencies in `apps\web` via `pnpm`.
4. Copies `.env.example` to `.env` (if not present) and runs `scripts\mcp_probe.py` to verify both MCP engines on Windows.

## 4. Starting the Application on Windows
```powershell
.\.venv\Scripts\python.exe scripts\dev.py
```
- Web UI: `http://localhost:3000`
- FastAPI Docs & Health Check: `http://127.0.0.1:8000/api/health?aws=true`

## 5. Migrating Existing Projects from Linux to Windows
1. Copy `data/aivs.sqlite3` and `projects/<project-id>/` into the Windows repository's `data\` and `projects\` folders.
2. Start the server (`.\.venv\Scripts\python.exe scripts\dev.py`) and open `http://localhost:3000`.
3. Existing exports (`renders/final.mp4`), scene previews (`renders/previews/*.png`), and single-scene regeneration (`scenes/<id>_v<N>/`) work immediately without re-rendering unchanged scenes.
