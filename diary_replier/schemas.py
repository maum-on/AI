from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class DiaryInput(BaseModel):
    text: str = Field(..., min_length=2, max_length=8000)
    user_id: Optional[str] = None
    date: Optional[str] = None
    meta: Dict = Field(default_factory=dict)

class AnalysisResult(BaseModel):
    valence: str
    emotions: List[str] = []
    keywords: List[str] = []
    summary: str = ""

class DiaryReplyOutput(BaseModel):
    reply_short: str
    reply_normal: str
    safety_flag: bool
    flags: Dict
    analysis: AnalysisResult
