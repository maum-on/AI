# src/routers/chat_to_diary.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import json

router = APIRouter(prefix="/chat-diary", tags=["chat-diary"])


@router.post("/chat-to-diary")
async def chat_to_diary(
    file: UploadFile = File(...),
    me_hint: str = Form(""),
):
    """
    디버깅용: 파일을 그대로 읽어서 key만 돌려준다.
    ingest / parser 다 생략.
    """
    try:
        raw = json.load(file.file)
    except Exception as e:
        # 여기서만 400을 던짐
        raise HTTPException(status_code=400, detail=f"JSON 파싱 실패: {e}")

    return {
        "raw_keys": list(raw.keys()),
        "me_hint": me_hint,
    }
