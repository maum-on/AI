# src/routers/chat_to_diary.py

from typing import Any, Dict, List, Optional

import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI

router = APIRouter(
    prefix="/chat-diary",
    tags=["chat-diary"],
)

# OPENAI_API_KEY는 .env + api/main.py에서 load_dotenv() 로 이미 로드된 상태라고 가정
client = OpenAI()


class ChatToDiaryResponse(BaseModel):
    """
    chat-to-diary 엔드포인트의 최종 응답 스키마.

    백엔드(Spring)에서는 이 구조 그대로 받아서:
    - diary_text: 일기 본문 저장
    - title: 일기 제목으로 사용 (없으면 DM title 사용 가능)
    - used_me_hint: 프롬프트에 사용된 me_hint (백엔드에서 참고용)
    - keywords: 일기를 대표하는 키워드 5~7개
    """
    diary_text: str
    title: Optional[str] = None
    used_me_hint: Optional[str] = None
    keywords: List[str]


def _build_conversation_text(messages: List[Dict[str, Any]]) -> str:
    """
    DM JSON의 messages 배열을 사람이 읽기 쉬운 텍스트로 정리.
    (모델에게 그대로 JSON을 던지는 것보다 토큰을 절약하고 명확하게 전달)
    """
    if not messages:
        return "(메시지가 없습니다.)"

    # timestamp_ms 기준으로 오래된 것부터 정렬
    sorted_msgs = sorted(messages, key=lambda m: m.get("timestamp_ms", 0))

    lines: List[str] = []
    for m in sorted_msgs:
        sender = m.get("sender_name", "알 수 없음")
        content = m.get("content", "")
        # 빈 content는 건너뛰기
        if not content:
            continue
        lines.append(f"[{sender}] {content}")

    return "\n".join(lines)


def _build_system_prompt() -> str:
    """
    chat-to-diary용 시스템 프롬프트.
    - 일기 텍스트 + 키워드 5~7개를 JSON으로 출력하도록 규정
    """
    return """
당신은 인스타 DM 대화 내용을 기반으로 '일기'를 작성하고, 핵심 키워드를 추출하는 어시스턴트입니다.

[역할]
1) 사용자가 보내는 DM 대화를 읽고 '나'의 시점에서 자연스러운 한국어 일기를 작성합니다.
2) 일기 내용을 보고 핵심 키워드 5~7개를 뽑아 JSON 배열로 제공합니다.
   - 키워드는 1~2 단어(예: "팀프로젝트", "회의", "과제", "피곤", "응원")
   - 너무 긴 문장은 금지
   - 감정/주제/상황 중심으로 요약

[일기 작성 방식]
- 어떤 일이 있었는지 (상황, 맥락)
- 상대방과 어떤 대화를 나눴는지 (핵심 위주)
- 내가 어떤 기분이었는지, 무엇을 느꼈는지
- 앞으로의 생각이나 다짐이 자연스럽게 이어지면 좋음
- 채팅 말투(ㅋㅋ, ㅠㅠ 등)는 필요하면 일부만 살리고, 전체적으로는 일기답게 정리된 문장으로 작성

[주의사항]
- 메시지를 하나하나 나열하지 말고, 자연스러운 "글"로 재구성하세요.
- 지나치게 과장된 위로나 조언 말고, 실제 내가 쓸 법한 담백한 일기 느낌으로 씁니다.
- 날짜가 명시되어 있지 않아도 "오늘", "요즘" 등의 표현은 자연스럽게 사용해도 됩니다.

[출력 형식]
반드시 아래 JSON 형태로만 출력하세요. 다른 텍스트는 절대 출력하지 마세요.

{
  "diary_text": "완성된 일기 본문을 여기에 작성합니다.",
  "title": "일기 제목으로 쓸만한 한 줄 (예: DM 제목이나 오늘의 키워드)",
  "used_me_hint": "모델이 참고한 me_hint 문자열 (없거나 비어 있으면 빈 문자열)",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
}

- keywords에는 반드시 5~7개의 문자열만 넣어야 합니다.
- 키워드는 일기의 핵심 주제와 감정을 잘 대표해야 합니다.
""".strip()


