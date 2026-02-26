"""Serviço de câmbio em tempo real — USD/BRL e EUR/BRL.

Fonte primária: AwesomeAPI (economia.awesomeapi.com.br) — gratuita, sem chave.
Fonte secundária: Banco Central do Brasil (BCB PTAX) — dados oficiais.
Fallback: Valores estáticos atualizados manualmente.

Cache: 1 hora (cotações não mudam a cada segundo para nosso caso de uso).
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ExchangeRate:
    """Cotação de uma moeda em relação ao BRL."""

    currency: str  # "USD" ou "EUR"
    buy: float  # Compra
    sell: float  # Venda
    rate: float  # Média (buy+sell)/2 — usamos essa para conversão
    source: str  # "AwesomeAPI", "BCB PTAX", "Estático"
    source_url: str
    updated_at: str  # ISO 8601
    flag: str  # Emoji da bandeira


@dataclass
class ExchangeRateCache:
    """Cache de cotações com TTL de 1 hora."""

    rates: dict[str, ExchangeRate] = field(default_factory=dict)
    last_fetch: datetime | None = None
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))

    @property
    def is_valid(self) -> bool:
        """Verifica se o cache ainda é válido."""
        if not self.last_fetch or not self.rates:
            return False
        return datetime.now() - self.last_fetch < self.ttl


# Cache global
_cache = ExchangeRateCache()

# Valores estáticos de fallback (atualizar periodicamente)
STATIC_RATES: dict[str, ExchangeRate] = {
    "USD": ExchangeRate(
        currency="USD",
        buy=5.75,
        sell=5.85,
        rate=5.80,
        source="Estático (câmbio médio 2025)",
        source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00",
        flag="🇺🇸",
    ),
    "EUR": ExchangeRate(
        currency="EUR",
        buy=6.05,
        sell=6.15,
        rate=6.10,
        source="Estático (câmbio médio 2025)",
        source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00",
        flag="🇪🇺",
    ),
}


async def _fetch_awesome_api() -> dict[str, ExchangeRate] | None:
    """Busca cotações na AwesomeAPI (economia.awesomeapi.com.br).

    Endpoint: GET https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL
    Retorna JSON com chaves 'USDBRL' e 'EURBRL', cada uma contendo:
      - bid (compra), ask (venda), high, low, timestamp, create_date
    """
    url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        rates: dict[str, ExchangeRate] = {}

        for key, currency, flag in [("USDBRL", "USD", "🇺🇸"), ("EURBRL", "EUR", "🇪🇺")]:
            item = data[key]
            buy = float(item["bid"])
            sell = float(item["ask"])
            rates[currency] = ExchangeRate(
                currency=currency,
                buy=buy,
                sell=sell,
                rate=round((buy + sell) / 2, 4),
                source="AwesomeAPI (tempo real)",
                source_url="https://economia.awesomeapi.com.br",
                updated_at=item.get("create_date", datetime.now().isoformat()),
                flag=flag,
            )

        logger.info("Cotações obtidas via AwesomeAPI: USD=%.4f, EUR=%.4f", rates["USD"].rate, rates["EUR"].rate)
        return rates

    except Exception as e:
        logger.warning("Falha na AwesomeAPI: %s", e)
        return None


async def _fetch_bcb_ptax() -> dict[str, ExchangeRate] | None:
    """Busca cotações no Banco Central do Brasil (PTAX).

    Endpoint: Olinda API (OData)
    https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/
    CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?
    @moeda='USD'&@dataCotacao='MM-DD-YYYY'&$format=json
    """
    today = datetime.now().strftime("%m-%d-%Y")
    base_url = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        "CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)"
    )

    rates: dict[str, ExchangeRate] = {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for currency, flag in [("USD", "🇺🇸"), ("EUR", "🇪🇺")]:
                url = f"{base_url}?@moeda='{currency}'&@dataCotacao='{today}'&$format=json&$top=1&$orderby=dataHoraCotacao%20desc"
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()

                items = data.get("value", [])
                if not items:
                    # Sem cotação hoje (final de semana/feriado) — tentar ontem
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
                    url = url.replace(today, yesterday)
                    resp = await client.get(url)
                    resp.raise_for_status()
                    data = resp.json()
                    items = data.get("value", [])

                if not items:
                    logger.warning("BCB PTAX: sem cotação disponível para %s", currency)
                    return None

                item = items[0]
                buy = float(item["cotacaoCompra"])
                sell = float(item["cotacaoVenda"])

                rates[currency] = ExchangeRate(
                    currency=currency,
                    buy=buy,
                    sell=sell,
                    rate=round((buy + sell) / 2, 4),
                    source="BCB PTAX (oficial)",
                    source_url="https://dadosabertos.bcb.gov.br",
                    updated_at=item.get("dataHoraCotacao", datetime.now().isoformat()),
                    flag=flag,
                )

        logger.info("Cotações obtidas via BCB PTAX: USD=%.4f, EUR=%.4f", rates["USD"].rate, rates["EUR"].rate)
        return rates

    except Exception as e:
        logger.warning("Falha no BCB PTAX: %s", e)
        return None


async def get_exchange_rates() -> dict[str, ExchangeRate]:
    """Retorna cotações USD/BRL e EUR/BRL com cache de 1 hora.

    Cascata de fontes:
    1. AwesomeAPI (rápida, tempo real)
    2. BCB PTAX (oficial, pode ter delay)
    3. Valores estáticos (fallback seguro)
    """
    global _cache

    if _cache.is_valid:
        return _cache.rates

    # Tenta AwesomeAPI primeiro
    rates = await _fetch_awesome_api()

    # Se falhou, tenta BCB
    if rates is None:
        rates = await _fetch_bcb_ptax()

    # Se tudo falhou, usa estático
    if rates is None:
        logger.warning("Todas as APIs de câmbio falharam. Usando valores estáticos.")
        rates = STATIC_RATES.copy()

    # Atualiza cache
    _cache.rates = rates
    _cache.last_fetch = datetime.now()

    return rates


def convert_to_brl(amount_foreign: float, currency: str, rates: dict[str, ExchangeRate]) -> float:
    """Converte valor em moeda estrangeira para BRL."""
    rate = rates.get(currency)
    if not rate:
        raise ValueError(f"Moeda não suportada: {currency}")
    return round(amount_foreign * rate.rate, 2)


async def get_international_with_live_rates() -> tuple[list[dict], dict[str, ExchangeRate]]:
    """Retorna dados internacionais recalculados com câmbio atualizado.

    Salários originais em moeda local:
    - EUA: Juiz ~US$26,300/mês, Professor ~US$6,900/mês
    - Alemanha: Juiz ~€8,500/mês, Professor ~€6,400/mês
    - Portugal: Juiz ~€6,000/mês, Professor ~€2,800/mês
    """
    rates = await get_exchange_rates()

    usd_rate = rates["USD"].rate
    eur_rate = rates["EUR"].rate

    international = [
        {
            "country": "Brasil",
            "flag": "🇧🇷",
            "judge_salary_brl": 81500.00,
            "judge_salary_note": "Média nacional com penduricalhos (DadosJusBr 2025)",
            "teacher_salary_brl": 5130.63,
            "teacher_salary_note": "Piso nacional (Portaria MEC 82/2026)",
            "ratio": 15.9,
            "source": "DadosJusBr + MEC",
            "original_currency": "BRL",
            "judge_original": 81500.00,
            "teacher_original": 5130.63,
        },
        {
            "country": "EUA",
            "flag": "🇺🇸",
            "judge_salary_brl": round(26300 * usd_rate, 2),
            "judge_salary_note": f"Federal Judge: ~US$26.300/mês (US$220k-274k/ano, judiciary.gov 2025)",
            "teacher_salary_brl": round(6900 * usd_rate, 2),
            "teacher_salary_note": f"Public school teacher: ~US$6.900/mês (BLS 2024, média US$65k/ano)",
            "ratio": round(26300 / 6900, 1),
            "source": "US Courts / BLS",
            "original_currency": "USD",
            "judge_original": 26300,
            "teacher_original": 6900,
        },
        {
            "country": "Alemanha",
            "flag": "🇩🇪",
            "judge_salary_brl": round(8500 * eur_rate, 2),
            "judge_salary_note": f"Richter R3: ~€8.500/mês (Bundesbesoldung 2025)",
            "teacher_salary_brl": round(6400 * eur_rate, 2),
            "teacher_salary_note": f"Gymnasiallehrer: ~€6.400/mês (OECD 2023)",
            "ratio": round(8500 / 6400, 1),
            "source": "OECD Government at a Glance 2023",
            "original_currency": "EUR",
            "judge_original": 8500,
            "teacher_original": 6400,
        },
        {
            "country": "Portugal",
            "flag": "🇵🇹",
            "judge_salary_brl": round(6000 * eur_rate, 2),
            "judge_salary_note": f"Juiz de Direito: ~€6.000/mês (CSTJ 2025)",
            "teacher_salary_brl": round(2800 * eur_rate, 2),
            "teacher_salary_note": f"Professor QZP: ~€2.800/mês (DGAE 2025)",
            "ratio": round(6000 / 2800, 1),
            "source": "CSTJ / DGAE Portugal",
            "original_currency": "EUR",
            "judge_original": 6000,
            "teacher_original": 2800,
        },
    ]

    return international, rates
