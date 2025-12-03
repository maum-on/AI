# src/parsers/base.py

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def _pick_first(d: Dict[str, Any], keys) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _normalize_timestamp(raw_ts: Any) -> Optional[str]:
    """
    int(ms) / int(sec) / ISO string -> ISO string
    """
    if raw_ts is None:
        return None

    # 숫자면 epoch 기준 시각
    if isinstance(raw_ts, (int, float)):
        # 10^11 이상이면 ms, 아니면 초
        if raw_ts > 10 ** 11:
            ts_sec = raw_ts / 1000.0
        else:
            ts_sec = raw_ts
        dt = datetime.fromtimestamp(ts_sec, tz=timezone.utc)
        return dt.isoformat()

    # 문자열이면 ISO 파싱 시도, 안 되면 그냥 raw 반환
    if isinstance(raw_ts, str):
        try:
            return datetime.fromisoformat(raw_ts).isoformat()
        except Exception:
            return raw_ts

    return None


def normalize_generic_chat(
    data: Any,
    me_hint: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    인스타/DM처럼 생긴 JSON을 공통 포맷으로 정규화한다.

    지원하는 최상위 형태:
      1) {..., "messages": [...]}
      2) [ { "messages": [...] }, ... ]  (리스트면 첫 번째 요소 사용)

    각 message 예시:
      {
        "sender_name": "가톨릭대 23 캡스톤 김가은",
        "timestamp_ms": 1762747380000,
        "content": "넵 괜찮습니다!",
        ...
      }

    반환 형식:
      [
        {
          "role": "me" | "other",
          "sender_name": "...",
          "content": "...",
          "timestamp": "ISO-STRING",
        },
        ...
      ]
    """
    # 만약 최상위가 리스트라면, 첫 번째 요소를 쓰자 (인스타 export가 이런 경우 있음)
    if isinstance(data, list):
        if not data:
            return []
        root = data[0]
    elif isinstance(data, dict):
        root = data
    else:
        # 전혀 예상치 못한 타입이면 그냥 빈 리스트
        return []

    me_name = (me_hint or "").strip()
    messages_out: List[Dict[str, Any]] = []

    raw_messages = root.get("messages")
    if not isinstance(raw_messages, list):
        return []

    for msg in raw_messages:
        if not isinstance(msg, dict):
            continue

        # 텍스트 내용
        content = _pick_first(msg, ["content", "message", "text"])
        if not content:
            # 시스템 메시지/사진만 있는 메시지는 스킵
            continue

        sender = _pick_first(msg, ["sender_name", "sender", "author", "from"]) or ""
        raw_ts = _pick_first(msg, ["timestamp_ms", "timestamp", "created_at"])
        ts_str = _normalize_timestamp(raw_ts)

        role = "me" if me_name and me_name in str(sender) else "other"

        messages_out.append(
            {
                "role": role,
                "sender_name": sender,
                "content": content,
                "timestamp": ts_str,
            }
        )

    return messages_out
