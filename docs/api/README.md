# 🧠 Diary Replier API v1

AI 기반 **일기 요약·감정 분석·답장 생성 서비스**의 FastAPI 엔드포인트 문서입니다.  
모든 요청/응답은 `application/json` 형식을 사용하며,  
응답은 항상 JSON 구조로 반환됩니다.

---

## 📑 목차
0️⃣ 헬스 / 버전

1️⃣ 일기 답장 (동기)

2️⃣ 요약 전용 (Summary)

3️⃣ 감정 분석 (Emotion)

---

## 0️⃣ 헬스 / 버전

### 🔹 GET `/healthz`
> 서버 상태 확인용 엔드포인트입니다.

**Response**
```json
{
  "status": "ok"
}
```
### 🔹 GET `/version`
> 서버 버전 및 모델 로드 상태를 반환합니다.

**Response**
```json
{
  "version": "1.0.0",
  "model": "gpt-4o-mini",
  "config_loaded": true
}
```
## 1️⃣ 일기 답장 (동기)
> 사용자의 일기 내용을 바탕으로 AI가 요약과 감정 분석을 수행하고,
선택적으로 짧은 답장(`reply_short`) 및 **일반 답장(`reply_normal`)**을 생성합니다.

**🔸 Endpoint**

`POST /v1/diary/reply`

**🔸 Request Body**
```json
{
  "text": "오늘 너무 힘들었어. 과제가 많아서 불안했어.",
  "user_id": "optional",
  "date": "optional",
  "meta": {},
  "options": {
    "tone": "friend",
    "length": "both",
    "long_mode": "full"
  }
}
```
**🔸 Response (200 OK)**
```json
{
  "reply_short": "많이 힘들었지? 오늘은 잠시 쉬어가도 괜찮아 🌿",
  "reply_normal": "오늘 정말 버거웠겠어요. 잠깐 쉬어가며 자신을 돌봐주는 것도 괜찮아요. 내일은 조금 더 가벼운 하루가 되길 바라요.",
  "safety_flag": false,
  "flags": {
    "danger_words": false
  },
  "analysis": {
    "valence": "negative",
    "emotions": ["불안"],
    "keywords": ["오늘", "불안", "과제"],
    "summary": "오늘 너무 힘들었어. 과제가 많아서 불안했어."
  },
  "version": "1.0.0"
}
```
**🔸 오류 응답 예시**

**📍 400 — text가 비어있을 때**
```json
{
  "error": {
    "code": "EMPTY_TEXT",
    "message": "text is empty"
  }
}
```
**📍 422 — 잘못된 요청 형식**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'text' must be at least 2 characters."
  }
}
```
**📍 500 — 내부 오류 (예: GPT 인증 실패)**
```json
{
  "error": {
    "code": "INTERNAL",
    "message": "pipeline error: Error code: 401 - invalid_api_key"
  }
}
```
**🔸 cURL 테스트 예시**
```bash
curl -X POST http://127.0.0.1:8000/v1/diary/reply \
  -H "Content-Type: application/json" \
  -d '{
    "text": "오늘 너무 힘들었어. 과제가 많아서 불안했어.",
    "options": { "tone": "friend", "length": "both" }
  }'
```

### 🧩 Notes

- reply_short, reply_normal은 설정에 따라 둘 중 하나만 반환될 수 있습니다.

- GPT 호출 실패 시 fallback 답장이 자동 생성됩니다.

- 감정 분석(analysis)은 간단한 규칙 기반으로 동작하며, 추후 LLM 기반으로 확장 예정입니다.

- API 버전(version)은 응답에 항상 포함됩니다.

---

## 2️⃣ 요약 전용 (Summary)

> 일기 또는 긴 텍스트를 요약하여 주요 문장과 키워드를 추출합니다.  
> `reply` API 내부에서도 이 모듈이 먼저 호출됩니다.


**🔸 Endpoint**

`POST /v1/diary/summary`

**🔸 Request**
```json
{
  "text": "오늘은 발표 준비 때문에 하루 종일 정신이 없었다. 내일도 해야 할 게 많다.",
  "options": { "style": "bullet" }
}
```

**🔸 Response (200 OK)**
```json
{
  "summary": "발표 준비로 하루 종일 바빴고, 내일도 해야 할 일이 많음.",
  "keywords": ["발표", "준비", "정신", "내일"],
  "emotions": ["anxiety"],
  "meta": { "len": 43 }
}
```
**🔸 오류 응답 예시**

**📍 400 — 텍스트 누락**
```json
{
  "error": {
    "code": "EMPTY_TEXT",
    "message": "text is empty"
  }
}
```
**📍 500 — 내부 오류**
```json
{
  "error": {
    "code": "INTERNAL",
    "message": "summary error: connection timeout"
  }
}
```
**🔸 cURL 테스트**
```bash
curl -X POST http://127.0.0.1:8000/v1/diary/summary \
  -H "Content-Type: application/json" \
  -d '{
    "text": "오늘은 발표 준비 때문에 하루 종일 정신이 없었다. 내일도 해야 할 게 많다.",
    "options": { "style": "bullet" }
  }'
```

---

## 3️⃣ 감정 분석 (Emotion)
> 텍스트에 포함된 주요 감정(joy, sadness, anger, anxiety 등)을 정량적으로 분석합니다.
일기뿐 아니라 대화, SNS 게시글에도 적용할 수 있습니다.

**🔸 Endpoint**

`POST /v1/diary/emotion`

**🔸 Request**
```json
{
  "text": "요즘 너무 지쳐서 아무것도 하기 싫어."
}
```
**🔸 Response (200 OK)**
```json
{
  "valence": "negative",
  "scores": {
    "joy": 0.05,
    "sadness": 0.70,
    "anger": 0.10,
    "anxiety": 0.45
  },
  "signals": ["스트레스 가능성 있음"],
  "evidence": ["요즘 너무 지쳐서 아무것도 하기 싫어."]
}
```
**🔸 오류 응답 예시**

**📍 422 — 요청 형식 오류**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'text' must not be empty"
  }
}
```
**📍 500 — 내부 오류**
```json
{
  "error": {
    "code": "INTERNAL",
    "message": "emotion error: LLM connection lost"
  }
}
```
**🔸 cURL 테스트**
```bash
curl -X POST http://127.0.0.1:8000/v1/diary/emotion \
  -H "Content-Type: application/json" \
  -d '{ "text": "요즘 너무 지쳐서 아무것도 하기 싫어." }'
```

### 🧩 Notes

- valence: 전반적인 정서 방향 (positive / neutral / negative)

- scores: 각 감정별 intensity 값 (0~1)

- signals: 감정 상태 요약 문장

- evidence: 감정 판단에 사용된 원문 일부