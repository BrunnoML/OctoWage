# CLAUDE.md — OctoWage

> Instruções para o Claude ao trabalhar neste projeto.
> Este arquivo é lido automaticamente pelo Claude Code/Cowork.

---

## Sobre o Projeto

**OctoWage** é uma plataforma open source de transparência salarial do setor público brasileiro. Visualiza a desigualdade entre supersalários (Judiciário/MP) e pisos de carreiras essenciais (professores, enfermeiros, policiais). Faz parte da suíte **Octo*** (OctoMask, OctoWage).

- **Repositório**: github.com/BrunnoML/OctoWage
- **Stack**: FastAPI + Jinja2/HTMX + PostgreSQL + Docker
- **Fontes de dados**: DadosJusBr API, Portal da Transparência API, Base dos Dados (CAGED/RAIS)
- **Público-alvo**: Cidadão comum, jornalistas, pesquisadores

---

## Padrões de Código

### Python (Backend)
- Python 3.11+
- FastAPI com async/await
- Type hints em todas as funções
- Docstrings em português
- Formatação: Black + isort + ruff
- Testes: pytest + pytest-asyncio
- Variáveis de ambiente via Pydantic Settings

### HTML/CSS/JS (Frontend)
- Jinja2 para templates (SSR)
- HTMX para interatividade (sem frameworks JS pesados)
- CSS: variáveis CSS nativas (custom properties) — SEM Tailwind, SEM Bootstrap
- Gráficos: Plotly.js ou Chart.js (via fragmentos HTMX)
- Mapas: Leaflet.js ou D3.js (para mapa do Brasil)

### Banco de Dados
- PostgreSQL 16+
- Schemas separados: bronze, silver, gold
- Materialized Views para consultas analíticas
- Migrações: Alembic

---

## UX/UI — DIRETRIZES OBRIGATÓRIAS

### Filosofia de Design
O OctoWage é uma ferramenta para o CIDADÃO COMUM, não para desenvolvedores. Todo elemento visual deve ser pensado para alguém que nunca acessou dados públicos antes. A experiência deve ser tão intuitiva quanto um feed de rede social.

### Mobile-First (OBRIGATÓRIO)
- **TODO layout deve ser projetado primeiro para mobile (360px), depois adaptado para desktop.**
- Breakpoints padrão:
  - `--bp-mobile: 360px` (design base)
  - `--bp-tablet: 768px`
  - `--bp-desktop: 1024px`
  - `--bp-wide: 1440px`
- Usar `min-width` media queries (mobile-first progression)
- Testar SEMPRE em viewport de 360px antes de considerar pronto
- Touch targets mínimos de 44x44px (acessibilidade)
- Sem hover-only interactions (mobile não tem hover)

### Responsividade
- Gráficos devem usar `responsive: true` no Plotly/Chart.js
- Tabelas em mobile: converter para card layout (stacked) em vez de scroll horizontal
- Menus: hamburger menu em mobile, nav horizontal em desktop
- Fontes: usar `clamp()` para tipografia fluida
  ```css
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  ```
- Imagens e SVGs: `width: 100%; height: auto;`

### Acessibilidade (a11y) — PRIORIDADE MÁXIMA
- Contraste mínimo WCAG AA (4.5:1 para texto normal, 3:1 para texto grande)
- Todas as imagens com `alt` descritivo
- Formulários com `label` associado via `for`
- Estados de foco visíveis (`:focus-visible` com outline)
- Navegação por teclado funcional
- `aria-label` em ícones sem texto
- Preferência de movimento reduzido: `@media (prefers-reduced-motion: reduce)`

#### Libras (Língua Brasileira de Sinais) — OBRIGATÓRIO
O Brasil tem aproximadamente 10 milhões de pessoas surdas ou com deficiência auditiva.
O OctoWage DEVE incluir suporte a Libras via **VLibras** (ferramenta gratuita do Governo Federal).

**Integração do VLibras Widget** (adicionar antes do `</body>` no base.html):
```html
<div vw class="enabled">
  <div vw-access-button class="active"></div>
  <div vw-plugin-wrapper>
    <div class="vw-plugin-top-wrapper"></div>
  </div>
</div>
<script src="https://vlibras.gov.br/app/vlibras-plugin.js"></script>
<script>
  new window.VLibras.Widget({ position: 'R', avatar: 'icaro' });
</script>
```

