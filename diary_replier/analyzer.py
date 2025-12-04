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
        # 행복 / 기쁨 / 설렘 / 신남
        "행복", "행복하", "행복했",
        "기쁨", "기뻤", "기분 좋", "좋은 기분",
        "즐겁", "즐거웠",
        "재밌", "재미있",
        "신나", "신났", "신나는",
        "설렘", "설레", "설렌", "설레는", "설레서",
        "두근두근", "두근거",
        "뿌듯", "만족스럽", "만족했",
        "감사하", "고맙게", "고마웠",
    ],
    "sad": [
        # 슬픔 / 우울 / 상실 / 외로움
        "슬프", "슬펐",
        "우울", "우울하", "우울했",
        "울적", "우중충",
        "눈물", "눈물이 나", "눈물 났", "울컥",
        "상실", "상실감",
        "허무", "허무하",
        "외롭", "외로웠", "쓸쓸",
        "서운", "속상",
        "괴로웠", "마음이 아프", "멘붕",
        "실망했", "좌절했",
    ],
    "angry": [
        # 화남 / 짜증 / 분노 / 억울
        "화나", "화났", "화가 나", "화가나",
        "짜증", "짜증나", "짜증났",
        "열받", "열 받",
        "분노", "성질나", "빡치",
        "어이없", "기분 나빴",
        "억울", "억울했",
        "부당하", "짜증스러",
    ],
    "shy": [
        # 부끄러움 / 어색함
        "부끄", "부끄러웠", "부끄러워",
        "쑥스", "쑥스럽",
        "민망", "머쓱",
        "어색", "낯가리", "낯가렸",
    ],
    "empty": [
        # 무기력 / 피곤 / 공허 / 그냥저냥
        "무기력", "무기력하",
        "멍하", "멍했",
        "공허", "공허하",
        "그냥그냥", "그냥 그랬", "그냥저냥",
        "심심",
        "피곤", "피곤하",
        "지침", "지쳤",
        "번아웃", "과로",
        "현타",
        "의욕이 없", "하기 싫", "귀찮",
        "흥미가 없", "재미가 없",
        "무덤덤", "감흥이 없",
    ],
}

# 긍정/부정 판단용 단어들 (valence 용)
POS_WORDS = [
    "좋았", "좋은 하루", "만족", "성공", "칭찬",
    "뿌듯", "행복", "행복했", "기쁨", "즐겁", "재밌", "재미있",
    "신났", "신나", "설렘", "설레", "설렌", "고마웠", "감사했",
]

NEG_WORDS = [
    "힘들", "힘들었",
    "실수", "후회",
    "불안", "불안했",
    "우울", "우울했",
    "짜증", "짜증나", "짜증났",
    "화나", "화났", "열받",
    "좌절", "좌절했",
    "실망", "실망했",
    "억울", "억울했",
    "피곤", "지쳤", "무기력", "현타",
    "슬펐", "외롭", "공허",
]


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
