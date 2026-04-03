"""
Vercel serverless entry point.
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

app = Flask(__name__)

init_error = None
init_traceback = None

try:
    from app.app_new import create_app
    from app.errors import register_error_handlers
    from app.logging_config import init_sentry, log_info, log_error
    
    app = create_app()
    init_sentry(app)
    
    log_info("Application initialized successfully")
    
except Exception as e:
    init_error = str(e)
    init_traceback = traceback.format_exc()
    
    print(f"INITIALIZATION ERROR: {init_error}", file=sys.stderr)
    print(f"TRACEBACK:\n{init_traceback}", file=sys.stderr)
    
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        is_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
        response = {
            "error": "Application initialization failed",
            "details": init_error,
        }
        if is_debug:
            response["traceback"] = init_traceback
            response["hint"] = "Check Vercel environment variables: NTC_SECRET_KEY is required"
        return jsonify(response), 500
