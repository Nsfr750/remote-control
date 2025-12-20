"""
Linux-specific input simulation using X11.
"""
import time
import Xlib
from Xlib import X, XK, display
from Xlib.ext import xtest

# Key codes for common keys (X11 keysymdef.h)
XK_BackSpace = 0xff08
XK_Tab = 0xff09
XK_Return = 0xff0d
XK_Shift_L = 0xffe1
XK_Shift_R = 0xffe2
XK_Control_L = 0xffe3
XK_Control_R = 0xffe4
XK_Alt_L = 0xffe9
XK_Alt_R = 0xffea
XK_Caps_Lock = 0xffe5
XK_Escape = 0xff1b
XK_space = 0x0020
XK_Left = 0xff51
XK_Up = 0xff52
XK_Right = 0xff53
XK_Down = 0xff54
XK_Page_Up = 0xff55
XK_Page_Down = 0xff56
XK_Home = 0xff50
XK_End = 0xff57
XK_Insert = 0xff63
XK_Delete = 0xffff
XK_F1 = 0xffbe
XK_F2 = 0xffbf
XK_F3 = 0xffc0
XK_F4 = 0xffc1
XK_F5 = 0xffc2
XK_F6 = 0xffc3
XK_F7 = 0xffc4
XK_F8 = 0xffc5
XK_F9 = 0xffc6
XK_F10 = 0xffc7
XK_F11 = 0xffc8
XK_F12 = 0xffc9

class LinuxInputController:
    """Linux input simulation using X11."""
    
    def __init__(self):
        self.display = display.Display()
        self.root = self.display.screen().root
        self.xtest = self.display.xtest_query_extension()
        
        # Get the screen dimensions
        self.screen_width = self.display.screen().width_in_pixels
        self.screen_height = self.display.screen().height_in_pixels
        
        # Initialize the keyboard mapping
        self.keysym_to_keycode = {}
        self.keycode_to_keysym = {}
        self._init_key_mapping()
    
    def _init_key_mapping(self):
        """Initialize the keycode to keysym mapping."""
        min_keycode = self.display.display.info.min_keycode
        max_keycode = self.display.display.info.max_keycode
        
        for keycode in range(min_keycode, max_keycode + 1):
            keysyms = self.display.keycode_to_keysym(keycode, 0)
            if keysyms:
                self.keysym_to_keycode[keysyms] = keycode
                self.keycode_to_keysym[keycode] = keysyms
    
    def move_mouse(self, x, y):
        """Move the mouse to the specified coordinates."""
        # Warp the pointer to the new position
        self.root.warp_pointer(x, y)
        self.display.sync()
    
    def mouse_click(self, button, pressed=True):
        """Simulate a mouse button click or release."""
        # Map button number to X11 button constants
        button_map = {0: 1, 1: 3, 2: 2, 3: 4, 4: 5}
        button = button_map.get(button, 1)
        
        if pressed:
            self.display.xtest_fake_input(X.ButtonPress, button)
        else:
            self.display.xtest_fake_input(X.ButtonRelease, button)
        
        self.display.sync()
    
    def mouse_scroll(self, dx=0, dy=0):
        """Simulate mouse wheel scrolling."""
        if dy > 0:  # Scroll up
            self.display.xtest_fake_input(X.ButtonPress, 4)  # Button 4 is scroll up
            self.display.xtest_fake_input(X.ButtonRelease, 4)
        elif dy < 0:  # Scroll down
            self.display.xtest_fake_input(X.ButtonPress, 5)  # Button 5 is scroll down
            self.display.xtest_fake_input(X.ButtonRelease, 5)
            
        if dx > 0:  # Scroll right
            self.display.xtest_fake_input(X.ButtonPress, 7)  # Button 7 is scroll right
            self.display.xtest_fake_input(X.ButtonRelease, 7)
        elif dx < 0:  # Scroll left
            self.display.xtest_fake_input(X.ButtonPress, 6)  # Button 6 is scroll left
            self.display.xtest_fake_input(X.ButtonRelease, 6)
        
        self.display.sync()
    
    def key_press(self, key, pressed=True):
        """Simulate a key press or release."""
        if isinstance(key, str):
            # Convert character to keysym
            keysym = XK.string_to_keysym(key)
        else:
            # Assume it's already a keysym
            keysym = key
        
        # Get the keycode for the keysym
        keycode = self.display.keysym_to_keycode(keysym)
        
        # Send the key event
        if pressed:
            self.display.xtest_fake_input(X.KeyPress, keycode)
        else:
            self.display.xtest_fake_input(X.KeyRelease, keycode)
        
        self.display.sync()
    
    def key_tap(self, key):
        """Simulate a key tap (press and release)."""
        self.key_press(key, True)
        time.sleep(0.01)  # Small delay between press and release
        self.key_press(key, False)
    
    def is_key_pressed(self, key):
        """Check if a key is currently pressed."""
        if isinstance(key, str):
            keysym = XK.string_to_keysym(key)
        else:
            keysym = key
        
        keycode = self.display.keysym_to_keycode(keysym)
        
        # Query the keyboard state
        keys = self.display.query_pointer(self.root).child.query_keymap()
        return bool(keys[keycode // 8] & (1 << (keycode % 8)))
    
    def type_text(self, text):
        """Type the specified text."""
        for char in text:
            if char == '\n':
                self.key_tap(XK_Return)
            elif char == '\t':
                self.key_tap(XK_Tab)
            else:
                # Handle uppercase letters and symbols with shift
                if char.isupper() or (not char.isalnum() and char in '~!@#$%^&*()_+{}|:"<>?'):
                    self.key_press(XK_Shift_L, True)
                
                # Send the key press and release
                self.key_tap(char)
                
                # Release shift if it was pressed
                if char.isupper() or (not char.isalnum() and char in '~!@#$%^&*()_+{}|:"<>?'):
                    self.key_press(XK_Shift_L, False)
            
            # Small delay between keystrokes
            time.sleep(0.01)
    
    def get_mouse_position(self):
        """Get the current mouse position."""
        pointer = self.root.query_pointer()
        return (pointer.root_x, pointer.root_y)
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'display'):
            self.display.close()
