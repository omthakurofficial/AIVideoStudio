"""Phase 5 & 6 Real Browser E2E: produce complete 30-second video with neural narration, captions, EffectCraft scenes,
FilmCraft assembly, QC verification, and single-scene visual correction + regeneration preserving other scenes."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "data" / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
PID = "5f87e209ca0e"

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    pg.goto(f"http://localhost:3000/projects/{PID}")
    expect(pg.get_by_role("heading", name="DevOps CI to K8s")).to_be_visible()

    prod_sec = pg.get_by_role("region", name="Production")
    if not pg.get_by_role("heading", name="Completed Export").is_visible():
        pg.get_by_role("button", name="Render & assemble video").click()
    expect(pg.get_by_role("heading", name="Completed Export")).to_be_visible(timeout=240000)
    expect(pg.locator(".badge.ok", has_text="PASSED")).to_be_visible(timeout=60000)
    expect(pg.get_by_text("Scene Preview (v1)").first).to_be_visible(timeout=30000)
    expect(prod_sec.get_by_text("Export ready & verified")).to_be_visible(timeout=60000)

    # Now test Scene Review: request a specific visual correction on Scene 1 and regenerate ONLY Scene 1
    pg.locator("#corr-s01").fill("Automated CI: Build, Test & Push")
    pg.get_by_role("button", name="Apply correction & regenerate scene").first.click()
    expect(prod_sec.get_by_text("regenerate_scene")).to_be_visible(timeout=30000)
    expect(pg.get_by_text("Scene Preview (v2)")).to_be_visible(timeout=180000)
    expect(prod_sec.get_by_text("Export ready & verified")).to_be_visible(timeout=180000)

    pg.screenshot(path=str(SHOTS / "phase5_6_completed.png"), full_page=True)

    # Check Dashboard shows Completed exports
    pg.goto("http://localhost:3000/")
    expect(pg.get_by_role("region", name="Completed exports").get_by_text("DevOps CI to K8s")).to_be_visible()
    pg.screenshot(path=str(SHOTS / "phase5_6_dashboard.png"), full_page=True)
    b.close()

ws = ROOT / "projects" / PID
qrep = json.loads((ws / "reports" / "quality_report.json").read_text())
assert qrep["ok"], qrep
scenes_by_id = {s["scene_id"]: s for s in qrep["scenes"]}
assert scenes_by_id["s01"]["version"] == 2
assert scenes_by_id["s02"]["version"] == 1
assert scenes_by_id["s03"]["version"] == 1
print("PHASE 5 & 6 UI E2E PASSED! Final MP4:", ws / "renders" / "final.mp4")
print("Scene versions:", {k: v["version"] for k, v in scenes_by_id.items()}, "durations:", {k: v["duration_s"] for k, v in scenes_by_id.items()})
