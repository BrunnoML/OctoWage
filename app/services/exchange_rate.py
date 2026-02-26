"""Serviço de câmbio em tempo real — múltiplas moedas vs BRL.

Fonte primária: AwesomeAPI (economia.awesomeapi.com.br) — gratuita, sem chave.
Fonte secundária: Banco Central do Brasil (BCB PTAX) — dados oficiais.
Fallback: Valores estáticos atualizados manualmente.

Cache: 1 hora (cotações não mudam a cada segundo para nosso caso de uso).

Moedas suportadas: USD, EUR, CLP, JPY, CNY, INR, RUB, ZAR
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

    currency: str  # "USD", "EUR", "CLP", "JPY", "CNY", "INR", "RUB", "ZAR"
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

# Moedas suportadas: código, bandeira
SUPPORTED_CURRENCIES: list[tuple[str, str]] = [
    ("USD", "🇺🇸"),
    ("EUR", "🇪🇺"),
    ("CLP", "🇨🇱"),
    ("JPY", "🇯🇵"),
    ("CNY", "🇨🇳"),
    ("INR", "🇮🇳"),
    ("RUB", "🇷🇺"),
    ("ZAR", "🇿🇦"),
    ("MXN", "🇲🇽"),
]

# Valores estáticos de fallback (atualizar periodicamente)
STATIC_RATES: dict[str, ExchangeRate] = {
    "USD": ExchangeRate(
        currency="USD", buy=5.75, sell=5.85, rate=5.80,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇺🇸",
    ),
    "EUR": ExchangeRate(
        currency="EUR", buy=6.05, sell=6.15, rate=6.10,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇪🇺",
    ),
    "CLP": ExchangeRate(
        currency="CLP", buy=0.0058, sell=0.0062, rate=0.0060,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇨🇱",
    ),
    "JPY": ExchangeRate(
        currency="JPY", buy=0.037, sell=0.039, rate=0.038,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇯🇵",
    ),
    "CNY": ExchangeRate(
        currency="CNY", buy=0.78, sell=0.82, rate=0.80,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇨🇳",
    ),
    "INR": ExchangeRate(
        currency="INR", buy=0.066, sell=0.070, rate=0.068,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇮🇳",
    ),
    "RUB": ExchangeRate(
        currency="RUB", buy=0.058, sell=0.062, rate=0.060,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇷🇺",
    ),
    "ZAR": ExchangeRate(
        currency="ZAR", buy=0.31, sell=0.33, rate=0.32,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇿🇦",
    ),
    "MXN": ExchangeRate(
        currency="MXN", buy=0.28, sell=0.30, rate=0.29,
        source="Estático (câmbio médio 2025)", source_url="https://www.bcb.gov.br",
        updated_at="2025-12-01T00:00:00", flag="🇲🇽",
    ),
}


async def _fetch_awesome_api() -> dict[str, ExchangeRate] | None:
    """Busca cotações na AwesomeAPI (economia.awesomeapi.com.br).

    Endpoint: GET https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,...
    Retorna JSON com chaves como 'USDBRL', 'EURBRL', etc., cada uma contendo:
      - bid (compra), ask (venda), high, low, timestamp, create_date
    """
    pairs = ",".join(f"{c}-BRL" for c, _ in SUPPORTED_CURRENCIES)
    url = f"https://economia.awesomeapi.com.br/last/{pairs}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        rates: dict[str, ExchangeRate] = {}

        for currency, flag in SUPPORTED_CURRENCIES:
            key = f"{currency}BRL"
            if key not in data:
                logger.warning("AwesomeAPI: moeda %s não retornada", currency)
                continue
            item = data[key]
            buy = float(item["bid"])
            sell = float(item["ask"])
            rates[currency] = ExchangeRate(
                currency=currency,
                buy=buy,
                sell=sell,
                rate=round((buy + sell) / 2, 6),
                source="AwesomeAPI (tempo real)",
                source_url="https://economia.awesomeapi.com.br",
                updated_at=item.get("create_date", datetime.now().isoformat()),
                flag=flag,
            )

        if "USD" in rates:
            logger.info("Cotações obtidas via AwesomeAPI: %d moedas, USD=%.4f", len(rates), rates["USD"].rate)
            return rates

        logger.warning("AwesomeAPI: USD não retornado, descartando resultado")
        return None

    except Exception as e:
        logger.warning("Falha na AwesomeAPI: %s", e)
        return None


async def _fetch_bcb_ptax() -> dict[str, ExchangeRate] | None:
    """Busca cotações no Banco Central do Brasil (PTAX) — apenas USD e EUR.

    O BCB PTAX é usado como fallback da AwesomeAPI e suporta apenas as moedas
    principais (USD, EUR). Para as demais, usamos valores estáticos.

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

        # Complementar com estáticos para moedas que o BCB não cobre facilmente
        for currency, flag in SUPPORTED_CURRENCIES:
            if currency not in rates and currency in STATIC_RATES:
                rates[currency] = STATIC_RATES[currency]

        logger.info("Cotações obtidas via BCB PTAX: USD=%.4f, EUR=%.4f (+%d estáticas)", rates["USD"].rate, rates["EUR"].rate, len(rates) - 2)
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


