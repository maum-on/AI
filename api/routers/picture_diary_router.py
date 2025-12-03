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

@router.post("/analyze")
async def analyze_picture_diary(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = analyze_image_style(image_bytes)
    return result
