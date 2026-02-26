# Análise Jurídica — OctoWage v1.0

> **AVISO IMPORTANTE**: Este documento é uma análise informativa elaborada com base em pesquisa de legislação e jurisprudência pública. **NÃO constitui assessoria jurídica**. Recomenda-se fortemente a consulta a um advogado especializado em Direito Digital e LGPD antes do lançamento público da plataforma.

---

## 1. Enquadramento Legal do Projeto

O OctoWage opera na interseção de três marcos legais brasileiros:

| Legislação | Dispositivo-chave | Relevância para o OctoWage |
|------------|-------------------|---------------------------|
| **Constituição Federal** | Art. 5º, XXXIII; Art. 37, caput | Direito de acesso à informação + princípio da publicidade |
| **Lei de Acesso à Informação (LAI)** | Lei 12.527/2011, Art. 8º, §1º, III | Obriga divulgação de remuneração individualizada de servidores |
| **LGPD** | Lei 13.709/2018, Arts. 7º, 11, 23-30 | Regras de tratamento de dados pessoais pelo poder público e setor privado |
| **Marco Civil da Internet** | Lei 12.965/2014, Arts. 7º, 15, 19 | Responsabilidade de provedores de aplicação |

### 1.1 O que a LAI garante

A Lei 12.527/2011 (Art. 8º, §1º, III) determina que os órgãos públicos devem divulgar, de forma ativa e em sítios eletrônicos oficiais, informações sobre a remuneração e subsídio recebidos por ocupante de cargo, posto, graduação, função e emprego público, **incluindo auxílios, ajudas de custo, jetons e quaisquer outras vantagens pecuniárias**, de maneira **individualizada**.

Isso significa que os dados que o OctoWage pretende utilizar já são, por lei, de divulgação obrigatória.

### 1.2 O que o STF já decidiu (Tema 483)

O Supremo Tribunal Federal, no julgamento do **ARE 652.777/SP** (Tema 483 da Repercussão Geral), decidiu **por unanimidade** que:

> É legítima a publicação, inclusive em sítio eletrônico mantido pela Administração Pública, dos nomes dos seus servidores e do valor dos correspondentes vencimentos e vantagens pecuniárias.

**Pontos fundamentais da decisão:**

- A pessoa que decide ingressar no serviço público adere ao regime jurídico da Administração Pública, que prevê a publicidade de informações de interesse coletivo.
- A remuneração de agentes públicos é informação de interesse coletivo e fortalece o controle social.
- A decisão tem repercussão geral, aplicando-se a todos os casos similares (334+ processos sobrestados).

**Limites estabelecidos:**
- A divulgação de dados **mais sensíveis** (endereço residencial, CPF completo, documentos de identificação) **é proibida**.
- A publicidade se refere a nome + cargo + remuneração, não a dados pessoais sensíveis.

### 1.3 Posição do Ministro Barroso (AO 2.367/DF)

Em 2018, o Ministro Luís Roberto Barroso reiterou que publicar salários de juízes é questão de transparência, julgando improcedente ação da Associação de Juízes Federais do RJ/ES que tentava impedir a divulgação de remuneração detalhada de magistrados pelo CNJ.

---

## 2. Análise de Riscos Jurídicos

### 2.1 RISCO BAIXO — Divulgação de dados já públicos

| Aspecto | Avaliação |
|---------|-----------|
| **Risco** | Baixo |
| **Fundamento** | Os dados de remuneração de servidores são públicos por força da LAI e da decisão do STF (Tema 483) |
| **Condição** | Desde que o OctoWage utilize apenas dados já publicados por fontes oficiais (Portal da Transparência, DadosJusBr, portais dos tribunais) |

**O que já é seguro fazer:**
- Exibir nome + cargo + remuneração bruta de servidores públicos
- Calcular médias, medianas e rankings por órgão/cargo
- Comparar remunerações entre setores (cross-setor)
- Exibir valores de penduricalhos (auxílio-moradia, auxílio-alimentação etc.) que já são públicos
- Criar visualizações, gráficos e dashboards com esses dados

