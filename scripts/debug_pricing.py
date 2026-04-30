"""
BN Sprint 2 — Diagnóstico de pricing.

Testea cómo MINOS resuelve y obtiene precios para acciones BYMA.
NO modifica ninguna lógica. Solo diagnóstico.

Uso:
    python scripts/debug_pricing.py
"""
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf

# ---------------------------------------------------------------------------
# Activos a testear — acciones BYMA
# ---------------------------------------------------------------------------
TEST_CASES = [
    {"ticker_input": "BMA",  "instrument_type": "EQUITY", "exchange": "BYMA"},
    {"ticker_input": "YPFD", "instrument_type": "EQUITY", "exchange": "BYMA"},
    {"ticker_input": "GGAL", "instrument_type": "EQUITY", "exchange": "BYMA"},
    {"ticker_input": "PAMP", "instrument_type": "EQUITY", "exchange": "BYMA"},
    {"ticker_input": "SUPV", "instrument_type": "EQUITY", "exchange": "BYMA"},
]

# Resultado esperado si BYMA se resuelve correctamente
EXPECTED_SUFFIX = ".BA"
EXPECTED_CURRENCY = "ARS"
STALE_THRESHOLD_HOURS = 24


def _resolve_symbol_current(ticker_input: str) -> str:
    """Reproduce exactamente lo que MarketDataService hace hoy: pasa el ticker sin modificar."""
    return ticker_input


def _resolve_symbol_correct(ticker_input: str, exchange: str) -> str:
    """Resolución correcta para BYMA: agrega sufijo .BA."""
    if exchange == "BYMA" and not ticker_input.endswith(".BA"):
        return ticker_input + ".BA"
    return ticker_input


def _fetch_price_data(symbol: str) -> dict:
    """Obtiene precio, moneda y timestamp de yfinance para un símbolo dado."""
    fetched_at = datetime.now(timezone.utc)
    try:
        ticker_obj = yf.Ticker(symbol)
        fast = ticker_obj.fast_info

        price = None
        currency = None
        quote_timestamp = None

        try:
            price = float(fast.last_price) if fast.last_price is not None else None
        except Exception:
            price = None

        try:
            currency = str(fast.currency).upper() if fast.currency else None
        except Exception:
            currency = None

        # yfinance no expone un timestamp de cotización directamente en fast_info.
        # Intentamos obtenerlo del campo last_fetch_time o de info general.
        try:
            # fast_info no tiene quote_timestamp — el más cercano es via .history()
            # Para no hacer llamadas pesadas, marcamos como NOT_AVAILABLE
            quote_timestamp = "NOT_AVAILABLE (fast_info no expone timestamp)"
        except Exception:
            quote_timestamp = None

        if price is None:
            return {
                "price": None,
                "currency": currency,
                "quote_timestamp": quote_timestamp,
                "fetched_at": fetched_at,
                "source": "yfinance/fast_info",
                "error": "last_price returned None",
                "status": "ERROR",
            }

        # Determinar si el precio es stale
        # yfinance/fast_info no retorna un timestamp de cotización, así que
        # no podemos verificar staleness real. Marcamos como UNKNOWN.
        return {
            "price": price,
            "currency": currency,
            "quote_timestamp": quote_timestamp,
            "fetched_at": fetched_at,
            "source": "yfinance/fast_info",
            "error": None,
            "status": "OK",
        }

    except Exception as exc:
        return {
            "price": None,
            "currency": None,
            "quote_timestamp": None,
            "fetched_at": fetched_at,
            "source": "yfinance/fast_info",
            "error": str(exc),
            "status": "ERROR",
        }


def _is_stale(data: dict) -> bool:
    """No tenemos quote_timestamp real — marcamos como UNKNOWN."""
    return False


