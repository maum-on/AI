# api/routers/picture_diary_router.py

from fastapi import APIRouter

from picture_diary.schemas import AnalyzeEmotionByUrlRequest, PictureEmotionResponse
from picture_diary.service import analyze_emotion_by_image_url

router = APIRouter(
    prefix="/picture",
    tags=["picture_diary"],
)


@router.post("/emotion/url", response_model=PictureEmotionResponse)
def analyze_emotion_from_url(payload: AnalyzeEmotionByUrlRequest) -> PictureEmotionResponse:
    """
    이미지 URL을 받아 gpt-4o vision으로 감정을 분석하는 엔드포인트.
    """
    return analyze_emotion_by_image_url(str(payload.image_url))


@router.get("/health")
def picture_diary_health():
    return {"status": "ok", "service": "picture_diary"}
