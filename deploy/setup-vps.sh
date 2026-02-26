#!/bin/bash
# ============================================================
# OctoWage — Setup inicial da VPS (executar UMA vez)
# Uso: ssh root@187.77.44.185 'bash -s' < deploy/setup-vps.sh
# ============================================================

set -e  # Parar em qualquer erro

echo "=== OctoWage — Configurando VPS ==="

# 1. Atualizar sistema
echo "[1/6] Atualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar Docker (se não tiver)
if ! command -v docker &> /dev/null; then
    echo "[2/6] Instalando Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "[2/6] Docker já instalado: $(docker --version)"
fi

# 3. Instalar Docker Compose plugin (se não tiver)
if ! docker compose version &> /dev/null; then
    echo "[3/6] Instalando Docker Compose plugin..."
    apt install -y docker-compose-plugin
else
    echo "[3/6] Docker Compose já instalado: $(docker compose version)"
fi

# 4. Instalar Git (se não tiver)
if ! command -v git &> /dev/null; then
    echo "[4/6] Instalando Git..."
    apt install -y git
else
    echo "[4/6] Git já instalado: $(git --version)"
fi

# 5. Clonar repositório
echo "[5/6] Clonando repositório..."
if [ ! -d "/opt/octowage" ]; then
    git clone https://github.com/BrunnoML/octowage.git /opt/octowage
else
    echo "  Repositório já existe em /opt/octowage"
    cd /opt/octowage && git pull
fi

# 6. Criar arquivo .env
echo "[6/6] Configurando .env..."
if [ ! -f "/opt/octowage/.env" ]; then
    cat > /opt/octowage/.env << 'EOF'
APP_ENV=production
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
PORTAL_TRANSPARENCIA_API_KEY=
EOF
    echo "  .env criado — edite se necessário: nano /opt/octowage/.env"
else
    echo "  .env já existe"
fi

echo ""
echo "=== Setup concluído! ==="
echo ""
echo "Próximos passos:"
echo "  1. Aponte o DNS de octowage.com.br para 187.77.44.185"
echo "  2. Execute: cd /opt/octowage && bash deploy/start.sh"
echo ""
