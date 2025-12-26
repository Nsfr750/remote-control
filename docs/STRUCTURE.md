# 🏗️ Project Structure

```
remote_control/
├── client/                 # Client application
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Main client logic
│   └── gui/                # GUI components
│       ├── __init__.py
│       ├── main_window.py  # Main application window
│       ├── login_dialog.py # Login interface
│       └── file_browser.py # File transfer interface
│
├── server/                 # Server application
│   ├── __init__.py
│   ├── server.py           # Main server logic
│   ├── input.py            # Input controller interface
│   ├── screen.py           # Screen controller interface
│   └── platform/           # Platform-specific implementations
│       ├── windows/        # Windows-specific code
│       │   ├── __init__.py
│       │   ├── input.py    # Windows input handling
│       │   └── screen.py   # Windows screen capture
│       └── linux/          # Linux-specific code
│           ├── __init__.py
│           ├── input.py    # Linux input handling (implemented)
│           └── screen.py   # Linux screen capture (import/scrot)
│
├── common/                 # Shared code
│   ├── __init__.py
│   ├── protocol.py         # Communication protocol
│   ├── security.py         # Security utilities
│   └── file_transfer.py    # File transfer utilities
│
├── setup/                  # Build system
│   ├── build_client.py     # Client compilation script
│   ├── build_server.py     # Server compilation script
│   ├── comp.py             # Legacy build script
│   └── firma.bat           # Code signing script
│
├── dist/                   # Compiled executables
│   ├── RemoteControlClient.exe
│   └── RemoteControlServer.exe
│
├── docs/                   # Documentation
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── ROADMAP.md
│   ├── STRUCTURE.md
│   └── USERGUIDE.md
│
├── assets/                 # Application assets
│   └── icon.ico            # Application icon
│
├── lang/                   # Language support
│   ├── language_manager.py
│   └── translations.py
│
├── tests/                  # Test suite
├── requirements.txt        # Dependencies
├── version.py              # Version information
├── main.py                 # Application entry point
├── logger.py               # Logging system
├── menu.py                 # Menu system
├── help.py                 # Help system
├── about.py                # About dialog
├── sponsor.py              # Sponsor information
├── update.py               # Update system
└── view_log.py             # Log viewer

## Client Components

### Core
- Handles network communication
- Manages application state
- Coordinates between GUI and network

### GUI
- Main window with remote desktop view
- Connection status indicators
- Settings panel
- File transfer interface

## Server Components

### Core
- Manages client connections
- Handles authentication
- Routes messages between components

### Input Handling
- Processes mouse and keyboard events
- Platform-specific implementations
- Event validation and security

### Screen Capture
- Captures screen content
- Handles multiple displays
- Optimizes image transfer

## Common Components

### Protocol
- Defines message formats
- Handles serialization/deserialization
- Manages connection handshake
- Data structures

### Security
- Encryption/decryption
- Hashing

### File Transfer
- File operations
- Directory traversal
- Transfer management
