# FastAPI 서버 (참조 구현)

# api/main.py
from fastapi import FastAPI, Depends, HTTPException
from api.deps import get_settings, get_pipeline
from api.models import DiaryRequest, DiaryReplyResponse

app = FastAPI(title="Diary Replier API", version="1.0.0")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/version")
def version(settings=Depends(get_settings)):
    cfg = settings.cfg or {}
    return {"version": app.version, "model": cfg.get("model_name", "unknown"), "config_loaded": bool(cfg)}

# 이 엔드포인트가 반드시 존재해야 tests/test_api.py 통과
@app.post("/v1/diary/reply", response_model=DiaryReplyResponse)
def create_reply(payload: DiaryRequest, pipeline=Depends(get_pipeline)):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")
    out = pipeline(payload)  # diary_replier.pipeline.diary_to_reply
    # pydantic 모델/딕셔너리 모두 대응
    return out if hasattr(out, "model_dump") else DiaryReplyResponse(**out)
