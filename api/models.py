# api/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class DiaryOptions(BaseModel):
    tone: Optional[str] = Field(default="friend", description="friend|mentor")
    length: Optional[str] = Field(default="both", description="short|normal|both")

class DiaryRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=8000)
    user_id: Optional[str] = None
    date: Optional[str] = None
    meta: Dict = Field(default_factory=dict)
    options: DiaryOptions = Field(default_factory=DiaryOptions)

class AnalysisResult(BaseModel):
    valence: str
    emotions: List[str] = []
    keywords: List[str] = []
    summary: str = ""

class DiaryReplyResponse(BaseModel):
    reply_short: Optional[str] = None
    reply_normal: Optional[str] = None
    safety_flag: bool
    flags: Dict
    analysis: AnalysisResult

class DiaryOptions(BaseModel):
    tone: Optional[str] = "friend"
    length: Optional[str] = "both"
    long_mode: Optional[str] = "full"   # "off" | "full"
