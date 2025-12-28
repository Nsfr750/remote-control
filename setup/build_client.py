#!/usr/bin/env python3
import os, sys, subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
CLIENT_ENTRY = BASE_DIR / "client" / "client.py"

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
        "--windows-company-name=Nsfr750",
        "--windows-product-name=RemoteControlClient",
        "--windows-product-version=1.0.1",
        "--windows-file-version=1.0.1",
        "--windows-file-description=Remote Control Client Application",
        "--windows-uac-admin",
        "--nofollow-import-to=PyQt6.QtNetwork",
        "--nofollow-import-to=PyQt6.QtWebEngine",
        "--nofollow-import-to=PyQt6.QtWebEngineWidgets",
        "--nofollow-import-to=ssl",
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
    