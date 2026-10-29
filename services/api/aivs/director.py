"""AI Director: creative planning only. Output is validated structured data; deterministic checks guard narration
fidelity and timing, and failures are fed back to the model for a bounded number of repair attempts."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pydantic import ValidationError
from .providers import LLMProvider, ModelSpec, ProviderError
from .storyboard import Storyboard, DirectorOutput
from .storyboard.schema import words
from .analysis import analyze_script
from .niches import detect_niche_from_text, get_niche
from .skills import get_skill, check_against_skill

PRIMITIVES_GUIDE = """Available visual building blocks (the renderer maps these to verified motion-graphics operations):
 element kinds: node, service_node, icon, label, callout, box, group, arrow, route, packet, chart_bar, chart_line, map_region,
   map_marker, timeline_marker, text, image, footage
 relationships: connects, contains, flows_to, compares, depends_on, precedes
 animation actions: appear, disappear, fade_in, fade_out, move, highlight, pulse, draw (reveal a line/arrow), flow (packets along a route),
   scale, type_text, grow (bars/charts)
 camera moves: static, pan, zoom_in, zoom_out, focus (on a target element id)
 visual types: animated_diagram, architecture, map, chart, timeline, icons_labels, footage, screenshot, ui_demo, layered_motion, hybrid"""

SYSTEM = f"""You are the AI Director of an educational/documentary video studio. Understand the script before deciding how to show it.

