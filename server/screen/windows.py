"""
Windows-specific screen capture implementation.
"""
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import io
import sys
import importlib

# Ensure system platform module is loaded before wand
if 'platform' in sys.modules:
    del sys.modules['platform']
platform = importlib.import_module('platform')

from wand.image import Image

def get_screens():
    """Get information about all connected screens."""
    monitors = []
    def callback(hm, hdc, rect, data):
        monitor_info = win32gui.GetMonitorInfo(hm)
        work_area = monitor_info['Work']
        monitors.append({
            'left': work_area[0],
            'top': work_area[1],
            'right': work_area[2],
            'bottom': work_area[3],
            'width': work_area[2] - work_area[0],
            'height': work_area[3] - work_area[1],
            'is_primary': monitor_info.get('Flags', 0) == win32con.MONITORINFOF_PRIMARY
        })
        return True
    
    # Use the correct method name
    if hasattr(win32gui, 'EnumDisplayMonitors'):
        win32gui.EnumDisplayMonitors(None, None, callback, None)
    else:
        # Fallback for older pywin32 versions
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        monitors.append({
            'left': 0,
            'top': 0,
            'right': width,
            'bottom': height,
            'width': width,
            'height': height,
            'is_primary': True
        })
    return monitors

class WindowsScreenController:
    """Windows screen capture and control."""
    
    def __init__(self):
        self.screens = get_screens()
        self.primary_screen = next((s for s in self.screens if s['is_primary']), self.screens[0])
    
    def capture_screen(self, screen_idx=0, region=None):
        """Capture a screenshot of the specified screen or region."""
        try:
            if screen_idx >= len(self.screens):
                screen_idx = 0
                
            screen = self.screens[screen_idx]
            hwin = win32gui.GetDesktopWindow()
            
            left = screen['left']
            top = screen['top']
            width = screen['width']
            height = screen['height']
            
            if region:
                left += region[0]
                top += region[1]
                width = min(region[2], width - region[0])
                height = min(region[3], height - region[1])
            
            hwindc = win32gui.GetWindowDC(hwin)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, width, height)
            memdc.SelectObject(bmp)
            memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
            
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            
            # Convert to wand Image
            img_data = np.frombuffer(bmpstr, dtype=np.uint8).reshape((height, width, 4))
            
            # Convert BGRX to RGB (remove the X channel)
            rgb_data = img_data[:, :, [2, 1, 0]]  # BGR -> RGB
            
            # Create wand image from numpy array
            with Image.from_array(rgb_data) as img:
                img_byte_arr = io.BytesIO()
                img.format = 'png'
                img.save(img_byte_arr)
                result = img_byte_arr.getvalue()
            
            # Clean up
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())
            
            return result
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def get_screen_size(self, screen_idx=0):
        """Get the size of the specified screen."""
        if 0 <= screen_idx < len(self.screens):
            return (self.screens[screen_idx]['width'], 
                   self.screens[screen_idx]['height'])
        return (self.primary_screen['width'], 
               self.primary_screen['height'])
    
    def get_screen_count(self):
        """Get the number of connected screens."""
        return len(self.screens)
