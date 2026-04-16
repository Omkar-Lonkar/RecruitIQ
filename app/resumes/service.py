import json
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from uuid import UUID

from app.resumes.models import Resume, ResumeParsedData
from app.candidates.models import Candidate
from app.utils.file_storage import save_resume_file
from app.utils.pdf_parser import extract_text_from_pdf
from app.core.gemini_client import parse_resume_with_gemini


def basic_resume_parser(text: str):
    lines = text.split("\n")

    skills = set()
    education = []
    projects = []
    experience = []

    keywords = [
        "python", "java", "c++", "sql", "machine learning",
        "deep learning", "ai", "data analysis", "opencv"
    ]

    for line in lines:
        clean = line.strip()
        lower = clean.lower()

        for skill in keywords:
            if skill in lower:
                skills.add(skill.title())

        if any(x in lower for x in ["b.tech", "degree", "college", "university"]):
            education.append({
                "degree": clean,
                "institution": "",
                "start_year": None,
                "end_year": None
            })

        if any(x in lower for x in ["project", "developed", "system", "built"]):
            projects.append({
                "title": clean,
                "description": clean,
                "skills": []
            })

        if any(x in lower for x in ["experience", "intern", "worked"]):
            experience.append({
                "role": clean,
                "company": "",
                "duration": ""
            })

    return {
        "skills": list(skills),
        "education": education,
        "work_experience": experience,
        "projects": projects,
        "certifications": []
    }


def upload_resume(db: Session, recruiter, candidate_id: UUID, file: UploadFile):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.company_id == recruiter.company_id,
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    existing = db.query(Resume).filter(
        Resume.candidate_id == candidate_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Resume already exists")

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

    candidate = db.query(Candidate).filter(
        Candidate.id == resume.candidate_id,
        Candidate.company_id == recruiter.company_id,
    ).first()

    if not candidate:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # -------- TEXT EXTRACTION --------
    resume_text = extract_text_from_pdf(resume.file_path)

    # FIX: remove null chars
    resume_text = resume_text.replace("\x00", "")
    resume_text = re.sub(r"\x00", "", resume_text)
    # -------- CLEAN (KEEP STRUCTURE) --------
    resume_text = re.sub(r"[ \t]+", " ", resume_text)
    resume_text = re.sub(r"\n+", "\n", resume_text)

    # -------- SECTION SPLIT --------
    sections = {
        "education": "",
        "projects": "",
        "experience": "",
        "skills": ""
    }

    current_section = None

    for line in resume_text.split("\n"):
        lower = line.lower()

        if "education" in lower:
            current_section = "education"
        elif "project" in lower:
            current_section = "projects"
        elif "experience" in lower:
            current_section = "experience"
        elif "skill" in lower:
            current_section = "skills"

        if current_section:
            sections[current_section] += line + "\n"

    # -------- CLEAN PROJECT SECTION --------
    sections["projects"] = re.sub(
        r"KEY EXPERTISE.*",
        "",
        sections["projects"],
        flags=re.IGNORECASE
    )

    # -------- CREATE INPUT FOR GEMINI --------
    clean_input = "\n\n".join([
        f"{key.upper()}:\n{value}"
        for key, value in sections.items()
    ])

    print("INPUT TO GEMINI:\n", clean_input[:1000])

    # -------- GEMINI CALL --------
    try:
        gemini_output = parse_resume_with_gemini(clean_input)
        print("GEMINI OUTPUT:\n", gemini_output)

        if not gemini_output:
            raise Exception("Empty Gemini output")

        try:
            structured_data = json.loads(gemini_output)
        except:
            match = re.search(r"\{.*\}", gemini_output, re.DOTALL)
            if match:
                structured_data = json.loads(match.group())
            else:
                raise Exception("Invalid JSON")

    except Exception as e:
        print("Gemini failed, using fallback:", e)
        structured_data = basic_resume_parser(resume_text)

    # -------- 🔥 FIX DATA TYPES (IMPORTANT) --------
    education_fixed = [
        {
            "degree": edu,
            "institution": "",
            "start_year": None,
            "end_year": None
        }
        if isinstance(edu, str) else edu
        for edu in structured_data.get("education", [])
    ]

    work_exp_fixed = [
        {
            "role": exp,
            "company": "",
            "duration": ""
        }
        if isinstance(exp, str) else exp
        for exp in structured_data.get("work_experience", [])
    ]

    # -------- SAVE --------
    parsed = ResumeParsedData(
        resume_id=resume.id,
        skills=structured_data.get("skills", []),
        education=education_fixed,
        work_experience=work_exp_fixed,
        projects=structured_data.get("projects", []),
        certifications=structured_data.get("certifications", []),
        raw_text=resume_text,
        parser_version="v3",
    )

    db.add(parsed)

    candidate.status = "SCREENING"

    db.commit()

    return parsed