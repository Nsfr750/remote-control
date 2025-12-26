"""
Version information
"""

# Version as a tuple (major, minor, patch)
VERSION = (1, 0, 1)

# String version
__version__ = ".".join(map(str, VERSION))

# Detailed version information
__status__ = "stable"
__author__ = "Nsfr750"
__maintainer__ = "Nsfr750"
__organization__ = 'Tuxxle'
__copyright__ = '© 2024-2025 Nsfr750 - All Rights Reserved'
__email__ = "nsfr750@yandex.com"
__license__ = "GPL-3.0"

# Build information
__build__ = ""
__date__ = "2025-12-24"

# Version description
__description__ = "A modern graphical user interface for remote control with enhanced encryption and security features"

# Dependencies
__requires__ = [
    "PyQt6>=6.6.1",
    "cryptography>=41.0.7",
    "pyautogui>=0.9.54",
    "watchdog>=3.0.0",
    "keyboard>=0.13.5",
    "pywin32>=306,<308; sys_platform == 'win32'",
    "python-xlib>=0.33; sys_platform == 'linux'",
    "wand>=0.6.11",
    "qrcode>=7.4.2",
    "psutil>=7.1.3",
    "pylint>=4.0.4"
]

# Version as a tuple for comparison
version_info = tuple(map(int, __version__.split('.')))

# Changelog
__changelog__ = """
## [1.0.1] - 2025-12-26
### Added
- Enhanced server GUI with user/password configuration fields
- Public IP detection in server configuration dialog
- Fixed platform import conflicts for better cross-platform compatibility
- Added user password update functionality
- Improved authentication error handling

### Fixed
- Fixed AttributeError in server authentication (MessageType.ERROR vs AUTH_RESPONSE)
- Resolved platform module naming conflicts
- Fixed client authentication flow
- Improved error handling in screen and input controllers

## [1.0.0] - 2025-12-25
### Added
- Complete remote control server and client implementation
- PyQt6-based GUI with modern interface
- Secure authentication with encrypted communication
- Screen sharing and remote control capabilities
- File transfer functionality
- System information monitoring
- Cross-platform support (Windows/Linux)
- Menu system with File, Help, and Support options
- System tray integration
- Comprehensive logging and error handling

## [0.1.0] - 2025-12-20
### Added
- Initial release
"""

def get_version():
    """Return the current version as a string."""
    return __version__

def get_version_info():
    """Return the version as a tuple for comparison."""
    return VERSION

def get_version_history():
    """Return the version history."""
    return [
           {
            "version": "0.1.0",
            "date": "2025-12-20",
            "changes": [
                "Initial release with basic functionality"
            ]
        }
    ]

def get_latest_changes():
    """Get the changes in the latest version."""
    if get_version_history():
        return get_version_history()[0]['changes']
    return []

def is_development():
    """Check if this is a development version."""
    return "dev" in __version__ or "a" in __version__ or "b" in __version__

def get_codename():
    """Get the codename for this version."""
    # Simple codename based on version number
    major, minor, patch = VERSION
    codenames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]
    return codenames[minor % len(codenames)]

def check_for_updates(current_version=None):
    """Check if there are updates available."""
    if current_version is None:
        current_version = get_version()
    
    # This would typically check against a remote server
    # For now, return a mock response
    return {
        'has_update': False,
        'current_version': current_version,
        'latest_version': __version__,
        'update_url': 'https://github.com/Nsfr750/remote-control/releases',
        'release_notes': get_latest_changes()
    }

def update_version_info(new_version):
    """Update the version information."""
    global VERSION, __version__, version_info
    
    if isinstance(new_version, str):
        VERSION = tuple(map(int, new_version.split('.')))
    else:
        VERSION = new_version
    
    __version__ = ".".join(map(str, VERSION))
    version_info = tuple(map(int, __version__.split('.')))
    
    # Update build date
    import datetime
    __date__ = datetime.datetime.now().strftime("%Y-%m-%d")

def get_update_info():
    """Get detailed update information."""
    return {
        'current_version': __version__,
        'version_info': VERSION,
        'status': __status__,
        'build_date': __date__,
        'author': __author__,
        'organization': __organization__,
        'license': __license__,
        'requires': __requires__,
        'codename': get_codename(),
        'is_development': is_development(),
        'changelog': __changelog__,
        'description': __description__
    }

def format_version():
    """Format version string with additional info."""
    return f"{__version__} ({get_codename()})"
