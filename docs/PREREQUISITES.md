# Prerequisites

## System Requirements

### Minimum Requirements

#### Windows
- **Operating System**: Windows 10 (64-bit) or later
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 200MB free disk space
- **Network**: TCP/IP connectivity
- **Permissions**: Administrator privileges for input simulation

#### Linux
- **Operating System**: Ubuntu 20.04 LTS / Debian 10 or later
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 200MB free disk space
- **Network**: TCP/IP connectivity
- **Display**: X11 server
- **Permissions**: User access to X11 display

### Recommended Requirements

#### For Optimal Performance
- **CPU**: Multi-core processor (4+ cores)
- **Memory**: 8GB RAM or more
- **Network**: Gigabit Ethernet or WiFi 5GHz
- **Display**: 1920x1080 resolution or higher

#### For Development
- **IDE**: VS Code, PyCharm, or similar
- **Git**: Version control for source code management
- **Python Tools**: pip, virtualenv, pytest
- **Build Tools**: Nuitka 2.8.9+ for compilation

## Software Dependencies

### Core Dependencies

```bash
# Required packages
pip install PyQt6>=6.4.0
pip install cryptography>=3.4.8
pip install numpy>=1.21.0
pip install wand>=0.6.6
pip install paramiko>=2.9.0
```

### Platform-Specific Dependencies

#### Windows

```bash
# Windows-specific packages
pip install pywin32>=304
pip install win32gui>=304
pip install win32ui>=304
pip install win32con>=304
pip install win32api>=304
```

Additional Windows requirement for screen capture conversion:
- ImageMagick (required by `wand`)

#### Linux

```bash
# Linux-specific packages
# System packages
sudo apt-get install x11-utils
sudo apt-get install scrot
sudo apt-get install xrandr

# Python packages
pip install pyautogui>=0.9.54
pip install python-xlib>=0.33
```

### Development Dependencies

```bash
# For building from source
pip install nuitka>=2.8.9
pip install pytest>=7.0.0
pip install black>=22.0.0
pip install flake8>=4.0.0
pip install mypy>=0.950
```

## Network Requirements

### Firewall Configuration

#### Windows Firewall
- **Inbound**: Allow TCP port 5000 (or custom port)
- **Outbound**: Allow TCP traffic to remote server
- **Application**: Add RemoteControlClient.exe to allowed applications

#### Linux Firewall (UFW)

```bash
# Allow server port
sudo ufw allow 5000/tcp

# Allow client outbound (usually enabled by default)
sudo ufw allow out 5000/tcp
```

### Router Configuration
- **Port Forwarding**: Forward port 5000 to server machine (if behind NAT)
- **DMZ**: Alternative to port forwarding for server access
- **QoS**: Prioritize remote control traffic for better performance

## Hardware Requirements

### Server Side
- **Display**: Active monitor connected for screen capture
- **Input**: Keyboard and mouse for remote control
- **Network**: Stable internet connection
- **Storage**: Space for log files and temporary data

### Client Side
- **Display**: Monitor for remote desktop viewing
- **Input**: Keyboard and mouse for remote control
- **Network**: Stable internet connection with low latency
- **Graphics**: Hardware acceleration support (optional)

## Optional Components

### For Enhanced Features

#### Code Signing (Windows)
- **Certificate**: Code signing certificate (.pfx/.p12)
- **Tools**: Windows SDK for signtool.exe
- **Permissions**: Administrator access for signing

#### Advanced Logging
- **Disk Space**: Additional 100MB for detailed logs
- **Tools**: Log viewing software (built-in viewer available)

Project logs are stored in the `logs/` folder.

#### File Transfer
- **Antivirus**: Real-time scanning for transferred files
- **Storage**: Additional space for file cache

## Installation Prerequisites

### Python Environment Setup

```bash
# Create virtual environment
python -m venv venv312

# Activate (Windows)
venv312\Scripts\activate

# Activate (Linux)
source venv312/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### System Preparation

#### Windows

```cmd
# Run as Administrator
# Install Visual C++ Redistributable (if needed)
# Disable antivirus real-time protection during installation
```

#### Linux

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install build dependencies
sudo apt install build-essential python3-dev

# Install X11 libraries
sudo apt install libx11-dev libxrandr-dev
```

## Testing Prerequisites

### Environment Validation

```python
# Test script to verify prerequisites
import sys
import platform
import subprocess

def check_python_version():
    if sys.version_info >= (3, 8):
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_platform():
    system = platform.system().lower()
    if system in ['windows', 'linux']:
        print(f"✅ Platform {system} supported")
        return True
    else:
        print(f"❌ Platform {system} not supported")
        return False

def check_dependencies():
    try:
        import PyQt6
        print("✅ PyQt6 available")
    except ImportError:
        print("❌ PyQt6 missing")
        return False
    
    try:
        import cryptography
        print("✅ Cryptography available")
    except ImportError:
        print("❌ Cryptography missing")
        return False
    
    return True

if __name__ == "__main__":
    print("Checking prerequisites...")
    all_good = True
    all_good &= check_python_version()
    all_good &= check_platform()
    all_good &= check_dependencies()
    
    if all_good:
        print("✅ All prerequisites satisfied")
    else:
        print("❌ Some prerequisites missing")
```

## Troubleshooting Prerequisites

### Common Issues

#### Python Version Conflicts
- **Problem**: Multiple Python installations
- **Solution**: Use full path to correct Python executable
- **Example**: `C:\Python312\python.exe -m venv venv312`

#### Permission Denied (Linux)
- **Problem**: Cannot access X11 display
- **Solution**: Set DISPLAY environment variable
- **Example**: `export DISPLAY=:0`

#### Network Connection Issues
- **Problem**: Cannot connect to remote server
- **Solution**: Check firewall and router settings
- **Test**: `telnet server_ip 5000`

#### Missing Dependencies
- **Problem**: Import errors for required packages
- **Solution**: Install from requirements.txt
- **Command**: `pip install -r requirements.txt`

---

**Last Updated**: December 27, 2025  
**Version**: 1.0.1  
**Supported Platforms**: Windows 10+, Ubuntu 20.04+
