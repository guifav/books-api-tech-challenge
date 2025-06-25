"""
Web scraper para extrair dados de livros do site books.toscrape.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import List, Dict, Optional
import os
from urllib.parse import urljoin, urlparse
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BookScraper:
    """Classe para fazer scraping de livros do books.toscrape.com"""
    
    def __init__(self, base_url: str = "https://books.toscrape.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.books_data = []
        
    def get_rating_number(self, rating_class: str) -> int:
        """Converte classe CSS de rating para número"""
        rating_map = {
            'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
        }
        for word in rating_class.split():
            if word in rating_map:
                return rating_map[word]
        return 0
    
    def clean_price(self, price_str: str) -> float:
        """Limpa string de preço e converte para float"""
        # Remove símbolos de moeda e espaços
        price_clean = re.sub(r'[£$€]', '', price_str).strip()
        try:
            return float(price_clean)
        except ValueError:
            return 0.0
    
    def extract_book_data(self, book_element) -> Dict:
        """Extrai dados de um elemento de livro"""
        try:
            # Título
            title_element = book_element.find('h3').find('a')
            title = title_element.get('title', title_element.text.strip())
            
            # Preço
            price_element = book_element.find('p', class_='price_color')
            price = self.clean_price(price_element.text) if price_element else 0.0
            
            # Rating
            rating_element = book_element.find('p', class_='star-rating')
            rating = self.get_rating_number(rating_element.get('class', [])[1]) if rating_element else 0
            
            # Disponibilidade
            availability_element = book_element.find('p', class_='instock availability')
            availability = availability_element.text.strip() if availability_element else 'Out of stock'
            
            # URL da imagem
            img_element = book_element.find('div', class_='image_container').find('img')
            image_url = urljoin(self.base_url, img_element.get('src', '')) if img_element else ''
            
            # URL do livro para obter categoria - corrigir caminho
            book_href = title_element.get('href', '')
            if book_href.startswith('../../../'):
                book_href = book_href.replace('../../../', 'catalogue/')
            book_url = urljoin(self.base_url, book_href)
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'image_url': image_url,
                'book_url': book_url
            }
        except Exception as e:
            logger.error(f"Erro ao extrair dados do livro: {e}")
            return None
    
    def get_book_category(self, book_url: str) -> str:
        """Obtém a categoria de um livro específico"""
        try:
            response = self.session.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Categoria está no breadcrumb
            breadcrumb = soup.find('ul', class_='breadcrumb')
            if breadcrumb:
                links = breadcrumb.find_all('a')
                if len(links) >= 3:  # Home > Books > Category
                    return links[2].text.strip()
            
            return 'Unknown'
        except Exception as e:
            logger.error(f"Erro ao obter categoria do livro {book_url}: {e}")
            return 'Unknown'
    
    def scrape_page(self, url: str) -> List[Dict]:
        """Faz scraping de uma página de livros"""
        try:
            logger.info(f"Fazendo scraping da página: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            books = soup.find_all('article', class_='product_pod')
            
            page_books = []
            for i, book in enumerate(books):
                book_data = self.extract_book_data(book)
                if book_data:
                    # Tenta obter categoria apenas para alguns livros para otimizar
                    if i < 5:  # Apenas para os primeiros 5 livros
                        book_data['category'] = self.get_book_category(book_data['book_url'])
                    else:
                        book_data['category'] = 'Books'  # Categoria padrão
                    page_books.append(book_data)
                    
                # Pequena pausa para não sobrecarregar o servidor
                time.sleep(0.05)
            
            return page_books
            
        except Exception as e:
            logger.error(f"Erro ao fazer scraping da página {url}: {e}")
            return []
    
    def get_next_page_url(self, soup) -> Optional[str]:
        """Obtém URL da próxima página"""
        next_link = soup.find('li', class_='next')
        if next_link:
            next_url = next_link.find('a').get('href')
            return urljoin(self.base_url, next_url)
        return None
    
    def scrape_all_books(self) -> List[Dict]:
        """Faz scraping de todos os livros do site"""
        logger.info("Iniciando scraping de todos os livros...")
        
        current_url = f"{self.base_url}/index.html"
        page_count = 1
        
        while current_url:
            logger.info(f"Processando página {page_count}")
            
            try:
                response = self.session.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Scraping da página atual
                page_books = self.scrape_page(current_url)
                self.books_data.extend(page_books)
                
                logger.info(f"Coletados {len(page_books)} livros da página {page_count}")
                
                # Verifica se há próxima página
                current_url = self.get_next_page_url(soup)
                page_count += 1
                
                # Pausa entre páginas
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao processar página {page_count}: {e}")
                break
        
        logger.info(f"Scraping concluído! Total de livros coletados: {len(self.books_data)}")
        return self.books_data
    
    def save_to_csv(self, filename: str = None) -> str:
        """Salva os dados coletados em arquivo CSV"""
        if not filename:
            filename = os.path.join('data', 'books_data.csv')
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.books_data:
            logger.warning("Nenhum dado para salvar")
            return filename
        
        df = pd.DataFrame(self.books_data)
        
        # Adiciona ID único para cada livro
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
    scraper = BookScraper()
    
    try:
        # Faz scraping de todos os livros
        books = scraper.scrape_all_books()
        
        if books:
            # Salva em CSV
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