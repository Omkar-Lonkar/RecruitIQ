from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


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
