from pydantic import BaseModel
from uuid import UUID


class InterviewStartRequest(BaseModel):
    candidate_id: UUID
    job_role: str
    experience_level: str


class InterviewStartResponse(BaseModel):
    interview_id: UUID
    first_question: str