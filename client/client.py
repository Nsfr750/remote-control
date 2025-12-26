"""
Remote Control Client

Handles the GUI and connection to the remote control server.
"""
# Add parent directory to path for module imports first
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Standard library imports
import json
import logging
import os
import socket
import threading
import time
from typing import Dict, Optional, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Starting Remote Control Client")

# Qt imports
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QFont, QTextCursor, QIcon, QPixmap, QDesktopServices, QAction, QMouseEvent, QKeyEvent, QPainter, QPen, QColor, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QWidget, QMessageBox, QFileDialog, QSystemTrayIcon, QMenu,
    QDialog, QLineEdit, QCheckBox, QDialogButtonBox, QFormLayout, QListWidget,
    QStatusBar, QStyle, QSizePolicy, QScrollArea, QFrame, QSplitter, QToolBar,
    QInputDialog, QMenuBar, QProgressBar
)

# Local application imports
import sys
from pathlib import Path

# Add struttura directory to path
struttura_path = str(Path(__file__).parent.parent / 'struttura')
if struttura_path not in sys.path:
    sys.path.insert(0, struttura_path)

# Import help-related modules
from struttura.about import show_about_dialog
from struttura.help import show_help_dialog
from struttura.sponsor import show_sponsor_dialog
from struttura.version import get_version
from struttura.view_log import show_log_viewer

from common.protocol import Message, MessageType
from common.security import SecurityManager
from common.file_transfer import FileTransfer
from common.utils import setup_logger

# Configure logging
import os
from pathlib import Path

# Ensure logs directory exists
logs_dir = Path('../logs')
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(logs_dir / 'client_debug.log', mode='w')
    ]
)

# Set higher log level for PIL to reduce noise
logging.getLogger('PIL').setLevel(logging.WARNING)

logger = logging.getLogger('RemoteControlClient')

class MessageSignal(QObject):
    message_received = pyqtSignal(int, bytes)  # Matches process_message signature  # msg_type, data

