"""
Local filesystem storage adapter
"""
import shutil
from pathlib import Path
from typing import List, Dict, Any
from .base import StorageAdapter
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LocalStorageAdapter(StorageAdapter):
    """Local filesystem storage"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or settings.DATASETS_DIR
    
    async def list_files(self, folder_path: str) -> List[Dict[str, Any]]:
        """List files in a local folder"""
        full_path = self.base_path / folder_path
        if not full_path.exists():
            return []
        
        files = []
        for item in full_path.rglob("*"):
            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_path)),
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                    "type": "file"
                })
        return files
    
    async def download_file(self, file_path: str, destination: Path) -> Path:
        """Copy file to destination"""
        source = self.base_path / file_path
        if not source.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return destination
    
    async def upload_file(self, file_path: Path, destination: str) -> str:
        """Copy file from local path to storage"""
        dest_path = self.base_path / destination
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dest_path)
        return destination
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    async def create_folder(self, folder_path: str) -> str:
        """Create a folder"""
        full_path = self.base_path / folder_path
        full_path.mkdir(parents=True, exist_ok=True)
        return folder_path
    
    async def get_file_url(self, file_path: str) -> str:
        """Get local file URL"""
        return f"/uploads/{file_path}"
