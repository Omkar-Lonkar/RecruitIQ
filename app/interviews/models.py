import uuid
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))

    interview_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ongoing")

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"))

    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    sequence_number = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id"))

    answer_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())


class InterviewScore(Base):
    __tablename__ = "interview_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"))

    communication_score = Column(Float)
    problem_solving_score = Column(Float)
    depth_score = Column(Float)
    consistency_score = Column(Float)

    overall_score = Column(Float)
    recommendation = Column(String)

    ai_summary = Column(Text)
    scored_at = Column(DateTime(timezone=True), server_default=func.now())
