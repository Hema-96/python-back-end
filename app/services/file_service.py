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
        # Initialize Supabase client with proper credentials
        try:
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize file storage service"
            )
    
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
        """Upload file to Supabase storage and return file path (not URL)"""
        try:
            # Validate file
            self.validate_file(file)
            
            # Read file content
            file_content = file.file.read()
            
            # Generate unique filename with folder structure
            filename = f"{folder}/{uuid.uuid4().hex}_{file.filename}"
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(settings.SUPABASE_BUCKET).upload(filename, file_content)
            
            # Check for upload errors
            if isinstance(response, dict) and response.get("error"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Supabase upload error: {response['error']['message']}"
                )
            
            logger.info(f"File uploaded successfully to Supabase: {filename}")
            return {
                "file_path": filename,
                "file_name": file.filename,
                "file_size": len(file_content),
                "content_type": file.content_type,
                "storage_type": "supabase",
                "bucket": settings.SUPABASE_BUCKET
            }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error during file upload: {str(e)}"
            )
    
    def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get signed URL for a file (for private storage access)"""
        try:
            # Create signed URL for private storage access
            response = self.supabase.storage.from_(settings.SUPABASE_BUCKET).create_signed_url(file_path, expires_in)
            
            if isinstance(response, dict) and response.get("error"):
                logger.error(f"Failed to create signed URL: {response['error']['message']}")
                return None
            
            # Extract the signed URL from the response
            if isinstance(response, dict) and response.get("signedURL"):
                signed_url = response["signedURL"]
                logger.info(f"Signed URL created successfully for: {file_path}")
                return signed_url
            else:
                logger.error(f"Unexpected response format from Supabase: {response}")
                return None
            
        except Exception as e:
            logger.error(f"Error creating signed URL: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Supabase storage"""
        try:
            # Delete from Supabase storage using the full path
            response = self.supabase.storage.from_(settings.SUPABASE_BUCKET).remove([file_path])
            
            if isinstance(response, dict) and response.get("error"):
                logger.error(f"Failed to delete from Supabase: {response['error']['message']}")
                return False
            
            logger.info(f"File deleted successfully from Supabase: {file_path}")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """Get signed URL for a file (deprecated - use get_signed_url instead)"""
        return self.get_signed_url(file_path) 