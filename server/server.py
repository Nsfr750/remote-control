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
from typing import Dict, Optional, Tuple, Callable, Any

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
        """Initialize the server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.running = False
        self.clients: Dict[str, Dict] = {}
        self.auth_required = True
        self.server_socket: Optional[socket.socket] = None
        
        # Initialize security manager first
        self.security_manager = SecurityManager()
        
        # Then load users which depends on security_manager
        self.allowed_users = self._load_users()
        
        # Platform-specific imports
        self.platform = platform.system().lower()
        self.screen_controller = self._get_screen_controller()
        self.input_controller = self._get_input_controller()
        
        # File transfer settings
        self.file_transfer = FileTransfer()
        self.allowed_directories = self._get_allowed_directories()
    
    def _load_users(self) -> Dict[str, dict]:
        """Load user credentials from file.
        
        Returns:
            Dict with usernames as keys and user data as values
        """
        users_file = Path('users.json')
        default_users = {
            'admin': {
                'password': self._hash_password('admin'),
                'is_admin': True,
                'created_at': '2023-01-01T00:00:00Z',
                'last_login': None
            }
        }
        
        if users_file.exists():
            try:
                with open(users_file, 'r') as f:
                    users = json.load(f)
                    # Convert old format if needed
                    if users and isinstance(next(iter(users.values())), str):
                        users = {user: {'password': pwd, 'is_admin': False} 
                               for user, pwd in users.items()}
                    return users
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading users file: {e}")
                logger.info("Creating new users file with default admin")
        
        # Create default admin user if no users file exists or there was an error
        try:
            with open(users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
            logger.info("Created default admin user with password 'admin'")
            return default_users
            
        except Exception as e:
            logger.error(f"Error creating default users file: {e}")
            return default_users
        except IOError as e:
            logger.error(f"Error creating default users file: {e}")
            return {}
    
    def _get_allowed_directories(self) -> Dict[str, str]:
        """Get allowed directories for file operations."""
        if self.platform == 'windows':
            return {
                'desktop': str(Path.home() / 'Desktop'),
                'documents': str(Path.home() / 'Documents'),
                'downloads': str(Path.home() / 'Downloads'),
            }
        else:  # Linux/Unix
            return {
                'home': str(Path.home()),
                'desktop': str(Path.home() / 'Desktop') if (Path.home() / 'Desktop').exists() else str(Path.home()),
                'downloads': str(Path.home() / 'Downloads') if (Path.home() / 'Downloads').exists() else str(Path.home()),
            }
    
    def _get_screen_controller(self):
        """Get the appropriate screen controller for the platform."""
        try:
            if self.platform == 'windows':
                from screen.windows import WindowsScreenController
                return WindowsScreenController()
            else:  # Linux/Unix
                from screen.linux import LinuxScreenController
                return LinuxScreenController()
        except ImportError as e:
            logger.error(f"Failed to load screen controller: {e}")
            return None
    
    def _get_input_controller(self):
        """Get the appropriate input controller for the platform."""
        try:
            if self.platform == 'windows':
                from input.windows import WindowsInputController
                return WindowsInputController()
            else:  # Linux/Unix
                from input.linux import LinuxInputController
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
                    logger.info(f"New connection from {client_address}")
                    
                    # Start a new thread for each client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except OSError as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    
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
        """Handle a client connection.
        
        Args:
            client_socket: Client socket
            client_address: Client address (ip, port)
        """
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
        """Handle an incoming message.
        
        Args:
            msg_type: Message type
            data: Message data
            client_socket: Client socket
            client_id: Client ID
            username: Authenticated username (if any)
            
        Returns:
            Optional tuple of (response_type, response_data)
        """
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
    
    def _hash_password(self, password: str) -> str:
        """Hash a password for storage."""
        return self.security_manager.hash_password(password)
        
    def verify_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Verify user credentials.
        
        Args:
            username: Username to verify
            password: Password to verify
            
        Returns:
            Tuple of (success, message)
        """
        if username not in self.allowed_users:
            return False, 'Invalid username or password'
            
        stored_hash = self.allowed_users[username].get('password')
        if not stored_hash:
            return False, 'User has no password set'
            
        if not self.security_manager.verify_password(password, stored_hash):
            return False, 'Invalid username or password'
            
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
        """Add a new user.
        
        Args:
            username: Username for the new user
            password: Password for the new user
            is_admin: Whether the user should have admin privileges
            
        Returns:
            Tuple of (success, message)
        """
        if not username or not password:
            return False, 'Username and password are required'
            
        if username in self.allowed_users:
            return False, 'Username already exists'
            
        self.allowed_users[username] = {
            'password': self._hash_password(password),
            'is_admin': is_admin,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'last_login': None
        }
        
        if self._save_users():
            return True, f'User {username} created successfully'
        return False, 'Failed to save user'
    
    def update_user_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """Update a user's password.
        
        Args:
            username: Username to update
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        if username not in self.allowed_users:
            return False, 'User not found'
            
        self.allowed_users[username]['password'] = self._hash_password(new_password)
        
        if self._save_users():
            return True, 'Password updated successfully'
        return False, 'Failed to update password'
    
    # In server/server.py, update the _handle_auth method
def _handle_auth(self, data: bytes, client_id: str) -> Tuple[MessageType, bytes]:
    """Handle authentication.
    
    Args:
        data: Authentication data
        client_id: Client ID
        
    Returns:
        Tuple of (response_type, response_data)
    """
    try:
        auth_data = json.loads(data.decode('utf-8'))
        username = auth_data.get('username')
        password = auth_data.get('password')
        
        if not username or not password:
            logger.warning("Missing username or password in auth request")
            return MessageType.AUTH_RESPONSE, json.dumps({
                'success': False,
                'message': 'Missing username or password'
            }).encode('utf-8')
            
        # Verify user credentials
        if username not in self.allowed_users:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return MessageType.AUTH_RESPONSE, json.dumps({
                'success': False,
                'message': 'Invalid username or password'
            }).encode('utf-8')
            
        # Get stored password hash
        stored_hash = self.allowed_users[username].get('password', '')
        if not stored_hash:
            logger.warning(f"No password hash found for user '{username}'")
            return MessageType.AUTH_RESPONSE, json.dumps({
                'success': False,
                'message': 'Invalid authentication data'
            }).encode('utf-8')
            
        # Verify password
        salt, hashed = stored_hash.split(':', 1) if ':' in stored_hash else ('', stored_hash)
        if not self.security_manager.verify_password(password, salt, hashed):
            logger.warning(f"Authentication failed: invalid password for user '{username}'")
            return MessageType.AUTH_RESPONSE, json.dumps({
                'success': False,
                'message': 'Invalid username or password'
            }).encode('utf-8')
        
        # Update last login time
        self.allowed_users[username]['last_login'] = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        self._save_users()
        
        # Authentication successful
        self.clients[client_id] = {
            'username': username,
            'authenticated': True,
            'is_admin': self.allowed_users[username].get('is_admin', False),
            'last_active': time.time()
        }
        
        logger.info(f"User '{username}' authenticated successfully")
        return MessageType.AUTH_RESPONSE, json.dumps({
            'success': True,
            'message': 'Authentication successful',
            'user': username,
            'is_admin': self.allowed_users[username].get('is_admin', False)
        }).encode('utf-8')
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in auth request")
        return MessageType.ERROR, b'Invalid authentication data'
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        return MessageType.ERROR, b'Authentication failed'
    
    def _handle_mouse_move(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle mouse movement.
        
        Args:
            data: Mouse movement data
            
        Returns:
            Tuple of (response_type, response_data)
        """
        if not self.input_controller:
            return MessageType.ERROR, b"Input controller not available"
            
        try:
            mouse_event = MouseEvent.from_bytes(data)
            self.input_controller.move_mouse(mouse_event.x, mouse_event.y)
            return MessageType.INFO, b"Mouse moved"
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _handle_mouse_click(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle mouse click.
        
        Args:
            data: Mouse click data
            
        Returns:
            Tuple of (response_type, response_data)
        """
        if not self.input_controller:
            return MessageType.ERROR, b"Input controller not available"
            
        try:
            mouse_event = MouseEvent.from_bytes(data)
            if mouse_event.pressed:
                self.input_controller.mouse_down(mouse_event.button)
            else:
                self.input_controller.mouse_up(mouse_event.button)
            return MessageType.INFO, b"Mouse click handled"
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _handle_key_event(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle keyboard event.
        
        Args:
            data: Key event data
            
        Returns:
            Tuple of (response_type, response_data)
        """
        if not self.input_controller:
            return MessageType.ERROR, b"Input controller not available"
            
        try:
            key_event = KeyEvent.from_bytes(data)
            if key_event.pressed:
                self.input_controller.key_down(key_event.key)
            else:
                self.input_controller.key_up(key_event.key)
            return MessageType.INFO, b"Key event handled"
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _handle_screenshot(self) -> Tuple[MessageType, bytes]:
        """Take a screenshot.
        
        Returns:
            Tuple of (response_type, screenshot_data)
        """
        if not self.screen_controller:
            return MessageType.ERROR, b"Screen controller not available"
            
        try:
            screenshot_data = self.screen_controller.take_screenshot()
            return MessageType.SCREENSHOT, screenshot_data
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _handle_file_transfer(self, data: bytes, client_socket: socket.socket) -> Tuple[MessageType, bytes]:
        """Handle file transfer operations.
        
        Args:
            data: File transfer message data
            client_socket: Client socket for streaming
            
        Returns:
            Tuple of (response_type, response_data)
        """
        try:
            msg = FileTransferMessage.deserialize(data)
            msg_type = msg.get('type')
            
            if msg_type == FileTransferMessage.Type.LIST_DIR:
                path = msg.get('path', '.')
                file_list = self.file_transfer.list_directory(path)
                return MessageType.FILE_TRANSFER, FileTransferMessage.serialize({
                    'type': 'list_dir',
                    'files': file_list
                })
                
            elif msg_type == FileTransferMessage.Type.GET_FILE:
                path = msg.get('path')
                offset = msg.get('offset', 0)
                
                # Check if path is within allowed directories
                if not self._is_path_allowed(path):
                    return MessageType.ERROR, b"Access to this path is not allowed"
                
                # Send file in chunks
                with open(path, 'rb') as f:
                    f.seek(offset)
                    while True:
                        chunk = f.read(FileTransfer.CHUNK_SIZE)
                        if not chunk:
                            break
                        self._send_message(client_socket, MessageType.FILE_TRANSFER, chunk)
                
                return None  # No response needed, already sent
                
            elif msg_type == FileTransferMessage.Type.PUT_FILE:
                path = msg.get('path')
                size = msg.get('size', 0)
                mode = msg.get('mode', 'wb')
                
                # Check if path is within allowed directories
                if not self._is_path_allowed(path):
                    return MessageType.ERROR, b"Access to this path is not allowed"
                
                # Receive file in chunks
                received = 0
                with open(path, mode) as f:
                    while received < size:
                        chunk = client_socket.recv(min(FileTransfer.CHUNK_SIZE, size - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                
                return MessageType.INFO, b"File received successfully"
                
            elif msg_type == FileTransferMessage.Type.DELETE:
                path = msg.get('path')
                
                # Check if path is within allowed directories
                if not self._is_path_allowed(path):
                    return MessageType.ERROR, b"Access to this path is not allowed"
                
                self.file_transfer.delete_path(path)
                return MessageType.INFO, b"File/directory deleted"
                
            elif msg_type == FileTransferMessage.Type.MOVE:
                src = msg.get('src')
                dst = msg.get('dst')
                
                # Check if paths are within allowed directories
                if not (self._is_path_allowed(src) and self._is_path_allowed(dst)):
                    return MessageType.ERROR, b"Access to one or both paths is not allowed"
                
                self.file_transfer.move_path(src, dst)
                return MessageType.INFO, b"File/directory moved"
                
            elif msg_type == FileTransferMessage.Type.COPY:
                src = msg.get('src')
                dst = msg.get('dst')
                
                # Check if paths are within allowed directories
                if not (self._is_path_allowed(src) and self._is_path_allowed(dst)):
                    return MessageType.ERROR, b"Access to one or both paths is not allowed"
                
                self.file_transfer.copy_path(src, dst)
                return MessageType.INFO, b"File/directory copied"
                
            elif msg_type == FileTransferMessage.Type.MKDIR:
                path = msg.get('path')
                
                # Check if path is within allowed directories
                if not self._is_path_allowed(path):
                    return MessageType.ERROR, b"Access to this path is not allowed"
                
                self.file_transfer.create_directory(path)
                return MessageType.INFO, b"Directory created"
                
            else:
                return MessageType.ERROR, b"Unknown file transfer operation"
                
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if a path is within allowed directories.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is allowed, False otherwise
        """
        try:
            path = os.path.abspath(path)
            for allowed_dir in self.allowed_directories.values():
                if os.path.commonpath([path, os.path.abspath(allowed_dir)]) == os.path.abspath(allowed_dir):
                    return True
            return False
        except (ValueError, TypeError):
            return False
    
    def _handle_clipboard_update(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle clipboard update.
        
        Args:
            data: Clipboard data
            
        Returns:
            Tuple of (response_type, response_data)
        """
        try:
            # This is a placeholder - actual implementation would depend on the platform
            # and would require additional permissions on some systems
            return MessageType.INFO, b"Clipboard update received (not implemented)"
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _handle_system_command(self, data: bytes) -> Tuple[MessageType, bytes]:
        """Handle system command execution.
        
        Args:
            data: Command data
            
        Returns:
            Tuple of (response_type, command output)
        """
        try:
            # This is a security-sensitive operation and should be restricted
            # In a production environment, you'd want to implement strict controls
            # over which commands can be executed
            import subprocess
            
            command = data.decode('utf-8')
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            output = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            return MessageType.INFO, json.dumps(output).encode('utf-8')
            
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _handle_info(self) -> Tuple[MessageType, bytes]:
        """Get system information.
        
        Returns:
            Tuple of (response_type, system_info)
        """
        try:
            info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': platform.node(),
                'cpu_count': os.cpu_count(),
                'memory': self._get_memory_info(),
                'disks': self._get_disk_info()
            }
            return MessageType.INFO, json.dumps(info).encode('utf-8')
        except Exception as e:
            return MessageType.ERROR, str(e).encode('utf-8')
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        try:
            if self.platform == 'windows':
                import psutil
                mem = psutil.virtual_memory()
                return {
                    'total': mem.total,
                    'available': mem.available,
                    'percent': mem.percent,
                    'used': mem.used,
                    'free': mem.free
                }
            else:  # Linux/Unix
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f:
                        key, value = line.split(':')
                        meminfo[key.strip()] = value.strip()
                    
                    total = int(meminfo['MemTotal'].split()[0]) * 1024
                    free = int(meminfo['MemFree'].split()[0]) * 1024
                    available = int(meminfo.get('MemAvailable', '0 kB').split()[0]) * 1024
                    used = total - free
                    percent = (used / total) * 100
                    
                    return {
                        'total': total,
                        'available': available,
                        'percent': percent,
                        'used': used,
                        'free': free
                    }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {'error': str(e)}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information."""
        try:
            import psutil
            
            disks = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except Exception as e:
                    logger.error(f"Error getting disk info for {partition.mountpoint}: {e}")
            
            return disks
            
        except Exception as e:
            logger.error(f"Error getting disk info: {e}")
            return {'error': str(e)}
    
    def _send_message(self, client_socket: socket.socket, msg_type: MessageType, data: bytes) -> None:
        """Send a message to a client.
        
        Args:
            client_socket: Client socket
            msg_type: Message type
            data: Message data
        """
        try:
            # Encrypt data if needed
            # In a real implementation, you'd want to encrypt sensitive data
            encrypted_data = data
            
            # Create message
            msg = Message(msg_type, encrypted_data)
            client_socket.sendall(msg.serialize())
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remote Control Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on (default: 5000)')
    parser.add_argument('--no-auth', action='store_true', help='Disable authentication (insecure!)')
    
    args = parser.parse_args()
    
    server = RemoteControlServer(host=args.host, port=args.port)
    server.auth_required = not args.no_auth
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        server.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
