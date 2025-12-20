"""
Linux-specific screen capture implementation.
"""
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class LinuxScreenCapture:
    """Linux-specific screen capture implementation."""
    
    def __init__(self):
        """Initialize the Linux screen capture."""
        logger.warning("Linux screen capture is not supported on Windows")
        self.supported = False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the screen size.
        
        Returns:
            tuple: (width, height) of the screen
        """
        logger.warning("Linux screen capture is not supported on Windows")
        return 0, 0
    
    def capture_screen(self) -> Optional[bytes]:
        """
        Capture the entire screen.
        
        Returns:
            bytes: PNG image data if successful, None otherwise
        """
        logger.warning("Linux screen capture is not supported on Windows")
        return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[bytes]:
        """
        Capture a region of the screen.
        
        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            width: Width of the region
            height: Height of the region
            
        Returns:
            bytes: PNG image data if successful, None otherwise
        """
        logger.warning("Linux screen capture is not supported on Windows")
        return None
