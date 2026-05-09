"""Application middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings


def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI app."""

    # CORS middleware - allow requests from frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Trusted host middleware for security
    allowed_hosts = ["localhost", "127.0.0.1", "*.up.railway.app"]
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )
