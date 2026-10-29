# AIVideoStudio Skills

Each folder here is one **video archetype**. The pipeline reads them at runtime — edit a `SKILL.md`, and the next
storyboard / render uses it (no restart, no Python change).

```
skills/<skill_id>/
  SKILL.md          # YAML frontmatter = locks the renderer enforces; markdown body = rules the AI Director reads
  references/*.md   # optional deep-dives; only those listed in `director_references` are sent to the model
skills/_vendor/     # upstream reference material (kept with its LICENSE); never loaded as a skill
```

| skill_id | archetype | reference channels |
|---|---|---|
| `geopolitics_map` | real map atlas | Johnny Harris, MirAtlas60 |
| `vox_documentary` | editorial explainer | Vox, vox-director |
| `story_cartoon` | cartoon history | Oversimplified |
| `tech_architecture` | cloud / system diagrams | Cloud X Berry, ByteByteGo |
| `finance_growth` | KPI + neon charts | DecodingYT |

## What the frontmatter locks (`render:`)
| key | enforced where |
|---|---|
| `allowed_visual_types`, `allowed_element_kinds`, `layout.max_elements_per_scene`, `layout.require_position_hints`, `reveal.max_simultaneous_entrances` | Director output validation → rejected & auto-repaired by the model |
| `reveal.lead_s` | narration word-timestamp alignment (entrance fires this long before the word) |
| `backdrop`, `visual_style` | scene renderer stage backdrop / palette |
| `camera.*` | camera rig clamp (max zoom, pan/focus allowed, idle push-in) |
| `stock_card.*` | stock picture-in-picture slot (or disabled) |
| `captions.font_size` | FilmCraft burned caption size |

Selecting a skill: project setting `niche_category` (= skill id). If empty, the skill whose `triggers` match the
script most wins.

## Adding a new archetype
Copy any folder, change `id`, `name`, `triggers`, the `render:` locks and the markdown rules. Validate with
`.venv/bin/pytest services/api/tests/test_skills.py`.

## Upstream material in `_vendor/`
- `vox-director/` — user-provided skill (Atlas Cloud generative collage pipeline). Its story layer
  (`beat-layer.md`) drives `vox_documentary`. Its scripts need `ATLASCLOUD_API_KEY` and are **not** wired into the
  deterministic pipeline.
- `anything2explainer/` — motion vocabulary, light & QC rules (see its LICENSE / required notice).
- `video-shotcraft/shots/` — shot library (Apache-2.0).
- `gsap-skills/` — easing/timeline vocabulary (MIT).
- remotion-dev/skills, threejs-skills, vox-ai-motion-graphics-generator: summarised in skill bodies only
  (remotion & vox-ai have no license file, threejs is a 3D/WebGL stack our renderer does not use).
