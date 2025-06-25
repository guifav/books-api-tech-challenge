"""
Testes para a API de livros
"""

import unittest
import json
from api.routes import app
from api.models import BookRepository

class TestBooksAPI(unittest.TestCase):
    """Testes para os endpoints da API"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_endpoint(self):
        """Testa endpoint raiz"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
    
    def test_health_check(self):
        """Testa endpoint de health check"""
        response = self.app.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('total_books_loaded', data)
    
    def test_list_books(self):
        """Testa listagem de livros"""
        response = self.app.get('/api/v1/books')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        
        if data:  # Se há livros na base
            book = data[0]
            required_fields = ['id', 'title', 'price', 'rating', 'availability', 'category']
            for field in required_fields:
                self.assertIn(field, book)
    
    def test_get_book_by_id(self):
        """Testa busca de livro por ID"""
        # Primeiro, pega a lista de livros para ter um ID válido
        response = self.app.get('/api/v1/books')
        books = json.loads(response.data)
        
        if books:
            book_id = books[0]['id']
            response = self.app.get(f'/api/v1/books/{book_id}')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['id'], book_id)
    
    def test_get_nonexistent_book(self):
        """Testa busca de livro que não existe"""
        response = self.app.get('/api/v1/books/99999')
        self.assertEqual(response.status_code, 404)
    
    def test_search_books(self):
        """Testa busca de livros"""
        response = self.app.get('/api/v1/books/search?title=sample')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_categories(self):
        """Testa listagem de categorias"""
        response = self.app.get('/api/v1/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('categories', data)
        self.assertIsInstance(data['categories'], list)
    
    def test_stats_overview(self):
        """Testa estatísticas gerais"""
        response = self.app.get('/api/v1/stats/overview')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        required_stats = ['total_books', 'average_price', 'total_categories']
        for stat in required_stats:
            self.assertIn(stat, data)
    
    def test_stats_categories(self):
        """Testa estatísticas por categoria"""
        response = self.app.get('/api/v1/stats/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
    
    def test_top_rated_books(self):
        """Testa busca de livros mais bem avaliados"""
        response = self.app.get('/api/v1/books/top-rated')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_price_range_filter(self):
        """Testa filtro por faixa de preço"""
        response = self.app.get('/api/v1/books/price-range?min=10&max=30')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)


class TestBookRepository(unittest.TestCase):
    """Testes para o repositório de livros"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.repo = BookRepository()
    
    def test_get_all_books(self):
        """Testa busca de todos os livros"""
        books = self.repo.get_all_books()
        self.assertIsInstance(books, list)
        self.assertGreater(len(books), 0)
    
    def test_get_book_by_id(self):
        """Testa busca por ID"""
        books = self.repo.get_all_books()
        if books:
            book_id = books[0].id
            book = self.repo.get_book_by_id(book_id)
            self.assertIsNotNone(book)
            self.assertEqual(book.id, book_id)
    
    def test_search_books(self):
        """Testa busca de livros"""
        results = self.repo.search_books(title="sample")
        self.assertIsInstance(results, list)
    
    def test_get_categories(self):
        """Testa busca de categorias"""
        categories = self.repo.get_all_categories()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
    
    def test_stats_overview(self):
        """Testa estatísticas gerais"""
        stats = self.repo.get_stats_overview()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_books', stats)
        self.assertIn('average_price', stats)


if __name__ == '__main__':
    unittest.main()