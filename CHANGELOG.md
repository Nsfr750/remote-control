# 📜 Changelog

All notable changes to this project will be documented in this file.

## 🚀 [1.0.1] - 2025-12-27

### 🐛 Fixed

- ✅ **Authentication Responses**: Standardized auth failures to return `AUTH_RESPONSE` (instead of `ERROR`) to avoid client-side parsing issues
- 🖥️ **Screen Controller Availability**: Resolved platform import conflicts that prevented screen capture initialization on Windows

### ✨ Added

- 🧾 **Log Viewer (Client)**: Added **Tools -> View Logs** to inspect log files inside the `logs/` folder
- 🗂️ **Centralized Logs Folder**: Server and client logs are now written under `logs/`
- 🎨 **Application Icon**: Client and server GUI configuration dialog now use `assets/icon.png`

### 🔄 Changed

- 🧹 **Better Diagnostics**: Improved debug logging around authentication, screen capture, and connection lifecycle

## 🚀 [1.0.0] - 2025-12-26

### ✨ Added 1.0.0

- 🔧 **Nuitka Compilation**: Added separate build scripts for client and server
- 📦 **Standalone Executables**: Successfully compiled RemoteControlClient.exe and RemoteControlServer.exe
- 🔐 **Code Signing**: Integrated digital certificate signing for executables
- 🖥️ **Linux Screen Capture**: Implemented proper Linux screen capture using import/scrot
- 📁 **File Transfer System**: Added complete file upload/download functionality
- 🖱️ **Mouse Control**: Fixed Linux mouse click handling with proper success detection
- ⌨️ **Fullscreen Exit**: Added ESC key to exit fullscreen mode
- 🛡️ **Socket Error Handling**: Improved disconnect handling to prevent socket errors
- 🎨 **Image Loading**: Enhanced client to support multiple image formats (PNG/JPEG)
- 🐛 **Debug Logging**: Added comprehensive debugging for mouse and screen operations

### 🔄 Changed 1.0.0

- 🏗️ **Build System**: Switched from single comp.py to separate build_client.py/build_server.py
- 🔧 **Nuitka Options**: Optimized compilation flags for PyQt6 compatibility
- 📊 **Error Handling**: Improved exception handling throughout client-server communication
- 🖼️ **Image Format**: Server now sends JPEG format for better compatibility

- ♻️ Refactored message handling in client.py
- 📚 Updated documentation structure and content
- 💬 Improved error messages and user feedback
- ⚡ Optimized network communication
- 🎨 UI/UX improvements for better usability

### 🐛 Fixed 1.0.0

- 💥 **Cryptography Issues**: Resolved _cffi_backend import errors
- 🔢 **NumPy Compatibility**: Fixed C extension compatibility issues
- 🖱️ **Mouse Click Errors**: Fixed "SUCCESS" being treated as error
- 📱 **Fullscreen Mode**: Added proper exit mechanism with ESC key
- 🔌 **Socket Errors**: Resolved WinError 10038 during disconnect
- 🖼️ **Static Screen Issue**: Fixed Linux server sending same screenshot repeatedly
- 📁 **File Transfer**: Implemented missing file transfer handler
- 🎨 **Image Loading**: Fixed client unable to display server screenshots

- 🔌 Fixed connection stability issues
- 🏎️ Resolved authentication race conditions
- 🖥️ Fixed screen sharing performance issues
- 🔒 Addressed security vulnerabilities in message processing
- 📂 Fixed file transfer reliability issues

### ⚡ Performance

- 🚀 **Faster Compilation**: Separate build scripts reduce compilation time
- 📊 **Better Logging**: Reduced debug overhead while maintaining detail
- 🔄 **Real-time Updates**: Improved screen capture frequency and quality

---

## 🎉 [0.1.0] - 2025-12-20

### ✨ Added (0.1.0)

- 🎯 Initial release
- 🖱️ Core remote control functionality
- 📁 Basic file transfer capabilities
- 📊 System information display
- 🔑 Basic authentication system

### 🔧 Technical Details

- Built with Python 3.8+
- Cross-platform support (Windows, Linux, macOS)
- Modular architecture for easy extension
- Comprehensive API documentation

### 📦 Dependencies

- PyQt6 for the GUI
- cryptography for security
- paramiko for SSH capabilities
- wand for image processing

---

## 📝 Versioning

This project uses [Semantic Versioning](https://semver.org/). For the versions available, see the [tags on this repository](https://github.com/Nsfr750/remote-control/tags).

## 📄 License

This project is licensed under the GPL v3 License - see the [LICENSE](LICENSE) file for details.
