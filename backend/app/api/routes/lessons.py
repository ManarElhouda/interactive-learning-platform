"""Lesson routes."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas import Lesson, LessonCreate, LessonUpdate
from app.services import LessonService

router = APIRouter()
lesson_service = LessonService()


@router.get("", response_model=list[Lesson])
async def list_lessons(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    difficulty: Optional[str] = None,
    type: Optional[str] = None,
) -> list[Lesson]:
    """List all lessons with optional filtering."""
    return lesson_service.get_lessons(
        skip=skip, limit=limit, difficulty=difficulty, lesson_type=type
    )


@router.get("/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: int) -> Lesson:
    """Get a specific lesson by ID."""
    lesson = lesson_service.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.post("", response_model=Lesson)
async def create_lesson(lesson_data: LessonCreate) -> Lesson:
    """Create a new lesson."""
    return lesson_service.create_lesson(lesson_data)


@router.put("/{lesson_id}", response_model=Lesson)
async def update_lesson(lesson_id: int, lesson_data: LessonUpdate) -> Lesson:
    """Update an existing lesson."""
    lesson = lesson_service.update_lesson(lesson_id, lesson_data)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: int) -> dict[str, str]:
    """Delete a lesson."""
    success = lesson_service.delete_lesson(lesson_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"message": "Lesson deleted successfully"}
