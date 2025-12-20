"""
Input controller for handling keyboard and mouse input.
"""
import logging
import platform
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class InputController:
    """Controller for handling input events."""
    
    def __init__(self):
        """Initialize the input controller."""
        self.platform = platform.system().lower()
        self.input_available = False
        self.initialize_input_controller()
    
    def initialize_input_controller(self) -> bool:
        """
        Initialize the input controller based on the current platform.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if self.platform == 'windows':
                from .platform.windows.input import WindowsInputHandler
                self.input_handler = WindowsInputHandler()
                self.input_available = True
            elif self.platform == 'linux':
                from .platform.linux.input import LinuxInputHandler
                self.input_handler = LinuxInputHandler()
                self.input_available = True
            else:
                logger.error(f"Unsupported platform for input handling: {self.platform}")
                return False
            
            logger.info("Input controller initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize input controller: {str(e)}")
            self.input_available = False
            return False
    
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
        if not self.input_available:
            logger.warning("Input controller is not available")
            return False
            
        try:
            return self.input_handler.send_mouse_click(x, y, button, double)
        except Exception as e:
            logger.error(f"Failed to send mouse click: {str(e)}")
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
        if not self.input_available:
            logger.warning("Input controller is not available")
            return False
            
        try:
            return self.input_handler.send_mouse_move(x, y)
        except Exception as e:
            logger.error(f"Failed to move mouse: {str(e)}")
            return False
    
    def send_key_press(self, key: str, modifier: Optional[str] = None) -> bool:
        """
        Send a key press event.
        
        Args:
            key: Key to press (e.g., 'a', 'enter', 'space')
            modifier: Optional modifier key (e.g., 'ctrl', 'alt', 'shift')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.input_available:
            logger.warning("Input controller is not available")
            return False
            
        try:
            return self.input_handler.send_key_press(key, modifier)
        except Exception as e:
            logger.error(f"Failed to send key press: {str(e)}")
            return False

# Create a global instance
input_controller = InputController()
