# picture_diary/generator.py

from typing import Mapping
from picture_diary.schemas import PictureDiaryResult

PICTURE_EMOTION_LABELS = ["HAPPY", "SAD", "ANGRY", "SHY", "EMPTY"]


def _decide_emotion(style: Mapping[str, str]) -> str:
    """
    단색(모노톤) 드로잉을 전제로,
    표정(expression) + 선의 에너지(line_energy) + 여백(space_density)만으로
    최종 감정(HAPPY, SAD, ANGRY, SHY, EMPTY)을 결정한다.

    style 예시:
    {
        "expression": "smile" | "sad" | "angry" | "neutral",
        "line_energy": "calm" | "dynamic" | "messy",
        "space_density": "minimal" | "balanced" | "crowded",
        ... (brightness, saturation 등은 무시)
    }
    """

    expression = style.get("expression", "neutral")
    line_energy = style.get("line_energy", "calm")
    space = style.get("space_density", "balanced")

    # 1️⃣ 표정이 최우선
    if expression == "smile":
        # 웃고 있으면 기본적으로 HAPPY
        return "HAPPY"
    if expression == "sad":
        return "SAD"
    if expression == "angry":
        return "ANGRY"
    # shy는 fer에서 직접 나오진 않지만, 나중에 확장 여지를 위해 남겨둠
    if expression == "shy":
        return "SHY"

    # 2️⃣ 표정이 중립/없을 때 → 선 + 여백 기준

    # 선이 매우 지저분/거칠면 감정이 날카롭거나 뒤엉킨 상태로 보고 ANGRY
    if line_energy == "messy":
        return "ANGRY"

    # 선이 역동적(dynamic)인데 단색 드로잉이면,
    # 보통 활기/에너지 쪽으로 해석 → HAPPY 쪽으로 봐줌
    if line_energy == "dynamic":
        return "HAPPY"

    # 여백이 거의 없고 화면이 꽉 차 있으면,
    # 답답하거나 부담스러운 느낌 → SAD 쪽
    if space == "crowded":
        return "SAD"

    # 여백이 넓고 선이 차분하면,
    # 수줍거나 조용한 상태 → SHY
    if space == "minimal" and line_energy == "calm":
        return "SHY"

    # 특별히 강한 신호가 없으면 감정이 비어 있거나 담담한 상태로 보고 EMPTY
    return "EMPTY"


def _build_reason_and_tip(emotion: str, style: Mapping[str, str]) -> tuple[str, str]:
    """
    감정 + 스타일 정보를 바탕으로,
    단색 드로잉 특성에 맞게 reason / tip 텍스트를 생성한다.
    (여기서도 색감 언급은 하지 않는다.)
    """

    expression = style.get("expression", "neutral")
    line_energy = style.get("line_energy", "calm")
    space = style.get("space_density", "balanced")

    if emotion == "HAPPY":
        reason = (
            "표정이나 선의 흐름에서 전반적으로 가볍고 긍정적인 분위기가 느껴져요. "
            "무겁지 않은 구성과 안정된 선 덕분에 편안한 인상이 강해요."
        )
        tip = "이 온화한 기분을 오늘 하루의 작은 힘으로 삼아보면 좋겠어요."
    elif emotion == "SAD":
        reason = (
            "표정이 조금 가라앉아 보이거나, 화면이 빽빽해서 답답한 느낌이 나요. "
            "조용히 감정을 눌러두고 있는 모습일 수도 있어 보여요."
        )
        tip = "지금 느끼는 감정을 혼자만 들고 있지 말고, 믿을 수 있는 사람과 조금 나눠보는 건 어떨까요?"
    elif emotion == "ANGRY":
        reason = (
            "짧고 빠른 선, 또는 뒤엉킨 선들이 많아서 "
            "조금 예민하고 날카로운 에너지가 느껴져요."
        )
        tip = "이 에너지를 운동이나 글쓰기처럼 안전한 방식으로 풀어내보면 도움이 될 거예요."
    elif emotion == "SHY":
        reason = (
            "여백이 넉넉하고 선이 조심스럽게 그려져 있어서, "
            "살짝 부끄럽고 속마음을 바로 드러내지 않는 분위기가 느껴져요."
        )
        tip = "당신의 속도대로 천천히 다가가도 괜찮아요. 서두를 필요는 전혀 없어요."
    else:  # EMPTY
        reason = (
            "강한 감정 표현보다는, 담담하게 장면을 스케치한 느낌이에요. "
            "감정보다는 상황 자체를 기록해 둔 것처럼 보여요."
        )
        tip = "지금 떠오르는 생각이나 기분을 한 줄만 더 적어본다면, 오늘의 나를 조금 더 이해하는 데 도움이 될 거예요."

    return reason, tip


def generate_result(style: Mapping[str, str]) -> PictureDiaryResult:
    """
    analyzer.analyze_image_style() 이 반환한 style 정보를 기반으로
    최종 감정, 이유, 코멘트를 생성한다.
    """
    emotion = _decide_emotion(style)
    reason, tip = _build_reason_and_tip(emotion, style)

    return PictureDiaryResult(
        emotion=emotion,
        reason=reason,
        tip=tip,
    )
