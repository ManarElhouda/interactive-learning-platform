"""Pydantic models for child profile."""
from pydantic import BaseModel
from typing import List, Optional


class UserProfile(BaseModel):
    """Child profile schema."""
    child_id: str = "child_001"
    name: str = "Enfant"
    age: int = 8
    cognitive_level: str = "intermediate"  # beginner / intermediate / advanced
    preferred_colors: List[str] = ["blue", "yellow", "green"]
    interests: List[str] = ["animals", "nature", "sport"]
    language: str = "tunisian_arabic"
    style_preference: str = "cartoon"  # cartoon / realistic / watercolor
    blacklist: List[str] = []
    positive_keywords: List[str] = []
    created_at: str = ""
    updated_at: str = ""
    version: int = 1

    class Config:
        json_schema_extra = {
            "example": {
                "child_id": "child_001",
                "name": "Ahmed",
                "age": 8,
                "cognitive_level": "intermediate",
                "preferred_colors": ["blue", "yellow"],
                "interests": ["animals", "sport"],
                "language": "tunisian_arabic",
                "style_preference": "cartoon",
                "blacklist": [],
                "positive_keywords": [],
            }
        }
