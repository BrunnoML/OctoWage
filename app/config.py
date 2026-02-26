"""Configuração centralizada do OctoWage via Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # App
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_title: str = "OctoWage"
    app_description: str = "Transparência salarial do setor público brasileiro"

    # APIs externas
    portal_transparencia_api_key: str = ""
    dadosjusbr_base_url: str = "https://api.dadosjusbr.org"

    # Cache
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 1000

    # Teto constitucional (atualizar quando mudar)
    teto_constitucional: float = 46366.19

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
