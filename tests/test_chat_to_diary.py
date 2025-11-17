from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_chat_to_diary_json():
    with open("tests/samples/insta_sample.json", "rb") as f:
        response = client.post(
            "/chat-diary/chat-to-diary",
            files={"file": ("insta_sample.json", f, "application/json")},
            data={"me_hint": "김가은"}
        )

    print(response.json())
    assert response.status_code == 200
    assert "diary" in response.json()
