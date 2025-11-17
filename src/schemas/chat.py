from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel

Platform = Literal["instagram", "kakaotalk"]

class ChatMessage(BaseModel):
    sender: str
    text: Optional[str] = None
    ts_utc: datetime
    attachments: Optional[List[str]] = None
    meta: Dict[str, Any] = {}

class ChatThread(BaseModel):
    platform: Platform
    thread_id: str
    title: Optional[str]
    participants: List[str]
    me: Optional[str]
    messages: List[ChatMessage]
