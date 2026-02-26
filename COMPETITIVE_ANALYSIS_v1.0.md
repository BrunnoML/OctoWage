# OctoWage — Análise Competitiva e Diferenciais v1.0

> **Data**: 2026-02-26
> **Objetivo**: Mapear o que já existe para não reinventar a roda e encontrar o "blue ocean" do OctoWage

---

## 1. Mapa de Concorrentes

### 1.1 Plataformas Brasileiras (Setor Público)

| Plataforma | O que faz | Pontos Fortes | Pontos Fracos |
|------------|-----------|---------------|---------------|
| **DadosJusBr** (dadosjusbr.org) | Contracheques padronizados do Judiciário e MP | API REST, open source, índice de transparência, 107 órgãos | Só cobre Judiciário/MP. Não compara com outras carreiras. Interface técnica, pouco acessível ao cidadão comum |
| **Portal da Transparência** (portaldatransparencia.gov.br) | Remuneração de servidores do Executivo Federal | Oficial, API documentada, dados individuais | UX péssima. Busca individual (nome/CPF). Sem comparações. Sem contexto (não explica penduricalhos). Só federal |
| **República em Dados** (dados.republica.org) | Painéis sobre gestão de pessoas no setor público | Gráficos bonitos, benchmark internacional, dados do SIAPE/RAIS | Foco em gestão pública, não em transparência salarial. Sem detalhamento por órgão/tribunal. Não mostra penduricalhos individualmente |
| **Portais estaduais** (cada estado) | Folha de pagamento estadual | Dados nominais, obrigação legal (LAI) | Fragmentados (27 sites diferentes). Formatos inconsistentes (PDF, XLS, HTML). Sem padronização. Sem comparação |
| **Brasil.IO** (brasil.io) | Dados abertos tratados (magistrados, eleições, etc.) | CSV limpo, API, comunidade ativa | Projeto voluntário, dados podem atrasar. Não tem interface de visualização |

### 1.2 Plataformas Brasileiras (Setor Privado)

| Plataforma | O que faz | Relevância para OctoWage |
|------------|-----------|-------------------------|
| **MeuSalário** (meusalario.org.br) | Comparação salarial via pesquisa crowdsourced (WageIndicator Foundation) | Modelo de comparação interessante. Já faz PPC internacional. Mas foco no privado, sem dados de setor público |
| **SalárioBR** (salariobr.com) | Pesquisa de cargos e salários para RH/DP | Mercado privado, ferramenta para empresas. Irrelevante para setor público |
| **Glassdoor Brasil** | Avaliações + salários auto-reportados | Setor privado. Praticamente sem dados de setor público |
| **Catho / Vagas.com** | Faixas salariais por cargo | Setor privado. Dados genéricos |

### 1.3 Plataformas Internacionais

| Plataforma | O que faz | Relevância |
|------------|-----------|-----------|
| **Levels.fyi** | Comparação salarial detalhada (tech, principalmente EUA) | Modelo de UX excelente para comparação. Foco em tech/privado |
| **Payscale** | Benchmarking salarial global | Modelo de negócio B2B. Sem foco em setor público |
| **WageWatchers** (GitHub) | Salary transparency multi-country (open source) | Crowdsourced. Foco Europa. Conceito similar mas escopo diferente |
| **Buffer Salaries** | Transparência salarial da empresa Buffer | Inspiração para transparência, mas é apenas uma empresa |
| **OpenGovSalary** (GitHub) | Salários do governo (genérico) | Projeto pequeno, pouca atividade |

### 1.4 Estudos/Pesquisas (Não são plataformas, mas produzem dados)

| Fonte | O que produz |
|-------|-------------|
| **Mov. Pessoas à Frente + República.org** | Benchmark internacional de supersalários (pesquisa UCSD) |
| **Transparência Brasil** | Mantém o DadosJusBr, publica relatórios |
| **IBGE / PNAD** | Dados de renda da população (incluindo setor público vs privado) |
| **DIEESE** | Pesquisas salariais por categoria profissional |

---

## 2. Análise de Gaps — O Que NINGUÉM Faz

Depois de mapear todos os concorrentes, identifiquei **6 gaps claros** que nenhuma plataforma preenche:

### GAP 1: Comparação Cross-Setor Visual e Acessível
**Ninguém compara** o salário de um juiz com o de um professor, enfermeiro e policial **no mesmo dashboard, com visualização clara para o cidadão comum**.

- DadosJusBr → Só Judiciário/MP
- Portal da Transparência → Só Executivo Federal
- República em Dados → Agregados, sem comparação entre carreiras
- Portais estaduais → Cada um isolado

### GAP 2: "Raio-X do Penduricalho"
**Ninguém decompõe visualmente** o contracheque mostrando "quanto é subsídio" vs "quanto é penduricalho" de forma que o cidadão leigo entenda.

- DadosJusBr padroniza as categorias, mas a interface é técnica
- Portal da Transparência mostra os valores mas sem contexto
- Nenhum site explica em linguagem simples

### GAP 3: Comparação Internacional de Setor Público
**Ninguém compara** o salário de um juiz/professor/policial brasileiro com equivalentes em outros países **com ajuste de poder de compra**.

- MeuSalário faz PPC, mas só para setor privado
- Benchmark UCSD é estudo estático (PDF), não plataforma interativa
- OECD Government at a Glance é relatório, não ferramenta

### GAP 4: Evolução Temporal dos Supersalários
**Ninguém mostra** a evolução temporal: como os penduricalhos cresceram ao longo dos anos vs como os pisos (professor, enfermeiro) evoluíram.

- DadosJusBr tem histórico mas não cruza com pisos de outras carreiras
- República em Dados não tem série temporal de penduricalhos

### GAP 5: Ranking de Transparência por Órgão
DadosJusBr tem um índice de transparência, mas **ninguém ranqueia** de forma comparável: "Qual tribunal é mais transparente? Qual mais esconde?"

### GAP 6: Open Source + API Pública para Jornalistas/Pesquisadores
**Nenhuma plataforma brasileira** oferece uma API REST pública consolidada que cruze dados do Judiciário + Executivo + pisos salariais em um único endpoint.

- DadosJusBr tem API, mas só do Judiciário
- Portal da Transparência tem API, mas só do Executivo Federal
- Ninguém unifica

---

## 3. Posicionamento do OctoWage

### 3.1 O Que o OctoWage NÃO Deve Ser

| Não ser... | Por quê |
|------------|---------|
| Outro portal de busca por nome/CPF | Portal da Transparência já faz isso |
| Clone do DadosJusBr | Eles já fazem muito bem o trabalho de coleta/padronização do Judiciário |
| Ferramenta para RH/empresas | Glassdoor, Payscale e SalárioBR já cobrem |
| Site com dados crus em tabelas | Brasil.IO já faz isso |

### 3.2 O Que o OctoWage DEVE Ser

**Tagline**: "A desigualdade salarial do setor público, visualizada."

**Posicionamento**: O OctoWage é a **ponte entre os dados brutos** (DadosJusBr, Portal da Transparência, portais estaduais) **e o entendimento do cidadão**. É a ferramenta que traduz números em indignação informada.

### 3.3 Features Únicas (Diferenciais Reais)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│   FEATURE 1: "Raio-X do Contracheque"                           │
│   ─────────────────────────────────────                         │
│   Visualização interativa que decompõe um contracheque          │
│   típico de magistrado em: subsídio base vs cada tipo           │
│   de penduricalho, com linguagem simples.                       │
│                                                                  │
│   "Se o teto é R$ 46.366, por que este juiz recebe              │
│    R$ 122.800? Aqui está a decomposição:"                       │
│                                                                  │
│   ████████████████████ Subsídio: R$ 35.462                      │
│   ██████████ Gratificação acervo: R$ 15.000                     │
│   ████████ Licença compensatória: R$ 12.000                     │
│   ██████ Férias indenizadas: R$ 8.000                           │
│   ████ Aux. alimentação: R$ 4.338                               │
│   ─────────────────── TETO: R$ 46.366 ──────────               │
│   ████████████████████████ ACIMA DO TETO: R$ 76.434            │
│                                                                  │
│   Ninguém faz isso de forma visual e acessível.                 │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FEATURE 2: "Quanto Vale Seu Trabalho?"                        │
│   ─────────────────────────────────────────                     │
│   Comparador cross-setor: selecione duas carreiras              │
│   e veja lado a lado: salário base, teto, benefícios,          │
│   requisitos (formação, concurso, risco).                       │
│                                                                  │
│   Exemplo:                                                      │
│   ┌─────────────────┬─────────────────┐                        │
│   │  PROFESSOR       │  JUIZ            │                       │
│   │  Piso: R$ 5.130  │  Subsídio: R$35k │                      │
│   │  Teto: ~R$ 12k   │  Real: R$ 81,5k  │                      │
│   │  Formação: Lic.  │  Formação: Bach.  │                     │
│   │  Risco: Baixo    │  Risco: Baixo     │                     │
│   │  Jornada: 40h    │  Jornada: ~30h    │                     │
│   │  Razão: 1x       │  Razão: 15,9x     │                    │
│   └─────────────────┴─────────────────┘                        │
│                                                                  │
│   Ninguém faz comparação entre carreiras públicas               │
│   com contexto (formação, jornada, risco).                      │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FEATURE 3: "O Custo da Desigualdade"                          │
│   ─────────────────────────────────────────                     │
│   Calculadora que mostra: "Com os R$ 20 bilhões                │
│   gastos em supersalários, seria possível:"                     │
│                                                                  │
│   → Contratar 326.000 professores (piso)                       │
│   → Contratar 421.000 enfermeiros (piso)                       │
│   → Dar aumento de 20% a todos os PMs do Brasil                │
│   → Financiar 1,3 milhão de bolsas universitárias              │
│                                                                  │
│   Isso torna o número abstrato (R$ 20 bi) em algo              │
│   tangível e compartilhável em redes sociais.                   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FEATURE 4: "Linha do Tempo da Desigualdade"                   │
│   ─────────────────────────────────────────                     │
│   Gráfico animado mostrando a evolução de 2015 a 2026:         │
│   - Piso do professor: de R$ 1.917 → R$ 5.130 (+168%)         │
│   - Custo dos supersalários: de R$ X → R$ 20 bi (+Y%)         │
│   - Salário real do juiz: de R$ X → R$ 81.500                 │
│                                                                  │
│   Pergunta visual: "Quem ganhou mais nos últimos 10 anos?"     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FEATURE 5: "Mapa da Desigualdade"                             │
│   ─────────────────────────────────────────                     │
│   Mapa do Brasil colorido por estado mostrando:                 │
│   - Razão juiz/professor por estado                             │
│   - Razão delegado/agente por estado                            │
│   - Estados que mais pagam acima do teto                        │
│                                                                  │
│   Clicar no estado abre detalhamento por tribunal/órgão.        │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FEATURE 6: API Pública Unificada                              │
│   ─────────────────────────────────────────                     │
│   Endpoint REST que cruza DadosJusBr + Portal da                │
│   Transparência + pisos em uma API única.                       │
│                                                                  │
│   GET /api/v1/compare?career1=juiz&career2=professor&state=PE  │
│                                                                  │
│   Para jornalistas, pesquisadores e outros desenvolvedores.     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Matriz de Diferenciação

| Feature | DadosJusBr | Portal Transp. | República em Dados | MeuSalário | **OctoWage** |
|---------|------------|----------------|-------------------|------------|-------------|
| Dados Judiciário/MP | ✅ | ❌ | Parcial | ❌ | ✅ (via DadosJusBr) |
| Dados Executivo Federal | ❌ | ✅ | ✅ | ❌ | ✅ (via Portal) |
| Comparação entre carreiras | ❌ | ❌ | ❌ | ❌ | **✅ ÚNICO** |
| Decomposição de penduricalhos | Técnico | Cru | ❌ | ❌ | **✅ ÚNICO** (visual) |
| Comparação internacional PPC | ❌ | ❌ | Parcial | ✅ (privado) | **✅ ÚNICO** (público) |
| Evolução temporal cruzada | Parcial | ❌ | ❌ | ❌ | **✅ ÚNICO** |
| Calculadora de custo social | ❌ | ❌ | ❌ | ❌ | **✅ ÚNICO** |
| Mapa por estado | ❌ | ❌ | ❌ | ❌ | **✅ ÚNICO** |
| API unificada | Parcial | Parcial | ❌ | ❌ | **✅ ÚNICO** |
| Open source | ✅ | ❌ | ❌ | ❌ | ✅ |
| Acessível ao cidadão leigo | ❌ | ❌ | Parcial | ✅ | **✅** |
| SEO (indexável) | Parcial | ✅ | ✅ | ✅ | **✅** (SSR) |

---

## 5. Relação com DadosJusBr — Complemento, Não Competição

O OctoWage **não compete** com o DadosJusBr — **consome** seus dados e adiciona camadas que eles não têm:

```
DadosJusBr (backend de dados)
    │
    ├── Coleta e padroniza contracheques → OctoWage CONSOME
    ├── Índice de transparência          → OctoWage REFERENCIA
    └── API REST                         → OctoWage USA COMO FONTE
         │
         ▼
OctoWage (camada de análise e visualização)
    │
    ├── Cruza com Portal da Transparência (Executivo)
    ├── Cruza com pisos salariais (tabela estática)
    ├── Adiciona comparação cross-setor
    ├── Adiciona contexto (formação, jornada, risco)
    ├── Adiciona calculadora de custo social
    ├── Adiciona mapa por estado
    └── Entrega tudo em linguagem acessível
```

**Oportunidade**: Propor parceria com a Transparência Brasil (mantenedora do DadosJusBr). O OctoWage pode ser a "camada de apresentação" dos dados deles.

---

## 6. Resumo: Por Que o OctoWage Existe

> **O problema não é falta de dados** — DadosJusBr, Portal da Transparência e portais estaduais publicam gigabytes de informação.
>
> **O problema é que ninguém traduz esses dados** em uma narrativa visual que o cidadão comum entenda e se indigne.
>
> O OctoWage é a ponte entre **dados brutos** e **entendimento público**.

---

*Análise competitiva — OctoWage v1.0*
*Pesquisa realizada em 26/02/2026*
