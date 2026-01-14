"""
Mirage Backend - FastAPI Application Entry Point

Voice AI Avatar Platform with:
- Supabase authentication
- LiveKit room token generation
- Session management
- Multi-agent support
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.config import get_settings
from app.utils.logging import configure_logging, get_logger
from app.api.endpoints import health, auth, users, sessions, livekit, agents

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Mirage API",
    version="1.0.0",
    description="Voice AI Avatar Platform - Backend API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(livekit.router, prefix="/api/v1/livekit", tags=["livekit"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Mirage API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "sessions": "/api/v1/sessions",
            "livekit": "/api/v1/livekit",
            "agents": "/api/v1/agents"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Ping endpoint
@app.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup - log configuration."""
    logger.info("=" * 60)
    logger.info("🚀 Mirage API Starting")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Supabase: {'✅ Configured' if settings.supabase_configured else '❌ Not configured'}")
    logger.info(f"LiveKit: {'✅ Configured' if settings.livekit_configured else '❌ Not configured'}")
    logger.info(f"Gemini: {'✅ Configured' if settings.GOOGLE_API_KEY else '❌ Not configured'}")
    logger.info(f"Simli: {'✅ Configured' if settings.SIMLI_API_KEY else '❌ Not configured'}")
    logger.info("=" * 60)
    logger.info("Available endpoints:")
    logger.info("  GET  /api/v1/health/ping")
    logger.info("  GET  /api/v1/auth/me")
    logger.info("  GET  /api/v1/users/profile")
    logger.info("  GET  /api/v1/sessions/")
    logger.info("  POST /api/v1/livekit/token")
    logger.info("  GET  /api/v1/agents/")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    logger.info("🛑 Mirage API Shutting Down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
