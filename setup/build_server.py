#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path

# Configuration
APP_NAME = "RemoteControlServer"
COMPANY = "Tuxxle"
AUTHOR = "Nsfr750"
DESCRIPTION = "Remote Control Server Application"
COPYRIGHT = f"© 2024-2026 {AUTHOR} - All rights reserved"

# Directories
BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SERVER_ENTRY = BASE_DIR / "server" / "server.py"
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
        "--jobs=4",
        f"--output-filename=RemoteControlServer.exe",
        "--windows-console-mode=disable",
        f"--windows-icon-from-ico={BASE_DIR / 'assets' / 'icon.ico'}",
        "--follow-imports", "--enable-plugin=pyqt6",
        f"--windows-company-name={COMPANY}",
        f"--windows-product-name={APP_NAME}",
        f"--windows-product-version={VERSION}",
        f"--windows-file-version={VERSION}",
        f"--windows-file-description={DESCRIPTION}",
        "--windows-uac-admin",
        # Include data directories
        "--include-data-dir=assets=assets",
        # Include data files with proper target filenames
        "--include-data-files=README.md=README.md",
        "--include-data-files=LICENSE=LICENSE.txt",
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
        str(SERVER_ENTRY)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    success = build()
    print("Build successful!" if success else "Build failed!")