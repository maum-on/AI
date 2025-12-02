# picture_diary/schemas.py
from pydantic import BaseModel, HttpUrl

class PictureDiaryRequest(BaseModel):
    image_url: HttpUrl  # 백엔드에서 넘겨주는 그림 이미지 URL


class PictureDiaryResult(BaseModel):
    emotion: str        # "HAPPY", "SAD", "ANGRY", "SHY", "EMPTY"
    reason: str         # 감정 판단 이유/짧은 설명
    tip: str            # 감정에 맞는 추가 코멘트


class PictureDiaryResponse(BaseModel):
    result: PictureDiaryResult
