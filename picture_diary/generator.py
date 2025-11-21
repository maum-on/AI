# picture_diary/generator.py
from picture_diary.schemas import PictureDiaryResult

def generate_result(style: str) -> PictureDiaryResult:
    """
    style 키워드에 기반한 심리 결과 생성 (임시 rule-based)
    """

    mapping = {
        "bright": ("낙천가형", "밝은 색감을 좋아하는 당신은 긍정 에너지가 강한 타입!",
                   "오늘도 좋은 기운이 주변을 채울 거예요."),
        "dark": ("사색가형", "어두운 톤에서 안정감을 느끼는 당신은 깊은 생각을 즐기는 스타일.",
                 "하루에 10분 정도는 산책하며 머리를 비워보세요."),
        "simple": ("미니멀형", "단순함을 좋아하는 당신은 효율과 명확함을 중시하는 성향!",
                   "내일은 잡동사니 하나만 정리해보는 건 어떨까요?"),
        "complex": ("탐험가형", "복잡하고 다채로운 이미지를 좋아하는 당신은 창의적 탐구심이 높아요.",
                    "새로운 아이디어를 적어보면 좋은 날이에요."),
        "cute": ("애정가형", "귀여운 요소가 있는 그림에 끌리는 당신은 따뜻함을 중요하게 여겨요.",
                 "지인에게 짧은 안부 한 마디 전해보면 좋겠어요."),
        "dynamic": ("모험가형", "움직임과 에너지 있는 그림을 좋아하는 당신은 적극적인 타입!",
                     "오늘 작은 도전을 하나 실행해보세요.")
    }

    type_, desc, tip = mapping.get(style, (
        "자유로운 영혼형",
        "당신은 틀에 얽매이지 않는 자유로운 성향!",
        "오늘은 직감이 좋은 판단을 도와줄 거예요."
    ))

    return PictureDiaryResult(type=type_, description=desc, extra_tip=tip)
