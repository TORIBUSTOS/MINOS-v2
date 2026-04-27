"""
Tests para ReallocationEngine (BN-015).
Sugiere qué hacer con capital liberable cuando hay activos en SELL o liquidez ociosa.
Principio: MINOS nunca sugiere vender sin proponer destino del capital.
"""
import pytest
from src.services.reallocation import ReallocationEngine


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_portfolio_data(assets: list[dict]) -> dict:
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


# ── Tests de capital liberable ────────────────────────────────────────────────

def test_activo_sell_genera_capital_liberable():
    """Ticker con SELL → releasable_capital > 0."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},   # 40% → SELL
        {"ticker": "GGAL", "valuation": 600.0},   # 60% → SELL
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)
    assert result["releasable_capital"] > 0


def test_capital_liberable_es_suma_de_valuaciones_sell():
    """releasable_capital == suma de valuaciones de tickers con SELL."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},   # 40% → SELL
        {"ticker": "GGAL", "valuation": 350.0},   # 35% → SELL
        {"ticker": "AL30", "valuation": 250.0},   # 25% → HOLD
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)
    # MELI y GGAL son SELL → capital liberable = 750
    assert abs(result["releasable_capital"] - 750.0) < 0.01


def test_sin_sells_capital_liberable_es_cero():
    """Sin señales SELL → releasable_capital == 0."""
    data = make_portfolio_data([
        {"ticker": f"T{i}", "valuation": 100.0} for i in range(8)  # 12.5% c/u → HOLD
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)
    assert result["releasable_capital"] == 0.0


# ── Tests de nivel de liquidez ────────────────────────────────────────────────

def test_nivel_liquidez_alta_cuando_mucho_capital_liberable():
    """Capital liberable > 30% del total → nivel ALTA."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},   # 40% → SELL
        {"ticker": "GGAL", "valuation": 350.0},   # 35% → SELL
        {"ticker": "AL30", "valuation": 250.0},
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)
    assert result["liquidity_level"] == "ALTA"


def test_nivel_liquidez_baja_sin_sells():
    """Sin capital liberable → nivel BAJA."""
    data = make_portfolio_data([
        {"ticker": f"T{i}", "valuation": 100.0} for i in range(8)
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)
    assert result["liquidity_level"] == "BAJA"


def test_nivel_liquidez_media():
    """Capital liberable entre 10% y 30% → nivel MEDIA."""
    # Total = 1000, SELL = 200 (20%) → MEDIA
    custom_rules = {
        "concentration_sell_threshold": 15.0,   # 20% > 15% → SELL
        "concentration_buy_threshold": 1.0,
        "riesgo_sell_ratio_threshold": 0.5,
        "riesgo_critical_concentration": 50.0,
        "riesgo_currency_dominance": 80.0,
        "expansion_buy_ratio_threshold": 0.5,
        "expansion_max_sell_ratio": 0.1,
        "liquidity_high_threshold": 30.0,
        "liquidity_low_threshold": 10.0,
    }
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 200.0},  # 20% → SELL con threshold 15
        {"ticker": "GGAL", "valuation": 800.0},  # 80% → SELL también... ajustar
    ])
    # Usar cartera donde sólo 1 ticker queda en SELL con ~20%
    data = make_portfolio_data([
        {"ticker": "GGAL", "valuation": 200.0},  # 20% → SELL (> 15%)
        {"ticker": "AL30", "valuation": 200.0},  # 20% → SELL
        {"ticker": "GD30", "valuation": 200.0},  # 20% → SELL
        {"ticker": "PAMP", "valuation": 200.0},  # 20% → SELL
        {"ticker": "BBAR", "valuation": 200.0},  # 20% → SELL
    ])
    # Con threshold 15%, todos son SELL (20% > 15%) → ALTA
    # Necesitamos exactamente entre 10-30% de capital liberable
    # Total 1000, exactamente 1 ticker SELL a 200 = 20% → MEDIA
    # Pero con threshold 15%, todos los de 20% son SELL
    # Usamos threshold 25% para que sólo los de > 25% sean SELL
    custom_rules["concentration_sell_threshold"] = 25.0
    data = make_portfolio_data([
        {"ticker": "HOT",  "valuation": 260.0},   # 26% → SELL
        {"ticker": "AL30", "valuation": 240.0},   # 24% → HOLD
        {"ticker": "GD30", "valuation": 240.0},   # 24% → HOLD
        {"ticker": "BBAR", "valuation": 260.0},   # 26% → SELL
    ])
    # releasable = 520 / 1000 = 52% → ALTA, no MEDIA
    # Busquemos un caso más controlado
    custom_rules["concentration_sell_threshold"] = 19.0
    data = make_portfolio_data([
        {"ticker": "HOT",  "valuation": 200.0},   # 20% → SELL (> 19%)
        {"ticker": "AL30", "valuation": 800.0},   # 80% → SELL también
    ])
    # Imposible con 2 tickers... mejor usar 10 tickers y 1 con 20%
    data = make_portfolio_data(
        [{"ticker": "BIG", "valuation": 200.0}] +
        [{"ticker": f"S{i}", "valuation": 80.0} for i in range(10)]
    )
    # Total = 200 + 800 = 1000, BIG = 20% → SELL, resto = 8.88% → HOLD (< 19%)
    # releasable = 200/1000 = 20% → MEDIA
    engine = ReallocationEngine(rules=custom_rules)
    result = engine.suggest(data)
    assert result["liquidity_level"] == "MEDIA"


# ── Tests de oportunidades ────────────────────────────────────────────────────

def test_tickers_buy_aparecen_en_oportunidades():
    """Tickers con señal BUY → en la lista de oportunidades."""
    custom_rules = {
        "concentration_sell_threshold": 90.0,   # nadie es SELL
        "concentration_buy_threshold": 5.0,     # < 5% → BUY
        "riesgo_sell_ratio_threshold": 0.5,
        "riesgo_critical_concentration": 95.0,
        "riesgo_currency_dominance": 95.0,
        "expansion_buy_ratio_threshold": 0.3,
        "expansion_max_sell_ratio": 0.2,
        "liquidity_high_threshold": 30.0,
        "liquidity_low_threshold": 10.0,
    }
    data = make_portfolio_data([
        {"ticker": "MAIN",  "valuation": 920.0},  # 92% → HOLD
        {"ticker": "TINY1", "valuation": 40.0},   # 4% → BUY
        {"ticker": "TINY2", "valuation": 40.0},   # 4% → BUY
    ])
    engine = ReallocationEngine(rules=custom_rules)
    result = engine.suggest(data)

    opp_tickers = [o["ticker"] for o in result["opportunities"]]
    assert "TINY1" in opp_tickers
    assert "TINY2" in opp_tickers


def test_sin_buy_sin_oportunidades():
    """Sin señales BUY → lista de oportunidades vacía."""
    data = make_portfolio_data([
        {"ticker": f"T{i}", "valuation": 100.0} for i in range(8)  # 12.5% → HOLD
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)
    assert result["opportunities"] == []


# ── Tests de rotaciones ───────────────────────────────────────────────────────

def test_sell_mas_buy_genera_rotaciones():
    """SELL + BUY → lista de rotaciones no vacía."""
    custom_rules = {
        "concentration_sell_threshold": 30.0,
        "concentration_buy_threshold": 3.0,
        "riesgo_sell_ratio_threshold": 0.5,
        "riesgo_critical_concentration": 50.0,
        "riesgo_currency_dominance": 80.0,
        "expansion_buy_ratio_threshold": 0.3,
        "expansion_max_sell_ratio": 0.2,
        "liquidity_high_threshold": 30.0,
        "liquidity_low_threshold": 10.0,
    }
    data = make_portfolio_data([
        {"ticker": "MELI",  "valuation": 400.0},  # 40% → SELL
        {"ticker": "MID",   "valuation": 580.0},  # 58% → SELL
        {"ticker": "TINY1", "valuation": 10.0},   # 1% → BUY
        {"ticker": "TINY2", "valuation": 10.0},   # 1% → BUY
    ])
    engine = ReallocationEngine(rules=custom_rules)
    result = engine.suggest(data)
    assert len(result["rotations"]) > 0


def test_rotacion_tiene_campos_from_to_amount():
    """Cada rotación incluye 'from', 'to', 'amount' y 'reason'."""
    custom_rules = {
        "concentration_sell_threshold": 30.0,
        "concentration_buy_threshold": 3.0,
        "riesgo_sell_ratio_threshold": 0.5,
        "riesgo_critical_concentration": 50.0,
        "riesgo_currency_dominance": 80.0,
        "expansion_buy_ratio_threshold": 0.3,
        "expansion_max_sell_ratio": 0.2,
        "liquidity_high_threshold": 30.0,
        "liquidity_low_threshold": 10.0,
    }
    data = make_portfolio_data([
        {"ticker": "BIG",   "valuation": 970.0},  # 97% → SELL
        {"ticker": "TINY1", "valuation": 20.0},   # 2% → BUY
        {"ticker": "TINY2", "valuation": 10.0},   # 1% → BUY
    ])
    engine = ReallocationEngine(rules=custom_rules)
    result = engine.suggest(data)

    for rot in result["rotations"]:
        assert "from" in rot
        assert "to" in rot
        assert "amount" in rot
        assert "reason" in rot
        assert rot["amount"] > 0


def test_sell_sin_buy_no_genera_rotaciones_pero_si_accion():
    """SELL sin BUY disponibles → rotaciones vacías pero acción sugerida presente."""
    data = make_portfolio_data([
        {"ticker": "MELI", "valuation": 400.0},  # 40% → SELL
        {"ticker": "GGAL", "valuation": 350.0},  # 35% → SELL
        {"ticker": "AL30", "valuation": 250.0},  # 25% → HOLD
    ])
    engine = ReallocationEngine()
    result = engine.suggest(data)

    assert result["rotations"] == []
    assert len(result["suggested_action"]) > 0
    # Sin destino disponible → debe mencionar liquidez o caja
    assert any(w in result["suggested_action"].lower()
               for w in ("liquidez", "caja", "mantener", "reserva"))


# ── Tests de estructura y principios ─────────────────────────────────────────

def test_retorna_campos_requeridos():
    """El resultado siempre incluye todos los campos definidos."""
    data = make_portfolio_data([{"ticker": "MELI", "valuation": 1000.0}])
    engine = ReallocationEngine()
    result = engine.suggest(data)

    assert "releasable_capital" in result
    assert "liquidity_level" in result
    assert "opportunities" in result
    assert "rotations" in result
    assert "suggested_action" in result


def test_cartera_vacia_retorna_valores_neutros():
    """Sin posiciones → releasable_capital=0, listas vacías, acción descriptiva."""
    data = {"total_valuation": 0.0, "by_asset": [], "by_source": [], "by_currency": []}
    engine = ReallocationEngine()
    result = engine.suggest(data)

    assert result["releasable_capital"] == 0.0
    assert result["opportunities"] == []
    assert result["rotations"] == []
    assert isinstance(result["suggested_action"], str)
    assert len(result["suggested_action"]) > 0


def test_accion_sugerida_siempre_presente():
    """suggested_action es siempre un string no vacío."""
    for assets in [
        [{"ticker": "MELI", "valuation": 1000.0}],               # 100% → SELL
        [{"ticker": f"T{i}", "valuation": 100.0} for i in range(8)],  # HOLD
    ]:
        engine = ReallocationEngine()
        result = engine.suggest(make_portfolio_data(assets))
        assert isinstance(result["suggested_action"], str)
        assert len(result["suggested_action"]) > 0
