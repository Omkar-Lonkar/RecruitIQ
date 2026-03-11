from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_recruiter

from app.interviews.schemas import InterviewStartRequest, InterviewStartResponse
from app.interviews.service import start_interview

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/start", response_model=InterviewStartResponse)
def start_interview_endpoint(
    payload: InterviewStartRequest,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter)
):

    interview_id, question = start_interview(
        db,
        recruiter,
        payload.candidate_id,
        payload.job_role,
        payload.experience_level
    )

    return {
        "interview_id": interview_id,
        "first_question": question
    }