#!/usr/bin/env python3
"""
Aplicação principal da Books API
Tech Challenge - Fase 1 - Machine Learning Engineering
Optimized for Vercel serverless deployment
"""

import os

# Set production defaults for Vercel
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')
os.environ.setdefault('API_HOST', '0.0.0.0')
os.environ.setdefault('PORT', '5005')

# Importa a aplicação Flask
from api.routes import app

# For Vercel compatibility
handler = app

if __name__ == '__main__':
    # Configurações da aplicação
    port = int(os.environ.get('PORT', 5005))
    host = os.environ.get('API_HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando Books API...")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📖 Documentação: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/api/docs")
    
    # Inicia a aplicação
    app.run(host=host, port=port, debug=debug)