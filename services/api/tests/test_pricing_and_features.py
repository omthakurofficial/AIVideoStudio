from pathlib import Path
from aivs.pricing import BEDROCK_MODEL_CATALOG, calculate_call_cost, record_token_usage, get_project_token_report
from aivs.engines.filmcraft import CaptionEntry, CaptionWord, write_ass_highlighted
from aivs.engines.scene_renderer import SceneCompiler
from aivs.storyboard import Scene


def test_bedrock_model_catalog_excludes_openai_and_calculates_official_pricing(tmp_path: Path):
    assert len(BEDROCK_MODEL_CATALOG) >= 17
    for m in BEDROCK_MODEL_CATALOG:
        assert "openai" not in m["model_id"].lower()
        assert "gpt" not in m["model_id"].lower()
        assert m["input_per_1m_usd"] > 0
        assert m["output_per_1m_usd"] > 0
        assert m["official_pricing_url"].startswith("https://")

    cost = calculate_call_cost("au.anthropic.claude-sonnet-4-5-20250929-v1:0", 2000, 1000)
    assert cost["input_cost_usd"] == 0.006
    assert cost["output_cost_usd"] == 0.015
    assert cost["total_cost_usd"] == 0.021

    rep = record_token_usage(tmp_path, "storyboard_planning", "au.anthropic.claude-sonnet-4-5-20250929-v1:0", 2000, 1000, 4.2, 1)
    assert rep["used_api_tokens"] is True
    assert rep["total_tokens"] == 3000
    assert rep["total_cost_usd"] == 0.021
    loaded = get_project_token_report(tmp_path)
    assert loaded["primary_model_id"] == "au.anthropic.claude-sonnet-4-5-20250929-v1:0"


def test_ass_active_word_highlighting_generates_per_word_gold_tags(tmp_path: Path):
    caps = [
        CaptionEntry(
            index=1,
            start_s=0.0,
            end_s=1.5,
            text="Extreme monsoon rain",
            words=[
                CaptionWord(word="Extreme", start_s=0.0, end_s=0.5),
                CaptionWord(word="monsoon", start_s=0.5, end_s=1.0),
                CaptionWord(word="rain", start_s=1.0, end_s=1.5),
            ],
        )
    ]
    ass_path = write_ass_highlighted(caps, tmp_path / "captions.ass", width=1920, height=1080)
    text = ass_path.read_text(encoding="utf-8")
    assert text.count("Dialogue:") == 3
    assert r"{\c&H0000D7FF&\fscx108\fscy108}Extreme" in text
    assert r"{\c&H0000D7FF&\fscx108\fscy108}monsoon" in text
    assert r"{\c&H0000D7FF&\fscx108\fscy108}rain" in text


def test_2d_map_and_vector_icon_scene_compilation():
    sc = Scene.model_validate({
        "id": "s01", "order": 1,
        "narration_text": "In late September, monsoon rain flooded Kathmandu Valley and the Koshi River basin in Nepal.",
        "estimated_duration": 4.0,
        "learning_objective": "Map Nepal flood zones",
        "key_message": "300mm Rain Over Nepal",
        "visual_type": "map",
        "visual_description": "2D map of Nepal showing Kathmandu Valley flood region, Koshi River marker, and monsoon rain icon.",
        "visual_elements": [
            {"id": "monsoon", "kind": "icon", "label": "Monsoon Storm", "props": {"icon": "rain", "color": "#0284c7"}},
            {"id": "ktm_zone", "kind": "map_region", "label": "Kathmandu Valley", "props": {"color": "#ea580c"}},
            {"id": "koshi_pin", "kind": "map_marker", "label": "Koshi Barrage", "props": {"color": "#ef4444"}},
            {"id": "flow_r", "kind": "route", "label": "", "props": {"from": "ktm_zone", "to": "koshi_pin"}},
        ],
        "element_relationships": [{"source": "ktm_zone", "target": "koshi_pin", "kind": "flows_to"}],
        "animation_sequence": [
            {"id": "a1", "at": 0.0, "duration": 0.6, "action": "fade_in", "targets": ["monsoon", "ktm_zone", "koshi_pin"]},
            {"id": "a2", "at": 0.7, "duration": 0.8, "action": "draw", "targets": ["flow_r"]},
        ],
    })
    build = SceneCompiler(sc, 1920, 1080, 30.0, "warm-documentary").compile()
    layer_names = [st["params"].get("name", "") for st in build.steps if "name" in st.get("params", {})]
    assert "map__land_outer" in layer_names
    assert "map__river_main" in layer_names
    assert "map__compass_ring" in layer_names
    assert "monsoon__vec_cloud" in layer_names
    assert "ktm_zone__shape" in layer_names
    assert "koshi_pin__ring" in layer_names
