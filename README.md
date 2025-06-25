# Books API - Tech Challenge Fase 1

## 📖 Descrição do Projeto

API pública para consulta de livros desenvolvida como parte do Tech Challenge da Fase 1 de Machine Learning Engineering. O sistema realiza web scraping do site [books.toscrape.com](https://books.toscrape.com) e disponibiliza os dados através de uma API RESTful completa com documentação Swagger.

## 🏗️ Arquitetura

```
[Web Scraping] → [Dados CSV] → [API RESTful] → [Consumidores ML]
     ↓              ↓              ↓              ↓
  books.toscrape   Armazenamento   Flask/RestX    Cientistas
     .com          Local/CSV       + Swagger      de Dados
```

### Componentes Principais

- **Web Scraping**: Sistema automatizado para extração de dados de livros
- **Armazenamento**: Dados estruturados em formato CSV
- **API RESTful**: Interface Flask com documentação Swagger automática
- **Documentação**: Swagger UI integrada para teste e documentação

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd solution
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente** (opcional)
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

### Executando o Web Scraping

```bash
# Execute o scraping para coletar dados
python run_scraper.py
```

Este comando irá:
- Extrair todos os livros do site books.toscrape.com
- Salvar os dados em `data/books_data.csv`
- Exibir estatísticas do processo

### Iniciando a API

```bash
# Inicia o servidor de desenvolvimento
python app.py
```

A API estará disponível em:
- **Base URL**: http://localhost:5005
- **Documentação Swagger**: http://localhost:5005/api/docs

### Iniciando o Dashboard Streamlit

```bash
# Em um novo terminal
make dashboard
```

O dashboard estará disponível em: **http://localhost:8501**

## 📚 Documentação da API

### Endpoints Obrigatórios

#### 📖 Livros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/books` | Lista todos os livros disponíveis |
| GET | `/api/v1/books/{id}` | Detalhes de um livro específico |
| GET | `/api/v1/books/search` | Busca livros por título e/ou categoria |
| GET | `/api/v1/books/top-rated` | Livros com melhor avaliação |
| GET | `/api/v1/books/price-range` | Livros por faixa de preço |

#### 🏷️ Categorias

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/categories` | Lista todas as categorias disponíveis |

#### 📊 Estatísticas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/stats/overview` | Estatísticas gerais da coleção |
| GET | `/api/v1/stats/categories` | Estatísticas detalhadas por categoria |

#### 🏥 Health Check

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/health` | Verifica status da API |

#### 🔐 Autenticação (Desafio Bônus 1)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Obter token JWT |
| POST | `/api/v1/auth/refresh` | Renovar token JWT |
| GET | `/api/v1/auth/verify` | Verificar token válido |
| GET | `/api/v1/auth/users` | Listar usuários (admin) |

#### 🤖 Machine Learning (Desafio Bônus 2)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/ml/features` | Dados formatados para ML |
| GET | `/api/v1/ml/training-data` | Dataset para treinamento |
| POST | `/api/v1/ml/train` | Treinar modelo |
| POST | `/api/v1/ml/predictions` | Fazer predições |
| GET | `/api/v1/ml/model-info` | Informações do modelo |

#### 🕷️ Controle de Scraping (Protegido)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/scraping/trigger` | Iniciar scraping (admin) |
| GET | `/api/v1/scraping/status` | Status do scraping |
| GET | `/api/v1/scraping/data-info` | Info dos dados coletados |

### Exemplos de Uso

#### 1. Listar todos os livros
```bash
curl -X GET "http://localhost:5005/api/v1/books"
```

**Resposta:**
```json
[
  {
    "id": 1,
    "title": "A Light in the Attic",
    "price": 51.77,
    "rating": 3,
    "availability": "In stock",
    "category": "Poetry",
    "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
    "book_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
  }
]
```

#### 2. Buscar livro por ID
```bash
curl -X GET "http://localhost:5005/api/v1/books/1"
```

#### 3. Buscar livros por título
```bash
curl -X GET "http://localhost:5005/api/v1/books/search?title=light"
```

#### 4. Buscar livros por categoria
```bash
curl -X GET "http://localhost:5005/api/v1/books/search?category=fiction"
```

#### 5. Buscar livros por faixa de preço
```bash
curl -X GET "http://localhost:5005/api/v1/books/price-range?min=10&max=30"
```

#### 6. Obter estatísticas gerais
```bash
curl -X GET "http://localhost:5005/api/v1/stats/overview"
```

**Resposta:**
```json
{
  "total_books": 1000,
  "average_price": 35.24,
  "min_price": 10.00,
  "max_price": 59.99,
  "rating_distribution": {
    "1": 50,
    "2": 100,
    "3": 200,
    "4": 350,
    "5": 300
  },
  "total_categories": 50
}
```

#### 7. Verificar status da API
```bash
curl -X GET "http://localhost:5005/api/v1/health"
```

#### 8. Autenticação - Obter token JWT
```bash
curl -X POST "http://localhost:5005/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "scientist", "password": "science123"}'
```

**Resposta:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "username": "scientist",
    "role": "data_scientist",
    "permissions": ["read", "ml"]
  }
}
```

#### 9. ML - Obter features para treinamento
```bash
curl -X GET "http://localhost:5005/api/v1/ml/features" \
  -H "Authorization: Bearer <seu-token-jwt>"
