from src.schemas.chat import ChatThread

def build_prompt_for_diary(thread: ChatThread) -> str:
    messages = sorted(thread.messages, key=lambda x: x.ts_utc)
    lines = [f"{m.sender}: {m.text}" for m in messages if m.text]

    return (
        "아래는 메신저 대화 내용입니다. 이 대화를 보고 오늘 하루를 대표하는 "
        "핵심 키워드를 뽑아줘.\n\n"
        "요구사항:\n"
        "- 하루의 사건/주제/프로젝트를 나타내는 명사 또는 명사구\n"
        "- 예: 팀플, 캡스톤 디자인, 회의 일정 조율, 프로젝트 준비 등\n"
        "- 감정/분위기 키워드도 1~2개 포함 가능 (예: 피곤함, 긴장)\n"
        "- 추상적인 표현(실용적 소통, 유연한 대응 등)은 피하고 구체적으로 작성\n"
        "- 한국어 키워드 3~7개\n"
        "- 키워드만 쉼표로 구분해서 한 줄로 출력\n"
        "- 절대 번호, 설명, 문장 형태는 사용하지 말 것\n\n"
        f"=== 대화 내용 ===\n{chat_text}\n"
    )