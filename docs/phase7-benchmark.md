# Phase 7 — Longer Video Benchmark (64.6-Second Global Cloud Architecture Video)

## 1. Benchmark Configuration
- **Project ID**: `27ae31a0422c` (`projects/27ae31a0422c/`)
- **Script**: [`examples/cloud_networking_75s.md`](../examples/cloud_networking_75s.md) (6 paragraphs covering Anycast DNS & Edge CDN, API Gateway security, L7 Load Balancing & Kubernetes horizontal pod autoscaling, Redis cache-aside & Primary-Replica database topology, OpenTelemetry observability, and automated canary rollback).
- **Settings**:
  - Output resolution & frame rate: `1920x1080` (`16:9`) @ `30 fps`
  - Visual style: `dark-neon`
  - Workflow mode: `automatic` (single-click planning $\rightarrow$ auto-approval $\rightarrow$ narration $\rightarrow$ captions $\rightarrow$ rendering $\rightarrow$ assembly $\rightarrow$ QC)
  - Narration: `generate` (`en-US-GuyNeural` via `edge-tts` with `WordBoundary` word-level timing)
  - Captions: `enabled` (`18` phrase-aligned segments burned into `renders/final.mp4` and exported as `captions/captions.srt`)

## 2. AI Director & Token Cost Metrics
Measured from `projects/27ae31a0422c/reports/director_usage.json`:
| Metric | Value |
|---|---|
| Model | `au.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Validation Attempts | `1` (passed schema, element-reference, narration-coverage, and duration checks on first attempt) |
| Input Tokens | `4,214` |
| Output Tokens | `11,589` |
| Bedrock Latency | `121.03 s` |
| Estimated Bedrock Cost | ~`\$0.186` USD (at `\$3.00 / 1M` input tokens + `\$15.00 / 1M` output tokens) |

## 3. Scene Breakdown & Timing Accuracy
| Scene | Topic | Planned Est. (s) | Measured Audio & Render (s) | Elements / Anim Steps | QC Status |
|---|---|---|---|---|---|
| `s01` | Anycast DNS & Edge CDN | `12.0 s` | `10.80 s` (`324` frames) | 9 elements / 9 steps | Passed (`v1`) |
| `s02` | Regional API Gateway (TLS, Auth, Rate Limit) | `13.0 s` | `11.43 s` (`343` frames) | 10 elements / 13 steps | Passed (`v1`) |
| `s03` | L7 Load Balancer & K8s Horizontal Pod Scaling | `13.0 s` | `10.90 s` (`327` frames) | 14 elements / 12 steps | Passed (`v1`) |
| `s04` | Redis Cache-Aside & Async DB Replication | `14.0 s` | `11.67 s` (`350` frames) | 11 elements / 13 steps | Passed (`v1`) |
| `s05` | OpenTelemetry Logs, Metrics & Traces | `12.0 s` | `10.37 s` (`311` frames) | 14 elements / 13 steps | Passed (`v1`) |
| `s06` | Error Budget Burn & Automated Canary Rollback | `11.0 s` | `9.40 s` (`282` frames) | 8 elements / 12 steps | Passed (`v1`) |
| **Total** | **Full Assembled Video (`renders/final.mp4`)** | **`75.0 s`** | **`64.57 s` (`1,937` frames)** | **66 elements / 72 steps** | **PASSED (8/8 checks)** |

## 4. System Resource & Stage Timing Profile (Linux CPU-Only Host)
Host: Ubuntu Linux, AMD Ryzen 5000U (12 logical threads, integrated graphics, 14 GiB RAM, no discrete GPU).
- **AI Director Planning (AWS Bedrock)**: `121.0 s`
- **Neural Narration Synthesis (`edge-tts`, 6 scenes)**: `8.4 s` (`0.0 s` on cached re-runs)
- **EffectCraft Scene Compilation & 1080p@30fps H.264 Rendering (6 scenes, 1,937 frames)**: `76.2 s` (~`12.7 s` per scene, or `25.4 fps` effective CPU render throughput)
- **FilmCraft Timeline Assembly + FFmpeg ASS Subtitle Burn-In + Final QC**: `16.8 s`
- **Peak System RAM Delta**: `+691.6 MiB` (`5,277.9 MiB` baseline $\rightarrow$ `5,969.5 MiB` peak across FastAPI, Next.js, EffectCraft/FilmCraft, and FFmpeg — well within the 14 GiB RAM envelope).
- **Final Output Size**: `4,171,758 bytes` (`4.17 MB`, `1920x1080` H.264 video + 48 kHz stereo AAC audio).

## 5. Visual Quality Findings & Fixes Applied During Phase 7
Inspecting midpoint frames (`data/screenshots/phase7_s01.png` through `phase7_s06.png`) revealed two subtle layout/camera issues when the AI Director emitted manual `x, y` coordinate hints and large `pan`/`zoom_in` camera amounts across 6 complex scenes:
1. **Manual Hint Clamping & Collision Fallback (`services/api/aivs/engines/scene_renderer.py`)**:
   - Clamped manual `x, y` hints into the safe diagram band (`[0.20*H, 0.79*H]`) so nodes never touch two-line top titles (`on_screen_text`) or bottom burned-in subtitles.
   - Added automatic bounding-box collision detection on manual `x, y` hints so scenes where LLM-guessed coordinates overlap automatically fall back to the deterministic DAG rank layout.
2. **Bounded Camera Rig Motion (`_camera_keys`)**:
   - Anchored `camera_rig` at `[W/2, H/2]` and bounded `zoom_in`/`focus` scale to `104%` and `pan` drift to `±3%` of frame width so camera movements provide smooth visual dynamism without pushing outer diagram nodes off-screen.
