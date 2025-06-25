#!/usr/bin/env python3
"""
Script para testar endpoints de autenticação e ML
"""

import requests
import json
from pprint import pprint
import time

class AuthMLTester:
    def __init__(self, base_url="http://localhost:5005"):
        self.base_url = base_url
        self.token = None
        
    def login(self, username, password):
        """Faz login e obtém token JWT"""
        print(f"\n🔐 Fazendo login como {username}...")
        
        url = f"{self.base_url}/api/v1/auth/login"
        data = {"username": username, "password": password}
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                self.token = result['token']
                print("✅ Login realizado com sucesso!")
                print(f"👤 Usuário: {result['user']['username']}")
                print(f"🎭 Role: {result['user']['role']}")
                print(f"🔑 Permissões: {result['user']['permissions']}")
                return True
            else:
                print(f"❌ Erro no login: {result.get('error', 'Erro desconhecido')}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def test_protected_endpoint(self, endpoint, description, method="GET", data=None):
        """Testa um endpoint protegido"""
        print(f"\n🔍 {description}")
        print(f"📍 {method} {endpoint}")
        
        if not self.token:
            print("❌ Token não disponível. Faça login primeiro.")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        if data:
            headers["Content-Type"] = "application/json"
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                print(f"❌ Método {method} não suportado")
                return None
            
            print(f"📊 Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                
                if isinstance(result, dict) and len(str(result)) > 1000:
                    # Resume resultado se muito grande
                    if 'features' in result:
                        print(f"📄 Features shape: {result.get('shape', 'N/A')}")
                        print(f"📄 Feature names: {len(result.get('feature_names', []))} features")
                    elif 'predictions' in result:
                        print(f"📄 Predições: {len(result['predictions'])} resultados")
                    else:
                        print("📄 Resposta (resumida):")
                        for key, value in list(result.items())[:5]:
                            if isinstance(value, (str, int, float, bool)):
                                print(f"  {key}: {value}")
                else:
                    print("📄 Resposta:")
                    pprint(result)
            else:
                print("📄 Resposta (texto):")
                print(response.text[:500])
            
            return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def test_auth_flow(self):
        """Testa fluxo completo de autenticação"""
        print("=" * 60)
        print("🧪 TESTANDO SISTEMA DE AUTENTICAÇÃO")
        print("=" * 60)
        
        # Teste 1: Login como scientist
        if not self.login("scientist", "science123"):
            return
        
        # Teste 2: Verificar token
        self.test_protected_endpoint("/api/v1/auth/verify", "Verificando token válido")
        
        # Teste 3: Tentar endpoint que requer admin (deve falhar)
        self.test_protected_endpoint("/api/v1/auth/users", "Tentando listar usuários (deve falhar)")
        
        # Teste 4: Login como admin
        if self.login("admin", "admin123"):
            # Teste 5: Listar usuários (agora deve funcionar)
            self.test_protected_endpoint("/api/v1/auth/users", "Listando usuários (admin)")
    
    def test_ml_flow(self):
        """Testa fluxo completo de ML"""
        print("\n" + "=" * 60)
        print("🤖 TESTANDO PIPELINE ML-READY")
        print("=" * 60)
        
        # Login como scientist
        if not self.login("scientist", "science123"):
            return
        
        # Teste 1: Info do modelo
        self.test_protected_endpoint("/api/v1/ml/model-info", "Informações do modelo")
        
        # Teste 2: Features
        print("\n⏳ Preparando features (pode demorar)...")
        self.test_protected_endpoint("/api/v1/ml/features", "Obtendo features para ML")
        
        # Teste 3: Training data
        print("\n⏳ Preparando dados de treinamento...")
        self.test_protected_endpoint("/api/v1/ml/training-data?target=rating", "Dados de treinamento")
        
        # Teste 4: Treinar modelo
        print("\n⏳ Treinando modelo (pode demorar)...")
        training_result = self.test_protected_endpoint(
            "/api/v1/ml/train", 
            "Treinando modelo Random Forest",
            method="POST",
            data={"target": "rating"}
        )
        
        if training_result and not training_result.get('error'):
            # Teste 5: Fazer predições
            print("\n⏳ Fazendo predições...")
            prediction_data = {
                "data": [
                    {
                        "title": "Test Book ML",
                        "price": 25.99,
                        "rating": 4,
                        "category": "Technology",
                        "availability": "In stock"
                    },
                    {
                        "title": "Another Test Book",
                        "price": 15.50,
                        "rating": 3,
                        "category": "Fiction",
                        "availability": "In stock"
                    }
                ]
            }
            
            self.test_protected_endpoint(
                "/api/v1/ml/predictions",
                "Fazendo predições com modelo treinado",
                method="POST",
                data=prediction_data
            )
        else:
            print("⚠️ Não foi possível treinar o modelo, pulando teste de predições")
    
    def test_scraping_endpoints(self):
        """Testa endpoints de scraping"""
        print("\n" + "=" * 60)
        print("🕷️ TESTANDO ENDPOINTS DE SCRAPING")
        print("=" * 60)
        
        # Login como admin para ter permissão
        if not self.login("admin", "admin123"):
            return
        
        # Teste 1: Status do scraping
        self.test_protected_endpoint("/api/v1/scraping/status", "Status do scraping")
        
        # Teste 2: Info dos dados
        self.test_protected_endpoint("/api/v1/scraping/data-info", "Informações dos dados")
        
        # Teste 3: Configuração
        self.test_protected_endpoint("/api/v1/scraping/config", "Configurações do scraping")
        
        print("\n⚠️ Trigger de scraping não será testado automaticamente")
        print("   Para testar: POST /api/v1/scraping/trigger (cuidado: demora)")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES COMPLETOS DE AUTENTICAÇÃO E ML")
        print("=" * 80)
        
        # Verifica se API está rodando
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            if response.status_code != 200:
                print("❌ API não está respondendo corretamente")
                return
        except:
            print("❌ API não está rodando. Execute 'make run' primeiro.")
            return
        
        print("✅ API está rodando!")
        
        # Executa testes
        self.test_auth_flow()
        self.test_ml_flow()
        self.test_scraping_endpoints()
        
        print("\n" + "=" * 80)
        print("✅ TESTES CONCLUÍDOS!")
        print("\n📚 Para mais informações:")
        print(f"   Swagger UI: {self.base_url}/api/docs")
        print("   README.md: Documentação completa")

if __name__ == "__main__":
    tester = AuthMLTester()
    tester.run_all_tests()