import os
import re
import html
from functools import wraps
from flask import request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def get_secure_cookie_settings():
    is_production = os.environ.get("VERCEL") == "1" or os.environ.get("FLASK_ENV") == "production"
    return {
        "SESSION_COOKIE_SECURE": is_production,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "REMEMBER_COOKIE_SECURE": is_production,
        "REMEMBER_COOKIE_HTTPONLY": True,
        "REMEMBER_COOKIE_SAMESITE": "Lax",
    }


def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://fonts.googleapis.com https://cdn.tiny.cloud; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = csp
    return response


def sanitize_input(value: str, max_length: int = None) -> str:
    if not value:
        return ""
    value = html.escape(value.strip())
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    if max_length:
        value = value[:max_length]
    return value


def validate_id(value, name="ID"):
    try:
        val = int(value)
        if val <= 0:
            raise ValueError()
        return val
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {name}")


def validate_category(value: str) -> str:
    if not value or len(value) > 50:
        raise ValueError("Invalid category")
    if not re.match(r'^[\w\s\-]+$', value):
        raise ValueError("Category contains invalid characters")
    return value.strip()


def validate_url(value: str) -> str:
    if not value:
        raise ValueError("URL is required")
    if len(value) > 2048:
        raise ValueError("URL too long")
    if not re.match(r'^https?://', value, re.IGNORECASE):
        raise ValueError("URL must start with http:// or https://")
    return value.strip()


def validate_score(value, min_val=0.0, max_val=1.0, name="Score"):
    try:
        val = float(value)
        if not (min_val <= val <= max_val):
            raise ValueError()
        return val
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {name} (must be between {min_val} and {max_val})")


def log_security_event(event_type: str, details: str = "", user_id: str = None):
    from datetime import datetime, timezone
    from .db import get_db
    
    try:
        conn = get_db()
        now = datetime.now(timezone.utc).isoformat()
        ip = get_remote_address()
        conn.execute(
            "INSERT INTO security_logs (event_type, user_id, ip_address, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (event_type, user_id, ip, details, now),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def audit_log(action: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            result = f(*args, **kwargs)
            try:
                from flask_login import current_user
                user_id = current_user.id if current_user.is_authenticated else None
                log_security_event(action, f"Endpoint: {request.endpoint}", user_id)
            except Exception:
                pass
            return result
        return wrapped
    return decorator
