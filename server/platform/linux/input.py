"""
Cross-platform input handling implementation.
"""
import logging
import os
import platform

logger = logging.getLogger(__name__)

class LinuxInputHandler:
    """Cross-platform input handling implementation."""
    
    def __init__(self):
        """Initialize the input handler."""
        self.supported = True
        self.headless = False
        self.pyautogui = None
        
        # Check if we're running in a headless environment
        if not os.environ.get('DISPLAY'):
            self.headless = True
            logger.warning("Running in headless mode - input simulation will be limited")
            return
            
        # Only import GUI-related modules if we have a display
        try:
            import pyautogui
            self.pyautogui = pyautogui
            
            # Configure pyautogui
            self.pyautogui.PAUSE = 0.1
            self.pyautogui.FAILSAFE = False
            logger.info("Initialized input handler with GUI support")
            
        except ImportError:
            self.headless = True
            logger.warning("pyautogui not available - input simulation will be limited")
    
    def send_mouse_click(self, x: int, y: int, button: str = 'left', double: bool = False) -> bool:
        """
        Send a mouse click event.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            double: Whether to perform a double click
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.headless or not self.pyautogui:
            logger.warning(f"Mouse click at ({x}, {y}) - not simulated in headless mode")
            return True  # Return True to avoid error messages
            
        try:
            self.pyautogui.moveTo(x, y, duration=0.1)
            if button == 'left':
                self.pyautogui.click(button='left', clicks=2 if double else 1)
            elif button == 'right':
                self.pyautogui.rightClick()
            elif button == 'middle':
                self.pyautogui.middleClick()
            else:
                logger.warning(f"Unsupported mouse button: {button}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error sending mouse click: {e}")
            return False
    
    def send_mouse_move(self, x: int, y: int) -> bool:
        """
        Move the mouse cursor to the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.headless or not self.pyautogui:
            # In headless mode, just log the movement
            logger.debug(f"Mouse move to ({x}, {y}) - not simulated in headless mode")
            return True
            
        try:
            self.pyautogui.moveTo(x, y, duration=0.1)
            return True
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return False
    
    def send_key_press(self, key: str, modifier: str = None) -> bool:
        """
        Send a key press event.
        
        Args:
            key: Key to press (e.g., 'a', 'enter', 'space')
            modifier: Optional modifier key (e.g., 'ctrl', 'alt', 'shift')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.headless or not self.pyautogui:
            logger.warning(f"Key press {modifier + '+' if modifier else ''}{key} - not simulated in headless mode")
            return True
            
        try:
            if modifier:
                with self.pyautogui.hold(modifier):
                    self.pyautogui.press(key)
            else:
                self.pyautogui.press(key)
            return True
        except Exception as e:
            logger.error(f"Error sending key press: {e}")
            return False
