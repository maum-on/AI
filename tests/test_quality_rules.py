import re
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

BANNED_TONES = ["진단", "처방", "약물", "법적 책임", "규탄", "야단", "혼내"]

def test_format_and_tone():
    payload = {"text": "오늘 집중이 잘 안 됐고 스스로에게 실망했어.", "meta": {"preset": "warm"}}
    r = client.post("/diary/reply", json=payload)
    assert r.status_code == 200
    j = r.json()

    # 필수 필드
    assert "reply_short" in j and "reply_normal" in j
    rs, rn = j["reply_short"], j["reply_normal"]

    # 길이/형식 간단 점검
    assert 20 <= len(rs) <= 180
    assert 80 <= len(rn) <= 500

    # 금지 톤 단어 점검
    joined = (rs + " " + rn)
    for bad in BANNED_TONES:
        assert bad not in joined
