"""
Windows-specific input handling implementation.
"""
import win32api
import win32con
import time

class WindowsInputHandler:
    """Windows-specific input handling implementation."""
    
    # Virtual key codes
    VK_CODES = {
        'backspace': 0x08,
        'tab': 0x09,
        'enter': 0x0D,
        'shift': 0x10,
        'ctrl': 0x11,
        'alt': 0x12,
        'space': 0x20,
        'left': 0x25,
        'up': 0x26,
        'right': 0x27,
        'down': 0x28,
        'f1': 0x70,
        'f2': 0x71,
        'f3': 0x72,
        'f4': 0x73,
        'f5': 0x74,
        'f6': 0x75,
        'f7': 0x76,
        'f8': 0x77,
        'f9': 0x78,
        'f10': 0x79,
        'f11': 0x7A,
        'f12': 0x7B,
    }
    
    # Mouse button codes
    MOUSE_BUTTONS = {
        'left': win32con.MOUSEEVENTF_LEFTDOWN,
        'right': win32con.MOUSEEVENTF_RIGHTDOWN,
        'middle': win32con.MOUSEEVENTF_MIDDLEDOWN
    }
    
    def __init__(self):
        """Initialize the Windows input handler."""
        pass
    
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
            # Move to the position
            win32api.SetCursorPos((x, y))
            
            # Get the button code
            btn_code = self.MOUSE_BUTTONS.get(button.lower(), win32con.MOUSEEVENTF_LEFTDOWN)
            
            # Perform the click(s)
            win32api.mouse_event(btn_code, x, y, 0, 0)  # Button down
            win32api.mouse_event(btn_code * 2, x, y, 0, 0)  # Button up
            
            if double:
                time.sleep(0.1)  # Small delay between clicks
                win32api.mouse_event(btn_code, x, y, 0, 0)  # Button down
                win32api.mouse_event(btn_code * 2, x, y, 0, 0)  # Button up
                
            return True
        except Exception as e:
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
            win32api.SetCursorPos((x, y))
            return True
        except:
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
            # Handle modifier keys
            if modifier:
                mod_code = self.VK_CODES.get(modifier.lower())
                if mod_code:
                    win32api.keybd_event(mod_code, 0, 0, 0)  # Key down
            
            # Handle the main key
            if len(key) == 1:  # Single character
                # Convert to virtual key code
                vk_code = win32api.VkKeyScan(ord(key)) & 0xff
                win32api.keybd_event(vk_code, 0, 0, 0)  # Key down
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            else:  # Special key
                key_code = self.VK_CODES.get(key.lower())
                if key_code:
                    win32api.keybd_event(key_code, 0, 0, 0)  # Key down
                    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            
            # Release modifier key if pressed
            if modifier:
                mod_code = self.VK_CODES.get(modifier.lower())
                if mod_code:
                    win32api.keybd_event(mod_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
            
            return True
        except:
            return False
