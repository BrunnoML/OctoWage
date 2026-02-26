# OctoWage — Validação de Acesso Programático às Fontes de Dados v1.0

> **Data**: 2026-02-26
> **Status**: Pesquisa concluída — APIs validadas documentalmente
> **Próximo passo**: Testar requests reais no ambiente local

---

## Resumo Executivo

| Fonte | API Disponível? | Autenticação | Formato | Viabilidade |
|-------|----------------|--------------|---------|-------------|
| **DadosJusBr** | SIM — REST API pública | Nenhuma | JSON | ★★★★★ Excelente |
| **Portal da Transparência** | SIM — REST API com Swagger | Chave API (gratuita via email) | JSON | ★★★★★ Excelente |
| **CNJ (Magistrados)** | Parcial — QlikView + planilhas | Nenhuma | CSV/XLS via scraping | ★★★☆☆ Moderada |
| **Brasil.IO** | SIM — API paginada | Nenhuma | CSV/JSON | ★★★★☆ Boa |
| **Base dos Dados (CAGED/RAIS)** | SIM — BigQuery | Chave Google Cloud (free tier) | SQL/CSV | ★★★★☆ Boa |

**Recomendação**: Começar pelo DadosJusBr (melhor API, dados já consolidados do Judiciário/MP) + Portal da Transparência (Executivo Federal).

---

## 1. DadosJusBr — ⭐ FONTE PRINCIPAL RECOMENDADA

### O que é
Plataforma open source que coleta, padroniza e disponibiliza dados de remuneração do sistema de justiça brasileiro (Judiciário + Ministério Público). Projeto mantido por comunidade de dados abertos, em conformidade com a LAI (Lei 12.527/2011).

### API de Produção

```
Base URL: https://api.dadosjusbr.org
Docs:     https://api.dadosjusbr.org/doc
Portal:   https://dadosjusbr.org
GitHub:   https://github.com/dadosjusbr/api
```

### Endpoints Principais

```
GET /v1/orgaos                    → Lista todos os órgãos cobertos
GET /v1/orgao/{orgao}             → Detalhes de um órgão específico
GET /v1/orgao/{orgao}/{ano}       → Dados anuais de um órgão
GET /v1/orgao/{orgao}/{ano}/{mes} → Dados mensais de um órgão
```

### Dados Disponíveis

- Remuneração base (subsídio)
- Verbas indenizatórias (penduricalhos!)
- Gratificações
- Deduções obrigatórias
- Remuneração líquida
- Dados por membro individual (anonimizado ou nominal conforme o órgão)

### Cobertura

Cobre tribunais estaduais, federais, trabalhistas, eleitorais, militares e Ministérios Públicos. O status de cobertura pode ser consultado em https://dadosjusbr.org/status

### Stack Técnica

- Backend: GoLang 1.18+
- Banco: PostgreSQL 14.4+
- Deploy: Docker / AWS Elastic Beanstalk
- Storage: AWS S3

### Exemplo de Request

```python
import requests

# Listar todos os órgãos
response = requests.get("https://api.dadosjusbr.org/v1/orgaos")
orgaos = response.json()

# Pegar dados do TJSP em janeiro/2025
response = requests.get("https://api.dadosjusbr.org/v1/orgao/tjsp/2025/1")
dados_tjsp = response.json()
```

### Vantagens para o OctoWage

1. **Dados já padronizados** — não precisa fazer ETL pesado
2. **API REST limpa** — sem autenticação, JSON direto
3. **Open source** — pode rodar instância própria se necessário
4. **Separa subsídio de penduricalhos** — essencial para o "Raio-X do Teto"
5. **Cobertura ampla** — Judiciário + MP em todos os estados

### Limitações

- Não cobre Executivo nem Legislativo (para isso, usar Portal da Transparência)
- Alguns órgãos atrasam o envio de dados
- API pode ter rate limiting (não documentado explicitamente)

---

## 2. Portal da Transparência do Governo Federal

### O que é
API oficial do governo federal brasileiro com dados de servidores, despesas, contratos, licitações e benefícios sociais.

### API de Produção

```
Base URL:  https://api.portaldatransparencia.gov.br/api-de-dados
Swagger:   https://api.portaldatransparencia.gov.br/swagger-ui/index.html
OpenAPI:   https://api.portaldatransparencia.gov.br/v3/api-docs
Cadastro:  https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
```

### Autenticação

**Obrigatória** — chave API gratuita:

1. Acessar https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
2. Registrar seu email
3. Receber chave por email
4. Incluir no header de todas as requisições:

```python
headers = {
    "chave-api-dados": "SUA_CHAVE_AQUI"
}
```

### Endpoints de Servidores (Relevantes para OctoWage)

