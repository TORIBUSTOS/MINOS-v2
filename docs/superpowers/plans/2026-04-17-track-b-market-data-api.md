# Track B — BN-007b + BN-008: Market Data & API Patrimonial

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar precios en vivo via yfinance (con cache TTL) y exponer todos los servicios de Track B como endpoints REST.

**Architecture:** `MarketDataService` es un singleton con cache in-memory; los endpoints de portfolio/tickers simplemente llaman a los servicios ya implementados (BN-005/006/007) y devuelven schemas Pydantic.

**Tech Stack:** FastAPI, SQLAlchemy, yfinance (nueva dep), unittest.mock para tests de market data.

**Estado al inicio:** BN-005, BN-006, BN-007 completos. 59 tests passing.

---

## Archivos a crear/modificar

| Acción | Archivo | Responsabilidad |
|--------|---------|-----------------|
| Modificar | `requirements.txt` | Agregar `yfinance>=0.2.54` |
| Crear | `src/services/market_data.py` | Cache TTL + consulta yfinance + fallback |
| Crear | `src/api/routes/market.py` | POST /refresh + GET /prices |
| Crear | `src/api/routes/portfolio.py` | GET summary, by-source, by-currency, /portfolios |
| Crear | `src/api/routes/tickers.py` | GET /tickers/unified |
| Modificar | `src/main.py` | Registrar 3 routers nuevos |
| Crear | `tests/test_market_data.py` | Tests con yfinance mockeado |
| Crear | `tests/test_api_portfolio.py` | Tests de endpoints via TestClient |

---

## Task 1: Agregar yfinance al proyecto

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Agregar dependencia**

En `requirements.txt`, agregar al final:
```
yfinance>=0.2.54
```

- [ ] **Step 2: Instalar**

```bash
pip install yfinance>=0.2.54
```

Expected: instalación sin errores.

- [ ] **Step 3: Verificar que los tests existentes siguen pasando**

```bash
pytest tests/ -v --tb=short
```

Expected: 59 passed.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add yfinance dependency for market data service"
```

---

## Task 2: Market Data Service (BN-007b)

**Files:**
- Create: `src/services/market_data.py`
- Create: `tests/test_market_data.py`

### 2a — RED: escribir tests con yfinance mockeado

- [ ] **Step 1: Crear `tests/test_market_data.py`**

```python
"""
BN-007b: Tests del Market Data Service.
yfinance se mockea — nunca pega a Yahoo en tests.
"""
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest

from src.services.market_data import MarketDataService, PriceCache


@pytest.fixture(autouse=True)
def fresh_cache():
    """Limpia el cache singleton antes de cada test."""
    MarketDataService._cache.clear()
    yield
    MarketDataService._cache.clear()


def _mock_yfinance(prices: dict[str, float]):
    """Helper: mockea yf.Ticker para retornar precios dados."""
    def fake_ticker(symbol):
        mock = MagicMock()
        price = prices.get(symbol, 0.0)
        mock.fast_info.last_price = price
        return mock
    return fake_ticker


# ── Consulta de precios ───────────────────────────────────────────────────────

def test_get_price_returns_value_from_yfinance():
    with patch("src.services.market_data.yf.Ticker", _mock_yfinance({"GGAL": 450.0})):
        price = MarketDataService.get_price("GGAL")
    assert price == 450.0


def test_get_price_caches_result():
    call_count = 0
    def counting_ticker(symbol):
        nonlocal call_count
        call_count += 1
        mock = MagicMock()
        mock.fast_info.last_price = 100.0
        return mock

    with patch("src.services.market_data.yf.Ticker", counting_ticker):
        MarketDataService.get_price("GGAL")
        MarketDataService.get_price("GGAL")  # segunda llamada — debería usar cache

    assert call_count == 1  # yfinance llamado solo una vez


def test_get_price_refreshes_after_ttl_expired():
    call_count = 0
    def counting_ticker(symbol):
        nonlocal call_count
        call_count += 1
        mock = MagicMock()
        mock.fast_info.last_price = 100.0
        return mock

    with patch("src.services.market_data.yf.Ticker", counting_ticker):
        MarketDataService.get_price("GGAL")
        # Expirar el cache manualmente
        MarketDataService._cache["GGAL"] = PriceCache(
            price=100.0,
            fetched_at=datetime.utcnow() - timedelta(minutes=20),
        )
        MarketDataService.get_price("GGAL")  # cache expirado → nuevo fetch

    assert call_count == 2


