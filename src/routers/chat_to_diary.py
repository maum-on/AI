# src/routers/chat_to_diary.py

from fastapi import APIRouter, UploadFile, File, Form

from src.services.ingest import ingest_chat_file

router = APIRouter(prefix="/chat-diary", tags=["chat-diary"])


@router.post("/chat-to-diary")
async def chat_to_diary(
    file: UploadFile = File(...),
    me_hint: str = Form(""),
):
    """
    채팅 JSON 파일 + 내 이름 힌트(me_hint)를 받아서
    정규화된 메시지 리스트를 돌려준다.

    우선은 파싱이 잘 되는지 확인하는 용도로 사용.
    """
    messages = ingest_chat_file(file, me_hint)
    # 나중에 여기서 diary 생성 서비스 붙이면 됨.
    return {"messages": messages}
