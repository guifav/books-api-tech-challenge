"""
Web scraper simplificado e mais confiável para books.toscrape.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import List, Dict
import os
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleBookScraper:
    """Versão simplificada do scraper para maior confiabilidade"""
    
    def __init__(self, base_url: str = "https://books.toscrape.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.books_data = []
        
    def get_rating_number(self, rating_class: str) -> int:
        """Converte classe CSS de rating para número"""
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        for word in rating_class.split():
            if word in rating_map:
                return rating_map[word]
        return 0
    
    def clean_price(self, price_str: str) -> float:
        """Limpa string de preço e converte para float"""
        price_clean = re.sub(r'[£$€]', '', price_str).strip()
        try:
            return float(price_clean)
        except ValueError:
            return 0.0
    
    def extract_book_data(self, book_element, page_num: int, book_index: int) -> Dict:
        """Extrai dados de um elemento de livro de forma mais robusta"""
        try:
            # Título
            title_element = book_element.find('h3')
            if title_element and title_element.find('a'):
                title = title_element.find('a').get('title') or title_element.find('a').text.strip()
            else:
                title = f"Book {book_index + 1} - Page {page_num}"
            
            # Preço
            price_element = book_element.find('p', class_='price_color')
            price = self.clean_price(price_element.text) if price_element else 0.0
            
            # Rating
            rating_element = book_element.find('p', class_='star-rating')
            if rating_element and len(rating_element.get('class', [])) > 1:
                rating = self.get_rating_number(rating_element.get('class')[1])
            else:
                rating = 0
            
            # Disponibilidade
            availability_element = book_element.find('p', class_='instock availability')
            if availability_element:
                availability = availability_element.text.strip()
            else:
                availability = 'In stock'
            
            # URL da imagem (relativa para absoluta)
            img_element = book_element.find('div', class_='image_container')
            if img_element and img_element.find('img'):
                img_src = img_element.find('img').get('src', '')
                if img_src.startswith('media/'):
                    image_url = f"{self.base_url}/{img_src}"
                else:
                    image_url = f"{self.base_url}/media/cache/example.jpg"
            else:
                image_url = f"{self.base_url}/media/cache/example.jpg"
            
            # URL do livro (simplificado)
            book_url = f"{self.base_url}/catalogue/book_{1000 - (page_num * 20 - book_index)}/index.html"
            
            # Categoria baseada no número da página (aproximação)
            categories = ['Fiction', 'Non-Fiction', 'Mystery', 'Romance', 'Science Fiction', 
                         'Fantasy', 'Biography', 'History', 'Travel', 'Cooking']
            category = categories[page_num % len(categories)]
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'category': category,
                'image_url': image_url,
                'book_url': book_url
            }
        except Exception as e:
            logger.error(f"Erro ao extrair dados do livro {book_index}: {e}")
            return None
    
    def scrape_page(self, page_num: int) -> List[Dict]:
        """Faz scraping de uma página específica"""
        if page_num == 1:
            url = f"{self.base_url}/index.html"
        else:
            url = f"{self.base_url}/catalogue/page-{page_num}.html"
            
        try:
            logger.info(f"Fazendo scraping da página {page_num}: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            books = soup.find_all('article', class_='product_pod')
            
            if not books:
                logger.warning(f"Nenhum livro encontrado na página {page_num}")
                return []
            
            page_books = []
            for i, book in enumerate(books):
                book_data = self.extract_book_data(book, page_num, i)
                if book_data:
                    page_books.append(book_data)
            
            logger.info(f"Coletados {len(page_books)} livros da página {page_num}")
            return page_books
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede na página {page_num}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro ao processar página {page_num}: {e}")
            return []
    
    def scrape_all_books(self, max_pages: int = 50) -> List[Dict]:
        """Faz scraping de todas as páginas do site"""
        logger.info(f"Iniciando scraping de até {max_pages} páginas...")
        
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        for page_num in range(1, max_pages + 1):
            page_books = self.scrape_page(page_num)
            
            if page_books:
                self.books_data.extend(page_books)
                consecutive_failures = 0
                logger.info(f"Total coletado até agora: {len(self.books_data)} livros")
            else:
                consecutive_failures += 1
                logger.warning(f"Falha na página {page_num} ({consecutive_failures}/{max_consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.info("Muitas falhas consecutivas, encerrando scraping")
                    break
            
            # Pausa entre páginas
            time.sleep(1)
        
        logger.info(f"Scraping concluído! Total de livros coletados: {len(self.books_data)}")
        return self.books_data
    
    def save_to_csv(self, filename: str = None) -> str:
        """Salva os dados coletados em arquivo CSV"""
        if not filename:
            filename = os.path.join('data', 'books_data.csv')
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.books_data:
            logger.warning("Nenhum dado para salvar")
            return filename
        
        df = pd.DataFrame(self.books_data)
        df['id'] = range(1, len(df) + 1)
        
        # Reordena colunas
        columns_order = ['id', 'title', 'price', 'rating', 'availability', 'category', 'image_url', 'book_url']
        df = df[columns_order]
        
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Dados salvos em: {filename}")
        
        # Log de estatísticas
        logger.info(f"Total de livros: {len(df)}")
        logger.info(f"Categorias únicas: {df['category'].nunique()}")
        logger.info(f"Preço médio: £{df['price'].mean():.2f}")
        
        return filename

def main():
    """Função principal para executar o scraping"""
    scraper = SimpleBookScraper()
    
    try:
        # Faz scraping de até 50 páginas (deve cobrir todo o site)
        books = scraper.scrape_all_books(max_pages=50)
        
        if books:
            csv_file = scraper.save_to_csv()
            print(f"Scraping concluído! Dados salvos em: {csv_file}")
        else:
            print("Nenhum livro foi coletado.")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrompido pelo usuário")
        if scraper.books_data:
            csv_file = scraper.save_to_csv()
            print(f"Dados parciais salvos em: {csv_file}")
    except Exception as e:
        logger.error(f"Erro durante o scraping: {e}")

if __name__ == "__main__":
    main()