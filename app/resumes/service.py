import json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.resumes.models import Resume, ResumeParsedData
from app.candidates.models import Candidate
from app.utils.file_storage import save_resume_file
from app.utils.pdf_parser import extract_text_from_pdf
from app.core.gemini_client import parse_resume_with_gemini
import re


def upload_resume(db: Session, recruiter, candidate_id: UUID, file):
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

    file_path, stored_filename = save_resume_file(
        recruiter.company_id,
        candidate_id,
        file,
    )

    resume = Resume(
        candidate_id=candidate.id,
        file_name=stored_filename,
        file_type=file.content_type,
        file_path=file_path,
        uploaded_via="manual",
    )

    db.add(resume)

    if candidate.status == "NEW":
        candidate.status = "APPLIED"

    db.commit()
    db.refresh(resume)

    return resume


def parse_resume(db: Session, recruiter, resume_id: UUID):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == resume.candidate_id,
            Candidate.company_id == recruiter.company_id,
        )
        .first()
    )

    if not candidate:
        raise HTTPException(status_code=403, detail="Unauthorized")

    resume_text = extract_text_from_pdf(resume.file_path)

    gemini_output = parse_resume_with_gemini(resume_text)

   

    try:
        # Extract JSON block using regex
        json_match = re.search(r"\{.*\}", gemini_output, re.DOTALL)

        if not json_match:
            raise ValueError("No JSON found")

        json_str = json_match.group()
        structured_data = json.loads(json_str)

    except Exception as e:
        print("Gemini Raw Output:\n", gemini_output)
        raise HTTPException(status_code=500, detail="Failed to parse Gemini output")

    parsed_record = ResumeParsedData(
        resume_id=resume.id,
        skills=structured_data.get("skills"),
        education=structured_data.get("education"),
        work_experience=structured_data.get("work_experience"),
        projects=structured_data.get("projects"),
        certifications=structured_data.get("certifications"),
        raw_text=resume_text,
        parser_version="v1",
    )

    db.add(parsed_record)

    candidate.status = "SCREENING"

    db.commit()

    return parsed_record
