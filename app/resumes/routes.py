from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.auth.dependencies import get_current_recruiter
from app.resumes.schemas import ResumeParsedResponse, ResumeResponse
from app.resumes.service import upload_resume, parse_resume

router = APIRouter(prefix="/candidates", tags=["resumes"])


@router.post("/{candidate_id}/resume", response_model=ResumeResponse)
def upload_resume_endpoint(
    candidate_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return upload_resume(db, recruiter, candidate_id, file)


@router.post("/resumes/{resume_id}/parse",
             response_model=ResumeParsedResponse)
def parse_resume_endpoint(
    resume_id: UUID,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return parse_resume(db, recruiter, resume_id)
