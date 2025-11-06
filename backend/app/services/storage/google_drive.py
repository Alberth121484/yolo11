"""
Google Drive storage adapter
"""
from pathlib import Path
from typing import List, Dict, Any
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from .base import StorageAdapter
import logging

logger = logging.getLogger(__name__)


class GoogleDriveAdapter(StorageAdapter):
    """Google Drive storage"""
    
    def __init__(self, credentials_dict: Dict[str, Any]):
        """
        Initialize with OAuth2 credentials
        credentials_dict should contain: token, refresh_token, token_uri, client_id, client_secret
        """
        self.credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret')
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    async def list_files(self, folder_path: str) -> List[Dict[str, Any]]:
        """List files in Google Drive folder"""
        try:
            # Find folder by path
            folder_id = await self._get_folder_id_by_path(folder_path)
            
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = []
            for item in results.get('files', []):
                files.append({
                    "name": item['name'],
                    "path": f"{folder_path}/{item['name']}",
                    "id": item['id'],
                    "size": int(item.get('size', 0)) if 'size' in item else 0,
                    "modified": item['modifiedTime'],
                    "type": "folder" if item['mimeType'] == 'application/vnd.google-apps.folder' else "file"
                })
            return files
        except Exception as e:
            logger.error(f"Error listing Google Drive files: {e}")
            return []
    
    async def download_file(self, file_id: str, destination: Path) -> Path:
        """Download file from Google Drive"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            with open(destination, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    logger.info(f"Download {int(status.progress() * 100)}%.")
            
            return destination
        except Exception as e:
            logger.error(f"Error downloading from Google Drive: {e}")
            raise
    
    async def upload_file(self, file_path: Path, destination: str) -> str:
        """Upload file to Google Drive"""
        try:
            folder_id = await self._get_or_create_folder(destination)
            
            file_metadata = {
                'name': file_path.name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(str(file_path), resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {e}")
            raise
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting from Google Drive: {e}")
            return False
    
    async def create_folder(self, folder_path: str) -> str:
        """Create folder in Google Drive"""
        folder_id = await self._get_or_create_folder(folder_path)
        return folder_id
    
    async def get_file_url(self, file_id: str) -> str:
        """Get Google Drive file URL"""
        return f"https://drive.google.com/file/d/{file_id}/view"
    
    async def _get_folder_id_by_path(self, folder_path: str) -> str:
        """Get folder ID by path"""
        # Start from root
        parent_id = 'root'
        
        if folder_path and folder_path != '/':
            parts = folder_path.strip('/').split('/')
            for part in parts:
                query = f"name='{part}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(q=query, fields="files(id)").execute()
                folders = results.get('files', [])
                
                if not folders:
                    # Folder doesn't exist
                    return None
                parent_id = folders[0]['id']
        
        return parent_id
    
    async def _get_or_create_folder(self, folder_path: str) -> str:
        """Get or create folder by path"""
        parent_id = 'root'
        
        if folder_path and folder_path != '/':
            parts = folder_path.strip('/').split('/')
            for part in parts:
                query = f"name='{part}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(q=query, fields="files(id)").execute()
                folders = results.get('files', [])
                
                if not folders:
                    # Create folder
                    file_metadata = {
                        'name': part,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [parent_id]
                    }
                    folder = self.service.files().create(body=file_metadata, fields='id').execute()
                    parent_id = folder.get('id')
                else:
                    parent_id = folders[0]['id']
        
        return parent_id
