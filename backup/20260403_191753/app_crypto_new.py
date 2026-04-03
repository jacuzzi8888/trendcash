"""
Encryption utilities for sensitive data.
Uses Fernet symmetric encryption with proper key derivation.
"""

import os
import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


_fernet_instance: Optional[Fernet] = None


def _derive_key(secret: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a secret."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


def get_encryption_key() -> bytes:
    """Get or derive the encryption key."""
    secret = os.environ.get("NTC_ENCRYPTION_KEY") or os.environ.get("NTC_SECRET_KEY")
    if not secret:
        raise RuntimeError("NTC_ENCRYPTION_KEY or NTC_SECRET_KEY must be set")
    
    if len(secret) < 32:
        secret = secret.ljust(32, '_')
    
    salt = b"ntc_encryption_v2"
    return _derive_key(secret, salt)


def get_fernet() -> Fernet:
    """Get or create Fernet instance."""
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(get_encryption_key())
    return _fernet_instance


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string value."""
    if not plaintext:
        return ""
    
    f = get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a string value."""
    if not ciphertext:
        return ""
    
    f = get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ""


def mask_value(value: str, show_chars: int = 4) -> str:
    """Mask a value for display, showing only first N characters."""
    if not value:
        return ""
    if len(value) <= show_chars:
        return "*" * len(value)
    return value[:show_chars] + "*" * (len(value) - show_chars)


def hash_value(value: str, salt: str = "") -> str:
    """Create a one-way hash of a value."""
    combined = f"{salt}{value}"
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_hash(value: str, hashed: str, salt: str = "") -> bool:
    """Verify a value against a hash."""
    return hash_value(value, salt) == hashed


class EncryptedField:
    """Descriptor for encrypted database fields."""
    
    def __init__(self, field_name: str):
        self.field_name = field_name
        self._encrypted_name = f"_encrypted_{field_name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        encrypted = getattr(obj, self._encrypted_name, None)
        if encrypted:
            return decrypt_value(encrypted)
        return None
    
    def __set__(self, obj, value):
        if value:
            setattr(obj, self._encrypted_name, encrypt_value(value))
        else:
            setattr(obj, self._encrypted_name, None)
