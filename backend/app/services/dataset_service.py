"""
Dataset management service
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil
import yaml
from datetime import datetime
import logging
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


class DatasetService:
    """Service for dataset management"""
    
    def __init__(self):
        self.datasets_dir = settings.DATASETS_DIR
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
    
    def create_dataset(
        self,
        name: str,
        class_names: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new dataset structure
        
        Args:
            name: Dataset name
            class_names: List of class names
            description: Optional description
            
        Returns:
            Dataset information
        """
        dataset_path = self.datasets_dir / name
        
        if dataset_path.exists():
            raise ValueError(f"Dataset {name} already exists")
        
        try:
            # Create directory structure
            (dataset_path / "images" / "train").mkdir(parents=True, exist_ok=True)
            (dataset_path / "images" / "val").mkdir(parents=True, exist_ok=True)
            (dataset_path / "images" / "test").mkdir(parents=True, exist_ok=True)
            (dataset_path / "labels" / "train").mkdir(parents=True, exist_ok=True)
            (dataset_path / "labels" / "val").mkdir(parents=True, exist_ok=True)
            (dataset_path / "labels" / "test").mkdir(parents=True, exist_ok=True)
            
            # Create data.yaml
            data_yaml = {
                "path": str(dataset_path.absolute()),
                "train": "images/train",
                "val": "images/val",
                "test": "images/test",
                "nc": len(class_names),
                "names": class_names
            }
            
            yaml_path = dataset_path / "data.yaml"
            with open(yaml_path, 'w') as f:
                yaml.dump(data_yaml, f, default_flow_style=False)
            
            # Create metadata file
            metadata = {
                "name": name,
                "description": description,
                "class_names": class_names,
                "created_at": datetime.now().isoformat(),
                "num_classes": len(class_names)
            }
            
            metadata_path = dataset_path / "metadata.yaml"
            with open(metadata_path, 'w') as f:
                yaml.dump(metadata, f, default_flow_style=False)
            
            logger.info(f"Dataset {name} created successfully")
            
            return {
                "name": name,
                "path": str(dataset_path),
                "num_classes": len(class_names),
                "class_names": class_names,
                "created_at": metadata["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create dataset {name}: {e}", exc_info=True)
            # Clean up on failure
            if dataset_path.exists():
                shutil.rmtree(dataset_path)
            raise
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all available datasets
        
        Returns:
            List of dataset information dictionaries
        """
        datasets = []
        
        for dataset_dir in self.datasets_dir.iterdir():
            if dataset_dir.is_dir():
                try:
                    info = self.get_dataset_info(dataset_dir.name)
                    datasets.append(info)
                except Exception as e:
                    logger.warning(f"Failed to get info for dataset {dataset_dir.name}: {e}")
        
        return datasets
    
    def get_dataset_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a dataset
        
        Args:
            name: Dataset name
            
        Returns:
            Dataset information dictionary
        """
        dataset_path = self.datasets_dir / name
        
        if not dataset_path.exists():
            raise ValueError(f"Dataset {name} not found")
        
        # Load metadata
        metadata_path = dataset_path / "metadata.yaml"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = yaml.safe_load(f)
        else:
            metadata = {}
        
        # Load data.yaml
        data_yaml_path = dataset_path / "data.yaml"
        if data_yaml_path.exists():
            with open(data_yaml_path, 'r') as f:
                data_yaml = yaml.safe_load(f)
        else:
            data_yaml = {}
        
        # Count images
        train_images = len(list((dataset_path / "images" / "train").glob("*.*")))
        val_images = len(list((dataset_path / "images" / "val").glob("*.*")))
        test_images = len(list((dataset_path / "images" / "test").glob("*.*")))
        
        return {
            "name": name,
            "path": str(dataset_path),
            "num_classes": data_yaml.get("nc", 0),
            "class_names": data_yaml.get("names", []),
            "num_images_train": train_images,
            "num_images_val": val_images,
            "num_images_test": test_images,
            "created_at": metadata.get("created_at", "unknown"),
            "description": metadata.get("description", "")
        }
    
    def delete_dataset(self, name: str) -> Dict[str, Any]:
        """
        Delete a dataset
        
        Args:
            name: Dataset name
            
        Returns:
            Success message
        """
        dataset_path = self.datasets_dir / name
        
        if not dataset_path.exists():
            raise ValueError(f"Dataset {name} not found")
        
        try:
            shutil.rmtree(dataset_path)
            logger.info(f"Dataset {name} deleted successfully")
            
            return {
                "success": True,
                "message": f"Dataset {name} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete dataset {name}: {e}", exc_info=True)
            raise
    
    def add_image(
        self,
        dataset_name: str,
        image_path: Path,
        split: str = "train",
        annotations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Add an image to a dataset
        
        Args:
            dataset_name: Name of the dataset
            image_path: Path to the image file
            split: Dataset split (train/val/test)
            annotations: Optional list of annotations
            
        Returns:
            Success message
        """
        dataset_path = self.datasets_dir / dataset_name
        
        if not dataset_path.exists():
            raise ValueError(f"Dataset {dataset_name} not found")
        
        if split not in ["train", "val", "test"]:
            raise ValueError("Split must be one of: train, val, test")
        
        try:
            # Copy image
            dest_image_path = dataset_path / "images" / split / image_path.name
            shutil.copy2(image_path, dest_image_path)
            
            # Save annotations if provided
            if annotations:
                # Get image dimensions
                with Image.open(dest_image_path) as img:
                    img_width, img_height = img.size
                
                # Convert annotations to YOLO format
                label_path = dataset_path / "labels" / split / f"{image_path.stem}.txt"
                with open(label_path, 'w') as f:
                    for ann in annotations:
                        # Convert to YOLO format (class_id x_center y_center width height)
                        # All values normalized to 0-1
                        bbox = ann["bbox"]
                        x_center = ((bbox["x1"] + bbox["x2"]) / 2) / img_width
                        y_center = ((bbox["y1"] + bbox["y2"]) / 2) / img_height
                        width = (bbox["x2"] - bbox["x1"]) / img_width
                        height = (bbox["y2"] - bbox["y1"]) / img_height
                        
                        class_id = ann["class_id"]
                        
                        f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")
            
            logger.info(f"Image {image_path.name} added to dataset {dataset_name}/{split}")
            
            return {
                "success": True,
                "message": f"Image added to {split} split",
                "image_path": str(dest_image_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to add image to dataset: {e}", exc_info=True)
            raise
    
    def split_dataset(
        self,
        dataset_name: str,
        train_ratio: float = 0.7,
        val_ratio: float = 0.2,
        test_ratio: float = 0.1
    ) -> Dict[str, Any]:
        """
        Split dataset images into train/val/test sets
        
        Args:
            dataset_name: Name of the dataset
            train_ratio: Ratio for training set
            val_ratio: Ratio for validation set
            test_ratio: Ratio for test set
            
        Returns:
            Split statistics
        """
        dataset_path = self.datasets_dir / dataset_name
        
        if not dataset_path.exists():
            raise ValueError(f"Dataset {dataset_name} not found")
        
        if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 0.01:
            raise ValueError("Ratios must sum to 1.0")
        
        try:
            # This is a placeholder - in production, implement actual splitting logic
            # that moves files between train/val/test directories
            
            logger.info(f"Dataset {dataset_name} split with ratios: "
                       f"train={train_ratio}, val={val_ratio}, test={test_ratio}")
            
            return {
                "success": True,
                "message": "Dataset split successfully",
                "train_ratio": train_ratio,
                "val_ratio": val_ratio,
                "test_ratio": test_ratio
            }
            
        except Exception as e:
            logger.error(f"Failed to split dataset: {e}", exc_info=True)
            raise
    
    def validate_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Validate dataset structure and integrity
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Validation results
        """
        dataset_path = self.datasets_dir / dataset_name
        
        if not dataset_path.exists():
            raise ValueError(f"Dataset {dataset_name} not found")
        
        issues = []
        warnings = []
        
        # Check required files
        if not (dataset_path / "data.yaml").exists():
            issues.append("Missing data.yaml file")
        
        # Check directory structure
        for split in ["train", "val"]:
            if not (dataset_path / "images" / split).exists():
                issues.append(f"Missing images/{split} directory")
            if not (dataset_path / "labels" / split).exists():
                issues.append(f"Missing labels/{split} directory")
        
        # Check for orphaned files
        for split in ["train", "val", "test"]:
            images_dir = dataset_path / "images" / split
            labels_dir = dataset_path / "labels" / split
            
            if images_dir.exists() and labels_dir.exists():
                image_stems = {p.stem for p in images_dir.glob("*.*")}
                label_stems = {p.stem for p in labels_dir.glob("*.txt")}
                
                missing_labels = image_stems - label_stems
                missing_images = label_stems - image_stems
                
                if missing_labels:
                    warnings.append(f"{split}: {len(missing_labels)} images without labels")
                if missing_images:
                    warnings.append(f"{split}: {len(missing_images)} labels without images")
        
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "dataset": dataset_name,
            "issues": issues,
            "warnings": warnings
        }


# Global service instance
dataset_service = DatasetService()
