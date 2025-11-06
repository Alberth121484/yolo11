"""
Base storage adapter interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, BinaryIO
from pathlib import Path


class StorageAdapter(ABC):
    """Base class for storage adapters"""
    
    @abstractmethod
    async def list_files(self, folder_path: str) -> List[Dict[str, Any]]:
        """List files in a folder"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str, destination: Path) -> Path:
        """Download a file"""
        pass
    
    @abstractmethod
    async def upload_file(self, file_path: Path, destination: str) -> str:
        """Upload a file"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        pass
    
    @abstractmethod
    async def create_folder(self, folder_path: str) -> str:
        """Create a folder"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file"""
        pass
