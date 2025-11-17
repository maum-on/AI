import re
from typing import Any, List
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from src.parsers.base import BaseChatParser
from src.schemas.chat import ChatThread, ChatMessage

KST = ZoneInfo("Asia/Seoul")

LINE_RE = re.compile(
    r"(?P<y>\d{4})\.\s*(?P<m>\d{1,2})\.\s*(?P<d>\d{1,2})\.\s*(?P<ampm>오전|오후)\s*(?P<h>\d{1,2}):(?P<min>\d{2}),\s*(?P<name>[^:]+)\s*:\s*(?P<text>.*)"
)

class KakaoTalkParser(BaseChatParser):
    def can_handle(self, payload: Any) -> bool:
        if isinstance(payload, str):
            return bool(LINE_RE.search(payload))
        if isinstance(payload, dict) and "messages" in payload:
            return True
        return False

    def parse(self, payload: Any, me_hint: str | None = None) -> ChatThread:
        if isinstance(payload, str):
            return self._parse_txt(payload, me_hint)
        return self._parse_json(payload, me_hint)

    def _parse_txt(self, text: str, me_hint: str | None) -> ChatThread:
        msgs, participants = [], set()

        for line in text.splitlines():
            m = LINE_RE.match(line)
            if not m:
                continue

            y, mo, d = int(m["y"]), int(m["m"]), int(m["d"])
            h = int(m["h"])
            if m["ampm"] == "오후" and h != 12: h += 12
            if m["ampm"] == "오전" and h == 12: h = 0

            ts_local = datetime(y, mo, d, h, int(m["min"]), tzinfo=KST)
            ts_utc = ts_local.astimezone(timezone.utc)

            name = m["name"]
            participants.add(name)

            msgs.append(ChatMessage(sender=name, text=m["text"], ts_utc=ts_utc))

        return ChatThread(
            platform="kakaotalk",
            thread_id="",
            title=None,
            participants=list(participants),
            me=me_hint,
            messages=msgs,
        )

    def _parse_json(self, payload: dict, me_hint: str | None) -> ChatThread:
        msgs, participants = [], set()

        for m in payload["messages"]:
            sender = m.get("sender") or m.get("name")
            participants.add(sender)

            ts = m.get("timestamp") or m.get("sendAt")
            ts_utc = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)

            msgs.append(ChatMessage(
                sender=sender, text=m.get("text"), ts_utc=ts_utc
            ))

        return ChatThread(
            platform="kakaotalk",
            thread_id=str(payload.get("chatId", "")),
            title=payload.get("title"),
            participants=list(participants),
            me=me_hint,
            messages=msgs
        )
