"""
Storage factory to create appropriate storage adapter
"""
from typing import Dict, Any
from .base import StorageAdapter
from .local import LocalStorageAdapter
from .google_drive import GoogleDriveAdapter
from .onedrive import OneDriveAdapter
import logging

logger = logging.getLogger(__name__)


class StorageFactory:
    """Factory to create storage adapters based on configuration"""
    
    @staticmethod
    def create_adapter(config: Dict[str, Any]) -> StorageAdapter:
        """
        Create storage adapter based on configuration
        
        Config format:
        {
            "type": "local" | "google_drive" | "onedrive",
            "credentials": {...}  # provider-specific credentials
        }
        """
        storage_type = config.get("type", "local")
        
        if storage_type == "local":
            return LocalStorageAdapter()
        
        elif storage_type == "google_drive":
            credentials = config.get("credentials", {})
            if not credentials:
                raise ValueError("Google Drive credentials are required")
            return GoogleDriveAdapter(credentials)
        
        elif storage_type == "onedrive":
            access_token = config.get("credentials", {}).get("access_token")
            if not access_token:
                raise ValueError("OneDrive access token is required")
            return OneDriveAdapter(access_token)
        
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
