"""
Linux-specific screen capture implementation using X11.
"""
import os
import io
import numpy as np
from PIL import Image
from Xlib import display, X
from Xlib.ext import xfixes

class LinuxScreenController:
    """Linux screen capture and control using X11."""
    
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        self.root = self.screen.root
        
        # Get screen dimensions
        self.width = self.screen.width_in_pixels
        self.height = self.screen.height_in_pixels
        
        # Initialize XFixes for cursor handling
        if self.display.has_extension('XFIXES'):
            self.xfix = self.display.xfixes
            self.xfix_version = self.display.xfixes_query_version()
        else:
            self.xfix = None
    
    def capture_screen(self, region=None):
        """Capture a screenshot of the screen or specified region."""
        try:
            if region:
                x, y, width, height = region
                # Ensure the region is within screen bounds
                x = max(0, min(x, self.width - 1))
                y = max(0, min(y, self.height - 1))
                width = min(width, self.width - x)
                height = min(height, self.height - y)
            else:
                x, y = 0, 0
                width, height = self.width, self.height
            
            # Get the image data
            raw = self.root.get_image(
                x, y, width, height,
                X.ZPixmap, 0xffffffff
            )
            
            # Convert to PIL Image
            img = Image.frombuffer(
                'RGB', (width, height),
                raw.data, 'raw', 'BGRX', 0, 1
            )
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=70)
            
            return img_byte_arr.getvalue()
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def get_screen_size(self, screen_idx=0):
        """Get the size of the screen."""
        return (self.width, self.height)
    
    def get_screen_count(self):
        """Get the number of screens (always 1 for X11)."""
        return 1
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'display'):
            self.display.close()
