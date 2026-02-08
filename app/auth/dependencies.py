from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.auth.models import Recruiter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def get_current_recruiter(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        recruiter_id = payload.get("sub")
        company_id = payload.get("company_id")

        if not recruiter_id or not company_id:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    recruiter = (
        db.query(Recruiter)
        .filter(
            Recruiter.id == recruiter_id,
            Recruiter.company_id == company_id,
        )
        .first()
    )

    if not recruiter:
        raise HTTPException(status_code=401, detail="Recruiter not found")

    return recruiter
