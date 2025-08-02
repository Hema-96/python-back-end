import os
import uuid
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, UploadFile
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate file type and size"""
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        # Check file size (read first chunk to check)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size {file_size} bytes exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        return True
    
    def upload_file(self, file: UploadFile, folder: str = "college-documents") -> Dict[str, Any]:
        """Upload file to Supabase storage"""
        try:
            # Validate file
            self.validate_file(file)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"{folder}/{unique_filename}"
            
            # Read file content
            file_content = file.file.read()
            
            # Upload to Supabase storage
            result = self.supabase.storage.from_("college-documents").upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
            
            if result:
                # Get public URL
                public_url = self.supabase.storage.from_("college-documents").get_public_url(unique_filename)
                
                logger.info(f"File uploaded successfully: {file_path}")
                return {
                    "file_path": file_path,
                    "file_url": public_url,
                    "file_name": file.filename,
                    "file_size": len(file_content),
                    "content_type": file.content_type
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload file to storage"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during file upload"
            )
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Supabase storage"""
        try:
            # Extract filename from path
            filename = os.path.basename(file_path)
            
            # Delete from Supabase storage
            result = self.supabase.storage.from_("college-documents").remove([filename])
            
            if result:
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"Failed to delete file: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """Get public URL for a file"""
        try:
            filename = os.path.basename(file_path)
            return self.supabase.storage.from_("college-documents").get_public_url(filename)
        except Exception as e:
            logger.error(f"Error getting file URL: {e}")
            return None 