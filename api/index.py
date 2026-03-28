import sys
import os

# Add the parent directory to the python path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import create_app

app = create_app()

def handler(request, context):
    return app(request, context)