def test_get_price_fallback_when_yfinance_fails():
    """Si yfinance lanza excepción, retorna último precio conocido."""
    # Seed cache con precio anterior
    MarketDataService._cache["GGAL"] = PriceCache(
        price=300.0,
        fetched_at=datetime.utcnow() - timedelta(minutes=20),  # expirado
    )

    def broken_ticker(symbol):
        raise ConnectionError("Yahoo no responde")

    with patch("src.services.market_data.yf.Ticker", broken_ticker):
        price = MarketDataService.get_price("GGAL")

    assert price == 300.0  # fallback al último conocido


def test_get_price_returns_none_when_no_cache_and_yfinance_fails():
    def broken_ticker(symbol):
        raise ConnectionError("Yahoo no responde")

    with patch("src.services.market_data.yf.Ticker", broken_ticker):
        price = MarketDataService.get_price("GGAL")

    assert price is None


# ── Refresh batch ─────────────────────────────────────────────────────────────

def test_refresh_prices_updates_multiple_tickers():
    prices = {"GGAL": 450.0, "AAPL": 180.0, "PAMP": 120.0}
    with patch("src.services.market_data.yf.Ticker", _mock_yfinance(prices)):
        result = MarketDataService.refresh_prices(["GGAL", "AAPL", "PAMP"])

    assert result["GGAL"] == 450.0
    assert result["AAPL"] == 180.0
    assert result["PAMP"] == 120.0


def test_refresh_prices_returns_none_for_failed_tickers():
    def broken_ticker(symbol):
        raise ConnectionError()

    with patch("src.services.market_data.yf.Ticker", broken_ticker):
        result = MarketDataService.refresh_prices(["GGAL"])

    assert result["GGAL"] is None


def test_get_all_cached_prices_returns_current_cache():
    MarketDataService._cache["GGAL"] = PriceCache(
        price=500.0,
        fetched_at=datetime.utcnow(),
    )
    cached = MarketDataService.get_all_cached()
    assert "GGAL" in cached
    assert cached["GGAL"]["price"] == 500.0
    assert "fetched_at" in cached["GGAL"]
```

- [ ] **Step 2: Verificar RED**

```bash
pytest tests/test_market_data.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.services.market_data'`

### 2b — GREEN: implementar el servicio

- [ ] **Step 3: Crear `src/services/market_data.py`**

```python
"""
Market Data Service: precios en vivo via yfinance con cache TTL.
Cache in-memory singleton. TTL configurable (default 15 min).
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import yfinance as yf

DEFAULT_TTL_MINUTES = 15


@dataclass
class PriceCache:
    price: float
    fetched_at: datetime


class MarketDataService:
    _cache: dict[str, PriceCache] = {}
    _ttl_minutes: int = DEFAULT_TTL_MINUTES

    @classmethod
    def _is_expired(cls, entry: PriceCache) -> bool:
        return datetime.utcnow() - entry.fetched_at > timedelta(minutes=cls._ttl_minutes)

    @classmethod
    def get_price(cls, ticker: str) -> Optional[float]:
        """
        Retorna precio del ticker. Usa cache si vigente.
        Fallback: último precio conocido si yfinance falla.
        Retorna None si no hay cache y yfinance falla.
        """
        cached = cls._cache.get(ticker)
        if cached and not cls._is_expired(cached):
            return cached.price

        try:
            info = yf.Ticker(ticker).fast_info
            price = float(info.last_price)
            cls._cache[ticker] = PriceCache(price=price, fetched_at=datetime.utcnow())
            return price
        except Exception:
            # Fallback: retornar último precio conocido aunque esté expirado
            if cached:
                return cached.price
            return None

    @classmethod
    def refresh_prices(cls, tickers: list[str]) -> dict[str, Optional[float]]:
        """Fuerza refresh de una lista de tickers. Ignora cache."""
        results: dict[str, Optional[float]] = {}
        for ticker in tickers:
            try:
                info = yf.Ticker(ticker).fast_info
                price = float(info.last_price)
                cls._cache[ticker] = PriceCache(price=price, fetched_at=datetime.utcnow())
                results[ticker] = price
            except Exception:
                results[ticker] = None
        return results

    @classmethod
    def get_all_cached(cls) -> dict[str, dict]:
        """Retorna snapshot del cache actual con precios y timestamps."""
        return {
            ticker: {
                "price": entry.price,
                "fetched_at": entry.fetched_at.isoformat(),
                "expired": cls._is_expired(entry),
            }
            for ticker, entry in cls._cache.items()
        }
```

- [ ] **Step 4: Verificar GREEN**

