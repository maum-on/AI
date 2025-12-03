# picture_diary/service.py

import json
from typing import Dict, Any

from fastapi import HTTPException
from openai import OpenAI

from .prompt_engine import build_vision_system_prompt
from .schemas import PictureEmotionResponse

client = OpenAI()  # OPENAI_API_KEY는 .env에서 로드됨


def analyze_emotion_by_image_url(image_url: str) -> PictureEmotionResponse:
    system_prompt = build_vision_system_prompt()

    try:
        resp = client.chat.completions.create(
            model="gpt-4o",  # 필요하면 gpt-4o 로 변경
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "다음 사진 속 메인 인물의 감정을 분석해 주세요."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to call OpenAI Vision API: {e}")

    message = resp.choices[0].message

    if getattr(message, "parsed", None) is not None:
        data: Dict[str, Any] = message.parsed
    else:
        try:
            data = json.loads(message.content)
        except Exception:
            raise HTTPException(status_code=500, detail="OpenAI 응답 JSON 파싱 실패")

    for key in ("emotion", "emotion_ko", "reason"):
        if key not in data:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI 응답에 필요한 필드({key})가 없습니다."
            )

    return PictureEmotionResponse(
        emotion=data["emotion"],
        emotion_ko=data["emotion_ko"],
        reason=data["reason"],
    )
