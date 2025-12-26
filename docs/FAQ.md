# Frequently Asked Questions (FAQ)

## Table of Contents
1. [Installation and Setup](#installation-and-setup)
2. [Connection Issues](#connection-issues)
3. [Usage and Features](#usage-and-features)
4. [Security and Privacy](#security-and-privacy)
5. [Platform-Specific Issues](#platform-specific-issues)
6. [Development and Contributing](#development-and-contributing)

## Installation and Setup

### Q: What are the minimum system requirements?
**A:** 
- **Windows**: Windows 10 (64-bit) or later, Python 3.8+, 4GB RAM
- **Linux**: Ubuntu 20.04+ / Debian 10+, Python 3.8+, 4GB RAM
- **Network**: TCP/IP connectivity, port 5000 (default) open

See [PREREQUISITES.md](PREREQUISITES.md) for detailed requirements.

### Q: How do I install the application?
**A:** You have several options:

1. **Pre-built Executables** (Recommended):
   - Download from [GitHub Releases](https://github.com/Nsfr750/remote-control/releases)
   - Extract and run `RemoteControlClient.exe` or `RemoteControlServer.exe`

2. **From Source**:
   ```bash
   git clone https://github.com/Nsfr750/remote-control.git
   cd remote-control
   python -m venv venv312
   source venv312/bin/activate  # Linux
   # or venv312\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Build from Source**:
   ```bash
   python setup/build_client.py  # Build client
   python setup/build_server.py  # Build server
   ```

### Q: Do I need administrator privileges?
**A:** It depends on your platform:

- **Windows**: Yes, for input simulation and screen capture
- **Linux**: No, but need X11 display access
- **Server**: Generally not required unless using privileged ports (< 1024)

### Q: How do I configure firewall settings?
**A:** 

**Windows Firewall**:
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add RemoteControlClient.exe and RemoteControlServer.exe
4. Allow TCP port 5000 (or your custom port)

**Linux (UFW)**:
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

## Connection Issues

### Q: "Connection refused" error
**A:** Common causes and solutions:

1. **Server not running**: Start the server first
   ```bash
   python -m server.server --host 0.0.0.0 --port 5000
   ```

2. **Wrong IP/Port**: Verify server address and port
3. **Firewall blocking**: Configure firewall as above
4. **Network issues**: Test connectivity:
   ```bash
   ping server_ip
   telnet server_ip 5000
   ```

### Q: "Authentication failed" error
**A:** Check these items:

1. **Correct credentials**: Verify username and password
2. **Server configuration**: Ensure server has user accounts configured
3. **Case sensitivity**: Usernames may be case-sensitive
4. **Special characters**: Some characters may cause issues

### Q: Connection drops frequently
**A:** Try these solutions:

1. **Network stability**: Check WiFi/cable connection
2. **Keepalive settings**: Ensure keepalive is enabled
3. **Firewall/antivirus**: May timeout connections
4. **Server resources**: Check server CPU/memory usage

### Q: Can't connect from outside local network
**A:** You need port forwarding:

1. **Router setup**: Forward port 5000 to server's local IP
2. **Dynamic DNS**: Use services like No-IP if your IP changes
3. **Public IP**: Use your public IP, not local (192.168.x.x)
4. **Test from external**: Use mobile data to test external access

## Usage and Features

### Q: How do I exit fullscreen mode?
**A:** Press the **ESC key** to exit fullscreen mode and return to windowed mode.

### Q: Mouse clicks aren't working on Linux
**A:** This is a known issue with some Linux configurations:

1. **Check X11 permissions**:
   ```bash
   xhost +local:username
   ```

2. **Verify pyautogui installation**:
   ```bash
   pip install pyautogui
   ```

3. **Check display server**: Ensure X11 is running (not Wayland by default)

### Q: Screen sharing shows static/old image
**A:** For Linux servers, ensure screen capture tools are installed:

```bash
# Install required tools
sudo apt-get install import
sudo apt-get install scrot
sudo apt-get install x11-utils

# Test screen capture
import -window root -screen png test.png
```

### Q: How do I transfer files?
**A:** Use the built-in file transfer feature:

1. **Upload**: Select files in client and click "Upload"
2. **Download**: Browse remote files and click "Download"
3. **Directory navigation**: Use the file browser to navigate folders
4. **Batch operations**: Select multiple files for bulk operations

### Q: What image formats are supported?
**A:** The client supports multiple formats automatically:

- **PNG**: Primary format (Windows servers)
- **JPEG**: Fallback format (Linux servers)
- **Auto-detection**: Client tries PNG first, then JPEG

## Security and Privacy

### Q: Is my connection secure?
**A:** Yes, the application uses:

- **AES-256 encryption** for all data transmission
- **PBKDF2 key derivation** for password hashing
- **TLS 1.2+** for secure connections
- **Session tokens** with expiration

### Q: Are my credentials stored securely?
**A:** Yes:

- **Passwords are hashed** using PBKDF2 with salt
- **No plain text storage** of sensitive information
- **Local encryption** for stored credentials (optional)
- **Secure memory handling** for sensitive data

### Q: Can someone intercept my session?
**A:** The application includes protections against:

- **Man-in-the-middle attacks** via certificate validation
- **Session hijacking** via secure token management
- **Replay attacks** via unique session identifiers
- **Eavesdropping** via end-to-end encryption

### Q: How do I report security issues?
**A:** Report security vulnerabilities privately:

- **Email**: [info@tuxxle.org](mailto:info@tuxxle.org)
- **Subject**: [SECURITY] Vulnerability description
- **Response**: Within 48 hours

See [SECURITY.md](SECURITY.md) for detailed security information.

## Platform-Specific Issues

### Windows

#### Q: "Screen controller not available" error
**A:** Install required dependencies:

```cmd
pip install --upgrade pywin32
pip install --upgrade numpy
pip install --upgrade wand
```

#### Q: Administrator access required?
**A:** Yes, for:

- **Screen capture**: Requires access to desktop
- **Input simulation**: Requires privilege escalation
- **System hooks**: Need administrator permissions

#### Q: Windows Defender blocks the application
**A:** Add exceptions:

1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings"
4. Add exclusions for RemoteControl*.exe

### Linux

#### Q: X11 display errors
**A:** Set up X11 properly:

```bash
# Set display variable
export DISPLAY=:0

# Allow local connections
xhost +local:

# Test X11 connection
echo $DISPLAY
```

#### Q: Wayland compatibility?
**A:** Currently **not fully supported**. Solutions:

1. **Switch to X11** (recommended):
   ```bash
   # At login, choose X11 session
   # Or configure Wayland to use XWayland
   ```

2. **Use XWayland** (limited support):
   ```bash
   # Some applications work via XWayland compatibility
   ```

#### Q: Missing scrot/import tools
**A:** Install required packages:

```bash
# Ubuntu/Debian
sudo apt-get install scrot imagemagick x11-utils

# Fedora/RHEL
sudo dnf install scrot ImageMagick xorg-x11-utils

# Arch Linux
sudo pacman -S scrot imagemagick xorg-x11-utils
```

## Development and Contributing

### Q: How do I contribute to the project?
**A:** See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines:

1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes
3. **Follow code style** guidelines (Black, flake8)
4. **Write tests** for new functionality
5. **Submit a pull request** with description

### Q: What coding style is required?
**A:** The project uses:

- **Black** for code formatting (88 character line length)
- **flake8** for linting
- **mypy** for type checking
- **PEP 8** compliance
- **Type hints** required for new code

### Q: How do I build the executables?
**A:** Use the build scripts:

```bash
# Build client
python setup/build_client.py

# Build server
python setup/build_server.py

# Both will be created in dist/ directory
```

### Q: How do I run tests?
**A:** Use pytest:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=client --cov=server --cov=common

# Run specific test
pytest tests/test_client.py
```

## Performance and Optimization

### Q: How can I improve performance?
**A:** Several optimization options:

1. **Network**: Use wired connection instead of WiFi
2. **Display**: Lower remote resolution if needed
3. **Compression**: Enable image compression in settings
4. **Resources**: Close unnecessary applications on server
5. **Hardware**: Use SSD for better I/O performance

### Q: High CPU usage on server
**A:** Common causes:

1. **Screen capture frequency**: Reduce screenshot interval
2. **Image compression**: Enable compression to reduce processing
3. **Multiple clients**: Limit concurrent connections
4. **Background processes**: Check for interfering applications

### Q: Lag in mouse/keyboard response
**A:** Troubleshooting steps:

1. **Network latency**: Test ping to server
2. **Server load**: Check CPU/memory usage
3. **Input processing**: Restart input services
4. **Display settings**: Reduce resolution or color depth

## Troubleshooting Common Issues

### Q: Application won't start
**A:** Check these items:

1. **Python version**: Ensure 3.8+ is installed
2. **Dependencies**: Verify all packages are installed
3. **Permissions**: Run as administrator if needed
4. **Antivirus**: Temporarily disable during testing
5. **Logs**: Check error logs for specific issues

### Q: "Module not found" errors
**A:** Install missing dependencies:

```bash
# Install all requirements
pip install -r requirements.txt

# Install specific missing module
pip install module_name

# Upgrade pip if needed
python -m pip install --upgrade pip
```

### Q: How do I enable debug logging?
**A:** Use debug flags:

```bash
# Client debug
python -m client.client --host localhost --port 5000 --debug

# Server debug
python -m server.server --host 0.0.0.0 --port 5000 --debug

# Check logs in view_log.py or console output
```

## Getting Help

### Q: Where can I get additional help?
**A:** Several resources available:

1. **Documentation**: [docs/](./) directory
2. **GitHub Issues**: [Create an issue](https://github.com/Nsfr750/remote-control/issues)
3. **GitHub Discussions**: [Ask questions](https://github.com/Nsfr750/remote-control/discussions)
4. **Email Support**: [info@tuxxle.org](mailto:info@tuxxle.org)

### Q: How do I report bugs?
**A:** Use the bug report template in GitHub Issues:

1. **Environment**: OS, Python version, app version
2. **Steps to reproduce**: Detailed reproduction steps
3. **Expected vs Actual**: What should happen vs what happens
4. **Logs**: Include relevant log output
5. **Screenshots**: If applicable to visual issues

### Q: How can I request new features?
**A:** Feature request process:

1. **Check existing issues**: Avoid duplicates
2. **Use feature request template**: Describe the feature clearly
3. **Explain use case**: Why the feature is needed
4. **Consider implementation**: Suggest possible approaches
5. **Community discussion**: Engage with other users

---

**Last Updated**: December 26, 2025  
**Version**: 1.0.0  
**For more help**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [CONTRIBUTING.md](CONTRIBUTING.md)
