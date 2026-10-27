import json, time
from dataclasses import replace
import pytest
from fastapi.testclient import TestClient
from aivs.config import load_settings
from aivs.main import create_app
from aivs.director import Director
from aivs.providers import StructuredResult
from aivs.providers.base import ModelSpec

SCRIPT = (
    "Every time a developer pushes code, a CI pipeline wakes up and builds the image.\n\n"
    "Next, Kubernetes pulls that image and schedules it across healthy worker nodes."
)
SPEC = ModelSpec("fake", "fake-model")
CFG = {"max_repair_attempts": 2, "duration_tolerance": 0.4, "narration_coverage_min": 0.90}


class FakeProvider:
    name = "fake"
    def __init__(self, payload):
        self.payload = payload
    def generate_structured(self, spec, system, messages, schema, tool_name, desc):
        return StructuredResult(data=self.payload, model_id="fake-director", input_tokens=100, output_tokens=200)


def build_storyboard_payload(inject_blank_s01: bool = False) -> dict:
    s1_anim = (
        [{"id": "hide_all", "at": 0.0, "duration": 0.1, "action": "disappear", "targets": ["dev", "ci", "ar"]}]
        if inject_blank_s01 else
        [
            {"id": "a1", "at": 0.0, "duration": 0.4, "action": "fade_in", "targets": ["dev", "ci"]},
            {"id": "a2", "at": 0.5, "duration": 0.6, "action": "draw", "targets": ["ar"]},
        ]
    )
    return {
        "title": "DevOps Pipeline",
        "scenes": [
            {
                "id": "s01", "order": 1,
                "narration_text": "Every time a developer pushes code, a CI pipeline wakes up and builds the image.",
                "estimated_duration": 4.0,
                "learning_objective": "Explain CI build trigger",
                "key_message": "Push triggers build",
                "visual_type": "animated_diagram",
                "visual_description": "Developer pushes code to CI node.",
                "visual_elements": [
                    {"id": "dev", "kind": "icon", "label": "Developer", "props": {"color": "#4A90E2"}},
                    {"id": "ci", "kind": "service_node", "label": "CI Build", "props": {"color": "#F5A623"}},
                    {"id": "ar", "kind": "arrow", "label": "", "props": {"from": "dev", "to": "ci"}},
                ],
                "element_relationships": [{"source": "dev", "target": "ci", "kind": "flows_to"}],
                "animation_sequence": s1_anim,
                "on_screen_text": [{"text": "CI Build", "at": 0.2, "duration": 2.5}] if not inject_blank_s01 else [],
            },
            {
                "id": "s02", "order": 2,
                "narration_text": "Next, Kubernetes pulls that image and schedules it across healthy worker nodes.",
                "estimated_duration": 4.0,
                "learning_objective": "Explain Kubernetes scheduling",
                "key_message": "K8s schedules containers",
                "visual_type": "architecture",
                "visual_description": "Kubernetes control plane routes to worker node.",
                "visual_elements": [
                    {"id": "k8s", "kind": "service_node", "label": "Kubernetes", "props": {"color": "#326CE5"}},
                    {"id": "node1", "kind": "node", "label": "Worker Node", "props": {"color": "#3ecf8e"}},
                    {"id": "r1", "kind": "route", "label": "", "props": {"from": "k8s", "to": "node1"}},
                ],
                "element_relationships": [{"source": "k8s", "target": "node1", "kind": "flows_to"}],
                "animation_sequence": [
                    {"id": "b1", "at": 0.0, "duration": 0.5, "action": "fade_in", "targets": ["k8s", "node1"]},
                    {"id": "b2", "at": 0.6, "duration": 0.6, "action": "draw", "targets": ["r1"]},
                ],
                "on_screen_text": [{"text": "Kubernetes Scheduling", "at": 0.2, "duration": 2.5}],
            },
        ],
    }


def wait_job(client: TestClient, jid: str, timeout: float = 120.0) -> dict:
    end = time.time() + timeout
    while time.time() < end:
        j = client.get(f"/api/jobs/{jid}").json()
        if j["state"] in ("completed", "failed", "cancelled", "awaiting_approval"):
            return j
        time.sleep(0.1)
    raise AssertionError(f"Job {jid} timed out")


def test_deliberate_scene_failure_auto_repairs_and_scene_regenerate_reuses_other_scenes(tmp_path):
    s = replace(load_settings(), data_dir=tmp_path / "d", projects_dir=tmp_path / "p", db_path=tmp_path / "d" / "db.sqlite3")
    app = create_app(s, director_factory=lambda: Director(FakeProvider(build_storyboard_payload(inject_blank_s01=True)), SPEC, CFG))

    with TestClient(app) as c:
        proj = c.post("/api/projects", json={
            "title": "Recovery Test",
            "script": SCRIPT,
            "settings": {
                "aspect_ratio": "16:9", "fps": 30, "target_duration_s": 8,
                "approval_mode": "automatic",
                "narration": {"mode": "generate", "voice": "synthetic"},
                "captions": {"enabled": True, "font_size": 44},
            },
        }).json()
        pid = proj["id"]

        # Start full production: s01 has a deliberate blank-frame animation failure that QC must detect and repair
        job = c.post(f"/api/projects/{pid}/jobs/produce").json()
        finished = wait_job(c, job["id"])
        assert finished["state"] == "completed", finished

        reports = c.get(f"/api/projects/{pid}/reports").json()
        qrep = reports["quality_report"]
        assert qrep["ok"] is True
        assert len(qrep["repairs_applied"]) == 1
        rep0 = qrep["repairs_applied"][0]
        assert rep0["scene_id"] == "s01" and rep0["failed_version"] == 1 and rep0["repaired_version"] == 2
        assert rep0["outcome"] == "passed"

        # Verify media serving endpoint works for final.mp4 and scene preview
        r_mp4 = c.get(f"/api/projects/{pid}/media/renders/final.mp4")
        assert r_mp4.status_code == 200 and len(r_mp4.content) > 5000
        r_prev = c.get(f"/api/projects/{pid}/media/renders/previews/s01.png")
        assert r_prev.status_code == 200 and len(r_prev.content) > 500

        # Now request a visual correction on Scene 2 only, and verify Scene 1 (v2) is preserved/reused!
        regen = c.post(f"/api/projects/{pid}/scenes/s02/regenerate", json={
            "visual_correction": "Healthy Pods Scheduled",
            "visual_type": "layered_motion",
        }).json()
        regen_done = wait_job(c, regen["id"])
        assert regen_done["state"] == "completed", regen_done

        logs_txt = "\n".join(l["message"] for l in regen_done["logs"])
        assert "Scene s01: reused verified render v2" in logs_txt
        assert "Narration s01:" in logs_txt and "reused cache" in logs_txt
        ckpt_scenes = regen_done["checkpoint"]["rendered_scenes"]
        assert ckpt_scenes["s01"]["version"] == 2
        assert ckpt_scenes["s02"]["version"] == 2
