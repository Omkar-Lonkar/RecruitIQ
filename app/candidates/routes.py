from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.candidates.models import Candidate
from app.interviews.models import Interview, InterviewReport

from app.core.database import get_db
from app.auth.dependencies import get_current_recruiter

from app.candidates.schemas import (
    CandidateCreateRequest,
    CandidateDetailResponse,
    CandidateResponse,
)

from app.candidates.service import (
    create_candidate,
    list_candidates,
    get_candidate,
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


# ✅ Create Candidate
@router.post("/", response_model=CandidateResponse)
def create_candidate_endpoint(
    payload: CandidateCreateRequest,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return create_candidate(db, recruiter, payload)


# ✅ List Candidates
@router.get("/", response_model=List[CandidateResponse])
def list_candidates_endpoint(
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return list_candidates(db, recruiter)


# ✅ Get Candidate (Detailed)
@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_candidate_endpoint(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return get_candidate(db, candidate_id, recruiter)


# ✅ Get Latest Interview Report
@router.get("/{candidate_id}/report")
def get_interview_report(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    report = (
        db.query(InterviewReport)
        .join(Interview, Interview.id == InterviewReport.interview_id)
        .filter(
            Interview.candidate_id == candidate_id,
            Interview.company_id == recruiter.company_id  # 🔥 IMPORTANT SECURITY FIX
        )
        .order_by(Interview.created_at.desc())
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not generated")

    return report