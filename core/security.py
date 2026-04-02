# core/security.py

import hashlib
import hmac
import time
from flask import request, abort
from functools import wraps
from cryptography.fernet import Fernet
import os


class SecurityManager:
    def __init__(self):
        self.encryption_key = None
        self.hmac_key = None

    # ───────── INIT ─────────
    def init_app(self, app):
        """Initialize security manager"""

        key_data = app.config.get('SECURITY_KEYS')

        if not key_data:
            self._generate_keys()
            app.config['SECURITY_KEYS'] = {
                'encryption': self.encryption_key,
                'hmac': self.hmac_key
            }
        else:
            self.encryption_key = key_data['encryption']
            self.hmac_key = key_data['hmac']

        app.security = self

    # ───────── KEY GEN ─────────
    def _generate_keys(self):
        self.encryption_key = Fernet.generate_key()
        self.hmac_key = os.urandom(32)

    # ───────── SIGNATURE ─────────
    def verify_signature(self, data: bytes, signature: str, timestamp: int) -> bool:
        """Verify HMAC signature with replay protection"""

        # Replay protection (5 min window)
        if abs(time.time() - timestamp) > 300:
            return False

        expected = hmac.new(
            self.hmac_key,
            data + str(timestamp).encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def sign_data(self, data: bytes, timestamp: int = None) -> tuple:
        """Sign data with HMAC"""

        if timestamp is None:
            timestamp = int(time.time())

        signature = hmac.new(
            self.hmac_key,
            data + str(timestamp).encode(),
            hashlib.sha256
        ).hexdigest()

        return signature, timestamp

    # ───────── ENCRYPTION ─────────
    def encrypt(self, data: str) -> str:
        f = Fernet(self.encryption_key)
        return f.encrypt(data.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted.encode()).decode()


# ───────── AUTH DECORATOR (FIXED) ─────────
def require_auth(f):
    """Auth decorator (Bearer token)"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, description="Missing or invalid Authorization header")

        token = auth_header.split(' ', 1)[1]

        expected = os.environ.get('C2LAB_ADMIN_TOKEN', "c2lab-default")

        if not hmac.compare_digest(token, expected):
            abort(403, description="Invalid token")

        return f(*args, **kwargs)

    return decorated_function


# ───────── GLOBAL INSTANCE ─────────
security_manager = SecurityManager()
