"""
Screen capture and control module.

This module provides platform-specific implementations for screen capture
and control functionality. It automatically selects the appropriate
implementation based on the current operating system.
"""
import platform

# Import the appropriate screen controller based on the platform
if platform.system() == 'Windows':
    from .windows import WindowsScreenController as ScreenController
else:
    from .linux import LinuxScreenController as ScreenController

__all__ = ['ScreenController']
