# Phase 1 — Environment and Compatibility Audit (2026-10-27, Linux)

## Host
Ubuntu, 12 threads, 14 GiB RAM, 385 GB free, no NVIDIA GPU used.

## Installed
Python 3.14.4, Node 22.23.4, npm 10.9.9, pnpm 12.4.1, FFmpeg/ffprobe 8.0.1 (libx264, aac, libass `subtitles`, `drawtext`), git 2.53, aws-cli 2.31.35, SQLite 3.46.1.

## Missing
uv, Docker (not needed), Rust/cargo (not needed, prebuilt binaries used), any TTS engine, any transcription tool.

## EffectCraft v0.17.0 (github.com/storytold/effectcraft, release tarball, SHA256 verified)
- Binary: `effectcraft-cli` (in the linux tarball). MCP: `effectcraft-cli mcp`, stdio, protocol 2024-11-05, headless, **27 tools**.
- VERIFIED on Linux, CPU only: comp.new, layer.newSolid, get_comp/get_layer, add_keyframe (Transform/Position, linear),
  save_project (.ecproj JSON), `effectcraft-cli render --comp C --out f.mp4 --format h264` (60 frames, 640x360@30, 0.18 s).
  Frame at t=1s showed the box at the interpolated midpoint.
- **Rendering is a CLI operation, not an MCP tool** (MCP only has render_frame). The adapter uses MCP for editing and the CLI for final render.
- 122 `comp.`/`layer.` commands; effects registry via list_effects; scripting via run_script (JS, After Effects-style).

## FilmCraft v0.13.0 (github.com/storytold/filmcraft, SHA256 verified)
- `filmcraft-cli mcp`, stdio, **17 tools**, 710 engine commands. Several tools (ui_*) need the live app and are unused.
- VERIFIED: file.newProject, file.newSequence (custom size/fps), file.import, timeline.place (V1/A1),
  captions.newTrack/add, file.saveAs (.fcproj), file.exportMedia h264 -> 640x360, 30 fps, H.264 + AAC, 2.0 s.
- **LIMITATION: caption tracks are NOT burned into the exported MP4** (frame at 1 s showed no text).
  Decision: burn captions via FFmpeg `subtitles` filter (ASS) after FilmCraft export, or ship an SRT/VTT sidecar.
- Note: `filmcraft-cli inspect` in a separate process shows an empty project; state lives only within a `run` process or MCP session.
  The adapter must build and export in one session (or reopen the saved .fcproj).

## AWS Bedrock
Credentials work (region ap-southeast-2). `list-foundation-models` returns many models incl. anthropic.claude-sonnet-5-5,
anthropic.claude-haiku-5-5, amazon.nova-2-lite-v1:0. Listing does not prove invocation rights; invocation is tested in Phase 3.
Polly: **AccessDenied** for this IAM user, so Polly is not usable for TTS without a policy change.

## Open decisions
- TTS: candidates are Piper (local, CPU, offline) or user-supplied audio. To be verified in Phase 5.
- Transcription/alignment for captions: to be verified in Phase 5 (faster-whisper or whisper.cpp on CPU, or Bedrock).
- Pexels/Pixabay API keys not yet configured; stock footage stays optional.

## Architecture
Next.js UI -> FastAPI (SQLite + project workspaces) -> in-process worker -> Director (Bedrock, schema-validated) -> deterministic
executors (EffectCraft adapter, FFmpeg, FilmCraft adapter) -> QC. Large media only on filesystem under `projects/`.
Stages: 2 app skeleton, 3 storyboard, 4 adapters, 5 e2e 30s, 6 QC/recovery, 7 longer benchmark, 8 Windows.
