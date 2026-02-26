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

from dataclasses import dataclass


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
    risk_level: str  # 'baixo', 'medio', 'alto', 'muito_alto'
    color: str  # Cor para gráficos


# Dados do MVP — validados com fontes oficiais (2025/2026)
CAREERS: list[CareerData] = [
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
        risk_level="medio",
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
        risk_level="alto",
        color="#8B5CF6",
    ),
    CareerData(
        id="soldado_pm",
        name="Soldado PM",
        category="seguranca",
        salary_base=6358.00,
        salary_real=6358.00,
        salary_max=10000.00,
        penduricalhos=0,
        source="Média nacional (SENASP/MJSP)",
        source_url="https://www.gov.br/mj/pt-br/assuntos/sua-seguranca",
        education="Ensino Médio + Curso de Formação",
        weekly_hours=40,
        risk_level="muito_alto",
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
        source="Lei 13.333/2016 (reajuste 2025)",
        source_url="https://www.gov.br/pf/pt-br",
        education="Bacharelado (qualquer área)",
        weekly_hours=40,
        risk_level="muito_alto",
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
        source="Lei 13.333/2016 (reajuste 2025)",
        source_url="https://www.gov.br/pf/pt-br",
        education="Bacharelado em Direito",
        weekly_hours=40,
        risk_level="alto",
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
        source_url="https://www.gov.br/mj/pt-br/assuntos/sua-seguranca",
        education="Bacharelado (qualquer área na maioria dos estados)",
        weekly_hours=40,
        risk_level="muito_alto",
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
        source_url="https://www.gov.br/mj/pt-br/assuntos/sua-seguranca",
        education="Bacharelado em Direito",
        weekly_hours=40,
        risk_level="alto",
        color="#6D28D9",
    ),
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
        risk_level="baixo",
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
        risk_level="baixo",
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
        risk_level="baixo",
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
