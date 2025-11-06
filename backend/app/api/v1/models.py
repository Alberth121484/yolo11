"""
Model management endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path
import logging
from datetime import datetime
import shutil

from app.schemas import ModelInfo, TaskType
from app.services.yolo_service import yolo_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """
    List all available models
    
    Returns a list of all models in the models directory
    """
    try:
        models = []
        
        for model_path in settings.MODELS_DIR.glob("*.pt"):
            try:
                # Get model info
                info = yolo_service.get_model_info(model_path.name)
                
                # Get file size
                file_size_mb = model_path.stat().st_size / (1024 * 1024)
                
                # Determine model size from name
                size = "n"
                for s in ["n", "s", "m", "l", "x"]:
                    if f"yolo11{s}" in model_path.name:
                        size = s
                        break
                
                models.append(ModelInfo(
                    name=model_path.name,
                    path=str(model_path),
                    size=size,
                    task=TaskType.DETECT,  # Default to detect
                    num_classes=info["num_classes"],
                    class_names=info["class_names"],
                    trained_on=None,
                    created_at=datetime.fromtimestamp(model_path.stat().st_ctime),
                    file_size_mb=round(file_size_mb, 2)
                ))
                
            except Exception as e:
                logger.warning(f"Failed to get info for model {model_path.name}: {e}")
                continue
        
        # Sort by creation date
        models.sort(key=lambda x: x.created_at, reverse=True)
        
        return models
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}", response_model=ModelInfo)
async def get_model_info_endpoint(model_name: str):
    """
    Get information about a specific model
    
    - **model_name**: Name of the model file (e.g., yolo11n.pt)
    
    Returns detailed model information
    """
    try:
        model_path = settings.MODELS_DIR / model_name
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get model info
        info = yolo_service.get_model_info(model_name)
        
        # Get file size
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        
        # Determine model size
        size = "n"
        for s in ["n", "s", "m", "l", "x"]:
            if f"yolo11{s}" in model_name:
                size = s
                break
        
        return ModelInfo(
            name=model_name,
            path=str(model_path),
            size=size,
            task=TaskType.DETECT,
            num_classes=info["num_classes"],
            class_names=info["class_names"],
            trained_on=None,
            created_at=datetime.fromtimestamp(model_path.stat().st_ctime),
            file_size_mb=round(file_size_mb, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}/download")
async def download_model(model_name: str):
    """
    Download a model file
    
    - **model_name**: Name of the model file
    
    Returns the model file for download
    """
    try:
        model_path = settings.MODELS_DIR / model_name
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        return FileResponse(
            path=model_path,
            media_type="application/octet-stream",
            filename=model_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/upload")
async def upload_model(
    file: UploadFile = File(..., description="Model file (.pt)")
):
    """
    Upload a custom trained model
    
    - **file**: Model file (.pt format)
    
    Uploads and stores a custom trained model
    """
    try:
        # Validate file extension
        if not file.filename.endswith(".pt"):
            raise HTTPException(
                status_code=400,
                detail="Only .pt model files are supported"
            )
        
        # Save model
        model_path = settings.MODELS_DIR / file.filename
        
        if model_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Model {file.filename} already exists"
            )
        
        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Model {file.filename} uploaded successfully")
        
        # Try to get model info
        try:
            info = yolo_service.get_model_info(file.filename)
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            
            return {
                "success": True,
                "message": "Model uploaded successfully",
                "model_name": file.filename,
                "path": str(model_path),
                "num_classes": info["num_classes"],
                "file_size_mb": round(file_size_mb, 2)
            }
        except Exception as e:
            logger.warning(f"Could not load model info: {e}")
            return {
                "success": True,
                "message": "Model uploaded successfully (info unavailable)",
                "model_name": file.filename,
                "path": str(model_path)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """
    Delete a model
    
    - **model_name**: Name of the model to delete
    
    Permanently deletes the model file
    """
    try:
        model_path = settings.MODELS_DIR / model_name
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Prevent deletion of default models
        default_models = [
            "yolo11n.pt", "yolo11s.pt", "yolo11m.pt", 
            "yolo11l.pt", "yolo11x.pt"
        ]
        
        if model_name in default_models:
            raise HTTPException(
                status_code=403,
                detail="Cannot delete default YOLO models"
            )
        
        model_path.unlink()
        
        logger.info(f"Model {model_name} deleted successfully")
        
        return {
            "success": True,
            "message": f"Model {model_name} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/export")
async def export_model(
    model_name: str,
    format: str = "onnx"
):
    """
    Export model to different format
    
    - **model_name**: Name of the model to export
    - **format**: Target format (onnx, torchscript, coreml, etc.)
    
    Exports the model to the specified format
    """
    try:
        model_path = settings.MODELS_DIR / model_name
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Export model
        result = yolo_service.export_model(
            model_path=model_path,
            format=format
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/validate")
async def validate_model(
    model_name: str,
    dataset_name: str
):
    """
    Validate a model on a dataset
    
    - **model_name**: Name of the model to validate
    - **dataset_name**: Name of the dataset to validate on
    
    Runs validation and returns metrics
    """
    try:
        from app.services.dataset_service import dataset_service
        
        model_path = settings.MODELS_DIR / model_name
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get dataset info
        dataset_info = dataset_service.get_dataset_info(dataset_name)
        data_yaml = Path(dataset_info["path"]) / "data.yaml"
        
        if not data_yaml.exists():
            raise HTTPException(
                status_code=404,
                detail="Dataset configuration not found"
            )
        
        # Validate model
        result = yolo_service.validate_model(
            model_path=model_path,
            data_yaml=data_yaml
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