```

#### 10. ML - Treinar modelo
```bash
curl -X POST "http://localhost:5005/api/v1/ml/train" \
  -H "Authorization: Bearer <seu-token-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"target": "rating"}'
```

#### 11. ML - Fazer predições
```bash
curl -X POST "http://localhost:5005/api/v1/ml/predictions" \
  -H "Authorization: Bearer <seu-token-jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "title": "New Book",
        "price": 29.99,
        "rating": 4,
        "category": "Fiction",
        "availability": "In stock"
      }
    ]
  }'
```

### Parâmetros de Consulta

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `title` | string | Busca por título (case-insensitive) | `?title=python` |
| `category` | string | Busca por categoria (case-insensitive) | `?category=fiction` |
| `min` | float | Preço mínimo | `?min=10.00` |
| `max` | float | Preço máximo | `?max=50.00` |

## 🗂️ Estrutura do Projeto

```
solution/
├── api/                    # Módulo da API
│   ├── __init__.py        # Inicialização do módulo
│   ├── models.py          # Modelos de dados e repositório
│   └── routes.py          # Rotas e endpoints da API
├── scripts/               # Scripts de automação
│   └── scraper.py         # Web scraper principal
├── data/                  # Dados coletados
│   └── books_data.csv     # Dados dos livros (gerado)
├── docs/                  # Documentação adicional
├── tests/                 # Testes automatizados
├── app.py                 # Aplicação principal
├── run_scraper.py         # Script para executar scraping
├── requirements.txt       # Dependências Python
├── .env.example           # Exemplo de variáveis de ambiente
├── README.md              # Este arquivo
└── vercel.json            # Configuração para deploy Vercel
```

## 🔧 Configuração para Produção

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
FLASK_ENV=production
FLASK_DEBUG=False
API_HOST=0.0.0.0
API_PORT=5000
```

### Deploy no Vercel

1. **Instale o Vercel CLI**
```bash
npm install -g vercel
```

2. **Configure o projeto**
```bash
vercel
```

3. **Deploy**
```bash
vercel --prod
```

## 🧪 Executando Testes

```bash
# Execute os testes
python -m pytest tests/

# Com cobertura
python -m pytest tests/ --cov=api
```

## 📊 Campos de Dados

Os dados coletados incluem os seguintes campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | Identificador único do livro |
| `title` | string | Título do livro |
| `price` | float | Preço em libras (£) |
| `rating` | int | Avaliação de 1 a 5 estrelas |
| `availability` | string | Status de disponibilidade |
| `category` | string | Categoria do livro |
| `image_url` | string | URL da imagem do livro |
| `book_url` | string | URL da página do livro |

## 🚀 Uso para Machine Learning

### Endpoints ML-Ready

A API foi projetada pensando no consumo por modelos de Machine Learning:

- **Features estruturadas**: Dados limpos e padronizados
- **Busca flexível**: Filtros por múltiplos critérios
- **Estatísticas**: Insights para análise exploratória
- **Formato JSON**: Fácil integração com bibliotecas ML

### Exemplo de Integração Python

```python
import requests
import pandas as pd

# Carregar dados para ML
response = requests.get('http://localhost:5005/api/v1/books')
books_data = response.json()

# Converter para DataFrame
df = pd.DataFrame(books_data)

# Usar para treinamento de modelo
features = df[['price', 'rating', 'category']]
```

## 📊 Dashboard Streamlit

### Funcionalidades do Dashboard

O dashboard interativo oferece:

- **📈 Visualizações**: Gráficos de distribuição de preços, ratings e categorias
- **🔍 Busca Interativa**: Filtros por título, categoria e faixa de preço
- **📊 Métricas em Tempo Real**: Estatísticas atualizadas da API
- **📋 Tabelas Dinâmicas**: Visualização e filtração dos dados
- **⚡ Status da API**: Monitoramento da conectividade

### Como Acessar

1. **Certifique-se que a API está rodando**:
   ```bash
   make run  # Terminal 1
   ```

2. **Inicie o dashboard**:
   ```bash
   make dashboard  # Terminal 2
   ```

