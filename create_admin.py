"""
Script to create an admin user for the Remote Control Server.
"""
import sys
import json
import time
from pathlib import Path
from getpass import getpass
from common.security import SecurityManager

def create_admin_user(username: str, password: str) -> None:
    """Create an admin user with the given credentials."""
    users_file = Path('users.json')
    users = {}
    
    # Load existing users if the file exists
    if users_file.exists():
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
        except Exception as e:
            print(f"Error loading users file: {e}")
            sys.exit(1)
    
    # Check if user already exists
    if username in users:
        print(f"User '{username}' already exists. Updating password...")
    
    # Create security manager and hash password
    security = SecurityManager()
    hashed_password = security.hash_password(password)
    
    # Verify the password can be verified
    if not security.verify_password(hashed_password, password):
        print("Error: Password hashing/verification failed!")
        sys.exit(1)
    
    # Add/update user
    users[username] = {
        'password': hashed_password,
        'is_admin': True,
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'last_login': None
    }
    
    # Save users
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"User '{username}' created/updated successfully!")
        print(f"Password hash: {hashed_password}")
    except Exception as e:
        print(f"Error saving users file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("Create Admin User")
    print("================")
    
    # Get username and password
    username = input("Enter username [admin]: ") or "admin"
    password = getpass("Enter password: ")
    confirm = getpass("Confirm password: ")
    
    if password != confirm:
        print("Error: Passwords do not match!")
        sys.exit(1)
    
    if not password:
        print("Error: Password cannot be empty!")
        sys.exit(1)
    
    create_admin_user(username, password)
