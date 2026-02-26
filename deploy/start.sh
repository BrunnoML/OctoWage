#!/bin/bash
# ============================================================
# OctoWage — Primeiro start (gerar SSL + subir containers)
# Uso: cd /opt/octowage && bash deploy/start.sh
# ============================================================

set -e

DOMAIN="octowage.com.br"
EMAIL="brunnoml@gmail.com"

echo "=== OctoWage — Primeiro deploy ==="

# 1. Verificar se DNS já aponta para este servidor
echo "[1/4] Verificando DNS..."
SERVER_IP=$(curl -s ifconfig.me)
DNS_IP=$(dig +short $DOMAIN 2>/dev/null || echo "")

if [ "$DNS_IP" != "$SERVER_IP" ]; then
    echo "  AVISO: $DOMAIN aponta para '$DNS_IP', mas este servidor é '$SERVER_IP'"
    echo "  O SSL só funciona quando o DNS estiver apontando corretamente."
    echo "  Deseja continuar sem SSL (HTTP apenas)? [s/N]"
    read -r resp
    if [ "$resp" != "s" ] && [ "$resp" != "S" ]; then
        echo "  Abortado. Configure o DNS e tente novamente."
        exit 1
    fi
    NO_SSL=true
else
    echo "  DNS OK: $DOMAIN -> $SERVER_IP"
    NO_SSL=false
fi

# 2. Subir sem SSL primeiro (para o Certbot conseguir validar)
echo "[2/4] Subindo Nginx temporário (HTTP)..."

# Criar config temporária sem SSL
cat > deploy/nginx-temp.conf << 'NGINX'
server {
    listen 80;
    server_name octowage.com.br www.octowage.com.br;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /static/ {
        alias /app/static/;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

# Usar config temporária
cp deploy/nginx.conf deploy/nginx-ssl.conf.bak
cp deploy/nginx-temp.conf deploy/nginx.conf

# Build e subir
docker compose up -d --build web nginx
echo "  Aguardando containers..."
sleep 5

# 3. Gerar certificado SSL
if [ "$NO_SSL" = false ]; then
    echo "[3/4] Gerando certificado SSL (Let's Encrypt)..."
    docker compose run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN

    # Restaurar config com SSL
    cp deploy/nginx-ssl.conf.bak deploy/nginx.conf
    rm -f deploy/nginx-temp.conf deploy/nginx-ssl.conf.bak

    echo "  SSL gerado com sucesso!"
else
    echo "[3/4] SSL pulado (DNS não configurado)"
fi

# 4. Reiniciar tudo com config final
echo "[4/4] Reiniciando com configuração final..."
docker compose up -d --build
sleep 3

echo ""
echo "=== Deploy concluído! ==="
echo ""
if [ "$NO_SSL" = false ]; then
    echo "  Acesse: https://$DOMAIN"
else
    echo "  Acesse: http://$SERVER_IP"
    echo "  (Execute novamente após configurar o DNS para ativar SSL)"
fi
echo ""
docker compose ps
