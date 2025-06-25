# Plano Arquitetural - Books API

## 📋 Visão Geral

Este documento detalha a arquitetura da Books API, um sistema completo de extração, processamento e disponibilização de dados de livros via API pública, projetada para integração com pipelines de Machine Learning.

## 🏗️ Arquitetura do Sistema

### Diagrama de Arquitetura

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐
│   Data Source   │    │    Scraper   │    │   Storage   │    │   API Layer     │
│                 │    │              │    │             │    │                 │
│ books.toscrape  │───▶│ Web Scraping │───▶│ CSV Files   │───▶│ Flask REST API  │
│     .com        │    │   (Python)   │    │  (Local)    │    │   + Swagger     │
└─────────────────┘    └──────────────┘    └─────────────┘    └─────────────────┘
                                                                        │
                                                                        ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐
│  ML Scientists  │    │   External   │    │  Front-end  │    │   Consumers     │
│                 │◀───│  Services    │◀───│ Dashboards  │◀───│                 │
│  Data Analysis  │    │   & APIs     │    │             │    │  Various Clients│
└─────────────────┘    └──────────────┘    └─────────────┘    └─────────────────┘
```

### Fluxo de Dados

1. **Ingestão**: Web scraper extrai dados do site books.toscrape.com
2. **Processamento**: Dados são limpos, estruturados e validados
3. **Armazenamento**: Informações são salvas em formato CSV
4. **Disponibilização**: API REST expõe dados via endpoints padronizados
5. **Consumo**: Cientistas de dados e aplicações consomem via HTTP

## 🔧 Componentes da Arquitetura

### 1. Camada de Ingestão (Data Ingestion)

**Responsabilidade**: Coleta automatizada de dados da fonte externa

```python
# Componente: scripts/scraper.py
class BookScraper:
    - Web scraping automatizado
    - Tratamento de erros e retries
    - Rate limiting para não sobrecarregar o servidor
    - Extração de campos estruturados
```

**Características**:
- **Robustez**: Tratamento de exceções e reconexão automática
- **Escalabilidade**: Paginação automática e processamento incremental
- **Configurabilidade**: Parâmetros ajustáveis via variáveis de ambiente

### 2. Camada de Processamento (Data Processing)

**Responsabilidade**: Limpeza, validação e estruturação dos dados

```python
# Componente: api/models.py
class BookRepository:
    - Validação de tipos de dados
    - Normalização de preços e ratings
    - Geração de IDs únicos
    - Indexação para busca eficiente
```

**Operações**:
- Limpeza de strings (remoção de caracteres especiais)
- Conversão de tipos (preços para float, ratings para int)
- Validação de URLs e disponibilidade
- Criação de índices para otimização de consultas

### 3. Camada de Armazenamento (Data Storage)

**Responsabilidade**: Persistência dos dados estruturados

```
data/
├── books_data.csv          # Dados principais dos livros
├── categories.csv          # Cache de categorias (futuro)
└── scraping_logs.csv      # Logs de execução (futuro)
```

**Características**:
- **Formato CSV**: Fácil integração com pandas e ferramentas ML
- **Estrutura Normalizada**: Campos padronizados e tipados
- **Versionamento**: Timestamps para controle de versão dos dados

### 4. Camada de API (API Layer)

**Responsabilidade**: Interface RESTful para consumo dos dados

```python
# Componente: api/routes.py
Flask + Flask-RESTX:
    - Endpoints RESTful padronizados
    - Documentação Swagger automática
    - Validação de parâmetros
    - Tratamento de erros HTTP
    - Suporte CORS para integração web
```

**Endpoints Principais**:
- `/api/v1/books` - CRUD operations
- `/api/v1/categories` - Operações com categorias
- `/api/v1/stats` - Estatísticas e insights
- `/api/v1/health` - Monitoramento

## 🚀 Escalabilidade Futura

### Fase 1: MVP Atual
```
[Scraper] → [CSV] → [Flask API] → [Consumers]
```

### Fase 2: Produção
```
[Scraper] → [PostgreSQL] → [Flask API + Cache] → [Load Balancer] → [Consumers]
                ↓                    ↓
          [Data Warehouse] → [Analytics Dashboard]
```

### Fase 3: Enterprise
```
[Multiple Sources] → [Data Pipeline] → [Data Lake] → [ML Platform] → [Applications]
        ↓                   ↓              ↓           ↓
   [Kafka Queue] → [Apache Airflow] → [MLflow] → [Model Serving]
```

## 🤖 Integração com Machine Learning

### Cenários de Uso para ML

#### 1. Sistema de Recomendação
```python
# Exemplo de consumo para recomendação
import requests
import pandas as pd

# Obter dados para treinamento
response = requests.get('http://api/v1/books')
books_df = pd.DataFrame(response.json())

# Features para modelo de recomendação
features = books_df[['price', 'rating', 'category']]
target = books_df['rating']

# Treinar modelo de recomendação
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
model.fit(features, target)
```

#### 2. Análise de Preços
```python
# Endpoint específico para análise de preços
response = requests.get('http://api/v1/stats/categories')
price_analysis = response.json()

