from app.core.gemini_client import generate_content


def generate_first_question(role, experience, skills):

    prompt = f"""
You are a senior technical interviewer.

Generate ONE realistic scenario-based interview question.

Candidate Profile:
Role: {role}
Experience Level: {experience}
Skills: {skills}

Rules:
- Ask exactly ONE question
- Make it practical and scenario based
- Avoid theoretical definitions
- Do not include explanations

Return only the question text.
"""

    response = generate_content(prompt)

    return response