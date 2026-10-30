from pathlib import Path
from services.api.aivs.url_extractor import is_url, extract_url_from_text, deconstruct_reference_media
from packages.creator_engine.templates import TemplateGenerator


def test_url_detector_and_extractor():
    text = "Please recreate this video: https://youtube.com/shorts/-hzypPgM_gs?si=test1234"
    assert is_url(text) is True
    assert extract_url_from_text(text) == "https://youtube.com/shorts/-hzypPgM_gs?si=test1234"


def test_youtube_deconstruction_extracts_rare_earths_context():
    url = "https://youtube.com/shorts/-hzypPgM_gs?si=j6qjhwRLbKOVjifD"
    info = deconstruct_reference_media(url)
    assert info["is_url"] is True
    assert "rare earths" in info["title"].lower() or "rare earth" in info["description"].lower()
    assert info["channel"] == "Villal Tales"
    assert len(info["key_facts"]) > 0
    assert "geopolitics" in info["suggested_niche"] or "vox" in info["suggested_niche"]


def test_blueprint_generation_uses_real_deconstructed_content():
    url = "https://youtube.com/shorts/-hzypPgM_gs?si=j6qjhwRLbKOVjifD"
    generator = TemplateGenerator()
    blueprint = generator.generate_blueprint(topic=url, niche_id="geopolitics_maps", aspect_ratio="9:16")

    assert blueprint["status"] == "success"
    assert "India Is 40 Years Late" in blueprint["project_title"]
    assert len(blueprint["scenes"]) == 6

    # Verify first scene has real topic headline and facts, not generic creator filler
    s1 = blueprint["scenes"][0]
    assert s1["headline"] == "CHINA'S 40-YEAR MONOPOLY"
    assert "7,280" in s1["spoken_narration"] or "7280" in s1["spoken_narration"] or "rare earth" in s1["spoken_narration"].lower()
    assert "Most people fail before they ever start" not in s1["spoken_narration"]

    # Verify standalone html does not include debug labels in canvas render
    html_code = blueprint["standalone_html_code"]
    assert "SCENE 0" + str(s1["scene_number"]) not in html_code  # No raw "SCENE 01" in canvas fillText
    assert "● BREAKING INVESTIGATION" in html_code
    assert "wrapLines" in html_code
