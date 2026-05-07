"""
Normalization service: estandariza tickers, monedas y detecta duplicados.
Aliases configurables en src/config/ticker_aliases.json y currency_aliases.json.
"""
import json
from pathlib import Path

_CONFIG = Path(__file__).parent.parent / "config"

def _load_aliases(filename: str) -> dict[str, str]:
    path = _CONFIG / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

_TICKER_ALIASES = _load_aliases("ticker_aliases.json")
_CURRENCY_ALIASES = _load_aliases("currency_aliases.json")


def normalize_ticker(raw: str) -> str:
    """Normaliza un ticker: strip → alias lookup → uppercase."""
    cleaned = raw.strip()
    key = cleaned.lower()
    if key in _TICKER_ALIASES:
        return _TICKER_ALIASES[key]
    return cleaned.upper()


def normalize_currency(raw: str) -> str:
    """Normaliza una moneda: strip → alias lookup → uppercase."""
    cleaned = raw.strip()
    key = cleaned.lower()
    if key in _CURRENCY_ALIASES:
        return _CURRENCY_ALIASES[key]
    return cleaned.upper()


def detect_duplicates(tickers: list[str]) -> list[str]:
    """Detecta tickers duplicados (case-insensitive). Retorna lista de duplicados únicos."""
    seen: set[str] = set()
    dupes: set[str] = set()
    for t in tickers:
        normalized = t.strip().upper()
        if normalized in seen:
            dupes.add(normalized)
        seen.add(normalized)
    return list(dupes)


BYMA_EQUITY_TICKERS = {
    "ALUA",
    "BBAR",
    "BMA",
    "BYMA",
    "CEPU",
    "COME",
    "CRES",
    "EDN",
    "GGAL",
    "LOMA",
    "MIRG",
    "PAMP",
    "SUPV",
    "TECO2",
    "TGNO4",
    "TGSU2",
    "TRAN",
    "TXAR",
    "VALO",
    "YPFD",
}

CEDEAR_UNDERLYINGS = {
    "AAPL": "Apple Inc.",
    "AMZN": "Amazon.com Inc.",
    "DIA": "SPDR Dow Jones Industrial Average ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "GOOGL": "Alphabet Inc.",
    "KO": "The Coca-Cola Company",
    "MELI": "MercadoLibre Inc.",
    "META": "Meta Platforms Inc.",
    "MSFT": "Microsoft Corporation",
    "NFLX": "Netflix Inc.",
    "NVDA": "NVIDIA Corporation",
    "QQQ": "Invesco QQQ Trust",
    "SPY": "SPDR S&P 500 ETF",
    "TSLA": "Tesla Inc.",
    "TSM": "Taiwan Semiconductor Manufacturing Company",
}


def infer_asset_type(ticker: str, current: str | None = None) -> str:
    """Infere tipo mínimo de instrumento cuando la carga no lo trae."""
    normalized = normalize_ticker(ticker).removesuffix(".BA")
    current_type = (current or "unknown").strip().upper()
    if current_type and current_type != "UNKNOWN":
        return current_type
    if normalized in CEDEAR_UNDERLYINGS:
        return "CEDEAR"
    if normalized in BYMA_EQUITY_TICKERS:
        return "EQUITY"
    return "unknown"


def cedear_underlying(ticker: str) -> str | None:
    """Retorna la acción/ETF subyacente conocida para un CEDEAR local."""
    normalized = normalize_ticker(ticker).removesuffix(".BA")
    return CEDEAR_UNDERLYINGS.get(normalized)
