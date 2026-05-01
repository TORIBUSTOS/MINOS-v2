import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.services.market_data import MarketDataService


DEBUG_INSTRUMENTS = [
    ("BMA", "BYMA", "EQUITY"),
    ("YPFD", "BYMA", "EQUITY"),
    ("GGAL", "BYMA", "EQUITY"),
    ("PAMP", "BYMA", "EQUITY"),
    ("SUPV", "BYMA", "EQUITY"),
]


def main() -> None:
    print(
        "ticker_input | instrument_type | exchange | resolved_symbol | source | "
        "price | currency | quote_timestamp | fetched_at | is_stale | status | error"
    )
    for ticker, exchange, instrument_type in DEBUG_INSTRUMENTS:
        quote = MarketDataService.get_quote(ticker, exchange, instrument_type)
        print(
            f"{quote.input_ticker} | {quote.instrument_type} | {quote.exchange} | "
            f"{quote.resolved_symbol} | {quote.source} | {quote.price} | "
            f"{quote.currency} | {quote.timestamp.isoformat() if quote.timestamp else None} | "
            f"{quote.fetched_at.isoformat()} | {quote.is_stale} | "
            f"{quote.status} | {quote.error}"
        )


if __name__ == "__main__":
    main()
