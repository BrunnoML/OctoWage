FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn[standard] jinja2 httpx pydantic pydantic-settings cachetools python-multipart

# Copiar código
COPY app/ app/
COPY static/ static/

# Porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Executar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
