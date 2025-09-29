# diary_replier/guard.py
import re

# ── 1) 간단 정규화: 공백/마침표 변형 흡수
def _normalize(text: str) -> str:
    t = text.strip()
    # 연속 공백을 1칸으로
    t = re.sub(r"\s+", " ", t)
    return t

# ── 2) 위기/자해/자살 관련 패턴 확장
CRISIS_PATTERNS = [
    r"죽고\s*싶[다어요]?",                 # 죽고 싶다/싶어요
    r"자살",                              # 자살
    r"목숨(?:을)?\s*끊",                   # 목숨을 끊…
    r"스스로\s*(?:를)?\s*끝내",            # 스스로 끝내…
    r"해치고\s*싶[다어요]?",                # 해치고 싶다
    r"끝내(?:버리)?고\s*싶[다어요]?",       # 끝내고/끝내버리고 싶다
    r"삶(?:을)?\s*끝내",                    # 삶을 끝내…
    r"살기\s*싫[다어요]?",                  # 살기 싫다
    r"없어지고\s*싶[다어요]?",              # 없어지고 싶다
    r"극단적(?:인)?\s*선택",                # 극단적(인) 선택
    r"희망이\s*없",                         # 희망이 없…
]

PII_PATTERNS = [
    r"\b\d{3}-\d{4}-\d{4}\b",              # 한국 전화번호
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"  # 이메일
]

def mask_pii(text: str) -> tuple[str, bool]:
    flagged = False
    for pat in PII_PATTERNS:
        if re.search(pat, text):
            flagged = True
            text = re.sub(pat, "[민감정보]", text)
    return text, flagged

def detect_crisis(text: str) -> bool:
    t = _normalize(text)
    return any(re.search(pat, t) for pat in CRISIS_PATTERNS)
