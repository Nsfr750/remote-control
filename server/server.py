"""
Remote Control Server

Handles incoming connections, authentication, and remote control commands.
"""
import os
import sys
import json
import socket
import logging
import threading
import platform
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

# Add parent directory to path for module imports
sys.path.append(str(Path(__file__).parent.parent))

from common.protocol import Message, MessageType, AuthMessage, MouseEvent, KeyEvent
from common.security import SecurityManager
from common.file_transfer import FileTransfer, FileTransferMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RemoteControlServer')

class RemoteControlServer:
    """Main server class for handling remote control connections."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """Initialize the server."""
        self.host = host
        self.port = port
        self.running = False
        self.clients: Dict[str, Dict] = {}
        self.auth_required = True
        self.server_socket: Optional[socket.socket] = None
        self.security_manager = SecurityManager()
        self.allowed_users = self._load_users()
        self.platform = platform.system().lower()
        self.screen_controller = self._get_screen_controller()
        self.input_controller = self._get_input_controller()
        self.file_transfer = FileTransfer()
        self.allowed_directories = self._get_allowed_directories()

    def _load_users(self) -> Dict:
        """Load users from a JSON file."""
        users_file = Path('users.json')
        if users_file.exists():
            try:
                with open(users_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading users file: {e}")
        return {}

    def _get_allowed_directories(self) -> list:
        """Get list of allowed directories for file operations."""
        return [str(Path.home())]

    def _get_screen_controller(self):
        """Get the appropriate screen controller for the platform."""
        try:
            from server.screen import ScreenController
            return ScreenController()
        except ImportError as e:
            logger.error(f"Failed to load screen controller: {e}")
            return None

    def _get_input_controller(self):
        """Get the appropriate input controller for the platform."""
        try:
            if self.platform == 'windows':
                from platform.windows.input import WindowsInputHandler as WindowsInputController
                return WindowsInputController()
            else:
                from server.platform.linux.input import LinuxInputHandler as LinuxInputController
                return LinuxInputController()
        except ImportError as e:
            logger.error(f"Failed to load input controller: {e}")
            return None

    def start(self) -> None:
        """Start the server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Server started on {self.host}:{self.port}")
            logger.info("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the server and clean up resources."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logger.error(f"Error closing server socket: {e}")
        logger.info("Server stopped")

    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """Handle a client connection."""
        client_id = f"{client_address[0]}:{client_address[1]}"
        authenticated = False
        username = None
        
        try:
            while self.running:
                # Receive message header (8 bytes: 4 for type, 4 for length)
                header = client_socket.recv(8)
                if not header:
                    break
                    
                # Parse message
                msg_type = int.from_bytes(header[:4], byteorder='big')
                data_len = int.from_bytes(header[4:8], byteorder='big')
                
                # Receive message data
                data = b''
                while len(data) < data_len:
                    chunk = client_socket.recv(min(4096, data_len - len(data)))
                    if not chunk:
                        break
                    data += chunk
                
                if len(data) != data_len:
                    logger.warning(f"Incomplete message from {client_id}")
                    break
                
                # Process message
                if not authenticated and msg_type != MessageType.AUTH.value:
                    logger.warning(f"Unauthenticated client {client_id} sent non-auth message")
                    self._send_message(client_socket, MessageType.ERROR, b"Authentication required")
                    break
                
                response = self._handle_message(msg_type, data, client_socket, client_id, username)
                if response:
                    msg_type, response_data = response
                    # Update authentication status if this was an AUTH message
                    if msg_type == MessageType.AUTH_RESPONSE:
                        try:
                            response_data_str = response_data.decode('utf-8')
                            response_json = json.loads(response_data_str)
                            if response_json.get('success', False):
                                authenticated = True
                                username = self.clients.get(client_id, {}).get('username')
                        except (json.JSONDecodeError, AttributeError) as e:
                            logger.error(f"Error parsing auth response: {e}")
                    
                    self._send_message(client_socket, msg_type, response_data)
                
        except ConnectionResetError:
            logger.info(f"Client {client_id} disconnected unexpectedly")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            client_socket.close()
            if username in self.clients:
                del self.clients[username]
            logger.info(f"Client {client_id} ({username or 'unauthenticated'}) disconnected")

    def _handle_message(self, msg_type: int, data: bytes, client_socket: socket.socket, 
                       client_id: str, username: Optional[str]) -> Optional[Tuple[MessageType, bytes]]:
        """Handle an incoming message."""
        try:
            if msg_type == MessageType.AUTH.value:
                return self._handle_auth(data, client_id)
                
            # At this point, the client should be authenticated
            if not username:
                return MessageType.ERROR, b"Not authenticated"
                
            if msg_type == MessageType.MOUSE_MOVE.value:
                return self._handle_mouse_move(data)
            elif msg_type == MessageType.MOUSE_CLICK.value:
                return self._handle_mouse_click(data)
            elif msg_type == MessageType.KEY_EVENT.value:
                return self._handle_key_event(data)
            elif msg_type == MessageType.SCREENSHOT.value:
                return self._handle_screenshot()
            elif msg_type == MessageType.FILE_TRANSFER.value:
                return self._handle_file_transfer(data, client_socket)
            elif msg_type == MessageType.CLIPBOARD_UPDATE.value:
                return self._handle_clipboard_update(data)
            elif msg_type == MessageType.SYSTEM_COMMAND.value:
                return self._handle_system_command(data)
            elif msg_type == MessageType.INFO.value:
                return self._handle_info()
            elif msg_type == MessageType.DISCONNECT.value:
                return None  # Client is disconnecting
            else:
                return MessageType.ERROR, b"Unknown message type"
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return MessageType.ERROR, str(e).encode('utf-8')

    def _send_message(self, client_socket: socket.socket, msg_type: MessageType, data: bytes) -> None:
        """Send a message to a client."""
        try:
            # Prepare message header (4 bytes for type, 4 for length)
            header = msg_type.value.to_bytes(4, byteorder='big')
            header += len(data).to_bytes(4, byteorder='big')
            
            # Send header + data
            client_socket.sendall(header + data)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    def _handle_info(self) -> Tuple[MessageType, bytes]:
        """Handle system information request."""
        try:
            system_info = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'hostname': platform.node(),
                'cpu_count': os.cpu_count(),
                'screen_controller': self.screen_controller is not None,
                'input_controller': self.input_controller is not None,
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_implementation': platform.python_implementation(),
                'python_compiler': platform.python_compiler()
            }
            return MessageType.INFO, json.dumps(system_info).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return MessageType.ERROR, f"Failed to get system info: {e}".encode('utf-8')

    def _handle_screenshot(self) -> Tuple[MessageType, bytes]:
        """Handle screenshot request."""
        try:
            if not self.screen_controller:
                return MessageType.ERROR, b"Screen controller not available"
            
            # Capture the screen
            screenshot = self.screen_controller.capture_screen()
            if screenshot is None:
                return MessageType.ERROR, b"Failed to capture screenshot"
                
            return MessageType.SCREENSHOT, screenshot
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return MessageType.ERROR, f"Failed to capture screenshot: {e}".encode('utf-8')

    def _get_total_ram(self) -> int:
        """Get total system RAM in bytes."""
        if self.platform == 'windows':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ('dwLength', c_ulong),
                    ('dwMemoryLoad', c_ulong),
                    ('dwTotalPhys', c_ulong),
                    ('dwAvailPhys', c_ulong),
                    ('dwTotalPageFile', c_ulong),
                    ('dwAvailPageFile', c_ulong),
                    ('dwTotalVirtual', c_ulong),
                    ('dwAvailVirtual', c_ulong)
                ]
            memoryStatus = MEMORYSTATUS()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
            ctypes.windll.kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
            return memoryStatus.dwTotalPhys
        else:
            with open('/proc/meminfo', 'r') as f:
                mem_total = f.readline()
                return int(mem_total.split()[1]) * 1024  # Convert from KB to bytes

    def _get_free_ram(self) -> int:
        """Get free system RAM in bytes."""
        if self.platform == 'windows':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ('dwLength', c_ulong),
                    ('dwMemoryLoad', c_ulong),
                    ('dwTotalPhys', c_ulong),
                    ('dwAvailPhys', c_ulong),
                    ('dwTotalPageFile', c_ulong),
                    ('dwAvailPageFile', c_ulong),
                    ('dwTotalVirtual', c_ulong),
                    ('dwAvailVirtual', c_ulong)
                ]
            memoryStatus = MEMORYSTATUS()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
            ctypes.windll.kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
            return memoryStatus.dwAvailPhys
        else:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable' in line:
                        return int(line.split()[1]) * 1024  # Convert from KB to bytes
            return 0

    def _get_disk_usage(self) -> dict:
        """Get disk usage information."""
        import shutil
        disk_usage = {}
        for partition in self.allowed_directories:
            try:
                usage = shutil.disk_usage(partition)
                disk_usage[partition] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                }
            except Exception as e:
                logger.warning(f"Error getting disk usage for {partition}: {e}")
        return disk_usage

    def _get_uptime(self) -> float:
        """Get system uptime in seconds."""
        if self.platform == 'windows':
            import ctypes
            lib = ctypes.windll.kernel32
            return float(lib.GetTickCount64() / 1000.0)
        else:
            with open('/proc/uptime', 'r') as f:
                return float(f.readline().split()[0])

    def _handle_mouse_move(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle mouse movement event."""
        try:
            if not self.input_controller:
                return MessageType.ERROR, b"Input controller not available"
                
            # Parse mouse event data
            mouse_event = MouseEvent.from_bytes(data)
            
            # Move the mouse
            success = self.input_controller.send_mouse_move(mouse_event.x, mouse_event.y)
            if not success:
                return MessageType.ERROR, b"Failed to move mouse"
                
            return MessageType.INFO, b"Mouse moved successfully"
            
        except Exception as e:
            logger.error(f"Error handling mouse move: {e}")
            return MessageType.ERROR, f"Failed to handle mouse move: {e}".encode('utf-8')

    def _handle_mouse_click(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle mouse click event."""
        try:
            if not self.input_controller:
                return MessageType.ERROR, b"Input controller not available"
                
            # Parse JSON data
            try:
                mouse_data = json.loads(data.decode('utf-8'))
                x = mouse_data['x']
                y = mouse_data['y']
                button = mouse_data['button']  # 0=left, 1=middle, 2=right
                pressed = mouse_data['pressed']  # True for press, False for release
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse mouse event: {e}")
                return MessageType.ERROR, f"Invalid mouse event data: {e}".encode('utf-8')
            
            # Map button number to button name
            button_map = {0: 'left', 1: 'middle', 2: 'right'}
            button_name = button_map.get(button, 'left')
            
            # For Linux, we'll use send_mouse_click for both press and release
            # since the LinuxInputHandler doesn't support separate down/up events
            if pressed:  # Only send the click on press, not on release
                success = self.input_controller.send_mouse_click(
                    x, 
                    y, 
                    button=button_name,
                    double=False  # Single click
                )
                
                if not success:
                    return MessageType.ERROR, b"Failed to send mouse click"
                    
            return MessageType.SUCCESS, b"Mouse click handled"
                
        except Exception as e:
            logger.error(f"Error handling mouse click: {e}")
            return MessageType.ERROR, f"Failed to handle mouse click: {e}".encode('utf-8')

    def _handle_key_event(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle keyboard event."""
        try:
            if not self.input_controller:
                return MessageType.ERROR, b"Input controller not available"
                
            # Parse key event data
            key_event = KeyEvent.from_bytes(data)
            
            # Send the key press/release
            # Note: The key event contains a 'pressed' flag, but our current input controller
            # combines press and release. We'll need to update the input controller to support this.
            if key_event.pressed:  # Only handle key presses for now
                success = self.input_controller.send_key_press(key_event.key)
                if not success:
                    return MessageType.ERROR, b"Failed to send key press"
            
            return MessageType.INFO, b"Key event handled successfully"
            
        except Exception as e:
            logger.error(f"Error handling key event: {e}")
            return MessageType.ERROR, f"Failed to handle key event: {e}".encode('utf-8')

    def _handle_auth(self, data: bytes, client_id: str) -> Tuple[MessageType, bytes]:
        """Handle authentication."""
        try:
            auth_data = json.loads(data.decode('utf-8'))
            username = auth_data.get('username')
            password = auth_data.get('password')
            
            if not username or not password:
                return MessageType.ERROR, b"Missing username or password"
                
            # Verify credentials
            success, message = self.verify_user(username, password)
            if not success:
                return MessageType.ERROR, message.encode('utf-8')
                
            # Authentication successful
            self.clients[client_id] = {
                'username': username,
                'authenticated': True,
                'last_active': time.time()
            }
            
            return MessageType.AUTH_RESPONSE, json.dumps({
                'success': True,
                'message': 'Authentication successful'
            }).encode('utf-8')
            
        except json.JSONDecodeError:
            return MessageType.ERROR, b"Invalid authentication data"
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return MessageType.ERROR, b"Authentication failed"

    def verify_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Verify user credentials."""
        logger.debug(f"Verifying user: {username}")
        
        if not username or not password:
            logger.warning("Empty username or password provided")
            return False, 'Username and password are required'
            
        if username not in self.allowed_users:
            logger.warning(f"User not found: {username}")
            return False, 'Invalid username or password'
            
        stored_hash = self.allowed_users[username].get('password')
        if not stored_hash:
            logger.error(f"No password hash found for user: {username}")
            return False, 'User has no password set'
            
        logger.debug(f"Stored hash: {stored_hash}")
        
        # Verify the password
        if not self.security_manager.verify_password(stored_hash, password):
            logger.warning(f"Password verification failed for user: {username}")
            return False, 'Invalid username or password'
            
        # Update last login time
        self.allowed_users[username]['last_login'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if not self._save_users():
            logger.error(f"Failed to update last login time for user: {username}")
            
        logger.info(f"User authenticated successfully: {username}")
        return True, 'Authentication successful'

    def _save_users(self) -> bool:
        """Save users to file."""
        users_file = Path('users.json')
        try:
            with open(users_file, 'w') as f:
                json.dump(self.allowed_users, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving users file: {e}")
            return False

    def add_user(self, username: str, password: str, is_admin: bool = False) -> Tuple[bool, str]:
        """Add a new user."""
        if not username or not password:
            return False, 'Username and password are required'
            
        if username in self.allowed_users:
            return False, 'Username already exists'
            
        self.allowed_users[username] = {
            'password': self.security_manager.hash_password(password),
            'is_admin': is_admin,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'last_login': None
        }
        
        if self._save_users():
            return True, f'User {username} created successfully'
        return False, 'Failed to save user'

def main() -> None:
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remote Control Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    args = parser.parse_args()
    
    server = RemoteControlServer(host=args.host, port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()
    except Exception as e:
        print(f"Error: {e}")
        server.stop()
        sys.exit(1)

if __name__ == '__main__':
    main()
