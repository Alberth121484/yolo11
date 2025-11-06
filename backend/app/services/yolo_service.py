"""
YOLO model service for inference and training
"""
from ultralytics import YOLO
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime
import torch
import shutil

from app.config import settings

logger = logging.getLogger(__name__)


class YOLOService:
    """Service for YOLO model operations"""
    
    def __init__(self):
        self.models_cache = {}
        self.device = self._get_device()
        logger.info(f"YOLOService initialized with device: {self.device}")
    
    def _get_device(self) -> str:
        """Detect and return the best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def get_model(self, model_name: Optional[str] = None) -> YOLO:
        """
        Get or load a YOLO model
        
        Args:
            model_name: Name of the model file
            
        Returns:
            YOLO model instance
        """
        if model_name is None:
            model_name = settings.DEFAULT_MODEL
        
        # Check cache
        if model_name in self.models_cache:
            return self.models_cache[model_name]
        
        # Build model path
        model_path = settings.MODELS_DIR / model_name
        
        # If model doesn't exist locally, download it
        if not model_path.exists():
            logger.info(f"Model {model_name} not found locally, downloading...")
            try:
                model = YOLO(model_name)
                model.to(self.device)
            except Exception as e:
                logger.error(f"Failed to download model {model_name}: {e}")
                raise
        else:
            logger.info(f"Loading model from {model_path}")
            model = YOLO(str(model_path))
            model.to(self.device)
        
        # Cache the model
        self.models_cache[model_name] = model
        return model
    
    def predict(
        self,
        image_path: Path,
        model_name: Optional[str] = None,
        confidence: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        imgsz: int = 640,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Run inference on a single image
        
        Args:
            image_path: Path to the image
            model_name: Model to use
            confidence: Confidence threshold
            iou: IoU threshold for NMS
            max_det: Maximum detections
            imgsz: Image size
            save: Whether to save annotated image
            
        Returns:
            Dictionary with detection results
        """
        start_time = datetime.now()
        
        try:
            # Load model
            model = self.get_model(model_name)
            
            # Run inference
            results = model.predict(
                source=str(image_path),
                conf=confidence,
                iou=iou,
                max_det=max_det,
                imgsz=imgsz,
                save=save,
                project=str(settings.RESULTS_DIR),
                name=f"{image_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                exist_ok=True
            )
            
            # Process results
            result = results[0]
            detections = []
            
            for box in result.boxes:
                detection = {
                    "class_id": int(box.cls[0]),
                    "class_name": model.names[int(box.cls[0])],
                    "confidence": float(box.conf[0]),
                    "bbox": {
                        "x1": float(box.xyxy[0][0]),
                        "y1": float(box.xyxy[0][1]),
                        "x2": float(box.xyxy[0][2]),
                        "y2": float(box.xyxy[0][3])
                    }
                }
                detections.append(detection)
            
            # Get result image path
            result_path = None
            if save and result.save_dir:
                result_files = list(Path(result.save_dir).glob(f"{image_path.stem}.*"))
                if result_files:
                    result_path = result_files[0]
            
            inference_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "image_path": str(image_path),
                "result_path": str(result_path) if result_path else None,
                "detections": detections,
                "inference_time": inference_time,
                "image_size": list(result.orig_shape),
                "model_used": model_name or settings.DEFAULT_MODEL
            }
            
        except Exception as e:
            logger.error(f"Inference failed for {image_path}: {e}", exc_info=True)
            raise
    
    def predict_batch(
        self,
        image_paths: List[Path],
        model_name: Optional[str] = None,
        confidence: float = 0.25,
        iou: float = 0.45,
        max_det: int = 300,
        imgsz: int = 640,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Run inference on multiple images
        
        Args:
            image_paths: List of image paths
            model_name: Model to use
            confidence: Confidence threshold
            iou: IoU threshold for NMS
            max_det: Maximum detections
            imgsz: Image size
            save: Whether to save annotated images
            
        Returns:
            Dictionary with batch detection results
        """
        results = []
        total_detections = 0
        total_time = 0
        
        for image_path in image_paths:
            try:
                result = self.predict(
                    image_path=image_path,
                    model_name=model_name,
                    confidence=confidence,
                    iou=iou,
                    max_det=max_det,
                    imgsz=imgsz,
                    save=save
                )
                results.append(result)
                total_detections += len(result["detections"])
                total_time += result["inference_time"]
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {e}")
                results.append({
                    "success": False,
                    "image_path": str(image_path),
                    "error": str(e)
                })
        
        avg_time = total_time / len(image_paths) if image_paths else 0
        
        return {
            "success": True,
            "results": results,
            "total_images": len(image_paths),
            "total_detections": total_detections,
            "average_inference_time": avg_time
        }
    
    def train_model(
        self,
        data_yaml: Path,
        model_size: str = "n",
        epochs: int = 100,
        batch_size: int = 16,
        imgsz: int = 640,
        progress_callback: Optional[callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train a YOLO model
        
        Args:
            data_yaml: Path to data configuration YAML
            model_size: Size of model (n, s, m, l, x)
            epochs: Number of epochs
            batch_size: Batch size
            imgsz: Image size
            progress_callback: Callback function to update progress
            **kwargs: Additional training arguments
            
        Returns:
            Training results dictionary
        """
        try:
            # Initialize model
            model_name = f"yolo11{model_size}.pt"
            model = self.get_model(model_name)
            
            # Set up training directory
            project_dir = settings.RESULTS_DIR / "training"
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Add callback for progress updates
            if progress_callback:
                def on_fit_epoch_end(trainer):
                    """Called at the end of each epoch after validation"""
                    try:
                        # Ultralytics stores metrics in trainer.metrics dict after validation
                        epoch = trainer.epoch
                        metrics_dict = {}
                        
                        # Try to get metrics from trainer
                        if hasattr(trainer, 'metrics') and trainer.metrics:
                            metrics_dict = trainer.metrics
                        
                        # Also try validator metrics
                        if hasattr(trainer, 'validator') and hasattr(trainer.validator, 'metrics'):
                            val_metrics = trainer.validator.metrics
                            if hasattr(val_metrics, 'results_dict'):
                                metrics_dict.update(val_metrics.results_dict)
                        
                        # Log for debugging
                        logger.info(f"Epoch {epoch}/{epochs} callback - metrics keys: {list(metrics_dict.keys())}")
                        
                        # Call the progress callback
                        progress_callback(
                            epoch=epoch,
                            total_epochs=epochs,
                            metrics=metrics_dict
                        )
                    except Exception as e:
                        logger.error(f"Error in progress callback: {e}", exc_info=True)
                
                # Add callback to model - use on_fit_epoch_end which fires after validation
                model.add_callback('on_fit_epoch_end', on_fit_epoch_end)
            
            # Train
            logger.info(f"Starting training with {model_name} on {data_yaml}")
            results = model.train(
                data=str(data_yaml),
                epochs=epochs,
                batch=batch_size,
                imgsz=imgsz,
                project=str(project_dir),
                name=f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                device=self.device,
                exist_ok=True,
                **kwargs
            )
            
            logger.info("Training completed successfully")
            
            # Copy best model to models directory with a readable name
            best_model_path = results.save_dir / "weights" / "best.pt"
            if best_model_path.exists():
                # Create model name from dataset and timestamp
                model_filename = f"{data_yaml.parent.name}_yolo11{model_size}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                destination_path = settings.MODELS_DIR / model_filename
                
                # Copy the model
                shutil.copy2(best_model_path, destination_path)
                logger.info(f"Model copied to: {destination_path}")
                saved_model_path = str(destination_path)
            else:
                logger.warning("Best model not found, using save_dir path")
                saved_model_path = str(best_model_path)
            
            return {
                "success": True,
                "results": results,
                "model_path": saved_model_path,
                "model_name": model_filename if best_model_path.exists() else None,
                "metrics": {
                    "map50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
                    "map50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
                    "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
                    "recall": float(results.results_dict.get("metrics/recall(B)", 0))
                }
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            raise
    
    def validate_model(
        self,
        model_path: Path,
        data_yaml: Path,
        batch_size: int = 16,
        imgsz: int = 640
    ) -> Dict[str, Any]:
        """
        Validate a trained model
        
        Args:
            model_path: Path to model weights
            data_yaml: Path to data configuration
            batch_size: Batch size
            imgsz: Image size
            
        Returns:
            Validation results
        """
        try:
            model = YOLO(str(model_path))
            model.to(self.device)
            
            results = model.val(
                data=str(data_yaml),
                batch=batch_size,
                imgsz=imgsz,
                device=self.device
            )
            
            return {
                "success": True,
                "metrics": {
                    "map50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
                    "map50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
                    "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
                    "recall": float(results.results_dict.get("metrics/recall(B)", 0))
                }
            }
            
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise
    
    def export_model(
        self,
        model_path: Path,
        format: str = "onnx",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Export model to different formats
        
        Args:
            model_path: Path to model weights
            format: Export format (onnx, torchscript, coreml, etc.)
            **kwargs: Additional export arguments
            
        Returns:
            Export results
        """
        try:
            model = YOLO(str(model_path))
            
            export_path = model.export(format=format, **kwargs)
            
            return {
                "success": True,
                "format": format,
                "export_path": str(export_path)
            }
            
        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            raise
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary
        """
        try:
            model = self.get_model(model_name)
            
            return {
                "name": model_name,
                "task": model.task,
                "num_classes": len(model.names),
                "class_names": list(model.names.values()),
                "device": str(model.device)
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}", exc_info=True)
            raise


# Global service instance
yolo_service = YOLOService()
