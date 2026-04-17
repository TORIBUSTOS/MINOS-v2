"""
BN-007: Tests de normalización de tickers, monedas y detección de duplicados.
Correr con: pytest tests/test_normalization.py -v
"""
from src.services.normalization import normalize_ticker, normalize_currency, detect_duplicates


# ── Ticker normalization ──────────────────────────────────────────────────────

def test_normalize_ticker_uppercases():
    assert normalize_ticker("meli") == "MELI"


def test_normalize_ticker_strips_whitespace():
    assert normalize_ticker("  GGAL  ") == "GGAL"


def test_normalize_ticker_resolves_alias():
    """Alias configurado: MercadoLibre → MELI"""
    assert normalize_ticker("MercadoLibre") == "MELI"


def test_normalize_ticker_resolves_alias_case_insensitive():
    assert normalize_ticker("mercadolibre") == "MELI"


def test_normalize_ticker_unknown_returns_uppercased():
    assert normalize_ticker("NVDA") == "NVDA"


def test_normalize_ticker_ba_suffix_preserved():
    """Tickers MERVAL con sufijo .BA se preservan."""
    assert normalize_ticker("ypfd.ba") == "YPFD.BA"


# ── Currency normalization ────────────────────────────────────────────────────

def test_normalize_currency_uppercases():
    assert normalize_currency("usd") == "USD"


def test_normalize_currency_strips_whitespace():
    assert normalize_currency("  ars  ") == "ARS"


def test_normalize_currency_resolves_alias():
    """'dólares' → 'USD', 'pesos' → 'ARS'"""
    assert normalize_currency("dólares") == "USD"
    assert normalize_currency("pesos") == "ARS"


def test_normalize_currency_unknown_returns_uppercased():
    assert normalize_currency("EUR") == "EUR"


# ── Duplicate detection ───────────────────────────────────────────────────────

def test_detect_duplicates_no_duplicates():
    tickers = ["GGAL", "MELI", "AAPL"]
    assert detect_duplicates(tickers) == []


def test_detect_duplicates_finds_repeated_ticker():
    tickers = ["GGAL", "MELI", "GGAL"]
    dupes = detect_duplicates(tickers)
    assert "GGAL" in dupes


def test_detect_duplicates_case_insensitive():
    tickers = ["ggal", "GGAL"]
    dupes = detect_duplicates(tickers)
    assert len(dupes) == 1


def test_detect_duplicates_returns_each_duplicate_once():
    tickers = ["GGAL", "GGAL", "GGAL"]
    dupes = detect_duplicates(tickers)
    assert dupes.count("GGAL") == 1
