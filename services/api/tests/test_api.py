import time, json
import pytest
from fastapi.testclient import TestClient
from aivs.config import load_settings
from aivs.main import create_app
from dataclasses import replace


@pytest.fixture
def env(tmp_path):
    s = replace(load_settings(), data_dir=tmp_path / "d", projects_dir=tmp_path / "p", db_path=tmp_path / "d" / "db.sqlite3")
    return s


def wait_job(c, jid, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        j = c.get(f"/api/jobs/{jid}").json()
        if j["state"] in ("completed", "failed", "cancelled"):
            return j
        time.sleep(0.05)
    raise AssertionError("job did not finish")


def test_project_roundtrip_and_analysis(env):
    with TestClient(create_app(env)) as c:
        r = c.post("/api/projects", json={"title": "T", "script": "Hello world. This is DevOps.\n\nSecond para here."})
        assert r.status_code == 201
        p = r.json()
        assert p["output"] == {"width": 1920, "height": 1080, "fps": 30}
        root = env.projects_dir / p["id"]
        for f in ["project.json", "script.md", "manifest.json", "assets", "reports"]:
            assert (root / f).exists()
        job = c.post(f"/api/projects/{p['id']}/jobs/analyze").json()
        j = wait_job(c, job["id"])
        assert j["state"] == "completed" and j["progress_done"] == j["progress_total"]
        rep = json.loads((root / "reports/script_analysis.json").read_text())
        assert rep["paragraph_count"] == 2 and rep["total_words"] == 8


def test_empty_script_fails_with_actionable_error_and_retry(env):
    with TestClient(create_app(env)) as c:
        p = c.post("/api/projects", json={"title": "T", "script": ""}).json()
        j = wait_job(c, c.post(f"/api/projects/{p['id']}/jobs/analyze").json()["id"])
        assert j["state"] == "failed" and "script is empty" in j["error"]
        c.put(f"/api/projects/{p['id']}/script", json={"script": "Now there is text."})
        assert c.post(f"/api/jobs/{j['id']}/retry").status_code == 202
        assert wait_job(c, j["id"])["state"] == "completed"


def test_state_survives_restart_and_interrupted_jobs_recovered(env):
    with TestClient(create_app(env)) as c:
        p = c.post("/api/projects", json={"title": "Persist", "script": "abc"}).json()
        jid = c.post(f"/api/projects/{p['id']}/jobs/analyze").json()["id"]
        wait_job(c, jid)
        # simulate crash mid-job
        st = c.app.state.store
        interrupted = st.create_job(p["id"], "analyze_script")["id"]
        st.update_job(interrupted, state="rendering_scenes")
    with TestClient(create_app(env)) as c2:
        assert c2.get(f"/api/projects/{p['id']}").json()["script"] == "abc"
        assert c2.get(f"/api/jobs/{jid}").json()["state"] == "completed"
        j = c2.get(f"/api/jobs/{interrupted}").json()
        assert j["state"] == "failed" and "restart" in j["error"]


def test_validation_and_404(env):
    with TestClient(create_app(env)) as c:
        assert c.post("/api/projects", json={"title": "   "}).status_code == 422
        assert c.post("/api/projects", json={"title": "x", "settings": {"aspect_ratio": "4:3"}}).status_code == 422
        assert c.get("/api/projects/nope").status_code == 404


def test_health_reports_real_tools(env):
    with TestClient(create_app(env)) as c:
        h = c.get("/api/health").json()
        assert h["tools"]["ffmpeg"]["ok"] and h["tools"]["effectcraft"]["ok"] and h["tools"]["filmcraft"]["ok"]


def test_sample_scripts_and_automatic_script_inspection(env):
    with TestClient(create_app(env)) as c:
        samples = c.get("/api/scripts/samples").json()
        assert len(samples["samples"]) >= 4
        assert len(samples["supported_formats"]) >= 3

        raw = "## Scene 1: Edge Routing\n[Visual: Animated DNS arrow]\nUser queries Anycast DNS to reach the nearest edge node.\n\n## Scene 2: Gateway\n[Visual: TLS badge]\nThe gateway checks mutual TLS certificates automatically."
        insp = c.post("/api/scripts/inspect", json={"script": raw}).json()
        assert insp["detected_format"] == "structured_scenes_with_visual_hints"
        assert insp["paragraph_count"] == 2
        assert "[Visual" not in insp["clean_narration"] and "## Scene" not in insp["clean_narration"]
        assert len(insp["visual_hints"]) == 2
        assert insp["recommended_aspect_ratio"] == "9:16"

        # Creating a project without specifying target_duration_s auto-calculates it from the script
        p = c.post("/api/projects", json={"title": "Auto Test", "script": raw}).json()
        assert p["settings"]["target_duration_s"] == insp["recommended_target_duration_s"]
        assert p["script_analysis"]["detected_format"] == "structured_scenes_with_visual_hints"
