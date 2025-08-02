"""
Rotas para controle de scraping (protegidas por autenticação)
"""

from flask_restx import Namespace, Resource, fields
from flask import request
# from .auth import admin_required, token_required - removido
import subprocess
import os
import threading
import time
from datetime import datetime

# Namespace para scraping
scraping_ns = Namespace('api/v1/scraping', description='Controle de web scraping')

# Status global do scraping
scraping_status = {
    'is_running': False,
    'last_run': None,
    'last_result': None,
    'total_books_scraped': 0
}

def run_scraping_background():
    """Executa scraping em background"""
    global scraping_status
    
    try:
        scraping_status['is_running'] = True
        scraping_status['last_run'] = datetime.now().isoformat()
        
        # Executa o script de scraping
        script_path = os.path.join(os.path.dirname(__file__), '..', 'run_scraper.py')
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode == 0:
            scraping_status['last_result'] = 'success'
            # Tenta extrair número de livros do output
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Total de livros:' in line:
                    try:
                        count = int(line.split(':')[1].strip())
                        scraping_status['total_books_scraped'] = count
                    except:
                        pass
        else:
            scraping_status['last_result'] = f'error: {result.stderr}'
            
    except subprocess.TimeoutExpired:
        scraping_status['last_result'] = 'timeout: Scraping demorou mais de 10 minutos'
    except Exception as e:
        scraping_status['last_result'] = f'error: {str(e)}'
    finally:
        scraping_status['is_running'] = False

@scraping_ns.route('/trigger')
class ScrapingTrigger(Resource):
    @scraping_ns.doc('trigger_scraping')
    # @admin_required - removido
    def post(self):
        """Inicia processo de web scraping (apenas admin)"""
        global scraping_status
        
        if scraping_status['is_running']:
            return {
                'success': False,
                'message': 'Scraping já está em execução',
                'status': scraping_status
            }, 409
        
        try:
            # Inicia scraping em background
            thread = threading.Thread(target=run_scraping_background)
            thread.daemon = True
            thread.start()
            
            return {
                'success': True,
                'message': 'Scraping iniciado em background',
                'status': 'running',
                'note': 'Use GET /api/v1/scraping/status para verificar progresso'
            }, 202
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao iniciar scraping: {str(e)}'
            }, 500

@scraping_ns.route('/status')
class ScrapingStatus(Resource):
    @scraping_ns.doc('scraping_status')
    # @token_required() - removido
    def get(self):
        """Verifica status do scraping"""
        global scraping_status
        
        return {
            'status': scraping_status,
            'data_file_exists': os.path.exists('data/books_data.csv'),
            'timestamp': datetime.now().isoformat()
        }, 200

@scraping_ns.route('/history')
class ScrapingHistory(Resource):
    @scraping_ns.doc('scraping_history')
    # @token_required() - removido
    def get(self):
        """Histórico de execuções de scraping"""
        # Em uma implementação real, isso viria de um banco de dados
        # Por ora, retornamos informações básicas
        
        history = []
        
        if scraping_status['last_run']:
            history.append({
                'timestamp': scraping_status['last_run'],
                'result': scraping_status['last_result'],
                'books_scraped': scraping_status['total_books_scraped']
            })
        
        return {
            'history': history,
            'total_executions': len(history)
        }, 200

@scraping_ns.route('/data-info')
class ScrapingDataInfo(Resource):
    @scraping_ns.doc('data_info')
    # @token_required() - removido
    def get(self):
        """Informações sobre os dados coletados"""
        try:
            import pandas as pd
            
            csv_path = 'data/books_data.csv'
            
            if not os.path.exists(csv_path):
                return {
                    'data_available': False,
                    'message': 'Arquivo de dados não encontrado. Execute scraping primeiro.'
                }, 404
            
            df = pd.read_csv(csv_path)
            
            file_stats = os.stat(csv_path)
            
            return {
                'data_available': True,
                'file_info': {
                    'path': csv_path,
                    'size_bytes': file_stats.st_size,
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                },
                'data_info': {
                    'total_books': len(df),
                    'columns': list(df.columns),
                    'categories': df['category'].nunique() if 'category' in df.columns else 0,
                    'price_range': {
                        'min': float(df['price'].min()) if 'price' in df.columns else None,
                        'max': float(df['price'].max()) if 'price' in df.columns else None,
                        'avg': float(df['price'].mean()) if 'price' in df.columns else None
                    }
                }
            }, 200
            
        except Exception as e:
            return {
                'error': f'Erro ao analisar dados: {str(e)}'
            }, 500

@scraping_ns.route('/config')
class ScrapingConfig(Resource):
    @scraping_ns.doc('scraping_config')
    # @admin_required - removido
    def get(self):
        """Configurações do scraping"""
        return {
            'scraper_type': 'SimpleBookScraper',
            'target_url': 'https://books.toscrape.com',
            'output_format': 'CSV',
            'max_pages': 50,
            'timeout_seconds': 600,
            'fields_collected': [
                'id', 'title', 'price', 'rating', 
                'availability', 'category', 'image_url', 'book_url'
            ]
        }, 200
    
    @scraping_ns.doc('update_scraping_config')
    # @admin_required - removido
    def put(self):
        """Atualiza configurações do scraping (placeholder)"""
        # Em uma implementação real, permitiria configurar parâmetros
        return {
            'message': 'Configurações atualizadas com sucesso',
            'note': 'Esta é uma implementação placeholder para demonstração'
        }, 200