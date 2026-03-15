import re

from app.interviews.models import Interview, InterviewMessage, InterviewReport
from app.interviews.question_engine import generate_first_question
from app.candidates.models import Candidate
from app.resumes.models import Resume
from app.resumes.models import ResumeParsedData
from uuid import uuid4
import json
from app.interviews.models import Interview, InterviewMessage
from app.core.gemini_client import evaluate_answer, generate_interview_report


def submit_answer(db, interview_id, answer):

    interview = db.query(Interview).filter(Interview.id == interview_id).first()

    if not interview:
        raise Exception("Interview not found")

    # get last question
    last_question = (
        db.query(InterviewMessage)
        .filter(
            InterviewMessage.interview_id == interview_id,
            InterviewMessage.message_type == "QUESTION"
        )
        .order_by(InterviewMessage.created_at.desc())
        .first()
    )

    # store candidate answer
    answer_message = InterviewMessage(
        interview_id=interview_id,
        message_type="ANSWER",
        content=answer
    )

    db.add(answer_message)
    db.flush()

    # evaluate using AI
    ai_response = evaluate_answer(last_question.content, answer)

    try:
        data = json.loads(ai_response)
    except:
    # fallback if Gemini adds formatting
        import re
        json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise Exception("AI response parsing failed")

    score = data["score"]
    feedback = data["feedback"]
    next_question = data["next_question"]

    # update answer with evaluation
    answer_message.score = score
    answer_message.feedback = feedback

    # stop after 5 questions
    if interview.current_question_number >= 5:

        messages = db.query(InterviewMessage).filter(
            InterviewMessage.interview_id == interview_id
        ).all()

        transcript = ""

        for m in messages:
            transcript += f"{m.message_type}: {m.content}\n"

        ai_report = generate_interview_report(transcript)

        try:
            data = json.loads(ai_report)
        except:
            json_match = re.search(r"\{.*\}", ai_report, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise Exception("AI report parsing failed")

        report = InterviewReport(
            interview_id=interview_id,
            overall_score=data["overall_score"],
            strengths=data["strengths"],
            weaknesses=data["weaknesses"],
            recommendation=data["recommendation"]
        )

        db.add(report)

        interview.status = "COMPLETED"

        db.commit()

        return {
            "interview_completed": True,
            "report": data
        }

    # save next question
    question_message = InterviewMessage(
        interview_id=interview_id,
        message_type="QUESTION",
        content=next_question
    )

    db.add(question_message)

    interview.current_question_number += 1

    db.commit()

    return {
        "score": score,
        "feedback": feedback,
        "next_question": next_question
    }


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
    message_type="QUESTION",
    content=question
    )

    db.add(message)

    candidate.status = "INTERVIEW_STARTED"

    db.commit()

    return interview.id, question

