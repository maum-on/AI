import json
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    assert "version" in r.json()

def test_diary_reply_endpoint(sample_text):
    payload = {
        "text": sample_text,
        "user_id": "u1",
        "options": {"tone":"mentor","length":"both"}
    }
    r = client.post("/v1/diary/reply", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "reply_short" in data
    assert "reply_normal" in data
    assert "safety_flag" in data
    assert "flags" in data
    assert "analysis" in data
    assert data["analysis"]["valence"] in ["positive","neutral","negative"]