def _detect_bugs(case: dict, current_symbol: str, correct_symbol: str, data: dict) -> list[str]:
    bugs = []

    if current_symbol != correct_symbol:
        bugs.append(
            f"BUG: resolved_symbol={current_symbol!r} sin sufijo .BA "
            f"(debería ser {correct_symbol!r})"
        )

    if data["currency"] and data["currency"] != EXPECTED_CURRENCY:
        bugs.append(
            f"BUG: currency={data['currency']!r} — se esperaba {EXPECTED_CURRENCY!r} para BYMA"
        )

    if data["price"] == 0.0:
        bugs.append("BUG: price=0 — posible fallback silencioso")

    if data["price"] is None and data["status"] != "ERROR":
        bugs.append("BUG: price=None sin status=ERROR — falla silenciosa")

    if data["source"] is None:
        bugs.append("BUG: source no registrado")

    return bugs


# ---------------------------------------------------------------------------
# Tabla de salida
# ---------------------------------------------------------------------------
COLUMNS = [
    "ticker_input", "instrument_type", "exchange", "resolved_symbol",
    "source", "price", "currency", "quote_timestamp",
    "fetched_at", "is_stale", "status", "error",
]

COL_WIDTHS = {
    "ticker_input":    12, "instrument_type": 16, "exchange": 8,
    "resolved_symbol": 16, "source":          20, "price":    12,
    "currency":        10, "quote_timestamp": 45, "fetched_at": 28,
    "is_stale":        10, "status":           8, "error":    40,
}


def _fmt(val, width: int) -> str:
    s = str(val) if val is not None else "None"
    return s[:width].ljust(width)


def _print_header():
    header = " | ".join(_fmt(c, COL_WIDTHS[c]) for c in COLUMNS)
    sep = "-+-".join("-" * COL_WIDTHS[c] for c in COLUMNS)
    print(header)
    print(sep)


