"""
Tests para IntelligenceEngine (BN-013).
Recibe el output de portfolio_engine.consolidate() y asigna señal por ticker.
"""
import pytest
from src.services.intelligence import IntelligenceEngine


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_portfolio_data(assets: list[dict]) -> dict:
    """Construye un portfolio_data mínimo para alimentar al engine."""
    total = sum(a["valuation"] for a in assets)
    by_asset = [
        {
            "ticker": a["ticker"],
            "valuation": a["valuation"],
            "pct": round(a["valuation"] / total * 100, 4) if total else 0,
            "portfolios": a.get("portfolios", ["Principal"]),
        }
        for a in assets
    ]
    return {
        "total_valuation": total,
        "by_asset": by_asset,
        "by_source": [],
        "by_currency": [],
    }


# ── Tests básicos de señales ──────────────────────────────────────────────────

def test_ticker_concentrado_señal_sell():
    """Ticker con pct > 30 → SELL con razón de concentración."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},   # 40%
        {"ticker": "GGAL", "valuation": 300.0},   # 30%  (límite, debe ser HOLD o BUY)
        {"ticker": "YPFD", "valuation": 300.0},   # 30%
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    meli = next(s for s in signals if s["ticker"] == "MELI")
    assert meli["signal"] == "SELL"
    assert "concentración" in meli["reason"].lower()
    assert "40" in meli["reason"]  # pct aparece en el mensaje


def test_ticker_subexposicion_señal_buy():
    """Ticker con pct < 3 → BUY."""
    data = make_portfolio_data([
        {"ticker": "TSLA", "valuation": 950.0},   # 95%
        {"ticker": "NVDA", "valuation": 20.0},    # 2%  → BUY
        {"ticker": "AMZN", "valuation": 30.0},    # 3%  → límite
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    nvda = next(s for s in signals if s["ticker"] == "NVDA")
    assert nvda["signal"] == "BUY"
    assert "exposición" in nvda["reason"].lower() or "subexposición" in nvda["reason"].lower() or "baja" in nvda["reason"].lower()


def test_ticker_normal_señal_hold():
    """Ticker entre thresholds → HOLD."""
    data = make_portfolio_data([
        {"ticker": "AL30", "valuation": 200.0},   # 20%  → HOLD
        {"ticker": "GD30", "valuation": 200.0},   # 20%  → HOLD
        {"ticker": "GGAL", "valuation": 200.0},   # 20%  → HOLD
        {"ticker": "PAMP", "valuation": 200.0},   # 20%  → HOLD
        {"ticker": "BBAR", "valuation": 200.0},   # 20%  → HOLD
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    for s in signals:
        assert s["signal"] == "HOLD", f"{s['ticker']} debería ser HOLD, es {s['signal']}"


def test_portfolio_vacio_retorna_lista_vacia():
    """Sin activos → lista vacía, sin errores."""
    data = {"total_valuation": 0.0, "by_asset": [], "by_source": [], "by_currency": []}
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)
    assert signals == []


# ── Tests de estructura de respuesta ─────────────────────────────────────────

def test_señal_contiene_campos_requeridos():
    """Cada señal debe tener: ticker, signal, reason, pct."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 500.0},
        {"ticker": "GGAL", "valuation": 500.0},
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    for s in signals:
        assert "ticker" in s
        assert "signal" in s
        assert "reason" in s
        assert "pct" in s
        assert s["signal"] in ("BUY", "HOLD", "SELL", "NEUTRAL")


def test_señal_pct_coincide_con_input():
    """El pct en la señal debe reflejar el pct real del activo."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 700.0},   # 70%
        {"ticker": "GGAL", "valuation": 300.0},   # 30%
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    meli = next(s for s in signals if s["ticker"] == "MELI")
    assert abs(meli["pct"] - 70.0) < 0.1


# ── Tests de reglas configurables ────────────────────────────────────────────

def test_reglas_custom_via_constructor():
    """Reglas personalizadas anulan los defaults."""
    custom_rules = {
        "concentration_sell_threshold": 50.0,   # más permisivo
        "concentration_buy_threshold": 1.0,     # muy bajo
    }
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},  # 40%  → HOLD con threshold 50
        {"ticker": "GGAL", "valuation": 600.0},  # 60%  → SELL con threshold 50
    ])
    engine = IntelligenceEngine(rules=custom_rules)
    signals = engine.evaluate_tickers(data)

    meli = next(s for s in signals if s["ticker"] == "MELI")
    ggal = next(s for s in signals if s["ticker"] == "GGAL")

    assert meli["signal"] == "HOLD"   # 40% < 50% → no es SELL
    assert ggal["signal"] == "SELL"   # 60% > 50% → SELL


def test_reglas_cargan_desde_json():
    """IntelligenceEngine sin args lee rules.json correctamente."""
    engine = IntelligenceEngine()
    assert engine.rules["concentration_sell_threshold"] > 0
    assert engine.rules["concentration_buy_threshold"] > 0
    assert engine.rules["concentration_sell_threshold"] > engine.rules["concentration_buy_threshold"]


# ── Test de interface ARGOS (placeholder) ────────────────────────────────────

def test_argos_interface_existe():
    """ARGOSInterface está definida y su método retorna None por defecto."""
    from src.services.intelligence import ARGOSInterface
    iface = ARGOSInterface()
    result = iface.get_external_signal("MELI")
    assert result is None


# ── Tests de cartera concentrada (caso real) ─────────────────────────────────

def test_cartera_concentrada_mayoría_sell():
    """Cartera con 2 activos dominando > 30% c/u → ambos SELL."""
    data = make_portfolio_data([
        {"ticker": "MELI",  "valuation": 350.0},  # 35%
        {"ticker": "GGAL",  "valuation": 400.0},  # 40%
        {"ticker": "AL30",  "valuation": 100.0},  # 10%
        {"ticker": "GD30",  "valuation": 100.0},  # 10%
        {"ticker": "PAMP",  "valuation": 50.0},   # 5%
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    sells = [s for s in signals if s["signal"] == "SELL"]
    sell_tickers = {s["ticker"] for s in sells}

    assert "MELI" in sell_tickers
    assert "GGAL" in sell_tickers


def test_cartera_diversificada_solo_hold():
    """Cartera perfectamente distribuida → todos HOLD."""
    data = make_portfolio_data([
        {"ticker": f"TICK{i}", "valuation": 100.0}
        for i in range(10)   # 10% c/u → HOLD
    ])
    engine = IntelligenceEngine()
    signals = engine.evaluate_tickers(data)

    assert all(s["signal"] == "HOLD" for s in signals)
