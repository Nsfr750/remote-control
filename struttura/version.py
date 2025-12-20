"""
Version information
"""

# Version as a tuple (major, minor, patch)
VERSION = (1, 0, 0)

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
__date__ = "2025-11-17"

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
## [1.0.0] - 2025-12-20
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
            "version": "1.0.0",
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
