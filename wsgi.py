#!/usr/bin/env python3
"""
WSGI entry point for production deployment
Optimized for Vercel serverless deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
else:
    load_dotenv()

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

# Import the Flask application
from api.routes import app as application

# Vercel expects 'app' variable
app = application

if __name__ == "__main__":
    application.run()