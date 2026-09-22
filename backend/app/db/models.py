import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    processes = relationship("Process", back_populates="user", cascade="all, delete-orphan")


class Process(Base):
    __tablename__ = "processes"

    id = Column(String(36), primary_key=True, default=lambda: f"proc_{uuid.uuid4().hex[:12]}")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="Draft", nullable=False)  # Draft, Analyzing, Completed, Failed

    overall_confidence = Column(Float, nullable=True)
    confidence_decision = Column(String(20), nullable=True)  # HIGH, REVIEW, LOW
    validation_status = Column(String(50), nullable=True)    # Validated, Needs review, Failed

    # Serialized JSON outputs of multi-agent execution
    analysis_json = Column(Text, nullable=True)
    model_json = Column(Text, nullable=True)
    validation_json = Column(Text, nullable=True)
    confidence_json = Column(Text, nullable=True)
    intelligence_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="processes")
