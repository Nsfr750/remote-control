# Troubleshooting Guide

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Connection Problems](#connection-problems)
3. [Screen Sharing Issues](#screen-sharing-issues)
4. [Input Control Issues](#input-control-issues)
5. [File Transfer Problems](#file-transfer-problems)
6. [Performance Issues](#performance-issues)
7. [Platform-Specific Issues](#platform-specific-issues)
8. [Advanced Debugging](#advanced-debugging)

## Installation Issues

### Python Environment Problems

#### Issue: "Python not found" or version errors
**Symptoms:**
- `python: command not found`
- `Python 3.8+ required` message
- Multiple Python versions causing conflicts

**Solutions:**

1. **Verify Python Installation:**

   ```bash
   python --version
   python3 --version
   ```

2. **Use Full Path:**

   ```bash
   # Windows
   C:\Python312\python.exe --version
   
   # Linux
   /usr/bin/python3 --version
   ```

3. **Update PATH Environment:**

   ```bash
   # Windows (add to System PATH)
   C:\Python312\
   C:\Python312\Scripts\
   
   # Linux (add to ~/.bashrc)
   export PATH="/usr/bin/python3:$PATH"
   ```

#### Issue: Virtual environment creation fails
**Symptoms:**
- `venv creation failed`
- Permission denied errors
- Module import errors

**Solutions:**

1. **Check Python Version:**

   ```bash
   python -m venv --help
   # Requires Python 3.7+
   ```

2. **Use Alternative Creation:**

   ```bash
   # Try different method
   python -m virtualenv venv312
   
   # Install virtualenv if needed
   pip install virtualenv
   ```

3. **Check Permissions:**

   ```bash
   # Linux: Ensure write permissions
   ls -la
   chmod 755 .
   
   # Windows: Run as Administrator
   # Right-click -> Run as administrator
   ```

### Dependency Installation Problems

#### Issue: "Failed building wheel" errors
**Symptoms:**
- Compiler errors during pip install
- Microsoft Visual C++ errors
- Missing build tools

**Solutions:**

1. **Install Build Tools (Windows):**

   ```cmd
   # Install Microsoft C++ Build Tools
   # Download from Visual Studio Installer
   
   # Or use pre-built wheels
   pip install --only-binary=all package_name
   ```

2. **Install Development Headers (Linux):**

   ```bash
   sudo apt-get install build-essential python3-dev
   sudo dnf install gcc python3-devel
   sudo pacman -S base-devel python
   ```

3. **Use Pre-compiled Wheels:**

   ```bash
   pip install --only-binary :all:
   pip install --prefer-binary
   ```

#### Issue: Cryptography installation fails
**Symptoms:**
- `_cffi_backend` import errors
- Rust compiler required errors
- Linking errors

**Solutions:**

1. **Install Rust Compiler:**

   ```bash
   # Windows: Install rustup
   # https://rustup.rs/
   
   # Linux
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Force Reinstall:**

   ```bash
   pip uninstall cryptography cffi
   pip install --upgrade cryptography
   pip install --upgrade cffi
   ```

3. **Use Pre-built Wheel:**

   ```bash
   pip install --only-binary :all: cryptography
   ```

## Connection Problems

### Network Connectivity Issues

#### Issue: "Connection refused" or timeout
**Symptoms:**
- Unable to connect to server
- Connection timeout errors
- Network unreachable messages

**Diagnostic Steps:**

1. **Test Basic Connectivity:**

   ```bash
   ping server_ip
   traceroute server_ip
   ```

2. **Test Port Accessibility:**

   ```bash
   telnet server_ip 5000
   nc -zv server_ip 5000
   ```

3. **Check Server Status:**

   ```bash
   # On server machine
   netstat -tlnp | grep 5000
   ss -tlnp | grep 5000
   ```

**Solutions:**

1. **Firewall Configuration:**

   ```bash
   # Windows Firewall
   # Add inbound rule for port 5000
   
   # Linux UFW
   sudo ufw allow 5000/tcp
   sudo ufw reload
   ```

2. **Router Port Forwarding:**
   - Access router admin panel
   - Forward port 5000 to server's local IP
   - Enable DMZ as alternative

3. **Server Configuration:**

   ```bash
   # Bind to all interfaces
   python -m server.server --host 0.0.0.0 --port 5000
   ```

#### Issue: "Authentication failed" errors
**Symptoms:**
- Invalid credentials message
- Repeated authentication prompts
- Access denied errors

**Diagnostic Steps:**

1. **Verify Server Configuration:**

   ```bash
   # Check if server has user accounts
   # Review server logs for authentication attempts
   ```

2. **Test Credentials Manually:**

   ```bash
   # Test with simple script
   python -c "
   import json
   from common.security import hash_password
   print(hash_password('your_password', 'salt'))
   "
   ```

**Solutions:**

1. **Reset Server Passwords:**

   ```bash
   # Check server documentation for password reset
   # Review user configuration files
   ```

2. **Check Case Sensitivity:**
   - Usernames may be case-sensitive
   - Verify exact spelling and case

3. **Clear Client Cache:**
   ```bash
   # Remove saved credentials
   # Clear authentication cache
   # Restart client application
   ```

### SSL/TLS Issues

#### Issue: Certificate validation errors
**Symptoms:**
- SSL handshake failed
- Certificate verification errors
- Secure connection warnings

**Solutions:**

1. **Generate New Certificates:**

   ```bash
   # For development
   openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
   
   # For production
   # Use proper CA-signed certificates
   ```

2. **Update Certificate Stores:**

   ```bash
   # Update system certificates
   sudo update-ca-certificates
   
   # Windows: Update certificate stores
   ```

3. **Disable Verification (Development Only):**

   ```bash
   # NOT RECOMMENDED FOR PRODUCTION
   export VERIFY_SSL=false
   ```

## Screen Sharing Issues

### Screen Capture Problems

#### Issue: Black screen or no image
**Symptoms:**
- Client shows black screen
- No image data received
- Static/corrupted display

**Diagnostic Steps:**

1. **Check Server Screen Capture:**

   ```bash
   # Test screen capture manually
   python -c "
   from server.platform.windows.screen import WindowsScreenCapture
   capture = WindowsScreenCapture()
   result = capture.capture_screen()
   print(f'Capture result: {len(result) if result else None} bytes')
   "
   ```

2. **Verify Image Format:**

   ```bash
   # Check if PNG is being generated
   file screenshot.png
   hexdump -C screenshot.png | head -5
   ```

**Solutions:**

1. **Windows Screen Capture:**

   ```cmd
   # Install required dependencies
   pip install --upgrade pywin32
   pip install --upgrade numpy
   pip install --upgrade wand
   
   # Check display settings
   # Ensure desktop is not locked
   # Verify screen resolution
   ```

2. **Linux Screen Capture:**

   ```bash
   # Install required tools
   sudo apt-get install import
   sudo apt-get install scrot
   sudo apt-get install x11-utils
   
   # Test tools manually
   import -window root -screen png test.png
   scrot test.png
   ```

#### Issue: Low image quality or performance
**Symptoms:**
- Blurry or pixelated display
- Slow screen updates
- High bandwidth usage

**Solutions:**

1. **Adjust Image Quality:**

   ```python
   # In server configuration
   IMAGE_QUALITY = 85  # JPEG quality (1-100)
   COMPRESSION_LEVEL = 6  # PNG compression (0-9)
   ```

2. **Optimize Screen Resolution:**

   ```python
   # Capture at lower resolution
   CAPTURE_SCALE = 0.75  # 75% of native resolution
   ```

3. **Enable Image Compression:**

   ```bash
   # Use JPEG instead of PNG
   # Adjust quality settings
   # Implement differential updates
   ```

### Display Resolution Issues

#### Issue: Incorrect screen size or scaling
**Symptoms:**
- Wrong resolution detected
- Incorrect aspect ratio
- Scaling problems

**Solutions:**

1. **Manual Resolution Configuration:**

   ```python
   # Override auto-detection
   SCREEN_WIDTH = 1920
   SCREEN_HEIGHT = 1080
   ```

2. **Multi-Monitor Setup:**

   ```python
   # Specify primary monitor
   PRIMARY_MONITOR = 0
   
   # Or capture all monitors
   CAPTURE_ALL_MONITORS = True
   ```

## Input Control Issues

### Mouse Control Problems

#### Issue: Mouse clicks not working
**Symptoms:**
- Clicks not registered on server
- Wrong button mapping
- Delayed response

**Diagnostic Steps:**

1. **Test Mouse Input Locally:**

   ```bash
   # Test input simulation
   python -c "
   from server.platform.windows.input import WindowsInputHandler
   input_handler = WindowsInputHandler()
   result = input_handler.send_mouse_click(100, 100, 'left', False)
   print(f'Mouse click result: {result}')
   "
   ```

2. **Check Button Mapping:**

   ```python
   # Verify button codes
   BUTTON_MAP = {'left': 1, 'middle': 2, 'right': 3}
   ```

**Solutions:**

1. **Windows Input Issues:**

   ```cmd
   # Run as administrator
   # Check UAC settings
   # Verify security software isn't blocking
   ```

2. **Linux Input Issues:**

   ```bash
   # Check X11 permissions
   xhost +local:username
   
   # Verify pyautogui installation
   pip install --upgrade pyautogui
   
   # Test with X11 display
   export DISPLAY=:0
   ```

#### Issue: Mouse movement is jerky or inaccurate
**Symptoms:**
- Unsmooth mouse movement
- Position drift
- Inaccurate tracking

**Solutions:**

1. **Adjust Mouse Sensitivity:**

   ```python
   # Configure sensitivity multiplier
   MOUSE_SENSITIVITY = 1.0
   SMOOTHING_FACTOR = 0.8
   ```

2. **Reduce Network Latency:**

   ```bash
   # Use wired connection
   # Reduce capture interval
   # Optimize image compression
   ```

### Keyboard Input Problems

#### Issue: Keys not registering or wrong characters
**Symptoms:**
- Keyboard input not working
- Wrong characters typed
- Modifier keys not working

**Solutions:**

1. **Check Keyboard Layout:**

   ```python
   # Configure keyboard layout
   KEYBOARD_LAYOUT = 'us'  # or 'uk', 'de', etc.
   ```

2. **Verify Key Mapping:**

   ```python
   # Test key codes
   from server.platform.windows.input import WindowsInputHandler
   handler = WindowsInputHandler()
   handler.send_key_press('a')  # Test individual keys
   ```

3. **Check Input Method:**

   ```bash
   # Linux: Ensure correct X11 input method
   # Windows: Check language bar settings
   # Verify no conflicting hotkeys
   ```

## File Transfer Problems

### Upload/Download Issues

#### Issue: File transfer fails
**Symptoms:**
- Upload/download doesn't start
- Transfer stops midway
- File corruption

**Diagnostic Steps:**

1. **Test File Permissions:**

   ```bash
   # Check directory permissions
   ls -la /path/to/directory
   
   # Test file creation
   touch /path/to/directory/test.txt
   ```

2. **Verify Network Stability:**

   ```bash
   # Test with large file transfer
   dd if=/dev/zero of=test_file bs=1M count=10
   # Monitor connection stability
   ```

**Solutions:**

1. **Check File Path Security:**

   ```python
   # Verify allowed directories
   ALLOWED_DIRS = ['/home/user/Downloads', '/tmp']
   
   # Validate paths
   def is_path_safe(path, allowed_dirs):
       return any(path.startswith(allowed) for allowed in allowed_dirs)
   ```

2. **Adjust Transfer Settings:**

   ```python
   # Configure chunk size
   CHUNK_SIZE = 8192  # bytes
   TIMEOUT = 30  # seconds
   
   # Enable resume capability
   RESUME_TRANSFERS = True
   ```

#### Issue: Slow file transfers
**Symptoms:**
- Very slow upload/download speeds
- Transfer timeouts
- Poor performance

**Solutions:**

1. **Optimize Chunk Size:**

   ```python
   # Experiment with different sizes
   CHUNK_SIZE = 65536  # 64KB chunks
   
   # Or use adaptive sizing
   def get_optimal_chunk_size(file_size, network_speed):
       # Calculate based on conditions
   ```

2. **Enable Compression:**

   ```python
   # Compress files before transfer
   import gzip
   import shutil
   
   with gzip.open('file.txt.gz', 'wb') as f_out:
       with open('file.txt', 'rb') as f_in:
           shutil.copyfileobj(f_in, f_out)
   ```

## Performance Issues

### High CPU Usage

#### Issue: Server CPU usage too high
**Symptoms:**
- Server process using 50%+ CPU
- System becomes sluggish
- Fan running constantly

**Diagnostic Steps:**

1. **Monitor Process Usage:**

   ```bash
   # Linux
   top -p $(pgrep -f "python.*server")
   
   # Windows
   tasklist /fi "imagename eq python.exe"
   ```

2. **Profile Python Code:**

   ```bash
   # Use cProfile
   python -m cProfile -o profile.stats -m server.server
   
   # Analyze results
   python -c "
   import pstats
   p = pstats.Stats('profile.stats')
   p.sort_stats('cumulative').print_stats(20)
   "
   ```

**Solutions:**

1. **Optimize Screen Capture:**

   ```python
   # Reduce capture frequency
   CAPTURE_INTERVAL = 0.1  # seconds
   
   # Skip unchanged frames
   if not screen_changed():
       continue
   
   # Use differential updates
   CAPTURE_DIFFERENCES = True
   ```

2. **Optimize Image Processing:**

   ```python
   # Reduce image quality
   JPEG_QUALITY = 75
   
   # Use faster compression
   COMPRESSION_SPEED = 'fast'
   
   # Limit capture resolution
   MAX_RESOLUTION = (1920, 1080)
   ```

### Memory Usage Issues

#### Issue: Memory leaks or high usage
**Symptoms:**
- Memory usage increases over time
- Application crashes after extended use
- System becomes unresponsive

**Solutions:**

1. **Monitor Memory Usage:**

   ```python
   import psutil
   import gc
   
   def monitor_memory():
       process = psutil.Process()
       print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
       gc.collect()  # Force garbage collection
   ```

2. **Implement Resource Cleanup:**

   ```python
   # Explicit cleanup
   def cleanup_resources():
       image_data = None  # Release large objects
       gc.collect()
   
   # Use context managers
   with open('file.png', 'rb') as f:
       data = f.read()
   ```

## Platform-Specific Issues

### Windows-Specific Problems

#### Issue: UAC prompts
**Symptoms:**
- User Account Control prompts
- Administrator permission required
- Input simulation blocked

**Solutions:**

1. **Run as Administrator:**
   ```cmd
   # Right-click executable
   # "Run as administrator"
   
   # Or modify manifest
   <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
   ```

2. **Configure UAC Settings:**
   - Lower UAC level (not recommended)
   - Add application to trusted list
   - Use digital code signing

#### Issue: Windows Defender blocking
**Symptoms:**
- Real-time protection blocks application
- False positive detections
- Features disabled

**Solutions:**

1. **Add Exclusions:**
   ```cmd
   # Add to Windows Defender exclusions
   # Exclude folder and executable
   
   # Or use PowerShell
   Add-MpPreference -ExclusionPath "C:\path\to\RemoteControl*.exe"
   ```

2. **Submit False Positive:**
   - Report to Microsoft
   - Request signature review
   - Use code signing certificate

### Linux-Specific Problems

#### Issue: X11 Display errors
**Symptoms:**
- Cannot connect to display
- "Display :0 not found"
- Screen capture fails

**Solutions:**

1. **Configure X11 Access:**

   ```bash
   # Set display variable
   export DISPLAY=:0
   
   # Allow local connections
   xhost +local:
   
   # Test X11 connection
   xdpyinfo -display :0
   ```

2. **Handle Wayland:**

   ```bash
   # Switch to X11 session
   # At login, select X11 instead of Wayland
   
   # Or use XWayland
   export GDK_BACKEND=x11
   export QT_QPA_PLATFORM=xcb
   ```

#### Issue: Permission denied errors
**Symptoms:**
- Permission denied for screen capture
- Cannot access input devices
- File access errors

**Solutions:**

1. **Check User Groups:**

   ```bash
   # Add user to required groups
   sudo usermod -a -G input,video $USER
   
   # Log out and back in
   groups $USER
   ```

2. **Verify File Permissions:**
   ```bash
   # Check directory permissions
   ls -la ~/.config/
   chmod 755 ~/.config/
   
   # Set proper ownership
   sudo chown $USER:$USER ~/.config/
   ```

## Advanced Debugging

### Enable Verbose Logging

#### Debug Mode

```bash
# Enable debug logging
python -m client.client --host localhost --port 5000 --debug
python -m server.server --host 0.0.0.0 --port 5000 --debug
```

#### Log Configuration

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Network Debugging

#### Packet Capture

```bash
# Capture network traffic
sudo tcpdump -i any port 5000 -w capture.pcap

# Analyze with Wireshark
wireshark capture.pcap
```

#### Connection Testing

```python
import socket
import time

def test_connection(host, port):
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        end = time.time()
        sock.close()
        
        print(f"Connection: {result == 0}")
        print(f"Latency: {(end - start) * 1000:.2f}ms")
        return result == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

test_connection('192.168.1.4', 5000)
```

### Performance Profiling

#### CPU Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    result = your_function()
    
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    
    return result

profile_function()
```

#### Memory Profiling

```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Your code here
your_function()

# Get statistics
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")

# Get top allocations
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

## Getting Additional Help

### Community Resources

- **GitHub Issues**: [Report problems](https://github.com/Nsfr750/remote-control/issues)
- **GitHub Discussions**: [Community support](https://github.com/Nsfr750/remote-control/discussions)
- **Documentation**: [Complete docs](./)
- **API Reference**: [Technical details](API.md)

### Contact Information

- **General Support**: [info@tuxxle.org](mailto:info@tuxxle.org)
- **Security Issues**: [Security reporting](SECURITY.md)
- **Project Maintainer**: [Nsfr750](https://github.com/Nsfr750)

---

**Last Updated**: December 26, 2025  
**Version**: 1.0.0  
**For more help**: See [FAQ.md](FAQ.md) or [CONTRIBUTING.md](CONTRIBUTING.md)
