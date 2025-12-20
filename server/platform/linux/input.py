"""
Linux-specific input handling implementation.
"""
import logging

logger = logging.getLogger(__name__)

class LinuxInputHandler:
    """Linux-specific input handling implementation."""
    
    def __init__(self):
        """Initialize the Linux input handler."""
        logger.warning("Linux input handling is not supported on Windows")
        self.supported = False
    
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
        logger.warning("Linux input handling is not supported on Windows")
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
        logger.warning("Linux input handling is not supported on Windows")
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
        logger.warning("Linux input handling is not supported on Windows")
        return False
