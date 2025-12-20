"""
Windows-specific screen capture implementation.
"""
import ctypes
import numpy as np
from PIL import ImageGrab, Image
import win32gui
import win32ui
import win32con
import win32api
from ctypes import wintypes

class WindowsScreenCapture:
    """Windows-specific screen capture implementation."""
    
    def __init__(self):
        """Initialize the Windows screen capture."""
        self.hwnd = win32gui.GetDesktopWindow()
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        
    def get_screen_size(self) -> tuple:
        """
        Get the screen size.
        
        Returns:
            tuple: (width, height) of the screen
        """
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        return width, height
    
    def capture_screen(self) -> bytes:
        """
        Capture the entire screen.
        
        Returns:
            bytes: PNG image data
        """
        width, height = self.get_screen_size()
        return self.capture_region(0, 0, width, height)
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> bytes:
        """
        Capture a region of the screen.
        
        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            width: Width of the region
            height: Height of the region
            
        Returns:
            bytes: PNG image data
        """
        # Create a bitmap
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(self.mfcDC, width, height)
        self.saveDC.SelectObject(saveBitMap)
        
        # Copy the screen to the bitmap
        self.saveDC.BitBlt(
            (0, 0), (width, height),
            self.mfcDC, (x, y),
            win32con.SRCCOPY
        )
        
        # Convert to PIL Image
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        
        # Convert to PNG bytes
        import io
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='PNG')
        
        # Clean up
        win32gui.DeleteObject(saveBitMap.GetHandle())
        
        return img_byte_arr.getvalue()
    
    def __del__(self):
        """Clean up resources."""
        try:
            self.saveDC.DeleteDC()
            self.mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, self.hwndDC)
        except:
            pass
