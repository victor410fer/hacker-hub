"""
Vercel Python Entry Point
DO NOT MODIFY - This is the Vercel serverless function handler
"""

import sys
import os

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app from the root app.py
from app import app

# Vercel automatically looks for a WSGI application named 'app'
# No additional code needed
