# OctoWage 🐙

**Plataforma open source de transparência salarial do setor público brasileiro.**

O OctoWage visualiza a desigualdade entre supersalários (Judiciário/MP) e pisos de carreiras essenciais — professores, enfermeiros e policiais. Feito para o cidadão comum, não para desenvolvedores.

> Enquanto carreiras essenciais recebem pisos abaixo de R$ 6 mil, uma elite de 53 mil servidores custa R$ 20 bilhões acima do teto constitucional.

---

## Funcionalidades

- **Comparação visual** — Barras proporcionais mostrando salários reais vs teto constitucional
- **Raio-X do contracheque** — Decomposição: salário base vs penduricalhos
- **Comparador cross-setor** — Professor vs Juiz, Enfermeiro vs Procurador, PM vs Delegado
- **Comparação internacional** — Brasil vs EUA, Alemanha, Portugal, Japão (câmbio em tempo real)
- **Custo da desigualdade** — Quantos professores/enfermeiros/PMs caberiam no orçamento dos supersalários
- **Risco ocupacional** — Metodologia com 4 indicadores e fontes oficiais (CLT, NRs, FBSP)
- **Fontes auditáveis** — Cada número tem link direto para a fonte oficial
- **Acessibilidade** — VLibras (Libras), WCAG AA, navegação por teclado, mobile-first

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11+ · FastAPI · async/await |
| Frontend | Jinja2 (SSR) · HTMX · CSS nativo (custom properties) |
| Gráficos | Plotly.js / Chart.js (lazy loading) |
| Banco | PostgreSQL 16+ (futuro — MVP usa dados estáticos validados) |
| Infra | Docker · Alembic (migrações) |

**Sem jQuery. Sem Bootstrap. Sem Tailwind. Sem frameworks JS pesados.**

HTMX (~14KB) é o único JavaScript obrigatório.

## Fontes de dados

| Fonte | O que fornece | Tipo |
|-------|--------------|------|
| [DadosJusBr](https://dadosjusbr.org) | Remuneração do Judiciário e MP | API |
| [Portal da Transparência](https://portaldatransparencia.gov.br) | Servidores do Executivo Federal | API |
| [SENASP/MJSP](https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica) | Dados de segurança pública | Relatórios |
| [MEC](https://www.gov.br/mec) | Piso do magistério | Portarias |
| [FBSP](https://forumseguranca.org.br) | Anuário de Segurança Pública | Relatório anual |
| [AwesomeAPI](https://economia.awesomeapi.com.br) / [BCB PTAX](https://dadosabertos.bcb.gov.br) | Cotações de câmbio | API (tempo real) |

## Quickstart

```bash
# Clonar
git clone https://github.com/BrunnoML/octowage.git
cd octowage

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Dependências
pip install -r requirements.txt

# Rodar
uvicorn app.main:app --reload

# Acessar
# http://localhost:8000
```

## Estrutura do projeto

```
app/
├── main.py              # Entry point FastAPI
├── config.py            # Configurações (Pydantic Settings)
├── routes/
│   ├── pages.py         # Rotas SSR (Jinja2)
│   └── fragments.py     # Fragmentos HTMX (barras, cards, detalhes)
├── services/
│   ├── salary_data.py   # Dados salariais + metodologia de risco
│   └── exchange_rate.py # Cotações em tempo real (AwesomeAPI → BCB → fallback)
└── templates/
    ├── base.html        # Layout base (header, footer, VLibras, meta tags)
    ├── pages/           # Páginas completas (home, comparar, sobre)
    ├── fragments/       # Fragmentos HTMX (barras, calculadora, raio-x)
    └── components/      # Componentes reutilizáveis
static/
├── css/
│   ├── variables.css    # Design tokens (cores, tipografia, espaçamento)
│   ├── base.css         # Reset + tipografia + layout
│   ├── components.css   # Cards, barras, botões, hero, footer
│   └── layouts.css      # Grid, flex, comparação
├── js/
│   └── htmx.min.js
└── img/
    ├── favicon.svg
    └── logo-versions.html
```

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| `CLAUDE.md` | Instruções para o Claude (padrões, UX, regras de negócio) |
| `ARCHITECTURE_v1.0.md` | Arquitetura técnica completa |
| `RESEARCH_supersalarios_v1.0.md` | Pesquisa sobre supersalários no Brasil |
| `API_VALIDATION_v1.0.md` | Validação das fontes de dados e APIs |
| `COMPETITIVE_ANALYSIS_v1.0.md` | Análise competitiva e diferenciais |
| `LEGAL_ANALYSIS_v1.0.md` | Análise jurídica, LGPD e proteção legal |

## Fundamento jurídico

O OctoWage exibe apenas dados públicos amparados por:

- **LAI** — Lei 12.527/2011, Art. 8º (transparência ativa)
- **STF Tema 483** — ARE 652.777/SP (publicidade de remuneração de servidores)
- **CF Art. 37** — Princípios da publicidade e transparência

Não exibimos dados pessoais sensíveis (CPF, endereço, saúde). Apenas nome, cargo e remuneração, conforme permitido.

## Ecossistema Octo*

| Projeto | Descrição |
|---------|-----------|
| **OctoWage** | Transparência salarial do setor público (este projeto) |
| [OctoMask](https://github.com/BrunnoML/OctoMask) | Anonimização de textos sensíveis |

## Status

**MVP em desenvolvimento** — dados estáticos validados com fontes oficiais. A fase 2 incluirá consumo direto das APIs do DadosJusBr e Portal da Transparência.

## Licença

Todos os direitos reservados por enquanto. Licença open source será definida antes do lançamento público.

---

Feito com dados públicos, código aberto e indignação cívica. 🇧🇷