### 2.2 RISCO MÉDIO — Tratamento de dados pessoais (LGPD)

| Aspecto | Avaliação |
|---------|-----------|
| **Risco** | Médio |
| **Fundamento** | A LGPD se aplica mesmo a dados tornados públicos. Remuneração é dado pessoal (não sensível). |
| **Atenção** | Necessário base legal clara + finalidade específica + princípio da necessidade |

**A LGPD não proíbe o uso de dados públicos**, mas exige:

1. **Base legal** (Art. 7º da LGPD): Para o OctoWage, as bases legais aplicáveis são:
   - **Art. 7º, V** — Execução de políticas públicas (se houver parceria com órgão público)
   - **Art. 7º, IX** — Legítimo interesse do controlador (controle social, transparência)
   - **Art. 7º, VII** — Proteção da vida ou segurança do titular (argumento mais fraco)

2. **Princípio da finalidade** (Art. 6º, I): O tratamento deve ter propósito legítimo, específico e informado. O OctoWage tem finalidade clara: promover transparência e controle social sobre gastos públicos com pessoal.

3. **Princípio da necessidade** (Art. 6º, III): Limitar o tratamento ao mínimo necessário. Isso significa:
   - NÃO coletar CPF, endereço, telefone, dados bancários
   - NÃO cruzar com outras bases para enriquecer perfil pessoal
   - Focar apenas em: nome, cargo, órgão, remuneração, componentes da remuneração

4. **Princípio da adequação** (Art. 6º, II): O tratamento deve ser compatível com a finalidade declarada.

### 2.3 RISCO MÉDIO-ALTO — Web Scraping / Raspagem de Dados

| Aspecto | Avaliação |
|---------|-----------|
| **Risco** | Médio-alto |
| **Fundamento** | ANPD incluiu raspagem de dados no Mapa de Temas Prioritários 2024-2025 |
| **Atenção** | Regulamentação específica está sendo elaborada pela ANPD |

**Situação atual:**
- A ANPD está consolidando parâmetros e orientações sobre raspagem de dados.
- Em 2025, a ANPD programou atividades de fiscalização (preventiva, orientativa ou repressiva) sobre o tema.
- Ainda não há regulamentação específica publicada, mas a tendência é de maior rigor.

**Mitigação para o OctoWage:**
- **Preferir APIs oficiais** (DadosJusBr, Portal da Transparência) em vez de scraping direto.
- **Respeitar robots.txt** dos portais oficiais.
- **Não sobrecarregar servidores** — implementar rate limiting e cache.
- **Documentar a origem** de cada dado coletado.
- Quando APIs não estiverem disponíveis, utilizar **datasets já processados** (como os da Base dos Dados / Brasil.IO) em vez de fazer scraping direto.

### 2.4 RISCO MÉDIO — Ações individuais de servidores

| Aspecto | Avaliação |
|---------|-----------|
| **Risco** | Médio |
| **Fundamento** | Apesar do STF ter decidido pela legitimidade, servidores individuais podem tentar ações |
| **Precedentes** | Associações de magistrados já tentaram impedir divulgação e perderam no STF |

**Cenários possíveis:**
- Servidor solicita remoção de seus dados → OctoWage não é obrigado a remover dados públicos obtidos de fontes oficiais, mas deve ter canal de comunicação.
- Servidor alega dano moral → Improvável que prospere se os dados são fidedignos e já públicos.
- Associação de classe tenta liminar → Precedente do STF (Tema 483) e caso dos juízes federais (AO 2.367) jogam a favor da transparência.

**Mitigação:**
- Citar sempre a **fonte oficial** de cada dado exibido.
- Jamais publicar **dados que não estejam em fonte oficial**.
- Manter **nota metodológica** clara e acessível.
- Ter um **canal de contato** visível para comunicações.

### 2.5 RISCO BAIXO — Direitos Autorais sobre Dados

| Aspecto | Avaliação |
|---------|-----------|
| **Risco** | Baixo |
| **Fundamento** | Dados públicos governamentais não são protegidos por direito autoral (Art. 8º, Lei 9.610/98) |

