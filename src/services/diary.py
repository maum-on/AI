from src.schemas.chat import ChatThread

def build_prompt_for_diary(thread: ChatThread) -> str:
    messages = sorted(thread.messages, key=lambda x: x.ts_utc)
    lines = [f"{m.sender}: {m.text}" for m in messages if m.text]

    return (
        "아래는 오늘 대화 내용입니다. 이 내용을 바탕으로 키워드 작성해줘.\n"
        "감정/상황/분위기를 담아 자연스러운 키워드 3~5개.\n\n"
        + "\n".join(lines)
    )
