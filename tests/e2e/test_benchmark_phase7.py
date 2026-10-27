"""Phase 7 Longer Benchmark E2E (60-90s video):
Creates a 6-scene (~75s) educational video on Global Cloud Architecture in automatic mode via the browser UI,
monitors system resource usage (RAM/CPU), and inspects Bedrock token usage, stage timing, and visual quality."""
from __future__ import annotations
import json, os, subprocess, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "data" / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
SCRIPT_TEXT = (ROOT / "examples" / "cloud_networking_75s.md").read_text(encoding="utf-8").strip()
EXISTING_PID = os.environ.get("AIVS_BENCHMARK_PID")


def sample_system_resources(stop_evt: threading.Event, samples: list[dict]) -> None:
    while not stop_evt.is_set():
        try:
            mem = Path("/proc/meminfo").read_text()
            mt = next(int(x.split()[1]) for x in mem.splitlines() if x.startswith("MemTotal:"))
            ma = next(int(x.split()[1]) for x in mem.splitlines() if x.startswith("MemAvailable:"))
            used_mib = round((mt - ma) / 1024.0, 1)
            load1 = float(Path("/proc/loadavg").read_text().split()[0])
            samples.append({"ts": time.time(), "used_ram_mib": used_mib, "load1": load1})
        except Exception:
            pass
        stop_evt.wait(1.0)


stop_evt = threading.Event()
samples: list[dict] = []
mon = threading.Thread(target=sample_system_resources, args=(stop_evt, samples), daemon=True)
mon.start()
t0 = time.monotonic()

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    if EXISTING_PID:
        pid = EXISTING_PID
        pg.goto(f"http://localhost:3000/projects/{pid}")
        expect(pg.get_by_role("heading", name="Global Cloud Architecture (75s Benchmark)")).to_be_visible()
    else:
        pg.goto("http://localhost:3000/projects/new")
        pg.get_by_label("Project title").fill("Global Cloud Architecture (75s Benchmark)")
        pg.get_by_label("Script", exact=True).fill(SCRIPT_TEXT)
        pg.get_by_label("Visual style").select_option("dark-neon")
        pg.get_by_label("Target duration (s)").fill("75")
        pg.get_by_label("Storyboard approval").select_option("automatic")
        pg.get_by_role("button", name="Create project").click()

        expect(pg.get_by_role("heading", name="Global Cloud Architecture (75s Benchmark)")).to_be_visible()
        pid = pg.url.rstrip("/").split("/")[-1]
        print("Created benchmark project:", pid)
        pg.get_by_role("button", name="Plan & produce full video").click()

    prod_sec = pg.get_by_role("region", name="Production")
    expect(pg.get_by_role("heading", name="Completed Export")).to_be_visible(timeout=420000)
    expect(pg.locator(".badge.ok", has_text="PASSED")).to_be_visible(timeout=60000)
    expect(prod_sec.get_by_text("Export ready & verified")).to_be_visible(timeout=60000)

    pg.screenshot(path=str(SHOTS / "phase7_benchmark_completed.png"), full_page=True)
    b.close()

total_wall_s = round(time.monotonic() - t0, 2)
stop_evt.set()
mon.join(timeout=2)

ws = ROOT / "projects" / pid
qrep = json.loads((ws / "reports" / "quality_report.json").read_text())
duse = json.loads((ws / "reports" / "director_usage.json").read_text())
cval = json.loads((ws / "reports" / "caption_validation.json").read_text())
sb = json.loads((ws / "storyboard.json").read_text())
final_dur = round(sum(float(s["duration_s"]) for s in qrep["scenes"]), 2)

assert qrep["ok"], qrep
assert cval["ok"], cval
assert 55.0 <= final_dur <= 105.0, f"Expected ~60-90s video, got {final_dur}s"
assert len(sb["scenes"]) >= 5, f"Expected >=5 scenes, got {len(sb['scenes'])}"

# Extract midpoint frame from each scene in final.mp4 for visual inspection
offset = 0.0
for sc in sb["scenes"]:
    dur = float(sc["timing"]["narration_audio_s"] or sc["estimated_duration"])
    mid = round(offset + dur * 0.55, 2)
    out_png = SHOTS / f"phase7_{sc['id']}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(mid), "-i", str(ws / "renders" / "final.mp4"), "-frames:v", "1", str(out_png)],
        check=True,
    )
    offset += dur

ram_vals = [s["used_ram_mib"] for s in samples] or [0.0]
load_vals = [s["load1"] for s in samples] or [0.0]
summary = {
    "project_id": pid,
    "wall_time_s": total_wall_s,
    "final_duration_s": final_dur,
    "final_size_bytes": (ws / "renders" / "final.mp4").stat().st_size,
    "scene_count": len(sb["scenes"]),
    "visual_types": [s["visual_type"] for s in sb["scenes"]],
    "scene_durations_s": {s["id"]: round(float(s["timing"]["narration_audio_s"] or s["estimated_duration"]), 2) for s in sb["scenes"]},
    "caption_segments": cval["caption_count"],
    "director_usage": duse,
    "repairs_applied": qrep["repairs_applied"],
    "ram_baseline_mib": ram_vals[0],
    "ram_peak_mib": max(ram_vals),
    "ram_delta_peak_mib": round(max(ram_vals) - min(ram_vals), 1),
    "cpu_load1_peak": max(load_vals),
}
(ws / "reports" / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("PHASE 7 BENCHMARK PASSED!")
print(json.dumps(summary, indent=2))