```
GET /api-de-dados/servidores
    → Lista servidores com filtros
    → Parâmetros: pagina, nome, cpf, orgaoServidorExercicio, etc.

GET /api-de-dados/servidores/{id}
    → Detalhes de um servidor específico

GET /api-de-dados/servidores/{id}/remuneracao
    → Remuneração detalhada de um servidor
```

### Campos de Remuneração Retornados

| Campo | Descrição |
|-------|-----------|
| `remuneracao_basica` | Salário base / subsídio |
| `remuneracao_eventual` | Gratificações eventuais |
| `verbas_indenizatorias` | **Penduricalhos!** |
| `total_remuneracao` | Soma bruta |
| `deducoes_obrigatorias` | IR, previdência, etc. |
| `normalizado_total_remuneracao` | Total normalizado |
| `mes_referencia` | Mês de referência |

### Exemplo de Request

```python
import requests

API_KEY = "SUA_CHAVE_AQUI"
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

headers = {
    "chave-api-dados": API_KEY,
    "Accept": "application/json"
}

# Buscar servidores por órgão
response = requests.get(
    f"{BASE_URL}/servidores",
    headers=headers,
    params={
        "pagina": 1,
        "orgaoServidorExercicio": "26246"  # Código do órgão
    }
)
servidores = response.json()

# Buscar remuneração de um servidor específico
servidor_id = servidores[0]["id"]
response = requests.get(
    f"{BASE_URL}/servidores/{servidor_id}/remuneracao",
    headers=headers
)
remuneracao = response.json()
```

### MCP Server Disponível

Existe um MCP Server pronto para integração com Claude Desktop/Cursor:

```bash
# Instalação
npm install mcp-portal-transparencia-brasil

# Configuração
npx mcp-portal-transparencia-brasil
# Requer: PORTAL_API_KEY no environment
```

GitHub: https://github.com/dutradotdev/mcp-portal-transparencia

### Vantagens para o OctoWage

1. **API oficial com Swagger** — documentação excelente
2. **Dados do Executivo Federal** — complementa DadosJusBr (Judiciário/MP)
3. **Inclui verbas indenizatórias** como campo separado
4. **Gratuita** — apenas cadastro de email
5. **MCP Server pronto** — pode usar no desenvolvimento

### Limitações

- Cobre apenas Executivo Federal (não estados/municípios)
- Paginação obrigatória (sem bulk download direto)
- Não cobre Legislativo diretamente
- Rate limiting não documentado claramente

---

## 3. CNJ — Remuneração dos Magistrados (Via Scraping)

### O que é
O CNJ publica planilhas de remuneração de magistrados de todos os tribunais brasileiros, conforme Resolução CNJ nº 215/2015 e Portaria nº 63/2017.

### Acesso

```
Portal:   https://www.cnj.jus.br/transparencia-cnj/remuneracao-dos-magistrados/
Links TJs: https://www.cnj.jus.br/transparencia-cnj/remuneracao-dos-magistrados/
           pagina-de-remuneracao-nos-sites-dos-tribunais/
```

### Formato

- **Planilhas padronizadas** (XLS/XLSX) enviadas por cada tribunal ao CNJ
- Publicadas em painel QlikView
- **Não há API REST oficial** para estes dados

### Projeto turicas/salarios-magistrados

Scraper open source que automatiza o download e conversão:

```
GitHub:    https://github.com/turicas/salarios-magistrados
Dados:     https://brasil.io/dataset/salarios-magistrados/
Formato:   CSV (via Brasil.IO)
Licença:   Open source
```

**Como funciona:**
1. Scrapy baixa todas as planilhas do CNJ
2. Extrai a aba "Contracheque"
3. Limpa e padroniza os dados
4. Exporta para CSV compactado

**Execução:**
```bash
git clone https://github.com/turicas/salarios-magistrados
cd salarios-magistrados
pip install -r requirements.txt
./run.sh  # Download + parse completo
```

### Brasil.IO como Intermediário

Os dados processados ficam disponíveis em https://brasil.io/dataset/salarios-magistrados/ sem necessidade de rodar o scraper localmente.

**API Brasil.IO:**
```python
import requests

# Acessar dados paginados
response = requests.get(
    "https://api.brasil.io/v1/dataset/salarios-magistrados/contracheques/data/",
    params={"page": 1, "page_size": 100}
)
dados = response.json()
```

### Vantagens

- Dados nominais por magistrado (nome + tribunal + mês)
- Histórico disponível
- Comunidade ativa mantendo o scraper

### Limitações

- Depende de scraping (pode quebrar se CNJ mudar o site)
- Dados podem ter atraso (depende do envio dos tribunais)
- Não é API oficial

---

## 4. Base dos Dados (basedosdados.org) — CAGED/RAIS