class RemoteControlClient(QMainWindow):
    """Main client application window."""
    
    def __init__(self):
        """Initialize the client application."""
        logger.debug("Initializing RemoteControlClient")
        super().__init__()
        
        # Debug window creation
        logger.debug(f"Window created, object: {self}")
        
        self.connected = False
        self.authenticated = False
        self.running = False  # Controls the receive thread
        self.client_socket = None
        self.receive_thread = None
        self.screen_timer = None
        self.keepalive_timer = None  # For sending keep-alive pings
        self.last_message_time = 0    # Track last message time
        self.current_screen = None
        self.screen_scale = 1.0
        self.drag_start_pos = None
        self.selection_rect = None
        self.dragging = False
        self.last_mouse_pos = None
        self.security_manager = SecurityManager()
        self.file_transfer = FileTransfer()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        
        # Create signal handler
        self.message_handler = MessageSignal()
        self.message_handler.message_received.connect(self.process_message)
        
        logger.debug("Initializing UI components")
        self.init_ui()
        logger.debug("Initializing tray icon")
        self.init_tray_icon()
        
        logger.debug("Showing connection dialog")
        self.show_connection_dialog()
        
        # Debug window visibility
        logger.debug(f"Window visible after init: {self.isVisible()}")
        logger.debug(f"Window geometry: {self.geometry()}")
        logger.debug(f"Screen: {QApplication.primaryScreen().name()}")
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Exit action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")  # Add Ctrl+Q shortcut for exit
        exit_action.triggered.connect(self.close_application)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Log viewer action
        log_viewer_action = QAction("&View Logs", self)
        log_viewer_action.setShortcut("Ctrl+L")  # Add Ctrl+L shortcut for log viewer
        log_viewer_action.triggered.connect(self.show_log_viewer)
        tools_menu.addAction(log_viewer_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # Documentation action
        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("F1")  # Add F1 shortcut for help
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
        
        # Add separator
        help_menu.addSeparator()
        
        # About action
        about_action = QAction(f"&About {self.windowTitle()}", self)
        about_action.setShortcut("F2")  # Add F2 shortcut for Anout
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
              
        # Add separator
        help_menu.addSeparator()
        
        # Sponsor action
        sponsor_action = QAction("&Support this Project", self)
        sponsor_action.setShortcut("F3")  # Add F3 shortcut for Sponsor
        sponsor_action.triggered.connect(self.show_sponsor)
        help_menu.addAction(sponsor_action)
    
    def show_documentation(self):
        """Open the documentation dialog."""
        try:
            show_help_dialog(self)
        except Exception as e:
            logger.error(f"Error showing documentation: {e}")
            QMessageBox.critical(self, "Error", "Could not load documentation.")
    
    def show_about(self):
        """Show the About dialog."""
        try:
            show_about_dialog(self)
        except Exception as e:
            logger.error(f"Error showing about dialog: {e}")
            QMessageBox.about(self, "About", "Remote Control Client\nError loading about information.")
    
    def show_sponsor(self):
        """Show the Sponsor dialog."""
        try:
            from struttura.sponsor import SponsorDialog
            sponsor_dialog = SponsorDialog(self)
            sponsor_dialog.exec()
        except ImportError:
            QMessageBox.information(self, "Sponsor", 
                                 "Thank you for considering to sponsor this project!\n\n"
                                 "Your support helps maintain and improve this software.")
    
    def show_log_viewer(self):
        """Show the Log Viewer dialog."""
        try:
            show_log_viewer(self)
        except Exception as e:
            logger.error(f"Error showing log viewer: {e}")
            QMessageBox.critical(self, "Error", "Could not load log viewer.")
    
    def close_application(self):
        """Handle application exit from menu."""
        logger.info("Application exit requested from menu")
        self.close()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Remote Control Client")
        self.setMinimumSize(800, 600)
        
        # Set application icon
        icon_path = Path(__file__).parent.parent / 'assets' / 'icon.png'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Create menu bar
        self.create_menu_bar()
        
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
        
        self.btn_fullscreen = QPushButton("Fullscreen (ESC to exit)")
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
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
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
        
        # Use command-line arguments if available, otherwise use defaults
        host = getattr(self, 'host', 'localhost')
        port = getattr(self, 'port', 5000)
        username = getattr(self, 'username', '')
        password = getattr(self, 'password', '')
        
        self.host_input = QLineEdit(host)
        self.port_input = QLineEdit(str(port))
        self.username_input = QLineEdit(username)
        self.password_input = QLineEdit(password)
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
        
        # Auto-connect if credentials are provided via command line
        if username and password:
            # Skip dialog and connect directly
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            self.connect_to_server()
        elif dialog.exec() == QDialog.DialogCode.Accepted:
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
            if self.connected:
                logger.warning("Already connected to server")
                return
                
            logger.info(f"Connecting to {self.host}:{self.port}...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)  # 10 second timeout for connect
            self.client_socket.connect((self.host, self.port))
            
            # Set socket options for keepalive
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if sys.platform == 'win32':
                # Windows specific keepalive settings
                self.client_socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 3000))
            else:
                # Linux/Unix keepalive settings
                self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
                self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            
            # Reset state
            self.connected = True
            self.authenticated = False
            self.running = True
            self.reconnect_attempts = 0
            self.last_message_time = time.time()
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
            # Start keepalive timer
            self.start_keepalive()
            
            # Send authentication
            self.authenticate()
            
            # Update UI
            self.status_bar.showMessage(f"Connecting to {self.host}:{self.port}...")
            logger.info("Connection established, authenticating...")
            
        except socket.timeout:
            error_msg = f"Connection to {self.host}:{self.port} timed out"
            logger.error(error_msg)
            self.handle_connection_error(error_msg)
        except ConnectionRefusedError:
            error_msg = f"Connection refused by {self.host}:{self.port}"
            logger.error(error_msg)
            self.handle_connection_error(error_msg)
        except Exception as e:
            error_msg = f"Failed to connect to server: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.handle_connection_error(error_msg)
    
    def authenticate(self):
        """Authenticate with the server."""
        try:
            logger.debug(f"Attempting authentication with username: {self.username}")
            logger.debug(f"Password provided: {'*' * len(self.password) if self.password else 'None'}")
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            self.send_message(MessageType.AUTH, json.dumps(auth_data).encode('utf-8'))
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to authenticate: {e}")
            self.disconnect_from_server()
    
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
    
    def start_keepalive(self):
        """Start the keep-alive timer."""
        self.stop_keepalive()  # Ensure any existing timer is stopped
        self.keepalive_timer = QTimer()
        self.keepalive_timer.timeout.connect(self.send_keepalive)
        self.keepalive_timer.start(30000)  # Send keepalive every 30 seconds
        logger.debug("Keep-alive timer started")
    
    def stop_keepalive(self):
        """Stop the keep-alive timer."""
        if hasattr(self, 'keepalive_timer') and self.keepalive_timer:
            self.keepalive_timer.stop()
            self.keepalive_timer = None
            logger.debug("Keep-alive timer stopped")
    
    def send_keepalive(self):
        """Send a keep-alive ping to the server."""
        if not self.connected or not self.authenticated:
            return
            
        try:
            # If we haven't received any messages in 2x keepalive interval, assume connection is dead
            time_since_last_msg = time.time() - self.last_message_time
            if time_since_last_msg > 60:  # 60 seconds of no messages
                logger.warning(f"No messages received for {time_since_last_msg:.1f} seconds, reconnecting...")
                self.reconnect()
                return
                
            # Send a ping if we're connected but idle
            if time_since_last_msg > 30:  # 30 seconds of no messages
                logger.debug("Sending keep-alive ping")
                self.send_message(MessageType.PING, b'')
                
        except Exception as e:
            logger.error(f"Error in keep-alive: {e}")
            self.reconnect()
    
    def reconnect(self):
        """Attempt to reconnect to the server."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached, giving up")
            self.disconnect_from_server()
            QMessageBox.critical(self, "Connection Lost", 
                               "Lost connection to the server and could not reconnect.")
            return
            
        self.reconnect_attempts += 1
        logger.info(f"Attempting to reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})...")
        
        # Clean up existing connection
        self.disconnect_from_server(show_message=False)
        
        # Try to reconnect after a delay
        QTimer.singleShot(2000 * self.reconnect_attempts, self.connect_to_server)
    
    def handle_connection_error(self, error_msg):
        """Handle connection errors and attempt reconnection if needed."""
        self.disconnect_from_server(show_message=False)
        
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = 2 * self.reconnect_attempts  # Exponential backoff
            logger.warning(f"{error_msg}. Reconnecting in {delay} seconds... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
            QTimer.singleShot(delay * 1000, self.connect_to_server)
        else:
            logger.error(f"{error_msg}. Max reconnection attempts reached.")
            self.show_connection_dialog()
            QMessageBox.critical(self, "Connection Error", 
                               f"{error_msg}\n\nPlease check the server address and try again.")
    
    def receive_messages(self):
        """Receive messages from the server in a separate thread."""
        logger.info("Starting message receiver thread")
        buffer = b''
        
        try:
            while self.running and self.client_socket:
                try:
                    # Check if socket is still valid
                    if not self.client_socket.fileno():
                        logger.info("Socket closed, stopping receive thread")
                        self.running = False
                        break
                    
                    # Set a short timeout to allow checking self.running
                    self.client_socket.settimeout(1.0)
                
                    # Receive message header (8 bytes: 4 for type, 4 for length)
                    header = b''
                    while len(header) < 8 and self.running:
                        try:
                            chunk = self.client_socket.recv(8 - len(header))
                            if not chunk:
                                logger.info("Server closed connection")
                                self.running = False
                                break
                            header += chunk
                        except socket.timeout:
                            # Check if we should still be running
                            if not self.running:
                                break
                            continue
                    
                    if not self.running:
                        break
                        
                    if len(header) < 8:
                        logger.warning(f"Incomplete header received: {len(header)} bytes")
                        continue
                        
                    # Parse message type and data length
                    msg_type = int.from_bytes(header[0:4], byteorder='big')
                    data_len = int.from_bytes(header[4:8], byteorder='big')
                    
                    if data_len > 10 * 1024 * 1024:  # 10MB max
                        logger.error(f"Message too large: {data_len} bytes")
                        break
                        
                    # Receive message data
                    data = b''
                    while len(data) < data_len and self.running:
                        try:
                            chunk = self.client_socket.recv(min(4096, data_len - len(data)))
                            if not chunk:
                                logger.warning("Connection closed while receiving data")
                                self.running = False
                                break
                            data += chunk
                        except socket.timeout:
                            if not self.running:
                                break
                            continue
                        except (ConnectionResetError, ConnectionAbortedError) as e:
                            logger.info(f"Connection closed while receiving data: {e}")
                            self.running = False
                            break
                    
                    if not self.running:
                        break
                        
                    if len(data) != data_len:
                        logger.warning(f"Incomplete data received: {len(data)}/{data_len} bytes")
                        continue
                        
                    # Process the message in the main thread
                    QMetaObject.invokeMethod(
                        self,
                        "process_message",
                        Qt.ConnectionType.QueuedConnection,
                        Q_ARG(int, msg_type),  # Pass as int to avoid enum issues
                        Q_ARG(bytes, data)
                    )
                    
                except ConnectionResetError:
                    logger.info("Connection reset by peer")
                    break
                except ConnectionAbortedError:
                    logger.info("Connection aborted")
                    break
                except OSError as e:
                    if e.errno == 10054:  # Connection reset by peer (WSAECONNRESET)
                        logger.info("Connection reset by peer (WSAECONNRESET)")
                    elif e.errno == 10053:  # Software caused connection abort (WSAECONNABORTED)
                        logger.info("Connection aborted by software")
                    else:
                        logger.error(f"Socket error: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}", exc_info=True)
                    break

        except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
            logger.error(f"Connection error: {e}")
            self.disconnect_from_server()
            self.show_connection_dialog()
        except Exception as e:
            logger.error(f"Unexpected error in receive loop: {e}", exc_info=True)
            self.disconnect_from_server()
            self.show_connection_dialog()
        finally:
            logger.info("Message receiver thread exiting")

    @pyqtSlot(int, bytes)
    def process_message(self, msg_type: int, data: bytes):
        """Process a received message in the main thread.
        
        Args:
            msg_type: Message type as int (will be converted to MessageType)
            data: Message data as bytes
        """
        try:
            # Update last message time for keepalive
            self.last_message_time = time.time()
            
            # Convert msg_type to MessageType
            try:
                msg_type_enum = MessageType(msg_type)
            except ValueError:
                logger.warning(f"Unknown message type: {msg_type}")
                return
                    
            logger.debug(f"Processing message type: {msg_type_enum}")
            
            # Handle PONG response to our PING
            if msg_type_enum == MessageType.PONG:
                logger.debug("Received PONG from server")
                return
                
            if msg_type_enum == MessageType.AUTH_RESPONSE:
                self.handle_auth_response(data)
                return  # Don't process further in this method
                
            # At this point, if we're not authenticated, ignore the message
            if not self.authenticated:
                logger.warning(f"Received {msg_type_enum} message before authentication")
                return
                
            # Handle other message types
            try:
                if msg_type_enum == MessageType.ERROR:
                    error_msg = data.decode('utf-8', errors='replace')
                    logger.error(f"Server error: {error_msg}")
                    logger.debug(f"Error message details: {data}")
                    QMessageBox.critical(self, "Server Error", error_msg)
                    self.disconnect_from_server()
                    
                elif msg_type_enum == MessageType.SCREENSHOT:
                    self.update_screen(data)
                
                elif msg_type_enum == MessageType.FILE_TRANSFER:
                    self.handle_file_transfer(data)
                
                elif msg_type_enum == MessageType.INFO:
                    self.update_system_info(data)
                
                else:
                    logger.warning(f"Unhandled message type: {msg_type_enum}")
                    
            except Exception as e:
                logger.error(f"Error processing {msg_type_enum} message: {e}", exc_info=True)
                
        except Exception as e:
            logger.error(f"Unexpected error in process_message: {e}", exc_info=True)
            self.disconnect_from_server()
            QMessageBox.critical(self, "Error", f"Error processing message: {e}")
    
    def handle_auth_response(self, data: bytes):
        """Handle authentication response from server."""
        try:
            response = json.loads(data.decode('utf-8'))
            if response.get('success'):
                logger.info("Authentication successful")
                self.authenticated = True
                self.connected = True
                
                # Update UI first
                self.status_bar.showMessage(f"Connected to {self.host}:{self.port} as {self.username}")
                self.update_ui_state()
                
                # Start keepalive before anything else
                self.start_keepalive()
                
                # Start screen updates after a short delay to let things settle
                QTimer.singleShot(500, self.start_screen_updates)
                
                # Request system info after a short delay
                QTimer.singleShot(1000, self.request_system_info)
                
            else:
                error_msg = response.get('message', 'Authentication failed')
                logger.warning(f"Authentication failed: {error_msg}")
                QMessageBox.warning(self, "Authentication Failed", error_msg)
                self.disconnect_from_server(show_message=False)
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid authentication response: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.disconnect_from_server(show_message=False)
            
        except Exception as e:
            error_msg = f"Error processing authentication: {e}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(self, "Error", error_msg)
            self.disconnect_from_server(show_message=False)
    
    def update_screen(self, image_data: bytes):
        """Update the screen with the received image."""
        try:
            logger.debug(f"Received image data: {len(image_data)} bytes")
            logger.debug(f"Window visible: {self.isVisible()}")
            if hasattr(self, 'screen_label'):
                logger.debug(f"Screen label size: {self.screen_label.size().width()}x{self.screen_label.size().height()}")
            
            # Try multiple image formats
            pixmap = QPixmap()
            
            # First try PNG
            if not pixmap.loadFromData(image_data, "PNG"):
                logger.debug("PNG format failed, trying JPEG")
                # Try JPEG format
                if not pixmap.loadFromData(image_data, "JPEG"):
                    logger.debug("JPEG format failed, trying auto-detection")
                    # Try without format specification
                    if not pixmap.loadFromData(image_data):
                        logger.error("Failed to load image from received data")
                        # Debug: save first few bytes to check format
                        logger.debug(f"First 20 bytes: {image_data[:20].hex()}")
                        return
                else:
                    logger.debug("Loaded image as JPEG")
            else:
                logger.debug("Loaded image as PNG")
                
            logger.debug(f"Pixmap size: {pixmap.size().width()}x{pixmap.size().height()}")
            self.current_screen = pixmap
        
            # Scale and update the label
            if hasattr(self, 'screen_label'):
                scaled_pixmap = pixmap.scaled(
                    self.screen_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                logger.debug(f"Scaled pixmap size: {scaled_pixmap.size().width()}x{scaled_pixmap.size().height()}")
                self.screen_label.setPixmap(scaled_pixmap)
                logger.debug("Screen updated successfully")
            else:
                logger.error("screen_label not found in the UI")
                
        except Exception as e:
            logger.error(f"Error updating screen: {e}", exc_info=True)
    
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
            info_text = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 15px; }
                    h3 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; }
                    .section { margin-bottom: 15px; }
                    .section-title { 
                        color: #3498db; 
                        font-weight: bold; 
                        margin: 10px 0 5px 0;
                    }
                    .info-item { margin: 3px 0; }
                    .info-label { font-weight: bold; }
                </style>
            </head>
            <body>
                <h3>System Information</h3>
            """
            
            # Process each section
            for section, content in info.items():
                info_text += f'<div class="section">\n'
                info_text += f'<div class="section-title">{section.replace("_", " ").title()}</div>\n'
                if isinstance(content, dict):
                    for key, value in content.items():
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, indent=2)
                        info_text += f'<div class="info-item"><span class="info-label">{key.replace("_", " ").title()}:</span> {value}</div>\n'
                elif isinstance(content, list):
                    for item in content:
                        info_text += f'<div class="info-item">• {str(item)}</div>\n'
                else:
                    info_text += f'<div class="info-item">{str(content)}</div>\n'
                info_text += '</div>\n'
            info_text += """
            </body>
            </html>
            """
            
            self.info_text.setText(info_text)
            
        except Exception as e:
            error_msg = f"Error updating system info: {str(e)}"
            logger.error(error_msg)
            self.info_text.setText(f"<div style='color: red;'>{error_msg}</div>")
    
    def show_error(self, message: str):
        """Show an error message to the user."""
        QMessageBox.critical(self, "Error", message)
    
    def start_screen_updates(self):
        """Start receiving screen updates from the server."""
        if not self.connected or not self.authenticated:
            logger.warning("Cannot start screen updates: not connected or not authenticated")
            return
            
        if not self.screen_timer:
            self.screen_timer = QTimer(self)
            self.screen_timer.setTimerType(Qt.TimerType.PreciseTimer)
            self.screen_timer.timeout.connect(self.request_screen_update)
        
        if not self.screen_timer.isActive():
            try:
                logger.info("Starting screen updates")
                # Start with a slightly longer interval for the first update
                self.screen_timer.start(200)  # Start with 200ms, will adjust after first update
                # Request the first update with a small delay
                QTimer.singleShot(100, self.request_screen_update)
            except Exception as e:
                logger.error(f"Error starting screen updates: {e}", exc_info=True)
                self.disconnect_from_server()
    
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
            self.info_text.setText("<h3>Requesting system information...</h3>")
            self.send_message(MessageType.INFO, b'')
    
    def on_tab_changed(self, index):
        """Handle tab change events."""
        if self.tabs.tabText(index) == "System Info" and self.connected and self.authenticated:
            self.request_system_info()
    
    def toggle_connection(self):
        """Toggle connection to the server."""
        if self.connected:
            self.disconnect_from_server()
        else:
            self.show_connection_dialog()
    
    def disconnect_from_server(self, show_message=True):
        """Disconnect from the server.
        
        Args:
            show_message: If True, shows a status bar message about disconnection
        """
        if not self.connected and not self.running:
            return
            
        logger.info("Disconnecting from server...")
        self.running = False
        self.connected = False
        self.authenticated = False
        
        # Stop timers
        self.stop_screen_updates()
        self.stop_keepalive()
        
        # Close socket
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.client_socket.close()
            except:
                pass
            finally:
                self.client_socket = None
        
        # Wait for receive thread to finish
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2.0)
            if self.receive_thread.is_alive():
                logger.warning("Receive thread did not terminate cleanly")
        self.authenticated = False
        
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
        """Handle window close event with proper cleanup."""
        logger.info("Application closing, cleaning up resources...")
        
        # Disconnect from server if connected
        if self.connected:
            self.disconnect_from_server(show_message=False)
        
        # Stop the message receiver thread
        if hasattr(self, 'message_receiver') and self.message_receiver.isRunning():
            logger.debug("Stopping message receiver thread...")
            self.running = False
            self.message_receiver.running = False
            self.message_receiver.wait(2000)  # Wait up to 2 seconds for the thread to finish
            
        # Stop any active timers
        if hasattr(self, 'screen_timer') and self.screen_timer is not None and hasattr(self.screen_timer, 'isActive') and self.screen_timer.isActive():
            logger.debug("Stopping screen update timer...")
            try:
                self.screen_timer.stop()
            except Exception as e:
                logger.error(f"Error stopping screen timer: {e}")
            
        if hasattr(self, 'keepalive_timer') and self.keepalive_timer is not None and hasattr(self.keepalive_timer, 'isActive') and self.keepalive_timer.isActive():
            logger.debug("Stopping keepalive timer...")
            try:
                self.keepalive_timer.stop()
            except Exception as e:
                logger.error(f"Error stopping keepalive timer: {e}")
        
        # Close the socket if it's still open
        if hasattr(self, 'client_socket') and self.client_socket:
            try:
                logger.debug("Closing client socket...")
                self.client_socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        # Hide the window if tray icon is visible
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            logger.debug("Hiding window to tray...")
            self.hide()
            event.ignore()
        else:
            logger.debug("Closing application...")
            event.accept()
        
        logger.info("Application cleanup complete")
        QApplication.quit()  # Ensure the application quits completely
    
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
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Exit fullscreen with ESC key
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
            logger.debug("Exited fullscreen mode with ESC key")
            return
        
        # Call parent implementation
        super().keyPressEvent(event)
    
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
        
        # Create a dictionary for the mouse event
        mouse_event = {
            'x': pos.x(),
            'y': pos.y(),
            'button': button,
            'pressed': True
        }
        
        # Convert to bytes and send
        self.send_message(MessageType.MOUSE_CLICK, json.dumps(mouse_event).encode('utf-8'))
        
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
        
        # Create a dictionary for the mouse event
        mouse_event = {
            'x': pos.x(),
            'y': pos.y(),
            'button': button,
            'pressed': False
        }
        
        # Convert to bytes and send
        self.send_message(MessageType.MOUSE_CLICK, json.dumps(mouse_event).encode('utf-8'))
        
        # Stop dragging and clean up
        self.dragging = False
        self.drag_start_pos = None
        self.last_mouse_pos = None
        self.selection_rect = None
        self.update()  # Clear the selection rectangle
        
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
            # Create a dictionary for the mouse move event
            mouse_event = {
                'x': pos.x(),
                'y': pos.y(),
                'dx': pos.x() - self.last_mouse_pos.x(),  # Delta X
                'dy': pos.y() - self.last_mouse_pos.y()   # Delta Y
            }
            
            # Convert to bytes and send
            self.send_message(MessageType.MOUSE_MOVE, json.dumps(mouse_event).encode('utf-8'))
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
            # In a real app, you would implement the folder creation logic here
            QMessageBox.information(self, "New Folder", f"Would create folder: {folder_name}")

def main():
    """Main entry point for the client application."""
    import sys
    import argparse
    from PyQt6.QtWidgets import QApplication
    import logging
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Remote Control Client')
    parser.add_argument('--host', default='localhost', help='Server host to connect to')
    parser.add_argument('--port', type=int, default=5000, help='Server port to connect to')
    parser.add_argument('--username', default='', help='Username for authentication')
    parser.add_argument('--password', default='', help='Password for authentication')
    args = parser.parse_args()
    
    # Set up application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look
    
    # Create and show main window
    logger.debug("Creating main window")
    window = RemoteControlClient()
    
    # Set connection parameters from command line args
    window.host = args.host
    window.port = args.port
    window.username = args.username
    window.password = args.password
    
    window.show()
    window.raise_()  # Bring window to front
    window.activateWindow()  # Activate the window
    
    logger.debug("Starting application event loop")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
