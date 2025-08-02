#!/usr/bin/env python3
"""
Aplicação principal da Books API
Tech Challenge - Fase 1 - Machine Learning Engineering
Optimized for Vercel serverless deployment
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
else:
    load_dotenv()

# Set production defaults
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

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