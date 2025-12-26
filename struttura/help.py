"""
Help Dialog for remote control app
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
    QPushButton, QWidget, QFrame, QLabel, QTabWidget,
    QApplication, QScrollArea, QSizePolicy, QMessageBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QFont, QTextCursor, QPixmap, QIcon

import os
import sys
import platform
import logging

# Get version information
try:
    from versione import get_version
    VERSION = get_version()
except ImportError:
    VERSION = "1.0.1"

def show_help_dialog(parent=None):
    """Show the help dialog."""
    dialog = HelpDialog(parent)
    dialog.exec()

logger = logging.getLogger('RemoteControl')

class HelpDialog(QDialog):
    """Help dialog for the application."""
    
    def __init__(self, parent=None):
        """Initialize the help dialog."""
        super().__init__(parent)
        self.setWindowTitle("Remote Control Help")
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
        # Set window flags
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        try:
            # Set up UI
            self.init_ui()
            logger.debug("Help dialog initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing help dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize help dialog: {str(e)}")

    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self.tabs.addTab(self._create_welcome_tab(), "Welcome")
        self.tabs.addTab(self._create_server_tab(), "Server Setup")
        self.tabs.addTab(self._create_client_tab(), "Client Usage")
        self.tabs.addTab(self._create_features_tab(), "Features")
        self.tabs.addTab(self._create_troubleshooting_tab(), "Troubleshooting")
        self.tabs.addTab(self._create_about_tab(), "About")
        
        main_layout.addWidget(self.tabs)
        
        # Close button
        button_box = QHBoxLayout()
        button_box.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setMinimumWidth(120)
        
        # Style the close button
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        button_box.addWidget(self.close_btn)
        main_layout.addLayout(button_box)
           
    def _create_welcome_tab(self):
        """Create the welcome tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Welcome message
        welcome_text = """
        <h2>Welcome to Remote Control</h2>
        <p>Thank you for using Remote Control, a secure and easy-to-use application for remote desktop control, 
        screen sharing, and file transfer with advanced security features.</p>
        
        <h3>What's New in 1.0.0</h3>
        <h4>🚀 Initial Release</h4>
        <ul>
            <li><b>Real-time Monitoring</b>: Connect to Security Information and Event Management systems</li>
            <li><b>Centralized Logging</b>: Send security events to your SIEM for analysis</li>
            <li><b>Secure Authentication</b>: API key and OAuth2 support for SIEM connections</li>
            <li><b>Event Forwarding</b>: Forward security events in real-time</li>
        </ul>        
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(welcome_text)
        
        layout.addWidget(text_browser)
        return widget

    def _create_server_tab(self):
        """Create the server tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Server message
        server_text = """
        <h2>Server Setup</h2>
        <p>Set up the server to control remote computers.</p>
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(server_text)
        
        layout.addWidget(text_browser)
        return widget

    def _create_client_tab(self):
        """Create the client tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Client message
        client_text = """
        <h2>Client Usage</h2>
        <p>Set up the client to control remote computers.</p>
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(client_text)
        
        layout.addWidget(text_browser)
        return widget

    def _create_features_tab(self):
        """Create the features tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)  

        # Features message
        features_text = """
        <h2>Features</h2>
        
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(features_text)
        
        layout.addWidget(text_browser)
        return widget          

    def _create_troubleshooting_tab(self):
        """Create the troubleshooting tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)   

        # troubleshooting message
        troubleshooting_text = """
        <h2>Troubleshooting</h2>
        
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(troubleshooting_text)
        
        layout.addWidget(text_browser)
        return widget           
             
    def _create_about_tab(self):
        """Create the about tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Get system information
        system = platform.system()
        release = platform.release()
        python_version = platform.python_version()
        
        about_text = f"""
        <div style="text-align: center;">
            <h2>Remote Control v{VERSION}</h2>
            <p>A secure and easy-to-use application for remote desktop control, screen sharing, and file transfer.</p>
            
            <h3>System Information</h3>
            <table style="margin: 0 auto; text-align: left;">
                <tr><td><b>Operating System:</b></td><td>{system} {release}</td></tr>
                <tr><td><b>Python Version:</b></td><td>{python_version}</td></tr>
                <tr><td><b>Key Types:</b></td><td>RSA, ECC, Ed25519</td></tr>
            </table>
            
            <h3>License</h3>
            <p>© Copyright 2024-2025 Nsfr750. All Rights Reserved</p>
            <p>Licensed under the GPL v3.0 License</p>
            
            <p>
                <a href="https://github.com/Nsfr750/remote-control">GitHub Repository</a> | 
                <a href="https://github.com/Nsfr750/remote-control/wiki">Wiki Pages</a> | 
                <a href="https://github.com/Nsfr750/remote-control/issues">Report Issues</a> |
                <a href="https://github.com/Nsfr750/remote-control/releases">Release Notes</a>
            </p>
        </div>
        """
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(about_text)
        
        layout.addWidget(text_browser)
        return widget
    
    def accept(self):
        """Handle dialog acceptance."""
        super().accept()
    
    def reject(self):
        """Handle dialog rejection."""
        super().reject()            
   
    def show_dialog(self):
        """Show the help dialog."""
        self.show()
        return self.exec_()
    
    def open_link(self, url):
        """
        Open a link in the default web browser.
        
        Args:
            url: QUrl of the link to open
        """
        try:
            QDesktopServices.openUrl(url)
        except Exception as e:
            logger.error(self.tr(
                "help.link_open_error",
                "Error opening link {url}: {error}"
            ).format(url=url.toString(), error=str(e)))
