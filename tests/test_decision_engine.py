"""
Tests para DecisionEngine (BN-014).
Evalúa la cartera completa y retorna estado + insights + acción sugerida.
"""
import pytest
from src.services.decision_engine import DecisionEngine


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_portfolio_data(assets: list[dict], currencies: list[dict] | None = None) -> dict:
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
    if currencies is None:
        currencies = []
    return {
        "total_valuation": total,
        "by_asset": by_asset,
        "by_source": [],
        "by_currency": currencies,
    }


# ── Tests de estado ───────────────────────────────────────────────────────────

def test_cartera_concentrada_retorna_riesgo():
    """Un activo con > 50% del patrimonio → RIESGO."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 600.0},   # 60%
        {"ticker": "GGAL", "valuation": 250.0},
        {"ticker": "AL30", "valuation": 150.0},
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "RIESGO"


def test_muchos_sell_retorna_riesgo():
    """Más del 30% de tickers con señal SELL → RIESGO."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},   # 40% → SELL
        {"ticker": "GGAL", "valuation": 350.0},   # 35% → SELL
        {"ticker": "AL30", "valuation": 250.0},   # 25% → HOLD
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "RIESGO"


def test_cartera_diversificada_retorna_neutral():
    """Cartera balanceada sin señales extremas → NEUTRAL."""
    data = make_portfolio_data([
        {"ticker": f"TICK{i}", "valuation": 100.0}
        for i in range(8)   # 12.5% c/u → HOLD
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "NEUTRAL"


def test_cartera_con_oportunidades_retorna_expansion():
    """Muchos tickers con BUY y pocos SELL → EXPANSIÓN."""
    # Para generar BUY necesitamos tickers con pct < 3%
    # Cartera: 1 ticker grande + muchos chicos
    assets = [{"ticker": "MELI", "valuation": 700.0}]  # 70% → SELL... no
    # Generamos BUY con activos sub-representados
    # total = 1000, buy_threshold = 3% → < 30 ARS
    assets = (
        [{"ticker": "MAIN", "valuation": 700.0}]       # 70% → SELL (esto da RIESGO)
    )
    # Mejor enfoque: usar reglas custom para forzar EXPANSIÓN
    custom_rules = {
        "concentration_sell_threshold": 80.0,   # umbral alto → no habrá SELL
        "concentration_buy_threshold": 3.0,
        "riesgo_sell_ratio_threshold": 0.5,
        "riesgo_critical_concentration": 99.0,
        "riesgo_currency_dominance": 99.0,
        "expansion_buy_ratio_threshold": 0.3,
        "expansion_max_sell_ratio": 0.3,
    }
    data = make_portfolio_data([
        {"ticker": "MAIN", "valuation": 940.0},   # 94% → HOLD (< 80% sell threshold)
        {"ticker": "TINY1", "valuation": 20.0},   # 2% → BUY
        {"ticker": "TINY2", "valuation": 20.0},   # 2% → BUY
        {"ticker": "TINY3", "valuation": 20.0},   # 2% → BUY
    ])
    engine = DecisionEngine(rules=custom_rules)
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "EXPANSIÓN"


def test_moneda_dominante_retorna_riesgo():
    """Exposición > 80% en una sola moneda → RIESGO."""
    data = make_portfolio_data(
        assets=[
            {"ticker": "AL30", "valuation": 500.0},
            {"ticker": "GD30", "valuation": 500.0},
        ],
        currencies=[
            {"currency": "ARS", "valuation": 900.0, "pct": 90.0},
            {"currency": "USD", "valuation": 100.0, "pct": 10.0},
        ],
    )
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "RIESGO"


def test_cartera_vacia_retorna_neutral():
    """Sin posiciones → NEUTRAL sin insights de activos."""
    data = {"total_valuation": 0.0, "by_asset": [], "by_source": [], "by_currency": []}
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "NEUTRAL"
    assert isinstance(result["insights"], list)


# ── Tests de estructura de respuesta ─────────────────────────────────────────

def test_retorna_campos_requeridos():
    """El resultado siempre incluye status, insights, suggested_action."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 500.0},
        {"ticker": "GGAL", "valuation": 500.0},
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)

    assert "status" in result
    assert "insights" in result
    assert "suggested_action" in result
    assert "sell_count" in result
    assert "buy_count" in result
    assert "hold_count" in result


def test_status_es_valor_valido():
    """Status siempre es uno de los tres valores definidos."""
    data = make_portfolio_data([{"ticker": "MELI", "valuation": 1000.0}])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert result["status"] in ("EXPANSIÓN", "NEUTRAL", "RIESGO")


def test_insights_es_lista_de_strings():
    """Insights es una lista de strings no vacíos."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 700.0},
        {"ticker": "GGAL", "valuation": 300.0},
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)

    assert isinstance(result["insights"], list)
    for insight in result["insights"]:
        assert isinstance(insight, str)
        assert len(insight) > 0


def test_accion_sugerida_no_vacia():
    """suggested_action es siempre un string no vacío."""
    data = make_portfolio_data([{"ticker": "MELI", "valuation": 500.0}])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)
    assert isinstance(result["suggested_action"], str)
    assert len(result["suggested_action"]) > 0


def test_contadores_sell_buy_hold_coherentes():
    """sell_count + buy_count + hold_count == total tickers."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},
        {"ticker": "GGAL", "valuation": 300.0},
        {"ticker": "AL30", "valuation": 200.0},
        {"ticker": "GD30", "valuation": 100.0},
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)

    total = result["sell_count"] + result["buy_count"] + result["hold_count"]
    assert total == len(data["by_asset"])


# ── Tests de insights ─────────────────────────────────────────────────────────

def test_cartera_concentrada_insight_menciona_ticker():
    """Con concentración alta el insight menciona el ticker problemático."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 700.0},
        {"ticker": "GGAL", "valuation": 300.0},
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)

    all_insights = " ".join(result["insights"])
    assert "MELI" in all_insights


def test_accion_riesgo_menciona_reducir():
    """Con estado RIESGO la acción sugiere reducir exposición."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 700.0},
        {"ticker": "GGAL", "valuation": 300.0},
    ])
    engine = DecisionEngine()
    result = engine.evaluate_portfolio(data)

    assert result["status"] == "RIESGO"
    assert any(word in result["suggested_action"].lower()
               for word in ("reducir", "diversificar", "rebalancear"))


# ── Tests de reglas configurables ────────────────────────────────────────────

def test_reglas_custom_cambian_estado():
    """Con umbrales más permisivos, una cartera concentrada puede ser NEUTRAL."""
    custom_rules = {
        "concentration_sell_threshold": 90.0,
        "concentration_buy_threshold": 1.0,
        "riesgo_sell_ratio_threshold": 1.0,     # nunca RIESGO por sell_ratio
        "riesgo_critical_concentration": 95.0,  # umbral muy alto
        "riesgo_currency_dominance": 99.0,
        "expansion_buy_ratio_threshold": 0.8,
        "expansion_max_sell_ratio": 0.0,
    }
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 700.0},   # 70% → HOLD con threshold 90
        {"ticker": "GGAL", "valuation": 300.0},   # 30% → HOLD
    ])
    engine = DecisionEngine(rules=custom_rules)
    result = engine.evaluate_portfolio(data)
    assert result["status"] == "NEUTRAL"
