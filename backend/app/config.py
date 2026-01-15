"""
Configuration settings for Mirage Backend.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


def get_env_file():
    """Determine which environment file to use."""
    is_production = any([
        os.getenv("ENVIRONMENT") == "production",
        os.getenv("K_SERVICE"),  # Cloud Run
        os.getenv("GAE_ENV"),    # App Engine
    ])
    
    if is_production:
        return None
    
    # Look for .env in parent directory (project root)
    parent_env = "../.env"
    if os.path.exists(parent_env):
        return parent_env
    
    # Look for .env in current directory
    if os.path.exists(".env"):
        return ".env"
    
    return None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ==========================================================================
    # Environment
    # ==========================================================================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # ==========================================================================
    # Server
    # ==========================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # ==========================================================================
    # Supabase Configuration
    # ==========================================================================
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    
    # ==========================================================================
    # LiveKit Configuration
    # ==========================================================================
    LIVEKIT_URL: str = ""
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    
    # ==========================================================================
    # Google Gemini Configuration
    # ==========================================================================
    GOOGLE_API_KEY: str = ""
    
    # ==========================================================================
    # Simli Configuration
    # ==========================================================================
    SIMLI_API_KEY: str = ""
    SIMLI_FACE_ID: str = "tmp9i8bbq7c"  # Default Simli face
    
    # ==========================================================================
    # Application Settings
    # ==========================================================================
    DEFAULT_AGENT_TYPE: str = "teacher"
    
    # ==========================================================================
    # Emotion Mapping Settings
    # ==========================================================================
    ENABLE_EMOTION_MAPPING: bool = True
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.6
    EMOTION_ANALYSIS_INTERVAL: int = 5  # seconds
    
    # ==========================================================================
    # Computed Properties
    # ==========================================================================
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def supabase_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY)
    
    @property
    def livekit_configured(self) -> bool:
        """Check if LiveKit is configured."""
        return bool(self.LIVEKIT_URL and self.LIVEKIT_API_KEY and self.LIVEKIT_API_SECRET)
    
    class Config:
        env_file = get_env_file()
        case_sensitive = True
        extra = "allow"


# Singleton pattern
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
        env_file = get_env_file()
        if env_file:
            print(f"🔧 Loading config from: {env_file}")
        else:
            print(f"🔧 Loading config from: environment variables")
    return _settings


# Alternative using lru_cache (used by FastAPI dependency injection)
@lru_cache()
def get_cached_settings() -> Settings:
    """Get cached settings for FastAPI dependencies."""
    return Settings()
