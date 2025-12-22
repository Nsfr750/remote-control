"""
Linux-specific screen capture implementation using X11 with fallback for headless environments.
"""
import os
import sys
import io
import logging
import numpy as np
from PIL import Image

try:
    from Xlib import display, X
    from Xlib.ext import xfixes
    X11_AVAILABLE = True
except (ImportError, OSError) as e:
    X11_AVAILABLE = False
    logging.warning(f"X11 not available: {e}. Running in headless mode.")

class HeadlessScreenController:
    """Fallback screen controller for headless environments."""
    
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.xfix = None
        logging.info("Initialized headless screen controller")
    
    def capture_screen(self, region=None):
        """Return a blank black image as JPEG bytes for headless environments."""
        try:
            if region:
                width = min(region[2], self.width)
                height = min(region[3], self.height)
            else:
                width, height = self.width, self.height
                
            # Create a black image
            img_array = np.zeros((height, width, 3), dtype=np.uint8)
            img = Image.fromarray(img_array, 'RGB')
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logging.error(f"Error in headless screen capture: {e}")
            # Return a minimal black image (1x1 pixel) as fallback
            img = Image.new('RGB', (1, 1), (0, 0, 0))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return img_byte_arr.getvalue()
            
    def get_screen_size(self):
        """Return the screen dimensions."""
        return self.width, self.height
    
    def get_screen_size(self):
        """Return the default screen size."""
        return self.width, self.height


class LinuxScreenController:
    """Linux screen capture and control using X11 with fallback to headless mode."""
    
    def __init__(self):
        self.xfix = None
        self.display = None
        self.screen = None
        self.root = None
        self.headless = False
        
        try:
            if not X11_AVAILABLE:
                raise RuntimeError("X11 libraries not available")
                
            self.display = display.Display()
            self.screen = self.display.screen()
            self.root = self.screen.root
            
            # Get screen dimensions
            self.width = self.screen.width_in_pixels
            self.height = self.screen.height_in_pixels
            
            # Initialize XFixes for cursor handling if available
            if self.display.has_extension('XFIXES'):
                self.xfix = self.display.xfixes
                self.xfix_version = self.display.xfixes_query_version()
                
            logging.info("Initialized X11 screen controller")
            
        except Exception as e:
            logging.warning(f"Failed to initialize X11 screen controller: {e}")
            logging.info("Falling back to headless mode")
            self.headless = True
            self._headless_controller = HeadlessScreenController()
            self.width, self.height = self._headless_controller.get_screen_size()
    
    def capture_screen(self, region=None):
        """Capture a screenshot of the screen or specified region and return as JPEG bytes."""
        if self.headless:
            return self._headless_controller.capture_screen(region)
            
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
            
            # Convert to PIL Image and then to JPEG bytes
            img = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            return img_byte_arr.getvalue()
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