# Usar para modelo de precificação dinâmica
```

#### 3. Classificação de Categorias
```python
# Dados limpos para NLP
books_data = requests.get('http://api/v1/books').json()
texts = [book['title'] for book in books_data]
categories = [book['category'] for book in books_data]

# Treinar classificador de texto
```

### Pipeline ML Proposto

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Books API  │───▶│ Feature Eng.│───▶│ ML Training │───▶│ Model Serve │
│   (Source)  │    │  Pipeline   │    │  Pipeline   │    │  (Predict)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                   │                  │
                           ▼                   ▼                  ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │  Processed  │    │   Trained   │    │ Predictions │
                   │  Features   │    │   Models    │    │ & Insights  │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

## 🛡️ Segurança e Confiabilidade

### Medidas de Segurança Implementadas

1. **Rate Limiting**: Controle de frequência de scraping
2. **Input Validation**: Validação de parâmetros da API
3. **Error Handling**: Tratamento robusto de exceções
4. **CORS Policy**: Controle de origem das requisições

### Medidas Futuras

1. **Autenticação JWT**: Sistema de tokens para controle de acesso
2. **HTTPS Obrigatório**: Criptografia de dados em trânsito
3. **API Throttling**: Limitação de requests por usuário
4. **Audit Logs**: Registro de todas as operações

## 📊 Monitoramento e Observabilidade

### Métricas Chave

1. **Performance**:
   - Tempo de resposta por endpoint
   - Throughput de requests/segundo
   - Taxa de erro HTTP

2. **Data Quality**:
   - Completude dos dados coletados
   - Taxa de sucesso do scraping
   - Freshness dos dados

3. **Business**:
   - Endpoints mais utilizados
   - Padrões de consumo
   - Crescimento da base de dados

### Stack de Monitoramento Proposta

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │───▶│ Prometheus  │───▶│  Grafana    │
│    Logs     │    │  (Metrics)  │    │ (Dashboard) │
└─────────────┘    └─────────────┘    └─────────────┘
        │                   │                  │
        ▼                   ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    ELK      │    │   Alert     │    │   Reports   │
│   Stack     │    │  Manager    │    │ Automated   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔄 Estratégia de Deploy e CI/CD

### Deploy Atual (MVP)
- **Plataforma**: Vercel (Serverless)
- **Processo**: Deploy manual via CLI
- **Ambiente**: Produção única

### Deploy Futuro (Produção)
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   GitHub    │───▶│   CI/CD     │───▶│   Testing   │───▶│  Deploy     │
│  (Source)   │    │ (Actions)   │    │ (Automated) │    │ (Automated) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
        │                   │                  │                  │
        ▼                   ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    PR       │    │   Build     │    │   QA Env    │    │   Prod Env  │
│  Reviews    │    │   Docker    │    │  (Staging)  │    │  (Live)     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 💡 Melhorias e Extensões Planejadas

### Curto Prazo (1-3 meses)
1. **Cache Redis**: Melhoria de performance
2. **PostgreSQL**: Migração do CSV para banco relacional
3. **Autenticação**: Sistema de API keys
4. **Documentação**: Postman collection

### Médio Prazo (3-6 meses)
1. **ML Endpoints**: Integração com modelos treinados
2. **Real-time Updates**: WebSocket para dados em tempo real
3. **Advanced Analytics**: Dashboard interativo
4. **Multi-source**: Scraping de múltiplos sites

### Longo Prazo (6+ meses)
1. **Microservices**: Arquitetura distribuída
2. **Event Streaming**: Apache Kafka para eventos
3. **ML Platform**: MLOps completo integrado
4. **Global CDN**: Distribuição mundial da API

## 🎯 KPIs e Métricas de Sucesso

### Técnicas
- **Uptime**: > 99.9%
- **Response Time**: < 200ms (P95)
- **Data Freshness**: < 24h
- **Error Rate**: < 0.1%

### Negócio
- **API Adoption**: Crescimento mensal de usuários
- **Data Quality**: > 95% completude
- **ML Integration**: Número de modelos integrados
- **Community**: Contribuições open source

## 📚 Tecnologias e Justificativas

### Escolhas Tecnológicas

| Tecnologia | Justificativa |
|------------|---------------|
| **Python** | Ecossistema ML, bibliotecas robustas |
| **Flask** | Simplicidade, flexibilidade, documentação |
| **Pandas** | Manipulação eficiente de dados |
| **BeautifulSoup** | Web scraping confiável |
| **Flask-RESTX** | Swagger automático, validação |
| **Vercel** | Deploy simples, serverless |

### Alternativas Consideradas

| Componente | Atual | Alternativa | Razão da Escolha |
|------------|-------|-------------|------------------|
| API Framework | Flask | FastAPI | Simplicidade para MVP |
| Database | CSV | PostgreSQL | Rápido desenvolvimento inicial |
| Cache | Nenhum | Redis | Não necessário para MVP |
| Queue | Nenhum | Celery | Complexidade desnecessária |

---

**Este documento é vivo e será atualizado conforme a evolução do projeto.**