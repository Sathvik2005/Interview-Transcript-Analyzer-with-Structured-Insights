from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    transcript: str = Field(min_length=1)
    provider: Optional[Literal["gemini", "groq", "openai"]] = None
    model: Optional[str] = None


class Profile(BaseModel):
    role: str
    level: str
    justification: str


class AnalysisResponse(BaseModel):
    topics_covered: List[str]
    profile: Profile
    candidate_summary: str

