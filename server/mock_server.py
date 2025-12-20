"""
Mock server for testing the remote control client.
This simulates the server behavior for testing purposes.
"""
import socket
import json
import time
import threading
from queue import Queue
import random
import base64
from PIL import Image, ImageDraw
import io

class MockServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.clients = {}
        self.running = False
        self.command_queue = Queue()
        self.screen_width = 1920
        self.screen_height = 1080
        
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
        
        # Accept incoming connections
        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()
                print(f"New connection from {addr}")
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
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
                command = self.command_queue.get(timeout=1)
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
                    print(f"Key {chr(command['key']) if 32 <= command['key'] <= 126 else f'0x{command[key]:02X}'} {action}")
                elif command['type'] == 'file_upload':
                    self._handle_file_upload(command['client_socket'], command['file_data'])
                elif command['type'] == 'file_download':
                    self._handle_file_download(command['client_socket'], command['file_path'])
                
                self.command_queue.task_done()
            except Exception as e:
                print(f"Error processing command: {e}")
    
    def _handle_client(self, client_socket, addr):
        """Handle a client connection."""
        try:
            while self.running:
                # Receive message length (first 4 bytes)
                msg_length = client_socket.recv(4)
                if not msg_length:
                    break
                    
                length = int.from_bytes(msg_length, byteorder='big')
                
                # Receive the actual message
                data = b''
                while len(data) < length:
                    packet = client_socket.recv(length - len(data))
                    if not packet:
                        break
                    data += packet
                
                if not data:
                    break
                
                # Process the received message
                self._process_message(client_socket, data)
                
        except ConnectionResetError:
            print(f"Client {addr} disconnected unexpectedly")
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()
            print(f"Connection closed with {addr}")
    
    def _process_message(self, client_socket, data):
        """Process a received message."""
        try:
            # Try to decode as JSON first (for control messages)
            try:
                message = json.loads(data.decode('utf-8'))
                message_type = message.get('type')
                
                if message_type == 'auth':
                    # Simulate authentication
                    response = {'status': 'success', 'session_id': 'mock_session_123'}
                    self._send_message(client_socket, 'auth_response', response)
                    
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
                    
            except json.JSONDecodeError:
                # Handle binary data (e.g., file chunks)
                print(f"Received binary data: {len(data)} bytes")
                
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _send_message(self, client_socket, msg_type, data):
        """Send a message to the client."""
        try:
            message = {'type': msg_type, 'data': data}
            message_bytes = json.dumps(message).encode('utf-8')
            # Send message length (4 bytes)
            client_socket.send(len(message_bytes).to_bytes(4, byteorder='big'))
            # Send the message
            client_socket.sendall(message_bytes)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _generate_screenshot(self, client_socket):
        """Generate a mock screenshot."""
        try:
            # Create a simple image with some text
            img = Image.new('RGB', (self.screen_width, self.screen_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add some text to the image
            text = f"Mock Server Screenshot\n{time.ctime()}"
            text_bbox = draw.textbbox((0, 0), text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (self.screen_width - text_width) // 2
            y = (self.screen_height - text_height) // 2
            
            draw.text((x, y), text, fill='black')
            
            # Add a simple pattern
            for i in range(0, self.screen_width, 20):
                draw.line([(i, 0), (i, self.screen_height)], fill='lightgray')
            for i in range(0, self.screen_height, 20):
                draw.line([(0, i), (self.screen_width, i)], fill='lightgray')
            
            # Convert to JPEG and send
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=70)
            img_data = img_byte_arr.getvalue()
            
            # Send the screenshot
            self._send_message(client_socket, 'screenshot', {
                'data': base64.b64encode(img_data).decode('utf-8'),
                'width': self.screen_width,
                'height': self.screen_height
            })
            
        except Exception as e:
            print(f"Error generating screenshot: {e}")
    
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
