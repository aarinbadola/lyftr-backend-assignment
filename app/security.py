# app/security.py
import hmac
import hashlib

def compute_signature(secret: str, body_bytes: bytes) -> str:
    """
    Compute HMAC-SHA256 hex digest for the exact raw body bytes.
    """
    return hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
