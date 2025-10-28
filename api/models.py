import os, json, time
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Boolean, Text
)
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class DiaryLog(Base):
    __tablename__ = "diary_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)

    user_id = Column(String(128), index=True, nullable=True)
    preset_used = Column(String(32), nullable=True)
    mood_hint = Column(String(64), nullable=True)

    text = Column(Text, nullable=False)
    reply_short = Column(Text, nullable=False)
    reply_normal = Column(Text, nullable=False)

    valence = Column(String(16), nullable=True)
    emotions = Column(SQLITE_JSON if DB_URL.startswith("sqlite") else Text, nullable=True)
    keywords = Column(SQLITE_JSON if DB_URL.startswith("sqlite") else Text, nullable=True)
    summary = Column(Text, nullable=True)

    safety_flag = Column(Boolean, default=False)
    flags = Column(SQLITE_JSON if DB_URL.startswith("sqlite") else Text, nullable=True)

    latency_ms = Column(Integer, default=0)

class UserPreset(Base):
    __tablename__ = "user_presets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128), index=True, nullable=False, unique=True)
    preset = Column(String(32), nullable=False, default="warm")
    mood_default = Column(String(64), nullable=True)

Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    return SessionLocal()

# 저장 유틸
def save_diary_log(
    db: Session,
    *,
    user_id: Optional[str],
    preset_used: Optional[str],
    mood_hint: Optional[str],
    text: str,
    reply_short: str,
    reply_normal: str,
    analysis: Dict[str, Any],
    safety_flag: bool,
    flags: Dict[str, Any],
    latency_ms: int
) -> int:
    # sqlite가 아니면 JSON을 문자열로 저장
    def _maybe_dump(v):
        if DB_URL.startswith("sqlite"):
            return v
        return json.dumps(v, ensure_ascii=False)

    row = DiaryLog(
        user_id=user_id,
        preset_used=preset_used,
        mood_hint=mood_hint,
        text=text,
        reply_short=reply_short,
        reply_normal=reply_normal,
        valence=analysis.get("valence"),
        emotions=_maybe_dump(analysis.get("emotions")),
        keywords=_maybe_dump(analysis.get("keywords")),
        summary=analysis.get("summary"),
        safety_flag=safety_flag,
        flags=_maybe_dump(flags),
        latency_ms=latency_ms,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row.id

def get_user_preset(db: Session, user_id: Optional[str]) -> Optional[str]:
    if not user_id:
        return None
    up = db.query(UserPreset).filter(UserPreset.user_id == user_id).first()
    return up.preset if up else None
