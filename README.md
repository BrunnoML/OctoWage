<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/img/octowage-banner-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="static/img/octowage-banner-light.png">
    <img src="static/img/octowage-banner-light.png" alt="OctoWage — Transparência salarial do setor público brasileiro" width="480">
  </picture>
</p>

<p align="center">
  <strong>Plataforma open source de transparência salarial do setor público brasileiro.</strong><br>
  <em>Projeto acadêmico e de cidadania — sem fins lucrativos.</em>
</p>

## Por que o OctoWage existe?

Os portais de transparência brasileiros (DadosJusBr, Portal da Transparência, sites dos tribunais) são ferramentas poderosas, mas foram feitas para especialistas. Um cidadão comum que quer saber "quanto ganha um juiz comparado a um professor" precisa navegar dezenas de páginas, entender siglas como "penduricalhos" e cruzar dados de fontes diferentes.

O OctoWage resolve isso: agrega dados de fontes oficiais públicas e apresenta de forma visual e comparativa, para que qualquer pessoa possa entender a desigualdade salarial no setor público brasileiro e exercer o controle social previsto na Constituição.

**Este projeto não tem fins lucrativos, não tem vinculação institucional com nenhum órgão público e utiliza exclusivamente dados públicos.**

> Enquanto carreiras essenciais recebem pisos abaixo de R$ 6 mil, uma elite de 53 mil servidores custa R$ 20 bilhões acima do teto constitucional.

---

## Funcionalidades

- **Comparação visual** — Barras proporcionais mostrando salários reais vs teto constitucional (10 carreiras)
- **Raio-X do contracheque** — Decomposição: salário base vs penduricalhos
- **Comparador dinâmico** — Seletor com dropdown para comparar qualquer par de carreiras lado a lado
- **Comparação internacional** — 12 países (câmbio em tempo real via AwesomeAPI/BCB) com insights automáticos
- **Custo da desigualdade** — Quantos professores/enfermeiros/PMs caberiam no orçamento dos supersalários
- **Risco ocupacional** — Metodologia com 4 indicadores e fontes oficiais (CLT, NRs, FBSP)
- **Sugira uma carreira** — Engajamento da comunidade via issues no GitHub
- **Fontes auditáveis** — Cada número tem link direto para a fonte oficial
- **Termos de Uso e Política de Privacidade** — LGPD-compliant, prontos para produção
- **Acessibilidade** — VLibras (Libras), WCAG AA, navegação por teclado, mobile-first

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11+ · FastAPI · async/await |
| Frontend | Jinja2 (SSR) · HTMX · CSS nativo (custom properties) |
| Gráficos | Plotly.js / Chart.js (lazy loading) |
| Banco | PostgreSQL 16+ (futuro — MVP usa dados estáticos validados) |
| Infra | Docker · Nginx · Let's Encrypt · Alembic (migrações) |
| Deploy | VPS Ubuntu 24.04 · Docker Compose |

**Sem jQuery. Sem Bootstrap. Sem Tailwind. Sem frameworks JS pesados.**

HTMX (~14KB) é o único JavaScript obrigatório.

## Fontes de dados

