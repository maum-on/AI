from typing import Any, List
from datetime import datetime, timezone
from src.parsers.base import BaseChatParser
from src.schemas.chat import ChatThread, ChatMessage

class InstagramParser(BaseChatParser):
    def can_handle(self, payload: Any) -> bool:
        return (
            isinstance(payload, dict)
            and "participants" in payload
            and "messages" in payload
            and any("timestamp_ms" in m for m in payload.get("messages", []))
        )

    def parse(self, payload: dict, me_hint: str | None = None) -> ChatThread:
        participants = [p["name"] for p in payload.get("participants", [])]
        me = me_hint if me_hint in participants else participants[-1]

        messages: List[ChatMessage] = []
        for m in payload.get("messages", []):
            ts_utc = datetime.fromtimestamp(m["timestamp_ms"] / 1000, tz=timezone.utc)
            messages.append(ChatMessage(
                sender=m["sender_name"],
                text=m.get("content"),
                ts_utc=ts_utc,
            ))

        return ChatThread(
            platform="instagram",
            thread_id=payload.get("thread_path", ""),
            title=payload.get("title"),
            participants=participants,
            me=me,
            messages=sorted(messages, key=lambda x: x.ts_utc),
        )
