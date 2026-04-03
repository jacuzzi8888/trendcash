"""
Structured logging and error tracking module.
Supports Sentry integration and JSON logging for production.
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from functools import wraps

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
IS_PRODUCTION = os.environ.get("VERCEL") == "1" or os.environ.get("FLASK_ENV") == "production"


class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info[0] else None,
            }
        
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data
        
        return json.dumps(log_entry)


class ConsoleFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s [DEBUG] %(name)s: %(message)s" + reset,
        logging.INFO: "%(asctime)s [INFO] %(name)s: %(message)s",
        logging.WARNING: yellow + "%(asctime)s [WARN] %(name)s: %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s [ERROR] %(name)s: %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s [CRITICAL] %(name)s: %(message)s" + reset,
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging():
    logger = logging.getLogger("ntc")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        
        if IS_PRODUCTION:
            handler.setFormatter(StructuredFormatter())
        else:
            handler.setFormatter(ConsoleFormatter())
        
        logger.addHandler(handler)
    
    return logger


def init_sentry(app=None):
    if not SENTRY_AVAILABLE or not SENTRY_DSN:
        return False
    
    integrations = []
    if app:
        integrations.append(FlaskIntegration())
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment="production" if IS_PRODUCTION else "development",
        traces_sample_rate=0.1,
        integrations=integrations,
    )
    return True


logger = setup_logging()


class LogContext:
    _context: Dict[str, Any] = {}
    
    @classmethod
    def set(cls, key: str, value: Any):
        cls._context[key] = value
    
    @classmethod
    def get(cls, key: str = None) -> Any:
        if key:
            return cls._context.get(key)
        return cls._context.copy()
    
    @classmethod
    def clear(cls):
        cls._context = {}
    
    @classmethod
    def bind(cls, **kwargs):
        cls._context.update(kwargs)


def log_info(message: str, **kwargs):
    extra = {"extra_data": {**LogContext.get(), **kwargs}} if kwargs or LogContext.get() else {}
    logger.info(message, extra=extra)


def log_error(message: str, exception: Exception = None, **kwargs):
    extra = {"extra_data": {**LogContext.get(), **kwargs}} if kwargs or LogContext.get() else {}
    if exception:
        logger.error(message, exc_info=exception, extra=extra)
        if SENTRY_AVAILABLE and SENTRY_DSN:
            sentry_sdk.capture_exception(exception)
    else:
        logger.error(message, extra=extra)


def log_warning(message: str, **kwargs):
    extra = {"extra_data": {**LogContext.get(), **kwargs}} if kwargs or LogContext.get() else {}
    logger.warning(message, extra=extra)


def log_debug(message: str, **kwargs):
    extra = {"extra_data": {**LogContext.get(), **kwargs}} if kwargs or LogContext.get() else {}
    logger.debug(message, extra=extra)


def log_security_event(event_type: str, details: str = "", user_id: str = None, ip_address: str = None):
    log_info(
        f"Security event: {event_type}",
        event_type=event_type,
        details=details,
        user_id=user_id,
        ip_address=ip_address,
    )
    
    if SENTRY_AVAILABLE and SENTRY_DSN:
        sentry_sdk.add_breadcrumb(
            category="security",
            message=f"{event_type}: {details}",
            level="info",
        )


def audit_log(action: str):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                from flask_login import current_user
                from flask import request
                
                LogContext.bind(
                    action=action,
                    endpoint=request.endpoint,
                    method=request.method,
                    user_id=current_user.id if current_user.is_authenticated else None,
                    ip=request.remote_addr,
                )
            except Exception:
                pass
            
            try:
                result = f(*args, **kwargs)
                log_info(f"Audit: {action} completed")
                return result
            except Exception as e:
                log_error(f"Audit: {action} failed", exception=e)
                raise
            finally:
                LogContext.clear()
        return wrapped
    return decorator
