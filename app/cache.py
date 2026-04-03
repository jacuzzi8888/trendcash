"""
Caching layer with Redis support and fallback to in-memory cache.
Works in both serverless and local environments.
"""

import os
import json
import time
import hashlib
from typing import Optional, Any, Dict
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

_cache: Dict[str, tuple] = {}
_cache_ttl: Dict[str, float] = {}

REDIS_URL = os.environ.get("REDIS_URL", "")
REDIS_ENABLED = bool(REDIS_URL and REDIS_AVAILABLE)

_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None and REDIS_ENABLED:
        try:
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        except Exception:
            _redis_client = None
    return _redis_client


def _make_key(prefix: str, key: str) -> str:
    return f"ntc:{prefix}:{key}"


def cache_get(prefix: str, key: str) -> Optional[Any]:
    full_key = _make_key(prefix, key)
    
    if REDIS_ENABLED:
        client = get_redis_client()
        if client:
            try:
                value = client.get(full_key)
                if value:
                    return json.loads(value)
            except Exception:
                pass
        return None
    
    if full_key in _cache_ttl:
        if time.time() > _cache_ttl[full_key]:
            del _cache[full_key]
            del _cache_ttl[full_key]
            return None
        return _cache.get(full_key)
    return None


def cache_set(prefix: str, key: str, value: Any, ttl: int = 300) -> bool:
    full_key = _make_key(prefix, key)
    
    if REDIS_ENABLED:
        client = get_redis_client()
        if client:
            try:
                client.setex(full_key, ttl, json.dumps(value))
                return True
            except Exception:
                pass
        return False
    
    _cache[full_key] = value
    _cache_ttl[full_key] = time.time() + ttl
    return True


def cache_delete(prefix: str, key: str) -> bool:
    full_key = _make_key(prefix, key)
    
    if REDIS_ENABLED:
        client = get_redis_client()
        if client:
            try:
                client.delete(full_key)
            except Exception:
                pass
    
    if full_key in _cache:
        del _cache[full_key]
    if full_key in _cache_ttl:
        del _cache_ttl[full_key]
    return True


def cache_clear_pattern(pattern: str) -> int:
    count = 0
    
    if REDIS_ENABLED:
        client = get_redis_client()
        if client:
            try:
                keys = client.keys(f"ntc:{pattern}*")
                if keys:
                    count = client.delete(*keys)
            except Exception:
                pass
    else:
        keys_to_delete = [k for k in _cache.keys() if k.startswith(f"ntc:{pattern}")]
        for k in keys_to_delete:
            del _cache[k]
            if k in _cache_ttl:
                del _cache_ttl[k]
            count += 1
    
    return count


def cached(prefix: str, ttl: int = 300, key_func: callable = None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_parts = [str(arg) for arg in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            result = cache_get(prefix, cache_key)
            if result is not None:
                return result
            
            result = f(*args, **kwargs)
            cache_set(prefix, cache_key, result, ttl)
            return result
        return wrapped
    return decorator


class SettingsCache:
    PREFIX = "settings"
    TTL = 60
    
    @classmethod
    def get(cls, key: str) -> Optional[str]:
        return cache_get(cls.PREFIX, key)
    
    @classmethod
    def set(cls, key: str, value: str) -> bool:
        return cache_set(cls.PREFIX, key, value, cls.TTL)
    
    @classmethod
    def delete(cls, key: str) -> bool:
        return cache_delete(cls.PREFIX, key)
    
    @classmethod
    def clear_all(cls) -> int:
        return cache_clear_pattern(cls.PREFIX)


class UserCache:
    PREFIX = "user"
    TTL = 300
    
    @classmethod
    def get(cls, user_id: str) -> Optional[dict]:
        return cache_get(cls.PREFIX, user_id)
    
    @classmethod
    def set(cls, user_id: str, user_data: dict) -> bool:
        return cache_set(cls.PREFIX, user_id, user_data, cls.TTL)
    
    @classmethod
    def delete(cls, user_id: str) -> bool:
        return cache_delete(cls.PREFIX, user_id)
    
    @classmethod
    def clear_all(cls) -> int:
        return cache_clear_pattern(cls.PREFIX)
