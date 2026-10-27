# Phase 4 — EffectCraft & FilmCraft MCP Integration (verified 2026-10-27)

## EffectCraft Adapter (`services/api/aivs/engines/effectcraft.py` + `scene_renderer.py`)
- **Transport**: Headless stdio MCP (`effectcraft-cli mcp`) via `MCPClient` for composition creation, batch layer creation, property sets, keyframes, and project saving (`.ecproj`), paired with `effectcraft-cli render` for H.264 MP4 output.
- **Capability discovery**: Verifies all required MCP tools (`batch`, `execute_command`, `save_project`, `get_comp`, `get_layer`, `render_frame`, `add_keyframe`) and engine commands (`comp.new`, `layer.newShape`, `layer.newText`, `layer.newNull`, `layer.setParent`, `prop.addKey`, `prop.set`).
- **Verified quirks resolved**:
  - `layer.newShape` requires 2-element `[w, h]` arrays for `size` even on ellipses/polygons, and 6-digit `#rrggbb` colors.
  - `layer.newText` `box` is in composition space when created; setting both `position` and `box` double-offsets text.
  - Spatial keyframe interpolation curves if a packet jumps from `[-100, -100]` to the route start; packets now start hidden at `[sx, sy]` so motion along routes is strictly linear.
  - Layout reserves the top 16% of the frame for on-screen titles and the bottom 20% for subtitle safe area.
- **Reusable primitives**: `icon` (colour-coded badge + monogram + label), `service_node`, `node`, `box`/`group` (outline containers), `callout`, `chart_bar` (bottom-anchored grow), `arrow`/`route` (angled shaft + arrowhead clipped to node boundaries), `packet` (animated flow along route), `on_screen_text`, and `camera_rig` (`pan`, `zoom_in`, `zoom_out`, `focus`).

## FilmCraft Adapter (`services/api/aivs/engines/filmcraft.py`)
- **Transport**: Headless stdio MCP (`filmcraft-cli mcp`) executing `file.newProject`, `file.newSequence`, `file.import`, `command_batch` (`timeline.place` on `V1`/`A1`, `captions.newTrack`, `captions.add`, `file.saveAs`), and synchronous `file.exportMedia` (`wait: true`).
- **Authoritative plan**: `TimelineManifest` saved to `assembly/timeline_manifest.json` before assembly.
- **Caption handling**: Saves native FilmCraft caption track in `.fcproj`, writes `captions/captions.srt`, and when `burn_captions=True` runs an FFmpeg `subtitles` filter pass to burn styled captions into the bottom safe area.
