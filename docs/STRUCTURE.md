# Project Structure

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
│   ├── server.py          # Main server logic
│   ├── mock_server.py     # Mock server for testing
│   ├── input/             # Input handling
│   │   ├── __init__.py
│   │   ├── windows.py     # Windows input handling
│   │   └── linux.py       # Linux input handling
│   └── screen/            # Screen capture
│       ├── __init__.py
│       ├── windows.py     # Windows screen capture
│       └── linux.py       # Linux screen capture
│
└── common/                # Shared code
    ├── __init__.py
    ├── protocol.py        # Communication protocol
    ├── security.py        # Security utilities
    └── file_transfer.py   # File transfer utilities
```

## Client Components

### Core
- Handles network communication
- Manages application state
- Coordinates between GUI and network

### GUI
- Main window with tabbed interface
- Login/authentication dialog
- File browser/transfer interface
- Remote control view
- System information display

## Server Components

### Core
- Manages client connections
- Handles authentication
- Routes messages between clients

### Input Handling
- Platform-specific input simulation
- Mouse and keyboard control
- Clipboard management

### Screen Capture
- Platform-specific screen capture
- Image compression
- Screen update optimization

## Common Components

### Protocol
- Message serialization/deserialization
- Command definitions
- Data structures

### Security
- Encryption/decryption
- Hashing
- Certificate management

### File Transfer
- File operations
- Directory traversal
- Transfer management
