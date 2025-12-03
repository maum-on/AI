# picture_diary/schemas.py

from typing import Literal
from pydantic import BaseModel, HttpUrl

EmotionCode = Literal["happy", "sad", "angry", "shy", "empty"]


class AnalyzeEmotionByUrlRequest(BaseModel):
    image_url: HttpUrl


class PictureEmotionResponse(BaseModel):
    emotion: EmotionCode
    emotion_ko: str
    reason: str
