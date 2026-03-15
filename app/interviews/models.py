from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))

    status = Column(String, default="STARTED")

    current_question_number = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False
    )

    message_type = Column(String, nullable=False)
    # QUESTION or ANSWER

    content = Column(Text, nullable=False)

    score = Column(Integer, nullable=True)

    feedback = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterviewScore(Base):
    __tablename__ = "interview_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"))

    question_number = Column(Integer)

    score = Column(Integer)

    strengths = Column(Text)
    weaknesses = Column(Text)

    followup_reason = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False
    )

    overall_score = Column(Integer)

    strengths = Column(Text)

    weaknesses = Column(Text)

    recommendation = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())