from app.interviews.models import Interview, InterviewMessage
from app.interviews.question_engine import generate_first_question
from app.candidates.models import Candidate
from app.resumes.models import Resume
from app.resumes.models import ResumeParsedData

from uuid import uuid4


def start_interview(db, recruiter, candidate_id, job_role, experience_level):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.company_id == recruiter.company_id
    ).first()

    if not candidate:
        raise Exception("Candidate not found")

    # Step 1: get candidate resume
    resume = db.query(Resume).filter(
        Resume.candidate_id == candidate.id
    ).order_by(Resume.uploaded_at.desc()).first()

    skills = []

# Step 2: get parsed resume data
    if resume:
        parsed_resume = db.query(ResumeParsedData).filter(
            ResumeParsedData.resume_id == resume.id
        ).first()

        if parsed_resume and parsed_resume.skills:
            skills = parsed_resume.skills

    skills = parsed_resume.skills if parsed_resume else []

    interview = Interview(
        candidate_id=candidate.id,
        company_id=recruiter.company_id
    )

    db.add(interview)
    db.flush()

    question = generate_first_question(
        job_role,
        experience_level,
        skills
    )

    message = InterviewMessage(
        interview_id=interview.id,
        sender="AI",
        message_text=question,
        question_number=1
    )

    db.add(message)

    candidate.status = "INTERVIEW_STARTED"

    db.commit()

    return interview.id, question