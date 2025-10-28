# 🧠 Diary Replier AI

AI 기반 **일기 답장 생성 서비스**  
이 브랜치는 일기 텍스트를 입력받아 GPT 기반으로 감정 분석과 맞춤형 답장을 생성하는 **AI 엔진(API)** 을 담당합니다.

---

## 📂 주요 기능

| 기능 | 설명 |
|------|------|
| `/diary/reply` | 일기 입력 → 감정 분석 + GPT 답장 생성 |
| `/user/preset` | 사용자별 답장 스타일(warm / coach / short) 저장·조회 |
| `/diary/logs` | 최근 일기·감정 분석 로그 조회 |
| `/health` | 서버 상태 체크 (배포용) |

---

## ⚙️ 실행 방법

### 1️⃣ 환경설정
```bash
# 가상환경
python -m venv .venv
.venv\Scripts\activate

# 라이브러리 설치
pip install -r requirements.txt
```

### 2️⃣ 환경변수 설정
`.env` 파일 생성:
```bash
OPENAI_API_KEY=sk-...          # OpenAI API 키
MODEL_NAME=gpt-4o-mini         # 사용할 모델명
DATABASE_URL=sqlite:///./app.db # 로컬 DB 경로
INTERNAL_API_KEY=mysecretkey   # 내부 호출용 인증키
EMO_MODEL=beomi/KcELECTRA-base # (선택) 감정모델
EMO_TOPK=2                     # 상위 감정 예측 개수
```
### 3️⃣ 실행
```bash
uvicorn api.main:app --reload
```
→ http://127.0.0.1:8000/docs 접속 후 테스트 가능

## 🧩 폴더 구조
```bash
api/
 ├─ main.py              # FastAPI 앱 엔트리포인트
 ├─ middleware.py        # 요청 ID / API Key 미들웨어
 ├─ models.py            # DB 모델 정의
 ├─ routers/
 │   ├─ diary.py         # 일기 답장 API
 │   └─ user.py          # 사용자 프리셋 API
diary_replier/
 ├─ generator.py         # GPT 호출 및 프롬프트 설계
 ├─ analyzer.py          # 감정 분석 (규칙 + HF)
 ├─ analyzer_hf.py       # HuggingFace 감정모델 래퍼
scripts/
 ├─ export_pairs_from_logs.py  # 로그 → CSV 추출
tests/
 ├─ test_reply_smoke.py        # 기본 API 응답 테스트
 ├─ test_quality_rules.py      # 품질 규칙 테스트
docs/
 ├─ ai_workflow.md             # AI 담당자용 워크플로우 문서
```

### 📊 AI 담당 퀵가이드
- 감정 분석 모델 교체: `.env`의 `EMO_MODEL` 수정 후 서버 재시작
- 데이터 추출:
```bash
python scripts/export_pairs_from_logs.py
```
→ exports/pairs_YYYYMMDD_HHMM.csv 생성

### ✅ Markdown preview 예시 JSON
```json
{
  "reply_short": "오늘 하루 고생했어. 잠깐 쉬어가도 괜찮아.",
  "reply_normal": "요즘 많이 지쳤구나. 너무 완벽하려 하지 말고...",
  "analysis": {
    "valence": "negative",
    "emotions": ["피곤","불안"],
    "keywords": ["발표","스트레스"],
    "summary": "발표 준비로 인한 피로감"
  }
}
```

### 📌 branch: diary-replier
담당: AI / NLP / 모델 품질

최종 병합 대상: develop → main