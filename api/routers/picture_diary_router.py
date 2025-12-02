# api/routers/picture_diary_router.py
from fastapi import APIRouter
from picture_diary.schemas import (
    PictureDiaryRequest,
    PictureDiaryResponse
)
from picture_diary.analyzer import analyze_image_style
from picture_diary.generator import generate_result

router = APIRouter(
    prefix="/picture-diary",
    tags=["picture_diary"]
)

@router.post("/analyze", response_model=PictureDiaryResponse)
async def analyze_picture_diary(body: PictureDiaryRequest):
    """
    그림 URL을 받아서 간단한 심리 테스트 결과 생성하는 API
    """
    style = analyze_image_style(req.image_url)
    result = generate_result(style)
    return PictureDiaryResponse(result=result)
