# Phase 5 & 6 — End-to-End 30-Second Production, Quality Control & Targeted Recovery

## 1. Overview
Phases 5 and 6 complete the end-to-end automated production and quality-control loop in AIVideoStudio:
1. **Asset Discovery & Caching (`services/api/aivs/engines/assets.py`)**:
   - Supports Pexels (`PEXELS_API_KEY`) and Pixabay (`PIXABAY_API_KEY`) stock video/image discovery.
   - Downloads and validates media with `ffprobe`, stores files in a content-addressed cache (`data/asset_cache/`), copies resolved assets into `projects/<id>/assets/`, and records licence/provenance metadata in `manifest.json`.
   - When external stock keys are not configured or no match is found, automatically falls back to custom EffectCraft motion graphics and records the fallback in `reports/asset_discovery.json`.
2. **Narration & Word-Level Caption Synchronization (`services/api/aivs/engines/narration.py`)**:
   - Supports three narration modes: `none`, `user_audio` (`narration/user_<scene_id>.wav`), and `generate` (`edge-tts` neural voices, default `en-US-GuyNeural`, with automatic fallback to an offline speech-cadence synthesizer `voice="synthetic"` when offline).
   - Captures `WordBoundary` word-level offsets during neural synthesis and caches audio + word timings by SHA-256 of `(mode, voice, narration_text)` in `narration/<scene_id>_meta.json` so visual regenerations reuse existing narration audio without re-synthesizing.
   - `revise_storyboard_with_audio` idempotently rescales scene durations and animation/camera/text keyframe timings to match actual measured audio duration.
   - `build_synchronized_captions` and `validate_captions` generate phrase-aligned SRT captions (`captions/captions.srt`) and validate word coverage ($\ge 90\%$), non-overlap, duration bounds, reading speed (CPS), and safe-area line width/count (`reports/caption_validation.json`).
3. **Automated Quality Control & Targeted Scene Repair (`services/api/aivs/qc.py`)**:
   - `inspect_rendered_scene` verifies each rendered scene's `.ecproj` and `.mp4`, checks resolution, frame rate, and duration against the storyboard, extracts a preview frame to `renders/previews/<scene_id>.png`, verifies non-blank visual content (`nonbackground_fraction` and luminance `stddev`), verifies visible animation motion across early/mid/late sample frames, and checks element bounding boxes for overlap.
   - `repair_scene_for_retry` performs targeted deterministic repairs when a scene fails QC (removing invalid `asset_ref` layers, synthesizing missing nodes/pulse animations on blank scenes, or expanding layout spacing on overlapping elements) and re-renders only the failed scene (`v(N+1)`).
   - `inspect_final_video` validates the assembled `renders/final.mp4` and `assembly/project.fcproj` (`reports/quality_report.json`).
4. **Checkpointed Production Pipeline & Single-Scene Regeneration (`services/api/aivs/pipeline.py`)**:
   - `ProductionPipeline.run_production` executes `generating_assets` $\rightarrow$ `generating_narration` $\rightarrow$ `rendering_scenes` $\rightarrow$ `assembling` $\rightarrow$ `quality_check` $\rightarrow$ `completed`.
   - Tracks per-scene visual hashes (`_scene_visual_hash`) in job checkpoints so approved/unchanged scenes are reused without re-rendering when regenerating a single scene (`POST /api/projects/{pid}/scenes/{scene_id}/regenerate`).

## 2. Verification Results
- **Unit & Integration Test Suite (`services/api/tests/test_pipeline_qc.py`)**:
  - `test_pipeline_detects_blank_scene_repairs_and_completes`: Injects a deliberate blank render on `s01` (`v1`), verifies `inspect_rendered_scene` catches `scene_visually_blank`, applies `repair_scene_for_retry`, re-renders `s01` (`v2`), and completes final assembly and QC.
  - `test_single_scene_regeneration_preserves_other_scenes_and_narration`: Regenerates `s02` with a visual correction (`v2`) while verifying `s01` (`v2`) and `s03` (`v1`) and all narration WAV files are reused from cache.
  - All 22 backend tests across `test_api.py`, `test_storyboard.py`, `test_engines.py`, and `test_pipeline_qc.py` pass.
- **Real 30-Second Browser E2E (`tests/e2e/test_ui_phase5_6.py`)**:
  - Project `5f87e209ca0e` (`examples/devops_30s.md`) rendered end-to-end at `1920x1080 @ 30fps` (`29.65s`, H.264 + AAC neural narration + burned-in synchronized captions).
  - Tested single-scene visual correction on Scene 1 (`"Automated CI: Build, Test & Push"`), producing `s01` `v2` (`10.97s`) while reusing `s02` `v1` (`11.23s`) and `s03` `v1` (`7.43s`).
  - Visually verified extracted frames (`data/screenshots/final_30s_s01.png`, `final_30s_s02.png`, `final_30s_s03.png`) and UI screenshots (`phase5_6_completed.png`, `phase5_6_dashboard.png`).
