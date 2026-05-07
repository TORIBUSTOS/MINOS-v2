from decimal import Decimal
from datetime import datetime, timezone

from src.services.market_data import PriceResult
from tests.conftest import make_asset, make_portfolio, make_position, make_source


def test_market_refresh_uses_byma_context_for_known_equities(monkeypatch, client, db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    asset = make_asset(db_session, "BMA")
    make_position(db_session, portfolio, asset, "BMA", quantity=65, currency="ARS")
    db_session.commit()

    def fake_refresh(contexts):
        assert contexts == [("BMA", "BYMA", "EQUITY")]
        now = datetime(2026, 4, 30, tzinfo=timezone.utc)
        return {
            "BMA": PriceResult(
                input_ticker="BMA",
                resolved_symbol="BMA.BA",
                source="test",
                price=Decimal("10890.0"),
                currency="ARS",
                timestamp=now,
                fetched_at=now,
                instrument_type="EQUITY",
                exchange="BYMA",
                quote_unit="PRICE",
                status="OK",
                is_stale=False,
                error=None,
            )
        }

    monkeypatch.setattr(
        "src.api.routes.market.MarketDataService.refresh_quote_contexts",
        fake_refresh,
    )

    response = client.post("/api/v1/market/refresh")

    assert response.status_code == 200
    assert response.json() == {"refreshed": 1, "prices": {"BMA": 10890.0}}
