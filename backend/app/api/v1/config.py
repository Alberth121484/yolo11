"""
Configuration endpoints for storage and settings
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from app.auth.jwt import get_current_user
from app.services.storage.factory import StorageFactory
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory config storage (replace with database in production)
user_configs = {}


class StorageConfig(BaseModel):
    type: Literal["local", "google_drive", "onedrive"]
    credentials: Optional[Dict[str, Any]] = None


class UserConfig(BaseModel):
    storage: StorageConfig
    training_defaults: Optional[Dict[str, Any]] = None


@router.get("/storage")
async def get_storage_config(current_user: dict = Depends(get_current_user)):
    """Get current storage configuration"""
    user_id = current_user.get("sub")
    config = user_configs.get(user_id, {}).get("storage")
    
    if not config:
        # Return default local storage
        return StorageConfig(type="local", credentials=None)
    
    return config


@router.post("/storage")
async def save_storage_config(
    config: StorageConfig,
    current_user: dict = Depends(get_current_user)
):
    """Save storage configuration"""
    user_id = current_user.get("sub")
    
    # Validate configuration by trying to create adapter
    try:
        adapter = StorageFactory.create_adapter(config.dict())
        logger.info(f"Storage adapter validated: {config.type}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid storage configuration: {str(e)}")
    
    # Save configuration
    if user_id not in user_configs:
        user_configs[user_id] = {}
    
    user_configs[user_id]["storage"] = config.dict()
    
    return {"message": "Storage configuration saved successfully", "config": config}


@router.delete("/storage")
async def reset_storage_config(current_user: dict = Depends(get_current_user)):
    """Reset storage configuration to default (local)"""
    user_id = current_user.get("sub")
    
    if user_id in user_configs and "storage" in user_configs[user_id]:
        del user_configs[user_id]["storage"]
    
    return {"message": "Storage configuration reset to local"}


@router.post("/storage/test")
async def test_storage_connection(
    config: StorageConfig,
    current_user: dict = Depends(get_current_user)
):
    """Test storage connection"""
    try:
        adapter = StorageFactory.create_adapter(config.dict())
        
        # Try to list files in root
        files = await adapter.list_files("/")
        
        return {
            "success": True,
            "message": "Connection successful",
            "files_count": len(files)
        }
    except Exception as e:
        logger.error(f"Storage test failed: {e}")
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@router.get("/training-defaults")
async def get_training_defaults(current_user: dict = Depends(get_current_user)):
    """Get default training parameters"""
    user_id = current_user.get("sub")
    defaults = user_configs.get(user_id, {}).get("training_defaults", {})
    
    # Return defaults
    return {
        "epochs": defaults.get("epochs", 50),
        "batch_size": defaults.get("batch_size", 16),
        "image_size": defaults.get("image_size", 640),
        "model_size": defaults.get("model_size", "n")
    }


@router.post("/training-defaults")
async def save_training_defaults(
    defaults: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Save default training parameters"""
    user_id = current_user.get("sub")
    
    if user_id not in user_configs:
        user_configs[user_id] = {}
    
    user_configs[user_id]["training_defaults"] = defaults
    
    return {"message": "Training defaults saved successfully", "defaults": defaults}
