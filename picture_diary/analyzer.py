# picture_diary/analyzer.py

import random

def analyze_image_style(image_url: str) -> str:
    """
    이미지 특징을 분석해 대표적인 style 키워드를 반환하는 함수.
    현재는 더미(random) 구현이지만, 나중에 Vision API로 대체 가능.

    style은 picture_diary/generator.py에서 emotion으로 매핑된다.
    """
    style_keywords = [
        "bright",   # → HAPPY
        "cute",     # → HAPPY
        "dark",     # → SAD
        "dynamic",  # → ANGRY
        "complex",  # → ANGRY
        "simple",   # → SHY
        "neutral"   # → EMPTY fallback
    ]

    return random.choice(style_keywords)
