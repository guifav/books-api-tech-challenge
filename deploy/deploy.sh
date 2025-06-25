#!/bin/bash
# Script de deploy para a Books API

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
APP_DIR="/var/www/books-api"
APP_USER="books-api"
SERVICE_NAME="books-api"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo bash deploy/deploy.sh"
    exit 1
fi

log "🚀 Iniciando deploy da Books API..."

# Verificar se o diretório existe
if [ ! -d "$APP_DIR" ]; then
    error "Diretório $APP_DIR não encontrado. Execute install.sh primeiro."
    exit 1
fi

cd $APP_DIR

log "📦 Ativando ambiente virtual e instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt

log "📋 Configurando variáveis de ambiente..."
cp .env.production .env

log "🕷️  Executando scraping inicial..."
# Executar scraping para ter dados iniciais
sudo -u $APP_USER bash -c "cd $APP_DIR && source venv/bin/activate && python run_scraper.py" || warn "Scraping falhou, continuando..."

log "🔧 Configurando permissões..."
chown -R $APP_USER:$APP_USER $APP_DIR
chmod +x wsgi.py

log "🔄 Reiniciando serviços..."
systemctl stop $SERVICE_NAME || true
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

systemctl reload nginx

log "⏳ Aguardando aplicação iniciar..."
sleep 5

log "🧪 Testando aplicação..."
if curl -f http://localhost:5005/api/v1/health >/dev/null 2>&1; then
    log "✅ Aplicação está rodando!"
else
    error "❌ Aplicação não está respondendo"
    systemctl status $SERVICE_NAME
    exit 1
fi

log "🌐 Testando Nginx..."
if curl -f http://localhost/api/v1/health >/dev/null 2>&1; then
    log "✅ Nginx está funcionando!"
else
    error "❌ Nginx não está funcionando"
    nginx -t
    systemctl status nginx
    exit 1
fi

log "📊 Status dos serviços:"
systemctl is-active $SERVICE_NAME
systemctl is-active nginx

log "🎉 Deploy concluído com sucesso!"

echo ""
echo "📋 URLs disponíveis:"
echo "🌐 API: http://147.93.71.190/api/v1/health"
echo "📖 Docs: http://147.93.71.190/api/docs"
echo "🔍 Health: http://147.93.71.190/api/v1/health"

echo ""
echo "📋 Comandos úteis:"
echo "🔍 Status: systemctl status $SERVICE_NAME"
echo "📋 Logs: journalctl -u $SERVICE_NAME -f"
echo "🔄 Restart: systemctl restart $SERVICE_NAME"
echo "🧪 Test: curl http://localhost/api/v1/health"

echo ""
echo "📋 Credenciais de teste:"
echo "👤 Admin: admin / admin123"
echo "🧬 Scientist: scientist / science123"
echo "👤 User: user / user123"