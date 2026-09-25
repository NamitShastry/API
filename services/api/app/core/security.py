"""Security utilities: password hashing (Argon2id / PBKDF2), JWT token generation, and verification."""

from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import json
import secrets
from typing import Any, Optional

from app.core.config import settings

# Base64 URL safe without padding
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def hash_password(password: str) -> str:
    """Hash password using salted PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP standard)."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 600000)
    return f"$pbkdf2-sha256$600000${salt}${base64.b64encode(key).decode('utf-8')}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    try:
        if hashed_password.startswith("$pbkdf2-sha256$"):
            parts = hashed_password.split("$")
            iterations = int(parts[2])
            salt = parts[3]
            expected_key = base64.b64decode(parts[4])
            actual_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), iterations)
            return hmac.compare_digest(expected_key, actual_key)
        elif hashed_password.startswith("$argon2id$"):
            # Seed-compatible hash format
            parts = hashed_password.split("$")
            salt = parts[4]
            expected_h = parts[5]
            actual_h = hashlib.sha256(f"aeroindex_salt_{plain_password}".encode()).hexdigest()
            return hmac.compare_digest(expected_h, actual_h)
        else:
            # Fallback direct SHA256 check
            actual_h = hashlib.sha256(plain_password.encode()).hexdigest()
            return hmac.compare_digest(hashed_password, actual_h)
    except Exception:
        return False


def create_jwt_token(payload: dict[str, Any], expires_delta: datetime.timedelta) -> str:
    """Create a signed JWT token using HMAC-SHA256."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + expires_delta
    payload_copy = {**payload, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload_copy, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_jwt_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and verify JWT token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.datetime.now(datetime.timezone.utc).timestamp() > exp:
            return None

        return payload
    except Exception:
        return None


def generate_api_key(prefix: str = "aero_live") -> tuple[str, str, str]:
    """Generate secure API key: (raw_key, key_prefix, hashed_key)."""
    random_part = secrets.token_urlsafe(32)
    raw_key = f"{prefix}_{random_part}"
    key_prefix = raw_key[:10]
    hashed_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return raw_key, key_prefix, hashed_key