def _rate(rates: dict[str, ExchangeRate], currency: str) -> float:
    """Retorna a taxa de câmbio para uma moeda, com fallback estático."""
    if currency in rates:
        return rates[currency].rate
    if currency in STATIC_RATES:
        return STATIC_RATES[currency].rate
    return 1.0


async def get_international_with_live_rates() -> tuple[list[dict], dict[str, ExchangeRate]]:
    """Retorna dados internacionais recalculados com câmbio atualizado.

    12 países: Brasil + 11 internacionais.
    Salários originais em moeda local, convertidos para BRL em tempo real.
    Fontes: OECD Government at a Glance, judiciary.gov, portais oficiais.
    """
    rates = await get_exchange_rates()

    usd = _rate(rates, "USD")
    eur = _rate(rates, "EUR")
    clp = _rate(rates, "CLP")
    jpy = _rate(rates, "JPY")
    cny = _rate(rates, "CNY")
    inr = _rate(rates, "INR")
    rub = _rate(rates, "RUB")
    zar = _rate(rates, "ZAR")
    mxn = _rate(rates, "MXN")

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
            "judge_salary_brl": round(26300 * usd, 2),
            "judge_salary_note": "Federal Judge: ~US$26.300/mês (judiciary.gov 2025)",
            "teacher_salary_brl": round(6900 * usd, 2),
            "teacher_salary_note": "Public school teacher: ~US$6.900/mês (BLS 2024)",
            "ratio": round(26300 / 6900, 1),
            "source": "US Courts / BLS",
            "original_currency": "USD",
            "judge_original": 26300,
            "teacher_original": 6900,
        },
        {
            "country": "Alemanha",
            "flag": "🇩🇪",
            "judge_salary_brl": round(8500 * eur, 2),
            "judge_salary_note": "Richter R3: ~€8.500/mês (Bundesbesoldung 2025)",
            "teacher_salary_brl": round(6400 * eur, 2),
            "teacher_salary_note": "Gymnasiallehrer: ~€6.400/mês (OECD 2023)",
            "ratio": round(8500 / 6400, 1),
            "source": "OECD Government at a Glance 2023",
            "original_currency": "EUR",
            "judge_original": 8500,
            "teacher_original": 6400,
        },
        {
            "country": "Portugal",
            "flag": "🇵🇹",
            "judge_salary_brl": round(6000 * eur, 2),
            "judge_salary_note": "Juiz de Direito: ~€6.000/mês (CSTJ 2025)",
            "teacher_salary_brl": round(2800 * eur, 2),
            "teacher_salary_note": "Professor QZP: ~€2.800/mês (DGAE 2025)",
            "ratio": round(6000 / 2800, 1),
            "source": "CSTJ / DGAE Portugal",
            "original_currency": "EUR",
            "judge_original": 6000,
            "teacher_original": 2800,
        },
        {
            "country": "Chile",
            "flag": "🇨🇱",
            "judge_salary_brl": round(6500000 * clp, 2),
            "judge_salary_note": "Ministro Corte: ~CLP 6.500.000/mês (Poder Judicial 2025)",
            "teacher_salary_brl": round(1100000 * clp, 2),
            "teacher_salary_note": "Profesor básica: ~CLP 1.100.000/mês (MINEDUC 2025)",
            "ratio": round(6500000 / 1100000, 1),
            "source": "Poder Judicial / MINEDUC Chile",
            "original_currency": "CLP",
            "judge_original": 6500000,
            "teacher_original": 1100000,
        },
        {
            "country": "Japão",
            "flag": "🇯🇵",
            "judge_salary_brl": round(1200000 * jpy, 2),
            "judge_salary_note": "裁判官: ~¥1.200.000/mês (Courts of Japan 2025)",
            "teacher_salary_brl": round(450000 * jpy, 2),
            "teacher_salary_note": "教員: ~¥450.000/mês (MEXT 2024)",
            "ratio": round(1200000 / 450000, 1),
            "source": "Courts of Japan / MEXT",
            "original_currency": "JPY",
            "judge_original": 1200000,
            "teacher_original": 450000,
        },
        {
            "country": "China",
            "flag": "🇨🇳",
            "judge_salary_brl": round(22000 * cny, 2),
            "judge_salary_note": "法官: ~¥22.000/mês (Supreme People's Court 2024)",
            "teacher_salary_brl": round(9000 * cny, 2),
            "teacher_salary_note": "教师: ~¥9.000/mês (Ministry of Education 2024)",
            "ratio": round(22000 / 9000, 1),
            "source": "SPC / MoE China",
            "original_currency": "CNY",
            "judge_original": 22000,
            "teacher_original": 9000,
        },
        {
            "country": "Índia",
            "flag": "🇮🇳",
            "judge_salary_brl": round(250000 * inr, 2),
            "judge_salary_note": "High Court Judge: ~₹250.000/mês (Dept of Justice 2024)",
            "teacher_salary_brl": round(45000 * inr, 2),
            "teacher_salary_note": "Govt School Teacher: ~₹45.000/mês (7th Pay Commission)",
            "ratio": round(250000 / 45000, 1),
            "source": "Dept of Justice / 7th Pay Commission India",
            "original_currency": "INR",
            "judge_original": 250000,
            "teacher_original": 45000,
        },
        {
            "country": "Rússia",
            "flag": "🇷🇺",
            "judge_salary_brl": round(180000 * rub, 2),
            "judge_salary_note": "Судья: ~₽180.000/mês (Judicial Department 2024)",
            "teacher_salary_brl": round(45000 * rub, 2),
            "teacher_salary_note": "Учитель: ~₽45.000/mês (Rosstat 2024)",
            "ratio": round(180000 / 45000, 1),
            "source": "Judicial Department / Rosstat Russia",
            "original_currency": "RUB",
            "judge_original": 180000,
            "teacher_original": 45000,
        },
        {
            "country": "África do Sul",
            "flag": "🇿🇦",
            "judge_salary_brl": round(280000 * zar, 2),
            "judge_salary_note": "Judge: ~R280.000/mês (JSC 2024)",
            "teacher_salary_brl": round(28000 * zar, 2),
            "teacher_salary_note": "Teacher: ~R28.000/mês (SACE 2024)",
            "ratio": round(280000 / 28000, 1),
            "source": "JSC / SACE South Africa",
            "original_currency": "ZAR",
            "judge_original": 280000,
            "teacher_original": 28000,
        },
        {
            "country": "México",
            "flag": "🇲🇽",
            "judge_salary_brl": round(120000 * mxn, 2),
            "judge_salary_note": "Juez de Distrito: ~MXN 120.000/mês (CJF 2024)",
            "teacher_salary_brl": round(24000 * mxn, 2),
            "teacher_salary_note": "Maestro básica: ~MXN 24.000/mês (SEP 2024)",
            "ratio": round(120000 / 24000, 1),
            "source": "CJF / SEP México",
            "original_currency": "MXN",
            "judge_original": 120000,
            "teacher_original": 24000,
        },
        {
            "country": "França",
            "flag": "🇫🇷",
            "judge_salary_brl": round(5800 * eur, 2),
            "judge_salary_note": "Magistrat: ~€5.800/mês (Ministère de la Justice 2024)",
            "teacher_salary_brl": round(3200 * eur, 2),
            "teacher_salary_note": "Professeur certifié: ~€3.200/mês (Éducation Nationale 2024)",
            "ratio": round(5800 / 3200, 1),
            "source": "Ministère de la Justice / Éducation Nationale France",
            "original_currency": "EUR",
            "judge_original": 5800,
            "teacher_original": 3200,
        },
    ]

    # Ordenar do maior para o menor ratio (desigualdade)
    international.sort(key=lambda c: c["ratio"], reverse=True)

    return international, rates
