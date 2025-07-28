import os
import logging
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

class FileValidator:
    """Validates uploaded files for safety and compatibility"""
    
    def __init__(self):
        # Universal supported formats - Expanded for maximum compatibility
        self.ALLOWED_EXTENSIONS = {
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
        
        # File size limits (in bytes) - Enhanced limits
        self.MAX_FILE_SIZES = {
            'images': 100 * 1024 * 1024,      # 100MB for images
            'documents': 200 * 1024 * 1024,   # 200MB for documents
            'spreadsheets': 100 * 1024 * 1024, # 100MB for spreadsheets
            'presentations': 200 * 1024 * 1024, # 200MB for presentations
            'data': 50 * 1024 * 1024,         # 50MB for data files
            'archives': 500 * 1024 * 1024,    # 500MB for archives
            'audio': 200 * 1024 * 1024,       # 200MB for audio
            'video': 1000 * 1024 * 1024,      # 1GB for video
            'code': 10 * 1024 * 1024,         # 10MB for code files
            'default': 500 * 1024 * 1024      # 500MB default
        }
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        
        extension = Path(filename).suffix[1:].lower()
        return extension in self.ALLOWED_EXTENSIONS
    
    def validate_file(self, file_path: str, original_filename: str = None) -> dict:
        """Comprehensive file validation"""
        try:
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': 'File does not exist',
                    'details': 'The uploaded file could not be found on the server.'
                }
            
            # Get file extension
            file_ext = Path(file_path).suffix[1:].lower()
            
            # Validate extension
            if file_ext not in self.ALLOWED_EXTENSIONS:
                return {
                    'valid': False,
                    'error': 'Unsupported file format',
                    'details': f'File format .{file_ext} is not supported. Supported formats: {", ".join(sorted(self.ALLOWED_EXTENSIONS))}'
                }
            
            # Validate file size
            file_size = os.path.getsize(file_path)
            max_size = self._get_max_size_for_format(file_ext)
            
            if file_size > max_size:
                return {
                    'valid': False,
                    'error': 'File too large',
                    'details': f'File size ({self._format_size(file_size)}) exceeds maximum allowed size ({self._format_size(max_size)})'
                }
            
            # Basic security checks
            security_check = self._validate_security(file_path)
            if not security_check['valid']:
                return security_check
            
            # Determine file category
            category = self._get_file_category(file_ext)
            
            return {
                'valid': True,
                'file_size': file_size,
                'file_size_formatted': self._format_size(file_size),
                'extension': file_ext,
                'category': category,
                'max_size': self._format_size(max_size)
            }
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return {
                'valid': False,
                'error': 'Validation error',
                'details': f'An error occurred during file validation: {str(e)}'
            }
    
    def _get_max_size_for_format(self, extension: str) -> int:
        """Get maximum file size for a given format"""
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'ico', 'svg']:
            return self.MAX_FILE_SIZES['images']
        elif extension in ['pdf', 'txt', 'docx', 'doc', 'rtf', 'md', 'html', 'htm']:
            return self.MAX_FILE_SIZES['documents']
        elif extension in ['xlsx', 'xls', 'csv']:
            return self.MAX_FILE_SIZES['spreadsheets']
        elif extension in ['pptx', 'ppt']:
            return self.MAX_FILE_SIZES['presentations']
        elif extension in ['json', 'xml']:
            return self.MAX_FILE_SIZES['data']
        elif extension in ['zip', 'rar', '7z', 'tar', 'gz']:
            return self.MAX_FILE_SIZES['archives']
        elif extension in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
            return self.MAX_FILE_SIZES['audio']
        elif extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']:
            return self.MAX_FILE_SIZES['video']
        elif extension in ['py', 'js', 'css', 'php', 'java', 'cpp', 'c', 'cs', 'rb', 'go', 'rs', 'log', 'ini', 'cfg', 'conf', 'yaml', 'yml', 'toml']:
            return self.MAX_FILE_SIZES['code']
        else:
            return self.MAX_FILE_SIZES['default']
    
    def _validate_security(self, file_path: str) -> dict:
        """Basic security validation"""
        try:
            # Check for null bytes in filename
            if '\x00' in os.path.basename(file_path):
                return {
                    'valid': False,
                    'error': 'Security violation',
                    'details': 'Filename contains invalid characters'
                }
            
            # Check for suspicious filename patterns
            filename = os.path.basename(file_path).lower()
            # More specific patterns to avoid false positives
            suspicious_patterns = [
                '..',  # Directory traversal
                '.cmd.', '.com.', '.bat.', '.exe.', '.dll.', '.vbs.', '.js.',  # Executable extensions
                'cmd.exe', 'command.com', 'autoexec.bat'  # Specific dangerous files
            ]
            
            for pattern in suspicious_patterns:
                if pattern in filename:
                    return {
                        'valid': False,
                        'error': 'Security violation',
                        'details': f'Filename contains suspicious pattern: {pattern}'
                    }
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"Security validation error: {str(e)}")
            return {
                'valid': False,
                'error': 'Security validation error',
                'details': f'Error during security validation: {str(e)}'
            }
    
    def _get_file_category(self, extension: str) -> str:
        """Get file category based on extension"""
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'ico', 'svg']:
            return 'image'
        elif extension in ['pdf', 'txt', 'docx', 'doc', 'rtf', 'md', 'html', 'htm']:
            return 'document'
        elif extension in ['xlsx', 'xls', 'csv']:
            return 'spreadsheet'
        elif extension in ['pptx', 'ppt']:
            return 'presentation'
        elif extension in ['json', 'xml']:
            return 'data'
        elif extension in ['zip', 'rar', '7z', 'tar', 'gz']:
            return 'archive'
        elif extension in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
            return 'audio'
        elif extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']:
            return 'video'
        elif extension in ['py', 'js', 'css', 'php', 'java', 'cpp', 'c', 'cs', 'rb', 'go', 'rs', 'log', 'ini', 'cfg', 'conf', 'yaml', 'yml', 'toml']:
            return 'code'
        else:
            return 'unknown'
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def get_supported_formats(self) -> dict:
        """Get information about supported formats"""
        return {
            'image_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'ico', 'svg'],
            'document_formats': ['pdf', 'txt', 'docx', 'doc', 'rtf', 'md', 'html', 'htm'],
            'spreadsheet_formats': ['xlsx', 'xls', 'csv'],
            'presentation_formats': ['pptx', 'ppt'],
            'data_formats': ['json', 'xml'],
            'archive_formats': ['zip', 'rar', '7z', 'tar', 'gz'],
            'audio_formats': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
            'video_formats': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'],
            'code_formats': ['py', 'js', 'css', 'php', 'java', 'cpp', 'c', 'cs', 'rb', 'go', 'rs', 'log', 'ini', 'cfg', 'conf', 'yaml', 'yml', 'toml'],
            'all_formats': sorted(list(self.ALLOWED_EXTENSIONS))
        }
    
    def get_format_info(self, extension: str) -> dict:
        """Get detailed information about a specific format"""
        extension = extension.lower()
        
        if extension not in self.ALLOWED_EXTENSIONS:
            return {
                'supported': False,
                'error': f'Format .{extension} is not supported'
            }
        
        category = self._get_file_category(extension)
        max_size = self._get_max_size_for_format(extension)
        
        return {
            'supported': True,
            'extension': extension,
            'category': category,
            'max_size': max_size,
            'max_size_formatted': self._format_size(max_size)
        } 