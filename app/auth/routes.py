from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.schemas import (
    CompanySignupRequest,
    LoginRequest,
    TokenResponse,
)
from app.auth.service import signup_company_and_recruiter, login_recruiter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/company/signup")
def company_signup(
    payload: CompanySignupRequest,
    db: Session = Depends(get_db),
):
    signup_company_and_recruiter(db, payload)
    return {"message": "Company and recruiter created"}


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    token = login_recruiter(db, payload.email, payload.password)
    return {"access_token": token}
