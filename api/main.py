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
# create_reply 내부

@app.post("/v1/diary/reply", response_model=DiaryReplyResponse)
def create_reply(payload: DiaryRequest, pipeline=Depends(get_pipeline)):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")
    try:
        out = pipeline(payload)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(500, detail=f"pipeline error: {e}")
    return out  # Pydantic이 자동 캐스팅


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
