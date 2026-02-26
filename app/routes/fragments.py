"""Rotas de fragmentos HTMX — retornam pedaços de HTML, não páginas completas."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.salary_data import (
    CAREERS,
    CUSTO_SOCIAL,
    CUSTO_SUPERSALARIOS_ANUAL,
    TETO_CONSTITUCIONAL,
    get_all_careers_sorted,
    get_career,
    get_careers_by_category,
)

router = APIRouter(prefix="/api/fragment")
templates = Jinja2Templates(directory="app/templates")


@router.get("/comparison-bars", response_class=HTMLResponse)
async def comparison_bars(request: Request, sort: str = "salary"):
    """Fragmento: barras de comparação salarial."""
    if sort == "salary":
        careers = get_all_careers_sorted()
    elif sort == "gap":
        careers = sorted(CAREERS, key=lambda c: c.penduricalhos, reverse=True)
    else:
        careers = get_all_careers_sorted()

    return templates.TemplateResponse(
        "fragments/comparison_bars.html",
        {
            "request": request,
            "careers": careers,
            "teto": TETO_CONSTITUCIONAL,
            "max_salary": max(c.salary_real for c in careers),
        },
    )


@router.get("/career-detail/{career_id}", response_class=HTMLResponse)
async def career_detail(request: Request, career_id: str):
    """Fragmento: detalhamento de uma carreira (raio-x do contracheque)."""
    career = get_career(career_id)
    if not career:
        return HTMLResponse("<p class='error'>Carreira não encontrada.</p>", status_code=404)

    return templates.TemplateResponse(
        "fragments/career_detail.html",
        {
            "request": request,
            "career": career,
            "teto": TETO_CONSTITUCIONAL,
            "above_teto": max(0, career.salary_real - TETO_CONSTITUCIONAL),
            "pct_above": (
                ((career.salary_real - TETO_CONSTITUCIONAL) / TETO_CONSTITUCIONAL * 100)
                if career.salary_real > TETO_CONSTITUCIONAL
                else 0
            ),
        },
    )


@router.get("/cost-calculator", response_class=HTMLResponse)
async def cost_calculator(request: Request):
    """Fragmento: calculadora 'O Custo da Desigualdade'."""
    return templates.TemplateResponse(
        "fragments/cost_calculator.html",
        {
            "request": request,
            "custo_anual": CUSTO_SUPERSALARIOS_ANUAL,
            "custo_social": CUSTO_SOCIAL,
        },
    )
