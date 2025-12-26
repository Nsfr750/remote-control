"""
Screen capture and control module.

This module provides platform-specific implementations for screen capture
and control functionality. It automatically selects the appropriate
implementation based on the current operating system.
"""
import os
import sys

# Ensure system platform module is available
if 'platform' in sys.modules:
    del sys.modules['platform']
import platform as sys_platform

# Import the appropriate screen controller based on the platform
if os.name == 'nt':  # Windows
    from .windows import WindowsScreenController as ScreenController
else:  # Linux and others
    from .linux import LinuxScreenController as ScreenController

__all__ = ['ScreenController']
