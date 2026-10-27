from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = "http://localhost:3000"
SCREENSHOT_DIR = Path("/tmp/aivs_ui_screenshots")


def test_premium_ui_all_pages_and_tabs():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Dashboard
        page.goto(BASE)
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
        expect(page.get_by_text("Total Projects")).to_be_visible()
        expect(page.get_by_text("Running Jobs")).to_be_visible()
        expect(page.get_by_text("Completed Exports").first).to_be_visible()
        expect(page.get_by_text("Failed Jobs", exact=True)).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "01_dashboard.png"), full_page=True)

        # 2. Settings & Live MCP Handshake Probe
        page.goto(f"{BASE}/settings?tab=effectcraft")
        expect(page.get_by_role("heading", name="EffectCraft Connection & Headless MCP Guide")).to_be_visible()
        page.get_by_role("button", name="Test EffectCraft MCP Connection Now").click()
        expect(page.get_by_text("ALL ENGINES & MCP VERIFIED")).to_be_visible(timeout=25000)
        page.screenshot(path=str(SCREENSHOT_DIR / "02_settings_mcp_verified.png"), full_page=True)

        # 3. Create Project Page
        page.goto(f"{BASE}/projects/new")
        expect(page.get_by_role("heading", name="Create Project")).to_be_visible()
        page.get_by_role("button", name="Load sample (9:16)").first.click()
        expect(page.get_by_text("Automatic Script Check:")).to_be_visible(timeout=10000)
        page.screenshot(path=str(SCREENSHOT_DIR / "03_create_project.png"), full_page=True)

        # 4. Jobs Monitor Page
        page.goto(f"{BASE}/jobs")
        expect(page.get_by_role("heading", name="Jobs & Exports Monitor")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "04_jobs_monitor.png"), full_page=True)

        # 5. Project Workspace 6 Tabs (using project 7aff8e938eba)
        page.goto(f"{BASE}/projects/7aff8e938eba")
        expect(page.get_by_role("button", name="1. Project Overview")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "05_project_overview.png"), full_page=True)

        page.get_by_role("button", name="2. Storyboard Editor", exact=False).click()
        expect(page.get_by_text("Storyboard Editor —")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "06_storyboard_editor.png"), full_page=True)

        page.get_by_role("button", name="3. Production Monitor", exact=False).click()
        expect(page.get_by_text("9-Stage Production Pipeline")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "07_production_monitor.png"), full_page=True)

        page.get_by_role("button", name="4. Scene Review").click()
        expect(page.get_by_text("Scene Details & Visual Options")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "08_scene_review.png"), full_page=True)

        page.get_by_role("button", name="5. Final Export", exact=False).click()
        expect(page.get_by_text("Project Details & Output Verification")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "09_final_export.png"), full_page=True)

        page.get_by_role("button", name="6. Project Files").click()
        expect(page.get_by_text("Project Files (Workspace)")).to_be_visible()
        page.screenshot(path=str(SCREENSHOT_DIR / "10_project_files.png"), full_page=True)

        browser.close()
