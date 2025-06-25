#!/bin/bash
# Script de instalação para VPS Ubuntu 22.04

set -e

echo "🚀 Iniciando instalação da Books API..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo ./install.sh"
    exit 1
fi

log "Atualizando sistema..."
apt update && apt upgrade -y

log "Instalando dependências do sistema..."
apt install -y python3 python3-pip python3-venv nginx git curl wget htop

log "Instalando Python 3.10 se necessário..."
apt install -y python3.10 python3.10-venv python3.10-dev

log "Criando usuário e diretórios..."
# Criar usuário para a aplicação se não existir
if ! id "books-api" &>/dev/null; then
    useradd -r -s /bin/false books-api
    log "Usuário books-api criado"
fi

# Criar diretórios
mkdir -p /var/www/books-api
mkdir -p /var/log/books-api
mkdir -p /etc/books-api

# Definir permissões
chown -R books-api:books-api /var/www/books-api
chown -R books-api:books-api /var/log/books-api
chmod 755 /var/www/books-api

log "Criando ambiente virtual Python..."
cd /var/www/books-api
python3 -m venv venv
chown -R books-api:books-api venv

log "Configurando Nginx..."
cat > /etc/nginx/sites-available/books-api << 'EOF'
server {
    listen 80;
    server_name 147.93.71.190 srv781710.hstgr.cloud;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Main location
    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static/ {
        alias /var/www/books-api/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5005/api/v1/health;
        access_log off;
    }
}
EOF

# Habilitar site
ln -sf /etc/nginx/sites-available/books-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
nginx -t

log "Criando serviço systemd..."
cat > /etc/systemd/system/books-api.service << 'EOF'
[Unit]
Description=Books API Gunicorn Application
After=network.target

[Service]
User=books-api
Group=books-api
WorkingDirectory=/var/www/books-api
Environment="PATH=/var/www/books-api/venv/bin"
ExecStart=/var/www/books-api/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
systemctl daemon-reload

log "Configurando firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

log "Instalação básica concluída!"
warn "Agora execute o script deploy.sh para fazer o deploy da aplicação"

echo ""
echo "📋 Próximos passos:"
echo "1. Clone o repositório em /var/www/books-api"
echo "2. Execute: bash deploy/deploy.sh"
echo "3. Inicie os serviços: systemctl start books-api nginx"