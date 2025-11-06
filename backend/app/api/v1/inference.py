"""
Inference endpoints for object detection
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path
import logging
import shutil
from datetime import datetime

from app.schemas import InferenceRequest, InferenceResponse, BatchInferenceResponse
from app.services.yolo_service import yolo_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict", response_model=InferenceResponse)
async def predict_single_image(
    file: UploadFile = File(..., description="Image file to analyze"),
    model_name: Optional[str] = Form(None, description="Model name to use"),
    confidence: Optional[float] = Form(0.25, description="Confidence threshold"),
    iou: Optional[float] = Form(0.45, description="IoU threshold"),
    max_det: Optional[int] = Form(300, description="Maximum detections"),
    imgsz: Optional[int] = Form(640, description="Image size")
):
    """
    Run object detection on a single image
    
    - **file**: Image file (JPG, PNG, etc.)
    - **model_name**: YOLO model to use (default: yolo11n.pt)
    - **confidence**: Confidence threshold (0.0-1.0)
    - **iou**: IoU threshold for NMS (0.0-1.0)
    - **max_det**: Maximum number of detections
    - **imgsz**: Image size for inference
    
    Returns detected objects with bounding boxes and confidence scores
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {settings.SUPPORTED_FORMATS}"
            )
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = settings.UPLOAD_DIR / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing image: {filename}")
        
        # Run inference
        result = yolo_service.predict(
            image_path=file_path,
            model_name=model_name,
            confidence=confidence,
            iou=iou,
            max_det=max_det,
            imgsz=imgsz,
            save=True
        )
        
        logger.info(f"Detected {len(result['detections'])} objects in {filename}")
        
        return InferenceResponse(**result)
        
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch", response_model=BatchInferenceResponse)
async def predict_batch_images(
    files: List[UploadFile] = File(..., description="List of image files to analyze"),
    model_name: Optional[str] = Form(None, description="Model name to use"),
    confidence: Optional[float] = Form(0.25, description="Confidence threshold"),
    iou: Optional[float] = Form(0.45, description="IoU threshold"),
    max_det: Optional[int] = Form(300, description="Maximum detections"),
    imgsz: Optional[int] = Form(640, description="Image size")
):
    """
    Run object detection on multiple images
    
    - **files**: List of image files (JPG, PNG, etc.)
    - **model_name**: YOLO model to use (default: yolo11n.pt)
    - **confidence**: Confidence threshold (0.0-1.0)
    - **iou**: IoU threshold for NMS (0.0-1.0)
    - **max_det**: Maximum number of detections per image
    - **imgsz**: Image size for inference
    
    Returns detected objects for all images
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 images allowed per batch")
        
        # Save all uploaded files
        file_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, file in enumerate(files):
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.SUPPORTED_FORMATS:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue
            
            filename = f"{timestamp}_{idx}_{file.filename}"
            file_path = settings.UPLOAD_DIR / filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_paths.append(file_path)
        
        if not file_paths:
            raise HTTPException(status_code=400, detail="No valid image files provided")
        
        logger.info(f"Processing batch of {len(file_paths)} images")
        
        # Run batch inference
        result = yolo_service.predict_batch(
            image_paths=file_paths,
            model_name=model_name,
            confidence=confidence,
            iou=iou,
            max_det=max_det,
            imgsz=imgsz,
            save=True
        )
        
        logger.info(f"Batch processing complete: {result['total_detections']} total detections")
        
        return BatchInferenceResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{filename}")
async def get_result_image(filename: str):
    """
    Download a result image
    
    - **filename**: Name of the result image file
    
    Returns the annotated image file
    """
    try:
        # Search for the file in results directory
        result_files = list(settings.RESULTS_DIR.rglob(filename))
        
        if not result_files:
            raise HTTPException(status_code=404, detail="Result image not found")
        
        result_path = result_files[0]
        
        return FileResponse(
            path=result_path,
            media_type="image/jpeg",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get result image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/url")
async def predict_from_url(
    url: str = Form(..., description="Image URL"),
    model_name: Optional[str] = Form(None, description="Model name to use"),
    confidence: Optional[float] = Form(0.25, description="Confidence threshold"),
    iou: Optional[float] = Form(0.45, description="IoU threshold")
):
    """
    Run object detection on an image from URL
    
    - **url**: URL of the image to analyze
    - **model_name**: YOLO model to use
    - **confidence**: Confidence threshold
    - **iou**: IoU threshold
    
    Returns detected objects
    """
    try:
        # Download image from URL
        import requests
        from io import BytesIO
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save to temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_url_image.jpg"
        file_path = settings.UPLOAD_DIR / filename
        
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Downloaded image from URL: {url}")
        
        # Run inference
        result = yolo_service.predict(
            image_path=file_path,
            model_name=model_name,
            confidence=confidence,
            iou=iou,
            save=True
        )
        
        return InferenceResponse(**result)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image from URL: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
    except Exception as e:
        logger.error(f"Inference from URL failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
