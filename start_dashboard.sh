#!/bin/bash
# Script para iniciar API e Dashboard automaticamente

echo "🚀 Iniciando Books API Dashboard..."
echo "=================================="

# Verifica se está no diretório correto
if [ ! -f "dashboard.py" ]; then
    echo "❌ Execute este script na pasta 'solution'"
    exit 1
fi

# Função para verificar se a API está rodando
check_api() {
    curl -s http://localhost:5005/api/v1/health > /dev/null 2>&1
    return $?
}

echo "🔍 Verificando se a API está rodando..."

if check_api; then
    echo "✅ API já está rodando em http://localhost:5005"
else
    echo "⚠️  API não está rodando"
    echo "📝 Para iniciar a API, execute em outro terminal:"
    echo "   cd $(pwd)"
    echo "   make run"
    echo ""
    echo "⏳ Aguardando API ficar disponível..."
    
    # Aguarda API ficar disponível (máximo 60 segundos)
    for i in {1..60}; do
        if check_api; then
            echo "✅ API detectada!"
            break
        fi
        sleep 1
        echo -n "."
    done
    
    if ! check_api; then
        echo ""
        echo "❌ API não foi detectada após 60 segundos"
        echo "   Inicie a API manualmente: make run"
        exit 1
    fi
fi

echo ""
echo "📊 Iniciando Dashboard Streamlit..."
echo "🌐 Dashboard será aberto em: http://localhost:8501"
echo ""

# Inicia o Streamlit
streamlit run dashboard.py