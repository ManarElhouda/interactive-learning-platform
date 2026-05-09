"""Health check routes."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthCheckResponse

router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint to verify backend is running."""
    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )
