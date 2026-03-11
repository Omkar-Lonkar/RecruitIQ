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
Extract structured information from this resume.

Return ONLY valid JSON.

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

    return generate_content(prompt)