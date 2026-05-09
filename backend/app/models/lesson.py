"""Database lesson model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, func

from app.database.connection import Base


class LessonModel(Base):
    """Lesson database model."""

    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(1000), nullable=True)
    difficulty = Column(String(50), default="beginner", nullable=False)
    type = Column(String(50), default="vocabulary", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
