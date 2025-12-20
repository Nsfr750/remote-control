"""
Mock server for testing the remote control client.
This simulates the server behavior for testing purposes.
"""
import socket
import json
import time
import threading
import queue
from queue import Queue
import random
import base64
import psutil
import platform
import subprocess
import win32clipboard
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import io
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

class MockServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.clients = {}  # type: Dict[str, Dict[str, Any]]
        self.running = False
        self.command_queue = Queue()
        self.screen_width = 1920
        self.screen_height = 1080
        self.chat_history = []  # type: List[Dict[str, str]]
        self.clipboard_content = ""
        self.last_clipboard_update = 0.0
        self.clipboard_lock = threading.Lock()
        self.system_stats_interval = 5.0  # seconds
        self.last_system_stats = {}
        self._init_system_monitoring()
        
    def _init_system_monitoring(self):
        """Initialize system monitoring."""
        self.system_stats_thread = threading.Thread(target=self._update_system_stats, daemon=True)
        self.system_stats_thread.start()
        
        # Start clipboard monitoring
        self.clipboard_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.clipboard_thread.start()

    def _update_system_stats(self):
        """Continuously update system statistics."""
        while self.running:
            try:
                self.last_system_stats = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory': dict(psutil.virtual_memory()._asdict()),
                    'disk_usage': dict(psutil.disk_usage('/')._asdict()),
                    'boot_time': psutil.boot_time(),
                    'users': [dict(user._asdict()) for user in psutil.users()],
                    'timestamp': time.time()
                }
            except Exception as e:
                print(f"Error updating system stats: {e}")
                traceback.print_exc()
            
            time.sleep(self.system_stats_interval)

    def _monitor_clipboard(self):
        """Monitor clipboard for changes and notify clients."""
        last_clipboard = ""
        
        while self.running:
            try:
                win32clipboard.OpenClipboard()
                try:
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                        clipboard_data = win32clipboard.GetClipboardData()
                        if clipboard_data != last_clipboard and time.time() - self.last_clipboard_update > 1.0:
                            last_clipboard = clipboard_data
                            self.clipboard_content = clipboard_data
                            self._broadcast_clipboard_update()
                finally:
                    win32clipboard.CloseClipboard()
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
            
            time.sleep(0.5)

    def _broadcast_clipboard_update(self):
        """Broadcast clipboard update to all connected clients."""
        message = {
            'type': 'clipboard_update',
            'content': self.clipboard_content,
            'timestamp': time.time()
        }
        self._broadcast(message)

    def _broadcast(self, message: Dict[str, Any], client_socket: Optional[socket.socket] = None):
        """Broadcast a message to all connected clients or a specific client."""
        try:
            data = json.dumps(message).encode('utf-8')
            if client_socket:
                client_socket.sendall(len(data).to_bytes(4, byteorder='big') + data)
            else:
                for client in list(self.clients.values()):
                    try:
                        client['socket'].sendall(len(data).to_bytes(4, byteorder='big') + data)
                    except Exception as e:
                        print(f"Error broadcasting to client: {e}")
                        self._remove_client(client['socket'])
        except Exception as e:
            print(f"Error in broadcast: {e}")

    def start(self):
        """Start the mock server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Mock server started on {self.host}:{self.port}")
        
        # Start the command processor in a separate thread
        self.command_thread = threading.Thread(target=self._process_commands)
        self.command_thread.daemon = True
        self.command_thread.start()
        
        # Start system monitoring
        self._init_system_monitoring()
        
        # Accept incoming connections
        try:
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"New connection from {addr}")
                    client_id = f"{addr[0]}:{addr[1]}"
                    self.clients[client_id] = {
                        'socket': client_socket,
                        'address': addr,
                        'authenticated': False,
                        'username': None
                    }
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr, client_id)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except OSError as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the mock server."""
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        print("Mock server stopped")
    
    def _process_commands(self):
        """Process commands from the queue."""
        while self.running:
            try:
                try:
                    command = self.command_queue.get(timeout=1)
                except queue.Empty:
                    # Timeout occurred, just continue the loop
                    continue
                    
                try:
                    if command['type'] == 'screenshot':
                        self._generate_screenshot(command['client_socket'])
                    elif command['type'] == 'mouse_move':
                        print(f"Mouse moved to ({command['x']}, {command['y']})")
                    elif command['type'] == 'mouse_click':
                        button = 'left' if command['button'] == 0 else 'right' if command['button'] == 1 else 'middle'
                        action = 'pressed' if command['pressed'] else 'released'
                        print(f"Mouse {button} button {action} at ({command['x']}, {command['y']})")
                    elif command['type'] == 'key_press':
                        action = 'pressed' if command['pressed'] else 'released'
                        key = command.get('key', 0)
                        key_str = chr(key) if 32 <= key <= 126 else f'0x{key:02X}'
                        print(f"Key {key_str} {action}")
                    elif command['type'] == 'file_upload':
                        self._handle_file_upload(command['client_socket'], command.get('file_data', b''))
                    elif command['type'] == 'file_download':
                        self._handle_file_download(command['client_socket'], command.get('file_path', ''))
                    elif command['type'] == 'chat_message':
                        self._handle_chat_message(command)
                    elif command['type'] == 'get_system_stats':
                        self._send_system_stats(command['client_socket'])
                    elif command['type'] == 'update_clipboard':
                        self._handle_clipboard_update(command)
                    else:
                        print(f"Unknown command type: {command.get('type')}")
                except KeyError as e:
                    print(f"Missing required field in command: {e}. Command: {command}")
                    traceback.print_exc()
                except Exception as e:
                    print(f"Error processing command {command.get('type')}: {str(e)}")
                    traceback.print_exc()
                
                self.command_queue.task_done()
                
            except Exception as e:
                print(f"Error in command processor: {str(e)}")
                traceback.print_exc()
    
    def _handle_chat_message(self, command: Dict[str, Any]):
        """Handle incoming chat message."""
        try:
            message = {
                'type': 'chat_message',
                'sender': command.get('sender', 'Unknown'),
                'message': command['message'],
                'timestamp': time.time()
            }
            self.chat_history.append(message)
            # Keep only last 100 messages
            self.chat_history = self.chat_history[-100:]
            # Broadcast to all clients
            self._broadcast(message)
        except Exception as e:
            print(f"Error handling chat message: {e}")
            traceback.print_exc()
    
    def _send_system_stats(self, client_socket: socket.socket):
        """Send current system statistics to a client."""
        try:
            message = {
                'type': 'system_stats',
                'stats': self.last_system_stats
            }
            self._send_to_client(client_socket, message)
        except Exception as e:
            print(f"Error sending system stats: {e}")
            traceback.print_exc()
    
    def _handle_clipboard_update(self, command: Dict[str, Any]):
        """Handle clipboard update from client."""
        try:
            with self.clipboard_lock:
                self.clipboard_content = command['content']
                self.last_clipboard_update = time.time()
                # Update system clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(self.clipboard_content)
                win32clipboard.CloseClipboard()
                # Broadcast to other clients
                self._broadcast({
                    'type': 'clipboard_update',
                    'content': self.clipboard_content,
                    'timestamp': self.last_clipboard_update
                })
        except Exception as e:
            print(f"Error updating clipboard: {e}")
            traceback.print_exc()
    
    def _send_to_client(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Send a message to a specific client."""
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.sendall(len(data).to_bytes(4, byteorder='big') + data)
        except Exception as e:
            print(f"Error sending to client: {e}")
            self._remove_client(client_socket)
    
    def _remove_client(self, client_socket: socket.socket):
        """Remove a client from the clients dictionary."""
        for client_id, client in list(self.clients.items()):
            if client['socket'] == client_socket:
                try:
                    client_socket.close()
                except:
                    pass
                self.clients.pop(client_id, None)
                print(f"Client {client_id} disconnected")
                break
    
    def _handle_client(self, client_socket, addr, client_id):
        """Handle a client connection."""
        try:
            # Send initial connection info
            self._send_to_client(client_socket, {
                'type': 'connection_established',
                'client_id': client_id,
                'server_time': time.time(),
                'chat_history': self.chat_history[-50:],  # Send last 50 messages
                'clipboard': self.clipboard_content
            })
            
            while self.running:
                try:
                    # Receive message length (first 4 bytes)
                    msg_length_data = client_socket.recv(4)
                    if not msg_length_data:
                        break
                        
                    length = int.from_bytes(msg_length_data, byteorder='big')
                    if length > 10 * 1024 * 1024:  # 10MB max message size
                        print(f"Message too large: {length} bytes")
                        break
                    
                    # Receive the actual message
                    data = bytearray()
                    while len(data) < length:
                        packet = client_socket.recv(min(4096, length - len(data)))
                        if not packet:
                            break
                        data.extend(packet)
                    
                    if not data:
                        break
                    
                    # Process the received message
                    self._process_message(client_socket, data, client_id)
                    
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    print(f"Client {client_id} disconnected")
                    break
                except Exception as e:
                    print(f"Error receiving from client {client_id}: {e}")
                    traceback.print_exc()
                    break
                    
        except Exception as e:
            print(f"Error in client handler for {client_id}: {e}")
            traceback.print_exc()
        finally:
            self._remove_client(client_socket)
    
    def _process_message(self, client_socket, data, client_id):
        """Process a received message."""
        try:
            # Try to decode as JSON first (for control messages)
            try:
                message = json.loads(data.decode('utf-8'))
                message_type = message.get('type')
                
                if message_type == 'auth':
                    # Simulate authentication
                    response = {
                        'type': 'auth_response',
                        'status': 'success', 
                        'session_id': f'session_{int(time.time())}',
                        'message': 'Authentication successful'
                    }
                    self._send_to_client(client_socket, response)
                    
                    # Update client info
                    for cid, client in self.clients.items():
                        if client['socket'] == client_socket:
                            client['authenticated'] = True
                            client['username'] = message.get('username', f'user_{cid}')
                            break
                    
                elif message_type == 'screenshot_request':
                    self.command_queue.put({'type': 'screenshot', 'client_socket': client_socket})
                    
                elif message_type == 'mouse_move':
                    self.command_queue.put({
                        'type': 'mouse_move',
                        'x': message['x'],
                        'y': message['y']
                    })
                    
                elif message_type == 'mouse_click':
                    self.command_queue.put({
                        'type': 'mouse_click',
                        'button': message['button'],
                        'pressed': message['pressed'],
                        'x': message['x'],
                        'y': message['y']
                    })
                    
                elif message_type == 'key_press':
                    self.command_queue.put({
                        'type': 'key_press',
                        'key': message['key'],
                        'pressed': message['pressed']
                    })
                    
                elif message_type == 'file_upload':
                    self.command_queue.put({
                        'type': 'file_upload',
                        'client_socket': client_socket,
                        'file_data': message['data']
                    })
                    
                elif message_type == 'file_download':
                    self.command_queue.put({
                        'type': 'file_download',
                        'client_socket': client_socket,
                        'file_path': message['path']
                    })
                    
                elif message_type == 'chat_message':
                    self.command_queue.put({
                        'type': 'chat_message',
                        'client_socket': client_socket,
                        'sender': self.clients.get(client_id, {}).get('username', 'unknown'),
                        'message': message['message']
                    })
                    
                elif message_type == 'get_system_stats':
                    self.command_queue.put({
                        'type': 'get_system_stats',
                        'client_socket': client_socket
                    })
                    
                elif message_type == 'update_clipboard':
                    self.command_queue.put({
                        'type': 'update_clipboard',
                        'client_socket': client_socket,
                        'content': message['content']
                    })
                    
                else:
                    print(f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                # Handle binary data (e.g., file chunks)
                print(f"Received binary data: {len(data)} bytes")
                
        except Exception as e:
            print(f"Error processing message from {client_id}: {e}")
            traceback.print_exc()
    
    def _send_message(self, client_socket, msg_type, data):
        """Send a message to the client."""
        try:
            message = {'type': msg_type, 'data': data}
            self._send_to_client(client_socket, message)
        except Exception as e:
            print(f"Error sending message: {e}")
            traceback.print_exc()
    
    def _generate_screenshot(self, client_socket):
    """Generate a mock screenshot with system information using Wand."""
    try:
        # Create a new image with Wand
        with Image(width=self.screen_width, height=self.screen_height, 
                  background=Color('white')) as img:
            
            draw = Drawing()
            
            # Draw header
            draw.fill_color = Color('#2c3e50')
            draw.rectangle(left=0, top=0, 
                         width=self.screen_width, height=30)
            
            # Draw header text
            header = f"Remote Control Server - {time.ctime()}"
            draw.fill_color = Color('white')
            draw.font_size = 16
            draw.text(10, 20, header)
            
            # System information section
            y_offset = 40
            draw.fill_color = Color('black')
            draw.text(20, y_offset, "System Information:")
            y_offset += 25
            
            # Get system info
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # System info text
                sys_info = [
                    f"CPU: {cpu_percent}%",
                    f"Memory: {mem.percent}% used ({mem.used//(1024*1024)}MB / {mem.total//(1024*1024)}MB)",
                    f"Disk: {disk.percent}% used ({disk.used//(1024*1024)}MB / {disk.total//(1024*1024)}MB)",
                    f"Connected Clients: {len([c for c in self.clients.values() if c.get('authenticated')])}"
                ]
                
                for info in sys_info:
                    draw.text(30, y_offset, info)
                    y_offset += 20
                    
            except Exception as e:
                error_msg = "System information unavailable"
                draw.fill_color = Color('red')
                draw.text(30, y_offset, error_msg)
                y_offset += 20
            
            # Add recent chat messages
            y_offset += 20
            draw.fill_color = Color('black')
            draw.text(20, y_offset, "Recent Chat:")
            y_offset += 25
            
            for msg in self.chat_history[-5:]:  # Show last 5 messages
                msg_text = f"{msg.get('sender', 'Unknown')}: {msg.get('message', '')}"
                draw.fill_color = Color('#2c3e50')
                draw.text(30, y_offset, msg_text)
                y_offset += 20
                if y_offset > self.screen_height - 50:
                    break
            
            # Add footer
            footer = f"Server: {platform.node()} | {len(self.clients)} clients connected"
            draw.fill_color = Color('#2c3e50')
            draw.rectangle(left=0, top=self.screen_height-25, 
                         width=self.screen_width, height=self.screen_height)
            draw.fill_color = Color('white')
            draw.text(10, self.screen_height-20, footer)
            
            # Add a subtle grid
            draw.stroke_color = Color('#f0f0f0')
            for i in range(0, self.screen_width, 50):
                draw.line((i, 30), (i, self.screen_height-25))
            for i in range(30, self.screen_height-25, 50):
                draw.line((0, i), (self.screen_width, i))
            
            # Apply all drawings
            draw(img)
            
            # Convert to JPEG and get binary data
            img.format = 'jpeg'
            img.compression_quality = 70
            img_data = img.make_blob()
            
            # Send the screenshot
            self._send_message(client_socket, 'screenshot', {
                'data': base64.b64encode(img_data).decode('utf-8'),
                'width': self.screen_width,
                'height': self.screen_height,
                'timestamp': time.time()
            })
            
    except Exception as e:
        print(f"Error generating screenshot: {e}")
        traceback.print_exc()
        
        # Fallback to simple screenshot on error
        try:
            with Image(width=800, height=600, background=Color('white')) as img:
                draw = Drawing()
                draw.fill_color = Color('red')
                draw.text(10, 10, f"Error generating screenshot: {e}")
                draw(img)
                
                img.format = 'jpeg'
                img_data = img.make_blob()
                
                self._send_message(client_socket, 'screenshot', {
                    'data': base64.b64encode(img_data).decode('utf-8'),
                    'width': 800,
                    'height': 600,
                    'error': str(e)
                })
        except Exception as e2:
            print(f"Error in fallback screenshot: {e2}")
    
    def _handle_file_upload(self, client_socket, file_data):
        """Handle file upload."""
        try:
            # In a real implementation, save the file
            print(f"Received file data: {len(file_data)} bytes")
            self._send_message(client_socket, 'file_upload_response', {
                'status': 'success',
                'message': 'File uploaded successfully',
                'size': len(file_data)
            })
        except Exception as e:
            print(f"Error handling file upload: {e}")
            self._send_message(client_socket, 'file_upload_response', {
                'status': 'error',
                'message': str(e)
            })
    
    def _handle_file_download(self, client_socket, file_path):
        """Handle file download."""
        try:
            # In a real implementation, read the file
            # For testing, create a dummy file
            file_content = f"This is a test file for {file_path}".encode('utf-8')
            
            self._send_message(client_socket, 'file_download_response', {
                'status': 'success',
                'filename': file_path.split('/')[-1],
                'data': base64.b64encode(file_content).decode('utf-8'),
                'size': len(file_content)
            })
        except Exception as e:
            print(f"Error handling file download: {e}")
            self._send_message(client_socket, 'file_download_response', {
                'status': 'error',
                'message': str(e)
            })

if __name__ == "__main__":
    server = MockServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
