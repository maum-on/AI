from src.schemas.chat import ChatThread

def build_prompt_for_diary(thread: ChatThread) -> str:
    messages = sorted(thread.messages, key=lambda x: x.ts_utc)
    lines = [f"{m.sender}: {m.text}" for m in messages if m.text]

    return (
        "아래는 메신저 대화 내용입니다. 이 대화를 보고 오늘 하루를 잘 대표하는 "
        "핵심 키워드를 뽑아줘.\n\n"
        "요구사항:\n"
        "- 하루의 사건, 주제, 활동, 프로젝트를 나타내는 명사/명사구로 작성\n"
        "- 예시: 팀플, 캡스톤 디자인, 회의 일정 조율, 프로젝트 준비, 발표 연습, 일정 조정 등\n"
        "- 감정·분위기 키워드도 1~2개 정도는 포함 가능 (예: 긴장, 뿌듯함, 피곤함)\n"
        "- 가능하면 구체적인 대상/활동/이벤트를 쓰고, "
        "‘실용적인 소통’, ‘유연한 대응’처럼 너무 추상적인 표현은 피하기\n"
        "- 한국어 키워드 3~7개\n"
        "- 키워드만 쉼표로 구분해서 한 줄로 출력\n"
        "- 번호(1., 2.), 문장, 설명, 따옴표는 쓰지 말 것\n\n"
        f"{chat_text}"
    )