A Lei de Direitos Autorais (Lei 9.610/98) em seu Art. 8º estabelece que **não são objeto de proteção como direitos autorais** os textos de tratados ou convenções, leis, decretos, regulamentos, **decisões judiciais e demais atos oficiais**.

Dados de remuneração publicados por órgãos governamentais são atos oficiais e, portanto, não possuem proteção autoral. No entanto, **bases de dados compiladas** (como as do DadosJusBr) podem ter proteção sui generis — por isso, sempre creditar a fonte e respeitar as licenças.

### 2.6 RISCO BAIXO-MÉDIO — Marco Civil da Internet

| Aspecto | Avaliação |
|---------|-----------|
| **Risco** | Baixo-médio |
| **Fundamento** | O OctoWage como provedor de aplicação tem responsabilidades legais |

**Responsabilidades:**
- Manter **registro de acesso** por 6 meses (Art. 15).
- Responsabilidade civil por conteúdo de terceiros só após **ordem judicial** não cumprida (Art. 19).
- Ter **Termos de Uso** e **Política de Privacidade** claros.

---

## 3. Medidas de Proteção Legal Obrigatórias

### 3.1 Documentos legais necessários

O OctoWage DEVE ter antes do lançamento público:

**a) Termos de Uso**
- Definir claramente o que a plataforma faz e o que não faz.
- Explicar que os dados são provenientes de fontes públicas oficiais.
- Incluir cláusula de isenção de responsabilidade por imprecisões nas fontes originais.
- Definir que a plataforma não presta assessoria jurídica ou financeira.

**b) Política de Privacidade (LGPD-compliant)**
- Identificar o controlador dos dados (Brunno ML / OctoWage).
- Descrever quais dados pessoais de **visitantes** são coletados (cookies, analytics).
- Descrever quais dados pessoais de **servidores** são tratados (nome, cargo, remuneração).
- Indicar a base legal para cada tratamento.
- Informar os direitos dos titulares (Art. 18 da LGPD).
- Indicar canal de contato do Encarregado de Dados (DPO).

**c) Nota Metodológica**
- Explicar de onde vêm os dados, como são tratados e com que periodicidade são atualizados.
- Explicar as limitações dos dados.

### 3.2 Disclaimers obrigatórios na interface

Em cada página/visualização, incluir:

```
Fonte: [nome da fonte oficial] | Dados referentes a [mês/ano]
Os dados exibidos são provenientes de fontes públicas oficiais e estão sujeitos
a atualizações e correções pelos órgãos responsáveis.
```

Rodapé global:

```
OctoWage é um projeto open source de controle social. Não tem vinculação
com nenhum órgão governamental. Os dados são obtidos exclusivamente de
fontes públicas oficiais conforme a Lei de Acesso à Informação (Lei 12.527/2011).
```

### 3.3 Boas práticas técnicas com implicação legal

| Prática | Justificativa Legal |
|---------|-------------------|
| Cache de dados (não consultar API a cada request) | Minimiza impacto nos servidores oficiais |
| Suprimir agregações com n < 10 | Evita identificação indireta em amostras pequenas |
| Não exibir CPF, endereço ou dados sensíveis | Limite estabelecido pelo STF no Tema 483 |
| Rate limiting no scraping | Respeito à infraestrutura pública + boa-fé |
| Registrar data/hora de cada coleta | Rastreabilidade para contestações |
| Manter backup das fontes originais | Prova de que o dado existia na fonte oficial |
| Usar HTTPS obrigatório | Segurança dos visitantes |
| Logs de acesso por 6 meses | Obrigação do Marco Civil da Internet (Art. 15) |

---

## 4. Dados Específicos — O Que Pode e O Que Não Pode

