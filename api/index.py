import sys
import os
import traceback
from flask import Flask, jsonify, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Log initialization errors to help debug
init_error = None
init_traceback = None

try:
    from app.app import create_app
    app = create_app()
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized"}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Too many requests. Please try again later."}), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        is_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
        if is_debug:
            return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
        return jsonify({"error": "An unexpected error occurred"}), 500
        
except Exception as e:
    init_error = str(e)
    init_traceback = traceback.format_exc()
    
    # Print to stderr for Vercel logs
    print(f"INITIALIZATION ERROR: {init_error}", file=sys.stderr)
    print(f"TRACEBACK:\n{init_traceback}", file=sys.stderr)
    
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        # Always show error details for debugging initialization issues
        return jsonify({
            "error": "Application initialization failed",
            "details": init_error,
            "traceback": init_traceback,
            "hint": "Check Vercel environment variables: NTC_SECRET_KEY is required"
        }), 500
