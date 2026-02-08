from pydantic import BaseModel, EmailStr, Field

class CompanySignupRequest(BaseModel):
    company_name: str
    company_domain: str | None = None
    inbox_email: EmailStr
    recruiter_full_name: str
    recruiter_email: EmailStr
    recruiter_password: str = Field(
        min_length=8,
        max_length=64,
        description="Password must be between 8 and 64 characters",
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
