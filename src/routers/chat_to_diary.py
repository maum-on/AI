from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import json

from src.services.ingest import parse_chat
from src.services.diary import build_prompt_for_diary
from diary_replier.generator import generate_reply

router = APIRouter(prefix="/chat-diary", tags=["chat-diary"])

@router.post("/chat-to-diary")
async def chat_to_diary(file: UploadFile = File(...), me_hint: str | None = Form(None)):

    raw = await file.read()

    try:
        payload = json.loads(raw.decode())
    except:
        payload = raw.decode("utf-8", errors="ignore")

    try:
        thread = parse_chat(payload, me_hint)
        prompt = build_prompt_for_diary(thread)
        diary = generate_reply(prompt)
        return {"diary": diary, "prompt_used": prompt}
    except Exception as e:
        raise HTTPException(400, str(e))
