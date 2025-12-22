"""
Cross-platform input handling implementation using pyautogui.
"""
import logging
import platform
import pyautogui

logger = logging.getLogger(__name__)

class LinuxInputHandler:
    """Cross-platform input handling implementation using pyautogui."""
    
    def __init__(self):
        """Initialize the input handler."""
        self.supported = True
        # Add a small delay after each PyAutoGUI call
        pyautogui.PAUSE = 0.1
        # Disable the fail-safe
        pyautogui.FAILSAFE = False
        logger.info("Initialized input handler")
    
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
        try:
            # Move to the position first
            pyautogui.moveTo(x, y, duration=0.1)
            
            # Perform the click
            if button == 'left':
                pyautogui.click(button='left', clicks=2 if double else 1)
            elif button == 'right':
                pyautogui.rightClick()
            elif button == 'middle':
                pyautogui.middleClick()
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
        try:
            pyautogui.moveTo(x, y, duration=0.1)
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
        try:
            if modifier:
                with pyautogui.hold(modifier):
                    pyautogui.press(key)
            else:
                pyautogui.press(key)
            return True
        except Exception as e:
            logger.error(f"Error sending key press: {e}")
            return False
