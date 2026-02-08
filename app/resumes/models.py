import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)

    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(Text, nullable=False)
    uploaded_via = Column(String, nullable=False)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class ResumeParsedData(Base):
    __tablename__ = "resume_parsed_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)

    skills = Column(JSONB)
    education = Column(JSONB)
    work_experience = Column(JSONB)
    projects = Column(JSONB)
    certifications = Column(JSONB)

    raw_text = Column(Text)
    parser_version = Column(String)

    parsed_at = Column(DateTime(timezone=True), server_default=func.now())