### 4.1 PODE exibir (dados públicos por lei):
- Nome completo do servidor
- Cargo/função
- Órgão de lotação
- Remuneração bruta (subsídio + vantagens)
- Detalhamento de verbas (penduricalhos): auxílio-moradia, auxílio-alimentação, diárias, indenizações, retroativos
- Descontos obrigatórios (IR, previdência)
- Remuneração líquida
- Comparações e rankings
- Médias, medianas e estatísticas agregadas

### 4.2 NÃO PODE exibir (dados sensíveis/privados):
- CPF (nem parcial, para evitar enriquecimento)
- Endereço residencial
- Telefone pessoal
- E-mail pessoal
- Dados bancários
- Informações de saúde
- Dados familiares (cônjuge, dependentes)
- Filiação partidária ou sindical
- Dados biométricos

### 4.3 ZONA CINZENTA (avaliar com advogado):
- Histórico funcional detalhado (todas as funções exercidas)
- Cruzamento de dados de remuneração com dados patrimoniais (ex: declarações de bens)
- Fotos dos servidores (disponíveis em alguns portais)
- Dados de lotação específica (unidade/vara/delegacia)

---

## 5. Cenários de Risco e Respostas

### Cenário 1: Servidor envia notificação extrajudicial pedindo remoção de dados

**Resposta recomendada:**
- Verificar se os dados são fidedignos e de fonte oficial.
- Responder formalmente citando: LAI (Art. 8º), STF Tema 483, e que os dados são de fonte pública.
- NÃO remover os dados se estiverem corretos e de fonte oficial.
- Documentar toda comunicação.

### Cenário 2: Ordem judicial determinando remoção

**Resposta recomendada:**
- Cumprir imediatamente (Marco Civil, Art. 19).
- Consultar advogado sobre possibilidade de recurso.
- Documentar a ordem e a remoção.

### Cenário 3: Ação de dano moral por servidor

**Defesa disponível:**
- Dados públicos por força de lei (LAI).
- Decisão vinculante do STF (Tema 483).
- Finalidade legítima de controle social.
- Ausência de culpa — dados fidedignos de fonte oficial.
- Exercício regular de direito (Art. 188, I, Código Civil).

### Cenário 4: Associação de classe tenta liminar para tirar o site do ar

**Defesa disponível:**
- Jurisprudência consolidada do STF a favor da transparência.
- Caso AO 2.367 (magistrados) julgado improcedente.
- Liberdade de expressão e direito à informação (Art. 5º, IV e XIV, CF).
- Controle social como direito constitucional.

### Cenário 5: ANPD solicita esclarecimentos sobre tratamento de dados

**Resposta recomendada:**
- Apresentar Política de Privacidade e Nota Metodológica.
- Demonstrar bases legais (legítimo interesse + LAI).
- Mostrar que aplica princípios de minimização, finalidade e necessidade.
- Demonstrar que não trata dados sensíveis.

---

## 6. Recomendações Finais

### 6.1 Antes do lançamento (OBRIGATÓRIO)
1. Elaborar **Termos de Uso** e **Política de Privacidade** com assessoria jurídica.
2. Implementar **nota metodológica** acessível em cada página.
3. Criar **canal de contato** visível (e-mail dedicado para questões jurídicas/LGPD).
4. Designar formalmente um **Encarregado de Proteção de Dados** (DPO), mesmo que seja o próprio Brunno inicialmente.
5. Revisar a plataforma com um **advogado especialista em Direito Digital/LGPD**.

### 6.2 Operação contínua
6. Manter **registro de todas as fontes** de dados com data de coleta.
7. **Atualizar dados regularmente** — dados desatualizados podem gerar imprecisões.
8. **Não editoralizar em excesso** — evitar juízos de valor sobre servidores individuais; deixar os números falarem.
9. **Responder comunicações jurídicas** dentro dos prazos legais.
10. **Acompanhar regulamentações da ANPD** sobre raspagem de dados.

### 6.3 Proteções adicionais recomendadas
11. Considerar constituir uma **associação ou organização sem fins lucrativos** para operar a plataforma (proteção patrimonial pessoal).
12. Estudar a viabilidade de um **seguro de responsabilidade civil digital**.
13. Manter **backup off-site** de toda a base de dados com timestamps (prova de fonte).
14. Documentar o projeto como **exercício de controle social e cidadania**, alinhado ao Art. 5º da Constituição Federal.