Rules:
1. Split the script into scenes at natural idea boundaries. Typically 1-3 sentences of narration per scene, 4-15 seconds each.
2. `narration_text` of all scenes, concatenated in order, must reproduce the ENTIRE script verbatim. Never paraphrase, add, drop or reorder narration. Visual instructions go in visual fields, never in narration.
3. For each scene state the learning objective and key message, then choose the visual technique by meaning: explain a process with an animated diagram showing the action, not a heading plus paragraph. Vary treatments across scenes; do not force one template.
4. Define visual_elements with unique snake_case ids, relationships between them, and an animation_sequence whose steps reference those ids and reveal things in the order the narration mentions them. All times are seconds relative to the scene start and must fit inside the scene duration.
5. Keep on-screen text short (labels, key terms), never a paragraph. Keep at most ~10 elements per scene so it stays legible. Every visual element (except arrows and packets) MUST have a meaningful, non-empty `label` (e.g. 'Route 53', 'AWS Lambda', 'Amazon RDS'). Never leave `label` empty.
6. For geographical, environmental, or real-world documentary scenes (e.g. Nepal floods, rivers, cities, climate), use `visual_type: "map"` with `map_region` and `map_marker` elements (which render on a 2D cartographic map canvas with terrain, rivers, graticule grid, and compass rose), plus `icon` elements (which render multi-shape 2D vector illustrations for rain, flood waves, mountains, rescue, warnings, cities, shields, and servers), and add a `stock_image` or `stock_video` entry in `asset_requirements` with a clear search query so real Pexels/Wikimedia documentary imagery is composited onto the scene.
7. Choose a transition for each scene boundary and note in director_notes how the scene connects to its neighbours.
8. Scene ids are s01, s02, ... in order. quality_checks list what must be visible in the final scene.
9. Every `arrow` or `route` element MUST carry props {{"from": <element id>, "to": <element id>}} naming two non-connector elements of the same scene (these are what get drawn). Also list the semantic link in element_relationships. A `flow` animation targets `packet` elements and MUST set params {{"route": <arrow/route element id>}}; `draw` reveals an arrow/route.
10. Optional layout hints: props {{"x": 0-1, "y": 0-1}} (fractions of the frame). Without hints, layout is automatic from the relationships (left-to-right, or top-to-bottom in portrait). Icons are drawn as colour-coded labelled badges (props.color hex like #2496ED); there are no brand logos, so make every label self-explanatory.
Return your answer ONLY by calling the provided tool.

{PRIMITIVES_GUIDE}"""


@dataclass
class DirectorReport:
    attempts: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    model_id: str = ""
    problems_by_attempt: list[list[str]] = field(default_factory=list)


class DirectorError(Exception):
    def __init__(self, message: str, report: DirectorReport):
        super().__init__(message)
        self.report = report


def narration_coverage(script: str, scenes_text: str) -> float:
    """Fraction of script words appearing, in order, in the concatenated scene narration (LCS ratio on word lists)."""
    a, b = words(script), words(scenes_text)
    if not a:
        return 1.0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1] / len(a)


def check_output(script: str, out: DirectorOutput, target_s: float, cfg: dict) -> list[str]:
    problems = []
    cov = narration_coverage(script, " ".join(s.narration_text for s in out.scenes))
    if cov < cfg["narration_coverage_min"]:
        problems.append(f"Scene narration covers only {cov:.0%} of the script in order; it must reproduce the whole script verbatim.")
    extra = len(words(" ".join(s.narration_text for s in out.scenes))) - len(words(script))
    if extra > max(5, 0.05 * len(words(script))):
        problems.append(f"Scene narration contains about {extra} words that are not in the script; do not add narration.")
    total = sum(s.estimated_duration for s in out.scenes)
    tol = cfg["duration_tolerance"]
    if target_s and not (target_s * (1 - tol) <= total <= target_s * (1 + tol)):
        problems.append(f"Total estimated duration is {total:.0f}s but the target is {target_s:.0f}s (allowed ±{tol:.0%}); adjust scene durations (pace roughly 2.5 words/second).")
    for i, s in enumerate(out.scenes, 1):
        if s.id != f"s{i:02d}" or s.order != i:
            problems.append(f"Scene {i} must have id s{i:02d} and order {i}.")
            break
    return problems


class Director:
    def __init__(self, provider: LLMProvider, spec: ModelSpec, cfg: dict):
        self.provider, self.spec, self.cfg = provider, spec, cfg

    def plan(self, project_id: str, script: str, settings: dict, log=lambda m: None) -> tuple[Storyboard, DirectorReport]:
        active_spec = self.spec
        override_model = (settings or {}).get("ai_model")
        if override_model and isinstance(override_model, str) and override_model.strip():
            from dataclasses import replace
            active_spec = replace(self.spec, model_id=override_model.strip())
        rep = DirectorReport(model_id=active_spec.model_id)
        parsed = analyze_script(script)
        clean_script = parsed["clean_narration"] or script.strip()
        hints_block = ("\nAuthor per-scene visual guidance (use for visual_description/elements, DO NOT include in narration_text):\n- "
                       + "\n- ".join(parsed["visual_hints"]) + "\n") if parsed["visual_hints"] else ""
        target_s = float(settings.get("target_duration_s") or parsed["recommended_target_duration_s"])
        niche_id = settings.get("niche_category") or detect_niche_from_text(clean_script, settings.get("visual_style", ""))
        niche = get_niche(niche_id)
        skill = get_skill(niche["id"])
        niche_block = f"\n{skill.director_brief() if skill else niche['director_rules']}\n"
        log(f"Director skill: {niche['id']} ({niche.get('skill_path') or 'built-in'})")
        brief = (f"Title: (derive from script)\nOutput: {settings['aspect_ratio']} at {settings['fps']} fps. Visual style: {settings['visual_style']}.\n"
                 f"Selected Niche Category Plugin: {niche['name']} ({niche['id']})\n"
                 f"Target total duration: about {target_s:.0f} seconds.\n"
                 + (f"Reference/style notes: {settings['reference_description']}\n" if settings.get("reference_description") else "")
                 + niche_block
                 + hints_block
                 + f"\nSCRIPT (reproduce verbatim across scenes):\n<script>\n{clean_script}\n</script>")
        messages = [{"role": "user", "content": [{"text": brief}]}]
        schema = DirectorOutput.model_json_schema()
        last_problems: list[str] = []
        for attempt in range(1, self.cfg["max_repair_attempts"] + 2):
            rep.attempts = attempt
            log(f"Director attempt {attempt} with {active_spec.model_id}")
            res = self.provider.generate_structured(active_spec, SYSTEM, messages, schema, "submit_storyboard",
                                                    "Submit the complete scene-by-scene storyboard.")
            rep.input_tokens += res.input_tokens; rep.output_tokens += res.output_tokens; rep.latency_s += res.latency_s
            problems: list[str] = []
            out = None
            try:
                if isinstance(res.data, dict) and "scenes" in res.data:
                    for sc_dict in res.data.get("scenes", []):
                        for el_dict in sc_dict.get("visual_elements", []):
                            if el_dict.get("kind") not in ("arrow", "route", "packet") and not (el_dict.get("label") or "").strip():
                                el_dict["label"] = el_dict.get("id", "item").replace("_", " ").title()
                out = DirectorOutput.model_validate(res.data)
                problems = check_output(clean_script, out, target_s, self.cfg)
                if skill:
                    problems += check_against_skill(skill, out.scenes)
            except ValidationError as e:
                problems = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()[:12]]
            rep.problems_by_attempt.append(problems)
            if not problems and out:
                sb = Storyboard(project_id=project_id, title=out.title, scenes=out.scenes,
                                created_by={"provider": self.provider.name, "model_id": active_spec.model_id, "attempts": attempt,
                                            "skill_id": niche["id"], "skill_fingerprint": skill.fingerprint() if skill else None})
                return sb, rep
            last_problems = problems
            log(f"Attempt {attempt} rejected: {len(problems)} problem(s): {problems[0][:160]}")
            messages += [{"role": "assistant", "content": [{"toolUse": {"toolUseId": f"t{attempt}", "name": "submit_storyboard", "input": res.data}}]},
                         {"role": "user", "content": [{"toolResult": {"toolUseId": f"t{attempt}", "status": "error",
                          "content": [{"text": "Rejected by validation. Fix ALL of these and resubmit the complete storyboard:\n- " + "\n- ".join(problems)}]}}]}]
        raise DirectorError("The AI Director could not produce a valid storyboard after "
                            f"{rep.attempts} attempts. Last problems: " + " | ".join(last_problems[:3]), rep)
