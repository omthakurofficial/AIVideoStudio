# AIVideoStudio

Local-first, AI-directed educational and documentary video production system.

## Features
- **AI Director (`services/api/aivs/director.py`)**: Analyzes scripts or generates scripts from a topic via AWS Bedrock (`au.anthropic.claude-sonnet-4-5-20250929-v1:0` / `haiku-4-5`), plans scene-by-scene visual storytelling, and validates output against `packages/contracts/storyboard.v1.schema.json` with deterministic narration-coverage ($\ge 92\%$ LCS) and duration checks.
- **Custom Motion Graphics (`services/api/aivs/engines/effectcraft.py`, `scene_renderer.py`)**: Compiles storyboard scenes (`animated_diagram`, `architecture`, `chart`, `timeline`, `layered_motion`, etc.) into EffectCraft v0.17.0 compositions via headless MCP (`effectcraft-cli mcp`), saves editable `.ecproj` files, and renders 1080p/9:16 H.264 clips via `effectcraft-cli render`.
- **Narration & Word-Level Synchronized Captions (`services/api/aivs/engines/narration.py`)**: Supports neural TTS (`edge-tts` with `WordBoundary` alignment and SHA-256 audio caching), user-supplied audio (`user_audio`), and offline synthetic fallback (`voice="synthetic"`). Automatically rescales scene and animation timings to match measured audio durations and validates SRT captions for coverage, non-overlap, CPS, and safe-area bounds.
- **Timeline Assembly (`services/api/aivs/engines/filmcraft.py`)**: Places rendered scenes, narration tracks, and caption tracks into FilmCraft v0.13.0 via headless MCP (`filmcraft-cli mcp`), saves editable `assembly/project.fcproj`, exports H.264 + AAC MP4, and burns in styled ASS subtitles via FFmpeg (`libass`).
- **Automated Quality Control & Targeted Scene Repair (`services/api/aivs/qc.py`, `pipeline.py`)**: Inspects every rendered scene for resolution, frame rate, duration, non-blank content, animation motion across early/mid/late frames, and element overlap. Automatically repairs and re-renders failed scenes (`v2`) while preserving approved scenes and cached narration.

## Quick Setup — Linux
```bash
bash scripts/setup_linux.sh
.venv/bin/python scripts/dev.py   # API: http://127.0.0.1:8000/docs | UI: http://localhost:3000
```

## Quick Setup — Windows (RTX 3060 Target)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
.\.venv\Scripts\python.exe scripts\dev.py
```
See [`docs/phase8-windows-migration.md`](docs/phase8-windows-migration.md) for full Windows migration and workspace portability details.

## Verification & Tests
```bash
# Verify EffectCraft & FilmCraft binaries and MCP handshakes
.venv/bin/python scripts/install_tools.py --verify-only
.venv/bin/python scripts/mcp_probe.py

# Run all 22 backend unit & integration tests (API, Storyboard, Engines, Pipeline & QC Repair)
.venv/bin/pytest services/api/tests/ -q

# Real headless Chrome E2E tests (with scripts/dev.py running)
.venv/bin/python tests/e2e/test_ui_phase2.py
.venv/bin/python tests/e2e/test_ui_phase3.py
.venv/bin/python tests/e2e/test_ui_phase5_6.py
.venv/bin/python tests/e2e/test_benchmark_phase7.py
```

## Architecture & Phase Documentation
- [`docs/phase1-audit.md`](docs/phase1-audit.md) — Environment, EffectCraft v0.17.0, FilmCraft v0.13.0, and AWS Bedrock capability audit
- [`docs/phase3-storyboard.md`](docs/phase3-storyboard.md) — Versioned storyboard contract, Bedrock provider abstraction, and AI Director validation loop
- [`docs/phase4-engines.md`](docs/phase4-engines.md) — EffectCraft & FilmCraft headless MCP adapters and scene compiler
- [`docs/phase5-6-production-qc.md`](docs/phase5-6-production-qc.md) — End-to-end 30s production, neural narration, synchronized captions, QC, and single-scene regeneration
- [`docs/phase7-benchmark.md`](docs/phase7-benchmark.md) — 60–90s educational video benchmark, timing, resource usage, and token cost analysis
- [`docs/phase8-windows-migration.md`](docs/phase8-windows-migration.md) — Windows + NVIDIA RTX 3060 setup and cross-platform migration guide
