# diary_replier/analyzer.py
from typing import Dict, Any, List
import re

def get_llm():
    from diary_replier.llm_providers.openai_client import OpenAILLMClient
    return OpenAILLMClient()

def summarize_text(text: str, options: Dict[str, str], settings=None) -> Dict[str, Any]:
    style = (options or {}).get("style", "paragraph")
    # 간단 규칙 베이스 + 선택적 LLM 호출로 확장 가능
    summary = text[:200] + ("..." if len(text) > 200 else "")
    keywords = _extract_keywords(text)
    emotions = _guess_emotions(text)
    if style == "bullet":
        summary = "• " + summary
    return {"summary": summary, "keywords": keywords, "emotions": emotions, "meta": {"len": len(text)}}

def emotion_scores(text: str, settings=None) -> Dict[str, Any]:
    lower = text.lower()
    scores = {"joy":0.1,"sadness":0.1,"anger":0.1,"anxiety":0.1}
    if any(k in lower for k in ["행복","좋아","기뻐","재밌","설레"]): scores["joy"]=0.6
    if any(k in lower for k in ["슬프","우울"]): scores["sadness"]=0.6
    if any(k in lower for k in ["화나","짜증"]): scores["anger"]=0.6
    if any(k in lower for k in ["불안","걱정","긴장"]): scores["anxiety"]=0.6
    valence = "positive" if scores["joy"]>0.5 else ("negative" if scores["sadness"]+scores["anger"]+scores["anxiety"]>0.9 else "neutral")
    signals = []
    if scores["anxiety"]>0.5: signals.append("스트레스 가능")
    evidence = _pick_evidence(text)
    return {"valence": valence, "scores": scores, "signals": signals, "evidence": evidence}

def analyze_conversation(convo: Dict[str, Any], settings=None) -> Dict[str, Any]:
    msgs = convo.get("messages", [])
    # 매우 단순 세션 분할(30분 간격 등은 이후 확장)
    session_id = "s1"
    text_join = "\n".join(m.get("text","") for m in msgs if m.get("text"))
    s = summarize_text(text_join, options={"style":"paragraph"}, settings=settings)
    e = emotion_scores(text_join, settings=settings)
    report = {
        "thread_id": convo.get("thread_id",""),
        "sessions": [{
            "session_id": session_id,
            "summary": s["summary"],
            "keywords": s["keywords"],
            "topics": [{"label":"일반","rep": s["keywords"][0] if s["keywords"] else ""}],
            "affect": {**e["scores"], "valence": e["valence"]},
            "signals": e["signals"]
        }],
        "global": {
            "summary": s["summary"],
            "open_issues": [],
            "todos": []
        },
        "version": "1.0.0"
    }
    return report

# --- helpers ---
def _extract_keywords(text: str) -> List[str]:
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", text)
    freq = {}
    for w in words:
        if len(w) < 2: continue
        freq[w] = freq.get(w,0)+1
    return [w for w,_ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:8]]

def _guess_emotions(text: str) -> List[str]:
    ls = text.lower()
    out = []
    if any(k in ls for k in ["불안","걱정","긴장","anxiety"]): out.append("anxiety")
    if any(k in ls for k in ["기뻐","좋아","행복","즐거","joy"]): out.append("joy")
    if any(k in ls for k in ["화나","짜증","분노","anger"]): out.append("anger")
    if any(k in ls for k in ["슬프","우울","sad"]): out.append("sadness")
    return out

def _pick_evidence(text: str) -> List[str]:
    sents = re.split(r"[.!?\n]+", text)
    sents = [s.strip() for s in sents if s.strip()]
    return sents[:2]
