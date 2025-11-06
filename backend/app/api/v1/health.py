"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
import torch

from app.schemas import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns API status and system information
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        yolo_available=True,
        cuda_available=torch.cuda.is_available()
    )


@router.get("/info")
async def api_info():
    """
    Get API information
    
    Returns detailed API and system information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "system": {
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "torch_version": torch.__version__,
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }
