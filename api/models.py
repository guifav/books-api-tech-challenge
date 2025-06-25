"""
Modelos de dados para a API
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import pandas as pd
import os

@dataclass
class Book:
    """Modelo de dados para um livro"""
    id: int
    title: str
    price: float
    rating: int
    availability: str
    category: str
    image_url: str
    book_url: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o livro para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'rating': self.rating,
            'availability': self.availability,
            'category': self.category,
            'image_url': self.image_url,
            'book_url': self.book_url
        }

class BookRepository:
    """Repositório para gerenciar dados dos livros"""
    
    def __init__(self, csv_file_path: str = None):
        if csv_file_path is None:
            csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'books_data.csv')
        
        self.csv_file_path = csv_file_path
        self._books = []
        self.load_books()
    
    def load_books(self):
        """Carrega livros do arquivo CSV"""
        try:
            if os.path.exists(self.csv_file_path):
                df = pd.read_csv(self.csv_file_path)
                self._books = []
                
                for _, row in df.iterrows():
                    book = Book(
                        id=int(row['id']),
                        title=str(row['title']),
                        price=float(row['price']),
                        rating=int(row['rating']),
                        availability=str(row['availability']),
                        category=str(row['category']),
                        image_url=str(row['image_url']),
                        book_url=str(row['book_url'])
                    )
                    self._books.append(book)
            else:
                # Se não existe arquivo, cria dados de exemplo
                self._create_sample_data()
                
        except Exception as e:
            print(f"Erro ao carregar livros: {e}")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Cria dados de exemplo se não houver arquivo CSV"""
        sample_books = [
            Book(1, "Sample Book 1", 19.99, 4, "In stock", "Fiction", 
                 "https://example.com/img1.jpg", "https://example.com/book1"),
            Book(2, "Sample Book 2", 25.50, 5, "In stock", "Science", 
                 "https://example.com/img2.jpg", "https://example.com/book2"),
            Book(3, "Sample Book 3", 15.75, 3, "Out of stock", "History", 
                 "https://example.com/img3.jpg", "https://example.com/book3")
        ]
        self._books = sample_books
    
    def get_all_books(self) -> List[Book]:
        """Retorna todos os livros"""
        return self._books
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Retorna um livro pelo ID"""
        for book in self._books:
            if book.id == book_id:
                return book
        return None
    
    def search_books(self, title: str = None, category: str = None) -> List[Book]:
        """Busca livros por título e/ou categoria"""
        results = self._books
        
        if title:
            title_lower = title.lower()
            results = [book for book in results if title_lower in book.title.lower()]
        
        if category:
            category_lower = category.lower()
            results = [book for book in results if category_lower in book.category.lower()]
        
        return results
    
    def get_all_categories(self) -> List[str]:
        """Retorna todas as categorias únicas"""
        categories = list(set(book.category for book in self._books))
        return sorted(categories)
    
    def get_books_by_price_range(self, min_price: float = None, max_price: float = None) -> List[Book]:
        """Retorna livros dentro de uma faixa de preço"""
        results = self._books
        
        if min_price is not None:
            results = [book for book in results if book.price >= min_price]
        
        if max_price is not None:
            results = [book for book in results if book.price <= max_price]
        
        return results
    
    def get_top_rated_books(self, limit: int = 10) -> List[Book]:
        """Retorna os livros com melhor avaliação"""
        sorted_books = sorted(self._books, key=lambda x: x.rating, reverse=True)
        return sorted_books[:limit]
    
    def get_stats_overview(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais da coleção"""
        if not self._books:
            return {
                'total_books': 0,
                'average_price': 0,
                'rating_distribution': {},
                'total_categories': 0
            }
        
        prices = [book.price for book in self._books]
        ratings = [book.rating for book in self._books]
        
        # Distribuição de ratings
        rating_dist = {}
        for rating in ratings:
            rating_dist[rating] = rating_dist.get(rating, 0) + 1
        
        return {
            'total_books': len(self._books),
            'average_price': sum(prices) / len(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'rating_distribution': rating_dist,
            'total_categories': len(self.get_all_categories())
        }
    
    def get_stats_by_categories(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas por categoria"""
        categories_stats = {}
        
        for category in self.get_all_categories():
            category_books = [book for book in self._books if book.category == category]
            if category_books:
                prices = [book.price for book in category_books]
                ratings = [book.rating for book in category_books]
                
                categories_stats[category] = {
                    'total_books': len(category_books),
                    'average_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'average_rating': sum(ratings) / len(ratings)
                }
        
        return categories_stats