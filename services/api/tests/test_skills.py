"""Tests for the skill registry and archetype SKILL.md definitions."""
from pathlib import Path
from aivs.skills import load_skills, get_skill, detect_skill, check_against_skill
from aivs.niches import list_niches, get_niche, detect_niche_from_text


def test_load_all_archetype_skills():
    skills = load_skills()
    assert len(skills) >= 5
    ids = {s.id for s in skills}
    expected = {"geopolitics_map", "vox_documentary", "story_cartoon", "tech_architecture", "finance_growth"}
    assert expected.issubset(ids)


def test_skill_fingerprint_changes_on_render_profile_change():
    s1 = get_skill("tech_architecture")
    fp1 = s1.fingerprint()
    s2 = s1.model_copy(deep=True)
    s2.render.camera.max_zoom = 1.35
    fp2 = s2.fingerprint()
    assert fp1 != fp2


def test_detect_skill_triggers():
    # Cloud / Tech architecture
    assert detect_skill("Every request starts at Route 53 DNS and hits AWS Lambda") == "tech_architecture"
    # Geopolitics / Map
    assert detect_skill("The border between Nepal and India across the Himalayas") == "geopolitics_map"
    # Finance
    assert detect_skill("Views grew to 820K with a $15 RPM and subscriber revenue") == "finance_growth"
    # Story / Cartoon
    assert detect_skill("Napoleon offered Thomas Jefferson the Louisiana territory") == "story_cartoon"
    # Vox documentary
    assert detect_skill("Why Nepal's 15 minute timezone is an unusual history investigation") == "vox_documentary"


def test_skill_director_brief_contains_locks_and_creative_rules():
    skill = get_skill("geopolitics_map")
    brief = skill.director_brief()
    assert "LOCKED CONSTRAINTS" in brief
    assert "CREATIVE RULES:" in brief
    assert "Johnny Harris" in brief
    # Includes reference content
    assert "Map rules" in brief or "remotion-maps" in brief


def test_niche_compatibility_layer():
    niches = list_niches()
    assert len(niches) >= 5
    n_tech = get_niche("tech_architecture")
    assert n_tech["badge"] == "SVG CLOUD TILES"
    assert n_tech["default_visual_style"] == "clean-technical"
    assert "render_profile" in n_tech
