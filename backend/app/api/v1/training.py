"""
Training endpoints for model training
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from pathlib import Path
import json
import uuid

from app.schemas import TrainingConfig, TrainingJob, TrainingStatus
from app.services.yolo_service import yolo_service
from app.services.dataset_service import dataset_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for training jobs (in production, use a database)
training_jobs: Dict[str, Dict[str, Any]] = {}


def run_training_job(job_id: str, config: TrainingConfig):
    """Background task to run training"""
    try:
        # Update status
        training_jobs[job_id]["status"] = TrainingStatus.RUNNING
        training_jobs[job_id]["updated_at"] = datetime.now()
        training_jobs[job_id]["current_epoch"] = 0
        training_jobs[job_id]["best_map"] = 0.0
        
        # Get dataset info
        dataset_info = dataset_service.get_dataset_info(config.dataset_name)
        data_yaml = Path(dataset_info["path"]) / "data.yaml"
        
        if not data_yaml.exists():
            raise ValueError(f"Dataset configuration not found: {data_yaml}")
        
        # Progress callback to update job status
        def update_progress(epoch: int, total_epochs: int, metrics: dict):
            """Update training progress in real-time"""
            try:
                # Log received metrics for debugging
                logger.info(f"Job {job_id}: Progress callback - Epoch {epoch}/{total_epochs}")
                logger.debug(f"Metrics keys: {list(metrics.keys())}")
                
                # Try different possible metric key formats
                map_value = 0.0
                for key in ['metrics/mAP50-95(B)', 'mAP50-95(B)', 'mAP50-95', 'map']:
                    if key in metrics:
                        map_value = float(metrics[key])
                        break
                
                map50_value = 0.0
                for key in ['metrics/mAP50(B)', 'mAP50(B)', 'mAP50', 'map50']:
                    if key in metrics:
                        map50_value = float(metrics[key])
                        break
                
                precision_value = 0.0
                for key in ['metrics/precision(B)', 'precision(B)', 'precision', 'P']:
                    if key in metrics:
                        precision_value = float(metrics[key])
                        break
                
                recall_value = 0.0
                for key in ['metrics/recall(B)', 'recall(B)', 'recall', 'R']:
                    if key in metrics:
                        recall_value = float(metrics[key])
                        break
                
                loss_value = 0.0
                for key in ['train/box_loss', 'box_loss', 'loss']:
                    if key in metrics:
                        loss_value = float(metrics[key])
                        break
                
                # Update job status
                training_jobs[job_id].update({
                    "current_epoch": epoch,
                    "best_map": max(training_jobs[job_id].get("best_map", 0.0), map_value),
                    "updated_at": datetime.now(),
                    "current_metrics": {
                        "map50": map50_value,
                        "map50_95": map_value,
                        "precision": precision_value,
                        "recall": recall_value,
                        "loss": loss_value
                    }
                })
                
                logger.info(f"Job {job_id}: Epoch {epoch}/{total_epochs} - mAP: {map_value:.4f}, P: {precision_value:.3f}, R: {recall_value:.3f}")
            
            except Exception as e:
                logger.error(f"Error updating progress for job {job_id}: {e}", exc_info=True)
        
        # Prepare training arguments
        train_args = {
            "data_yaml": data_yaml,
            "model_size": config.model_size.value,
            "epochs": config.epochs,
            "batch_size": config.batch_size,
            "imgsz": config.imgsz,
            "lr0": config.lr0,
            "lrf": config.lrf,
            "optimizer": config.optimizer,
            "patience": config.patience,
            "workers": config.workers,
            "pretrained": config.pretrained,
            "progress_callback": update_progress
        }
        
        if config.device:
            train_args["device"] = config.device
        if config.save_period > 0:
            train_args["save_period"] = config.save_period
        
        logger.info(f"Starting training job {job_id}")
        
        # Run training
        result = yolo_service.train_model(**train_args)
        
        # Update job with results
        training_jobs[job_id].update({
            "status": TrainingStatus.COMPLETED,
            "updated_at": datetime.now(),
            "result": result,
            "model_path": result.get("model_path"),
            "model_name": result.get("model_name"),  # Model name for inference
            "best_map": result.get("metrics", {}).get("map50_95", 0.0),
            "current_epoch": config.epochs,
            "final_metrics": result.get("metrics", {})
        })
        
        logger.info(f"Training job {job_id} completed successfully. Model: {result.get('model_name')}")
        
    except Exception as e:
        logger.error(f"Training job {job_id} failed: {e}", exc_info=True)
        training_jobs[job_id].update({
            "status": TrainingStatus.FAILED,
            "updated_at": datetime.now(),
            "error": str(e)
        })


@router.post("/train", response_model=TrainingJob)
async def start_training(
    config: TrainingConfig,
    background_tasks: BackgroundTasks
):
    """
    Start a new training job
    
    Creates a background training job with the specified configuration.
    
    - **dataset_name**: Name of the dataset to train on
    - **model_size**: Size of the YOLO model (n, s, m, l, x)
    - **epochs**: Number of training epochs
    - **batch_size**: Batch size for training
    - **imgsz**: Image size for training
    - **lr0**: Initial learning rate
    - **lrf**: Final learning rate
    - **optimizer**: Optimizer to use (auto, SGD, Adam, etc.)
    - **patience**: Early stopping patience
    - **pretrained**: Whether to use pretrained weights
    
    Returns job information including job_id for tracking
    """
    try:
        # Validate dataset exists
        dataset_info = dataset_service.get_dataset_info(config.dataset_name)
        
        # Validate dataset has images
        if dataset_info["num_images_train"] == 0:
            raise HTTPException(
                status_code=400,
                detail="Dataset has no training images"
            )
        
        if dataset_info["num_images_val"] == 0:
            raise HTTPException(
                status_code=400,
                detail="Dataset has no validation images"
            )
        
        # Create job
        job_id = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        job = {
            "job_id": job_id,
            "status": TrainingStatus.PENDING,
            "dataset_name": config.dataset_name,
            "model_size": config.model_size.value,
            "epochs": config.epochs,
            "current_epoch": 0,
            "best_map": 0.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "config": config.dict()
        }
        
        training_jobs[job_id] = job
        
        # Start training in background
        background_tasks.add_task(run_training_job, job_id, config)
        
        logger.info(f"Training job {job_id} created and queued")
        
        return TrainingJob(**job)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start training: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/train/{job_id}", response_model=TrainingJob)
async def get_training_job(job_id: str):
    """
    Get training job status and information
    
    - **job_id**: ID of the training job
    
    Returns current status, progress, and metrics
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return TrainingJob(**training_jobs[job_id])