def _build_user_prompt(
    raw: Dict[str, Any],
    me_hint: str,
) -> str:
    """
    OpenAI에 보낼 user 프롬프트 구성.
    DM JSON과 me_hint를 이용해 모델에게 상황 설명.
    """
    title = raw.get("title", "")
    participants = raw.get("participants", [])
    messages = raw.get("messages", [])

    conversation_text = _build_conversation_text(messages)

    participants_txt = ", ".join(
        p.get("name", "알 수 없음") for p in participants
    ) or "(참여자 정보 없음)"

    return f"""
다음은 인스타 DM 대화의 일부입니다.

[대화 제목]
{title or "(제목 없음)"}

[참여자]
{participants_txt}

[나에 대한 힌트 (me_hint)]
{me_hint or "(백엔드에서 따로 관리되고, 여기에는 별도 힌트가 없습니다.)"}

[대화 내용]
아래는 시간 순서대로 정리한 대화입니다.

=== 대화 시작 ===
{conversation_text}
=== 대화 끝 ===

위 DM 대화 내용을 바탕으로, '나'의 입장에서 오늘 있었던 일을 한국어 일기 형식으로 정리해 주세요.
그리고 일기 내용을 보고 핵심 키워드 5~7개를 함께 추출해 주세요.
반드시 이전에 설명한 JSON 형식으로만 출력해야 합니다.
""".strip()


@router.post("/chat-to-diary", response_model=ChatToDiaryResponse)
async def chat_to_diary(
    file: UploadFile = File(..., description="인스타 DM JSON 파일"),
    me_hint: str = Form("", description="사용자에 대한 힌트(이름, 별명 등)"),
):
    """
    인스타 DM 형식의 JSON 파일을 받아,
    '나'의 입장에서 쓴 일기 텍스트와 키워드를 생성해 주는 엔드포인트.

    - file: 인스타 DM 내보내기 JSON
      (예: { "title": "...", "participants": [...], "messages": [...] } 구조)
    - me_hint: 나를 식별하는 힌트 문자열 (예: "가톨릭대 23 캡스톤 김가은")
      실제 user_id는 백엔드(Spring)에서 관리하며, 이 API는 문자열 힌트만 사용.
    """
    # 1) JSON 파싱
    try:
        contents = await file.read()
        raw = json.loads(contents)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"JSON 파싱 실패: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"파일 처리 중 오류 발생: {e}",
        )

    # 최소 구조 체크
    if "messages" not in raw or not isinstance(raw["messages"], list):
        raise HTTPException(
            status_code=400,
            detail="유효한 DM JSON 형식이 아닙니다. 'messages' 배열이 필요합니다.",
        )

    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(raw, me_hint)

    # 2) OpenAI 호출
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # 필요하면 gpt-4o로 변경 가능
            temperature=0.5,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI API 호출 실패: {e}",
        )

    msg = resp.choices[0].message

    # response_format=json_object 덕분에 parsed가 있을 수도 있고,
    # 없으면 content를 직접 파싱
    try:
        data: Dict[str, Any] = getattr(msg, "parsed", None) or json.loads(msg.content)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="OpenAI 응답을 JSON으로 파싱하는 데 실패했습니다.",
        )

    diary_text = data.get("diary_text")
    if not diary_text:
        raise HTTPException(
            status_code=500,
            detail="OpenAI 응답에 diary_text 필드가 없습니다.",
        )

    # title은 응답에 없으면 DM title을 fallback으로 사용
    title = data.get("title") or raw.get("title") or None
    used_me_hint = data.get("used_me_hint") or me_hint or ""

    keywords = data.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        raise HTTPException(
            status_code=500,
            detail="OpenAI 응답에 keywords 필드가 없거나 형식이 올바르지 않습니다.",
        )

    # 안전하게 문자열만 남기기 + 개수 살짝 정리(최대 7개)
    clean_keywords: List[str] = []
    for kw in keywords:
        if not isinstance(kw, str):
            continue
        kw = kw.strip()
        if kw:
            clean_keywords.append(kw)

    if not clean_keywords:
        raise HTTPException(
            status_code=500,
            detail="유효한 키워드를 추출하지 못했습니다.",
        )

    # 최대 7개까지만 사용 (모델이 10개 보내도 자르기)
    if len(clean_keywords) > 7:
        clean_keywords = clean_keywords[:7]

    result = ChatToDiaryResponse(
        diary_text=diary_text,
        title=title,
        used_me_hint=used_me_hint,
        keywords=clean_keywords,
    )

    return JSONResponse(result.model_dump())