```bash
pytest tests/test_market_data.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Suite completa**

```bash
pytest tests/ -v --tb=short
```

Expected: 68 passed.

- [ ] **Step 6: Commit**

```bash
git add src/services/market_data.py tests/test_market_data.py
git commit -m "feat(bn007b): market data service con cache TTL y fallback"
```

---

## Task 3: Endpoints de Market Data

**Files:**
- Create: `src/api/routes/market.py`
- Modify: `src/main.py`

- [ ] **Step 1: Crear `src/api/routes/market.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.position import Position
from src.services.market_data import MarketDataService

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.post("/refresh")
def refresh_market_prices(db: Session = Depends(get_db)):
    """Fuerza refresh de precios para todos los tickers en cartera."""
    tickers = [row[0] for row in db.query(Position.ticker).distinct().all()]
    result = MarketDataService.refresh_prices(tickers)
    return {"refreshed": len(result), "prices": result}


@router.get("/prices")
def get_market_prices():
    """Retorna precios en cache con timestamp de última actualización."""
    return MarketDataService.get_all_cached()
```

- [ ] **Step 2: Registrar router en `src/main.py`**

Agregar imports y `app.include_router(market_router)`:

```python
from src.api.routes.market import router as market_router
# ...
app.include_router(market_router)
```

- [ ] **Step 3: Verificar que la app levanta sin errores**

```bash
python -c "from src.main import app; print('OK')"
```

- [ ] **Step 4: Suite completa**

```bash
pytest tests/ -v --tb=short
```

Expected: 68 passed (market endpoints no tienen tests dedicados — los ejercita BN-008).

- [ ] **Step 5: Commit**

```bash
git add src/api/routes/market.py src/main.py
git commit -m "feat(bn007b): endpoints POST /market/refresh + GET /market/prices"
```

---

## Task 4: API Patrimonial — BN-008

**Files:**
- Create: `src/api/routes/portfolio.py`
- Create: `src/api/routes/tickers.py`
- Create: `tests/test_api_portfolio.py`
- Modify: `src/main.py`

### 4a — RED

- [ ] **Step 1: Crear `tests/test_api_portfolio.py`**

```python
"""
BN-008: Tests de la API de consulta patrimonial.
Correr con: pytest tests/test_api_portfolio.py -v
"""
import pytest
from tests.conftest import make_asset, make_portfolio, make_position, make_source


def _seed(db_session):
    src_b = make_source(db_session, "Balanz")
    src_i = make_source(db_session, "IOL")
    port1 = make_portfolio(db_session, "Principal", src_b)
    port2 = make_portfolio(db_session, "Conservadora", src_i)
    a_ggal = make_asset(db_session, "GGAL")
    a_aapl = make_asset(db_session, "AAPL")
    make_position(db_session, port1, a_ggal, "GGAL", valuation=3000.0, currency="ARS")
    make_position(db_session, port1, a_aapl, "AAPL", valuation=2000.0, currency="USD")
    make_position(db_session, port2, a_ggal, "GGAL", valuation=1000.0, currency="ARS")
    db_session.commit()


# ── GET /api/v1/portfolio/summary ─────────────────────────────────────────────

def test_portfolio_summary_returns_200(client, db_session):
    _seed(db_session)
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200


