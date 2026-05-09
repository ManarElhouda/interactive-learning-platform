from fastapi import APIRouter

from .health import router as health_router
from .lessons import router as lessons_router

# Main API router
api_router = APIRouter(prefix="/api")

# Include all route modules
api_router.include_router(health_router, tags=["health"])
api_router.include_router(lessons_router, prefix="/lessons", tags=["lessons"])

__all__ = ["api_router"]
