# api/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class DiaryOptions(BaseModel):
    tone: str = Field(default="friend")     # "friend" | "mentor"
    length: str = Field(default="both")     # "short" | "normal" | "both"
    long_mode: str = Field(default="full")  # "off" | "full"

class DiaryRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=8000)
    user_id: Optional[str] = None
    date: Optional[str] = None
    meta: Dict = Field(default_factory=dict)
    options: DiaryOptions = Field(default_factory=DiaryOptions)

class AnalysisResult(BaseModel):
    valence: Optional[str] = None
    emotions: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    summary: str = ""

class DiaryReplyResponse(BaseModel):
    reply_short: Optional[str] = None
    reply_normal: Optional[str] = None
    safety_flag: bool = False
    flags: Dict = Field(default_factory=dict)
    analysis: AnalysisResult = Field(default_factory=AnalysisResult)
