from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.auth.models import Recruiter
from app.companies.models import Company
from app.core.security import hash_password, verify_password, create_access_token

def signup_company_and_recruiter(db: Session, data):
    # Prevent duplicate company inbox
    if db.query(Company).filter(Company.inbox_email == data.inbox_email).first():
        raise HTTPException(status_code=400, detail="Inbox already registered")

    company = Company(
        name=data.company_name,
        domain=data.company_domain,
        inbox_email=data.inbox_email,
    )
    db.add(company)
    db.flush()  # get company.id

    recruiter = Recruiter(
        email=data.recruiter_email,
        full_name=data.recruiter_full_name,
        password_hash=hash_password(data.recruiter_password),
        company_id=company.id,
    )
    db.add(recruiter)
    db.commit()

    return True


def login_recruiter(db: Session, email: str, password: str):
    recruiter = db.query(Recruiter).filter(Recruiter.email == email).first()
    if not recruiter:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, recruiter.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        subject=str(recruiter.id),
        company_id=str(recruiter.company_id),
    )

    return token