def _print_row(row: dict):
    line = " | ".join(_fmt(row.get(c), COL_WIDTHS[c]) for c in COLUMNS)
    print(line)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("MINOS Sprint 2 — Diagnóstico de Pricing (BN diagnóstico)")
    print(f"Ejecutado: {datetime.now(timezone.utc).isoformat()}")
    print()
    print("NOTA: 'resolved_symbol (CURRENT)' = lo que MINOS hace hoy")
    print("      'resolved_symbol (CORRECT)' = lo que debería hacer para BYMA")
    print("=" * 80)
    print()

    results = []
    all_bugs = []

    for case in TEST_CASES:
        ticker_input = case["ticker_input"]
        instrument_type = case["instrument_type"]
        exchange = case["exchange"]

        current_symbol = _resolve_symbol_current(ticker_input)
        correct_symbol = _resolve_symbol_correct(ticker_input, exchange)

        # Fetch usando el símbolo ACTUAL (lo que MINOS hace hoy)
        data_current = _fetch_price_data(current_symbol)
        # Fetch usando el símbolo CORRECTO (con .BA)
        data_correct = _fetch_price_data(correct_symbol)

        bugs = _detect_bugs(case, current_symbol, correct_symbol, data_current)
        all_bugs.extend([(ticker_input, b) for b in bugs])

        status_current = "BUG" if bugs else data_current["status"]

        row = {
            "ticker_input":    ticker_input,
            "instrument_type": instrument_type,
            "exchange":        exchange,
            "resolved_symbol": f"{current_symbol} [CURRENT]",
            "source":          data_current["source"] or "None",
            "price":           data_current["price"],
            "currency":        data_current["currency"] or "None",
            "quote_timestamp": data_current["quote_timestamp"] or "None",
            "fetched_at":      data_current["fetched_at"].isoformat() if data_current["fetched_at"] else "None",
            "is_stale":        str(_is_stale(data_current)),
            "status":          status_current,
            "error":           data_current["error"] or "",
        }
        results.append(row)

    # ---- Tabla: resolución ACTUAL ----
    print("[ RESOLUCIÓN ACTUAL — lo que MINOS hace hoy ]")
    print()
    _print_header()
    for r in results:
        _print_row(r)

    print()
    print("=" * 80)
    print()

    # ---- Tabla: resolución CORRECTA para comparación ----
    results_correct = []
    for case in TEST_CASES:
        ticker_input = case["ticker_input"]
        instrument_type = case["instrument_type"]
        exchange = case["exchange"]
        correct_symbol = _resolve_symbol_correct(ticker_input, exchange)
        data_correct = _fetch_price_data(correct_symbol)

        row = {
            "ticker_input":    ticker_input,
            "instrument_type": instrument_type,
            "exchange":        exchange,
            "resolved_symbol": f"{correct_symbol} [CORRECT]",
            "source":          data_correct["source"] or "None",
            "price":           data_correct["price"],
            "currency":        data_correct["currency"] or "None",
            "quote_timestamp": data_correct["quote_timestamp"] or "None",
            "fetched_at":      data_correct["fetched_at"].isoformat() if data_correct["fetched_at"] else "None",
            "is_stale":        str(_is_stale(data_correct)),
            "status":          data_correct["status"],
            "error":           data_correct["error"] or "",
        }
        results_correct.append(row)

    print("[ RESOLUCIÓN CORRECTA — con sufijo .BA (referencia) ]")
    print()
    _print_header()
    for r in results_correct:
        _print_row(r)

    print()
    print("=" * 80)
    print()

    # ---- Resumen de bugs ----
    print("[ BUGS DETECTADOS ]")
    print()
    if all_bugs:
        for ticker, bug in all_bugs:
            print(f"  [{ticker}] {bug}")
    else:
        print("  Ninguno.")

    print()
    print("=" * 80)
    print()

    # ---- Diagnóstico estructural ----
    print("[ DIAGNÓSTICO ESTRUCTURAL ]")
    print()

    structural_issues = [
        ("NO_EXCHANGE_FIELD",
         "El modelo Asset y Position NO tienen campo exchange ni instrument_type. "
         "Imposible saber si un ticker es BYMA/NYSE sin metadata adicional."),

        ("NO_BA_SUFFIX_LOGIC",
         "MarketDataService.get_price() pasa el ticker tal cual a yfinance. "
         "No existe lógica para agregar sufijo .BA a tickers BYMA."),

        ("TICKER_ALIASES_INCOMPLETO",
         "ticker_aliases.json mapea 'ypf' → 'YPFD' (sin .BA), 'galicia' → 'GGAL' (sin .BA). "
         "Aliases no son exchange-aware."),

        ("VALUATION_ESTATICA",
         "portfolio_engine.consolidate() usa pos.valuation (ingested, static). "
         "MarketDataService NO está integrado en la valuación de cartera."),

        ("NO_CURRENCY_IN_PRICE",
         "MarketDataService.get_price() retorna solo float. "
         "No retorna moneda. PriceCache almacena solo price + fetched_at."),

        ("NO_QUOTE_TIMESTAMP",
         "yfinance.fast_info no expone timestamp de cotización. "
         "PriceCache solo tiene fetched_at (cuándo se fetcheó, no cuándo cotizó)."),

        ("FALLBACK_SILENCIOSO",
         "Si yfinance falla y hay cache, se retorna cached.price sin indicación de staleness. "
         "El caller no sabe si el precio es fresco o antiguo."),
    ]

    for code, desc in structural_issues:
        print(f"  [{code}]")
        print(f"    {desc}")
        print()

    print("=" * 80)
    print()
    print("[ PRÓXIMO BN RECOMENDADO ]")
    print()
    print("  BN Sprint 2 — Implementar InstrumentResolver:")
    print("  1. Agregar campo exchange + instrument_type a Asset model")
    print("  2. Crear InstrumentResolver que mapea (ticker, exchange) → yfinance_symbol")
    print("     - BYMA EQUITY → ticker + '.BA'")
    print("     - NYSE/NASDAQ → ticker sin cambio")
    print("     - CEDEAR → ticker + '.BA' (o sufijo específico)")
    print("  3. Integrar InstrumentResolver en MarketDataService")
    print("  4. PriceResult debe incluir: price, currency, source, quote_timestamp, is_stale")
    print("  5. portfolio_engine.consolidate() debe usar precios live (market_price × quantity)")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
