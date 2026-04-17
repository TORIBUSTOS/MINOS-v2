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
