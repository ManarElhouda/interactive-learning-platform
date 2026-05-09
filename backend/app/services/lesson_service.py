"""Lesson service - business logic layer."""

from typing import Optional

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.lesson import LessonModel
from app.schemas import Lesson, LessonCreate, LessonUpdate


class LessonService:
    """Service for lesson-related operations."""

    def __init__(self, db: Optional[Session] = None):
        """Initialize service with database session."""
        self.db = db or SessionLocal()

    def get_lessons(
        self,
        skip: int = 0,
        limit: int = 10,
        difficulty: Optional[str] = None,
        lesson_type: Optional[str] = None,
    ) -> list[Lesson]:
        """Get all lessons with optional filtering."""
        query = self.db.query(LessonModel)

        if difficulty:
            query = query.filter(LessonModel.difficulty == difficulty)

        if lesson_type:
            query = query.filter(LessonModel.type == lesson_type)

        lessons = query.offset(skip).limit(limit).all()
        return [Lesson.model_validate(lesson) for lesson in lessons]

    def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        """Get a specific lesson by ID."""
        lesson = self.db.query(LessonModel).filter(LessonModel.id == lesson_id).first()
        if lesson:
            return Lesson.model_validate(lesson)
        return None

    def create_lesson(self, lesson_data: LessonCreate) -> Lesson:
        """Create a new lesson."""
        db_lesson = LessonModel(**lesson_data.model_dump())
        self.db.add(db_lesson)
        self.db.commit()
        self.db.refresh(db_lesson)
        return Lesson.model_validate(db_lesson)

    def update_lesson(self, lesson_id: int, lesson_data: LessonUpdate) -> Optional[Lesson]:
        """Update an existing lesson."""
        db_lesson = self.db.query(LessonModel).filter(LessonModel.id == lesson_id).first()

        if not db_lesson:
            return None

        update_data = lesson_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lesson, key, value)

        self.db.add(db_lesson)
        self.db.commit()
        self.db.refresh(db_lesson)
        return Lesson.model_validate(db_lesson)

    def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson by ID."""
        db_lesson = self.db.query(LessonModel).filter(LessonModel.id == lesson_id).first()

        if not db_lesson:
            return False

        self.db.delete(db_lesson)
        self.db.commit()
        return True
