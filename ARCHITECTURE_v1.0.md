# OctoWage — Documento de Arquitetura v1.0

> **Projeto**: OctoWage — Plataforma Open Source de Monitoramento e Comparação Salarial
> **Autor**: Brunno ML + Claude (Arquitetura)
> **Data**: 2026-02-26
> **Stack**: FastAPI + Jinja2/HTMX + PostgreSQL + Docker
> **Repositório relacionado**: [OctoMask](https://github.com/BrunnoML/OctoMask)

---

## 1. Arquitetura de Dados — Pipeline ETL para Grandes Volumes

### 1.1 Visão Geral do Pipeline

O volume estimado de 10M–100M registros (microdados parciais com séries históricas de 5–10 anos) exige uma estratégia de ETL em camadas com pré-agregação.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FONTES DE DADOS                          │
├──────────┬──────────┬───────────┬──────────┬───────────────────┤
│  CAGED   │  RAIS    │  Portal   │   WID    │   OECD / ILO      │
│ (Brasil) │ (Brasil) │ Transp.   │ (Global) │   (Global)         │
└────┬─────┴────┬─────┴─────┬─────┴────┬─────┴─────────┬─────────┘
     │          │           │          │               │
     ▼          ▼           ▼          ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA BRONZE (Raw)                           │
│  Ingestão bruta via scripts Python (requests + basedosdados)    │
│  Formato: Parquet no disco / staging tables no PostgreSQL       │
│  Frequência: Batch mensal (CAGED) / Anual (RAIS)               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA SILVER (Cleaned)                       │
│  - Normalização de schemas (CBO → ISCO para comparação global)  │
│  - Tratamento de nulos, duplicatas, encoding                    │
│  - Conversão monetária (BCB API para câmbio histórico)          │
│  - Ajuste por inflação (IPCA/CPI)                               │
│  Formato: Tabelas normalizadas no PostgreSQL                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA GOLD (Aggregated)                      │
│  - Materialized Views para consultas frequentes                 │
│  - Agregações: mediana/média/percentis por ocupação×região×ano  │
│  - Tabelas de fato desnormalizadas para o FastAPI               │
│  Formato: Materialized Views + índices compostos                │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Decisões Técnicas

**Por que Parquet na camada Bronze?**
Os microdados do CAGED/RAIS vêm em CSV com milhões de linhas. Parquet oferece compressão 5–10x e leitura colunar, ideal para ETL com Pandas/DuckDB. Isso permite processar os dados localmente antes de carregar no PostgreSQL.

**Por que Materialized Views na camada Gold?**
O FastAPI não deve fazer agregações pesadas em tempo real sobre 50M+ registros. A estratégia é:

```sql
-- Exemplo: View materializada para salário mediano por ocupação e região
CREATE MATERIALIZED VIEW mv_salary_by_occupation_region AS
SELECT
    occupation_code,
    occupation_name,
    region_code,
    region_name,
    year,
    month,
    percentile_cont(0.25) WITHIN GROUP (ORDER BY salary) AS p25,
    percentile_cont(0.50) WITHIN GROUP (ORDER BY salary) AS p50_median,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY salary) AS p75,
    AVG(salary) AS mean_salary,
    COUNT(*) AS sample_size
FROM silver.salary_records
GROUP BY occupation_code, occupation_name, region_code, region_name, year, month;

-- Índice composto para queries do frontend
CREATE INDEX idx_mv_salary_occ_region_year
ON mv_salary_by_occupation_region(occupation_code, region_code, year DESC);

-- Refresh mensal (após ingestão do CAGED)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_salary_by_occupation_region;
```

**Ferramenta de ETL recomendada (gratuita):**
- **Opção 1 (Simples)**: Scripts Python com Pandas + SQLAlchemy, orquestrados por cron jobs no Docker
- **Opção 2 (Escalável)**: Apache Airflow (free, self-hosted) para orquestração — útil quando tiver múltiplas fontes com dependências
- **Opção 3 (Leve)**: Prefect ou Dagster (free tier) — mais moderno que Airflow, menor overhead

**Recomendação para fase inicial**: Opção 1 com scripts Python. Migrar para Airflow/Prefect quando o número de pipelines ultrapassar 10.

### 1.3 Schema Proposto (PostgreSQL)

```sql
-- Schema de staging (Bronze)
CREATE SCHEMA IF NOT EXISTS bronze;

-- Schema limpo (Silver)
CREATE SCHEMA IF NOT EXISTS silver;

-- Schema analítico (Gold)
CREATE SCHEMA IF NOT EXISTS gold;

-- Tabela principal Silver
CREATE TABLE silver.salary_records (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,          -- 'caged', 'rais', 'wid', 'oecd', 'ilo'
    country_code CHAR(3) NOT NULL,        -- ISO 3166-1 alpha-3
    region_code VARCHAR(20),              -- UF para Brasil, NUTS para Europa
    region_name VARCHAR(100),
    occupation_code VARCHAR(20) NOT NULL, -- CBO (Brasil) ou ISCO (internacional)
    occupation_name VARCHAR(200),
    sector_code VARCHAR(20),              -- CNAE (Brasil) ou ISIC (internacional)
    sector_name VARCHAR(200),
    year SMALLINT NOT NULL,
    month SMALLINT,                       -- NULL para dados anuais
    salary NUMERIC(12,2) NOT NULL,        -- Valor original na moeda local
    currency CHAR(3) NOT NULL,            -- ISO 4217 (BRL, USD, EUR)
    salary_usd NUMERIC(12,2),            -- Convertido para USD (câmbio médio do período)
    salary_ppp NUMERIC(12,2),            -- Ajustado por Paridade de Poder de Compra
    employment_type VARCHAR(20),          -- 'formal', 'informal', 'public', 'private'
    education_level VARCHAR(50),
    gender CHAR(1),                       -- 'M', 'F', NULL
    age_group VARCHAR(20),
    hours_weekly SMALLINT,
    created_at TIMESTAMP DEFAULT NOW(),

    -- Particionamento por ano para performance
    CONSTRAINT pk_salary_year CHECK (year >= 2000 AND year <= 2030)
) PARTITION BY RANGE (year);

-- Partições por ano
CREATE TABLE silver.salary_records_2020 PARTITION OF silver.salary_records
    FOR VALUES FROM (2020) TO (2021);
CREATE TABLE silver.salary_records_2021 PARTITION OF silver.salary_records
    FOR VALUES FROM (2021) TO (2022);
-- ... criar para cada ano

-- Tabela de metadados das fontes
CREATE TABLE silver.data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_url VARCHAR(500),
    last_update DATE,
    record_count BIGINT,
    coverage_start DATE,
    coverage_end DATE,
    notes TEXT
);

-- Tabela de câmbio histórico
CREATE TABLE silver.exchange_rates (
    date DATE NOT NULL,
    currency_from CHAR(3) NOT NULL,
    currency_to CHAR(3) NOT NULL,
    rate NUMERIC(12,6) NOT NULL,
    source VARCHAR(50),
    PRIMARY KEY (date, currency_from, currency_to)
);

-- Tabela de índices de preço (para salários reais)
CREATE TABLE silver.price_indices (
    country_code CHAR(3) NOT NULL,
    year SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    index_type VARCHAR(20) NOT NULL,  -- 'ipca', 'cpi', 'ppp'
    value NUMERIC(12,4) NOT NULL,
    base_year SMALLINT,
    PRIMARY KEY (country_code, year, month, index_type)
);
```

### 1.4 Otimizações de Performance no PostgreSQL

```sql
-- Extensão para compressão de dados antigos
-- TimescaleDB (free) ou pg_partman para gerenciar partições automaticamente

-- Índices estratégicos na camada Silver
CREATE INDEX idx_salary_country_year ON silver.salary_records(country_code, year DESC);
CREATE INDEX idx_salary_occupation ON silver.salary_records(occupation_code);
CREATE INDEX idx_salary_region ON silver.salary_records(region_code, year DESC);

-- Estatísticas estendidas para o query planner
CREATE STATISTICS salary_stats (dependencies)
ON country_code, region_code, occupation_code
FROM silver.salary_records;

-- Configuração do PostgreSQL para workload analítico
-- (adicionar no postgresql.conf ou docker-compose)
-- shared_buffers = 256MB (25% da RAM disponível)
-- work_mem = 64MB (para sorts e agregações)
-- effective_cache_size = 768MB (75% da RAM)
-- random_page_cost = 1.1 (se usando SSD)
```

---

## 2. Implementação HTMX — Padrões de Design

### 2.1 Arquitetura de Componentes

A filosofia é: **o servidor renderiza fragmentos HTML, o HTMX injeta na página**. Sem JSON, sem JavaScript pesado.

```
┌────────────────────────────────────────────────────────────┐
│                      BROWSER                                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Filtros       │  │ Gráfico      │  │ Tabela           │ │
│  │ (hx-get)     │  │ (Plotly/     │  │ (hx-get com      │ │
│  │              │  │  Chart.js)   │  │  paginação)      │ │
│  │ hx-trigger=  │  │              │  │                  │ │
│  │  "change"    │  │ hx-swap=     │  │ hx-indicator=    │ │
│  │              │  │  "innerHTML" │  │  "#loading"      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────┘ │
│         │                 │                  │              │
│         └────────┬────────┘──────────────────┘              │
│                  │ (HTTP: fragmentos HTML)                   │
└──────────────────┼──────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                             │
│                                                               │
│  /api/fragment/chart?occ=XXX&region=YYY&year=2025            │
│  /api/fragment/table?occ=XXX&page=1&per_page=20              │
│  /api/fragment/filters?country=BRA                            │
│                                                               │
│  → Jinja2 renderiza fragmento HTML (não página completa)     │
│  → Retorna <div> com script Plotly/Chart.js embutido         │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Padrão: Comparação Salarial com Filtros Encadeados

```html
<!-- templates/pages/compare.html -->
<div class="compare-container">

  <!-- Filtros com encadeamento -->
  <div class="filters">
    <!-- País dispara atualização dos outros filtros -->
    <select name="country"
            hx-get="/api/fragment/filters/regions"
            hx-target="#region-select"
            hx-trigger="change"
            hx-indicator="#filter-loading">
      <option value="BRA">Brasil</option>
      <option value="USA">Estados Unidos</option>
      <option value="DEU">Alemanha</option>
    </select>

    <!-- Região (atualizada pelo país) -->
    <div id="region-select">
      <select name="region"
              hx-get="/api/fragment/filters/occupations"
              hx-target="#occupation-select"
              hx-trigger="change"
              hx-indicator="#filter-loading">
        <!-- Preenchido via HTMX -->
      </select>
    </div>

    <!-- Ocupação (atualizada pela região) -->
    <div id="occupation-select">
      <select name="occupation">
        <!-- Preenchido via HTMX -->
      </select>
    </div>

    <!-- Botão de comparação -->
    <button hx-get="/api/fragment/comparison"
            hx-target="#results"
            hx-include="[name='country'], [name='region'], [name='occupation']"
            hx-indicator="#results-loading"
            hx-swap="innerHTML transition:true">
      Comparar
    </button>

    <!-- Indicador de loading -->
    <span id="filter-loading" class="htmx-indicator">
      <img src="/static/img/octowage-spinner.svg" width="20" alt="Carregando..."/>
    </span>
  </div>

  <!-- Resultados -->
  <div id="results">
    <span id="results-loading" class="htmx-indicator">
      Carregando dados...
    </span>
    <!-- Fragmentos injetados aqui -->
  </div>
</div>
```

### 2.3 Padrão: Gráfico Plotly via Fragmento HTMX

```python
# app/routes/fragments.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.salary_service import SalaryService

router = APIRouter(prefix="/api/fragment")

@router.get("/chart/salary-trend", response_class=HTMLResponse)
async def salary_trend_chart(
    request: Request,
    occupation: str,
    country: str = "BRA",
    years: int = 5
):
    """Retorna fragmento HTML com gráfico Plotly embutido."""
    data = await SalaryService.get_salary_trend(occupation, country, years)

    return templates.TemplateResponse(
        "fragments/chart_salary_trend.html",
        {
            "request": request,
            "chart_data": data.to_dict(orient="records"),
            "chart_id": f"chart-{occupation}-{country}",
            "title": f"Evolução Salarial — {data.occupation_name.iloc[0]}"
        }
    )
```

```html
<!-- templates/fragments/chart_salary_trend.html -->
<div class="chart-container">
  <h3>{{ title }}</h3>
  <div id="{{ chart_id }}"></div>
  <script>
    (function() {
      const data = {{ chart_data | tojson }};
      const trace = {
        x: data.map(d => d.year + '-' + String(d.month).padStart(2, '0')),
        y: data.map(d => d.p50_median),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Mediana',
        line: { color: '#2E86AB', width: 2 },
        fill: 'none'
      };

      const traceP25 = {
        x: data.map(d => d.year + '-' + String(d.month).padStart(2, '0')),
        y: data.map(d => d.p25),
        type: 'scatter',
        mode: 'lines',
        name: 'P25',
        line: { color: '#2E86AB', width: 0 },
        showlegend: false
      };

      const traceP75 = {
        x: data.map(d => d.year + '-' + String(d.month).padStart(2, '0')),
        y: data.map(d => d.p75),
        type: 'scatter',
        mode: 'lines',
        name: 'P75',
        line: { color: '#2E86AB', width: 0 },
        fill: 'tonexty',
        fillcolor: 'rgba(46, 134, 171, 0.15)',
        showlegend: false
      };

      Plotly.newPlot('{{ chart_id }}', [traceP25, traceP75, trace], {
        margin: { t: 10, r: 20, b: 40, l: 60 },
        yaxis: { title: 'Salário (R$)', tickformat: ',.0f' },
        xaxis: { title: '' },
        responsive: true,
        displayModeBar: false
      });
    })();
  </script>
</div>
```

### 2.4 Padrão: Tabela com Paginação Infinita

```html
<!-- templates/fragments/salary_table.html -->
<table class="salary-table">
  <thead>
    <tr>
      <th>Ocupação</th>
      <th>Região</th>
      <th>Mediana</th>
      <th>P25–P75</th>
      <th>Amostra</th>
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
    <tr>
      <td>{{ row.occupation_name }}</td>
      <td>{{ row.region_name }}</td>
      <td>R$ {{ "{:,.2f}".format(row.p50_median) }}</td>
      <td>R$ {{ "{:,.2f}".format(row.p25) }} – {{ "{:,.2f}".format(row.p75) }}</td>
      <td>{{ "{:,}".format(row.sample_size) }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

{% if has_more %}
<!-- Infinite scroll: carrega próxima página ao entrar no viewport -->
<div hx-get="/api/fragment/table?page={{ next_page }}&{{ query_params }}"
     hx-trigger="revealed"
     hx-swap="afterend"
     hx-indicator="#table-loading">
  <span id="table-loading" class="htmx-indicator">Carregando mais...</span>
</div>
{% endif %}
```

### 2.5 Anti-Padrões a Evitar com HTMX

| Anti-Padrão | Problema | Solução |
|-------------|----------|---------|
| `hx-trigger="keyup"` em campos de busca | Excesso de requests | Usar `hx-trigger="keyup changed delay:500ms"` |
| Não usar `hx-indicator` | Usuário não sabe que algo está carregando | Sempre incluir indicador visual |
| Recarregar gráfico inteiro ao mudar filtro | Gráfico "pisca" e perde estado de zoom | Usar `hx-swap="innerHTML transition:true"` com CSS transitions |
| Múltiplos `hx-get` que dependem entre si | Race conditions | Usar `hx-sync="closest form:abort"` |
| Enviar dados via query string longa | Limite de URL | Para filtros complexos, usar `hx-post` com formulário |

---

## 3. Escalabilidade — Estratégia de Cache e Performance

### 3.1 Arquitetura de Cache em 3 Camadas

Considerando o cenário de free tier + picos após atualização de bases governamentais:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA 1: CDN / Edge Cache                │
│                                                              │
│  Cloudflare (Free Tier — ilimitado para sites)               │
│  - Cache de assets estáticos (CSS, JS, imagens): 30 dias     │
│  - Cache de páginas HTML "frias" (dados do ano anterior):     │
│    Cache-Control: public, max-age=86400, s-maxage=604800     │
│  - Cache de fragmentos HTMX com Vary: HX-Request            │
│  - DDoS protection inclusa no free tier                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ MISS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA 2: Application Cache                │
│                                                              │
│  Redis (ou Valkey — fork open source) — 25MB free no Upstash │
│  OU cache em memória com cachetools (zero-cost)              │
│                                                              │
│  Estratégia por tipo de dado:                                │
│  ┌────────────────────────┬─────────┬──────────────────────┐ │
│  │ Tipo                   │ TTL     │ Invalidação          │ │
│  ├────────────────────────┼─────────┼──────────────────────┤ │
│  │ Filtros (países, UFs)  │ 24h     │ Deploy               │ │
│  │ Dados ano anterior     │ 7 dias  │ Manual               │ │
│  │ Dados mês atual        │ 1 hora  │ Após ETL             │ │
│  │ Fragmentos de gráfico  │ 4 horas │ Após ETL             │ │
│  │ Resultados de busca    │ 30 min  │ Tempo                │ │
│  └────────────────────────┴─────────┴──────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ MISS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA 3: Database Cache                   │
│                                                              │
│  PostgreSQL Materialized Views (já na camada Gold)           │
│  - Refresh CONCURRENTLY (sem lock de leitura)                │
│  - Índices compostos para queries do frontend                │
│  - pg_stat_statements para monitorar queries lentas          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Implementação de Cache no FastAPI

```python
# app/core/cache.py
from functools import wraps
from cachetools import TTLCache
import hashlib
import json

# Cache em memória (zero-cost, ideal para free tier)
# 1000 entradas, TTL de 1 hora
_cache = TTLCache(maxsize=1000, ttl=3600)

def cached_fragment(ttl: int = 3600):
    """Decorator para cachear fragmentos HTML renderizados."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gera chave baseada nos parâmetros
            key = hashlib.md5(
                json.dumps({"fn": func.__name__, "kwargs": kwargs}, sort_keys=True).encode()
            ).hexdigest()

            if key in _cache:
                return _cache[key]

            result = await func(*args, **kwargs)
            _cache[key] = result
            return result
        return wrapper
    return decorator

def invalidate_cache():
    """Chamado após ETL completar."""
    _cache.clear()
```

```python
# app/routes/fragments.py
from app.core.cache import cached_fragment

@router.get("/chart/salary-trend", response_class=HTMLResponse)
@cached_fragment(ttl=14400)  # 4 horas
async def salary_trend_chart(
    request: Request,
    occupation: str,
    country: str = "BRA",
    years: int = 5
):
    # ... (mesmo código anterior)
```

### 3.3 Headers HTTP para Cloudflare

```python
# app/middleware/cache_headers.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CacheHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        path = request.url.path

        # Assets estáticos: cache longo
        if path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=2592000"  # 30 dias

        # Fragmentos HTMX: cache médio com revalidação
        elif path.startswith("/api/fragment/"):
            response.headers["Cache-Control"] = "public, max-age=300, s-maxage=3600"
            response.headers["Vary"] = "HX-Request"  # Diferencia HTMX de browser direto

        # Páginas: cache curto
        elif request.headers.get("HX-Request") != "true":
            response.headers["Cache-Control"] = "public, max-age=60, s-maxage=300"

        return response
```

### 3.4 Deploy Gratuito — Opções Ranqueadas

| Opção | Custo | PostgreSQL | Limitações | Ideal para |
|-------|-------|------------|------------|------------|
| **Railway** | $5 free/mês | Incluso (1GB) | 500h execução/mês | MVP / Demonstração |
| **Render** | Free tier | Externo (Neon/Supabase) | Sleep após 15min inatividade | Projeto pessoal |
| **Fly.io** | Free tier | Incluso (1GB) | 3 VMs shared | Produção leve |
| **Oracle Cloud** | Always Free | Incluso (20GB!) | 1GB RAM, ARM | Melhor free tier |
| **Cloudflare Pages + Worker** | Free | Externo | Não roda Python diretamente | Apenas frontend |

**Recomendação**: Oracle Cloud Always Free (melhor custo-benefício) + Cloudflare CDN (free) na frente.

### 3.5 Estratégia para Picos Pós-Atualização Governamental

```
Calendário de publicações:
- CAGED: ~20 dias após o mês de referência (mensal)
- RAIS: Geralmente entre março e setembro (anual, com atraso)
- Portal da Transparência: Atualizações variáveis

Ações para picos:
1. PRÉ-AQUECIMENTO: Script que faz GET nas MVs mais acessadas 1h antes da publicação
2. CACHE ESTENDIDO: Aumentar TTL durante pico (de 1h para 4h)
3. RATE LIMITING: FastAPI-limiter (10 req/min por IP para fragmentos pesados)
4. QUEUE: Se usando VPS, Celery + Redis para requests pesados (gerar CSV/Excel)
```

---

## 4. Governança — Anonimização e Conformidade

### 4.1 Escopo Atual: Apenas Dados Públicos

Como o foco inicial é **apenas dados públicos** (CAGED, RAIS, Portal da Transparência, WID, OECD, ILO), o risco de LGPD é significativamente menor, mas não zero.

**Riscos remanescentes com dados públicos:**

| Risco | Exemplo | Mitigação |
|-------|---------|-----------|
| Reidentificação por cruzamento | Salário médio de "Analistas de TI" em "Limoeiro-PE" com amostra n=3 | Suprimir dados com n < 10 |
| Exposição de dados individuais do Portal da Transparência | Servidores públicos têm salário nominal público | Agregar por cargo/órgão, não por indivíduo |
| Dados de crowdsourcing futuro | Se implementar, cada registro = pessoa real | Differential privacy (k-anonymity ≥ 10) |

### 4.2 Regras de Supressão (Implementação Imediata)

```python
# app/services/anonymization.py
from dataclasses import dataclass

@dataclass
class AnonymizationConfig:
    """Configuração de anonimização por tipo de dado."""
    min_sample_size: int = 10        # Mínimo de registros para exibir
    min_employers: int = 3           # Mínimo de empregadores distintos
    round_salary: bool = True        # Arredondar para centenas
    suppress_outliers: bool = True   # Remover P1 e P99

class SalaryAnonymizer:
    def __init__(self, config: AnonymizationConfig = None):
        self.config = config or AnonymizationConfig()

    def should_suppress(self, sample_size: int, employer_count: int = None) -> bool:
        """Verifica se o dado deve ser suprimido."""
        if sample_size < self.config.min_sample_size:
            return True
        if employer_count and employer_count < self.config.min_employers:
            return True
        return False

    def anonymize_salary(self, salary: float) -> float:
        """Arredonda salário para dificultar reidentificação."""
        if self.config.round_salary:
            return round(salary / 100) * 100  # Arredonda para centenas
        return salary

    def filter_aggregation(self, data: dict) -> dict:
        """Filtra agregações que não atendem critérios mínimos."""
        if self.should_suppress(data.get("sample_size", 0), data.get("employer_count")):
            return {
                **data,
                "p50_median": None,
                "mean_salary": None,
                "suppressed": True,
                "suppression_reason": "Amostra insuficiente para garantir privacidade"
            }
        return data
```

### 4.3 Middleware LGPD

```python
# app/middleware/lgpd.py
from fastapi import Request, Response

class LGPDMiddleware:
    """Headers e políticas de conformidade LGPD."""

    async def __call__(self, request: Request, call_next):
        response = await call_next(request)

        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.plot.ly; "  # Plotly CDN
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )

        return response
```

### 4.4 Integração com OctoMask (Preparação para Crowdsourcing Futuro)

Se no futuro o crowdsourcing for implementado, o OctoMask pode ser adaptado como camada de anonimização:

```
┌──────────────────────────────────────────────────────┐
│              Fluxo Futuro de Crowdsourcing            │
│                                                       │
│  Usuário submete salário                              │
│       │                                               │
│       ▼                                               │
│  OctoMask API (nova) → Anonimiza metadados            │
│  - Remove nome, CPF, email do payload                 │
│  - Generaliza localização (bairro → cidade)           │
│  - Generaliza ocupação (subcategoria → categoria CBO) │
│       │                                               │
│       ▼                                               │
│  OctoWage Backend → Valida + armazena                 │
│  - K-anonymity check (k ≥ 10)                         │
│  - Detecção de outliers                               │
│  - Arredondamento de valores                          │
└──────────────────────────────────────────────────────┘
```

---

## 5. Análise Crítica — Pontos Cegos da Stack

### 5.1 FastAPI + HTMX: Limitações Reais

| Ponto Cego | Impacto | Severidade | Mitigação |
|------------|---------|------------|-----------|
| **Gráficos interativos pesados** | Plotly com 100k+ pontos trava o browser | Alta | Pré-agregar no backend, limitar a 10k pontos por gráfico, usar downsampling (LTTB algorithm) |
| **Estado do cliente** | HTMX é stateless por design — não mantém estado de filtros entre páginas | Média | Usar query parameters na URL (bookmarkable) + `hx-push-url="true"` para manter histórico |
| **Comparações lado a lado** | Múltiplos gráficos simultâneos = múltiplos requests | Média | Endpoint que retorna fragmento composto (2 gráficos em 1 request) |
| **Export pesado (CSV/Excel)** | Gerar CSV de 1M+ linhas bloqueia o worker | Alta | Celery task assíncrona + download via link temporário |
| **Real-time updates** | HTMX não suporta WebSocket nativamente (precisa extensão) | Baixa | Para dados governamentais (batch), polling com `hx-trigger="every 60s"` é suficiente |
| **SEO de dados dinâmicos** | Fragmentos HTMX não são indexados pelo Google | Média | Páginas principais renderizadas com SSR completo via Jinja2, fragmentos apenas para interação |
| **Mobile** | HTMX funciona bem, mas gráficos Plotly são pesados em mobile | Média | Chart.js como alternativa leve para mobile (detectar via User-Agent) |
| **Testes E2E** | HTMX é difícil de testar com ferramentas tradicionais | Média | Playwright para testes E2E, testar endpoints de fragmento como API normal |

### 5.2 Comparação com Alternativas (Por que HTMX e não SPA?)

```
                    HTMX + Jinja2         React/Next.js         Streamlit
                    ─────────────         ─────────────         ─────────
Complexidade        ★★☆☆☆ (Baixa)        ★★★★★ (Alta)          ★☆☆☆☆ (Mín.)
Performance         ★★★★☆ (Boa)          ★★★★★ (Excelente)     ★★☆☆☆ (Fraca)
SEO                 ★★★★★ (Nativo)       ★★★★☆ (com SSR)       ★☆☆☆☆ (Zero)
Curva Aprendizado   ★★★★★ (Python only)  ★★★☆☆ (JS/TS req.)   ★★★★★ (Python)
Manutenção OSS      ★★★★★ (Simples)      ★★★☆☆ (Build chain)   ★★★★☆ (Simples)
Escala (usuários)   ★★★★☆ (Boa)          ★★★★★ (Excelente)     ★☆☆☆☆ (Péssima)
Gráficos ricos      ★★★☆☆ (Limitado)     ★★★★★ (D3/Recharts)   ★★★★★ (Built-in)
```

**Veredicto**: Para o OctoWage, HTMX é a escolha certa. O trade-off em gráficos interativos é aceitável porque os dados são primariamente tabulares/temporais, e Plotly cobre 90% dos casos de visualização.

### 5.3 Recomendações de Mitigação Prioritárias

1. **Implementar downsampling LTTB** no backend para séries temporais longas (já tem lib Python: `lttb`)
2. **Usar `hx-push-url`** em todos os filtros para que comparações sejam compartilháveis via URL
3. **Endpoint de export assíncrono** desde o início — não deixar para depois
4. **Progressive enhancement**: páginas funcionam sem JavaScript, HTMX melhora a experiência
5. **Meta tags Open Graph** para compartilhamento em redes sociais (salário médio de X em Y)

---

## 6. Integração OctoMask ↔ OctoWage

### 6.1 Estado Atual do OctoMask

O OctoMask é uma aplicação frontend-only (HTML + JavaScript) que roda inteiramente no browser. Seus pontos fortes relevantes para o OctoWage são: detecção de CPF, CNPJ, email, telefone e endereço, suporte a português/inglês, e processamento 100% local.

### 6.2 Possibilidades de Integração

**Opção A: OctoMask como Módulo Python (Recomendada para OctoWage)**

Portar a lógica de detecção de entidades sensíveis do OctoMask para um módulo Python que o FastAPI possa usar diretamente.

```python
# octomask_py/detector.py (novo módulo derivado do OctoMask)
import re
from typing import List, Dict

class OctoMaskDetector:
    """Detector de dados sensíveis portado do OctoMask JS para Python."""

    PATTERNS = {
        "cpf": r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
        "cnpj": r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone_br": r"(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}",
        "cep": r"\d{5}-?\d{3}",
    }

    def detect(self, text: str) -> List[Dict]:
        """Detecta entidades sensíveis no texto."""
        findings = []
        for entity_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                findings.append({
                    "type": entity_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        return findings

    def mask(self, text: str) -> str:
        """Substitui entidades sensíveis por máscaras."""
        for entity_type, pattern in self.PATTERNS.items():
            text = re.sub(pattern, f"[{entity_type.upper()}_MASKED]", text)
        return text
```

**Opção B: OctoMask como API Separada**

Criar um microserviço Docker a partir do OctoMask para ser chamado pelo OctoWage.

```yaml
# docker-compose.yml (futuro)
services:
  octowage:
    build: ./octowage
    ports: ["8000:8000"]
    depends_on: [postgres, octomask-api]

  octomask-api:
    build: ./octomask-api
    ports: ["8001:8001"]
    # FastAPI wrapper em torno da lógica do OctoMask

  postgres:
    image: postgres:16
    volumes: ["pgdata:/var/lib/postgresql/data"]
```

**Opção C: OctoMask como Validador de Input (Crowdsourcing Futuro)**

Integrar o OctoMask diretamente no formulário de submissão de salários, rodando no browser antes de enviar ao servidor.

```html
<!-- No formulário de crowdsourcing (futuro) -->
<form hx-post="/api/crowdsource/submit"
      hx-trigger="submit"
      hx-target="#result"
      hx-ext="octomask-validator">

  <textarea name="additional_info"
            data-octomask="true"
            placeholder="Informações adicionais sobre o cargo...">
  </textarea>

  <div id="octomask-warnings">
    <!-- OctoMask JS avisa se detectar dados sensíveis antes de enviar -->
  </div>

  <button type="submit">Enviar salário (anonimizado)</button>
</form>
```

### 6.3 Identidade Visual — Suíte Octo*

```
Suíte Octo*
├── OctoMask   🐙🎭  — Anonimização de texto (privacidade)
├── OctoWage   🐙💰  — Monitoramento salarial (transparência)
└── [Futuro]   🐙📊  — OctoStats? OctoCrime? (análise criminal PCPE)

Identidade compartilhada:
- Prefixo "Octo" (polvo = ferramenta multibraço para dados)
- Paleta de cores: Azul marinho (#1B2838) + Laranja (#E8651A) + Branco
- Logo: Polvo estilizado segurando o ícone relevante (máscara, moeda, etc.)
- GitHub Organization: github.com/BrunnoML/Octo-Suite (ou repos separados)
```

---

## 7. Estrutura de Diretórios Proposta

```
octowage/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── README.md
├── LICENSE                          # MIT ou Apache 2.0
├── pyproject.toml                   # Poetry/pip
│
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app factory
│   ├── config.py                    # Settings via Pydantic
│   │
│   ├── core/
│   │   ├── cache.py                 # Cache em memória / Redis
│   │   ├── database.py              # SQLAlchemy async
│   │   └── security.py              # Rate limiting, CORS
│   │
│   ├── models/                      # SQLAlchemy models
│   │   ├── salary.py
│   │   ├── source.py
│   │   └── exchange_rate.py
│   │
│   ├── services/                    # Business logic
│   │   ├── salary_service.py
│   │   ├── comparison_service.py
│   │   └── anonymization.py
│   │
│   ├── routes/
│   │   ├── pages.py                 # Rotas de páginas completas (Jinja2)
│   │   ├── fragments.py             # Rotas de fragmentos HTMX
│   │   └── api.py                   # API JSON (para integrações futuras)
│   │
│   ├── middleware/
│   │   ├── cache_headers.py
│   │   └── lgpd.py
│   │
│   └── templates/
│       ├── base.html                # Layout principal
│       ├── pages/
│       │   ├── index.html           # Home
│       │   ├── compare.html         # Comparação salarial
│       │   ├── trends.html          # Tendências
│       │   └── about.html           # Sobre / metodologia
│       └── fragments/
│           ├── chart_salary_trend.html
│           ├── chart_comparison.html
│           ├── table_salaries.html
│           └── filters_region.html
│
├── etl/
│   ├── __init__.py
│   ├── sources/
│   │   ├── caged.py                 # ETL do CAGED (via basedosdados)
│   │   ├── rais.py                  # ETL da RAIS
│   │   ├── transparency.py          # Portal da Transparência
│   │   ├── wid.py                   # World Inequality Database
│   │   ├── oecd.py                  # OECD Stats
│   │   └── ilo.py                   # International Labour Organization
│   │
│   ├── transformers/
│   │   ├── currency.py              # Conversão monetária
│   │   ├── occupation_mapper.py     # CBO ↔ ISCO mapping
│   │   └── inflation_adjuster.py    # Ajuste por IPCA/CPI
│   │
│   └── orchestrator.py              # Cron job / scheduler
│
├── octomask_py/                     # Módulo Python do OctoMask
│   ├── __init__.py
│   └── detector.py
│
├── static/
│   ├── css/
│   ├── js/
│   │   └── htmx.min.js             # ~14KB
│   └── img/
│       └── octowage-logo.svg
│
├── tests/
│   ├── test_services/
│   ├── test_routes/
│   ├── test_etl/
│   └── test_anonymization/
│
├── scripts/
│   ├── init_db.py                   # Criar schemas e tabelas
│   ├── seed_data.py                 # Dados de exemplo
│   └── refresh_materialized.py      # Atualizar MVs
│
└── docs/
    ├── API.md
    ├── ETL.md
    └── CONTRIBUTING.md
```

---

## 8. Sustentabilidade Financeira do Projeto

Considerando seu interesse em financiamento, opções para projetos open source:

| Canal | Detalhes | Esforço |
|-------|----------|---------|
| **GitHub Sponsors** | Botão "Sponsor" no repo, recebimento via Stripe | Baixo |
| **Open Collective** | Transparência total de gastos, ideal para OSS | Baixo |
| **Selo "Powered by OctoWage"** | Empresas que usam a API citam o projeto | Médio |
| **Consultoria** | Oferecer setup/customização para empresas | Alto |
| **Grants** | Mozilla Open Source Fund, NLnet, Sovereign Tech Fund | Alto (aplicação) |

Texto sugerido para o README:

```markdown
## 💚 Apoie o projeto

OctoWage é 100% open source e gratuito. Se este projeto é útil para você:

- ⭐ Dê uma estrela no GitHub
- 🐛 Reporte bugs ou sugira funcionalidades
- 💰 [Sponsor via GitHub](link)
- 🏢 Empresas: Considere apoiar com infraestrutura (hosting, banco de dados)
```

---

## 9. Próximos Passos Sugeridos

**Fase 1 — MVP (4-6 semanas)**
1. Setup do repositório com Docker + PostgreSQL + FastAPI
2. ETL do CAGED via Base dos Dados (fonte mais acessível)
3. 3 telas: Home, Comparação por Ocupação, Tendências
4. Deploy no Oracle Cloud Free Tier

**Fase 2 — Expansão (6-10 semanas)**
5. Adicionar RAIS e Portal da Transparência
6. Comparação internacional (OECD como primeira fonte)
7. Cache com Cloudflare CDN
8. Testes automatizados

**Fase 3 — Maturidade (10-16 semanas)**
9. Módulo OctoMask Python integrado
10. API pública documentada (Swagger)
11. GitHub Sponsors + landing page
12. CI/CD com GitHub Actions

---

*Documento gerado em 2026-02-26. Versão 1.0.*
*Sujeito a revisão conforme evolução do projeto.*
