"""
Health check endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from app.config import get_settings, Settings
from app.core.database.connection import get_database_client
from app.utils.supabase_auth import test_supabase_connection

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple health check."""
    return {
        "status": "healthy",
        "service": "mirage-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/")
async def health():
    """Basic health check with timestamp."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/detailed")
async def detailed_health(settings: Settings = Depends(get_settings)):
    """Detailed health check with service status."""
    
    services = {
        "api": True,
        "supabase": False,
        "livekit": False,
        "gemini": False,
        "simli": False
    }
    
    # Check Supabase
    services["supabase"] = settings.supabase_configured and test_supabase_connection()
    
    # Check LiveKit configuration
    services["livekit"] = settings.livekit_configured
    
    # Check Gemini configuration
    services["gemini"] = bool(settings.GOOGLE_API_KEY)
    
    # Check Simli configuration
    services["simli"] = bool(settings.SIMLI_API_KEY)
    
    overall_status = "healthy" if all(services.values()) else "degraded"
    
    return {
        "status": overall_status,
        "environment": settings.ENVIRONMENT,
        "services": services,
        "timestamp": datetime.utcnow().isoformat()
    }
