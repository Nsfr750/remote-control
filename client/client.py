"""
Remote Control Client

Handles the GUI and connection to the remote control server.
"""
import os
import sys
import json
import socket
import logging
import threading
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

# Add parent directory to path for module imports
sys.path.append(str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget,
                            QFileDialog, QListWidget, QSystemTrayIcon, QStyle, QStatusBar,
                            QDialog, QDialogButtonBox, QFormLayout, QCheckBox, QProgressBar,
                            QInputDialog)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QSettings
from PyQt6.QtGui import QPixmap, QIcon, QAction, QCursor

from common.protocol import Message, MessageType, AuthMessage, MouseEvent, KeyEvent
from common.security import SecurityManager
from common.file_transfer import FileTransfer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RemoteControlClient')

class RemoteControlClient(QMainWindow):
    """Main client application window."""
    
    def __init__(self):
        super().__init__()
        
        self.connected = False
        self.authenticated = False
        self.client_socket = None
        self.receive_thread = None
        self.screen_timer = None
        self.current_screen = None
        self.screen_scale = 1.0
        self.drag_start_pos = None
        self.selection_rect = None
        self.dragging = False
        self.last_mouse_pos = None
        self.security_manager = SecurityManager()
        self.file_transfer = FileTransfer()
        
        self.init_ui()
        self.init_tray_icon()
        self.show_connection_dialog()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Remote Control Client")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Remote control tab
        self.remote_tab = QWidget()
        self.remote_layout = QVBoxLayout(self.remote_tab)
        
        # Screen display
        self.screen_label = QLabel()
        self.screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screen_label.setStyleSheet("background-color: black;")
        self.screen_label.mousePressEvent = self.screen_mouse_press
        self.screen_label.mouseReleaseEvent = self.screen_mouse_release
        self.screen_label.mouseMoveEvent = self.screen_mouse_move
        
        # Control buttons
        self.control_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_connection)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.request_screen_update)
        self.btn_refresh.setEnabled(False)
        
        self.btn_fullscreen = QPushButton("Fullscreen")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.btn_fullscreen.setEnabled(False)
        
        self.control_layout.addWidget(self.btn_connect)
        self.control_layout.addWidget(self.btn_refresh)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.btn_fullscreen)
        
        # Add widgets to remote tab
        self.remote_layout.addWidget(self.screen_label, 1)
        self.remote_layout.addLayout(self.control_layout)
        
        # File transfer tab
        self.files_tab = QWidget()
        self.files_layout = QVBoxLayout(self.files_tab)
        
        # File transfer controls
        self.files_control_layout = QHBoxLayout()
        
        self.btn_upload = QPushButton("Upload")
        self.btn_upload.clicked.connect(self.upload_file)
        self.btn_upload.setEnabled(False)
        
        self.btn_download = QPushButton("Download")
        self.btn_download.clicked.connect(self.download_file)
        self.btn_download.setEnabled(False)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_file)
        self.btn_delete.setEnabled(False)
        
        self.btn_new_folder = QPushButton("New Folder")
        self.btn_new_folder.clicked.connect(self.create_folder)
        self.btn_new_folder.setEnabled(False)
        
        self.files_control_layout.addWidget(self.btn_upload)
        self.files_control_layout.addWidget(self.btn_download)
        self.files_control_layout.addWidget(self.btn_delete)
        self.files_control_layout.addWidget(self.btn_new_folder)
        self.files_control_layout.addStretch()
        
        # File browser
        self.file_browser_layout = QHBoxLayout()
        
        self.local_files = QListWidget()
        self.remote_files = QListWidget()
        
        self.file_browser_layout.addWidget(self.local_files, 1)
        self.file_browser_layout.addWidget(self.remote_files, 1)
        
        # Add widgets to files tab
        self.files_layout.addLayout(self.files_control_layout)
        self.files_layout.addLayout(self.file_browser_layout, 1)
        
        # System info tab
        self.info_tab = QWidget()
        self.info_layout = QVBoxLayout(self.info_tab)
        
        self.info_text = QLabel("System information will be displayed here")
        self.info_text.setWordWrap(True)
        self.info_layout.addWidget(self.info_text)
        
        # Add tabs
        self.tabs.addTab(self.remote_tab, "Remote Control")
        self.tabs.addTab(self.files_tab, "File Transfer")
        self.tabs.addTab(self.info_tab, "System Info")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")
        
        # Set initial state
        self.update_ui_state()
    
    def init_tray_icon(self):
        """Initialize the system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_normal)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Toggle window on tray icon click
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def show_connection_dialog(self):
        """Show the connection dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect to Server")
        
        layout = QFormLayout()
        
        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("5000")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.remember_check = QCheckBox("Remember credentials")
        
        layout.addRow("Host:", self.host_input)
        layout.addRow("Port:", self.port_input)
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("", self.remember_check)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addRow(buttons)
        dialog.setLayout(layout)
        
        # Load saved credentials if available
        self.load_credentials()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.host = self.host_input.text()
            self.port = int(self.port_input.text())
            self.username = self.username_input.text()
            self.password = self.password_input.text()
            
            if self.remember_check.isChecked():
                self.save_credentials()
            else:
                self.clear_credentials()
            
            self.connect_to_server()
        else:
            # If user cancels, show the dialog again
            QTimer.singleShot(0, self.show_connection_dialog)
    
    def load_credentials(self):
        """Load saved credentials from settings."""
        settings = QSettings("RemoteControl", "Client")
        
        self.host_input.setText(settings.value("host", "localhost"))
        self.port_input.setText(settings.value("port", "5000"))
        self.username_input.setText(settings.value("username", ""))
        self.password_input.setText(settings.value("password", ""))
        self.remember_check.setChecked(settings.value("remember", False, bool))
    
    def save_credentials(self):
        """Save credentials to settings."""
        settings = QSettings("RemoteControl", "Client")
        
        settings.setValue("host", self.host_input.text())
        settings.setValue("port", self.port_input.text())
        settings.setValue("username", self.username_input.text())
        settings.setValue("password", self.password_input.text())
        settings.setValue("remember", self.remember_check.isChecked())
    
    def clear_credentials(self):
        """Clear saved credentials."""
        settings = QSettings("RemoteControl", "Client")
        settings.clear()
    
    def connect_to_server(self):
        """Connect to the remote server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
            # Send authentication
            self.authenticate()
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to server: {e}")
            self.show_connection_dialog()
    
    def authenticate(self):
        """Authenticate with the server."""
        auth_msg = AuthMessage(self.username, self.password)
        self.send_message(MessageType.AUTH, auth_msg.to_bytes())
    
    def send_message(self, msg_type: MessageType, data: bytes):
        """Send a message to the server."""
        if not self.client_socket:
            return
            
        try:
            msg = Message(msg_type, data)
            self.client_socket.sendall(msg.serialize())
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect_from_server()
    
    def receive_messages(self):
        """Receive messages from the server in a separate thread."""
        try:
            while True:
                # Receive message header (8 bytes: 4 for type, 4 for length)
                header = self.client_socket.recv(8)
                if not header:
                    break
                
                # Parse message
                msg_type = MessageType(int.from_bytes(header[:4], byteorder='big'))
                data_len = int.from_bytes(header[4:8], byteorder='big')
                
                # Receive message data
                data = b''
                while len(data) < data_len:
                    chunk = self.client_socket.recv(min(4096, data_len - len(data)))
                    if not chunk:
                        break
                    data += chunk
                
                if len(data) != data_len:
                    logger.warning("Incomplete message received")
                    continue
                
                # Process message in the main thread
                self.process_message(msg_type, data)
                
        except ConnectionResetError:
            logger.info("Connection reset by server")
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
        finally:
            self.disconnect_from_server()
    
    def process_message(self, msg_type: MessageType, data: bytes):
        """Process a received message in the main thread."""
        if msg_type == MessageType.AUTH_RESPONSE:
            self.handle_auth_response(data)
        elif msg_type == MessageType.SCREENSHOT:
            self.update_screen(data)
        elif msg_type == MessageType.FILE_TRANSFER:
            self.handle_file_transfer(data)
        elif msg_type == MessageType.INFO:
            self.update_system_info(data)
        elif msg_type == MessageType.ERROR:
            self.show_error(data.decode('utf-8', errors='replace'))
    
    def handle_auth_response(self, data: bytes):
        """Handle authentication response from server."""
        try:
            response = json.loads(data.decode('utf-8'))
            if response.get('success'):
                self.authenticated = True
                self.connected = True
                self.status_bar.showMessage(f"Connected to {self.host}:{self.port} as {self.username}")
                
                # Start screen updates
                self.start_screen_updates()
                
                # Update UI
                self.update_ui_state()
                
                # Request system info
                self.request_system_info()
                
            else:
                error_msg = response.get('message', 'Authentication failed')
                QMessageBox.warning(self, "Authentication Failed", error_msg)
                self.disconnect_from_server()
                
        except Exception as e:
            logger.error(f"Error processing auth response: {e}")
            self.disconnect_from_server()
    
    def update_screen(self, image_data: bytes):
        """Update the screen with the received image."""
        try:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            
            if not pixmap.isNull():
                self.current_screen = pixmap
                self.screen_label.setPixmap(
                    pixmap.scaled(
                        self.screen_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
        except Exception as e:
            logger.error(f"Error updating screen: {e}")
    
    def handle_file_transfer(self, data: bytes):
        """Handle file transfer data from server."""
        # This is a simplified implementation
        try:
            # For now, just show a message
            QMessageBox.information(self, "File Transfer", "File transfer completed")
        except Exception as e:
            logger.error(f"Error handling file transfer: {e}")
    
    def update_system_info(self, data: bytes):
        """Update the system info tab with received data."""
        try:
            info = json.loads(data.decode('utf-8'))
            info_text = "<h3>System Information</h3>"
            
            for key, value in info.items():
                if isinstance(value, dict):
                    info_text += f"<b>{key}:</b><br>"
                    for k, v in value.items():
                        info_text += f"  {k}: {v}<br>"
                else:
                    info_text += f"<b>{key}:</b> {value}<br>"
            
            self.info_text.setText(info_text)
        except Exception as e:
            logger.error(f"Error updating system info: {e}")
    
    def show_error(self, message: str):
        """Show an error message to the user."""
        QMessageBox.critical(self, "Error", message)
    
    def start_screen_updates(self):
        """Start periodic screen updates."""
        if self.screen_timer is None:
            self.screen_timer = QTimer()
            self.screen_timer.timeout.connect(self.request_screen_update)
            self.screen_timer.start(100)  # 10 FPS
    
    def stop_screen_updates(self):
        """Stop periodic screen updates."""
        if self.screen_timer:
            self.screen_timer.stop()
            self.screen_timer = None
    
    def request_screen_update(self):
        """Request a screen update from the server."""
        if self.connected and self.authenticated:
            self.send_message(MessageType.SCREENSHOT, b'')
    
    def request_system_info(self):
        """Request system information from the server."""
        if self.connected and self.authenticated:
            self.send_message(MessageType.INFO, b'')
    
    def toggle_connection(self):
        """Toggle connection to the server."""
        if self.connected:
            self.disconnect_from_server()
        else:
            self.show_connection_dialog()
    
    def disconnect_from_server(self):
        """Disconnect from the server."""
        self.connected = False
        self.authenticated = False
        
        # Stop screen updates
        self.stop_screen_updates()
        
        # Close socket
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        # Update UI
        self.update_ui_state()
        self.status_bar.showMessage("Disconnected")
        
        # Clear screen
        self.screen_label.clear()
        self.current_screen = None
    
    def update_ui_state(self):
        """Update the UI based on the current connection state."""
        connected = self.connected and self.authenticated
        
        self.btn_connect.setText("Disconnect" if connected else "Connect")
        self.btn_refresh.setEnabled(connected)
        self.btn_fullscreen.setEnabled(connected)
        self.btn_upload.setEnabled(connected)
        self.btn_download.setEnabled(connected)
        self.btn_delete.setEnabled(connected)
        self.btn_new_folder.setEnabled(connected)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Hide the window instead of closing it
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.disconnect_from_server()
            event.accept()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_normal()
    
    def show_normal(self):
        """Show the window in normal state."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    # Mouse and keyboard event handlers for remote control
    def screen_mouse_press(self, event):
        """Handle mouse press on the screen."""
        if not self.connected or not self.authenticated:
            return
        
        # Calculate the actual position on the remote screen
        pos = self.map_to_remote(event.pos())
        if pos is None:
            return
        
        # Determine which button was pressed
        button = 0  # Left button by default
        if event.button() == Qt.MouseButton.RightButton:
            button = 2
        elif event.button() == Qt.MouseButton.MiddleButton:
            button = 1
        
        # Send mouse down event
        mouse_event = MouseEvent(pos.x(), pos.y(), button, True)
        self.send_message(MessageType.MOUSE_CLICK, mouse_event.to_bytes())
        
        # Start dragging
        self.dragging = True
        self.drag_start_pos = event.pos()
        self.last_mouse_pos = pos
        
        # Request immediate screen update
        self.request_screen_update()
    
    def screen_mouse_release(self, event):
        """Handle mouse release on the screen."""
        if not self.connected or not self.authenticated:
            return
        
        # Calculate the actual position on the remote screen
        pos = self.map_to_remote(event.pos())
        if pos is None:
            return
        
        # Determine which button was released
        button = 0  # Left button by default
        if event.button() == Qt.MouseButton.RightButton:
            button = 2
        elif event.button() == Qt.MouseButton.MiddleButton:
            button = 1
        
        # Send mouse up event
        mouse_event = MouseEvent(pos.x(), pos.y(), button, False)
        self.send_message(MessageType.MOUSE_CLICK, mouse_event.to_bytes())
        
        # Stop dragging
        self.dragging = False
        self.drag_start_pos = None
        self.last_mouse_pos = None
        
        # Clear selection rectangle
        self.selection_rect = None
        self.update()
        
        # Request immediate screen update
        self.request_screen_update()
    
    def screen_mouse_move(self, event):
        """Handle mouse movement on the screen."""
        if not self.connected or not self.authenticated:
            return
        
        # Calculate the actual position on the remote screen
        pos = self.map_to_remote(event.pos())
        if pos is None:
            return
        
        # Send mouse move event
        if self.dragging and self.last_mouse_pos and (pos - self.last_mouse_pos).manhattanLength() > 1:
            mouse_event = MouseEvent(pos.x(), pos.y(), 0, False)  # Button 0 for move
            self.send_message(MessageType.MOUSE_MOVE, mouse_event.to_bytes())
            self.last_mouse_pos = pos
        
        # Update selection rectangle if dragging
        if self.dragging and self.drag_start_pos:
            self.selection_rect = QRect(
                min(self.drag_start_pos.x(), event.pos().x()),
                min(self.drag_start_pos.y(), event.pos().y()),
                abs(event.pos().x() - self.drag_start_pos.x()),
                abs(event.pos().y() - self.drag_start_pos.y())
            )
            self.update()
    
    def map_to_remote(self, local_pos):
        """Map local screen coordinates to remote screen coordinates."""
        if not self.current_screen or self.current_screen.isNull():
            return None
        
        # Get the displayed pixmap rect
        pixmap_rect = self.screen_label.pixmap().rect()
        if not pixmap_rect.isValid():
            return None
        
        # Calculate the position within the pixmap
        x_ratio = self.current_screen.width() / pixmap_rect.width()
        y_ratio = self.current_screen.height() / pixmap_rect.height()
        
        # Adjust for alignment
        pos_in_label = self.screen_label.mapFrom(self, local_pos)
        x = int((pos_in_label.x() - pixmap_rect.x()) * x_ratio)
        y = int((pos_in_label.y() - pixmap_rect.y()) * y_ratio)
        
        # Clamp to screen bounds
        x = max(0, min(x, self.current_screen.width() - 1))
        y = max(0, min(y, self.current_screen.height() - 1))
        
        return QPoint(x, y)
    
    # File transfer methods
    def upload_file(self):
        """Upload a file to the remote server."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if not file_path:
            return
        
        # In a real app, you would implement the file transfer logic here
        QMessageBox.information(self, "Upload", f"Would upload: {file_path}")
    
    def download_file(self):
        """Download a file from the remote server."""
        selected_items = self.remote_files.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Download", "No file selected")
            return
        
        # In a real app, you would implement the file transfer logic here
        file_names = ", ".join(item.text() for item in selected_items)
        QMessageBox.information(self, "Download", f"Would download: {file_names}")
    
    def delete_file(self):
        """Delete a file on the remote server."""
        selected_items = self.remote_files.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Delete", "No file selected")
            return
        
        # In a real app, you would implement the delete logic here
        file_names = ", ".join(item.text() for item in selected_items)
        QMessageBox.information(self, "Delete", f"Would delete: {file_names}")
    
    def create_folder(self):
        """Create a new folder on the remote server."""
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            # In a real app, you would implement the create folder logic here
            QMessageBox.information(self, "New Folder", f"Would create folder: {folder_name}")

def main():
    """Main entry point for the client application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    client = RemoteControlClient()
    client.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
