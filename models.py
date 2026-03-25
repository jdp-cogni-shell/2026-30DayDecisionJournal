from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DecisionCreate(BaseModel):
    title: str
    description: str = ""
    confidence_initial: int
    evidence_known: str = ""
    evidence_unknown: str = ""
    evidence_would_change: str = ""
    premortem_reason_1: str = ""
    premortem_reason_2: str = ""
    premortem_reason_3: str = ""
    tags: list[str] = []


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    confidence_initial: Optional[int] = None
    evidence_known: Optional[str] = None
    evidence_unknown: Optional[str] = None
    evidence_would_change: Optional[str] = None
    premortem_reason_1: Optional[str] = None
    premortem_reason_2: Optional[str] = None
    premortem_reason_3: Optional[str] = None
    tags: Optional[list[str]] = None


class DecisionRead(BaseModel):
    id: str
    title: str
    description: str
    status: str
    confidence_initial: int
    evidence_known: str
    evidence_unknown: str
    evidence_would_change: str
    premortem_reason_1: str
    premortem_reason_2: str
    premortem_reason_3: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
