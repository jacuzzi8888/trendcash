"""
Centralized error handling with consistent API responses.
"""

from typing import Optional, Dict, Any, Union
from flask import jsonify, Response
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """Base API error with consistent format."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result
    
    def to_response(self) -> tuple:
        return jsonify(self.to_dict()), self.status_code


class ValidationError(APIError):
    """Validation error for invalid input."""
    
    def __init__(self, message: str, field: str = None, details: dict = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(
            message=message,
            status_code=400,
            error_code="validation_error",
            details=error_details,
        )


class NotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(self, resource: str = "Resource", resource_id: str = None):
        message = f"{resource} not found"
        details = {}
        if resource_id:
            details["id"] = resource_id
        super().__init__(
            message=message,
            status_code=404,
            error_code="not_found",
            details=details,
        )


class UnauthorizedError(APIError):
    """Authentication required error."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="unauthorized",
        )


class ForbiddenError(APIError):
    """Permission denied error."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="forbidden",
        )


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    
    def __init__(self, retry_after: int = None):
        message = "Rate limit exceeded. Please try again later."
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            status_code=429,
            error_code="rate_limit_exceeded",
            details=details,
        )


class ExternalServiceError(APIError):
    """External service error."""
    
    def __init__(self, service: str, message: str = None):
        msg = message or f"External service '{service}' is unavailable"
        super().__init__(
            message=msg,
            status_code=502,
            error_code="external_service_error",
            details={"service": service},
        )


class DatabaseError(APIError):
    """Database operation error."""
    
    def __init__(self, message: str = "Database operation failed", original_error: Exception = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(
            message=message,
            status_code=500,
            error_code="database_error",
            details=details,
        )


class ConfigurationError(APIError):
    """Configuration error."""
    
    def __init__(self, message: str, setting: str = None):
        details = {}
        if setting:
            details["setting"] = setting
        super().__init__(
            message=message,
            status_code=500,
            error_code="configuration_error",
            details=details,
        )


def success_response(
    data: Any = None,
    message: str = None,
    status_code: int = 200,
) -> tuple:
    """Create a success response."""
    response = {"success": True}
    
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    
    return jsonify(response), status_code


def error_response(
    message: str,
    status_code: int = 400,
    error_code: str = "error",
    details: dict = None,
) -> tuple:
    """Create an error response."""
    return APIError(
        message=message,
        status_code=status_code,
        error_code=error_code,
        details=details,
    ).to_response()


def handle_exception(e: Exception) -> tuple:
    """Handle any exception and return appropriate response."""
    if isinstance(e, APIError):
        return e.to_response()
    
    if isinstance(e, HTTPException):
        return jsonify({
            "success": False,
            "error": {
                "code": "http_error",
                "message": e.description,
            }
        }), e.code
    
    from .logging_config import log_error
    log_error("Unhandled exception", exception=e)
    
    return jsonify({
        "success": False,
        "error": {
            "code": "internal_error",
            "message": "An unexpected error occurred",
        }
    }), 500


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(e):
        return e.to_response()
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return e.to_response()
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "not_found",
                "message": "Resource not found",
            }
        }), 404
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "unauthorized",
                "message": "Authentication required",
            }
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "forbidden",
                "message": "Permission denied",
            }
        }), 403
    
    @app.errorhandler(429)
    def handle_rate_limit(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Rate limit exceeded. Please try again later.",
            }
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
            }
        }), 500
    
    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        return handle_exception(e)
