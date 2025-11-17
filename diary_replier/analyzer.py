import re
from collections import Counter
from typing import List, Tuple
from .schemas import AnalysisResult
from .analyzer_hf import available as hf_available, predict_emotions as hf_predict


# 아주 단순 키워드 맵 (원하면 계속 확장)
EMO_LEX = {
    "불안": ["불안", "초조", "걱정", "긴장", "두려", "떨려"],
    "슬픔": ["슬프", "우울", "눈물", "상실", "허무", "외롭"],
    "분노": ["화나", "짜증", "열받", "억울", "분노"],
    "피곤": ["피곤", "지침", "번아웃", "과로", "기진"],
    "기쁨": ["행복", "기쁨", "뿌듯", "즐겁", "신남", "설렘"],
}

POS_WORDS = ["좋았", "만족", "성공", "칭찬", "뿌듯", "행복", "기쁨"]
NEG_WORDS = ["힘들", "실수", "후회", "불안", "우울", "짜증", "화나", "좌절", "실망"]

def _extract_keywords(text: str, topk: int = 5) -> List[str]:
    # 아주 단순한 키워드 추출 (영/숫자/한글 단어 기준)
    tokens = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text)
    cnt = Counter(t.lower() for t in tokens)
    stop = {"그리고", "하지만", "그러나", "그래서", "오늘", "정말", "조금", "내일", "약간"}
    keywords = [w for w, _ in cnt.most_common() if w not in stop]
    return keywords[:topk]

def _detect_emotions(text: str) -> List[str]:
    found = []
    for emo, kws in EMO_LEX.items():
        if any(k in text for k in kws):
            found.append(emo)
    return found[:3] if found else []

def _judge_valence(text: str) -> str:
    pos = sum(text.count(w) for w in POS_WORDS)
    neg = sum(text.count(w) for w in NEG_WORDS)
    if pos > neg: return "positive"
    if neg > pos: return "negative"
    return "neutral"

def _make_summary(text: str) -> str:
    # 첫 문장/핵심 문장 간단 요약
    sents = re.split(r"[.!?？。…\n]+", text.strip())
    sents = [s for s in sents if s]
    if not sents: return ""
    head = sents[0][:120]
    if len(sents) > 1:
        tail = sents[-1][:120]
        if head != tail:
            return f"{head} … {tail}"
    return head

def analyze(text: str) -> AnalysisResult:
    return AnalysisResult(
        valence=_judge_valence(text),
        emotions=_detect_emotions(text),
        keywords=_extract_keywords(text),
        summary=_make_summary(text),
    )
def get_llm():
    """
    Monkeypatch에서 DummyLLMClient로 교체하기 위해 필요한 자리만들기용 함수.
    실제 운영에서는 이 함수가 호출되지 않는다.
    """
    raise NotImplementedError("get_llm is only used during tests.")
