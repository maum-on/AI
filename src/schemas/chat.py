# shemas/chat.py

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


# ─────────────────────────────
# 여기부터 chat-to-diary 결과용
# ─────────────────────────────

EmotionCode = Literal["happy", "sad", "angry", "shy", "empty"]

class ChatToDiaryAnalysis(BaseModel):
    """chat-to-diary에서 쓰는 분석 결과"""
    emotion: EmotionCode          # 대표 감정 1개
    keywords: List[str] = []      # 요약용 키워드들

class ChatToDiaryResult(BaseModel):
    """chat-to-diary 최종 응답 구조"""
    diary_text: str               # LLM이 만든 일기 문장
    analysis: ChatToDiaryAnalysis
