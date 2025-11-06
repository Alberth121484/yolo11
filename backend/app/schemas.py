"""
Pydantic schemas for request/response models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class TaskType(str, Enum):
    DETECT = "detect"
    SEGMENT = "segment"
    CLASSIFY = "classify"
    POSE = "pose"
    OBB = "obb"


class TrainingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelSize(str, Enum):
    NANO = "n"
    SMALL = "s"
    MEDIUM = "m"
    LARGE = "l"
    XLARGE = "x"


# Detection schemas
class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "x1": 100.5,
                "y1": 200.3,
                "x2": 300.7,
                "y2": 400.9
            }
        }


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    
    class Config:
        json_schema_extra = {
            "example": {
                "class_id": 0,
                "class_name": "person",
                "confidence": 0.95,
                "bbox": {
                    "x1": 100.5,
                    "y1": 200.3,
                    "x2": 300.7,
                    "y2": 400.9
                }
            }
        }


class InferenceRequest(BaseModel):
    model_name: Optional[str] = Field(None, description="Model to use for inference")
    confidence: Optional[float] = Field(0.25, ge=0.0, le=1.0, description="Confidence threshold")
    iou: Optional[float] = Field(0.45, ge=0.0, le=1.0, description="IoU threshold for NMS")
    max_det: Optional[int] = Field(300, ge=1, description="Maximum detections per image")
    imgsz: Optional[int] = Field(640, description="Image size for inference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "yolo11n.pt",
                "confidence": 0.25,
                "iou": 0.45,
                "max_det": 300,
                "imgsz": 640
            }
        }


class InferenceResponse(BaseModel):
    success: bool
    image_path: str
    result_path: Optional[str] = None
    detections: List[Detection]
    inference_time: float
    image_size: List[int]
    model_used: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "image_path": "/uploads/image.jpg",
                "result_path": "/results/image_result.jpg",
                "detections": [
                    {
                        "class_id": 0,
                        "class_name": "person",
                        "confidence": 0.95,
                        "bbox": {"x1": 100.5, "y1": 200.3, "x2": 300.7, "y2": 400.9}
                    }
                ],
                "inference_time": 0.15,
                "image_size": [640, 480],
                "model_used": "yolo11n.pt"
            }
        }


class BatchInferenceResponse(BaseModel):
    success: bool
    results: List[InferenceResponse]
    total_images: int
    total_detections: int
    average_inference_time: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "results": [],
                "total_images": 5,
                "total_detections": 15,
                "average_inference_time": 0.18
            }
        }


# Training schemas
class TrainingConfig(BaseModel):
    dataset_name: str = Field(..., description="Name of the dataset to train on")
    model_size: ModelSize = Field(ModelSize.NANO, description="Size of the model")
    epochs: int = Field(100, ge=1, description="Number of training epochs")
    batch_size: int = Field(16, ge=1, description="Batch size for training")
    imgsz: int = Field(640, description="Image size for training")
    lr0: float = Field(0.01, gt=0, description="Initial learning rate")
    lrf: float = Field(0.01, gt=0, description="Final learning rate")
    optimizer: str = Field("auto", description="Optimizer to use")
    patience: int = Field(50, ge=1, description="Patience for early stopping")
    save_period: int = Field(-1, description="Save checkpoint every n epochs")
    pretrained: bool = Field(True, description="Use pretrained weights")
    device: Optional[str] = Field(None, description="Device to train on (cuda/cpu/mps)")
    workers: int = Field(8, ge=1, description="Number of data loader workers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_name": "my_dataset",
                "model_size": "n",
                "epochs": 100,
                "batch_size": 16,
                "imgsz": 640,
                "lr0": 0.01,
                "lrf": 0.01,
                "optimizer": "auto",
                "patience": 50,
                "pretrained": True
            }
        }


class TrainingJob(BaseModel):
    job_id: str
    status: TrainingStatus
    dataset_name: str
    model_size: str
    epochs: int
    current_epoch: int = 0
    best_map: float = 0.0
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any]
    error: Optional[str] = None  # Error message if training failed
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "train_20240101_123456",
                "status": "running",
                "dataset_name": "my_dataset",
                "model_size": "n",
                "epochs": 100,
                "current_epoch": 50,
                "best_map": 0.85,
                "created_at": "2024-01-01T12:34:56",
                "updated_at": "2024-01-01T13:00:00",
                "config": {}
            }
        }


class TrainingMetrics(BaseModel):
    epoch: int
    train_loss: float
    val_loss: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    map50: Optional[float] = None
    map50_95: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "epoch": 50,
                "train_loss": 0.25,
                "val_loss": 0.30,
                "precision": 0.85,
                "recall": 0.80,
                "map50": 0.88,
                "map50_95": 0.75
            }
        }


# Dataset schemas
class DatasetInfo(BaseModel):
    name: str
    path: str
    num_classes: int
    class_names: List[str]
    num_images_train: int
    num_images_val: int
    num_images_test: Optional[int] = 0
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "my_dataset",
                "path": "/datasets/my_dataset",
                "num_classes": 3,
                "class_names": ["class1", "class2", "class3"],
                "num_images_train": 100,
                "num_images_val": 20,
                "num_images_test": 10,
                "created_at": "2024-01-01T12:00:00"
            }
        }


class CreateDatasetRequest(BaseModel):
    name: str = Field(..., description="Dataset name")
    class_names: List[str] = Field(..., description="List of class names")
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Dataset name must be alphanumeric (underscores and hyphens allowed)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "my_custom_dataset",
                "class_names": ["person", "car", "dog"],
                "description": "My custom object detection dataset"
            }
        }


class AnnotationFormat(str, Enum):
    YOLO = "yolo"
    COCO = "coco"
    PASCAL_VOC = "pascal_voc"


class ImageAnnotation(BaseModel):
    class_id: int
    bbox: BoundingBox
    
    class Config:
        json_schema_extra = {
            "example": {
                "class_id": 0,
                "bbox": {"x1": 100, "y1": 200, "x2": 300, "y2": 400}
            }
        }


# Model schemas
class ModelInfo(BaseModel):
    name: str
    path: str
    size: str
    task: TaskType
    num_classes: int
    class_names: List[str]
    trained_on: Optional[str] = None
    created_at: datetime
    file_size_mb: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "yolo11n_custom.pt",
                "path": "/models/yolo11n_custom.pt",
                "size": "n",
                "task": "detect",
                "num_classes": 80,
                "class_names": ["person", "car", "..."],
                "trained_on": "coco",
                "created_at": "2024-01-01T12:00:00",
                "file_size_mb": 6.2
            }
        }


# Health schemas
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    yolo_available: bool
    cuda_available: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-01T12:00:00",
                "yolo_available": True,
                "cuda_available": True
            }
        }


# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Error occurred",
                "message": "Detailed error message"
            }
        }
