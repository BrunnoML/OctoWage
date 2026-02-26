# OctoWage — Dockerfile de produção (multi-stage)

# === Stage 1: Builder (instala deps em camada cacheada) ===
FROM python:3.11-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# === Stage 2: Runtime (imagem leve) ===
FROM python:3.11-slim

LABEL maintainer="Brunno ML <brunnoml@gmail.com>"
LABEL description="OctoWage — Transparência salarial do setor público brasileiro"

# Usuário não-root (segurança)
RUN groupadd -r octowage && useradd -r -g octowage octowage

WORKDIR /app

# Dependências do builder
COPY --from=builder /install /usr/local

# Código da aplicação
COPY app/ ./app/
COPY static/ ./static/

ENV APP_ENV=production \
    APP_DEBUG=false \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER octowage

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

EXPOSE 8000

# 2 workers para 1 CPU (1 processando + 1 aguardando I/O)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--access-log"]