| Fonte | O que fornece | Tipo |
|-------|--------------|------|
| [DadosJusBr](https://dadosjusbr.org) | Remuneração do Judiciário e MP | API |
| [Portal da Transparência](https://portaldatransparencia.gov.br) | Servidores do Executivo Federal | API |
| [MEC](https://www.gov.br/mec) | Piso do magistério | Portarias |
| [Planalto.gov.br](https://www.planalto.gov.br) | Legislação (leis de remuneração PF, enfermagem, etc.) | Legislação |
| [FBSP](https://forumseguranca.org.br) | Anuário de Segurança Pública (mortalidade policial) | Relatório anual |
| [AwesomeAPI](https://economia.awesomeapi.com.br) / [BCB PTAX](https://dadosabertos.bcb.gov.br) | Cotações de câmbio | API (tempo real) |

### Nota sobre valores de Soldado PM, Agente PC e Delegado PC

Os valores dessas carreiras são **médias nacionais estimadas** a partir de tabelas remuneratórias estaduais publicadas em diários oficiais. Não existe uma fonte federal única que consolide esses dados. A SENASP/MJSP publica estatísticas de segurança pública, mas não tabelas salariais unificadas. O cálculo foi feito cruzando editais de concursos públicos estaduais e tabelas remuneratórias disponíveis nos sites das secretarias de segurança e dos governos estaduais. Detalhes completos na [página Sobre > Metodologia salarial](./app/templates/pages/about.html).

## Quickstart

### Desenvolvimento local

```bash
# Clonar
git clone https://github.com/BrunnoML/octowage.git
cd octowage

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Dependências
pip install .

# Rodar
uvicorn app.main:app --reload

# Acessar: http://localhost:8000
```

### Docker (produção)

```bash
docker compose up -d --build
# Acessar: http://localhost (ou https://octowage.com.br em produção)
```

Guia completo de deploy na VPS: [`docs/DEPLOY_v1.0.md`](docs/DEPLOY_v1.0.md)

## Estrutura do projeto

```
app/
├── main.py              # Entry point FastAPI
├── config.py            # Configurações (Pydantic Settings)
├── routes/
│   ├── pages.py         # Rotas SSR (/, /comparar, /sobre, /termos, /privacidade)
│   └── fragments.py     # Fragmentos HTMX (barras, cards, detalhes)
├── services/
│   ├── salary_data.py   # 10 carreiras + metodologia de risco (4 indicadores)
│   └── exchange_rate.py # 9 moedas em tempo real (AwesomeAPI → BCB → fallback)
└── templates/
    ├── base.html        # Layout (header, footer, VLibras, meta tags)
    ├── pages/           # home, compare, about, terms, privacy
    └── fragments/       # Fragmentos HTMX (barras, calculadora, raio-x)
static/
├── css/                 # CSS nativo (custom properties, mobile-first)
├── js/                  # HTMX (~14KB)
└── img/                 # Logo, favicon, banners
deploy/
├── nginx.conf           # Reverse proxy + SSL + gzip + cache
├── setup-vps.sh         # Setup inicial da VPS (1x)
├── start.sh             # Primeiro deploy com SSL (1x)
└── update.sh            # Atualizar após cada push
docs/                    # Arquitetura, pesquisa, jurídico, deploy
```

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| `CLAUDE.md` | Instruções para o Claude (padrões, UX, regras de negócio) |
| `docs/ARCHITECTURE_v1.0.md` | Arquitetura técnica completa |
| `docs/RESEARCH_supersalarios_v1.0.md` | Pesquisa sobre supersalários no Brasil |
| `docs/API_VALIDATION_v1.0.md` | Validação das fontes de dados e APIs |
| `docs/COMPETITIVE_ANALYSIS_v1.0.md` | Análise competitiva e diferenciais |
| `docs/LEGAL_ANALYSIS_v1.0.md` | Análise jurídica, LGPD e proteção legal |
| `docs/DEPLOY_v1.0.md` | Guia de deploy na VPS (Docker + Nginx + SSL) |

## Fundamento jurídico

O OctoWage exibe apenas dados públicos amparados por:

- **LAI** — Lei 12.527/2011, Art. 8º (transparência ativa)
- **STF Tema 483** — ARE 652.777/SP (publicidade de remuneração de servidores)
- **CF Art. 37** — Princípios da publicidade e transparência

Não exibimos dados pessoais sensíveis (CPF, endereço, saúde). Atualmente trabalhamos apenas com dados agregados por carreira. Quando houver dados individualizados (fase 2), serão limitados a cargo e remuneração, conforme permitido pelo STF. O projeto não utiliza nem acessa nenhum sistema ou ferramenta institucional de qualquer órgão público.

## Outros projetos do autor

| Projeto | Descrição |
|---------|-----------|
| **OctoWage** | Transparência salarial do setor público (este projeto) |
| [OctoMask](https://github.com/BrunnoML/OctoMask) | Anonimização de textos sensíveis |

Ambos são projetos independentes, open source, desenvolvidos como parte do aprendizado em Sistemas de Informação.

## Sobre o autor

Desenvolvido por **Brunno ML** — graduando em Sistemas de Informação pela Estácio. Este projeto é parte do aprendizado acadêmico em desenvolvimento web, APIs e visualização de dados, e também um exercício de cidadania digital: facilitar o acesso a informações públicas que já existem, mas são difíceis de encontrar e comparar.

Não tem vinculação com nenhuma instituição pública ou privada. Todos os dados utilizados são públicos e acessíveis a qualquer cidadão pela internet.

## Status

**MVP pronto para deploy** — 10 carreiras com dados validados, comparação internacional com 12 países, seletor dinâmico, termos de uso e privacidade (LGPD). Deploy configurado para VPS com Docker + Nginx + SSL.

**Domínio:** [octowage.com.br](https://octowage.com.br) (em configuração)

**Próximos passos:** Consumo direto das APIs do DadosJusBr e Portal da Transparência, dados individualizados por tribunal, progressão de carreira dentro de cada cargo.

## Licença

Todos os direitos reservados por enquanto. Licença open source será definida antes do lançamento público.

---

<p align="center">Feito com ☕ por <a href="https://www.brunnoml.com.br"><strong>BrunnoML</strong></a></p>
