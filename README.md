# Remote Control Application

A cross-platform remote control application with secure authentication, file transfer, and system monitoring capabilities.

## Features

- **Secure Authentication**
  - Password protection
  - Credential management
  - Session management

- **Remote Control**
  - Full mouse and keyboard control
  - Multi-monitor support
  - Real-time screen sharing

- **File Management**
  - File upload/download
  - Directory navigation
  - File operations (copy, move, delete)

- **System Monitoring**
  - System information
  - Resource usage
  - Process management

- **Additional Features**
  - Clipboard sharing
  - Chat functionality
  - System tray integration
  - Auto-update

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/NSFR750/remote-control.git
   cd remote-control
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Server

```bash
python -m server.server [--host HOST] [--port PORT] [--password PASSWORD]
```

### Client

```bash
python -m client.client [--host HOST] [--port PORT] [--username USERNAME]
```

## Security

- All communications are encrypted
- Password hashing with PBKDF2
- Secure credential storage
- Access control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

GNU General Public License v3.0

## Support

For support, please open an issue or contact info@tuxxle.org
