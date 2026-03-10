from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.auth.dependencies import get_current_recruiter
from fastapi import Depends
from app.candidates.routes import router as candidate_router
from app.resumes.routes import router as resume_router

app = FastAPI(title="AI Recruitment Automation System")

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(candidate_router)

@app.get("/me")
def get_me(current_recruiter=Depends(get_current_recruiter)):
    return {
        "recruiter_id": str(current_recruiter.id),
        "company_id": str(current_recruiter.company_id),
        "email": current_recruiter.email,
    }

app.include_router(resume_router)