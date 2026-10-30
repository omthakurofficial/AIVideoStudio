from fastapi.testclient import TestClient
from aivs.main import create_app
from packages.creator_engine.templates import TOP_10_NICHES, TemplateGenerator


def test_top_10_niches_catalog():
    assert len(TOP_10_NICHES) == 10
    niche_ids = [n["id"] for n in TOP_10_NICHES]
    assert "youtube_growth" in niche_ids
    assert "finance_wealth" in niche_ids
    assert "vox_explainer" in niche_ids
    assert "geopolitics_maps" in niche_ids
    assert "podcast_avatar" in niche_ids
    assert "saas_tech_3d" in niche_ids
    assert "mindset_motivation" in niche_ids
    assert "true_crime" in niche_ids
    assert "science_tech" in niche_ids
    assert "luxury_business" in niche_ids


def test_template_generator_blueprint_generation():
    tg = TemplateGenerator()
    bp = tg.generate_blueprint(
        topic="How to Hit 100K YouTube Subscribers",
        niche_id="youtube_growth",
        target_duration_s=60,
        aspect_ratio="9:16",
        mode="master_auto"
    )
    assert bp["status"] == "success"
    assert bp["target_duration_s"] == 60
    assert bp["target_word_count"] == 150
    assert len(bp["scenes"]) >= 6
    assert "WHAT WOULD YOU LIKE TO DO NEXT?" in bp["portable_master_prompt"]
    assert "Kokoro" in bp["portable_master_prompt"]


def test_v2_templates_api_endpoints():
    app = create_app()
    with TestClient(app) as client:
        # Test niches catalog
        res = client.get("/api/v2/templates/niches")
        assert res.status_code == 200
        data = res.json()
        assert "niches" in data
        assert len(data["niches"]) == 10

        # Test blueprint generation endpoint
        res = client.post("/api/v2/templates/generate", json={
            "topic": "The 30-Day Wall Motivation",
            "niche_id": "mindset_motivation",
            "target_duration_s": 60,
            "aspect_ratio": "9:16",
            "mode": "master_auto"
        })
        assert res.status_code == 200
        bp = res.json()
        assert bp["project_title"] == "The 30-Day Wall Motivation"
        assert len(bp["scenes"]) == 6
        assert bp["niche"]["id"] == "mindset_motivation"
        assert "portable_master_prompt" in bp
