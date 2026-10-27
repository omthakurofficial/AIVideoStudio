import json, time, pytest
from dataclasses import replace
from fastapi.testclient import TestClient
from aivs.config import load_settings
from aivs.main import create_app
from aivs.director import Director, DirectorError, narration_coverage
from aivs.providers import ProviderError, StructuredResult
from aivs.providers.base import ModelSpec
from aivs.storyboard import Storyboard, DirectorOutput, scene_starts, total_duration, load_storyboard, MIGRATIONS
from aivs.storyboard.migrate import SchemaVersionError, migrate_data
from aivs.storyboard.timeline import revise_durations_from_audio

SCRIPT = "Code is pushed to a repository. A pipeline builds and tests it. Then it is deployed."
SPEC = ModelSpec("fake", "fake-model")
CFG = {"max_repair_attempts": 2, "duration_tolerance": 0.3, "narration_coverage_min": 0.92}


def scene(i, text, dur=5.0, **kw):
    d = {"id": f"s{i:02d}", "order": i, "narration_text": text, "estimated_duration": dur, "learning_objective": "obj", "key_message": "msg",
         "visual_type": "animated_diagram", "visual_description": "desc",
         "visual_elements": [{"id": "a", "kind": "node", "label": "A"}, {"id": "b", "kind": "node", "label": "B"}],
         "element_relationships": [{"source": "a", "target": "b", "kind": "flows_to"}],
         "animation_sequence": [{"id": "x1", "at": 0, "duration": 1, "action": "appear", "targets": ["a", "b"]}]}
    d.update(kw); return d


def good():
    return {"title": "T", "scenes": [scene(1, "Code is pushed to a repository.", 5), scene(2, "A pipeline builds and tests it. Then it is deployed.", 5)]}


class FakeProvider:
    """Test double that returns scripted payloads (used only to test Director repair logic deterministically)."""
    name = "fake"
    def __init__(self, *payloads): self.payloads, self.calls, self.messages = list(payloads), 0, []
    def generate_structured(self, spec, system, messages, schema, tool_name, desc):
        self.messages.append(list(messages)); p = self.payloads[min(self.calls, len(self.payloads) - 1)]; self.calls += 1
        if isinstance(p, Exception): raise p
        return StructuredResult(data=p, model_id="fake", input_tokens=10, output_tokens=20)


SETTINGS = {"aspect_ratio": "16:9", "fps": 30, "visual_style": "x", "target_duration_s": 10, "reference_description": None}


def test_valid_plan_first_attempt():
    sb, rep = Director(FakeProvider(good()), SPEC, CFG).plan("p1", SCRIPT, SETTINGS)
    assert rep.attempts == 1 and len(sb.scenes) == 2 and total_duration(sb) == 10 and scene_starts(sb) == {"s01": 0, "s02": 5}


def test_dangling_reference_rejected_then_repaired():
    bad = good(); bad["scenes"][0]["animation_sequence"][0]["targets"] = ["ghost"]
    fp = FakeProvider(bad, good())
    sb, rep = Director(fp, SPEC, CFG).plan("p1", SCRIPT, SETTINGS)
    assert rep.attempts == 2 and "ghost" in json.dumps(rep.problems_by_attempt[0])
    assert "Rejected by validation" in json.dumps(fp.messages[1])  # model was told what to fix


def test_paraphrased_narration_rejected():
    bad = good(); bad["scenes"][0]["narration_text"] = "Developers upload source files."
    with pytest.raises(DirectorError) as e:
        Director(FakeProvider(bad), SPEC, CFG).plan("p1", SCRIPT, SETTINGS)
    assert "verbatim" in str(e.value) and e.value.report.attempts == 3


def test_duration_out_of_target_rejected():
    bad = good(); bad["scenes"][0]["estimated_duration"] = 40
    with pytest.raises(DirectorError):
        Director(FakeProvider(bad), SPEC, CFG).plan("p1", SCRIPT, SETTINGS)


def test_animation_past_scene_end_and_duplicate_ids_invalid():
    for mutate in (lambda s: s["animation_sequence"][0].update(at=4.9, duration=3),
                   lambda s: s["visual_elements"].append({"id": "a", "kind": "node"})):
        d = scene(1, "x"); mutate(d)
        with pytest.raises(Exception):
            DirectorOutput.model_validate({"title": "t", "scenes": [d]})


def test_unknown_field_rejected():
    with pytest.raises(Exception):
        DirectorOutput.model_validate({"title": "t", "scenes": [scene(1, "x", surprise=1)]})


def test_audio_timing_revision_changes_timeline():
    sb = Storyboard(project_id="p", title="t", scenes=DirectorOutput.model_validate(good()).scenes)
    sb2 = revise_durations_from_audio(sb, {"s01": 6.1, "s02": 3.0})
    assert sb2.scenes[0].duration == 6.5 and scene_starts(sb2)["s02"] == 6.5 and sb2.scenes[1].timing.revised_from_audio


def test_migration_chain_and_future_version():
    d = json.loads(Storyboard(project_id="p", title="t", scenes=DirectorOutput.model_validate(good()).scenes).model_dump_json())
    with pytest.raises(SchemaVersionError): migrate_data({**d, "schema_version": 99})
    old = {**d, "schema_version": 0}
    out, changed = migrate_data(old, target=1, migrations={0: lambda x: x})
    assert changed and out["schema_version"] == 1
    with pytest.raises(SchemaVersionError): migrate_data(old, target=1, migrations={})