**Regras para compatibilidade com VLibras:**
- Textos devem ser claros e diretos (o VLibras traduz texto para Libras automaticamente)
- Evitar siglas sem expansão (usar `<abbr title="Teto Constitucional">TC</abbr>`)
- Evitar textos em imagens — todo conteúdo textual deve estar no HTML
- Tooltips e títulos de gráficos devem estar em texto, não só em SVG
- O botão do VLibras (canto inferior direito) não deve ser coberto por outros elementos

### Paleta de Cores
```css
:root {
  /* Primárias */
  --color-primary: #1B2838;       /* Azul marinho escuro — confiança */
  --color-primary-light: #2E86AB; /* Azul médio — interativo */
  --color-accent: #E8651A;        /* Laranja — destaque/alerta */
  --color-accent-light: #F59E0B;  /* Amarelo — warning */

  /* Semânticas */
  --color-success: #10B981;       /* Verde — dentro do teto */
  --color-danger: #EF4444;        /* Vermelho — acima do teto */
  --color-warning: #F59E0B;       /* Amarelo — atenção */

  /* Neutras */
  --color-bg: #F8FAFC;            /* Fundo claro */
  --color-surface: #FFFFFF;       /* Cards */
  --color-text: #1E293B;          /* Texto principal */
  --color-text-muted: #64748B;    /* Texto secundário */
  --color-border: #E2E8F0;        /* Bordas */

  /* Dark mode (futuro) */
  --color-bg-dark: #0F172A;
  --color-surface-dark: #1E293B;
  --color-text-dark: #F1F5F9;
}
```

### Tipografia
- Font stack: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Carregar Inter via Google Fonts (variável weight)
- Hierarquia:
  - H1: `clamp(1.75rem, 4vw, 2.5rem)` — bold
  - H2: `clamp(1.25rem, 3vw, 1.75rem)` — semibold
  - H3: `clamp(1.1rem, 2.5vw, 1.375rem)` — semibold
  - Body: `clamp(0.875rem, 2vw, 1rem)` — regular
  - Small: `clamp(0.75rem, 1.5vw, 0.875rem)` — regular

### Componentes UI

#### Cards de Dados
- Border-radius: 12px
- Sombra sutil: `0 1px 3px rgba(0,0,0,0.1)`
- Padding: 16px mobile, 24px desktop
- Hover: elevar sombra (`0 4px 12px rgba(0,0,0,0.15)`)

#### Barras de Comparação (Feature principal)
- Barras horizontais proporcionais
- Cor verde para "dentro do teto", vermelho para "acima do teto"
- Linha vertical tracejada marcando o teto constitucional
- Labels com valor em R$ e percentual vs teto
- Animação de preenchimento ao entrar no viewport

#### Gráficos
- Cores consistentes com a paleta
- Sempre incluir título e subtítulo descritivo
- Tooltip claro com formatação de moeda brasileira
- Responsivo (resize automático)
- Opção de download (PNG/SVG)
- Legenda fora do gráfico em mobile

#### Loading States (HTMX)
- Usar `hx-indicator` SEMPRE
- Spinner do OctoWage (polvo girando) para loads > 500ms
- Skeleton screens para conteúdo principal (não usar spinners para tudo)
- Transições suaves: `transition: opacity 0.3s ease;`

#### Empty States
- Sempre ter um estado vazio amigável com ilustração
- Texto guiando o próximo passo ("Selecione um estado para começar")
- Nunca mostrar tela em branco ou mensagem técnica de erro

#### Feedback Visual
- Toast notifications para ações (copiar link, download)
- Cores semânticas (verde=sucesso, vermelho=erro, amarelo=aviso)
- Animações sutis (não usar animações pesadas ou distrativas)

### Micro-interações
- Botões: efeito ripple sutil no clique
- Cards: leve elevação no hover (desktop)
- Números: animação de contagem ao aparecer (`countUp.js`)
- Gráficos: animação de entrada (draw-in para linhas, grow para barras)
- Transições HTMX: `htmx.config.defaultSwapStyle = 'innerHTML transition:true'`

### Performance Frontend
- HTMX: ~14KB (único JS obrigatório)
- Plotly: carregar lazy (só quando gráfico entrar no viewport)
- Imagens: WebP com fallback, lazy loading nativo (`loading="lazy"`)
- CSS: inline critical CSS, carregar resto async
- Meta viewport: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Não usar jQuery, não usar Bootstrap JS

