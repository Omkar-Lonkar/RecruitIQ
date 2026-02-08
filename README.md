# RecruitIQ  
### AI-Powered Multi-Company Recruitment Automation System

RecruitIQ is a backend-first recruitment automation platform designed to streamline early-stage hiring using AI-driven email intake, resume screening, and intelligent interview workflows.

This project is built as a **Final Year Engineering Project** with emphasis on:
- Clean backend architecture
- Multi-company (multi-tenant) design
- AI orchestration using Gemini
- Real-world recruitment workflows

---

## 🚀 Key Features

- Multi-company support (SaaS-style architecture)
- Recruiter authentication with JWT
- Company-scoped candidate pipeline
- Resume ingestion & parsing (planned)
- Intelligent interview bot (planned)
- AutoMail email intake integration (existing module)

---

## 🏗️ Architecture Overview

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Auth**: JWT (HTTP Bearer)
- **AI Provider**: Gemini API
- **Design Style**: Modular, service-based, backend-first

---

## 🔐 Authentication

- Recruiters belong to a company
- JWT contains `recruiter_id` and `company_id`
- All protected APIs are company-scoped
- Passwords hashed using **Argon2**

---

## 🗂️ Project Structure
app/
├── auth/ # Recruiter auth & JWT
├── companies/ # Company entity
├── candidates/ # Candidate pipeline (upcoming)
├── resumes/ # Resume handling (upcoming)
├── interviews/ # AI interview system (upcoming)
├── core/ # DB, config, security
└── main.py # FastAPI entry point


---

## ⚙️ Setup Instructions

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app


```


---

## ⚙️ Current Status

✅ Multi-company database schema
✅ Recruiter signup/login (JWT-based)
✅ Auth + company isolation verified

🚧 Candidate APIs
🚧 Resume parsing
🚧 Interview bot
🚧 AutoMail integration

---

## ⚙️ Academic Context

This project is developed as a Final Year Project focusing on:
-Scalable backend design
-AI-assisted automation
-Real-world SaaS patterns.