#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
SERVER_ENTRY = BASE_DIR / "server" / "server.py"

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
        f"--output-filename=RemoteControlServer.exe",
        "--windows-console-mode=disable",
        f"--windows-icon-from-ico={BASE_DIR / 'assets' / 'icon.ico'}",
        "--follow-imports", "--enable-plugin=pyqt6",
        "--windows-company-name=Nsfr750",
        "--windows-product-name=RemoteControlServer",
        "--windows-product-version=1.0.0",
        "--windows-file-version=1.0.0",
        "--windows-file-description=Remote Control Server Application",
        "--windows-uac-admin",
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