### SEO e Compartilhamento
- Cada página de comparação deve ter URL única e descritiva
  ```
  /comparar/juiz-vs-professor?estado=PE
  /raio-x/tjsp/2025/12
  ```
- Meta tags Open Graph para compartilhamento em redes sociais
- Twitter Card com preview visual (imagem dinâmica do gráfico)
- Structured Data (JSON-LD) para dados salariais
- `hx-push-url="true"` em todos os filtros para manter URL atualizada

---

## Arquitetura de Pastas

```
app/
├── main.py
├── config.py
├── core/           # Cache, DB, segurança
├── models/         # SQLAlchemy
├── services/       # Lógica de negócio
├── routes/
│   ├── pages.py    # Rotas SSR (Jinja2)
│   └── fragments.py # Fragmentos HTMX
├── middleware/
├── templates/
│   ├── base.html
│   ├── components/ # Componentes reutilizáveis (header, footer, cards)
│   ├── pages/
│   └── fragments/
static/
├── css/
│   ├── variables.css    # Custom properties
│   ├── base.css         # Reset + tipografia
│   ├── components.css   # Cards, botões, tabelas
│   ├── layouts.css      # Grid, container
│   └── responsive.css   # Media queries
├── js/
│   ├── htmx.min.js
│   └── charts.js        # Helpers para Plotly/Chart.js
└── img/
    ├── octowage-logo.svg
    └── octowage-spinner.svg
etl/                # Pipeline de dados
tests/
```

---

## Convenções de Commit

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação (sem mudança de lógica)
refactor: refatoração
test: testes
chore: manutenção (deps, config)
data: atualização de dados/ETL
```

Exemplo: `feat: adiciona comparador cross-setor juiz vs professor`

---

## Regras de Negócio Críticas

1. **NUNCA inventar dados** — usar apenas fontes oficiais documentadas
2. **NUNCA exibir agregações com amostra < 10** — suprimir por privacidade
3. **SEMPRE citar a fonte** — rodapé de cada visualização com link para fonte original
4. **SEMPRE diferenciar** salário bruto vs líquido vs real (ajustado por inflação)
5. **SEMPRE incluir nota metodológica** acessível em cada página
6. **Teto constitucional**: R$ 46.366,19 (atualizar quando mudar)
7. **Dados do DadosJusBr**: consumir via API, não copiar/redistribuir base completa
8. **Portal da Transparência**: requer chave API (armazenar em .env, NUNCA commitar)
9. **NUNCA exibir dados sensíveis** — CPF, endereço, telefone, dados bancários, dados de saúde (STF Tema 483 limita a: nome + cargo + remuneração)
10. **NUNCA editoralizar sobre servidores individuais** — deixar os números falarem, sem juízos de valor sobre pessoas específicas
11. **SEMPRE incluir disclaimer** em cada página: fonte oficial + data de referência + aviso de que não há vinculação governamental
12. **Preferir APIs oficiais** sobre web scraping (mitigação de risco LGPD/ANPD)
13. **Manter registros de coleta** — data/hora de cada extração com fonte, para rastreabilidade em caso de contestação

---

## Proteção Legal e LGPD

### Fundamento jurídico
O OctoWage se ampara em: LAI (Lei 12.527/2011, Art. 8º), STF Tema 483 (ARE 652.777/SP), e princípios da publicidade e transparência (CF, Art. 37). Consultar `docs/LEGAL_ANALYSIS_v1.0.md` para análise completa.

### Requisitos legais do projeto
1. **Termos de Uso** — devem existir antes do lançamento público
2. **Política de Privacidade** — LGPD-compliant, com base legal para cada tratamento
3. **Nota Metodológica** — acessível em cada página de dados
4. **Canal de contato** — e-mail dedicado para questões jurídicas/LGPD
5. **Encarregado de Dados (DPO)** — designar formalmente antes do lançamento
6. **Logs de acesso** — manter por 6 meses (Marco Civil, Art. 15)

### Bases legais aplicáveis (LGPD Art. 7º)
- **Art. 7º, IX** — Legítimo interesse (controle social e transparência)
- **Art. 7º, V** — Execução de políticas públicas (se houver parceria governamental)

### Regras técnicas com implicação legal
- Implementar cache para minimizar requisições às APIs oficiais
- Respeitar robots.txt dos portais governamentais
- Rate limiting em toda coleta automatizada
- HTTPS obrigatório em produção
- Backup das fontes originais com timestamps (prova de fonte)

---

## Internacionalização (i18n)

### Estratégia: pt-BR primeiro, inglês como segundo idioma
O OctoWage nasce em português brasileiro, mas deve suportar inglês para alcançar pesquisadores e jornalistas internacionais interessados em transparência salarial.

### Stack de i18n
- **gettext** + **Babel** para extração e compilação de traduções
- **Jinja2 i18n extension** (integrado) para templates
- **fastapi-babel** ou middleware customizado para detectar idioma

### Regras
1. **Strings no código**: usar `_("texto")` para todas as strings visíveis ao usuário
2. **Templates Jinja2**: usar `{{ _("texto") }}` ou `{% trans %}bloco{% endtrans %}`
3. **Arquivos de tradução**: `locales/pt_BR/LC_MESSAGES/messages.po` e `locales/en/LC_MESSAGES/messages.po`
4. **Detecção de idioma** (prioridade):
   - Query param: `?lang=en`
   - Cookie: `octowage_lang`
   - Header: `Accept-Language`
   - Fallback: `pt-BR`
5. **Seletor de idioma**: bandeira BR/US no header, persiste via cookie
6. **Valores monetários**: sempre em R$ (Real) — NÃO converter para USD
7. **Nomes de cargos**: manter original em português com tradução entre parênteses
   - Ex: "Juiz (Judge)" / "Professor (Teacher)"
8. **URLs**: não traduzir slugs de URL (manter `/comparar/`, `/sobre/` etc.)

### Fluxo de tradução
```bash
# Extrair strings
pybabel extract -F babel.cfg -o messages.pot .

