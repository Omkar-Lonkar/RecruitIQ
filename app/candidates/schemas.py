from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class CandidateCreateRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    current_role: str | None = None
    experience_years: float | None = None
    location: str | None = None
    source: str


class CandidateResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: str | None
    current_role: str | None
    experience_years: float | None
    location: str | None
    status: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeData(BaseModel):
    skills: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class InterviewReport(BaseModel):
    overall_score: Optional[int]
    strengths: Optional[str]
    weaknesses: Optional[str]
    recommendation: Optional[str]

    class Config:
        from_attributes = True


class CandidateDetailResponse(CandidateResponse):
    resume: Optional[ResumeData] = None
    interview_report: Optional[InterviewReport] = None