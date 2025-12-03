# src/services/ingest.py

import json
from typing import List, Dict, Any

from fastapi import UploadFile, HTTPException

from src.parsers.base import normalize_generic_chat


def ingest_chat_file(file: UploadFile, me_hint: str) -> List[Dict[str, Any]]:
    """
    업로드된 채팅 JSON 파일을 읽어서
    우리 내부 공통 message 리스트로 변환.
    (인스타/DM 형식: title + participants + messages[...] 기준)
    """
    try:
        raw = json.load(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON 파싱에 실패했습니다: {e}")

    try:
        messages = normalize_generic_chat(raw, me_hint)
    except Exception as e:
        # 어디서 에러 나는지 확인하고 싶으면 e를 detail에 같이 넣어도 됨
        raise HTTPException(
            status_code=400,
            detail=f"지원되지 않는 채팅 형식입니다: {e}",
        )

    if not messages:
        raise HTTPException(
            status_code=400,
            detail="유효한 메시지를 찾지 못했습니다.",
        )

    return messages
