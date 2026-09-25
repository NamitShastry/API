"""Unit tests for password hashing, JWT encoding/decoding, and API key generation."""

import datetime
import unittest
from app.core.security import (
    create_jwt_token,
    decode_jwt_token,
    generate_api_key,
    hash_password,
    verify_password,
)


class TestSecurity(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        pw = "Secret@Password2026!"
        h = hash_password(pw)
        self.assertTrue(verify_password(pw, h))
        self.assertFalse(verify_password("WrongPassword!", h))

    def test_jwt_token_lifecycle(self):
        payload = {"sub": "123", "role": "QUANT_ANALYST"}
        token = create_jwt_token(payload, expires_delta=datetime.timedelta(minutes=15))

        decoded = decode_jwt_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "123")
        self.assertEqual(decoded["role"], "QUANT_ANALYST")

    def test_jwt_tampered_token_rejection(self):
        token = create_jwt_token({"sub": "admin"}, expires_delta=datetime.timedelta(minutes=15))
        parts = token.split(".")
        tampered = f"{parts[0]}.eyJhZG1pbiI6dHJ1ZX0.{parts[2]}"  # Altered payload
        self.assertIsNone(decode_jwt_token(tampered))

    def test_jwt_expired_token_rejection(self):
        token = create_jwt_token({"sub": "expired"}, expires_delta=datetime.timedelta(seconds=-10))
        self.assertIsNone(decode_jwt_token(token))

    def test_api_key_generation(self):
        raw_key, prefix, hashed = generate_api_key()
        self.assertTrue(raw_key.startswith("aero_live_"))
        self.assertEqual(prefix, raw_key[:10])
        self.assertEqual(len(hashed), 64)


if __name__ == "__main__":
    unittest.main()
