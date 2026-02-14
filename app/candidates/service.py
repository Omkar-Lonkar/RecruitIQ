from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.candidates.models import Candidate


def create_candidate(db: Session, recruiter, data):
    # Enforce uniqueness per company
    existing = (
        db.query(Candidate)
        .filter(
            Candidate.company_id == recruiter.company_id,
            Candidate.email == data.email,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Candidate with this email already exists in your company",
        )

    candidate = Candidate(
        company_id=recruiter.company_id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        current_role=data.current_role,
        experience_years=data.experience_years,
        location=data.location,
        status="NEW",
        source=data.source,
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


def list_candidates(db: Session, recruiter):
    return (
        db.query(Candidate)
        .filter(Candidate.company_id == recruiter.company_id)
        .all()
    )


def get_candidate(db: Session, recruiter, candidate_id: UUID):
    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
            Candidate.company_id == recruiter.company_id,
        )
        .first()
    )

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return candidate
