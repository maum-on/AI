# diary_replier/analyzer.py

import re
from collections import Counter
from typing import List

from .schemas import AnalysisResult
from .analyzer_hf import available as hf_available, predict_emotions as hf_predict

# -----------------------------
# 감정 키워드 사전 (영문 코드 5개로 통일)
# -----------------------------
# happy, sad, angry, shy, empty 중에서만 나오도록 매핑
EMO_CODE_LEX = {
    "happy": [
        "행복", "기쁨", "기분 좋", "뿌듯", "즐겁", "신나", "신남", "설렘", "재밌", "좋았",
    ],
    "sad": [
        "슬프", "우울", "눈물", "상실", "허무", "외롭", "서운", "속상",
    ],
    "angry": [
        "화나", "짜증", "열받", "분노", "억울", "빡치", "화가", "성나",
    ],
    "shy": [
        "부끄", "쑥스", "민망", "머쓱",
    ],
    "empty": [
        "무기력", "멍하", "공허", "그냥그냥", "심심", "피곤", "지침", "번아웃", "과로",
    ],
}

# 긍정/부정 판단용 단어들 (valence 용)
POS_WORDS = ["좋았", "만족", "성공", "칭찬", "뿌듯", "행복", "기쁨", "즐겁", "설렘"]
NEG_WORDS = ["힘들", "실수", "후회", "불안", "우울", "짜증", "화나", "좌절", "실망", "억울"]


# -----------------------------
# 감정 감지 → happy/sad/angry/shy/empty 코드 리스트로 반환
# -----------------------------
def _detect_emotions(text: str) -> List[str]:
    """
    텍스트에서 감정 키워드를 찾아서
    happy/sad/angry/shy/empty 중 최대 3개까지 반환.
    """
    found: List[str] = []
    for code, kws in EMO_CODE_LEX.items():
        if any(k in text for k in kws):
            found.append(code)

    # 발견된 감정이 너무 많으면 앞에서부터 3개만
    return found[:3]


# -----------------------------
# valence 판단 (positive / negative / neutral)
# -----------------------------
def _judge_valence(text: str) -> str:
    """
    대략적인 분위기를 positive / negative / neutral 로만 나눔.
    감정 코드(emotions)는 따로 happy/sad/... 로 리턴.
    """
    pos = sum(text.count(w) for w in POS_WORDS)
    neg = sum(text.count(w) for w in NEG_WORDS)

    # 감정 코드도 참고해서 보정
    emos = _detect_emotions(text)

    # happy가 있으면 positive 쪽으로
    if "happy" in emos:
        return "positive"

    # sad/angry가 있으면 negative 쪽으로
    if any(e in emos for e in ["sad", "angry"]):
        return "negative"

    # 키워드 기반 기본 로직
    if pos == 0 and neg == 0:
        # 진짜 아무 단서도 없으면 neutral
        return "neutral"

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
    """
    diary-replier에서 사용하는 분석 함수.

    - valence : "positive" / "negative" / "neutral"
    - emotions: ["happy"] / ["sad"] / ... 중 1개 이상
    - summary : 간단 요약
    """
    valence = _judge_valence(text)
    detected = _detect_emotions(text)
    summary = _make_summary(text)

    # 🔥 1) neutral이면 무조건 ["empty"]
    if valence == "neutral":
        emotions = ["empty"]
    else:
        # 2) positive / negative일 때는 감정 키워드 우선 사용
        if detected:
            emotions = detected
        else:
            # 3) 키워드가 하나도 없으면 valence 기준으로 폴백
            if valence == "positive":
                emotions = ["happy"]
            elif valence == "negative":
                emotions = ["sad"]
            else:
                emotions = ["empty"]

    # 4) 방어 코드: 혹시 허용 안 되는 값이 섞여 있으면 정리
    allowed = {"happy", "sad", "angry", "shy", "empty"}
    emotions = [e for e in emotions if e in allowed]
    if not emotions:
        emotions = ["empty"]

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
