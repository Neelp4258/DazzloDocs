import os
import time
import threading
import logging
from config import Config

logger = logging.getLogger(__name__)

class CleanupManager:
    """Manages automatic cleanup of old files"""
    
    def __init__(self):
        self.cleanup_interval = Config.CLEANUP_INTERVAL
        # Convert hours to seconds for file retention time
        self.file_retention_time = Config.FILE_RETENTION_HOURS * 3600
        self.upload_folder = Config.UPLOAD_FOLDER
        self.converted_folder = Config.CONVERTED_FOLDER
        self.cleanup_thread = None
        self.running = False
    
    def start_cleanup_thread(self):
        """Start the cleanup thread"""
        if self.cleanup_thread is None or not self.cleanup_thread.is_alive():
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            logger.info("Cleanup thread started")
    
    def stop_cleanup_thread(self):
        """Stop the cleanup thread"""
        self.running = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
            logger.info("Cleanup thread stopped")
    
    def _cleanup_loop(self):
        """Main cleanup loop"""
        while self.running:
            try:
                self._cleanup_old_files()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _cleanup_old_files(self):
        """Clean up old files from upload and converted folders"""
        try:
            current_time = time.time()
            deleted_count = 0
            
            for folder in [self.upload_folder, self.converted_folder]:
                if not os.path.exists(folder):
                    continue
                
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        # Check file age
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > self.file_retention_time:
                            if self._delete_file_safely(file_path):
                                deleted_count += 1
                    except OSError:
                        # File might have been deleted by another process
                        continue
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old files")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _delete_file_safely(self, file_path: str) -> bool:
        """Safely delete a file"""
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def cleanup_now(self) -> int:
        """Trigger immediate cleanup and return number of deleted files"""
        try:
            current_time = time.time()
            deleted_count = 0
            
            for folder in [self.upload_folder, self.converted_folder]:
                if not os.path.exists(folder):
                    continue
                
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > self.file_retention_time:
                            if self._delete_file_safely(file_path):
                                deleted_count += 1
                    except OSError:
                        continue
            
            if deleted_count > 0:
                logger.info(f"Manual cleanup: deleted {deleted_count} files")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during manual cleanup: {e}")
            return 0
    
    def schedule_cleanup(self, file_path: str):
        """Schedule a file for cleanup (this is handled by the cleanup loop)"""
        # The cleanup loop will automatically handle files based on their modification time
        logger.debug(f"File scheduled for cleanup: {file_path}") 