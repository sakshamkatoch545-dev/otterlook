"""
Authentication Utilities for Otterlook AI.
Provides PBKDF2 password hashing and RFC 6238 TOTP (Google Authenticator)
2-step verification using only Python's standard library.
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote


def hash_password(password: str) -> str:
    """Hash password with a random 16-byte salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$digest string in constant time."""
    try:
        salt_b64, dk_b64 = stored_hash.split("$", 1)
        salt = base64.b64decode(salt_b64)
        expected_dk = base64.b64decode(dk_b64)
        actual_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(actual_dk, expected_dk)
    except Exception:
        return False


def generate_totp_secret() -> str:
    """Generate a 160-bit Base32 secret compatible with Google Authenticator."""
    raw = secrets.token_bytes(20)
    return base64.b32encode(raw).decode("ascii").rstrip("=")


def build_otpauth_uri(email: str, secret: str, issuer: str = "Otterlook AI") -> str:
    """Build standard otpauth:// URI for Google Authenticator QR codes."""
    label = quote(f"{issuer}:{email}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"


def _totp_at(secret: str, counter: int) -> str:
    padded = secret.strip().upper()
    padded += "=" * ((8 - len(padded) % 8) % 8)
    key = base64.b32decode(padded, casefold=True)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{code_int % 1_000_000:06d}"


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """Verify a 6-digit Google Authenticator TOTP code within +/- window steps."""
    clean = (code or "").strip()
    if len(clean) != 6 or not clean.isdigit() or not secret:
        return False
    step = int(time.time()) // 30
    for offset in range(-window, window + 1):
        try:
            if hmac.compare_digest(_totp_at(secret, step + offset), clean):
                return True
        except Exception:
            return False
    return False
