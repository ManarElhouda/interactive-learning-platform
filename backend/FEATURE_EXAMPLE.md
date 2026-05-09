"""
Example: How to add a new feature to the backend

This file demonstrates the recommended pattern for extending the platform.
Delete this file once you understand the pattern.
"""

# Step 1: Create a new schema in app/schemas.py
# Example:
# class ExerciseBase(BaseModel):
#     lesson_id: int
#     question: str
#     answer: str
#
# class ExerciseCreate(ExerciseBase):
#     pass
#
# class Exercise(ExerciseBase):
#     id: int
#     created_at: datetime

# Step 2: Create a database model in app/models/
# Example: app/models/exercise.py
# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
# from app.database.connection import Base
#
# class ExerciseModel(Base):
#     __tablename__ = "exercises"
#     id = Column(Integer, primary_key=True)
#     lesson_id = Column(Integer, ForeignKey("lessons.id"))
#     question = Column(String, nullable=False)
#     answer = Column(String, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())

# Step 3: Create a service in app/services/
# Example: app/services/exercise_service.py
# class ExerciseService:
#     def __init__(self, db=None):
#         self.db = db or SessionLocal()
#
#     def get_exercises_for_lesson(self, lesson_id: int):
#         return self.db.query(ExerciseModel).filter(
#             ExerciseModel.lesson_id == lesson_id
#         ).all()

# Step 4: Create routes in app/api/routes/
# Example: app/api/routes/exercises.py
# @router.get("/lesson/{lesson_id}")
# async def get_lesson_exercises(lesson_id: int):
#     service = ExerciseService()
#     exercises = service.get_exercises_for_lesson(lesson_id)
#     return [Exercise.model_validate(e) for e in exercises]

# Step 5: Update app/api/routes/__init__.py
# from .exercises import router as exercises_router
# api_router.include_router(exercises_router, prefix="/exercises", tags=["exercises"])

# That's it! You now have a complete feature integrated.

# 🎯 Key Principles:
# 1. Keep concerns separated (routes, services, models, schemas)
# 2. Use type hints everywhere
# 3. Validate input with Pydantic schemas
# 4. Keep business logic in services
# 5. Document public functions with docstrings
