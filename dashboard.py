#!/usr/bin/env python3
"""
Dashboard Streamlit para visualização dos dados da Books API
Tech Challenge - Fase 1 - Machine Learning Engineering
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Books API Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL base da API
API_BASE_URL = "http://localhost:5005"

class BooksDashboard:
    """Classe principal do dashboard"""
    
    def __init__(self):
        self.api_url = API_BASE_URL
        
    def check_api_status(self):
        """Verifica se a API está funcionando"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/health", timeout=5)
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_books_data(self):
        """Obtém dados de todos os livros"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/books", timeout=10)
            if response.status_code == 200:
                return pd.DataFrame(response.json())
            return None
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None
    
    def get_stats_overview(self):
        """Obtém estatísticas gerais"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/stats/overview", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Erro ao carregar estatísticas: {e}")
            return None
    
    def get_categories_stats(self):
        """Obtém estatísticas por categoria"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/stats/categories", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Erro ao carregar estatísticas por categoria: {e}")
            return None

def create_header():
    """Cria o cabeçalho do dashboard"""
    st.title("📚 Books API Dashboard")
    st.markdown("### Análise Interativa dos Dados de Livros")
    st.markdown("---")

def create_sidebar():
    """Cria a barra lateral com controles"""
    st.sidebar.title("🎛️ Controles")
    
    # Configurações
    st.sidebar.subheader("⚙️ Configurações")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Filtros
    st.sidebar.subheader("🔍 Filtros")
    
    return {
        'auto_refresh': auto_refresh
    }

def show_api_status(dashboard):
    """Mostra o status da API"""
    col1, col2, col3 = st.columns([1, 1, 2])
    
    status_ok, status_data = dashboard.check_api_status()
    
    with col1:
        if status_ok:
            st.success("✅ API Online")
        else:
            st.error("❌ API Offline")
    
    with col2:
        st.info(f"🌐 {dashboard.api_url}")
    
    with col3:
        if status_ok and 'total_books_loaded' in status_data:
            st.metric("📖 Livros Carregados", status_data['total_books_loaded'])
        else:
            st.metric("📖 Livros Carregados", "N/A")

def show_overview_metrics(stats):
    """Mostra métricas gerais"""
    if not stats:
        st.warning("Estatísticas não disponíveis")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📚 Total de Livros",
            f"{stats.get('total_books', 0):,}",
            help="Número total de livros na base de dados"
        )
    
    with col2:
        avg_price = stats.get('average_price', 0)
        st.metric(
            "💰 Preço Médio",
            f"£{avg_price:.2f}",
            help="Preço médio de todos os livros"
        )
    
    with col3:
        min_price = stats.get('min_price', 0)
        max_price = stats.get('max_price', 0)
        st.metric(
            "📊 Faixa de Preços",
            f"£{min_price:.2f} - £{max_price:.2f}",
            help="Menor e maior preço encontrados"
        )
    
    with col4:
        st.metric(
            "🏷️ Categorias",
            stats.get('total_categories', 0),
            help="Número de categorias diferentes"
        )

def create_price_distribution_chart(df):
    """Cria gráfico de distribuição de preços"""
    if df is None or df.empty:
        return None
    
    fig = px.histogram(
        df, 
        x='price', 
        nbins=20,
        title="📊 Distribuição de Preços",
        labels={'price': 'Preço (£)', 'count': 'Quantidade de Livros'},
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_layout(
        xaxis_title="Preço (£)",
        yaxis_title="Quantidade de Livros",
        showlegend=False
    )
    
    return fig

def create_rating_chart(stats):
    """Cria gráfico de distribuição de ratings"""
    if not stats or 'rating_distribution' not in stats:
        return None
    
    rating_dist = stats['rating_distribution']
    
    ratings = list(rating_dist.keys())
    counts = list(rating_dist.values())
    
    fig = px.bar(
        x=ratings,
        y=counts,
        title="⭐ Distribuição de Ratings",
        labels={'x': 'Rating (estrelas)', 'y': 'Quantidade de Livros'},
        color=counts,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Rating (estrelas)",
        yaxis_title="Quantidade de Livros",
        showlegend=False
    )
    
    return fig

def create_category_chart(df):
    """Cria gráfico de livros por categoria"""
    if df is None or df.empty:
        return None
    
    category_counts = df['category'].value_counts().head(10)
    
    fig = px.bar(
        x=category_counts.index,
        y=category_counts.values,
        title="🏷️ Top 10 Categorias",
        labels={'x': 'Categoria', 'y': 'Quantidade de Livros'},
        color=category_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title="Categoria",
        yaxis_title="Quantidade de Livros",
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

def create_price_vs_rating_scatter(df):
    """Cria gráfico de dispersão preço vs rating"""
    if df is None or df.empty:
        return None
    
    fig = px.scatter(
        df,
        x='price',
        y='rating',
        size='rating',
        color='category',
        title="💰⭐ Relação Preço vs Rating",
        labels={'price': 'Preço (£)', 'rating': 'Rating'},
        hover_data=['title']
    )
    
    fig.update_layout(
        xaxis_title="Preço (£)",
        yaxis_title="Rating (estrelas)"
    )
    
    return fig

def show_data_table(df, title="📋 Dados dos Livros"):
    """Mostra tabela de dados"""
    if df is None or df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    st.subheader(title)
    
    # Filtros para a tabela
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['Todas'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Filtrar por categoria", categories)
    
    with col2:
        min_price = st.number_input("Preço mínimo", min_value=0.0, value=0.0, step=1.0)
    
    with col3:
        max_price = st.number_input("Preço máximo", min_value=0.0, value=float(df['price'].max()), step=1.0)
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if selected_category != 'Todas':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= min_price) & 
        (filtered_df['price'] <= max_price)
    ]
    
    # Mostrar tabela
    st.dataframe(
        filtered_df[['id', 'title', 'price', 'rating', 'category', 'availability']],
        use_container_width=True,
        height=400
    )
    
    st.info(f"Mostrando {len(filtered_df)} de {len(df)} livros")

def show_search_interface(dashboard):
    """Interface de busca de livros"""
    st.subheader("🔍 Busca de Livros")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_title = st.text_input("Buscar por título")
    
    with col2:
        search_category = st.text_input("Buscar por categoria")
    
    if st.button("🔍 Buscar") or search_title or search_category:
        try:
            params = {}
            if search_title:
                params['title'] = search_title
            if search_category:
                params['category'] = search_category
            
            response = requests.get(f"{dashboard.api_url}/api/v1/books/search", params=params)
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    results_df = pd.DataFrame(results)
                    st.success(f"Encontrados {len(results)} livros")
                    show_data_table(results_df, "📋 Resultados da Busca")
                else:
                    st.warning("Nenhum livro encontrado com os critérios especificados")
            else:
                st.error("Erro ao realizar busca")
                
        except Exception as e:
            st.error(f"Erro na busca: {e}")

def main():
    """Função principal do dashboard"""
    create_header()
    
    # Inicializa dashboard
    dashboard = BooksDashboard()
    
    # Sidebar
    sidebar_config = create_sidebar()
    
    # Status da API
    show_api_status(dashboard)
    st.markdown("---")
    
    # Verifica se API está online
    status_ok, _ = dashboard.check_api_status()
    
    if not status_ok:
        st.error("⚠️ API não está disponível. Verifique se está rodando em http://localhost:5005")
        st.info("Execute: `make run` ou `python app.py` para iniciar a API")
        return
    
    # Carrega dados
    with st.spinner("📊 Carregando dados..."):
        df = dashboard.get_books_data()
        stats = dashboard.get_stats_overview()
    
    # Métricas principais
    st.subheader("📊 Visão Geral")
    show_overview_metrics(stats)
    st.markdown("---")
    
    # Gráficos
    if df is not None and not df.empty:
        # Layout em colunas para gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            price_chart = create_price_distribution_chart(df)
            if price_chart:
                st.plotly_chart(price_chart, use_container_width=True)
        
        with col2:
            rating_chart = create_rating_chart(stats)
            if rating_chart:
                st.plotly_chart(rating_chart, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            category_chart = create_category_chart(df)
            if category_chart:
                st.plotly_chart(category_chart, use_container_width=True)
        
        with col4:
            scatter_chart = create_price_vs_rating_scatter(df)
            if scatter_chart:
                st.plotly_chart(scatter_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Interface de busca
        show_search_interface(dashboard)
        st.markdown("---")
        
        # Tabela de dados
        show_data_table(df)
        
    else:
        st.warning("📭 Nenhum dado disponível. Execute o scraping primeiro com `make scrape`")
    
    # Informações do dashboard
    st.markdown("---")
    st.info(f"🕐 Última atualização: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()