# diary_replier/generator.py
from typing import Optional, Dict, Any, List

# ❌ 상단 정적 임포트 금지:
# from diary_replier.llm_providers.openai_client import OpenAILLMClient

def get_llm():
    # ✅ 지연 임포트로 순환 차단
    from diary_replier.llm_providers.openai_client import OpenAILLMClient
    return OpenAILLMClient()

def generate_reply(text: str, options: Optional[Dict[str, Any]] = None, llm=None) -> Dict[str, Any]:
    """
    일기에 대한 답장을 생성하는 최소 예시.
    tests/conftest.py에서 get_llm을 DummyLLMClient로 바꾸면 그대로 대체됨.
    """
    if llm is None:
        llm = get_llm()

    length = ((options or {}).get("length") or "both").lower()

    system = "너는 일기에 따뜻하게 답장하는 친구야. 과장 금지, 한국어, 제안형 조언."
    msgs_short = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"아래 일기에 한 문장으로 짧게 답장해줘.\n\n{text}"},
    ]
    msgs_normal = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"아래 일기에 2~4문장으로 부드럽게 답장해줘.\n\n{text}"},
    ]

    reply_short = None
    reply_normal = None

    if length in ("short", "both"):
        reply_short = llm.chat(msgs_short, temperature=0.6)
    if length in ("normal", "both"):
        reply_normal = llm.chat(msgs_normal, temperature=0.6)

    return {
        "reply_short": reply_short,
        "reply_normal": reply_normal,
    }
