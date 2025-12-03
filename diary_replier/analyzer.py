import re
from collections import Counter
from typing import List, Tuple
from .schemas import AnalysisResult
from .analyzer_hf import available as hf_available, predict_emotions as hf_predict

# -----------------------------
# 감정 키워드 사전
# -----------------------------
EMO_LEX = {
    "불안": ["불안", "초조", "걱정", "긴장", "두려", "떨려"],
    "슬픔": ["슬프", "우울", "눈물", "상실", "허무", "외롭"],
    "분노": ["화나", "짜증", "열받", "억울", "분노"],
    "피곤": ["피곤", "지침", "번아웃", "과로", "기진"],
    "기쁨": ["행복", "기쁨", "뿌듯", "즐겁", "신남", "설렘"],
}

# 긍정/부정 판단용 단어들
POS_WORDS = ["좋았", "만족", "성공", "칭찬", "뿌듯", "행복", "기쁨", "즐겁", "설렘"]
NEG_WORDS = ["힘들", "실수", "후회", "불안", "우울", "짜증", "화나", "좌절", "실망", "억울"]

# -----------------------------
# 키워드 추출
# -----------------------------
def _extract_keywords(text: str, topk: int = 5) -> List[str]:
    tokens = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text)
    cnt = Counter(t.lower() for t in tokens)

    stop = {"그리고", "하지만", "그러나", "그래서", "오늘", "정말", "조금", "내일", "약간"}
    keywords = [w for w, _ in cnt.most_common() if w not in stop]
    return keywords[:topk]

# -----------------------------
# 감정 감지
# -----------------------------
def _detect_emotions(text: str) -> List[str]:
    found = []
    for emo, kws in EMO_LEX.items():
        if any(k in text for k in kws):
            found.append(emo)
    return found[:3] if found else []

# -----------------------------
# ★ normal을 거의 안 만들도록 수정된 valence 판단
# -----------------------------
def _judge_valence(text: str) -> str:
    pos = sum(text.count(w) for w in POS_WORDS)
    neg = sum(text.count(w) for w in NEG_WORDS)

    # 1) 긍정/부정 키워드가 아예 없을 때만 neutral 가능
    if pos == 0 and neg == 0:
        emos = _detect_emotions(text)

        # 기쁨 계열이 있으면 positive
        if "기쁨" in emos:
            return "positive"

        # 슬픔/불안/분노/피곤 등 감정이 잡히면 negative
        if emos:
            return "negative"

        # 진짜 아무 감정도 안 담긴 일기만 neutral
        return "neutral"

    # 2) 키워드가 있으면 neutral 거의 안 나오게
    if pos >= neg:
        return "positive"
    else:
        return "negative"

# -----------------------------
# 요약
# -----------------------------
def _make_summary(text: str) -> str:
    sents = re.split(r"[.!?？。…\n]+", text.strip())
    sents = [s for s in sents if s]
    if not sents:
        return ""
    head = sents[0][:120]
    if len(sents) > 1:
        tail = sents[-1][:120]
        if head != tail:
            return f"{head} … {tail}"
    return head

# -----------------------------
# 메인 analyze 함수
# -----------------------------
def analyze(text: str) -> AnalysisResult:
    valence = _judge_valence(text)
    emotions = _detect_emotions(text)
    summary = _make_summary(text)

    # 감정이 하나도 안 잡혔으면 valence 기준으로 대충이라도 채워주기
    if not emotions:
        if valence == "positive":
            emotions = ["기쁨"]
        elif valence == "negative":
            emotions = ["슬픔"]
        else:
            emotions = []

    return AnalysisResult(
        valence=valence,
        emotions=emotions,
        summary=summary,
    )
# -----------------------------
# (테스트용) LLM Stub
# -----------------------------
def get_llm():
    raise NotImplementedError("get_llm is only used during tests.")
