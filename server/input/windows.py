"""
Windows-specific input simulation.
"""
import ctypes
import time
from ctypes import wintypes

# Constants for mouse input
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_ABSOLUTE = 0x8000

# Constants for keybd_event
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# Virtual key codes
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_XBUTTON1 = 0x05
VK_XBUTTON2 = 0x06
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt key
VK_PAUSE = 0x13
VK_CAPITAL = 0x14
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_PRIOR = 0x21  # Page Up
VK_NEXT = 0x22   # Page Down
VK_END = 0x23
VK_HOME = 0x24
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_PRINT = 0x2A
VK_SNAPSHOT = 0x2C  # Print Screen
VK_INSERT = 0x2D
VK_DELETE = 0x2E

# 0-9 keys are the same as ASCII '0' to '9' (0x30 - 0x39)
# A-Z keys are the same as ASCII 'A' to 'Z' (0x41 - 0x5A)

# Numpad keys
VK_NUMPAD0 = 0x60
VK_NUMPAD1 = 0x61
VK_NUMPAD2 = 0x62
VK_NUMPAD3 = 0x63
VK_NUMPAD4 = 0x64
VK_NUMPAD5 = 0x65
VK_NUMPAD6 = 0x66
VK_NUMPAD7 = 0x67
VK_NUMPAD8 = 0x68
VK_NUMPAD9 = 0x69
VK_MULTIPLY = 0x6A
VK_ADD = 0x6B
VK_SEPARATOR = 0x6C
VK_SUBTRACT = 0x6D
VK_DECIMAL = 0x6E
VK_DIVIDE = 0x6F

# Function keys
VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F4 = 0x73
VK_F5 = 0x74
VK_F6 = 0x75
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_F10 = 0x79
VK_F11 = 0x7A
VK_F12 = 0x7B

# Key state masks for GetKeyState/GetAsyncKeyState
KEY_PRESSED = 0x8000
KEY_TOGGLED = 0x0001

# Import required Windows API functions
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Define function prototypes
user32.mouse_event.argtypes = [
    wintypes.DWORD,  # dwFlags
    wintypes.DWORD,  # dx
    wintypes.DWORD,  # dy
    wintypes.DWORD,  # dwData
    wintypes.ULONG_PTR  # dwExtraInfo
]

user32.keybd_event.argtypes = [
    wintypes.BYTE,   # bVk
    wintypes.BYTE,   # bScan
    wintypes.DWORD,  # dwFlags
    wintypes.ULONG_PTR  # dwExtraInfo
]

user32.GetKeyState.argtypes = [wintypes.INT]
user32.GetKeyState.restype = wintypes.SHORT

user32.GetAsyncKeyState.argtypes = [wintypes.INT]
user32.GetAsyncKeyState.restype = wintypes.SHORT

user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT

class WindowsInputController:
    """Windows input simulation and control."""
    
    def __init__(self):
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        self.key_states = {}
    
    def move_mouse(self, x, y):
        """Move the mouse to the specified coordinates."""
        # Convert to absolute coordinates (0-65535)
        x = int((x * 65535) / self.screen_width)
        y = int((y * 65535) / self.screen_height)
        
        user32.mouse_event(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            x, y, 0, 0
        )
    
    def mouse_click(self, button, pressed=True):
        """Simulate a mouse button click or release."""
        if button == 0:  # Left button
            event = MOUSEEVENTF_LEFTDOWN if pressed else MOUSEEVENTF_LEFTUP
        elif button == 1:  # Right button
            event = MOUSEEVENTF_RIGHTDOWN if pressed else MOUSEEVENTF_RIGHTUP
        elif button == 2:  # Middle button
            event = MOUSEEVENTF_MIDDLEDOWN if pressed else MOUSEEVENTF_MIDDLEUP
        else:
            return
        
        user32.mouse_event(event, 0, 0, 0, 0)
    
    def mouse_scroll(self, dx=0, dy=0):
        """Simulate mouse wheel scrolling."""
        if dy != 0:
            user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, dy * 120, 0)
        if dx != 0:
            user32.mouse_event(MOUSEEVENTF_HWHEEL, 0, 0, dx * 120, 0)
    
    def key_press(self, key, pressed=True):
        """Simulate a key press or release."""
        if not isinstance(key, int):
            # Convert character to virtual key code
            key = ord(key.upper())
        
        # Check if this is an extended key (right alt/ctrl/numlock, etc.)
        extended = key in [
            VK_RMENU, VK_RCONTROL, VK_INSERT, VK_DELETE,
            VK_HOME, VK_END, VK_PRIOR, VK_NEXT,
            VK_LEFT, VK_RIGHT, VK_UP, VK_DOWN,
            VK_NUMLOCK, VK_RETURN, VK_DIVIDE
        ]
        
        # Get the scan code
        scan_code = user32.MapVirtualKeyW(key, 0)
        
        # Set the extended key flag if needed
        flags = 0
        if extended:
            flags |= KEYEVENTF_EXTENDEDKEY
        if not pressed:
            flags |= KEYEVENTF_KEYUP
        
        # Send the key event
        user32.keybd_event(key, scan_code, flags, 0)
    
    def key_tap(self, key):
        """Simulate a key tap (press and release)."""
        self.key_press(key, True)
        time.sleep(0.01)  # Small delay between press and release
        self.key_press(key, False)
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed."""
        if not isinstance(key, int):
            key = ord(key.upper())
        
        state = user32.GetAsyncKeyState(key)
        return (state & KEY_PRESSED) != 0
    
    def type_text(self, text):
        """Type the specified text."""
        for char in text:
            if char == '\n':
                self.key_tap(VK_RETURN)
            elif char == '\t':
                self.key_tap(VK_TAB)
            else:
                # Handle uppercase letters and symbols with shift
                if char.isupper() or (not char.isalnum() and char in '~!@#$%^&*()_+{}|:"<>?'):
                    self.key_press(VK_SHIFT, True)
                
                # Send the key press and release
                self.key_tap(ord(char.upper()))
                
                # Release shift if it was pressed
                if char.isupper() or (not char.isalnum() and char in '~!@#$%^&*()_+{}|:"<>?'):
                    self.key_press(VK_SHIFT, False)
            
            # Small delay between keystrokes
            time.sleep(0.01)
    
    def get_mouse_position(self):
        """Get the current mouse position."""
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)
