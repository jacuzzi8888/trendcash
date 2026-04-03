"""
Security module with rate limiting, CSRF protection, input validation, and headers.
Uses Redis for distributed rate limiting when available.
"""

import os
import re
import html
import time
import hashlib
import secrets
from functools import wraps
from typing import Optional, Tuple
from flask import request, jsonify, g, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from .logging_config import log_security_event, log_warning, log_error


csrf = CSRFProtect()

REDIS_URL = os.environ.get("REDIS_URL", "")

if REDIS_URL:
    try:
        import redis
        _redis_client = redis.from_url(REDIS_URL)
        STORAGE_URI = REDIS_URL
    except Exception:
        STORAGE_URI = "memory://"
        _redis_client = None
else:
    STORAGE_URI = "memory://"
    _redis_client = None


def _get_rate_limit_key():
    from flask_login import current_user
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    return f"ip:{get_remote_address()}"


limiter = Limiter(
    key_func=_get_rate_limit_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=STORAGE_URI,
    strategy="fixed-window" if STORAGE_URI.startswith("redis") else "memory",
)


def get_secure_cookie_settings() -> dict:
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
    
    nonce = secrets.token_hex(16)
    response.headers["X-Request-ID"] = nonce
    
    return response


class InputValidator:
    """Centralized input validation."""
    
    MAX_STRING_LENGTH = 2000
    MAX_URL_LENGTH = 2048
    MAX_TEXT_LENGTH = 50000
    
    ALLOWED_CATEGORIES = {
        'betting', 'crypto', 'finance', 'education', 'politics', 
        'sports', 'entertainment', 'travel', 'jobs', 'general'
    }
    
    @staticmethod
    def sanitize(value: str, max_length: int = None) -> str:
        if not value:
            return ""
        
        if not isinstance(value, str):
            value = str(value)
        
        value = html.escape(value.strip())
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        if max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_id(value, name: str = "ID") -> int:
        try:
            val = int(value)
            if val <= 0:
                raise ValueError(f"{name} must be positive")
            return val
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid {name}: {str(e)}")
    
    @staticmethod
    def validate_category(value: str, allow_custom: bool = True) -> str:
        if not value:
            raise ValueError("Category is required")
        
        value = value.strip().lower()[:50]
        
        if not re.match(r'^[\w\s\-]+$', value):
            raise ValueError("Category contains invalid characters")
        
        return value
    
    @staticmethod
    def validate_url(value: str, require_https: bool = True) -> str:
        if not value:
            raise ValueError("URL is required")
        
        value = value.strip()
        
        if len(value) > InputValidator.MAX_URL_LENGTH:
            raise ValueError(f"URL exceeds maximum length of {InputValidator.MAX_URL_LENGTH}")
        
        if require_https and not value.lower().startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(value):
            raise ValueError("Invalid URL format")
        
        return value
    
    @staticmethod
    def validate_score(value, min_val: float = 0.0, max_val: float = 1.0, name: str = "Score") -> float:
        try:
            val = float(value)
            if not (min_val <= val <= max_val):
                raise ValueError(f"{name} must be between {min_val} and {max_val}")
            return val
        except (TypeError, ValueError):
            raise ValueError(f"Invalid {name}")
    
    @staticmethod
    def validate_username(value: str) -> str:
        if not value:
            raise ValueError("Username is required")
        
        value = value.strip().lower()
        
        if len(value) < 3 or len(value) > 50:
            raise ValueError("Username must be 3-50 characters")
        
        if not re.match(r'^[\w\-]+$', value):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        
        return value
    
    @staticmethod
    def validate_password(value: str) -> str:
        if not value:
            raise ValueError("Password is required")
        
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        if len(value) > 128:
            raise ValueError("Password is too long")
        
        return value
    
    @staticmethod
    def validate_email(value: str) -> str:
        if not value:
            raise ValueError("Email is required")
        
        value = value.strip().lower()
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not email_pattern.match(value):
            raise ValueError("Invalid email format")
        
        return value


validator = InputValidator()

sanitize_input = InputValidator.sanitize
validate_id = InputValidator.validate_id
validate_category = InputValidator.validate_category
validate_url = InputValidator.validate_url
validate_score = InputValidator.validate_score


class RateLimitExceeded(Exception):
    """Custom exception for rate limit exceeded."""
    pass


def check_rate_limit(identifier: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
    """Check rate limit using Redis or in-memory storage."""
    key = f"ratelimit:{identifier}"
    current_time = int(time.time())
    
    if _redis_client:
        try:
            count = _redis_client.get(key)
            if count is None:
                _redis_client.setex(key, window_seconds, 1)
                return True, max_requests - 1
            
            count = int(count)
            if count >= max_requests:
                ttl = _redis_client.ttl(key)
                return False, ttl if ttl > 0 else window_seconds
            
            _redis_client.incr(key)
            return True, max_requests - count - 1
        except Exception as e:
            log_error("Rate limit check failed", exception=e)
            return True, max_requests
    
    return True, max_requests


def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            abort(401)
        
        if current_user.role != 'admin':
            log_security_event(
                "unauthorized_access_attempt",
                f"User {current_user.username} attempted to access admin endpoint",
                user_id=current_user.id
            )
            abort(403)
        
        return f(*args, **kwargs)
    return wrapped


def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token."""
    if not token:
        return False
    
    stored_token = session.get('_csrf_token')
    if not stored_token:
        return False
    
    return secrets.compare_digest(token, stored_token)


def log_request():
    """Log request details for audit trail."""
    from flask_login import current_user
    
    log_security_event(
        "request",
        f"{request.method} {request.path}",
        user_id=current_user.id if current_user.is_authenticated else None,
        ip_address=request.remote_addr,
    )
