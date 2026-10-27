# Phase 3 — Storyboard generation (verified 2026-10-27)

## Bedrock findings (ap-southeast-2, this account)
- Bare Claude model IDs fail ("on-demand throughput isn't supported"): use inference-profile IDs (`au.` / `global.`).
- Invocable: `au.anthropic.claude-sonnet-4-5-20250929-v1:0`, `au.anthropic.claude-haiku-4-5-20251001-v1:0`, `global.*` equivalents, `openai.gpt-oss-120b-1:0` (returns a reasoning block first; not used).
- NOT available despite being listed: `anthropic.claude-sonnet-5(-5)`, `anthropic.claude-haiku-5-5` (AccessDenied).
- Structured output = Converse forced tool use (`toolChoice`) with the Pydantic JSON schema. Models are set per task in `config/models.json`
  (override: `AIVS_MODEL_PLANNING` etc.).

## Contract
`services/api/aivs/storyboard/schema.py` (schema_version 1; JSON Schema exported to `packages/contracts/storyboard.v1.schema.json`).
Time model, ID rules and cross-reference validation are documented in that file's docstring. Migrations: `storyboard/migrate.py`.

## Director guards (deterministic, outside the model)
Schema validation, dangling element references, animation/camera/text beyond scene end, narration coverage (LCS ≥ 92%, no added
narration), total duration within ±30% of target, scene id order. Failures are fed back to the model (max 2 repairs).

## Measured (3-scene, ~90-word DevOps script, Sonnet 4.5)
Run 1: 1 attempt, 3,900 in / 5,934 out tokens, 63 s. Run 2 (UI test): 1 attempt, 3,900 / 6,417, 69 s. No dollar cost is claimed;
token counts are saved per project in `reports/director_usage.json`.
Quality notes: scenes used animated diagrams with sensible element graphs, sequenced to the narration; no unnecessary stock footage.
Limitation: all 3 scenes chose `animated_diagram`; variety across a longer script is untested. Some `arrow` elements have no relationship entry.
