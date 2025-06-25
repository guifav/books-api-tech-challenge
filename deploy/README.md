# 🚀 Deploy Guide - Books API

Guia completo para deploy da Books API em produção na VPS Ubuntu 22.04.

## 📋 Informações da VPS

- **Host**: srv781710.hstgr.cloud
- **IP**: 147.93.71.190
- **SO**: Ubuntu 22.04 LTS
- **Acesso**: SSH root@147.93.71.190

## 🚀 Deploy Rápido

### 1. Conectar na VPS
```bash
ssh root@147.93.71.190
```

### 2. Clonar repositório
```bash
cd /var/www
git clone <URL_DO_REPOSITORIO> books-api
cd books-api
```

### 3. Executar instalação
```bash
bash deploy/install.sh
```

### 4. Fazer deploy
```bash
bash deploy/deploy.sh
```

### 5. Verificar status
```bash
bash deploy/monitor.sh
```

## 📝 Deploy Detalhado

### Pré-requisitos

A VPS deve ter:
- Ubuntu 22.04 LTS
- Acesso root via SSH
- Conexão com internet

### Passo 1: Preparação do Sistema

O script `install.sh` irá:
- Atualizar o sistema
- Instalar Python 3.10, Nginx, Git
- Criar usuário `books-api`
- Configurar diretórios em `/var/www/books-api`
- Configurar Nginx como proxy reverso
- Criar serviço systemd
- Configurar firewall básico

### Passo 2: Deploy da Aplicação

O script `deploy.sh` irá:
- Instalar dependências Python
- Configurar variáveis de ambiente
- Executar scraping inicial
- Iniciar serviços
- Testar a aplicação

## 🌐 URLs de Acesso

Após o deploy:

- **API Base**: http://147.93.71.190/
- **Health Check**: http://147.93.71.190/api/v1/health
- **Swagger Docs**: http://147.93.71.190/api/docs
- **Lista Livros**: http://147.93.71.190/api/v1/books

## 🔐 Credenciais de Teste

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin123` | admin | Todas |
| `scientist` | `science123` | data_scientist | read, ml |
| `user` | `user123` | user | read |

## 🔧 Comandos de Manutenção

### Verificar Status
```bash
systemctl status books-api
systemctl status nginx
```

### Ver Logs
```bash
journalctl -u books-api -f
journalctl -u nginx -f
```

### Reiniciar Serviços
```bash
systemctl restart books-api
systemctl restart nginx
```

### Atualizar Aplicação
```bash
cd /var/www/books-api
git pull
bash deploy/deploy.sh
```

### Monitor Completo
```bash
bash deploy/monitor.sh
```

## 📊 Monitoramento

### Logs da Aplicação
- **Aplicação**: `/var/log/books-api/`
- **Systemd**: `journalctl -u books-api`
- **Nginx**: `/var/log/nginx/`

### Métricas
- **CPU/Memory**: `htop`
- **Disk**: `df -h`
- **Network**: `ss -tuln`
- **Processes**: `ps aux | grep books-api`

## 🐛 Troubleshooting

### API não responde
```bash
# Verificar se está rodando
systemctl status books-api

# Ver logs
journalctl -u books-api -n 50

# Reiniciar
systemctl restart books-api
```

### Nginx erro 502
```bash
# Verificar configuração
nginx -t

# Verificar se API está rodando na porta 5005
ss -tuln | grep 5005

# Reiniciar nginx
systemctl restart nginx
```

### Erro de permissões
```bash
# Corrigir permissões
chown -R books-api:books-api /var/www/books-api
chmod +x /var/www/books-api/wsgi.py
```

### Dados não disponíveis
```bash
# Executar scraping manual
cd /var/www/books-api
sudo -u books-api bash -c "source venv/bin/activate && python run_scraper.py"
```

## 🔄 Atualizações

### Deploy de Nova Versão
```bash
cd /var/www/books-api
git pull origin main
bash deploy/deploy.sh
```

### Rollback
```bash
cd /var/www/books-api
git checkout <commit-anterior>
bash deploy/deploy.sh
```

## 🔒 Segurança

### Firewall
```bash
# Verificar regras
ufw status

# Bloquear IP suspeito
ufw deny from <IP>
```

### SSL (Opcional)
```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx

# Obter certificado
certbot --nginx -d srv781710.hstgr.cloud
```

## 📈 Performance

### Otimizações Implementadas
- **Gunicorn**: Multi-worker para concorrência
- **Nginx**: Proxy reverso com cache
- **Systemd**: Auto-restart em caso de falha
- **Logs**: Rotação automática

### Monitorar Performance
```bash
# CPU e Memory
htop

# Requisições por segundo
tail -f /var/log/nginx/access.log | grep -o "GET\|POST" | uniq -c

# Tempo de resposta
curl -w "@-" -o /dev/null -s "http://localhost/api/v1/health" <<< 'time_total: %{time_total}\n'
```

## 📞 Suporte

Em caso de problemas:
1. Execute `bash deploy/monitor.sh`
2. Verifique logs com `journalctl -u books-api -n 100`
3. Teste endpoints manualmente
4. Consulte este README