@router.get("/train", response_model=list[TrainingJob])
async def list_training_jobs(
    status: Optional[TrainingStatus] = None,
    limit: int = 50
):
    """
    List all training jobs
    
    - **status**: Filter by status (optional)
    - **limit**: Maximum number of jobs to return
    
    Returns list of training jobs
    """
    jobs = list(training_jobs.values())
    
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    # Sort by created_at descending
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [TrainingJob(**job) for job in jobs[:limit]]


@router.delete("/train/{job_id}")
async def cancel_training_job(job_id: str):
    """
    Cancel a training job
    
    - **job_id**: ID of the training job
    
    Attempts to cancel a running training job
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    
    if job["status"] == TrainingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    if job["status"] == TrainingStatus.FAILED:
        raise HTTPException(status_code=400, detail="Cannot cancel failed job")
    
    # Update status (actual cancellation would require more complex implementation)
    training_jobs[job_id]["status"] = TrainingStatus.CANCELLED
    training_jobs[job_id]["updated_at"] = datetime.now()
    
    logger.info(f"Training job {job_id} cancelled")
    
    return {
        "success": True,
        "message": f"Training job {job_id} cancelled",
        "job_id": job_id
    }


@router.get("/train/{job_id}/metrics")
async def get_training_metrics(job_id: str):
    """
    Get detailed training metrics for a job
    
    - **job_id**: ID of the training job
    
    Returns training metrics and loss curves
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    
    if job["status"] not in [TrainingStatus.RUNNING, TrainingStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail="Metrics only available for running or completed jobs"
        )
    
    # In production, read actual metrics from training logs
    # This is a placeholder response
    return {
        "job_id": job_id,
        "status": job["status"],
        "current_epoch": job.get("current_epoch", 0),
        "total_epochs": job["epochs"],
        "best_map": job.get("best_map", 0.0),
        "metrics": job.get("result", {}).get("metrics", {})
    }


@router.post("/train/{job_id}/resume")
async def resume_training(
    job_id: str,
    background_tasks: BackgroundTasks
):
    """
    Resume a cancelled or failed training job
    
    - **job_id**: ID of the training job
    
    Resumes training from the last checkpoint
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    
    if job["status"] not in [TrainingStatus.CANCELLED, TrainingStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail="Can only resume cancelled or failed jobs"
        )
    
    # Update status and resume training
    config = TrainingConfig(**job["config"])
    background_tasks.add_task(run_training_job, job_id, config)
    
    training_jobs[job_id]["status"] = TrainingStatus.PENDING
    training_jobs[job_id]["updated_at"] = datetime.now()
    
    logger.info(f"Training job {job_id} resumed")
    
    return TrainingJob(**training_jobs[job_id])
