# picture_diary/analyzer.py

from typing import Dict

import cv2
import numpy as np
import requests
from fer import FER

# 전역으로 한 번만 로드 (CPU에서도 충분히 돌아감)
_emotion_detector = FER(mtcnn=False)  # mtcnn=True 쓰면 mtcnn 설치 필요


def _download_image(image_url: str) -> np.ndarray:
    """
    URL에서 이미지를 받아와 OpenCV BGR 이미지로 디코딩.
    """
    resp = requests.get(image_url, timeout=5)
    resp.raise_for_status()
    data = np.frombuffer(resp.content, np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("이미지를 디코딩할 수 없습니다.")
    return img


def _analyze_expression(img: np.ndarray) -> str:
    """
    fer 라이브러리로 얼굴 표정 분석 후
    smile / sad / angry / shy / neutral 로 매핑.
    """

    # 전체 이미지에서 최상위 감정 하나만 본다
    try:
        result = _emotion_detector.top_emotion(img)  # (label, score) or None
    except Exception:
        return "neutral"

    if result is None:
        return "neutral"

    label, score = result
    if not label:
        return "neutral"

    label = label.lower()

    # fer label → 우리가 쓰는 expression으로 매핑
    if label in ("happy", "surprise"):
        return "smile"
    if label in ("sad", "disgust"):
        return "sad"
    if label in ("angry", "fear"):
        return "angry"
    if label == "neutral":
        return "neutral"

    # 알 수 없는 라벨은 일단 neutral 처리
    return "neutral"


def _analyze_color(img: np.ndarray) -> Dict[str, str]:
    """
    전체 밝기(V), 채도(S)를 보고
    brightness / saturation 추정.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    mean_v = float(np.mean(v))    # 밝기
    mean_s = float(np.mean(s))    # 채도

    # 밝기 구간
    if mean_v >= 180:
        brightness = "bright"
    elif mean_v <= 80:
        brightness = "dark"
    else:
        brightness = "medium"

    # 채도 구간
    if mean_s >= 140:
        saturation = "vivid"
    elif mean_s <= 60:
        saturation = "greyed"
    else:
        saturation = "soft"

    return {
        "brightness": brightness,
        "saturation": saturation,
    }


def _analyze_lines_and_space(img: np.ndarray) -> Dict[str, str]:
    """
    에지 비율 + 흰 여백 비율로
    line_energy / space_density 추정.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 에지(윤곽선) 비율
    edges = cv2.Canny(gray, 100, 200)
    edge_ratio = float(np.count_nonzero(edges)) / edges.size

    if edge_ratio < 0.03:
        line_energy = "calm"
    elif edge_ratio < 0.10:
        line_energy = "dynamic"
    else:
        line_energy = "messy"

    # 거의 흰색(배경) 픽셀 비율
    _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
    white_ratio = float(np.count_nonzero(thresh)) / thresh.size

    if white_ratio >= 0.7:
        space_density = "minimal"
    elif white_ratio <= 0.3:
        space_density = "crowded"
    else:
        space_density = "balanced"

    return {
        "line_energy": line_energy,
        "space_density": space_density,
    }


def analyze_image_style(image_url: str) -> Dict[str, str]:
    """
    최종 스타일 분석 함수.
    return 예시:
    {
        "expression": "smile",
        "brightness": "bright",
        "saturation": "soft",
        "line_energy": "calm",
        "space_density": "balanced",
    }
    """
    img = _download_image(image_url)

    expression = _analyze_expression(img)
    color_info = _analyze_color(img)
    line_space_info = _analyze_lines_and_space(img)

    style = {
        "expression": expression,
        **color_info,
        **line_space_info,
    }

    return style
