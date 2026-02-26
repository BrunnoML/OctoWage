"""Sistema de cache em memória para fragmentos HTMX e dados de API."""

import hashlib
import json
from functools import wraps
from typing import Any, Callable

from cachetools import TTLCache

from app.config import get_settings

settings = get_settings()

_cache: TTLCache = TTLCache(
    maxsize=settings.cache_max_size,
    ttl=settings.cache_ttl_seconds,
)


def cached_fragment(ttl: int | None = None) -> Callable:
    """Decorator para cachear fragmentos HTML renderizados.

    Args:
        ttl: Tempo de vida do cache em segundos. Se None, usa o padrão.
    """
    cache_store = _cache if ttl is None else TTLCache(maxsize=500, ttl=ttl)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Gera chave baseada nos parâmetros
            key = hashlib.md5(
                json.dumps(
                    {"fn": func.__name__, "kwargs": {k: v for k, v in kwargs.items() if k != "request"}},
                    sort_keys=True,
                    default=str,
                ).encode()
            ).hexdigest()

            if key in cache_store:
                return cache_store[key]

            result = await func(*args, **kwargs)
            cache_store[key] = result
            return result

        return wrapper

    return decorator


def invalidate_cache() -> None:
    """Limpa todo o cache. Chamar após ETL completar."""
    _cache.clear()
