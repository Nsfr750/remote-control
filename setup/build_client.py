#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path

# Configuration
APP_NAME = "RemoteControlClient"
COMPANY = "Tuxxle"
AUTHOR = "Nsfr750"
DESCRIPTION = "Remote Control Client Application"
COPYRIGHT = f"© 2024-2026 {AUTHOR} - All rights reserved"

# Directories
BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
CLIENT_ENTRY = BASE_DIR / "client" / "client.py"
ASSETS_DIR = BASE_DIR / "assets"
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 1
VERSION_QUALIFIER = ""
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}{VERSION_QUALIFIER}"


def clean_dirs():
    for d in [BASE_DIR / "build", DIST_DIR]:
        if d.exists():
            import shutil
            shutil.rmtree(d)

def build():
    clean_dirs()
    cmd = [
        sys.executable, "-m", "nuitka",
        f"--output-dir={DIST_DIR}",
        "--onefile", "--standalone",
        f"--output-filename=RemoteControlClient.exe",
        "--windows-console-mode=disable",
        f"--windows-icon-from-ico={BASE_DIR / 'assets' / 'icon.ico'}",
        "--follow-imports", "--enable-plugin=pyqt6",
        f"--windows-company-name={COMPANY}",
        "--windows-product-name=RemoteControlClient",
        f"--windows-product-version={VERSION}",
        f"--windows-file-version={VERSION}",
        f"--windows-file-description={DESCRIPTION}",
        "--windows-uac-admin",
        "--nofollow-import-to=PyQt6.QtNetwork",
        "--nofollow-import-to=PyQt6.QtWebEngine",
        "--nofollow-import-to=PyQt6.QtWebEngineWidgets",
        "--nofollow-import-to=ssl",
        # Include data files with proper target filenames
        "--include-data-files=README.md=README.md",
        "--include-data-files=LICENSE=LICENSE",
        "--include-data-files=CHANGELOG.md=CHANGELOG.md",
        # Additional metadata
        f"--company-name={COMPANY}",
        f"--product-name={APP_NAME}",
        f"--product-version={VERSION}",
        f"--file-version={VERSION}",
        f"--output-filename={APP_NAME}",
        f"--file-description={DESCRIPTION}",
        f"--copyright={COPYRIGHT}",
        f"--windows-product-version={VERSION}",
        f"--windows-file-version={VERSION}",
        f"--windows-file-description={DESCRIPTION}",
        "--remove-output",
        "--assume-yes-for-downloads",
        f"--output-dir={DIST_DIR}",
        "--mingw64",
        str(CLIENT_ENTRY)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    success = build()
    print("Build successful!" if success else "Build failed!")
    