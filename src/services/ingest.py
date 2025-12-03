# src/services/ingest.py

import json
from typing import List, Dict, Any

from fastapi import UploadFile, HTTPException

from src.parsers.base import (
    detect_platform,
    ChatPlatform,
    normalize_generic_chat,
)


def ingest_chat_file(file: UploadFile, me_hint: str) -> List[Dict[str, Any]]:
    """
    업로드된 채팅 JSON 파일을 읽어서
    우리 내부 공통 message 리스트로 변환.
    """
    try:
        raw = json.load(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON 파싱에 실패했습니다: {e}")

    platform = detect_platform(raw)

    if platform == ChatPlatform.GENERIC:
        messages = normalize_generic_chat(raw, me_hint)
    else:
        # 마지막 안전망: 어떻게든 generic으로 한 번 더 시도
        try:
            messages = normalize_generic_chat(raw, me_hint)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="지원되지 않는 채팅 형식입니다.",
            )

    if not messages:
        raise HTTPException(
            status_code=400,
            detail="유효한 메시지를 찾지 못했습니다.",
        )

    return messages
