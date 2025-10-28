from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_reply_smoke():
    payload = {"text": "테스트 일기입니다. 조금 힘들었어요.", "meta": {"preset": "warm"}}
    res = client.post("/diary/reply", json=payload)
    assert res.status_code == 200
    j = res.json()
    assert "reply_short" in j and "reply_normal" in j
    assert isinstance(j["analysis"]["keywords"], list)
