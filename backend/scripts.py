"""
Quick start scripts for development.

Usage:
    python scripts/init_db.py  - Initialize database with sample data
    python scripts/seed_lessons.py - Add sample lessons
"""

import os
import sys

# Add backend root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal, create_all_tables
from app.models.lesson import LessonModel


def init_db():
    """Initialize database with tables."""
    print("Creating database tables...")
    create_all_tables()
    print("✓ Database initialized")


def seed_sample_lessons():
    """Add sample lessons to database."""
    db = SessionLocal()
    
    # Check if lessons already exist
    existing = db.query(LessonModel).count()
    if existing > 0:
        print(f"✓ Database already has {existing} lessons")
        db.close()
        return
    
    sample_lessons = [
        LessonModel(
            title="Greetings",
            description="Learn basic greetings and introductions",
            difficulty="beginner",
            type="vocabulary"
        ),
        LessonModel(
            title="Numbers 1-10",
            description="Learn counting from 1 to 10",
            difficulty="beginner",
            type="vocabulary"
        ),
        LessonModel(
            title="Present Simple Tense",
            description="Understanding the present simple tense",
            difficulty="intermediate",
            type="grammar"
        ),
        LessonModel(
            title="Restaurant Dialogue",
            description="Common phrases for ordering at a restaurant",
            difficulty="intermediate",
            type="listening"
        ),
        LessonModel(
            title="Pronunciation Guide",
            description="Master difficult pronunciations",
            difficulty="beginner",
            type="speaking"
        ),
    ]
    
    db.add_all(sample_lessons)
    db.commit()
    print(f"✓ Added {len(sample_lessons)} sample lessons")
    db.close()


if __name__ == "__main__":
    init_db()
    seed_sample_lessons()
    print("\n✓ Database setup complete!")
