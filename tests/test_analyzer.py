from diary_replier.analyzer import analyze_diary

try:
    from .analyzer_hf import available as hf_available, predict_emotions as hf_predict
except Exception:
    hf_available = lambda: False
    hf_predict = lambda text, topk=None: []

# _detect_emotions 함수 교체
def _detect_emotions(text: str) -> List[str]:
    # HF 모델 있으면 우선 사용
    if hf_available():
        preds = hf_predict(text, topk=3)
        if preds:
            return preds
    # 없으면 기존 규칙 기반
    found = []
    for emo, kws in EMO_LEX.items():
        if any(k in text for k in kws):
            found.append(emo)
    return found[:3] if found else []

def test_analyze_diary_basic(sample_text):
    res = analyze_diary(sample_text)
    # 최소 필드 보장
    assert isinstance(res, dict)
    assert res.get("valence") in {"positive", "neutral", "negative"}
    assert isinstance(res.get("emotions"), list)
    assert isinstance(res.get("keywords"), list)
    assert isinstance(res.get("summary"), str)
