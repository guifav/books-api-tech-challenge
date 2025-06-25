# Makefile para Books API - Tech Challenge

.PHONY: help install scrape run test clean deploy

# Variáveis
PYTHON = python3
PIP = pip3
APP_NAME = Books API
PORT = 5005

help: ## Mostra esta mensagem de ajuda
	@echo "$(APP_NAME) - Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências
	@echo "📦 Instalando dependências..."
	$(PIP) install -r requirements.txt

scrape: ## Executa web scraping
	@echo "🕷️  Executando web scraping..."
	$(PYTHON) run_scraper.py

run: ## Inicia o servidor da API
	@echo "🚀 Iniciando $(APP_NAME) na porta $(PORT)..."
	$(PYTHON) app.py

dashboard: ## Inicia o dashboard Streamlit
	@echo "📊 Iniciando Dashboard Streamlit..."
	streamlit run dashboard.py

run-all: ## Inicia API e Dashboard em paralelo
	@echo "🚀 Iniciando API e Dashboard..."
	@echo "⚠️  Execute em terminais separados:"
	@echo "   Terminal 1: make run"
	@echo "   Terminal 2: make dashboard"

test: ## Executa testes unitários
	@echo "🧪 Executando testes unitários..."
	$(PYTHON) -m pytest tests/ -v

test-api: ## Testa endpoints da API (requer API rodando)
	@echo "🌐 Testando endpoints da API..."
	$(PYTHON) test_api.py

test-api-curl: ## Testa API usando curl
	@echo "🌐 Testando API com curl..."
	./test_api.sh

test-interactive: ## Teste interativo da API
	@echo "🛠️  Iniciando teste interativo..."
	$(PYTHON) test_api.py --interactive

test-auth-ml: ## Testa autenticação e endpoints ML
	@echo "🔐🤖 Testando autenticação e ML..."
	$(PYTHON) test_auth_ml.py

test-coverage: ## Executa testes com cobertura
	@echo "🧪 Executando testes com cobertura..."
	$(PYTHON) -m pytest tests/ --cov=api --cov-report=html

clean: ## Remove arquivos temporários
	@echo "🧹 Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage

setup: install ## Configuração inicial completa
	@echo "⚙️  Configuração inicial..."
	cp .env.example .env
	@echo "✅ Projeto configurado! Execute 'make scrape' para coletar dados e 'make run' para iniciar a API"

dev: ## Modo desenvolvimento (scraping + API)
	@echo "👨‍💻 Modo desenvolvimento..."
	$(MAKE) scrape
	$(MAKE) run

deploy: ## Deploy no Vercel
	@echo "🚀 Fazendo deploy no Vercel..."
	vercel --prod

deploy-preview: ## Deploy preview no Vercel
	@echo "🔍 Fazendo deploy preview no Vercel..."
	vercel

lint: ## Executa linting do código
	@echo "🔍 Executando linting..."
	flake8 api/ scripts/ --max-line-length=100

format: ## Formata código com black
	@echo "✨ Formatando código..."
	black api/ scripts/ tests/

check-deps: ## Verifica dependências desatualizadas
	@echo "📋 Verificando dependências..."
	$(PIP) list --outdated

docs: ## Gera documentação local
	@echo "📚 Documentação disponível em:"
	@echo "  - API Docs: http://localhost:$(PORT)/api/docs"
	@echo "  - README: $(PWD)/README.md"
	@echo "  - Arquitetura: $(PWD)/docs/ARCHITECTURE.md"

stats: ## Mostra estatísticas do projeto
	@echo "📊 Estatísticas do projeto:"
	@echo "  - Linhas de código Python:"
	@find . -name "*.py" -not -path "./venv/*" | xargs wc -l | tail -1
	@echo "  - Número de endpoints:"
	@grep -r "@ns_" api/routes.py | wc -l
	@echo "  - Arquivos de teste:"
	@find tests/ -name "test_*.py" | wc -l

# Comandos de desenvolvimento
dev-install: ## Instala dependências de desenvolvimento
	$(PIP) install pytest pytest-cov flake8 black

full-setup: dev-install setup ## Configuração completa para desenvolvimento
	@echo "🎉 Configuração completa finalizada!"

# Comandos de produção
prod-install: ## Instala apenas dependências de produção
	$(PIP) install -r requirements.txt --no-dev

health-check: ## Verifica se a API está funcionando
	@echo "🏥 Verificando saúde da API..."
	curl -f http://localhost:$(PORT)/api/v1/health || echo "❌ API não está respondendo"

# Comandos de dados
data-sample: ## Cria dados de exemplo
	@echo "📋 Criando dados de exemplo..."
	mkdir -p data
	echo "id,title,price,rating,availability,category,image_url,book_url" > data/books_data.csv
	echo "1,Sample Book,19.99,4,In stock,Fiction,http://example.com/img.jpg,http://example.com/book" >> data/books_data.csv

backup-data: ## Faz backup dos dados
	@echo "💾 Fazendo backup dos dados..."
	cp data/books_data.csv data/books_data_backup_$(shell date +%Y%m%d_%H%M%S).csv

# Comandos de monitoramento
logs: ## Mostra logs da aplicação
	@echo "📋 Logs da aplicação..."
	tail -f logs/app.log 2>/dev/null || echo "Arquivo de log não encontrado"

monitor: ## Monitora recursos da aplicação
	@echo "📊 Monitorando recursos..."
	@while true; do \
		ps aux | grep "python.*app.py" | grep -v grep || echo "API não está rodando"; \
		sleep 5; \
	done