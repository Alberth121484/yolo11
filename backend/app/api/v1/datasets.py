"""
Dataset management endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from pathlib import Path
import logging
import shutil
from datetime import datetime

from app.schemas import DatasetInfo, CreateDatasetRequest, ImageAnnotation
from app.services.dataset_service import dataset_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/datasets", response_model=DatasetInfo)
async def create_dataset(request: CreateDatasetRequest):
    """
    Create a new dataset
    
    - **name**: Dataset name (alphanumeric, underscores, hyphens)
    - **class_names**: List of class names for the dataset
    - **description**: Optional description
    
    Creates a new dataset with the YOLO directory structure
    """
    try:
        result = dataset_service.create_dataset(
            name=request.name,
            class_names=request.class_names,
            description=request.description
        )
        
        return DatasetInfo(
            name=result["name"],
            path=result["path"],
            num_classes=result["num_classes"],
            class_names=result["class_names"],
            num_images_train=0,
            num_images_val=0,
            num_images_test=0,
            created_at=datetime.fromisoformat(result["created_at"])
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets", response_model=List[DatasetInfo])
async def list_datasets():
    """
    List all available datasets
    
    Returns a list of all datasets with their information
    """
    try:
        datasets = dataset_service.list_datasets()
        
        return [
            DatasetInfo(
                name=d["name"],
                path=d["path"],
                num_classes=d["num_classes"],
                class_names=d["class_names"],
                num_images_train=d["num_images_train"],
                num_images_val=d["num_images_val"],
                num_images_test=d.get("num_images_test", 0),
                created_at=datetime.fromisoformat(d["created_at"]) 
                    if d["created_at"] != "unknown" else datetime.now()
            )
            for d in datasets
        ]
        
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_name}", response_model=DatasetInfo)
async def get_dataset(dataset_name: str):
    """
    Get information about a specific dataset
    
    - **dataset_name**: Name of the dataset
    
    Returns detailed dataset information
    """
    try:
        info = dataset_service.get_dataset_info(dataset_name)
        
        return DatasetInfo(
            name=info["name"],
            path=info["path"],
            num_classes=info["num_classes"],
            class_names=info["class_names"],
            num_images_train=info["num_images_train"],
            num_images_val=info["num_images_val"],
            num_images_test=info.get("num_images_test", 0),
            created_at=datetime.fromisoformat(info["created_at"])
                if info["created_at"] != "unknown" else datetime.now()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get dataset info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/datasets/{dataset_name}")
async def delete_dataset(dataset_name: str):
    """
    Delete a dataset
    
    - **dataset_name**: Name of the dataset to delete
    
    Permanently deletes the dataset and all its contents
    """
    try:
        result = dataset_service.delete_dataset(dataset_name)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{dataset_name}/images")
async def add_images_to_dataset(
    dataset_name: str,
    files: List[UploadFile] = File(..., description="Image files to add"),
    split: str = Form("train", description="Dataset split (train/val/test)")
):
    """
    Add images to a dataset
    
    - **dataset_name**: Name of the dataset
    - **files**: List of image files to add
    - **split**: Which split to add images to (train/val/test)
    
    Adds the uploaded images to the specified dataset split
    """
    try:
        if split not in ["train", "val", "test"]:
            raise HTTPException(
                status_code=400,
                detail="Split must be one of: train, val, test"
            )
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        results = []
        
        for file in files:
            # Validate file
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.SUPPORTED_FORMATS:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue
            
            # Save temporarily
            temp_path = settings.UPLOAD_DIR / file.filename
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Add to dataset
            try:
                result = dataset_service.add_image(
                    dataset_name=dataset_name,
                    image_path=temp_path,
                    split=split,
                    annotations=None  # No annotations by default
                )
                results.append(result)
            finally:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()
        
        logger.info(f"Added {len(results)} images to {dataset_name}/{split}")
        
        return {
            "success": True,
            "message": f"Added {len(results)} images to {split} split",
            "results": results
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add images to dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{dataset_name}/images/annotated")
async def add_annotated_image(
    dataset_name: str,
    file: UploadFile = File(..., description="Image file"),
    split: str = Form("train", description="Dataset split"),
    annotations: str = Form(..., description="JSON string of annotations")
):
    """
    Add an annotated image to a dataset
    
    - **dataset_name**: Name of the dataset
    - **file**: Image file
    - **split**: Dataset split (train/val/test)
    - **annotations**: JSON array of annotations with class_id and bbox
    
    Example annotations format:
    ```json
    [
        {
            "class_id": 0,
            "bbox": {"x1": 100, "y1": 200, "x2": 300, "y2": 400}
        }
    ]
    ```
    """
    try:
        import json
        
        # Parse annotations
        try:
            annotations_list = json.loads(annotations)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for annotations"
            )
        
        # Validate file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}"
            )
        
        # Save temporarily
        temp_path = settings.UPLOAD_DIR / file.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # Add to dataset with annotations
            result = dataset_service.add_image(
                dataset_name=dataset_name,
                image_path=temp_path,
                split=split,
                annotations=annotations_list
            )
            
            return result
            
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add annotated image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{dataset_name}/split")
async def split_dataset(
    dataset_name: str,
    train_ratio: float = Form(0.7, description="Training set ratio"),
    val_ratio: float = Form(0.2, description="Validation set ratio"),
    test_ratio: float = Form(0.1, description="Test set ratio")
):
    """
    Split dataset into train/val/test sets
    
    - **dataset_name**: Name of the dataset
    - **train_ratio**: Ratio for training set (default: 0.7)
    - **val_ratio**: Ratio for validation set (default: 0.2)
    - **test_ratio**: Ratio for test set (default: 0.1)
    
    Redistributes images across splits according to the specified ratios
    """
    try:
        result = dataset_service.split_dataset(
            dataset_name=dataset_name,
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            test_ratio=test_ratio
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to split dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_name}/validate")
async def validate_dataset(dataset_name: str):
    """
    Validate dataset structure and integrity
    
    - **dataset_name**: Name of the dataset
    
    Checks for missing files, orphaned labels, and other issues
    """
    try:
        result = dataset_service.validate_dataset(dataset_name)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to validate dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_name}/export")
async def export_dataset(
    dataset_name: str,
    format: str = "yolo"
):
    """
    Export dataset in specified format
    
    - **dataset_name**: Name of the dataset
    - **format**: Export format (yolo, coco, pascal_voc)
    
    Returns a download link for the exported dataset
    """
    try:
        # This is a placeholder - in production, implement actual export logic
        raise HTTPException(
            status_code=501,
            detail="Export functionality not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{name}/annotation/images")
async def get_annotation_images(name: str, split: str = "train"):
    """
    Get list of images for annotation
    
    Returns images with their annotation status
    """
    try:
        dataset_info = dataset_service.get_dataset_info(name)
        images_dir = Path(dataset_info["path"]) / "images" / split
        labels_dir = Path(dataset_info["path"]) / "labels" / split
        
        if not images_dir.exists():
            raise HTTPException(status_code=404, detail=f"Images directory not found for {split} split")
        
        images = []
        for img_path in images_dir.glob("*"):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                # Check if annotation exists
                label_path = labels_dir / f"{img_path.stem}.txt"
                has_annotation = label_path.exists() and label_path.stat().st_size > 0
                
                images.append({
                    "filename": img_path.name,
                    "path": f"/uploads/datasets/{name}/images/{split}/{img_path.name}",
                    "has_annotation": has_annotation
                })
        
        return {
            "dataset_name": name,
            "split": split,
            "total_images": len(images),
            "annotated": sum(1 for img in images if img["has_annotation"]),
            "images": images
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get annotation images: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{name}/annotation/save")
async def save_annotation(
    name: str,
    filename: str = Form(...),
    split: str = Form("train"),
    annotations: str = Form(...)  # JSON string of bounding boxes
):
    """
    Save annotations for an image
    
    annotations format: [{"class_id": 0, "x_center": 0.5, "y_center": 0.5, "width": 0.3, "height": 0.4}, ...]
    """
    try:
        import json
        
        dataset_info = dataset_service.get_dataset_info(name)
        labels_dir = Path(dataset_info["path"]) / "labels" / split
        labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse annotations
        boxes = json.loads(annotations)
        
        # Save to train, val, and test splits (for small datasets)
        dataset_path = Path(dataset_info["path"])
        saved_paths = []
        
        for split_name in ["train", "val", "test"]:
            split_labels_dir = dataset_path / "labels" / split_name
            split_labels_dir.mkdir(parents=True, exist_ok=True)
            
            label_path = split_labels_dir / f"{Path(filename).stem}.txt"
            
            with open(label_path, 'w') as f:
                for box in boxes:
                    # YOLO format: class_id x_center y_center width height (normalized 0-1)
                    f.write(f"{box['class_id']} {box['x_center']} {box['y_center']} {box['width']} {box['height']}\n")
            
            saved_paths.append(str(label_path))
        
        logger.info(f"Saved {len(boxes)} annotations for {filename} in train/val/test splits of dataset {name}")
        
        return {
            "success": True,
            "filename": filename,
            "num_annotations": len(boxes),
            "splits_saved": ["train", "val", "test"],
            "label_paths": saved_paths
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid annotations format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save annotation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
