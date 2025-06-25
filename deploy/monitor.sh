#!/bin/bash
# Script de monitoramento da Books API

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📊 BOOKS API - STATUS MONITOR${NC}"
echo "=================================="

# Função para verificar serviço
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "✅ $service: ${GREEN}RUNNING${NC}"
    else
        echo -e "❌ $service: ${RED}STOPPED${NC}"
    fi
}

# Função para verificar porta
check_port() {
    local port=$1
    local desc=$2
    if ss -tuln | grep -q ":$port "; then
        echo -e "✅ Port $port ($desc): ${GREEN}OPEN${NC}"
    else
        echo -e "❌ Port $port ($desc): ${RED}CLOSED${NC}"
    fi
}

# Função para verificar URL
check_url() {
    local url=$1
    local desc=$2
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "✅ $desc: ${GREEN}OK${NC}"
    else
        echo -e "❌ $desc: ${RED}FAILED${NC}"
    fi
}

echo "🔧 System Services:"
check_service "books-api"
check_service "nginx"

echo ""
echo "🌐 Network Ports:"
check_port "5005" "Books API"
check_port "80" "Nginx HTTP"

echo ""
echo "🌍 API Endpoints:"
check_url "http://localhost:5005/api/v1/health" "Direct API"
check_url "http://localhost/api/v1/health" "Via Nginx"

echo ""
echo "💾 Disk Usage:"
df -h /var/www/books-api | tail -1

echo ""
echo "🧠 Memory Usage:"
free -h | grep Mem

echo ""
echo "📋 Recent Logs (last 5 lines):"
echo -e "${YELLOW}Books API:${NC}"
journalctl -u books-api --no-pager -n 5

echo ""
echo -e "${YELLOW}Nginx:${NC}"
journalctl -u nginx --no-pager -n 5

echo ""
echo "📊 Process Info:"
ps aux | grep -E "(gunicorn|nginx)" | grep -v grep

echo ""
echo "🔄 Last Restart Times:"
systemctl show books-api --property=ActiveEnterTimestamp --no-pager
systemctl show nginx --property=ActiveEnterTimestamp --no-pager