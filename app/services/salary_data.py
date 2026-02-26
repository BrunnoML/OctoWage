"""Dados salariais para o MVP — fonte estática baseada em fontes oficiais.

Na fase de MVP, usamos dados validados de fontes oficiais como constantes.
Na fase 2, esses dados virão da API do DadosJusBr e Portal da Transparência.

Fontes:
- Teto constitucional: CF Art. 37, XI (R$ 46.366,19)
- Magistrados: DadosJusBr / Mov. Pessoas à Frente (2025)
- Piso professor: Portaria MEC nº 82/2026 (R$ 5.130,63)
- Piso enfermeiro: Lei 14.434/2022 (R$ 4.750,00)
- Policiais: Tabelas remuneratórias federais/estaduais (2025)
"""

from dataclasses import dataclass, field


@dataclass
class RiskAssessment:
    """Avaliação de risco ocupacional com critérios objetivos e auditáveis.

    Metodologia OctoWage v1.0 — baseada em 4 indicadores com fontes oficiais:

    1. Adicional legal (periculosidade/insalubridade):
       - Tem direito a adicional de periculosidade (30%)? → +2 pontos
       - Tem direito a adicional de insalubridade (10-40%)? → +1 ponto
       - Sem adicional legal → 0 pontos
       Fonte: CLT Art. 193-195, NR-15, NR-16, jurisprudência TST/STJ

    2. Mortalidade em serviço:
       - Alta (dados FBSP: policiais ~170 mortes violentas/ano em ~800 mil efetivo) → +3 pontos
       - Moderada (enfermagem: exposição biológica, NR-15 Anexo 14) → +1 ponto
       - Baixa (sem registro significativo de mortes em serviço) → 0 pontos
       Fonte: FBSP 19º Anuário (2025), COFEN, COREN

    3. Exposição a violência/agentes nocivos:
       - Contato direto com armas de fogo / confronto → +2 pontos
       - Exposição a agentes biológicos/químicos → +1 ponto
       - Ambiente controlado (escritório/gabinete) → 0 pontos
       Fonte: NR-15, NR-16, regulamentos das carreiras

    4. Jornada e condições:
       - Escala 12x36 ou plantão noturno regular → +1 ponto
       - Jornada regular diurna → 0 pontos
       Fonte: CLT, estatutos das carreiras

    Classificação final (soma dos pontos):
    - 0-1: Baixo
    - 2-3: Médio
    - 4-5: Alto
    - 6+: Muito Alto
    """

    adicional_legal: int  # 0, 1 ou 2
    mortalidade: int  # 0, 1 ou 3
    exposicao_violencia: int  # 0, 1 ou 2
    jornada_condicoes: int  # 0 ou 1
    justificativa: str  # Explicação em texto
    fontes: list[dict[str, str]]  # Lista de fontes: [{"nome": "...", "url": "..."}]

    @property
    def score(self) -> int:
        """Pontuação total de risco."""
        return self.adicional_legal + self.mortalidade + self.exposicao_violencia + self.jornada_condicoes

    @property
    def level(self) -> str:
        """Nível de risco baseado na pontuação."""
        s = self.score
        if s <= 1:
            return "baixo"
        elif s <= 3:
            return "medio"
        elif s <= 5:
            return "alto"
        else:
            return "muito_alto"

    @property
    def level_display(self) -> str:
        """Nível de risco formatado para exibição."""
        labels = {
            "baixo": "Baixo",
            "medio": "Médio",
            "alto": "Alto",
            "muito_alto": "Muito Alto",
        }
        return labels.get(self.level, self.level)


@dataclass
class CareerData:
    """Dados de uma carreira pública."""

    id: str
    name: str
    category: str  # 'essencial', 'seguranca', 'justica', 'legislativo'
    salary_base: float  # Subsídio/piso base
    salary_real: float  # Remuneração média real (com penduricalhos se aplicável)
    salary_max: float | None  # Teto prático observado
    penduricalhos: float  # Valor médio de penduricalhos/indenizações
    source: str  # Fonte oficial
    source_url: str
    education: str  # Formação exigida
    weekly_hours: int
    risk_assessment: RiskAssessment  # Avaliação de risco com metodologia
    color: str  # Cor para gráficos

    @property
    def risk_level(self) -> str:
        """Nível de risco (compatibilidade com templates existentes)."""
        return self.risk_assessment.level


