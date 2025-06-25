#!/usr/bin/env python3
"""
Script para executar o web scraping
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Tenta usar o scraper simplificado primeiro, depois o original
try:
    from scripts.simple_scraper import main
    print("🕷️  Usando scraper simplificado (mais confiável)")
except ImportError:
    from scripts.scraper import main
    print("🕷️  Usando scraper original")

if __name__ == "__main__":
    main()