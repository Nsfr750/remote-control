# Remote-Control - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [User Interface](#user-interface)
6. [Features](#features)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)
9. [Frequently Asked Questions](#frequently-asked-questions)
10. [Support](#support)

## Introduction

Welcome to the Windsurf project! This guide will help you get started with the application and make the most of its features.

## System Requirements

### Windows
- Windows 10/11 (64-bit)
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 200MB free disk space

### Linux
- Ubuntu 20.04 LTS or later / Debian 10 or later
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 200MB free disk space

## Installation

### Windows
1. Download the latest installer from our [GitHub Releases](https://github.com/Nsfr750/remote-control/releases)
2. Run the installer and follow the on-screen instructions
3. Launch the application from the Start Menu or desktop shortcut

### Linux
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk

# Clone the repository
cd ~
git clone https://github.com/Nsfr750/remote-control.git
cd remote-control

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required system permissions for screen capture and input simulation
- Network access to the remote system

### Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/remote-control.git
   cd remote-control
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

```bash
python -m server.server --host 0.0.0.0 --port 5000
```

### Running the Client

```bash
python -m client.client --host <server-address> --port 5000
```

## User Interface

### Main Window
- **Connection Status**: Shows current connection status and server information
- **Remote Desktop**: Displays the remote screen in real-time
- **Control Bar**: Quick access to common functions
- **File Browser**: Tab for managing file transfers

### Connection Dialog
- **Server Address**: IP or hostname of the remote server
- **Port**: Server port (default: 5000)
- **Authentication**: Username and password for secure access

## Features

### Remote Desktop
- **Screen Sharing**: View the remote desktop in real-time
- **Mouse Control**: Full mouse control including movement, clicks, and scrolling
- **Keyboard Input**: Send keyboard events to the remote system
- **Multi-Monitor Support**: Switch between multiple displays on the remote system

### Input Handling
- **Platform-Specific**: Optimized implementations for Windows and Linux
- **Low Latency**: Responsive control with minimal delay
- **Secure**: Input validation to prevent unauthorized access

### File Transfer
- **Secure File Transfer**: Encrypted file transfers between systems
- **Drag & Drop**: Intuitive interface for transferring files
- **Directory Navigation**: Browse remote file system with ease

### Security
- **Encrypted Communication**: All data is encrypted in transit
- **Authentication**: Secure login with username and password
- **Access Control**: Granular permissions for different users

## Configuration

### Application Settings
Access settings through the gear icon in the top-right corner:
- **General**: Basic application preferences
- **Appearance**: Customize the look and feel
- **Network**: Configure network settings
- **Updates**: Manage automatic updates

### Configuration Files
Application configuration is stored in:
- **Windows**: `%APPDATA%\remote-control\config.ini`
- **Linux**: `~/.config/remote-control/config.ini`

## Troubleshooting

### Common Issues
1. **Application won't start**
   - Verify Python 3.8+ is installed
   - Check system requirements
   - Run with `--debug` flag for more information

2. **Missing dependencies**
   - Run `pip install -r requirements.txt`
   - Ensure all system packages are installed

3. **Performance issues**
   - Close other applications
   - Reduce update frequency in settings
   - Check system resources

### Logs
Application logs are stored in:
- **Windows**: `%APPDATA%\remote-control\logs\`
- **Linux**: `~/.local/share/remote-control/logs/`

## Frequently Asked Questions

### General
**Q: How do I update the application?**  
A: Use the built-in updater in the Help menu or download the latest release from GitHub.

**Q: Where are my settings stored?**  
A: Settings are stored in your user profile directory under `.config/remote-control/` (Linux) or `%APPDATA%\remote-control\` (Windows).

**Q: How can I contribute to the project?**  
A: Visit our [GitHub repository](https://github.com/Nsfr750/remote-control) to report issues, submit pull requests, or suggest features.

## Support

### Documentation
- [GitHub Wiki](https://github.com/Nsfr750/remote-control/wiki)
- [API Documentation](https://github.com/Nsfr750/remote-control/docs)

### Getting Help
- **GitHub Issues**: [Report issues](https://github.com/Nsfr750/remote-control/issues)
- **Email**: [Info](mailto:info@tuxxle.org)
- **Security Reports**: [Security](mailto:info@tuxxle.org)

### Donate
If you find this project useful, consider supporting its development:
- **PayPal**: [paypal.me/3dmega](https://paypal.me/3dmega)
- **Monero**: `47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF`

---
© Copyright 2024-2025 Nsfr750 - All rights reserved
