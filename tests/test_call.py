# tests/test_call.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    assert "model" in body
    assert "config_loaded" in body

def test_diary_reply_basic():
    payload = {"text": "오늘 너무 힘들었어. 과제가 많아서 불안했어.", "options": {"length": "both"}}
    r = client.post("/v1/diary/reply", json=payload)
    # 디버깅용 출력 (실패 시 콘솔에서 확인)
    print("\nRESP:", r.status_code, r.text)
    assert r.status_code == 200
    data = r.json()
    # 최소 스키마 검증
    for k in ["reply_short", "reply_normal", "safety_flag", "flags", "analysis"]:
        assert k in data
