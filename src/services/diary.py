from src.schemas.chat import ChatThread

def build_prompt_for_diary(thread: ChatThread) -> str:
    # 대화 정렬
    messages = sorted(thread.messages, key=lambda x: x.ts_utc)

    # "플레이어: 내용" 형태로 변환
    lines = [f"{m.sender}: {m.text}" for m in messages if m.text]

    # 여기서 chat_text를 반드시 만들어줘야 함!!
    chat_text = "\n".join(lines)

    return (
        "아래는 메신저 대화 내용입니다. "
        "대화를 기반으로 오늘 사용자의 감정을 반드시 한 가지로 분류해주세요.\n\n"
        "선택 가능한 감정:\n"
        "- Happy: 기쁨, 만족, 편안함, 즐거움\n"
        "- Sad: 슬픔, 아쉬움, 외로움\n"
        "- Angry: 짜증, 불만, 화남, 답답함\n"
        "- Shy: 부끄러움, 조심스러움, 부담됨, 어색함\n"
        "- Empty: 감정 신호가 거의 없거나 무표정 상태\n\n"
        "규칙:\n"
        "- 반드시 위 5개 중 하나만 출력\n"
        "- 설명 금지, 단일 단어로만 출력\n"
        "- 감정이 아주 약하게라도 드러나면 해당 카테고리 선택\n"
        "- 모호하다고 해서 자동으로 Empty를 선택하지 말 것\n\n"
        f"=== 대화 내용 ===\n{chat_text}\n\n"
        "=== 감정 ==="
    )