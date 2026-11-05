"""
Vercel Serverless Function Entry Point for Otterlook AI.
Exports the FastAPI application instance `app`.
"""

import os
import sys

# Add project root directory to sys.path so backend packages resolve
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.main import app

