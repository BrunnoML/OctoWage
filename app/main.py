"""OctoWage — Ponto de entrada da aplicação FastAPI."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import fragments, pages

settings = get_settings()


def format_brl(value: float, decimals: int = 2) -> str:
    """Formata número no padrão brasileiro: 1.234,56"""
    if decimals == 0:
        formatted = f"{value:,.0f}"
    else:
        formatted = f"{value:,.{decimals}f}"
    # Troca padrão americano (1,234.56) para brasileiro (1.234,56)
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


def format_brl_int(value: int | float) -> str:
    """Formata inteiro no padrão brasileiro: 53.000"""
    return f"{int(value):,}".replace(",", ".")


def create_app() -> FastAPI:
    """Factory da aplicação FastAPI."""
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version="0.1.0",
        docs_url="/docs" if settings.app_debug else None,
        redoc_url=None,
    )

    # Static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Filtros Jinja2 para formatação brasileira
    pages.templates.env.filters["brl"] = format_brl
    pages.templates.env.filters["brl_int"] = format_brl_int
    fragments.templates.env.filters["brl"] = format_brl
    fragments.templates.env.filters["brl_int"] = format_brl_int

    # Rotas
    app.include_router(pages.router)
    app.include_router(fragments.router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
