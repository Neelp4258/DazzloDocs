import os
import shutil
import logging
from pathlib import Path
from werkzeug.datastructures import FileStorage
from config import Config

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for the application"""
    
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        self.converted_folder = Config.CONVERTED_FOLDER
        
        # Create directories if they don't exist
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.converted_folder, exist_ok=True)
    
    def save_uploaded_file(self, file: FileStorage, filename: str) -> str:
        """Save uploaded file to upload folder"""
        try:
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            logger.info(f"File saved: {filename}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving file {filename}: {e}")
            raise
    
    def get_output_path(self, filename: str) -> str:
        """Get full path for output file"""
        return os.path.join(self.converted_folder, filename)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file safely"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)
    
    def cleanup_old_files(self, max_age_seconds: int = None) -> int:
        """Clean up old files from both upload and converted folders"""
        if max_age_seconds is None:
            max_age_seconds = Config.FILE_RETENTION_TIME
        
        deleted_count = 0
        current_time = os.path.getmtime(__file__)  # Use current time
        
        for folder in [self.upload_folder, self.converted_folder]:
            try:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > max_age_seconds:
                            if self.delete_file(file_path):
                                deleted_count += 1
                    except OSError:
                        # File might have been deleted by another process
                        continue
            except OSError as e:
                logger.error(f"Error accessing folder {folder}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old files")
        
        return deleted_count 