### O que é
Plataforma que disponibiliza dados públicos brasileiros tratados e padronizados via BigQuery (Google Cloud).

### Acesso

```
Portal:    https://basedosdados.org
BigQuery:  Consulta SQL direta (requer conta Google Cloud)
Docs:      https://basedosdados.github.io/mais/
```

### Dados Relevantes

```sql
-- CAGED (movimentações mensais)
SELECT * FROM `basedosdados.br_me_caged.microdados_movimentacao`
WHERE ano = 2025 AND sigla_uf = 'PE'

-- RAIS (declaração anual)
SELECT * FROM `basedosdados.br_me_rais.microdados_vinculos`
WHERE ano = 2024
```

### Autenticação

- Conta Google Cloud (free tier: 1TB de consultas/mês)
- Pacote Python: `pip install basedosdados`

```python
import basedosdados as bd

# Consultar CAGED de PE
df = bd.read_sql(
    "SELECT * FROM `basedosdados.br_me_caged.microdados_movimentacao` "
    "WHERE ano = 2025 AND sigla_uf = 'PE' LIMIT 1000",
    billing_project_id="seu-projeto-gcp"
)
```

### Vantagens

- Dados já tratados e padronizados
- SQL nativo (sem download de arquivos gigantes)
- CAGED + RAIS + muitas outras bases

### Limitações

- Requer conta Google Cloud
- Free tier limitado a 1TB/mês de queries
- Dados do setor privado (não cobre Judiciário/MP diretamente)

---

## 5. Estratégia de Integração Recomendada

### Fase 1 — MVP "Raio-X do Teto" (prioridade)

```
┌─────────────────────────────────────────────────────┐
│                   FONTES DO MVP                      │
│                                                      │
│  DadosJusBr API ──→ Judiciário + MP (supersalários) │
│        +                                             │
│  Portal Transparência API ──→ Executivo Federal      │
│        =                                             │
│  Dashboard comparativo: Quem ganha acima do teto?    │
└─────────────────────────────────────────────────────┘
```

**Por que essas duas primeiro:**
- DadosJusBr já tem os dados padronizados do Judiciário (onde estão 57,5% dos supersalários)
- Portal da Transparência cobre o Executivo Federal (Delegados, Agentes, AGU, etc.)
- Ambas APIs são REST + JSON = integração rápida com FastAPI

### Fase 2 — Comparação com Pisos

```
┌─────────────────────────────────────────────────────┐
│                   DADOS DE PISO                      │
│                                                      │
│  Tabela estática (atualizada manualmente):           │
│  - Piso professor: R$ 5.130 (MEC, jan/2026)         │
│  - Piso enfermeiro: R$ 4.750 (Lei 14.434/2022)      │
│  - Soldado PM: ~R$ 6.358 (média nacional)           │
│  - Agente PF: R$ 14.164 (Lei 13.333/2016)           │
│  - Delegado PF: R$ 26.800                            │
│  - Teto constitucional: R$ 46.366,19                │
│                                                      │
│  Fonte: Legislação + portarias oficiais              │
└─────────────────────────────────────────────────────┘
```

**Nota**: Pisos são definidos por lei/portaria e mudam pouco (1x/ano). Uma tabela estática com atualização manual anual é suficiente.

### Fase 3 — Setor Privado e Comparação Internacional

```
Base dos Dados (CAGED/RAIS) ──→ Salários formais Brasil
WID / OECD / ILO            ──→ Comparação internacional
```

---

## 6. Script de Validação (para rodar localmente)

Brunno, rode este script no seu ambiente local para confirmar o acesso:

