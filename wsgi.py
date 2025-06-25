#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to the Python path
project_home = '/var/www/books-api'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load production environment variables
load_dotenv('.env.production')

# Import the Flask application
from api.routes import app as application

if __name__ == "__main__":
    application.run()