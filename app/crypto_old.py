import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_encryption_key():
    secret = os.environ.get("NTC_ENCRYPTION_KEY") or os.environ.get("NTC_SECRET_KEY")
    if not secret:
        raise RuntimeError("NTC_ENCRYPTION_KEY or NTC_SECRET_KEY must be set")
    salt = b"ntc_salt_v1"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    return key


_fernet_cache = None


def get_fernet():
    global _fernet_cache
    if _fernet_cache is None:
        _fernet_cache = Fernet(get_encryption_key())
    return _fernet_cache


def encrypt_value(plaintext: str) -> str:
    if not plaintext:
        return ""
    f = get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    f = get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ""


def mask_value(value: str, show_chars: int = 4) -> str:
    if not value or len(value) <= show_chars:
        return "****" if value else ""
    return value[:show_chars] + "*" * (len(value) - show_chars)
