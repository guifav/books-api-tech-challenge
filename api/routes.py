"""
Rotas da API REST para consulta de livros
"""

from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
from flask_cors import CORS
from .models import BookRepository
import os

# Configuração da aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração da API com Swagger
api = Api(
    app,
    version='1.0',
    title='Books API',
    description='API pública para consulta de livros extraídos via web scraping',
    doc='/api/docs'
)

# Namespace para organizar endpoints
ns_books = api.namespace('api/v1/books', description='Operações com livros')
ns_categories = api.namespace('api/v1/categories', description='Operações com categorias')
ns_stats = api.namespace('api/v1/stats', description='Estatísticas dos dados')
ns_health = api.namespace('api/v1/health', description='Status da API')

# Importa e adiciona novos namespaces
from .auth_routes import auth_ns
from .ml_routes import ml_ns
from .scraping_routes import scraping_ns

api.add_namespace(auth_ns)
api.add_namespace(ml_ns)
api.add_namespace(scraping_ns)

# Modelos para documentação Swagger
book_model = api.model('Book', {
    'id': fields.Integer(required=True, description='ID único do livro'),
    'title': fields.String(required=True, description='Título do livro'),
    'price': fields.Float(required=True, description='Preço do livro'),
    'rating': fields.Integer(required=True, description='Avaliação (1-5 estrelas)'),
    'availability': fields.String(required=True, description='Status de disponibilidade'),
    'category': fields.String(required=True, description='Categoria do livro'),
    'image_url': fields.String(required=True, description='URL da imagem do livro'),
    'book_url': fields.String(required=True, description='URL da página do livro')
})

stats_overview_model = api.model('StatsOverview', {
    'total_books': fields.Integer(description='Total de livros na base'),
    'average_price': fields.Float(description='Preço médio dos livros'),
    'min_price': fields.Float(description='Menor preço'),
    'max_price': fields.Float(description='Maior preço'),
    'rating_distribution': fields.Raw(description='Distribuição de ratings'),
    'total_categories': fields.Integer(description='Total de categorias')
})

# Inicializa o repositório
book_repo = BookRepository()

# Parser para parâmetros de busca
search_parser = reqparse.RequestParser()
search_parser.add_argument('title', type=str, help='Título do livro para busca')
search_parser.add_argument('category', type=str, help='Categoria do livro para busca')

# Parser para faixa de preço
price_parser = reqparse.RequestParser()
price_parser.add_argument('min', type=float, help='Preço mínimo')
price_parser.add_argument('max', type=float, help='Preço máximo')

# Rotas da API

@ns_books.route('')
class BooksList(Resource):
    @ns_books.marshal_list_with(book_model)
    @ns_books.doc('list_books')
    def get(self):
        """Lista todos os livros disponíveis na base de dados"""
        books = book_repo.get_all_books()
        return [book.to_dict() for book in books]

@ns_books.route('/<int:book_id>')
class BookDetail(Resource):
    @ns_books.marshal_with(book_model)
    @ns_books.doc('get_book')
    def get(self, book_id):
        """Retorna detalhes completos de um livro específico pelo ID"""
        book = book_repo.get_book_by_id(book_id)
        if book:
            return book.to_dict()
        api.abort(404, f"Livro com ID {book_id} não encontrado")

@ns_books.route('/search')
class BookSearch(Resource):
    @ns_books.expect(search_parser)
    @ns_books.marshal_list_with(book_model)
    @ns_books.doc('search_books')
    def get(self):
        """Busca livros por título e/ou categoria"""
        args = search_parser.parse_args()
        books = book_repo.search_books(title=args['title'], category=args['category'])
        return [book.to_dict() for book in books]

@ns_books.route('/top-rated')
class TopRatedBooks(Resource):
    @ns_books.marshal_list_with(book_model)
    @ns_books.doc('top_rated_books')
    def get(self):
        """Lista os livros com melhor avaliação (rating mais alto)"""
        books = book_repo.get_top_rated_books(limit=20)
        return [book.to_dict() for book in books]

@ns_books.route('/price-range')
class BooksByPriceRange(Resource):
    @ns_books.expect(price_parser)
    @ns_books.marshal_list_with(book_model)
    @ns_books.doc('books_by_price_range')
    def get(self):
        """Filtra livros dentro de uma faixa de preço específica"""
        args = price_parser.parse_args()
        books = book_repo.get_books_by_price_range(min_price=args['min'], max_price=args['max'])
        return [book.to_dict() for book in books]

@ns_categories.route('')
class CategoriesList(Resource):
    @ns_categories.doc('list_categories')
    def get(self):
        """Lista todas as categorias de livros disponíveis"""
        categories = book_repo.get_all_categories()
        return {'categories': categories}

@ns_stats.route('/overview')
class StatsOverview(Resource):
    @ns_stats.marshal_with(stats_overview_model)
    @ns_stats.doc('stats_overview')
    def get(self):
        """Estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings)"""
        return book_repo.get_stats_overview()

@ns_stats.route('/categories')
class StatsCategories(Resource):
    @ns_stats.doc('stats_categories')
    def get(self):
        """Estatísticas detalhadas por categoria (quantidade de livros, preços por categoria)"""
        return book_repo.get_stats_by_categories()

@ns_health.route('')
class HealthCheck(Resource):
    @ns_health.doc('health_check')
    def get(self):
        """Verifica status da API e conectividade com os dados"""
        try:
            total_books = len(book_repo.get_all_books())
            return {
                'status': 'healthy',
                'message': 'API está funcionando corretamente',
                'data_connection': 'ok',
                'total_books_loaded': total_books,
                'version': '1.0'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Erro na API: {str(e)}',
                'data_connection': 'error',
                'version': '1.0'
            }, 500

# Rota raiz
@app.route('/')
def home():
    """Página inicial da API"""
    return {
        'message': 'Books API - Tech Challenge Fase 1',
        'version': '1.0',
        'documentation': '/api/docs',
        'endpoints': {
            'books': '/api/v1/books',
            'categories': '/api/v1/categories',
            'stats': '/api/v1/stats',
            'health': '/api/v1/health'
        }
    }

if __name__ == '__main__':
    # Configuração para desenvolvimento
    port = int(os.environ.get('PORT', 5005))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)