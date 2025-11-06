"""
Configuration settings for the YOLO11 API
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "YOLO11 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OAuth2 Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_CLIENT_ID: Optional[str] = None
    FACEBOOK_CLIENT_SECRET: Optional[str] = None
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # File Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MODELS_DIR: Path = BASE_DIR / "models"
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    RESULTS_DIR: Path = BASE_DIR / "results"
    
    # YOLO Settings
    DEFAULT_MODEL: str = "yolo11n.pt"
    DEFAULT_CONFIDENCE: float = 0.25
    DEFAULT_IOU: float = 0.45
    MAX_IMAGE_SIZE: int = 4096
    SUPPORTED_FORMATS: list = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    
    # Training Settings
    DEFAULT_EPOCHS: int = 100
    DEFAULT_BATCH_SIZE: int = 16
    DEFAULT_IMG_SIZE: int = 640
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        for directory in [self.UPLOAD_DIR, self.MODELS_DIR, self.DATASETS_DIR, self.RESULTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
