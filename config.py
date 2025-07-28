import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 500 * 1024 * 1024))  # 500MB
    
    # Server settings
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # File paths
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    CONVERTED_FOLDER = os.environ.get('CONVERTED_FOLDER', 'converted')
    
    # Universal supported file extensions
    ALLOWED_EXTENSIONS = {
        # Images
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'ico', 'svg',
        
        # Documents
        'pdf', 'txt', 'docx', 'doc', 'rtf', 'md', 'html', 'htm',
        
        # Spreadsheets
        'xlsx', 'xls', 'csv',
        
        # Presentations
        'pptx', 'ppt',
        
        # Data formats
        'json', 'xml',
        
        # Archives
        'zip', 'rar', '7z', 'tar', 'gz',
        
        # Audio
        'mp3', 'wav', 'flac', 'aac', 'ogg',
        
        # Video
        'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm',
        
        # Code files
        'py', 'js', 'html', 'css', 'php', 'java', 'cpp', 'c', 'cs', 'rb', 'go', 'rs',
        
        # Other common formats
        'log', 'ini', 'cfg', 'conf', 'yaml', 'yml', 'toml'
    }
    
    # Conversion settings
    IMAGE_QUALITY = int(os.environ.get('IMAGE_QUALITY', 85))
    IMAGE_MAX_DIMENSION = int(os.environ.get('IMAGE_MAX_DIMENSION', 2048))
    PDF_RESOLUTION = int(os.environ.get('PDF_RESOLUTION', 300))
    
    # Cleanup settings
    CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', 3600))  # 1 hour
    FILE_RETENTION_HOURS = int(os.environ.get('FILE_RETENTION_HOURS', 24))  # 24 hours
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'app.log' 