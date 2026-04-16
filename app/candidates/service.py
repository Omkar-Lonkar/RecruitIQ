from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.candidates.models import Candidate
from app.resumes.models import Resume, ResumeParsedData
from app.interviews.models import Interview, InterviewReport
from uuid import UUID

from app.candidates.models import Candidate


def create_candidate(db: Session, recruiter, data):
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


def get_candidate(db, candidate_id, recruiter):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.company_id == recruiter.company_id   # ✅ CORRECT
    ).first()       

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # ✅ Get latest resume
    resume = db.query(Resume).filter(
        Resume.candidate_id == candidate.id
    ).order_by(Resume.uploaded_at.desc()).first()

    parsed_data = None

    if resume:
        parsed_data = db.query(ResumeParsedData).filter(
            ResumeParsedData.resume_id == resume.id
        ).first()

    # ✅ Get latest interview report
    report = db.query(InterviewReport)\
        .join(Interview, Interview.id == InterviewReport.interview_id)\
        .filter(Interview.candidate_id == candidate.id)\
        .order_by(Interview.created_at.desc())\
        .first()

    return {
        **candidate.__dict__,
        "resume": parsed_data.__dict__ if parsed_data else None,
        "interview_report": report.__dict__ if report else None
    }