#!/usr/bin/env python3
"""
Code signing script for Remote Control executables.

Uses signtool to digitally sign the compiled executables with the Tuxxle certificate.
Requires:
- signtool.exe (Windows SDK)
- Valid certificate file and password
"""

import subprocess
import sys
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"
SIGNTOOL_PATH = Path(r"X:\firma\signtool.exe")
CERT_PATH = Path(r"X:\Certificati\tuxxle.pfx")
CERT_PASSWORD = "CERT_PASSWORD_HERE"
TIMESTAMP_URL = "http://timestamp.digicert.com"

# Executables to sign
EXECUTABLES = [
    DIST_DIR / "RemoteControlServer.exe",
    DIST_DIR / "RemoteControlClient.exe",
]

def sign_file(file_path: Path) -> bool:
    """Sign a single file using signtool."""
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False

    cmd = [
        str(SIGNTOOL_PATH),
        "sign",
        "/fd", "sha256",
        "/td", "SHA256",
        "/f", str(CERT_PATH),
        "/p", CERT_PASSWORD,
        "/tr", TIMESTAMP_URL,
        str(file_path)
    ]

    print(f"Signing: {file_path.name}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Successfully signed: {file_path.name}")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR signing {file_path.name}:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"ERROR: signtool not found at {SIGNTOOL_PATH}")
        print("Please ensure Windows SDK is installed and signtool is accessible.")
        return False

def main() -> int:
    """Sign all configured executables."""
    print("=== Remote Control Code Signing ===")
    print(f"Using signtool: {SIGNTOOL_PATH}")
    print(f"Certificate: {CERT_PATH}")
    print(f"Distribution directory: {DIST_DIR}")
    print()

    if not SIGNTOOL_PATH.exists():
        print(f"ERROR: signtool not found at {SIGNTOOL_PATH}")
        return 1

    if not CERT_PATH.exists():
        print(f"ERROR: Certificate file not found at {CERT_PATH}")
        return 1

    success_count = 0
    for exe in EXECUTABLES:
        if sign_file(exe):
            success_count += 1
        print()

    total = len(EXECUTABLES)
    print(f"=== Signing Complete: {success_count}/{total} files signed ===")
    return 0 if success_count == total else 1

if __name__ == "__main__":
    sys.exit(main())
