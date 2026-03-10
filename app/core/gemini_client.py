import os
from click import prompt
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")


def parse_resume_with_gemini(resume_text: str) -> str:
    prompt = f"""
    Extract structured information from this resume.

    Return ONLY valid JSON.
    Do NOT include explanations.
    Do NOT include markdown.
    Do NOT include backticks.

    Schema:
    {{
    "skills": [],
    "education": [],
    "work_experience": [],
    "projects": [],
    "certifications": []
    }}

    Resume:
    {resume_text}
    """


    response = model.generate_content(prompt)

    return response.text
