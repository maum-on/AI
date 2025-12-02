# picture_diary/generator.py

from picture_diary.schemas import PictureDiaryResult

# 5가지 감정 라벨
PICTURE_EMOTION_LABELS = ["HAPPY", "SAD", "ANGRY", "SHY", "EMPTY"]

def generate_result(style: str) -> PictureDiaryResult:
    """
    그림 style 기반으로 5가지 감정(HAPPY, SAD, ANGRY, SHY, EMPTY) 중 하나를 매핑.
    이전의 '모험가형/미니멀형' 등 성격 타입은 완전히 제거.
    """

    # style → emotion 매핑 (원하면 더 정교하게 튜닝 가능)
    style_to_emotion = {
        "bright": "HAPPY",
        "cute": "HAPPY",

        "dark": "SAD",

        "dynamic": "ANGRY",      # 강렬한 움직임 → 에너지/분노 계열로 해석
        "complex": "ANGRY",      # 복잡하고 강한 대비 → 긴장/압도감 → ANGRY 계열 처리

        "simple": "SHY",         # 단정하고 담백한 구성 → 조심스러움/소극적 에너지
    }

    # fallback: 감정이 명확하지 않은 그림 → EMPTY
    emotion = style_to_emotion.get(style, "EMPTY")

    # 감정별 기본 reason & tip
    emotion_reason_tip = {
        "HAPPY": (
            "밝고 긍정적인 분위기가 느껴져요.",
            "오늘의 좋은 에너지를 오래 간직해보세요!"
        ),
        "SAD": (
            "조금은 차분하고 감성적인 느낌이에요.",
            "감정이 쌓이지 않도록 자신을 가볍게 돌봐주세요."
        ),
        "ANGRY": (
            "강렬한 색감이나 움직임에서 에너지가 느껴져요.",
            "이 에너지를 생산적인 방향으로 사용해보면 도움이 돼요."
        ),
        "SHY": (
            "섬세하고 조용한 분위기가 느껴져요.",
            "천천히 당신만의 속도로 하루를 걸어가도 괜찮아요."
        ),
        "EMPTY": (
            "특정 감정이 강하게 드러나지 않는 그림이에요.",
            "자유롭게 오늘 기분을 가볍게 표현해보는 건 어떨까요?"
        ),
    }

    reason, tip = emotion_reason_tip[emotion]

    return PictureDiaryResult(
        emotion=emotion,
        reason=reason,
        tip=tip,
    )
