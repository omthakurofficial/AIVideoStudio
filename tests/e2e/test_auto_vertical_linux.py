"""Full Production Linux E2E Test:
Verifies Sample Script selection, supported script format inspection (## Scene headings + [Visual: ...] hints),
automatic script duration/narration/caption configuration, aspect ratio selection (9:16 vertical 1080x1920),
and one-click 'Create & Produce Video Automatically' using EffectCraft and FilmCraft on Linux."""
from __future__ import annotations
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "data" / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    pg.goto("http://localhost:3000/projects/new")

    # 1. Open supported script formats guide
    pg.get_by_role("button", name="What script formats are supported?").click()
    expect(pg.get_by_text("Scene Headings + [Visual: ...] Hints")).to_be_visible()

    # 2. Click the 9:16 sample script ("Zero-Trust mTLS Security (9:16 Vertical Short)")
    pg.get_by_role("button", name="Load sample (9:16)").click()

    # 3. Verify automatic script analysis populated duration, narration, captions, and 9:16 aspect ratio automatically
    auto_box = pg.get_by_role("region", name="Automatic script analysis")
    expect(auto_box).to_be_visible()
    expect(auto_box.get_by_text("Format: structured scenes with visual hints")).to_be_visible()
    expect(auto_box.get_by_text("Recommended aspect: 9:16")).to_be_visible()
    expect(pg.get_by_label("Aspect ratio")).to_have_value("9:16")

    pg.screenshot(path=str(SHOTS / "new_project_auto_samples.png"), full_page=True)

    # 4. One-click end-to-end automatic production (no manual duration or storyboard approval steps!)
    pg.get_by_role("button", name="Create & Produce Video Automatically").click()
    expect(pg.get_by_role("heading", name="Zero-Trust mTLS Security (9:16 Vertical Short)")).to_be_visible(timeout=30000)
    pid = pg.url.rstrip("/").split("/")[-1]
    print("Started automatic 9:16 Linux production project:", pid)

    prod_sec = pg.get_by_role("region", name="Production")
    expect(pg.get_by_role("heading", name="Completed Export")).to_be_visible(timeout=300000)
    expect(pg.locator(".badge.ok", has_text="PASSED")).to_be_visible(timeout=60000)
    expect(prod_sec.get_by_text("Export ready & verified")).to_be_visible(timeout=60000)

    pg.screenshot(path=str(SHOTS / "vertical_9x16_completed.png"), full_page=True)
    b.close()

ws = ROOT / "projects" / pid
qrep = json.loads((ws / "reports" / "quality_report.json").read_text())
sb = json.loads((ws / "storyboard.json").read_text())
srt_text = (ws / "captions" / "captions.srt").read_text(encoding="utf-8")

assert qrep["ok"], qrep
assert "final_resolution_1080x1920" in qrep["passed_checks"], qrep["passed_checks"]
assert "[Visual" not in srt_text and "## Scene" not in srt_text, "Stage directions leaked into spoken captions!"

offset = 0.0
for sc in sb["scenes"]:
    dur = float(sc["timing"]["narration_audio_s"] or sc["estimated_duration"])
    mid = round(offset + dur * 0.55, 2)
    out_png = SHOTS / f"vertical_9x16_{sc['id']}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(mid), "-i", str(ws / "renders" / "final.mp4"), "-frames:v", "1", str(out_png)],
        check=True,
    )
    offset += dur

print("FULL LINUX 9:16 AUTOMATIC E2E PASSED! Project:", pid, "Final MP4:", ws / "renders" / "final.mp4")
