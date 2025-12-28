"""
Log Viewer Dialog for Remote Control Application
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
    QPushButton, QWidget, QLabel, QTabWidget,
    QComboBox, QLineEdit, QCheckBox, QGroupBox,
    QScrollArea, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QFont, QTextCursor, QIcon

import os
import sys
import platform
import logging
from pathlib import Path
from datetime import datetime

# Get version information
try:
    from versione import get_version
    VERSION = get_version()
except ImportError:
    VERSION = "1.0.1"

def show_log_viewer(parent=None):
    """Show the log viewer dialog."""
    dialog = LogViewerDialog(parent)
    dialog.exec()

logger = logging.getLogger('RemoteControl')

class LogViewerDialog(QDialog):
    """Log viewer dialog for the application."""
    
    def __init__(self, parent=None):
        """Initialize the log viewer dialog."""
        super().__init__(parent)
        self.setWindowTitle("Remote Control Log Viewer")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        
        # Set window flags
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Initialize variables
        self.current_log_file = None
        self.log_content = ""
        
        try:
            # Set up UI
            self.init_ui()
            self.load_available_logs()
            logger.debug("Log viewer dialog initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing log viewer dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize log viewer: {str(e)}")

    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Log file selector
        self.log_combo = QComboBox()
        self.log_combo.currentTextChanged.connect(self.load_log_file)
        controls_layout.addWidget(QLabel("Log File:"))
        controls_layout.addWidget(self.log_combo)
        controls_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_current_log)
        controls_layout.addWidget(self.refresh_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.clear_current_log)
        controls_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Filter controls
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # Level filter
        filter_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.level_combo)
        
        # Search box
        filter_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_box)
        
        # Auto-scroll checkbox
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        filter_layout.addWidget(self.auto_scroll_cb)
        
        main_layout.addWidget(filter_group)
        
        # Log display area
        self.log_browser = QTextBrowser()
        self.log_browser.setFont(QFont("Consolas", 10))
        main_layout.addWidget(self.log_browser)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Line count
        self.line_count_label = QLabel("Lines: 0")
        status_layout.addWidget(self.line_count_label)
        
        main_layout.addLayout(status_layout)
        
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

    def load_available_logs(self):
        """Load available log files from the logs directory."""
        # Use absolute path to logs directory
        current_dir = Path(__file__).parent
        logs_dir = current_dir.parent / 'logs'
        if not logs_dir.exists():
            self.status_label.setText("Logs directory not found")
            return
        
        # Clear existing items
        self.log_combo.clear()
        
        # Find all log files
        log_files = list(logs_dir.glob('*.log'))
        if not log_files:
            self.status_label.setText("No log files found")
            return
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Add to combo box
        for log_file in log_files:
            self.log_combo.addItem(log_file.name, str(log_file))
        
        self.status_label.setText(f"Found {len(log_files)} log files")

    def load_log_file(self, filename=None):
        """Load the selected log file."""
        if filename is None:
            filename = self.log_combo.currentText()
        
        if not filename:
            return
        
        # Get the full path
        # Use absolute path to logs directory
        current_dir = Path(__file__).parent
        logs_dir = current_dir.parent / 'logs'
        log_file = logs_dir / filename
        
        if not log_file.exists():
            self.status_label.setText(f"Log file not found: {filename}")
            return
        
        try:
            # Read the log file
            with open(log_file, 'r', encoding='utf-8') as f:
                self.log_content = f.read()
            
            self.current_log_file = log_file
            self.apply_filters()
            
            # Update status
            file_size = log_file.stat().st_size
            mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            self.status_label.setText(f"Loaded: {filename} ({file_size} bytes, modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
            
        except Exception as e:
            logger.error(f"Error loading log file {filename}: {str(e)}")
            self.status_label.setText(f"Error loading log file: {str(e)}")

    def apply_filters(self):
        """Apply filters to the log content."""
        if not self.log_content:
            return
        
        lines = self.log_content.split('\n')
        filtered_lines = []
        
        # Get filter values
        level_filter = self.level_combo.currentText()
        search_filter = self.search_box.text().lower()
        
        for line in lines:
            if not line.strip():
                continue
            
            # Apply level filter
            if level_filter != "ALL":
                if level_filter not in line:
                    continue
            
            # Apply search filter
            if search_filter and search_filter not in line.lower():
                continue
            
            filtered_lines.append(line)
        
        # Display filtered content
        display_content = '\n'.join(filtered_lines)
        self.log_browser.setPlainText(display_content)
        
        # Update line count
        self.line_count_label.setText(f"Lines: {len(filtered_lines)}")
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_cb.isChecked():
            cursor = self.log_browser.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_browser.setTextCursor(cursor)

    def refresh_current_log(self):
        """Refresh the current log file."""
        if self.current_log_file:
            self.load_log_file(self.current_log_file.name)
        else:
            self.load_log_file()

    def clear_current_log(self):
        """Clear the current log file."""
        if not self.current_log_file:
            QMessageBox.warning(self, "Warning", "No log file selected")
            return
        
        reply = QMessageBox.question(
            self, 
            "Clear Log File", 
            f"Are you sure you want to clear {self.current_log_file.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear the file
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                
                # Reload and display
                self.load_log_file()
                QMessageBox.information(self, "Success", "Log file cleared successfully")
                
            except Exception as e:
                logger.error(f"Error clearing log file: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to clear log file: {str(e)}")

    def accept(self):
        """Handle dialog acceptance."""
        super().accept()
    
    def reject(self):
        """Handle dialog rejection."""
        super().reject()            
   
    def show_dialog(self):
        """Show the log viewer dialog."""
        self.show()
        return self.exec_()
