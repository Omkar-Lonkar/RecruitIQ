from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ResumeResponse(BaseModel):
    id: UUID
    file_name: str
    file_type: str
    uploaded_via: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ResumeParsedResponse(BaseModel):
    resume_id: UUID
    skills: list | None
    education: list | None
    work_experience: list | None
    projects: list | None
    certifications: list | None

    class Config:
        from_attributes = True