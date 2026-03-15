from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.auth.dependencies import get_current_recruiter
from app.interviews.schemas import InterviewStartRequest, InterviewStartResponse
from app.interviews.service import start_interview, submit_answer
router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("/{interview_id}/answer")
def submit_answer_endpoint(
    interview_id: UUID,
    payload: dict,
    db: Session = Depends(get_db),
):
    return submit_answer(db, interview_id, payload["answer"])

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