from typing import Dict, Tuple

# 매우 기본적인 금칙 패턴 (필요 시 확장/정교화)
RISK_PATTERNS = {
    "self_harm": ["죽고", "자해", "극단", "그만 살", "생을 마감", "목숨"],
    "violence": ["폭력", "때리", "칼", "해치"],
    "abuse": ["학대", "가해", "괴롭힘", "스토킹"],
}

def safety_scan(text: str) -> Tuple[bool, Dict]:
    flags = {}
    hit_any = False
    low_text = text.lower()
    for k, toks in RISK_PATTERNS.items():
        hit = any(t in low_text for t in toks)
        flags[k] = hit
        hit_any = hit_any or hit
    return hit_any, flags
