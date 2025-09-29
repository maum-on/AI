from diary_replier.llm_providers.openai_client import OpenAILLMClient

_llm = None
def get_llm():
    global _llm
    if _llm is None:
        _llm = OpenAILLMClient()
    return _llm

def generate_reply(text: str, analysis: dict, style: str = "normal") -> str:
    sys = "너는 따뜻하고 예의 바른 한국어 상담 파트너야."
    quotes = analysis.get("_evidence_quotes", [])[:3]  # 긴 글에서 뽑은 실제 문장들
    quotes_block = ""
    if quotes:
        quotes_block = "일기에서 인용한 문장:\n- " + "\n- ".join(quotes) + "\n"

    ctx = f"""감정 극성: {analysis.get('valence')}
세부 감정: {', '.join(analysis.get('emotions', []))}
키워드: {', '.join(analysis.get('keywords', []))}
하루 요약: {analysis.get('summary')}
{quotes_block}"""

    length_hint = "2~3문장" if style == "short" else "6~9문장"  # 긴 글이면 조금 더 길게
    max_tokens = 400 if style=="short" else 800

    usr = f"""아래 일기에 대해 {length_hint}으로 답장만 작성해.

일기:
{text}

규칙:
- 첫 문장은 공감으로 시작
- 인용된 문장 또는 키워드 중 1~2개를 자연스럽게 반영(직접 인용 표시 없이, 내용만 녹여쓰기)
- 훈수 금지, 필요한 경우 가벼운 제안 1개만
- 존댓말
"""
    return get_llm().call(sys, ctx + "\n" + usr, temperature=0.7, max_tokens=max_tokens)
