import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_company_candidate_email"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    current_role = Column(String)
    experience_years = Column(Float)
    location = Column(String)

    status = Column(String, nullable=False, default="NEW")
    source = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
