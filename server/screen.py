"""
Screen controller for capturing and managing screen content.
"""
import logging
from typing import Optional, Tuple
import platform

logger = logging.getLogger(__name__)

class ScreenController:
    """Controller for screen capture functionality."""
    
    def __init__(self):
        """Initialize the screen controller."""
        self.platform = platform.system().lower()
        self.screen_available = False
        self.screen_width = 0
        self.screen_height = 0
        self.initialize_screen_capture()
    
    def initialize_screen_capture(self) -> bool:
        """
        Initialize screen capture based on the current platform.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if self.platform == 'windows':
                from .platform.windows.screen import WindowsScreenCapture
                self.capture = WindowsScreenCapture()
                self.screen_available = True
            elif self.platform == 'linux':
                from .platform.linux.screen import LinuxScreenCapture
                self.capture = LinuxScreenCapture()
                self.screen_available = True
            else:
                logger.error(f"Unsupported platform for screen capture: {self.platform}")
                return False
            
            # Get screen dimensions
            self.screen_width, self.screen_height = self.capture.get_screen_size()
            logger.info(f"Screen capture initialized. Resolution: {self.screen_width}x{self.screen_height}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize screen capture: {str(e)}")
            self.screen_available = False
            return False
    
    def capture_screen(self, region: Tuple[int, int, int, int] = None) -> Optional[bytes]:
        """
        Capture the screen or a region of the screen.
        
        Args:
            region: Tuple of (x, y, width, height) for the region to capture.
                   If None, captures the entire screen.
                   
        Returns:
            bytes: PNG image data if successful, None otherwise
        """
        if not self.screen_available:
            logger.warning("Screen capture is not available")
            return None
            
        try:
            if region is None:
                return self.capture.capture_screen()
            else:
                return self.capture.capture_region(*region)
        except Exception as e:
            logger.error(f"Failed to capture screen: {str(e)}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the screen dimensions.
        
        Returns:
            Tuple[int, int]: (width, height) of the screen
        """
        return self.screen_width, self.screen_height

# Create a global instance
screen_controller = ScreenController()
