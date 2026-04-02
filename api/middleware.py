from flask import request, jsonify
from functools import wraps
import time

# ─────────────────────────────────────────
# 🚦 RATE LIMIT MIDDLEWARE (GLOBAL)
# ─────────────────────────────────────────
class RateLimitMiddleware:
    def __init__(self, app, max_requests=100, window=60):
        self.app = app
        self.max_requests = max_requests
        self.window = window
        self.requests = {}

    def __call__(self, environ, start_response):
        ip = environ.get('REMOTE_ADDR', 'unknown')
        now = time.time()

        if ip not in self.requests:
            self.requests[ip] = []

        # Remove old requests
        self.requests[ip] = [
            t for t in self.requests[ip]
            if now - t < self.window
        ]

        if len(self.requests[ip]) >= self.max_requests:
            start_response(
                '429 Too Many Requests',
                [('Content-Type', 'application/json')]
            )
            return [b'{"error": "Rate limit exceeded"}']

        self.requests[ip].append(now)

        return self.app(environ, start_response)


# ─────────────────────────────────────────
# 🎯 DECORATOR RATE LIMIT (OPTIONAL)
# ─────────────────────────────────────────
def rate_limit(max_requests: int = 100, window: int = 60):
    def decorator(f):
        calls = {}

        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()

            if client_ip not in calls:
                calls[client_ip] = []

            calls[client_ip] = [
                t for t in calls[client_ip]
                if now - t < window
            ]

            if len(calls[client_ip]) >= max_requests:
                return jsonify({'error': 'Too many requests'}), 429

            calls[client_ip].append(now)

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# ─────────────────────────────────────────
# 📦 JSON VALIDATION
# ─────────────────────────────────────────
def validate_json(schema=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'JSON required'}), 400

            # Optional schema validation (future)
            return f(*args, **kwargs)

        return decorated_function
    return decorator


# ─────────────────────────────────────────
# ⚙ INIT
# ─────────────────────────────────────────
def init_app(app):
    app.wsgi_app = RateLimitMiddleware(app.wsgi_app)
