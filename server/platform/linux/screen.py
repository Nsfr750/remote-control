"""
Linux-specific screen capture implementation.
"""
import logging
import subprocess
import tempfile
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class LinuxScreenCapture:
    """Linux-specific screen capture implementation."""
    
    def __init__(self):
        """Initialize Linux screen capture."""
        try:
            # Check if we're actually on Linux
            import platform
            if platform.system().lower() != 'linux':
                logger.warning("Linux screen capture is not supported on Windows")
                self.supported = False
                return
            
            # Try to import required modules
            try:
                import numpy as np
                from wand.image import Image
                self.np = np
                self.Image = Image
                self.supported = True
                logger.info("Linux screen capture initialized successfully")
            except ImportError as e:
                logger.error(f"Failed to import required modules: {e}")
                self.supported = False
                
        except Exception as e:
            logger.error(f"Error initializing Linux screen capture: {e}")
            self.supported = False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the screen size.
        
        Returns:
            tuple: (width, height) of the screen
        """
        if not self.supported:
            return 0, 0
            
        try:
            # Use xrandr to get screen resolution
            result = subprocess.run(['xrandr'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '*' in line and 'x' in line:
                        parts = line.split()
                        for part in parts:
                            if 'x' in part and '+' not in part:
                                try:
                                    width, height = part.split('x')
                                    return int(width), int(height)
                                except ValueError:
                                    continue
            
            # Fallback to a common resolution
            return 1920, 1080
            
        except Exception as e:
            logger.error(f"Error getting screen size: {e}")
            return 1920, 1080
    
    def capture_screen(self) -> Optional[bytes]:
        """
        Capture the entire screen.
        
        Returns:
            bytes: PNG image data if successful, None otherwise
        """
        if not self.supported:
            logger.warning("Linux screen capture not supported")
            return None
            
        try:
            # Try using import first
            result = subprocess.run([
                'import', '-window', 'root', '-screen', 'png', '-'
            ], capture_output=True)
            
            if result.returncode == 0:
                return result.stdout
            
            # Fallback to scrot
            result = subprocess.run([
                'scrot', '-f', 'png', '-'
            ], capture_output=True)
            
            if result.returncode == 0:
                return result.stdout
                
            logger.error("Neither import nor scrot available for screen capture")
            return None
            
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
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
