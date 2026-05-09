"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.config import settings
from app.database.connection import create_all_tables
from app.middleware import setup_middleware


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/api/docs" if settings.enable_docs else None,
        redoc_url="/api/redoc" if settings.enable_docs else None,
        openapi_url="/api/openapi.json" if settings.enable_docs else None,
    )

    # Setup middleware
    setup_middleware(app)

    # Include API routes
    app.include_router(api_router)

    # Create database tables
    @app.on_event("startup")
    def startup_event() -> None:
        """Run on application startup."""
        create_all_tables()

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": "Interactive Learning Platform API",
            "version": settings.app_version,
            "docs": "/api/docs" if settings.enable_docs else "disabled",
        }

    # Error handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc: Exception) -> JSONResponse:
        """Handle generic exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc) if settings.debug else "An error occurred",
            },
        )

    return app


app = create_app()