# Iniciar idioma
pybabel init -i messages.pot -d locales -l en

# Atualizar traduções existentes
pybabel update -i messages.pot -d locales

# Compilar
pybabel compile -d locales
```

---

## Ecossistema e Projetos Relacionados

### Filosofia: Não reinventar a roda
O OctoWage se posiciona como COMPLEMENTO, não concorrente, de ferramentas existentes. O diferencial é a **comparação cross-setor** e a **tradução para o cidadão comum**.

### Projetos do ecossistema

| Projeto | O que faz | Como o OctoWage se relaciona |
|---------|-----------|------------------------------|
| **DadosJusBr** (dadosjusbr.org) | Padroniza remuneração do Judiciário/MP | Fonte primária de dados — consumir via API |
| **ExtraTeto** (github.com/andredutraf/extrateto) | Rankings e mapas de calor de magistrados | Linkar para DadosJusBr.org (ExtraTeto não tem deploy público) |
| **Portal da Transparência** | Dados do Executivo Federal | Fonte complementar via API (requer chave) |
| **República.org** | Benchmark internacional de supersalários | Referência para comparações internacionais |
| **OctoMask** (github.com/BrunnoML/OctoMask) | Anonimização de textos | Futuro: integrar para crowdsourcing seguro |

### Regras de referência
1. **NUNCA duplicar** funcionalidades que já existem em ferramentas especializadas
2. Para rankings de magistrados → direcionar para **DadosJusBr.org** (tem interface pública acessível)
3. Para dados do Executivo → usar API do **Portal da Transparência**
4. **SEMPRE creditar** projetos referenciados com link e nome
5. O diferencial do OctoWage é a **visão cross-setor** (comparar juiz vs professor vs enfermeiro vs PM)
6. Manter seção "Ecossistema" na página Sobre com links para projetos parceiros

---

## Documentação do Projeto

- `docs/ARCHITECTURE_v1.0.md` — Arquitetura técnica completa
- `docs/RESEARCH_supersalarios_v1.0.md` — Pesquisa sobre supersalários
- `docs/API_VALIDATION_v1.0.md` — Validação das fontes de dados
- `docs/COMPETITIVE_ANALYSIS_v1.0.md` — Análise competitiva e diferenciais
- `docs/LEGAL_ANALYSIS_v1.0.md` — Análise jurídica, LGPD e proteção legal
- `CLAUDE.md` — Este arquivo (instruções para o Claude)

---

*Última atualização: 2026-02-26*
