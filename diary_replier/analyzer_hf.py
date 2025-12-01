import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

_EMO_MODEL = os.getenv("EMO_MODEL")  # 빈 값이면 사용 안 함
_EMO_TOPK = int(os.getenv("EMO_TOPK", "2"))

# 라벨 매핑은 모델에 따라 다름. 일단 보편 label 이름만 정규화 예시 제공.
_DEFAULT_MAP = {
    "joy": "기쁨", "happy": "기쁨", "happiness": "기쁨",
    "sad": "슬픔", "sadness": "슬픔",
    "angry": "분노", "anger": "분노",
    "fear": "불안", "anxiety": "불안",
    "tired": "피곤", "fatigue": "피곤",
    "empty": "중립", "others": "중립"
}

_pipe = None
_err = None

def _lazy_load():
    global _pipe, _err
    if _pipe is not None or _err is not None:
        return
    if not _EMO_MODEL:
        _err = "no model specified"
        return
    try:
        from transformers import pipeline
        _pipe = pipeline("text-classification", model=_EMO_MODEL, tokenizer=_EMO_MODEL, top_k=None)
    except Exception as e:
        _err = str(e)

def available() -> bool:
    _lazy_load()
    return _pipe is not None

def predict_emotions(text: str, topk: int | None = None) -> List[str]:
    _lazy_load()
    if _pipe is None:
        return []  # 폴백은 기존 analyzer.py가 담당
    k = topk or _EMO_TOPK
    out = _pipe(text)
    # transformers >=4.36: list[dict] or list[list[dict]] 형태 → 통일
    if isinstance(out, list) and out and isinstance(out[0], dict):
        candidates = out
    elif isinstance(out, list) and out and isinstance(out[0], list):
        candidates = out[0]
    else:
        candidates = []

    # 상위 k개 label 정규화
    labels = []
    for item in sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:k]:
        lab = str(item.get("label", "")).lower()
        labels.append(_DEFAULT_MAP.get(lab, lab))
    # 중복 제거
    uniq = []
    for x in labels:
        if x not in uniq:
            uniq.append(x)
    return uniq[:k]
