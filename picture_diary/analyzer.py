# picture_diary/analyzer.py

import random

def analyze_image_style(image_url: str) -> str:
    """
    이미지 URL 기반으로 심리 타입에 영향을 줄 법한 '특성'을 산출하는 더미 함수.
    실제로는 Vision API 또는 ML 모델로 확장 가능.
    """
    keywords = ["bright", "dark", "simple", "complex", "cute", "dynamic"]
    return random.choice(keywords)
