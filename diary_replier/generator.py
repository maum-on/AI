# ⬇ 기존: llm = OpenAILLMClient()  ← 이 줄 삭제
from diary_replier.llm_providers.openai_client import OpenAILLMClient

_llm = None
def get_llm():
    global _llm
    if _llm is None:
        _llm = OpenAILLMClient()
    return _llm

def generate_reply(text: str, analysis: dict, style: str = "normal") -> str:
    sys = "너는 따뜻하고 예의 바른 한국어 상담 파트너야."
    ctx = f"""감정 극성: {analysis.get('valence')}
세부 감정: {', '.join(analysis.get('emotions', []))}
키워드: {', '.join(analysis.get('keywords', []))}
하루 요약: {analysis.get('summary')}"""

    length_hint = "2~3문장" if style == "short" else "5~7문장"

    usr = f"""아래 일기에 대해 {length_hint}으로 답장만 작성해.

일기:
{text}

규칙:
- 공감으로 시작
- 일기의 구체적 디테일 1~2개 반영
- 존댓말
"""
    return get_llm().call(sys, ctx + "\n" + usr, temperature=0.7, max_tokens=400)
