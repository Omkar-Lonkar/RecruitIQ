import os
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")


def generate_content(prompt: str) -> str:
    """
    Generic Gemini text generation function
    """

    response = model.generate_content(prompt)

    if not response.text:
        raise Exception("Gemini returned empty response")

    return response.text.strip()


def parse_resume_with_gemini(resume_text: str) -> str:
    """
    Resume structured extraction
    """

    prompt = f"""
    You are an expert resume parser.

    Extract structured data in STRICT JSON format.

    Rules:
    - Output ONLY JSON
    - Do NOT include explanations
    - Do NOT skip project descriptions
    - If description exists → include it fully

    Schema:
    {{
    "skills": [string],

    "education": [string],

    "work_experience": [string],

    "projects": [
        {{
        "title": string,
        "description": string
        }}
    ],

    "certifications": [string]
    }}

    Important instructions:
    - Each project MUST have both title AND description
    - Do NOT return project title alone
    - Combine multiple lines into one meaningful description
    - Ignore unrelated text
    - Clean and concise output

    Resume:
    {resume_text}
    """

    return generate_content(prompt)


def evaluate_answer(question, answer):

    prompt = f"""
You are a technical interviewer evaluating a candidate answer.

Question:
{question}

Candidate Answer:
{answer}

Return ONLY valid JSON. Do not include explanations or markdown.

Format:

{{
"score": number between 1 and 10,
"feedback": "short feedback",
"next_question": "next technical follow-up question"
}}
"""

    response = model.generate_content(prompt)

    try:
        return response.candidates[0].content.parts[0].text
    except Exception:
        print("Full Gemini response:", response)
        return ""


def generate_interview_report(transcript):

    prompt = f"""
You are a senior technical interviewer.

Below is an interview transcript.

{transcript}

Evaluate the candidate.

Return JSON ONLY in this format:

{{
"overall_score": number between 1-10,
"strengths": "key strengths",
"weaknesses": "key weaknesses",
"recommendation": "HIRE / CONSIDER / REJECT"
}}
"""

    response = model.generate_content(prompt)

    return response.text.strip()