def test_narration_coverage_metric():
    assert narration_coverage("a b c d", "a b c d") == 1.0 and narration_coverage("a b c d", "a b") == 0.5


@pytest.fixture
def make_client(tmp_path):
    def mk(provider):
        s = replace(load_settings(), data_dir=tmp_path / "d", projects_dir=tmp_path / "p", db_path=tmp_path / "d" / "db.sqlite3")
        return TestClient(create_app(s, director_factory=lambda: Director(provider, SPEC, CFG))), s
    return mk


def wait(c, jid, states=("completed", "failed", "cancelled", "awaiting_approval")):
    end = time.time() + 10
    while time.time() < end:
        j = c.get(f"/api/jobs/{jid}").json()
        if j["state"] in states: return j
        time.sleep(0.05)
    raise AssertionError("timeout")


def test_api_plan_edit_approve_persist(make_client):
    c, s = make_client(FakeProvider(good()))
    with c:
        pid = c.post("/api/projects", json={"title": "T", "script": SCRIPT, "settings": {"target_duration_s": 10}}).json()["id"]
        j = wait(c, c.post(f"/api/projects/{pid}/jobs/storyboard").json()["id"])
        assert j["state"] == "awaiting_approval"
        sb = c.get(f"/api/projects/{pid}/storyboard").json()
        assert sb["revision"] == 1 and not sb["approved"] and len(sb["scenes"]) == 2
        usage = json.loads((s.projects_dir / pid / "reports/director_usage.json").read_text())
        assert usage["input_tokens"] == 10 and usage["outcome"] == "ok"
        # edit: valid
        sb["scenes"][0]["visual_description"] = "Edited description"
        r = c.put(f"/api/projects/{pid}/storyboard", json=sb); assert r.status_code == 200 and r.json()["revision"] == 2
        # edit: invalid -> 422 with a useful location, stored version untouched
        sb["scenes"][0]["animation_sequence"][0]["targets"] = ["nope"]
        r = c.put(f"/api/projects/{pid}/storyboard", json=sb); assert r.status_code == 422 and "nope" in json.dumps(r.json())
        assert c.get(f"/api/projects/{pid}/storyboard").json()["revision"] == 2
        assert c.post(f"/api/projects/{pid}/storyboard/approve").json()["approved"] is True
        assert c.get(f"/api/jobs/{j['id']}").json()["state"] == "completed"
        assert (s.projects_dir / pid / "storyboard_history/r001.json").exists()
    c2 = TestClient(create_app(s, director_factory=lambda: None))
    with c2:  # restart
        sb = c2.get(f"/api/projects/{pid}/storyboard").json()
        assert sb["approved"] and sb["scenes"][0]["visual_description"] == "Edited description"


def test_provider_outage_gives_actionable_job_error_and_retry_works(make_client):
    fp = FakeProvider(ProviderError("Bedrock temporarily unavailable (ThrottlingException). Retry shortly.", retryable=True), good())
    c, s = make_client(fp)
    with c:
        pid = c.post("/api/projects", json={"title": "T", "script": SCRIPT, "settings": {"target_duration_s": 10}}).json()["id"]
        j = wait(c, c.post(f"/api/projects/{pid}/jobs/storyboard").json()["id"])
        assert j["state"] == "failed" and "Retry" in j["error"] and "deterministic features" in j["error"]
        assert c.post(f"/api/projects/{pid}/jobs/analyze").status_code == 202  # deterministic path still works
        c.post(f"/api/jobs/{j['id']}/retry")
        assert wait(c, j["id"])["state"] == "awaiting_approval"


def test_automatic_approval_mode(make_client):
    c, s = make_client(FakeProvider(good()))
    with c:
        pid = c.post("/api/projects", json={"title": "T", "script": SCRIPT, "settings": {"target_duration_s": 10, "approval_mode": "automatic"}}).json()["id"]
        assert wait(c, c.post(f"/api/projects/{pid}/jobs/storyboard").json()["id"])["state"] == "completed"
        assert c.get(f"/api/projects/{pid}/storyboard").json()["approved"] is True


def test_connector_requires_endpoints_and_flow_requires_route():
    base = scene(1, "x", visual_elements=[{"id": "a", "kind": "node"}, {"id": "b", "kind": "node"}, {"id": "ar", "kind": "arrow"}, {"id": "pk", "kind": "packet"}])
    with pytest.raises(Exception, match="props.from"):
        DirectorOutput.model_validate({"title": "t", "scenes": [base]})
    ok = scene(1, "x", visual_elements=[{"id": "a", "kind": "node"}, {"id": "b", "kind": "node"}, {"id": "ar", "kind": "arrow", "props": {"from": "a", "to": "b"}}, {"id": "pk", "kind": "packet"}],
               animation_sequence=[{"id": "f", "at": 0, "duration": 1, "action": "flow", "targets": ["pk"], "params": {"route": "ar"}}])
    DirectorOutput.model_validate({"title": "t", "scenes": [ok]})
    ok["animation_sequence"][0]["params"] = {}
    with pytest.raises(Exception, match="params.route"):
        DirectorOutput.model_validate({"title": "t", "scenes": [ok]})
