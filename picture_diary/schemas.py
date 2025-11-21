# picture_diary/schemas.py
from pydantic import BaseModel, HttpUrl

class PictureDiaryRequest(BaseModel):
    image_url: HttpUrl  # 백엔드에서 넘겨주는 그림 이미지 URL

class PictureDiaryResult(BaseModel):
    type: str           # 예: "모험가형", "감성형" 같은 심리 타입
    description: str    # 결과 설명
    extra_tip: str      # 추가 코멘트

class PictureDiaryResponse(BaseModel):
    result: PictureDiaryResult
