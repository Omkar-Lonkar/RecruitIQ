from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.auth.dependencies import get_current_recruiter
from app.candidates.schemas import (
    CandidateCreateRequest,
    CandidateResponse,
)
from app.candidates.service import (
    create_candidate,
    list_candidates,
    get_candidate,
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateResponse)
def create_candidate_endpoint(
    payload: CandidateCreateRequest,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return create_candidate(db, recruiter, payload)


@router.get("/", response_model=List[CandidateResponse])
def list_candidates_endpoint(
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return list_candidates(db, recruiter)


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate_endpoint(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    recruiter=Depends(get_current_recruiter),
):
    return get_candidate(db, recruiter, candidate_id)
