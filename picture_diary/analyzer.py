# picture_diary/analyzer.py

from io import BytesIO
from typing import Dict, Any, Tuple

from PIL import Image, ImageStat


def _get_foreground_mask(
    img_gray: Image.Image,
    threshold: int = 230,
) -> Tuple[int, int, float, Tuple[float, float]]:
    """
    단색 그림이라고 가정하고,
    - 배경은 거의 흰색(밝은 값)
    - 선/색이 있는 부분은 더 어둡다고 보고
    foreground(그려진 부분) 마스크를 계산한다.

    반환:
      - fg_count: 선/색이 있는 픽셀 수
      - total: 전체 픽셀 수
      - fill_ratio: 채움 비율 (0~1)
      - center_of_mass: (cx, cy) 0~1 스케일 (좌→우, 상→하)
    """
    w, h = img_gray.size
    pixels = img_gray.load()

    fg_count = 0
    sum_x = 0.0
    sum_y = 0.0

    for y in range(h):
        for x in range(w):
            v = pixels[x, y]  # 0(검정) ~ 255(흰색)
            # threshold 보다 어두우면 '그려진 부분'으로 간주
            if v < threshold:
                fg_count += 1
                sum_x += x
                sum_y += y

    total = w * h
    if fg_count == 0:
        # 아무 것도 안 그려진 경우, 중앙에 있다고 가정
        return 0, total, 0.0, (0.5, 0.5)

    fill_ratio = fg_count / total
    cx = (sum_x / fg_count) / w   # 0 ~ 1
    cy = (sum_y / fg_count) / h   # 0 ~ 1

    return fg_count, total, fill_ratio, (cx, cy)


def analyze_image_style(image_bytes: bytes) -> Dict[str, Any]:
    """
    단색 그림(선 + 배경) 기준 스타일 분석기.

    - 얼마나 많이 칠해졌는지 (fill_ratio) → 단순/복잡
    - 그림의 중심이 위/가운데/아래 어디에 있는지 → 안정감
    - 좌우로 치우쳤는지 → 균형감
    """
    # 1) 이미지 로드
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size

    # 2) 그레이스케일 변환
    img_gray = img.convert("L")

    # 3) 선/색이 있는 부분(전경) 마스크 추출
    fg_count, total, fill_ratio, (cx, cy) = _get_foreground_mask(
        img_gray,
        threshold=230,
    )

    # 4) 채움 비율 기반 설명
    if fill_ratio < 0.02:
        density_label = "매우 미니멀한 그림 (여백이 거의 대부분)"
    elif fill_ratio < 0.07:
        density_label = "여백이 많은 단순한 그림"
    elif fill_ratio < 0.15:
        density_label = "적당히 채워진 그림"
    elif fill_ratio < 0.30:
        density_label = "꽤 풍부하게 채워진 그림"
    else:
        density_label = "화면을 가득 채운 강한 인상의 그림"

    # 5) 중심의 세로 위치 (위/가운데/아래 느낌)
    if cy < 0.4:
        vertical_label = "화면 위쪽에 요소가 모여 있어 가벼운 느낌"
    elif cy > 0.6:
        vertical_label = "화면 아래쪽에 무게가 실려 안정적인 느낌"
    else:
        vertical_label = "화면 중앙에 요소가 모여 균형 잡힌 느낌"

    # 6) 좌우 치우침
    if cx < 0.4:
        horizontal_label = "왼쪽으로 살짝 치우친 구도"
    elif cx > 0.6:
        horizontal_label = "오른쪽으로 살짝 치우친 구도"
    else:
        horizontal_label = "좌우 균형이 비교적 잘 맞는 구도"

    return {
        "width": w,
        "height": h,
        "fill_ratio": fill_ratio,
        "center_of_mass": {
            "x": cx,  # 0(왼쪽) ~ 1(오른쪽)
            "y": cy,  # 0(위) ~ 1(아래)
        },
        "density_label": density_label,
        "vertical_label": vertical_label,
        "horizontal_label": horizontal_label,
    }