# Dados do MVP — validados com fontes oficiais (2025/2026)
CAREERS: list[CareerData] = [
    # ── CARREIRAS ESSENCIAIS ──
    CareerData(
        id="professor",
        name="Professor (Ed. Básica)",
        category="essencial",
        salary_base=5130.63,
        salary_real=5130.63,
        salary_max=12000.00,
        penduricalhos=0,
        source="Portaria MEC nº 82/2026",
        source_url="https://www.gov.br/mec/pt-br/assuntos/noticias/2026/janeiro/piso-nacional-do-magisterio-e-fixado-em-r-5-1-mil",
        education="Licenciatura",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=0,  # Sem adicional por padrão
            mortalidade=0,  # Sem registro significativo de mortes em serviço
            exposicao_violencia=1,  # Violência escolar crescente (FBSP registra agressões)
            jornada_condicoes=0,  # Jornada diurna regular
            justificativa=(
                "Sem adicional de periculosidade/insalubridade por padrão. "
                "Exposição a violência escolar reconhecida em jurisprudência do TJDFT "
                "(adicional de insalubridade em unidades de internação). "
                "Score 1 = Baixo, mas próximo de Médio."
            ),
            fontes=[
                {"nome": "FBSP 19º Anuário 2025 — violência nas escolas", "url": "https://forumseguranca.org.br/wp-content/uploads/2025/07/anuario-2025.pdf"},
                {"nome": "TJDFT — Professor em unidade de internação", "url": "https://www.tjdft.jus.br"},
            ],
        ),
        color="#3B82F6",
    ),
    CareerData(
        id="enfermeiro",
        name="Enfermeiro(a)",
        category="essencial",
        salary_base=4750.00,
        salary_real=4750.00,
        salary_max=8000.00,
        penduricalhos=0,
        source="Lei 14.434/2022",
        source_url="https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14434.htm",
        education="Bacharelado em Enfermagem",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=1,  # Insalubridade grau máximo (40%) — NR-15 Anexo 14
            mortalidade=1,  # Exposição biológica (COVID, hepatite, tuberculose)
            exposicao_violencia=1,  # Agentes biológicos (NR-15 Anexo 14)
            jornada_condicoes=1,  # Plantão 12x36, noturno
            justificativa=(
                "Adicional de insalubridade grau máximo (40%) reconhecido judicialmente "
                "(TJSP, COFEN). Exposição permanente a agentes biológicos (NR-15, Anexo 14). "
                "Jornada inclui plantões 12x36 e noturnos. Score 4 = Alto."
            ),
            fontes=[
                {"nome": "NR-15 Anexo 14 — Agentes biológicos", "url": "https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-15-nr-15"},
                {"nome": "COFEN — Insalubridade para enfermagem", "url": "https://www.cofen.gov.br"},
            ],
        ),
        color="#8B5CF6",
    ),
    # ── SEGURANÇA PÚBLICA ──
    CareerData(
        id="soldado_pm",
        name="Soldado PM",
        category="seguranca",
        salary_base=6358.00,
        salary_real=6358.00,
        salary_max=10000.00,
        penduricalhos=0,
        source="Média nacional (SENASP/MJSP)",
        source_url="https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica",
        education="Ensino Médio + Curso de Formação",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=2,  # Periculosidade (porte de arma, NR-16)
            mortalidade=3,  # ~170 policiais assassinados/ano (FBSP 2025)
            exposicao_violencia=2,  # Confronto armado direto
            jornada_condicoes=1,  # Escala 12x36, plantões
            justificativa=(
                "Adicional de periculosidade (30%) por porte de arma de fogo e risco de morte. "
                "FBSP 19º Anuário (2025): ~170 mortes violentas de policiais/ano + 126 suicídios. "
                "Confronto armado é parte da rotina operacional. Score 8 = Muito Alto."
            ),
            fontes=[
                {"nome": "FBSP 19º Anuário 2025 — policiais mortos", "url": "https://forumseguranca.org.br/wp-content/uploads/2025/07/anuario-2025.pdf"},
                {"nome": "NR-16 — Atividades periculosas", "url": "https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-16-nr-16"},
                {"nome": "CLT Art. 193 — Periculosidade", "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm#art193"},
            ],
        ),
        color="#06B6D4",
    ),
    CareerData(
        id="agente_pf",
        name="Agente PF",
        category="seguranca",
        salary_base=14164.00,
        salary_real=14164.00,
        salary_max=21000.00,
        penduricalhos=0,
        source="Lei 13.371/2016 + Lei 14.875/2024",
        source_url="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13371.htm",
        education="Bacharelado (qualquer área)",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=2,  # Periculosidade (porte de arma, operações)
            mortalidade=3,  # Operações de alto risco (narcotráfico, fronteira)
            exposicao_violencia=2,  # Confronto armado em operações
            jornada_condicoes=1,  # Operações fora de horário, plantões
            justificativa=(
                "Adicional de periculosidade por porte de arma e operações de campo. "
                "Atua em operações contra narcotráfico, contrabando e crime organizado. "
                "Mesma taxa de mortalidade que PM estadual proporcionalmente. Score 8 = Muito Alto."
            ),
            fontes=[
                {"nome": "FBSP 19º Anuário 2025 — mortalidade policial", "url": "https://forumseguranca.org.br/wp-content/uploads/2025/07/anuario-2025.pdf"},
                {"nome": "Lei 13.371/2016 — Remuneração PF", "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13371.htm"},
                {"nome": "NR-16 — Periculosidade", "url": "https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-16-nr-16"},
            ],
        ),
        color="#0EA5E9",
    ),
    CareerData(
        id="delegado_pf",
        name="Delegado PF",
        category="seguranca",
        salary_base=26800.00,
        salary_real=26800.00,
        salary_max=41350.00,
        penduricalhos=0,
        source="Lei 13.371/2016 + Lei 14.875/2024",
        source_url="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13371.htm",
        education="Bacharelado em Direito",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=2,  # Periculosidade (porte de arma, operações)
            mortalidade=1,  # Menor exposição direta que agentes, mas presente
            exposicao_violencia=1,  # Coordena operações, menor exposição direta
            jornada_condicoes=1,  # Plantões e operações fora de horário
            justificativa=(
                "Adicional de periculosidade por porte de arma. Coordena operações de campo "
                "com menor exposição direta a confronto que agentes. "
                "Menor mortalidade proporcional. Score 5 = Alto."
            ),
            fontes=[
                {"nome": "Lei 13.371/2016 — Remuneração PF", "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13371.htm"},
                {"nome": "NR-16 — Periculosidade", "url": "https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-16-nr-16"},
            ],
        ),
        color="#2563EB",
    ),
    CareerData(
        id="agente_pc",
        name="Agente PC (média)",
        category="seguranca",
        salary_base=7200.00,
        salary_real=7200.00,
        salary_max=13000.00,
        penduricalhos=0,
        source="Média estadual (SENASP/MJSP 2025)",
        source_url="https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica",
        education="Bacharelado (qualquer área na maioria dos estados)",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=2,  # Periculosidade (porte de arma)
            mortalidade=3,  # FBSP: policiais civis inclusos nas ~170 mortes/ano
            exposicao_violencia=2,  # Diligências, mandados, confronto
            jornada_condicoes=1,  # Plantões
            justificativa=(
                "Adicional de periculosidade por porte de arma e atividade de campo. "
                "Agentes de PC realizam diligências, cumprimento de mandados e atuam "
                "em flagrantes com risco de confronto. Inclusos na estatística de mortes "
                "violentas do FBSP. Score 8 = Muito Alto."
            ),
            fontes=[
                {"nome": "FBSP 19º Anuário 2025 — mortalidade policial", "url": "https://forumseguranca.org.br/wp-content/uploads/2025/07/anuario-2025.pdf"},
                {"nome": "NR-16 — Periculosidade", "url": "https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-16-nr-16"},
            ],
        ),
        color="#7C3AED",
    ),
    CareerData(
        id="delegado_pc",
        name="Delegado PC (média)",
        category="seguranca",
        salary_base=22000.00,
        salary_real=22000.00,
        salary_max=35000.00,
        penduricalhos=0,
        source="Média estadual (SENASP/MJSP 2025)",
        source_url="https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica",
        education="Bacharelado em Direito",
        weekly_hours=40,
        risk_assessment=RiskAssessment(
            adicional_legal=2,  # Periculosidade (porte de arma)
            mortalidade=1,  # Menor exposição direta que agentes
            exposicao_violencia=1,  # Coordena investigações, menos campo
            jornada_condicoes=1,  # Plantões
            justificativa=(
                "Adicional de periculosidade por porte de arma. Coordena investigações "
                "com menor exposição direta a campo que agentes/investigadores. "
                "Score 5 = Alto."
            ),
            fontes=[
                {"nome": "NR-16 — Periculosidade", "url": "https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-16-nr-16"},
            ],
        ),
        color="#6D28D9",
    ),
    # ── JUSTIÇA ──
    CareerData(
        id="juiz_media",
        name="Juiz (média nacional)",
        category="justica",
        salary_base=35462.00,
        salary_real=81500.00,
        salary_max=200000.00,
        penduricalhos=46038.00,
        source="DadosJusBr / Mov. Pessoas à Frente (2025)",
        source_url="https://dadosjusbr.org",
        education="Bacharelado em Direito + 3 anos exp.",
        weekly_hours=35,
        risk_assessment=RiskAssessment(
            adicional_legal=0,  # Sem adicional de periculosidade/insalubridade
            mortalidade=0,  # Sem registro significativo de mortes em serviço
            exposicao_violencia=0,  # Ambiente de gabinete com segurança
            jornada_condicoes=0,  # Jornada diurna, sem plantão obrigatório
            justificativa=(
                "Sem adicional de periculosidade ou insalubridade. Ambiente de trabalho "
                "em gabinete com segurança institucional. Sem registro expressivo de "
                "mortes em serviço. Score 0 = Baixo."
            ),
            fontes=[
                {"nome": "LOMAN (LC 35/1979) — Estatuto da Magistratura", "url": "https://www.planalto.gov.br/ccivil_03/Leis/LCP/Lcp35.htm"},
                {"nome": "CNJ — Dados sobre a magistratura", "url": "https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/"},
            ],
        ),
        color="#EF4444",
    ),
    CareerData(
        id="juiz_tjsp",
        name="Juiz (TJSP)",
        category="justica",
        salary_base=35462.00,
        salary_real=122800.00,
        salary_max=300000.00,
        penduricalhos=87338.00,
        source="DadosJusBr / Mov. Pessoas à Frente (2025)",
        source_url="https://dadosjusbr.org",
        education="Bacharelado em Direito + 3 anos exp.",
        weekly_hours=35,
        risk_assessment=RiskAssessment(
            adicional_legal=0,
            mortalidade=0,
            exposicao_violencia=0,
            jornada_condicoes=0,
            justificativa=(
                "Mesmo perfil de risco do juiz médio nacional. Ambiente de gabinete "
                "com segurança institucional do TJSP. Score 0 = Baixo."
            ),
            fontes=[
                {"nome": "LOMAN (LC 35/1979)", "url": "https://www.planalto.gov.br/ccivil_03/Leis/LCP/Lcp35.htm"},
                {"nome": "CNJ — Justiça em Números", "url": "https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/"},
            ],
        ),
        color="#DC2626",
    ),
    CareerData(
        id="procurador_mp",
        name="Procurador MP",
        category="justica",
        salary_base=35462.00,
        salary_real=73000.00,
        salary_max=180000.00,
        penduricalhos=37538.00,
        source="DadosJusBr (2025)",
        source_url="https://dadosjusbr.org",
        education="Bacharelado em Direito + 3 anos exp.",
        weekly_hours=35,
        risk_assessment=RiskAssessment(
            adicional_legal=0,  # Sem adicional
            mortalidade=0,  # Sem registro significativo
            exposicao_violencia=0,  # Ambiente de gabinete
            jornada_condicoes=0,  # Jornada diurna
            justificativa=(
                "Sem adicional de periculosidade ou insalubridade. Atuação predominantemente "
                "em gabinete. Procuradores do GAECO/operações especiais teriam score diferente, "
                "mas usamos o perfil médio. Score 0 = Baixo."
            ),
            fontes=[
                {"nome": "LONMP (Lei 8.625/1993) — Lei Orgânica do MP", "url": "https://www.planalto.gov.br/ccivil_03/leis/l8625.htm"},
                {"nome": "CNMP — Dados sobre o Ministério Público", "url": "https://www.cnmp.mp.br/portal/institucional/476-portal-transparencia"},
            ],
        ),
        color="#F97316",
    ),
]

