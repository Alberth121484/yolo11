"""
OneDrive storage adapter using Microsoft Graph API
"""
from pathlib import Path
from typing import List, Dict, Any
import requests
from .base import StorageAdapter
import logging

logger = logging.getLogger(__name__)


class OneDriveAdapter(StorageAdapter):
    """OneDrive storage via Microsoft Graph API"""
    
    def __init__(self, access_token: str):
        """Initialize with Microsoft access token"""
        self.access_token = access_token
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def list_files(self, folder_path: str) -> List[Dict[str, Any]]:
        """List files in OneDrive folder"""
        try:
            # Clean path
            path = folder_path.strip('/')
            if path:
                url = f"{self.graph_url}/me/drive/root:/{path}:/children"
            else:
                url = f"{self.graph_url}/me/drive/root/children"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            files = []
            
            for item in data.get('value', []):
                files.append({
                    "name": item['name'],
                    "path": f"{folder_path}/{item['name']}",
                    "id": item['id'],
                    "size": item.get('size', 0),
                    "modified": item.get('lastModifiedDateTime'),
                    "type": "folder" if 'folder' in item else "file",
                    "download_url": item.get('@microsoft.graph.downloadUrl')
                })
            
            return files
        except Exception as e:
            logger.error(f"Error listing OneDrive files: {e}")
            return []
    
    async def download_file(self, file_id: str, destination: Path) -> Path:
        """Download file from OneDrive"""
        try:
            # Get download URL
            url = f"{self.graph_url}/me/drive/items/{file_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            download_url = response.json().get('@microsoft.graph.downloadUrl')
            
            # Download file
            response = requests.get(download_url)
            response.raise_for_status()
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, 'wb') as f:
                f.write(response.content)
            
            return destination
        except Exception as e:
            logger.error(f"Error downloading from OneDrive: {e}")
            raise
    
    async def upload_file(self, file_path: Path, destination: str) -> str:
        """Upload file to OneDrive"""
        try:
            # Clean path
            path = destination.strip('/')
            filename = file_path.name
            
            if path:
                url = f"{self.graph_url}/me/drive/root:/{path}/{filename}:/content"
            else:
                url = f"{self.graph_url}/me/drive/root:/{filename}:/content"
            
            with open(file_path, 'rb') as f:
                response = requests.put(url, headers=self.headers, data=f)
            
            response.raise_for_status()
            return response.json().get('id')
        except Exception as e:
            logger.error(f"Error uploading to OneDrive: {e}")
            raise
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from OneDrive"""
        try:
            url = f"{self.graph_url}/me/drive/items/{file_id}"
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error deleting from OneDrive: {e}")
            return False
    
    async def create_folder(self, folder_path: str) -> str:
        """Create folder in OneDrive"""
        try:
            # Split path into parent and folder name
            parts = folder_path.strip('/').split('/')
            folder_name = parts[-1]
            parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ''
            
            if parent_path:
                url = f"{self.graph_url}/me/drive/root:/{parent_path}:/children"
            else:
                url = f"{self.graph_url}/me/drive/root/children"
            
            data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            return response.json().get('id')
        except Exception as e:
            logger.error(f"Error creating OneDrive folder: {e}")
            raise
    
    async def get_file_url(self, file_id: str) -> str:
        """Get OneDrive file sharing URL"""
        try:
            url = f"{self.graph_url}/me/drive/items/{file_id}/createLink"
            data = {
                "type": "view",
                "scope": "anonymous"
            }
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            return response.json().get('link', {}).get('webUrl', '')
        except Exception as e:
            logger.error(f"Error getting OneDrive file URL: {e}")
            return ""
