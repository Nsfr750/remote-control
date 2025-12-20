"""
Security module for handling encryption, decryption, and secure communication.
"""
import os
import base64
import hashlib
import json
from typing import Tuple, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    """Handles encryption, decryption, and secure communication."""
    
    SALT_LENGTH = 16
    KEY_ITERATIONS = 100000
    
    def __init__(self, password: Optional[bytes] = None, salt: Optional[bytes] = None):
        """Initialize with optional password and salt.
        
        Args:
            password: Optional password bytes for encryption key derivation
            salt: Optional salt for key derivation. If None, a random one will be generated.
        """
        self.salt = salt or os.urandom(self.SALT_LENGTH)
        self.key = None
        self.cipher_suite = None
        
        if password is not None:
            self.derive_key(password)
    
    def derive_key(self, password: bytes) -> None:
        """Derive an encryption key from a password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.KEY_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.key = key
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using the derived key."""
        if not self.cipher_suite:
            raise ValueError("Encryption key not initialized")
        return self.cipher_suite.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using the derived key."""
        if not self.cipher_suite:
            raise ValueError("Decryption key not initialized")
        try:
            return self.cipher_suite.decrypt(encrypted_data)
        except InvalidToken:
            raise ValueError("Invalid decryption key or corrupted data")
    
    def hash_password(self, password: str) -> str:
        """Hash a password for secure storage."""
        salt = os.urandom(self.SALT_LENGTH)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            self.KEY_ITERATIONS
        )
        # Store the salt and hash together
        return f"{salt.hex()}:{pwd_hash.hex()}"
    
    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify a password against a stored hash."""
        try:
            salt_hex, stored_hash = stored_password.split(':')
            salt = bytes.fromhex(salt_hex)
            stored_hash_bytes = bytes.fromhex(stored_hash)
            
            pwd_hash = hashlib.pbkdf2_hmac(
                'sha256',
                provided_password.encode('utf-8'),
                salt,
                self.KEY_ITERATIONS
            )
            
            return pwd_hash == stored_hash_bytes
        except (ValueError, AttributeError):
            return False
    
    def get_key_material(self) -> Tuple[bytes, bytes]:
        """Get the key material for secure transmission."""
        if not self.key:
            raise ValueError("Key not initialized")
        return self.salt, self.key
    
    def encrypt_message(self, message: dict) -> bytes:
        """Encrypt a message dictionary."""
        return self.encrypt(json.dumps(message).encode('utf-8'))
    
    def decrypt_message(self, encrypted_data: bytes) -> dict:
        """Decrypt data to a message dictionary."""
        return json.loads(self.decrypt(encrypted_data).decode('utf-8'))

# Utility functions
def generate_rsa_keypair() -> Tuple[str, str]:
    """Generate an RSA key pair for secure communication.
    
    Returns:
        Tuple of (private_key, public_key) as strings
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem
