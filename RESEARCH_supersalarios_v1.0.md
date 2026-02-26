# OctoWage — Pesquisa: Supersalários e Disparidades Salariais no Setor Público Brasileiro

> **Versão**: 1.0
> **Data**: 2026-02-26
> **Contexto**: Julgamento STF sobre penduricalhos (25/02/2026)
> **Objetivo**: Mapear dados, fontes e definir escopo de features do OctoWage

---

## 1. Panorama dos Supersalários — Dados-Chave

### 1.1 O Problema em Números

| Métrica | Valor | Fonte |
|---------|-------|-------|
| Teto constitucional atual | R$ 46.366,19/mês | CF Art. 37, XI |
| Servidores que ganham acima do teto | 53.000 (1,34% de 4 milhões) | República.org / Mov. Pessoas à Frente |
| Custo anual dos supersalários | R$ 20 bilhões (ago/2024–jul/2025) | Benchmark Internacional (UCSD) |
| Custo concentrado na magistratura | R$ 11,5 bilhões | idem |
| Custo no Ministério Público | R$ 3,2 bilhões | idem |
| Custo no Executivo Federal | R$ 4,33 bi (82% AGU/procuradores) | idem |
| Salário médio líquido de magistrado ativo | R$ 81.500/mês | idem |
| Salário médio líquido no TJSP | R$ 122.800/mês (165% acima do teto) | idem |
| Aumento do custo com supersalários de juízes em 2024 | +49,3% vs 2023 | Mov. Pessoas à Frente |
| Juízes brasileiros que ganham acima de US$400k/ano | ~11.000 | Benchmark Internacional |
| Apoio popular ao fim dos penduricalhos | 93% (Datafolha 2021), 83% (2025) | Datafolha |

### 1.2 Ranking Internacional (Benchmark UCSD)

Pesquisa de Sérgio Guedes-Reis (University of California San Diego), encomendada pelo Movimento Pessoas à Frente e República.org. Comparou 10 países.

| País | Servidores acima do teto | Observação |
|------|--------------------------|------------|
| **Brasil** | **53.000** | **R$ 20 bi/ano — 1º lugar** |
| Argentina | ~2.500 (estimativa) | 21x menor que o Brasil |
| EUA | ~4.000 | Valores controlados |
| Alemanha | 0 | Nenhum caso registrado |
| Demais (Chile, Colômbia, França, Itália, México, Portugal, Reino Unido) | < 2.000 cada | Limites respeitados |

**Dado impactante**: O gasto do Brasil com supersalários é 133 mil vezes maior que o de Portugal.

### 1.3 Os 5 Principais Penduricalhos

Classificados pelo STF/Flávio Dino como "indevidos acréscimos de natureza remuneratória dissimulados de indenização":

| Penduricalho | Valor estimado | Mecanismo |
|--------------|----------------|-----------|
| **Licença compensatória** | ~R$ 1.500/dia (R$ 15k por 10 dias) | Folgas não usufruídas convertidas em dinheiro |
| **Gratificação por acervo processual** | R$ 10k–15k/mês | Pagamento por volume de processos |
| **Férias acumuladas** | R$ 20k–100k+ (pagamento único) | Conversão de até 20 dias/ano em dinheiro |
| **Auxílio-alimentação inflado** | > R$ 4.000/mês | ~10% da remuneração de magistrado |
| **Auxílio-moradia** | R$ 4.377/mês (referência anterior) | Mesmo para quem tem imóvel próprio |

---

## 2. Disparidade Salarial — Segurança Pública

### 2.1 Polícia Federal (2025/2026)

| Cargo | Salário Inicial (2025) | Previsto 2026 |
|-------|----------------------|---------------|
| Delegado/Perito | R$ 26.800 | R$ 27.831 |
| Agente/Escrivão/Papiloscopista | R$ 14.164 | R$ 14.710 |
| **Razão Delegado:Agente** | **1,89x** | **1,89x** |

### 2.2 Polícias Civis Estaduais (variação extrema)

| Estado | Delegado (final carreira) | Agente/Escrivão (inicial) | Razão |
|--------|--------------------------|--------------------------|-------|
| São Paulo | ~R$ 30.000+ | ~R$ 5.500 | ~5,5x |
| Rio de Janeiro | R$ 26.981 | R$ 13.981 | ~1,9x |
| Bahia | R$ 13.032 | R$ 4.873 | ~2,7x |
| Mato Grosso | R$ 30.961 | ~R$ 8.000 | ~3,9x |
| **Pernambuco** | ~R$ 28.000–30.000 | ~R$ 5.000–7.000 | ~4-5x |

**Nota**: Os dados de PE precisam ser confirmados com fontes oficiais do governo estadual.

### 2.3 Polícia Militar

| Patente | Salário médio bruto |
|---------|-------------------|
| Soldado | R$ 6.358 |
| Média geral (praças + oficiais) | R$ 8.628 |
| Coronel | R$ 29.033 |
| **Razão Coronel:Soldado** | **4,6x** |

Reajuste de 9% para militares federais dividido em 2 parcelas: 4,5% em 2025 e 4,5% em 2026.

---

## 3. A Grande Disparidade — Carreiras Essenciais vs Cúpula do Judiciário

### 3.1 Comparação Direta (valores 2026)

| Carreira | Piso/Salário Base | Teto prático | vs Juiz médio (R$ 81,5k) |
|----------|-------------------|-------------|--------------------------|
| **Professor (ed. básica)** | R$ 5.130/mês (40h) | ~R$ 12.000 | **6,3%** do juiz médio |
| **Enfermeiro** | R$ 4.750/mês | ~R$ 8.000 | **5,8%** do juiz médio |
| **Soldado PM** | R$ 6.358/mês | ~R$ 10.000 | **7,8%** do juiz médio |
| **Agente PC (BA)** | R$ 4.873/mês | ~R$ 10.000 | **6,0%** do juiz médio |
| **Delegado PF** | R$ 26.800/mês | R$ 41.350 | **32,9%** do juiz médio |
| **Juiz (média nacional)** | R$ 35.462 (subsídio) | **R$ 81.500 líquido** | 100% (referência) |
| **Juiz (TJSP)** | R$ 35.462 (subsídio) | **R$ 122.800 líquido** | 150,7% |

### 3.2 Visualização da Disparidade (conceito para o OctoWage)

```
Salário mensal (R$) — Escala proporcional

Professor (piso)    ██ R$ 5.130
Enfermeiro (piso)   █▉ R$ 4.750
Soldado PM          ██▌ R$ 6.358
Agente PC (BA)      █▉ R$ 4.873
Agente PF           █████▌ R$ 14.164
Delegado PF         ██████████▌ R$ 26.800
Teto constitucional ██████████████████ R$ 46.366
Juiz (média real)   ████████████████████████████████ R$ 81.500
Juiz (TJSP real)    ████████████████████████████████████████████████ R$ 122.800
```

---

## 4. Fontes de Dados para o OctoWage

### 4.1 Fontes Primárias (Dados Abertos)

| Fonte | URL / Acesso | Tipo de Dado | Formato | Frequência |
|-------|-------------|-------------|---------|------------|
| **CNJ — Remuneração dos Magistrados** | cnj.jus.br/transparencia-cnj/remuneracao-dos-magistrados/ | Salário nominal + penduricalhos por magistrado | CSV/JSON/XML | Mensal |
| **Portal da Transparência Federal** | portaldatransparencia.gov.br | Remuneração servidores federais | CSV/API REST | Mensal |
| **Tribunais Estaduais** | Links individuais por TJ (Resolução CNJ 151) | Folha de pagamento por nome | PDF/CSV/Excel | Mensal |
| **CAGED (via Base dos Dados)** | basedosdados.org | Salários formais (setor privado + público) | BigQuery/CSV | Mensal |
| **RAIS** | gov.br/trabalho (microdados) | Salários anuais detalhados | CSV | Anual |
| **SIAPE** | Dados.gov.br | Servidores civis federais | CSV | Mensal |

### 4.2 Fontes de Pesquisa/Benchmark

| Fonte | Tipo | Relevância |
|-------|------|-----------|
| **República.org / Mov. Pessoas à Frente** | Benchmark internacional + estudo UCSD | Metodologia de comparação global |
| **World Inequality Database (WID)** | Distribuição de renda global | Contextualizar salários vs renda média |
| **OECD Government at a Glance** | Remuneração setor público por país | Comparação internacional padronizada |
| **ILO — Global Wage Report** | Salários globais por setor | Poder de compra internacional |

### 4.3 Fontes Específicas para o Problema dos Penduricalhos

A grande inovação do OctoWage pode ser **cruzar automaticamente** as seguintes bases:

```
CNJ (salário bruto + indenizações de cada juiz)
    ×
Portal da Transparência (outros servidores federais)
    ×
Portais estaduais (policiais, professores, enfermeiros)
    =
Dashboard que mostra a DISPARIDADE REAL em tempo real
```

---

## 5. Impacto no Escopo do OctoWage

### 5.1 Features Prioritárias Repensadas

Com base nesta pesquisa, sugiro **reordenar as prioridades** do MVP:

**ANTES (foco genérico):**
1. Comparação salarial por ocupação (CAGED/RAIS)
2. Tendências temporais
3. Comparação internacional

**DEPOIS (foco em impacto social):**
1. **"Raio-X do Teto"** — Dashboard que mostra quantos servidores ganham acima do teto, quanto custa, e quais são os penduricalhos (dados do CNJ + Portal da Transparência)
2. **"Quem Ganha Quanto?"** — Comparador visual entre carreiras essenciais (professor, enfermeiro, PM, bombeiro) vs cúpula do Judiciário/MP
3. **"Ranking da Transparência"** — Quais tribunais/órgãos publicam dados abertos vs quais dificultam o acesso
4. Comparação internacional (Benchmark UCSD como base)
5. Tendências temporais (evolução dos supersalários vs pisos)

### 5.2 Narrativa do Projeto

O OctoWage não é apenas uma ferramenta de dados — é uma **ferramenta de accountability democrática**.

**Tagline sugerida**: *"Transparência salarial para uma democracia mais justa"*

**Argumento central**: Se 93% da população é contra os penduricalhos, mas o problema persiste, é porque falta uma ferramenta acessível que traduza os dados brutos em informação compreensível para o cidadão.

### 5.3 Riscos e Cuidados

| Risco | Mitigação |
|-------|-----------|
| Processo judicial por exposição de dados | Todos os dados são públicos por lei (Resolução CNJ 151 + LAI) — citar a fonte sempre |
| Dados incorretos gerando desinformação | NUNCA estimar — usar apenas dados oficiais. Incluir nota metodológica em cada visualização |
| Pressão política para tirar do ar | Hospedagem distribuída (GitHub Pages como mirror), código open source |
| Confusão entre salário bruto e líquido | Sempre exibir ambos + explicação clara do que são penduricalhos |
| Viés na apresentação | Mostrar TODOS os dados, incluir contexto (custo de vida, complexidade do cargo) |

---

## 6. Cronologia STF — Linha do Tempo (para feature do OctoWage)

| Data | Evento |
|------|--------|
| 05/02/2026 | Dino determina revisão das verbas indenizatórias em todos os poderes |
| 18/02/2026 | Lula veta projetos de licenças compensatórias para TCU, Câmara e Senado |
| 19/02/2026 | Dino proíbe edição de novas leis que permitam pagamentos acima do teto |
| 23/02/2026 | Gilmar Mendes: verbas indenizatórias só com lei aprovada pelo Congresso |
| 24/02/2026 | Reunião: presidentes do STF, Senado, Câmara, TCU propõem regra de transição |
| 25/02/2026 | Plenário do STF julga ratificação da liminar de Dino |

---

## 7. Próximos Passos

1. **Validar fontes**: Testar acesso programático ao CNJ e Portal da Transparência
2. **Prototipar "Raio-X do Teto"**: Wireframe da tela principal
3. **Definir MVP mínimo**: Apenas dados federais (mais acessíveis) → depois estaduais
4. **Identidade visual**: Logo OctoWage + paleta de cores para o tema "transparência"

---

*Documento de pesquisa — OctoWage v1.0*
*Dados coletados em 26/02/2026 via fontes públicas*