# Teto constitucional
TETO_CONSTITUCIONAL: float = 46366.19

# Custo total dos supersalários
CUSTO_SUPERSALARIOS_ANUAL: float = 20_000_000_000.00  # R$ 20 bilhões
SERVIDORES_ACIMA_TETO: int = 53_000

# Dados para a calculadora "O Custo da Desigualdade"
CUSTO_SOCIAL: dict[str, dict] = {
    "professores": {
        "label": "professores com piso",
        "piso": 5130.63,
        "total_possivel": int(CUSTO_SUPERSALARIOS_ANUAL / (5130.63 * 13)),  # 13 salários
    },
    "enfermeiros": {
        "label": "enfermeiros com piso",
        "piso": 4750.00,
        "total_possivel": int(CUSTO_SUPERSALARIOS_ANUAL / (4750.00 * 13)),
    },
    "soldados_pm": {
        "label": "soldados PM",
        "piso": 6358.00,
        "total_possivel": int(CUSTO_SUPERSALARIOS_ANUAL / (6358.00 * 13)),
    },
    "bolsas_universidade": {
        "label": "bolsas universitárias integrais (R$ 1.200/mês)",
        "piso": 1200.00,
        "total_possivel": int(CUSTO_SUPERSALARIOS_ANUAL / (1200.00 * 12)),
    },
}



def get_career(career_id: str) -> CareerData | None:
    """Retorna dados de uma carreira pelo ID."""
    for c in CAREERS:
        if c.id == career_id:
            return c
    return None


def get_careers_by_category(category: str) -> list[CareerData]:
    """Retorna carreiras filtradas por categoria."""
    return [c for c in CAREERS if c.category == category]


def get_all_careers_sorted() -> list[CareerData]:
    """Retorna todas as carreiras ordenadas por salário real (crescente)."""
    return sorted(CAREERS, key=lambda c: c.salary_real)
