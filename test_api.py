#!/usr/bin/env python3
"""
Script Python para testar a API de forma interativa
"""

import requests
import json
from pprint import pprint

class APITester:
    def __init__(self, base_url="http://localhost:5005"):
        self.base_url = base_url
        
    def test_endpoint(self, endpoint, description):
        """Testa um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        print(f"\n🔍 {description}")
        print(f"📍 URL: {url}")
        print("-" * 50)
        
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                if isinstance(data, list) and len(data) > 3:
                    print("📄 Resposta (primeiros 3 itens):")
                    pprint(data[:3])
                    print(f"... e mais {len(data) - 3} itens")
                else:
                    print("📄 Resposta:")
                    pprint(data)
            else:
                print("📄 Resposta (texto):")
                print(response.text[:200])
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro: API não está rodando. Execute 'make run' primeiro.")
        except requests.exceptions.Timeout:
            print("⏰ Erro: Timeout na requisição")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 TESTANDO BOOKS API")
        print("=" * 60)
        
        tests = [
            ("/", "Página inicial da API"),
            ("/api/v1/health", "Health Check - Status da API"),
            ("/api/v1/books", "Lista todos os livros"),
            ("/api/v1/books/1", "Detalhes do livro ID 1"),
            ("/api/v1/books/search?title=book", "Busca livros por título"),
            ("/api/v1/books/search?category=fiction", "Busca livros por categoria"),
            ("/api/v1/categories", "Lista todas as categorias"),
            ("/api/v1/stats/overview", "Estatísticas gerais"),
            ("/api/v1/stats/categories", "Estatísticas por categoria"),
            ("/api/v1/books/top-rated", "Livros mais bem avaliados"),
            ("/api/v1/books/price-range?min=15&max=40", "Livros por faixa de preço"),
        ]
        
        for endpoint, description in tests:
            self.test_endpoint(endpoint, description)
        
        print("\n" + "=" * 60)
        print("✅ Testes concluídos!")
        print("\n📚 Para ver a documentação completa:")
        print(f"   {self.base_url}/api/docs")

def interactive_test():
    """Permite testes interativos"""
    tester = APITester()
    
    while True:
        print("\n" + "=" * 40)
        print("🛠️  TESTE INTERATIVO DA API")
        print("=" * 40)
        print("1. Executar todos os testes")
        print("2. Testar endpoint específico")
        print("3. Verificar se API está rodando")
        print("4. Sair")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            tester.run_all_tests()
        elif choice == "2":
            endpoint = input("Digite o endpoint (ex: /api/v1/books): ").strip()
            description = input("Descrição do teste: ").strip()
            tester.test_endpoint(endpoint, description)
        elif choice == "3":
            tester.test_endpoint("/api/v1/health", "Verificação de conectividade")
        elif choice == "4":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        tester = APITester()
        tester.run_all_tests()