#!/bin/bash
# ============================================================
# OctoWage — Atualizar deploy (executar após cada push)
# Uso: ssh root@187.77.44.185 'cd /opt/octowage && bash deploy/update.sh'
# ============================================================

set -e

echo "=== OctoWage — Atualizando ==="

cd /opt/octowage

# 1. Puxar alterações
echo "[1/3] Puxando do GitHub..."
git pull origin main

# 2. Rebuild e restart
echo "[2/3] Rebuild dos containers..."
docker compose up -d --build

# 3. Limpar imagens antigas
echo "[3/3] Limpando imagens não usadas..."
docker image prune -f

echo ""
echo "=== Atualização concluída! ==="
docker compose ps
