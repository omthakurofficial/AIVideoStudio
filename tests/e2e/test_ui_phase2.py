"""Real-browser acceptance test: create a project through the UI, analyze, verify persistence. Needs dev servers running."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "data" / "screenshots"; SHOTS.mkdir(parents=True, exist_ok=True)
SCRIPT = ("Docker packages an application with its dependencies into a container.\n\n"
          "A CI pipeline builds the image, runs tests, and pushes it to a registry.\n\n"
          "Kubernetes then pulls the image and runs it across a cluster of nodes.")

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    bad = []
    pg.on("response", lambda r: bad.append(r.url) if r.status >= 400 else None)
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto("http://localhost:3000/")
    expect(pg.get_by_role("heading", name="Dashboard")).to_be_visible()
    expect(pg.get_by_text("effectcraft: ok")).to_be_visible(timeout=10000)
    pg.get_by_role("link", name="Create project").click()
    pg.get_by_label("Project title").fill("DevOps Intro E2E")
    pg.get_by_label("Script").fill(SCRIPT)
    pg.get_by_label("Aspect ratio").select_option("9:16")
    pg.get_by_role("button", name="Create project").click()
    expect(pg.get_by_role("heading", name="DevOps Intro E2E")).to_be_visible()
    expect(pg.get_by_text("1080×1920")).to_be_visible()
    pg.get_by_role("button", name="Save & analyze").click()
    expect(pg.locator(".badge.completed")).to_be_visible(timeout=15000)
    pg.screenshot(path=str(SHOTS / "project_completed.png"))
    pid = pg.url.rstrip("/").split("/")[-1]
    rep = json.loads((ROOT / "projects" / pid / "reports" / "script_analysis.json").read_text())
    assert rep["paragraph_count"] == 3, rep
    pg.reload()
    expect(pg.get_by_label("Edit and save your script")).to_have_value(SCRIPT)
    pg.goto("http://localhost:3000/")
    expect(pg.get_by_role("link", name="DevOps Intro E2E").first).to_be_visible()
    pg.screenshot(path=str(SHOTS / "dashboard.png"))
    assert not [u for u in bad if "favicon" not in u], bad  # failed requests other than the favicon
    assert not [e for e in errors if "Failed to load resource" not in e], errors
    print("UI E2E PASSED; project", pid, "paragraphs", rep["paragraph_count"])
    b.close()
