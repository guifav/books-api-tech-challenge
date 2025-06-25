#!/usr/bin/env python3
"""
Aplicação principal da Books API
Tech Challenge - Fase 1 - Machine Learning Engineering
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa a aplicação Flask
from api.routes import app

if __name__ == '__main__':
    # Configurações da aplicação
    port = int(os.environ.get('PORT', 5005))
    host = os.environ.get('API_HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando Books API...")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📖 Documentação: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/api/docs")
    
    # Inicia a aplicação
    app.run(host=host, port=port, debug=debug)