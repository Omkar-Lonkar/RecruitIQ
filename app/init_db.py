from app.core.database import engine, Base

from app.companies.models import Company
from app.auth.models import Recruiter
from app.candidates.models import Candidate
from app.resumes.models import Resume, ResumeParsedData
from app.interviews.models import (
    Interview,
    InterviewQuestion,
    InterviewAnswer,
    InterviewScore,
)

Base.metadata.create_all(bind=engine)