def test_portfolio_summary_total_valuation(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    assert body["total_valuation"] == 6000.0


def test_portfolio_summary_has_by_asset(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    tickers = {item["ticker"] for item in body["by_asset"]}
    assert "GGAL" in tickers
    assert "AAPL" in tickers


def test_portfolio_summary_has_by_source(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    sources = {item["source"] for item in body["by_source"]}
    assert "Balanz" in sources
    assert "IOL" in sources


def test_portfolio_summary_has_by_currency(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    currencies = {item["currency"] for item in body["by_currency"]}
    assert "ARS" in currencies
    assert "USD" in currencies


def test_portfolio_summary_empty_db_returns_zeros(client):
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_valuation"] == 0.0


# ── GET /api/v1/portfolio/by-source ──────────────────────────────────────────

def test_portfolio_by_source_returns_200(client, db_session):
    _seed(db_session)
    response = client.get("/api/v1/portfolio/by-source")
    assert response.status_code == 200


def test_portfolio_by_source_has_source_and_valuation(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/by-source").json()
    by_source = {item["source"]: item for item in body}
    assert by_source["Balanz"]["valuation"] == 5000.0
    assert by_source["IOL"]["valuation"] == 1000.0


# ── GET /api/v1/portfolio/by-currency ────────────────────────────────────────

def test_portfolio_by_currency_returns_200(client, db_session):
    _seed(db_session)
    response = client.get("/api/v1/portfolio/by-currency")
    assert response.status_code == 200


def test_portfolio_by_currency_values(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/by-currency").json()
    by_cur = {item["currency"]: item for item in body}
    assert by_cur["ARS"]["valuation"] == 4000.0
    assert by_cur["USD"]["valuation"] == 2000.0


# ── GET /api/v1/portfolios ────────────────────────────────────────────────────

def test_portfolios_list_returns_200(client, db_session):
    _seed(db_session)
    response = client.get("/api/v1/portfolios")
    assert response.status_code == 200


def test_portfolios_list_returns_all_portfolios(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolios").json()
    names = {item["name"] for item in body}
    assert "Principal" in names
    assert "Conservadora" in names


def test_portfolios_list_has_position_count(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolios").json()
    by_name = {item["name"]: item for item in body}
    assert by_name["Principal"]["position_count"] == 2
    assert by_name["Conservadora"]["position_count"] == 1


# ── GET /api/v1/tickers/unified ───────────────────────────────────────────────

def test_tickers_unified_returns_200(client, db_session):
    _seed(db_session)
    response = client.get("/api/v1/tickers/unified")
    assert response.status_code == 200


def test_tickers_unified_returns_distinct_tickers(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/tickers/unified").json()
    tickers = [item["ticker"] for item in body]
    assert len(tickers) == len(set(tickers))
    assert set(tickers) == {"GGAL", "AAPL"}


def test_tickers_unified_ggal_presence_is_two(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/tickers/unified").json()
    by_ticker = {item["ticker"]: item for item in body}
    assert by_ticker["GGAL"]["presence"] == 2
```

- [ ] **Step 2: Verificar RED**

```bash
pytest tests/test_api_portfolio.py -v
```

Expected: `404` en todos los endpoints (rutas no existen).

### 4b — GREEN

- [ ] **Step 3: Crear `src/api/routes/portfolio.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.portfolio import Portfolio
from src.models.position import Position
from src.services.portfolio_engine import consolidate

router = APIRouter(prefix="/api/v1", tags=["portfolio"])


@router.get("/portfolio/summary")
def portfolio_summary(db: Session = Depends(get_db)):
    return consolidate(db)


@router.get("/portfolio/by-source")
def portfolio_by_source(db: Session = Depends(get_db)):
    return consolidate(db)["by_source"]


@router.get("/portfolio/by-currency")
def portfolio_by_currency(db: Session = Depends(get_db)):
    return consolidate(db)["by_currency"]


@router.get("/portfolios")
def list_portfolios(db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).all()
    result = []
    for p in portfolios:
        count = db.query(Position).filter_by(portfolio_id=p.id).count()
        result.append({
            "id": p.id,
            "name": p.name,
            "source_id": p.source_id,
            "position_count": count,
        })
    return result
```

- [ ] **Step 4: Crear `src/api/routes/tickers.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.unified_ticker import unify

router = APIRouter(prefix="/api/v1/tickers", tags=["tickers"])


@router.get("/unified")
def tickers_unified(db: Session = Depends(get_db)):
    return unify(db)
```

- [ ] **Step 5: Registrar routers en `src/main.py`**

```python
from src.api.routes.portfolio import router as portfolio_router
from src.api.routes.tickers import router as tickers_router
# ...
app.include_router(portfolio_router)
app.include_router(tickers_router)
```

- [ ] **Step 6: Verificar GREEN — BN-008**

```bash
pytest tests/test_api_portfolio.py -v
```

Expected: 20 passed.

- [ ] **Step 7: Suite completa**

```bash
pytest tests/ -v
```

Expected: ~88 passed.

- [ ] **Step 8: Commit**

```bash
git add src/api/routes/portfolio.py src/api/routes/tickers.py src/main.py tests/test_api_portfolio.py
git commit -m "feat(bn008): API patrimonial — summary, by-source, by-currency, portfolios, tickers/unified"
```

---

## Task 5: Actualizar CLAUDE.md y push final

- [ ] **Step 1: Actualizar checklist en CLAUDE.md**

En sección `BN Activo`, marcar completos:
```
- [x] BN-007b: Market Data Service (yfinance, cache TTL, fallback)
- [x] BN-008: API patrimonial — 6 endpoints
Track B completo.
```

- [ ] **Step 2: Push**

```bash
git push
```

- [ ] **Step 3: Abrir PR Track B** (si no existe ya)

```bash
gh pr create --title "Sprint 1 — Track B: Portfolio Engine completo" ...
```

---

## Resumen de entregables

| BN | Tests | Archivos nuevos |
|----|-------|-----------------|
| BN-007b | 9 tests | `market_data.py`, `routes/market.py` |
| BN-008 | 20 tests | `routes/portfolio.py`, `routes/tickers.py` |

**Total Track B al cierre:** ~88 tests passing | 6 endpoints nuevos | 1 nueva dependencia (yfinance)

---

## Dependencia pendiente de aprobación

`yfinance>=0.2.54` — necesaria para BN-007b. Sin ella, Task 2 no se puede ejecutar.
Task 3, 4 y 5 **no dependen** de yfinance y pueden ejecutarse en paralelo si se decide posponer el market data.