```python
#!/usr/bin/env python3
"""
OctoWage — Script de Validação de APIs
Rode localmente para confirmar acesso às fontes de dados.
"""
import requests
import json
import sys

def test_dadosjusbr():
    """Testa acesso à API do DadosJusBr."""
    print("\n" + "=" * 60)
    print("TESTE 1: DadosJusBr API")
    print("=" * 60)

    try:
        # Listar órgãos
        r = requests.get("https://api.dadosjusbr.org/v1/orgaos", timeout=15)
        print(f"  GET /v1/orgaos → Status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            print(f"  Órgãos encontrados: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"  Exemplo: {json.dumps(data[0], indent=2, ensure_ascii=False)[:300]}")
            print("  ✅ DadosJusBr: ACESSÍVEL")
        else:
            print(f"  ⚠️ Status inesperado: {r.status_code}")
            print(f"  Resposta: {r.text[:200]}")

    except Exception as e:
        print(f"  ❌ ERRO: {e}")


def test_portal_transparencia(api_key=None):
    """Testa acesso à API do Portal da Transparência."""
    print("\n" + "=" * 60)
    print("TESTE 2: Portal da Transparência API")
    print("=" * 60)

    if not api_key:
        print("  ⚠️ Sem chave API.")
        print("  Cadastre em: https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email")
        print("  Depois rode: python validate_apis.py SUA_CHAVE")
        return

    headers = {
        "chave-api-dados": api_key,
        "Accept": "application/json"
    }

    try:
        # Buscar servidores (página 1)
        r = requests.get(
            "https://api.portaldatransparencia.gov.br/api-de-dados/servidores",
            headers=headers,
            params={"pagina": 1},
            timeout=15
        )
        print(f"  GET /servidores → Status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            print(f"  Servidores retornados: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"  Primeiro registro: {json.dumps(data[0], indent=2, ensure_ascii=False)[:300]}")
            print("  ✅ Portal da Transparência: ACESSÍVEL")
        elif r.status_code == 401:
            print("  ❌ Chave API inválida ou expirada")
        else:
            print(f"  ⚠️ Status: {r.status_code} - {r.text[:200]}")

    except Exception as e:
        print(f"  ❌ ERRO: {e}")


def test_brasil_io():
    """Testa acesso ao Brasil.IO (salários magistrados)."""
    print("\n" + "=" * 60)
    print("TESTE 3: Brasil.IO — Salários Magistrados")
    print("=" * 60)

    try:
        r = requests.get(
            "https://api.brasil.io/v1/dataset/salarios-magistrados/contracheques/data/",
            params={"page_size": 5},
            timeout=15
        )
        print(f"  GET /salarios-magistrados → Status: {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            print(f"  Registros na página: {len(results)}")
            if results:
                print(f"  Campos: {list(results[0].keys())}")
            print("  ✅ Brasil.IO: ACESSÍVEL")
        elif r.status_code == 401:
            print("  ⚠️ Brasil.IO pode requerer token para API")
            print("  Alternativa: download direto do CSV em https://brasil.io/dataset/salarios-magistrados/")
        else:
            print(f"  ⚠️ Status: {r.status_code}")

    except Exception as e:
        print(f"  ❌ ERRO: {e}")


def test_swagger_spec():
    """Testa acesso à especificação OpenAPI do Portal da Transparência."""
    print("\n" + "=" * 60)
    print("TESTE 4: Swagger/OpenAPI Spec — Portal da Transparência")
    print("=" * 60)

    try:
        r = requests.get(
            "https://api.portaldatransparencia.gov.br/v3/api-docs",
            timeout=15
        )
        print(f"  GET /v3/api-docs → Status: {r.status_code}")

        if r.status_code == 200:
            spec = r.json()
            paths = spec.get("paths", {})
            servidor_endpoints = [p for p in paths if "servidor" in p.lower()]
            print(f"  Total de endpoints: {len(paths)}")
            print(f"  Endpoints de servidores: {len(servidor_endpoints)}")
            for ep in servidor_endpoints[:5]:
                print(f"    → {ep}")
            print("  ✅ Swagger: ACESSÍVEL")
        else:
            print(f"  ⚠️ Status: {r.status_code}")

    except Exception as e:
        print(f"  ❌ ERRO: {e}")


if __name__ == "__main__":
    print("🐙 OctoWage — Validação de APIs")
    print("================================")

    api_key = sys.argv[1] if len(sys.argv) > 1 else None

    test_dadosjusbr()
    test_portal_transparencia(api_key)
    test_brasil_io()
    test_swagger_spec()

    print("\n" + "=" * 60)
    print("PRÓXIMOS PASSOS:")
    print("=" * 60)
    print("1. Se DadosJusBr OK → começar ETL dos dados do Judiciário")
    print("2. Cadastrar email no Portal da Transparência para obter chave API")
    print("3. Testar endpoints de remuneração com a chave obtida")
    print("4. Avaliar Brasil.IO como fonte complementar ou fallback")
```

---

## 7. Ações Imediatas para Brunno

### Prioridade 1 (Fazer agora)
- [ ] Cadastrar email em https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
- [ ] Salvar o script acima como `validate_apis.py` e rodar localmente
- [ ] Acessar https://api.dadosjusbr.org/doc para ver a documentação Swagger completa

### Prioridade 2 (Esta semana)
- [ ] Testar `GET /v1/orgao/tjsp/2025/1` no DadosJusBr para ver formato real dos dados
- [ ] Testar endpoint de remuneração do Portal da Transparência com a chave API
- [ ] Criar conta Google Cloud (free) para acessar Base dos Dados (CAGED/RAIS)

### Prioridade 3 (Próxima semana)
- [ ] Definir schema do PostgreSQL baseado nos campos reais das APIs
- [ ] Prototipar primeira tela do "Raio-X do Teto"
- [ ] Configurar repositório GitHub com Docker + FastAPI

---

*Documento de validação — OctoWage v1.0*
*Pesquisa realizada em 26/02/2026*
