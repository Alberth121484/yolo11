"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging

from app.config import settings
from app.api.v1 import inference, training, datasets, models, health, auth, config
from starlette.middleware.sessions import SessionMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # YOLO11 API - Sistema de Detección de Objetos con IA
    
    Esta API proporciona endpoints para:
    - **Inferencia**: Detectar objetos en imágenes usando modelos YOLO11
    - **Entrenamiento**: Entrenar modelos personalizados con tus propios datos
    - **Datasets**: Gestionar datasets y anotaciones
    - **Modelos**: Gestionar y descargar modelos entrenados
    
    ## Características
    - Detección de objetos en tiempo real
    - Entrenamiento de modelos personalizados
    - Múltiples formatos de imagen soportados
    - API RESTful completa
    - Documentación interactiva
    
    ## Tecnologías
    - FastAPI
    - Ultralytics YOLO11
    - PyTorch
    - OpenCV
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add Session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(inference.router, prefix="/api/v1", tags=["Inference"])
app.include_router(training.router, prefix="/api/v1", tags=["Training"])
app.include_router(datasets.router, prefix="/api/v1", tags=["Datasets"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])

# Mount static files
app.mount("/uploads/datasets", StaticFiles(directory=str(settings.DATASETS_DIR)), name="datasets")
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
app.mount("/results", StaticFiles(directory=str(settings.RESULTS_DIR)), name="results")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info("API is ready to accept requests")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
