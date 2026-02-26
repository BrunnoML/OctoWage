"""Rotas de páginas completas (SSR com Jinja2)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.exchange_rate import get_international_with_live_rates
from app.services.salary_data import (
    CAREERS,
    CUSTO_SOCIAL,
    CUSTO_SUPERSALARIOS_ANUAL,
    SERVIDORES_ACIMA_TETO,
    TETO_CONSTITUCIONAL,
    get_all_careers_sorted,
    get_career,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial com visão geral da desigualdade."""
    careers = get_all_careers_sorted()
    international, exchange_rates = await get_international_with_live_rates()
    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "careers": careers,
            "teto": TETO_CONSTITUCIONAL,
            "custo_anual": CUSTO_SUPERSALARIOS_ANUAL,
            "servidores_acima": SERVIDORES_ACIMA_TETO,
            "custo_social": CUSTO_SOCIAL,
            "international": international,
            "exchange_rates": exchange_rates,
            "page_title": "OctoWage — Transparência Salarial",
            "page_description": "Visualize a desigualdade salarial no setor público brasileiro. Compare supersalários com pisos de professores, enfermeiros e policiais.",
        },
    )


@router.get("/comparar/{career1_id}-vs-{career2_id}", response_class=HTMLResponse)
async def compare(request: Request, career1_id: str, career2_id: str):
    """Página de comparação entre duas carreiras."""
    c1 = get_career(career1_id)
    c2 = get_career(career2_id)

    if not c1 or not c2:
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "message": "Carreira não encontrada."},
            status_code=404,
        )

    return templates.TemplateResponse(
        "pages/compare.html",
        {
            "request": request,
            "career1": c1,
            "career2": c2,
            "teto": TETO_CONSTITUCIONAL,
            "page_title": f"{c1.name} vs {c2.name} — OctoWage",
            "page_description": f"Compare salários: {c1.name} (R$ {c1.salary_real:,.0f}) vs {c2.name} (R$ {c2.salary_real:,.0f})",
        },
    )


@router.get("/sobre", response_class=HTMLResponse)
async def about(request: Request):
    """Página sobre o projeto e metodologia."""
    return templates.TemplateResponse(
        "pages/about.html",
        {
            "request": request,
            "page_title": "Sobre — OctoWage",
            "page_description": "Conheça o OctoWage: metodologia, fontes de dados e como contribuir.",
        },
    )