---

## 7. Legislação Referenciada

| Legislação | Dispositivo |
|------------|-------------|
| Constituição Federal/1988 | Art. 5º, XXXIII (acesso à informação); Art. 37, caput (publicidade) |
| Lei 12.527/2011 (LAI) | Art. 3º (diretrizes); Art. 8º (divulgação ativa) |
| Lei 13.709/2018 (LGPD) | Arts. 6º (princípios), 7º (bases legais), 23-30 (poder público) |
| Lei 12.965/2014 (Marco Civil) | Arts. 7º (direitos), 15 (registro), 19 (responsabilidade) |
| Lei 9.610/98 (Direitos Autorais) | Art. 8º (exceções — atos oficiais) |
| STF — ARE 652.777/SP | Tema 483 — Divulgação de remuneração de servidores |
| STF — AO 2.367/DF | Divulgação de remuneração de magistrados |

---

## 8. Fontes Consultadas

- [STF — Tema 483: Divulgação de remuneração de servidores](https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?incidente=4121428&numeroProcesso=652777&classeProcesso=ARE&numeroTema=483)
- [STF — Notícia sobre legitimidade da divulgação de vencimentos](https://noticias.stf.jus.br/postsnoticias/stf-decide-que-e-legitima-a-divulgacao-de-vencimentos-de-servidores/)
- [ConJur — Publicar salários de juízes é questão de transparência (Barroso)](https://www.conjur.com.br/2018-ago-25/publicar-salarios-juizes-questao-transparencia-barroso/)
- [ConJur — Servidor público não pode impedir divulgação de salário](https://www.conjur.com.br/2017-nov-15/servidor-publico-nao-impedir-orgao-divulgue-salario/)
- [JOTA — LAI vs LGPD: Itu terá de divulgar dados de remuneração](https://www.jota.info/coberturas-especiais/protecao-de-dados/lai-v-lgpd-itu-tera-de-divulgar-dados-completos-de-remuneracao-de-servidores-16082022)
- [Migalhas — Desafios jurídicos do web scraping](https://www.migalhas.com.br/coluna/dados-publicos/378258/os-desafios-juridicos-do-web-scraping)
- [Migalhas — Análise da raspagem de dados deveria ser antecipada pela ANPD](https://www.migalhas.com.br/depeso/409555/analise-da-raspagem-de-dados-deveria-ser-antecipada-pela-anpd)
- [Assis e Mendes — Web scraping e LGPD: riscos jurídicos](https://assisemendes.com.br/web-scraping-e-lgpd-riscos-juridicos-do-uso-de-dados-publicos/)
- [Portal da Transparência — Termos de uso](https://portaldatransparencia.gov.br/termos-de-uso)
- [Lei 12.527/2011 (LAI) — Texto integral](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm)
- [Fiquem Sabendo — Como a LGPD e a LAI vão se relacionar?](https://fiquemsabendo.com.br/transparencia/lgpd-lai)
- [Terracap — Dados de servidores no Portal da Transparência e LGPD](https://www.terracap.df.gov.br/index.php/listagem-faq/78-lgpd-lei-geral-de-protecao-de-dados-pessoais/192-49-sou-empregado-publico-e-meus-dados-estao-no-portal-da-transparencia-com-a-lgpd-isso-muda)
- [Mayer Brown — Retrospectiva ANPD e Proteção de Dados 2024](https://www.mayerbrown.com/pt/insights/publications/2025/01/um-olhar-retrospectivo-sobre-a-anpd-e-a-protecao-de-dados-no-brasil-em-2024)

---

> **Lembrete**: Esta análise não substitui assessoria jurídica profissional. Antes do lançamento público do OctoWage, consulte um advogado especializado em Direito Digital e LGPD.

---

*Versão: 1.0 | Data: 2026-02-26 | Autor: Pesquisa assistida por IA (não constitui parecer jurídico)*
