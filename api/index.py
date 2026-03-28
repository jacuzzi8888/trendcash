import sys
import os
import traceback
from flask import Flask

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

try:
    from app.app import create_app
    app = create_app()
except Exception as e:
    error_msg = traceback.format_exc()
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return f"<pre>{error_msg}</pre>", 500
