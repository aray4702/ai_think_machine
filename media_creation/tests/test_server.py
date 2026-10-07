import base64
import time

from fastapi.testclient import TestClient

from media_director.server import create_app
from test_manual import JPEG
from test_manual import scripted as scripted_manual
from test_production import scripted_client


def wait(c, job, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        j = c.get(f"/api/jobs/{job}").json()
        if j["status"] != "running":
            assert j["status"] == "done", j["error"]
            return j["result"]
        time.sleep(0.05)
    raise TimeoutError(job)


def start(c, budget=5):
    s = c.post("/api/sessions", json={"budget": budget}).json()
    return s["id"], s


def test_index_and_static(tmp_path):
    c = TestClient(create_app(tmp_path))
    assert "Media Director" in c.get("/").text
    assert "textContent" in c.get("/static/app.js").text


def test_consent_is_required_before_any_model_call(tmp_path):
    client, requests = scripted_client()
    c = TestClient(create_app(tmp_path, client_factory=lambda: client))
    sid, _ = start(c)
    job = c.post(f"/api/sessions/{sid}/intent", json={"answers": ["a birthday"]}).json()["job"]
    j = c.get(f"/api/jobs/{job}").json()
    while j["status"] == "running":
        time.sleep(0.05)
        j = c.get(f"/api/jobs/{job}").json()
    assert j["status"] == "error" and "approval" in j["error"] and requests == []


def test_automatic_flow_through_the_api(tmp_path):
    client, _ = scripted_client()
    c = TestClient(create_app(tmp_path, client_factory=lambda: client))
    sid, s = start(c)
    assert len(s["questions"]) == 4 and "midjourney" in s["targets"]
    c.post(f"/api/sessions/{sid}/consent")
    draft = wait(c, c.post(f"/api/sessions/{sid}/intent", json={"answers": ["Mira's 10th"]}).json()["job"])
    draft["intent"]["avoid"].append("glitter")  # the person edits the draft
    st = c.post(f"/api/sessions/{sid}/intent/confirm",
                json={"draft": draft, "open_answers": [{"question": "Time?", "answer": "4pm"}]}).json()
    assert st["intent"]["avoid"][-1] == "glitter" and any("4pm" in x for x in st["constraints"])
    concepts = wait(c, c.post(f"/api/sessions/{sid}/concepts").json()["job"])
    st = c.post(f"/api/sessions/{sid}/choose", json={"index": 0, "note": "warmer amber"}).json()
    assert st["concept"]["title"] == concepts[0]["title"] and any("warmer" in x for x in st["constraints"])
    out = wait(c, c.post(f"/api/sessions/{sid}/produce", json={"rounds": 2}).json()["job"])
    assert out["state"]["renders"] and "serves the intent" in out["stopped"]
    png = c.get(f"/api/sessions/{sid}/files/{out['state']['renders'][-1]}")
    assert png.status_code == 200 and png.content[:4] == b"\x89PNG"
    st = wait(c, c.post(f"/api/sessions/{sid}/undo").json()["job"])
    assert st["cursor"] < len(st["versions"]) - 1
    assert c.post(f"/api/sessions/{sid}/export", json={"approved": False}).status_code == 403
    assert c.post(f"/api/sessions/{sid}/export", json={"approved": True}).status_code == 200


def test_files_are_restricted_to_session_outputs(tmp_path):
    c = TestClient(create_app(tmp_path, client_factory=lambda: scripted_client()[0]))
    sid, _ = start(c)
    for name in ("working_state.json", "..%2F..%2Fetc%2Fpasswd", "episodes.jsonl"):
        assert c.get(f"/api/sessions/{sid}/files/{name}").status_code == 404


def test_manual_flow_through_the_api(tmp_path):
    client, requests = scripted_manual()
    c = TestClient(create_app(tmp_path, client_factory=lambda: client))
    sid, _ = start(c)
    c.post(f"/api/sessions/{sid}/consent")
    draft = wait(c, c.post(f"/api/sessions/{sid}/intent", json={"answers": ["Mira's 10th"]}).json()["job"])
    c.post(f"/api/sessions/{sid}/intent/confirm", json={"draft": draft})
    wait(c, c.post(f"/api/sessions/{sid}/concepts").json()["job"])
    c.post(f"/api/sessions/{sid}/choose", json={"index": 0})
    r = wait(c, c.post(f"/api/sessions/{sid}/prompt", json={"target": "midjourney"}).json()["job"])
    assert "--ar 4:5" in r["markdown"]
    rev = wait(c, c.post(f"/api/sessions/{sid}/revise",
                         json={"image_base64": base64.b64encode(JPEG).decode(), "note": "too bright"}).json()["job"])
    assert rev["revision"]["what_misses_the_intent"] == ["too bright"]
    assert c.get(f"/api/sessions/{sid}/files/{rev['file']}").status_code == 200


def test_one_job_at_a_time_and_input_checks(tmp_path):
    c = TestClient(create_app(tmp_path, client_factory=lambda: scripted_client()[0]))
    assert c.post("/api/sessions", json={"budget": 500}).status_code == 400
    sid, _ = start(c)
    assert c.post(f"/api/sessions/{sid}/prompt", json={"target": "nope"}).status_code == 400
    assert c.post(f"/api/sessions/{sid}/revise", json={"image_base64": "%%%"}).status_code == 400
    assert c.get("/api/sessions/unknown").status_code == 404
