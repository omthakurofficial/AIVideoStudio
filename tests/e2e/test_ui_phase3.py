"""Real E2E (real Bedrock, real browser). Costs one Director call. Dev servers must be running."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "data" / "screenshots"; SHOTS.mkdir(parents=True, exist_ok=True)
SCRIPT = (ROOT / "examples" / "devops_30s.md").read_text()
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    pg.goto("http://localhost:3000/projects/new")
    pg.get_by_label("Project title").fill("DevOps CI to K8s")
    pg.get_by_label("Script").fill(SCRIPT)
    pg.get_by_role("button", name="Create project").click()
    expect(pg.get_by_role("heading", name="DevOps CI to K8s")).to_be_visible()
    pg.get_by_role("button", name="Plan storyboard with AI").click()
    expect(pg.get_by_role("article", name="Scene 1")).to_be_visible(timeout=240000)
    n = pg.get_by_role("article").count(); assert n >= 2, n
    expect(pg.get_by_text("needs review")).to_be_visible()
    pg.screenshot(path=str(SHOTS / "storyboard.png"), full_page=True)
    box = pg.locator("#vd-s01"); box.fill("EDITED BY USER: show a developer pushing code.")
    expect(pg.get_by_text("Unsaved changes")).to_be_visible()
    pg.get_by_role("button", name="Save changes").click()
    expect(pg.get_by_text("Changes saved")).to_be_visible()
    pg.get_by_role("button", name="Approve storyboard").click()
    expect(pg.locator(".badge.ok", has_text="approved")).to_be_visible()
    pid = pg.url.rstrip("/").split("/")[-1]
    pg.reload()
    expect(pg.locator("#vd-s01")).to_have_value("EDITED BY USER: show a developer pushing code.", timeout=15000)
    expect(pg.locator(".badge.ok", has_text="approved")).to_be_visible()
    sb = json.loads((ROOT / "projects" / pid / "storyboard.json").read_text())
    assert sb["approved"] and sb["revision"] == 2 and sb["schema_version"] == 1
    usage = json.loads((ROOT / "projects" / pid / "reports" / "director_usage.json").read_text())
    print("PASSED scenes", n, "revision", sb["revision"], "tokens", usage["input_tokens"], "/", usage["output_tokens"], "attempts", usage["attempts"], "latency", round(usage["latency_s"]), "s")
    b.close()
