import json, re
from typing import List, Dict
from diary_replier.llm_providers.openai_client import OpenAILLMClient

_llm = None
def get_llm():
    global _llm
    if _llm is None:
        _llm = OpenAILLMClient()
    return _llm

def _split_paragraphs(text:str) -> List[str]:
    # 빈 줄 기준 문단 분할, 너무 짧은 문장 합치기
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    merged = []
    buf = ""
    for p in paras:
        if len(p) < 80:
            buf = (buf + " " + p).strip()
        else:
            if buf: merged.append(buf); buf=""
            merged.append(p)
    if buf: merged.append(buf)
    return merged

def _chunk(paras: List[str], max_chars=800) -> List[str]:
    # 문자 길이 기준 단순 청크 (토크나이저 없이도 안전)
    chunks, cur = [], ""
    for p in paras:
        if len(cur)+len(p)+2 <= max_chars:
            cur = (cur + "\n\n" + p).strip()
        else:
            if cur: chunks.append(cur)
            cur = p
    if cur: chunks.append(cur)
    return chunks

def _summarize_chunk(chunk: str) -> Dict:
    system = "너는 한국어 일기 요약 도우미야. JSON으로 핵심/감정/키워드를 반환해."
    user = f"""다음 일기 부분을 요약해줘.
일기 부분:
{chunk}

형식:
{{"mini_summary":"", "emotions":[], "keywords":[], "notable_quotes":[]}}
규칙:
- mini_summary는 1~2문장
- 일기의 문장 중 특징적인 1~3개를 notable_quotes에 그대로 담아줘(따옴표 없이)
"""
    raw = get_llm().call(system, user, temperature=0.2, max_tokens=280)
    try:
        return json.loads(raw)
    except:
        return {"mini_summary": chunk[:120], "emotions": [], "keywords": [], "notable_quotes": []}

def _reduce_summaries(items: List[Dict]) -> Dict:
    # map 결과 합치기
    all_summ = [it.get("mini_summary","") for it in items]
    all_emot = sum([it.get("emotions",[]) for it in items], [])
    all_keys = sum([it.get("keywords",[]) for it in items], [])
    all_quotes = sum([it.get("notable_quotes",[]) for it in items], [])

    # 통합 요약 프롬프트
    system = "너는 한국어 통합 요약 도우미야. JSON으로 결과를 반환해."
    user = f"""다음 조각 요약들을 하나의 하루 요약으로 통합해줘.

조각 요약들:
{all_summ}

형식:
{{"valence":"positive|neutral|negative","emotions":[], "keywords":[], "summary":""}}

참고:
- 조각에서 많이 등장하는 감정/키워드를 우선 반영
- summary는 2~3문장
"""
    raw = get_llm().call(system, user, temperature=0.2, max_tokens=220)
    try:
        merged = json.loads(raw)
    except:
        merged = {"valence":"neutral","emotions":[],"keywords":[],"summary":" / ".join(all_summ)[:300]}
    # 디테일(인용) 보존
    merged["_evidence_quotes"] = list(dict.fromkeys(all_quotes))[:6]
    merged["_keywords_all"] = list(dict.fromkeys(all_keys))[:12]
    return merged

def analyze_diary_long(text: str, max_chars_per_chunk=800) -> dict:
    paras = _split_paragraphs(text)
    chunks = _chunk(paras, max_chars=max_chars_per_chunk)
    mapped = [_summarize_chunk(c) for c in chunks]
    merged = _reduce_summaries(mapped)
    return {
        "valence": merged.get("valence","neutral"),
        "emotions": merged.get("emotions",[]),
        "keywords": merged.get("keywords",[]),
        "summary": merged.get("summary",""),
        # 답장 품질 향상을 위한 보조 필드
        "_evidence_quotes": merged.get("_evidence_quotes", []),
        "_keywords_all": merged.get("_keywords_all", []),
    }

def analyze_diary(text: str) -> dict:
    # 기본(짧은 글) 분석: 기존 경로 유지
    system = "너는 한국어 일기 분석 도우미야. JSON으로 감정/키워드/요약을 반환해."
    user = f"""일기:
{text}

형식: {{"valence":"positive|neutral|negative","emotions":[],"keywords":[],"summary":""}}"""
    try:
        raw = get_llm().call(system, user, temperature=0.2, max_tokens=256)
        return json.loads(raw)
    except:
        return {"valence": "neutral", "emotions": [], "keywords": [], "summary": text[:60]}
