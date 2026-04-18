import re
import json
from uuid import uuid4

from app.interviews.models import Interview, InterviewMessage, InterviewReport
from app.interviews.question_engine import generate_first_question
from app.candidates.models import Candidate
from app.resumes.models import Resume, ResumeParsedData
from app.core.gemini_client import evaluate_answer, generate_interview_report


def submit_answer(db, interview_id, answer):

    interview = db.query(Interview).filter(Interview.id == interview_id).first()

    if not interview:
        raise Exception("Interview not found")

    # -------- GET LAST QUESTION --------
    last_question = (
        db.query(InterviewMessage)
        .filter(
            InterviewMessage.interview_id == interview_id,
            InterviewMessage.message_type == "QUESTION"
        )
        .order_by(InterviewMessage.created_at.desc())
        .first()
    )

    # -------- STORE ANSWER --------
    answer_message = InterviewMessage(
        interview_id=interview_id,
        message_type="ANSWER",
        content=answer
    )

    db.add(answer_message)
    db.flush()

    # -------- AI EVALUATION --------
    ai_response = evaluate_answer(last_question.content, answer)

    try:
        if not ai_response or len(ai_response.strip()) < 10:
            raise Exception("Empty AI response")

        try:
            data = json.loads(ai_response)
        except:
            match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                raise Exception("Invalid JSON from AI")

    except Exception as e:
        print("AI RAW OUTPUT:", ai_response)
        print("ERROR:", str(e))

        data = {
            "score": 5,
            "feedback": "Evaluation failed",
            "next_question": "Can you explain one project you worked on?"
        }

    score = data.get("score", 5)
    feedback = data.get("feedback", "")
    next_question = data.get("next_question", "Tell me about your experience.")

    # -------- SAVE EVALUATION --------
    answer_message.score = score
    answer_message.feedback = feedback

    # -------- COMPLETE AFTER 5 QUESTIONS --------
    if interview.current_question_number >= 5:

        messages = db.query(InterviewMessage).filter(
            InterviewMessage.interview_id == interview_id
        ).all()

        transcript = ""
        for m in messages:
            transcript += f"{m.message_type}: {m.content}\n"

        ai_report = generate_interview_report(transcript)

        try:
            if not ai_report or len(ai_report.strip()) < 10:
                raise Exception("Empty AI report")

            try:
                data = json.loads(ai_report)
            except:
                match = re.search(r"\{.*\}", ai_report, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    raise Exception("Invalid JSON from AI report")

        except Exception as e:
            print("AI REPORT RAW:", ai_report)
            print("ERROR:", str(e))

            data = {
                "overall_score": 5,
                "strengths": "Could not evaluate",
                "weaknesses": "AI parsing failed",
                "recommendation": "CONSIDER"
            }

        report = InterviewReport(
            interview_id=interview_id,
            overall_score=data.get("overall_score", 5),
            strengths=data.get("strengths", ""),
            weaknesses=data.get("weaknesses", ""),
            recommendation=data.get("recommendation", "CONSIDER")
        )

        db.add(report)

        interview.status = "COMPLETED"

        candidate = db.query(Candidate).filter(
            Candidate.id == interview.candidate_id
        ).first()

        candidate.status = "INTERVIEW_COMPLETED"

        db.commit()

        return {
            "interview_completed": True,
            "report": data
        }

    # -------- NEXT QUESTION --------
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

    # -------- GET RESUME --------
    resume = db.query(Resume).filter(
        Resume.candidate_id == candidate.id
    ).order_by(Resume.uploaded_at.desc()).first()

    skills = []

    # -------- GET PARSED DATA --------
    parsed_resume = None

    if resume:
        parsed_resume = db.query(ResumeParsedData).filter(
            ResumeParsedData.resume_id == resume.id
        ).first()

    if parsed_resume and parsed_resume.skills:
        skills = parsed_resume.skills

    # -------- CREATE INTERVIEW --------
    interview = Interview(
        candidate_id=candidate.id,
        company_id=recruiter.company_id
    )

    db.add(interview)
    db.flush()

    # -------- FIRST QUESTION --------
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

    return {
    "interview_id": str(interview.id),
    "question": question
}