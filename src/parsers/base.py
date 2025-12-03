# src/parsers/base.py

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class ChatPlatform(str, Enum):
    GENERIC = "generic"
    UNKNOWN = "unknown"


def detect_platform(data: Dict[str, Any]) -> ChatPlatform:
    """
    JSON 구조 보고 '제법 그럴싸한 채팅 포맷'이면 GENERIC 으로 태운다.
    title / participants / messages[...] 형식이면 거의 다 들어오게.
    """
    msgs = data.get("messages")
    if isinstance(msgs, list) and len(msgs) > 0:
        m0 = msgs[0]
        has_sender = any(k in m0 for k in ["sender_name", "sender", "author", "from"])
        has_text = any(k in m0 for k in ["content", "message", "text"])
        has_ts = any(k in m0 for k in ["timestamp_ms", "timestamp", "created_at"])

        if has_sender and has_text and has_ts:
            return ChatPlatform.GENERIC

    return ChatPlatform.UNKNOWN


def _pick_first(d: Dict[str, Any], keys) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _normalize_timestamp(raw_ts: Any) -> Optional[str]:
    """
    int(ms) / int(sec) / ISO string → ISO string
    """
    if raw_ts is None:
        return None

    if isinstance(raw_ts, (int, float)):
        # 10^11 이상이면 ms, 아니면 seconds 로 취급
        if raw_ts > 10 ** 11:
            ts_sec = raw_ts / 1000.0
        else:
            ts_sec = raw_ts
        dt = datetime.fromtimestamp(ts_sec, tz=timezone.utc)
        return dt.isoformat()

    if isinstance(raw_ts, str):
        # 이미 iso 형식일 수도 있고, 아닐 수도 있지만
        # 파싱 실패해도 그냥 raw string 리턴
        try:
            return datetime.fromisoformat(raw_ts).isoformat()
        except Exception:
            return raw_ts

    return None


def normalize_generic_chat(
    data: Dict[str, Any],
    me_hint: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    이런 식의 JSON을 전부 공통 포맷으로 변환:

    {
      "title": "...",
      "participants": [{ "name": "..." }, ...],
      "messages": [
        {
          "sender_name": "...",
          "timestamp_ms": 1762747380000,
          "content": "...",
          ...
        },
        ...
      ]
    }

    → 반환:

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
    me_name = (me_hint or "").strip()
    messages_out: List[Dict[str, Any]] = []

    for msg in data.get("messages", []):
        content = _pick_first(msg, ["content", "message", "text"])
        if not content:
            # 파일/이미지/시스템 메시지 등은 스킵
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
