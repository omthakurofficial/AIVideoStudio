# AIVideoStudio

Local-first, AI-directed video production. Status: **Phase 2 complete** (project creation, script persistence, job
status, health checks, basic UI). Storyboard generation, rendering and assembly are not implemented yet.
See `docs/phase1-audit.md` for verified tool capabilities and known limitations.

## Linux setup
```bash
sudo apt install ffmpeg git python3-venv nodejs npm && npm i -g pnpm      # if missing
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
(cd apps/web && pnpm install)
# EffectCraft + FilmCraft: download Linux tarballs from github.com/storytold/{effectcraft,filmcraft}/releases,
# verify SHA256SUMS.txt, extract under tools/effectcraft and tools/filmcraft (auto-detected).
python scripts/dev.py          # API http://127.0.0.1:8000/docs, UI http://localhost:3000
```
## Windows setup (untested until Phase 8)
```powershell
winget install Gyan.FFmpeg Python.Python.3.12 OpenJS.NodeJS; npm i -g pnpm
python -m venv .venv; .venv\Scripts\pip install -r requirements.txt
cd apps\web; pnpm install; cd ..\..
# Extract the windows-x64 portable zips of EffectCraft/FilmCraft under tools\ or set AIVS_*_CLI in .env
python scripts\dev.py
```
## Tests
```bash
cd services/api && ../../.venv/bin/python -m pytest          # backend unit/integration
.venv/bin/python tests/e2e/test_ui_phase2.py                 # real Chrome UI test (dev servers must be running)
```
## Layout
`apps/web` Next.js UI · `services/api` FastAPI + SQLite migrations + in-process worker · `projects/` per-project workspaces
(gitignored) · `data/` SQLite DB (gitignored) · `tools/` downloaded binaries (gitignored).
Secrets are read from the environment/AWS credential chain, never stored in the repo or returned by the API.
