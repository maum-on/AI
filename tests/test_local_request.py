import requests
import json

url = "http://127.0.0.1:8000/v1/diary/reply"
payload = {
    "text": "오늘 너무 힘들었어. 과제가 많아서 불안했어.",
    "options": {"tone": "friend", "length": "both"}
}

res = requests.post(url, json=payload)
print(f"Status: {res.status_code}")
print(json.dumps(res.json(), ensure_ascii=False, indent=2))
