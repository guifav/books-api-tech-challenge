#!/usr/bin/env python3
"""
WSGI entry point for production deployment
Optimized for Vercel serverless deployment
"""

import os
import sys

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')
os.environ.setdefault('API_HOST', '0.0.0.0')
os.environ.setdefault('PORT', '5005')

# Import the Flask application
from api.routes import app as application

# Vercel expects 'app' variable
app = application

if __name__ == "__main__":
    application.run()