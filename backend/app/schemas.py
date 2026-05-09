"""Pydantic schemas for request/response validation (similar to Zod in frontend)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LessonBase(BaseModel):
    """Base lesson schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    difficulty: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")
    type: str = Field("vocabulary", pattern="^(vocabulary|grammar|listening|speaking)$")


class LessonCreate(LessonBase):
    """Schema for creating a lesson."""

    pass


class LessonUpdate(BaseModel):
    """Schema for updating a lesson."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    difficulty: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    type: Optional[str] = Field(None, pattern="^(vocabulary|grammar|listening|speaking)$")


class Lesson(LessonBase):
    """Complete lesson schema for responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str
    message: str
    status_code: int