3. **Acesse no navegador**: http://localhost:8501

### Script Automático

Para facilitar, use o script que verifica a API automaticamente:

```bash
./start_dashboard.sh
```

### Gráficos Disponíveis

- **📊 Distribuição de Preços**: Histograma dos preços dos livros
- **⭐ Distribuição de Ratings**: Gráfico de barras dos ratings
- **🏷️ Top Categorias**: Categorias com mais livros
- **💰⭐ Preço vs Rating**: Análise de correlação
- **🔍 Busca Dinâmica**: Filtros interativos em tempo real

## 🔐 Sistema de Autenticação JWT (Desafio Bônus 1)

### Usuários Disponíveis

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | admin | read, write, admin |
| `scientist` | `science123` | data_scientist | read, ml |
| `user` | `user123` | user | read |

### Como Usar Autenticação

1. **Fazer Login**:
   ```bash
   curl -X POST "http://localhost:5005/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "scientist", "password": "science123"}'
   ```

2. **Usar o Token** em requisições subsequentes:
   ```bash
   curl -X GET "http://localhost:5005/api/v1/ml/features" \
     -H "Authorization: Bearer <token-recebido>"
   ```

3. **Renovar Token**:
   ```bash
   curl -X POST "http://localhost:5005/api/v1/auth/refresh" \
     -H "Content-Type: application/json" \
     -d '{"token": "<token-atual>"}'
   ```

### Rotas Protegidas

- **Admin**: `/api/v1/scraping/trigger`, `/api/v1/auth/users`
- **ML Permission**: Todos os endpoints `/api/v1/ml/*`
- **Token Required**: `/api/v1/scraping/status`, `/api/v1/auth/verify`

## 🤖 Pipeline ML-Ready (Desafio Bônus 2)

### Funcionalidades ML

1. **Preparação de Features**:
   - Engenharia de features automática
   - Normalização de dados
   - Encoding de variáveis categóricas
   - Estatísticas descritivas

2. **Dataset para Treinamento**:
   - Split automático train/test
   - Dados normalizados
   - Target configurável

3. **Modelo de Exemplo**:
   - Random Forest Regressor
   - Predição de ratings
   - Feature importance
   - Métricas de performance

### Workflow ML Completo

```bash
# 1. Login para obter token
TOKEN=$(curl -s -X POST "http://localhost:5005/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "scientist", "password": "science123"}' | \
  jq -r '.token')

# 2. Verificar dados disponíveis
curl -X GET "http://localhost:5005/api/v1/ml/model-info" \
  -H "Authorization: Bearer $TOKEN"

# 3. Obter features preparadas
curl -X GET "http://localhost:5005/api/v1/ml/features" \
  -H "Authorization: Bearer $TOKEN"

# 4. Obter dataset de treinamento
curl -X GET "http://localhost:5005/api/v1/ml/training-data?target=rating" \
  -H "Authorization: Bearer $TOKEN"

# 5. Treinar modelo
curl -X POST "http://localhost:5005/api/v1/ml/train" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target": "rating"}'

# 6. Fazer predições
curl -X POST "http://localhost:5005/api/v1/ml/predictions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "title": "Machine Learning Book",
        "price": 35.99,
        "rating": 4,
        "category": "Technology", 
        "availability": "In stock"
      }
    ]
  }'
```

### Features Engenhadas Automaticamente

- **Numéricas**: price, rating
- **Categóricas**: category_encoded, availability_encoded  
- **Derivadas**: title_length, title_word_count, price_per_rating
- **Flags**: is_expensive, is_high_rated

## 🔍 Monitoramento

### Logs

A aplicação gera logs estruturados para:
- Requisições HTTP
- Operações de scraping
- Erros e exceções

### Métricas

- Total de livros na base
- Tempo de resposta da API
- Uso por endpoint
- Estatísticas de dados

## 🛠️ Desenvolvimento

### Adicionando Novos Endpoints

1. **Defina o modelo** em `api/models.py`
2. **Adicione a rota** em `api/routes.py`
3. **Documente** com decoradores Flask-RESTX
4. **Teste** o endpoint

### Extensões Futuras

- **Autenticação JWT**: Sistema de login e tokens
- **Cache Redis**: Melhoria de performance
- **Base de dados**: PostgreSQL para produção
- **Monitoramento**: Grafana + Prometheus
- **Pipeline ML**: Endpoints para predições

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:

1. Verifique a [documentação Swagger](http://localhost:5000/api/docs)
2. Consulte os logs da aplicação
3. Abra uma issue no repositório

---

**Tech Challenge - Fase 1 - Machine Learning Engineering**  
*Desenvolvido como parte do programa de especialização ALURA*