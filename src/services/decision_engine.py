"""
Portfolio Decision Engine — BN-014.
Interpreta la cartera completa y genera estado + insights + acción sugerida.
"""
from src.services.intelligence import IntelligenceEngine, _load_rules


class DecisionEngine:
    """
    Evalúa el portfolio completo y produce:
    - status:           EXPANSIÓN | NEUTRAL | RIESGO
    - insights:         2-4 observaciones concretas
    - suggested_action: texto accionable
    - sell_count / buy_count / hold_count: contadores de señales

    Lógica de estado:
    - RIESGO    si: sell_ratio > umbral  OR  concentración crítica  OR  FX dominante
    - EXPANSIÓN si: buy_ratio  > umbral  AND sell_ratio <= max tolerable
    - NEUTRAL   en cualquier otro caso
    """

    def __init__(self, rules: dict | None = None) -> None:
        self._rules = rules or _load_rules()
        self._intel = IntelligenceEngine(rules=self._rules)

    @property
    def rules(self) -> dict:
        return self._rules

    # ── Public API ────────────────────────────────────────────────────────────

    def evaluate_portfolio(self, portfolio_data: dict) -> dict:
        """
        Recibe el output de portfolio_engine.consolidate() y retorna evaluación.

        Returns:
            {
                "status":           str,
                "insights":         list[str],
                "suggested_action": str,
                "sell_count":       int,
                "buy_count":        int,
                "hold_count":       int,
            }
        """
        by_asset = portfolio_data.get("by_asset", [])
        by_currency = portfolio_data.get("by_currency", [])

        if not by_asset:
            return {
                "status": "NEUTRAL",
                "insights": [],
                "suggested_action": "Cargá posiciones para obtener una evaluación de cartera.",
                "sell_count": 0,
                "buy_count": 0,
                "hold_count": 0,
            }

        signals = self._intel.evaluate_tickers(portfolio_data)
        sell_count = sum(1 for s in signals if s["signal"] == "SELL")
        buy_count  = sum(1 for s in signals if s["signal"] == "BUY")
        hold_count = sum(1 for s in signals if s["signal"] == "HOLD")
        total      = len(signals)

        sell_ratio = sell_count / total
        buy_ratio  = buy_count  / total

        max_asset     = max(by_asset, key=lambda a: a["pct"])
        max_currency  = max(by_currency, key=lambda c: c["pct"]) if by_currency else None

        status   = self._compute_status(sell_ratio, buy_ratio, max_asset, max_currency)
        insights = self._build_insights(signals, max_asset, max_currency, sell_count, buy_count)
        action   = self._build_action(status, signals, max_asset)

        return {
            "status": status,
            "insights": insights,
            "suggested_action": action,
            "sell_count": sell_count,
            "buy_count": buy_count,
            "hold_count": hold_count,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _compute_status(
        self,
        sell_ratio: float,
        buy_ratio: float,
        max_asset: dict,
        max_currency: dict | None,
    ) -> str:
        r = self._rules

        riesgo = (
            sell_ratio  >= r["riesgo_sell_ratio_threshold"]
            or max_asset["pct"] >= r["riesgo_critical_concentration"]
            or (max_currency is not None and max_currency["pct"] >= r["riesgo_currency_dominance"])
        )
        if riesgo:
            return "RIESGO"

        expansion = (
            buy_ratio  >= r["expansion_buy_ratio_threshold"]
            and sell_ratio <= r["expansion_max_sell_ratio"]
        )
        if expansion:
            return "EXPANSIÓN"

        return "NEUTRAL"

    def _build_insights(
        self,
        signals: list[dict],
        max_asset: dict,
        max_currency: dict | None,
        sell_count: int,
        buy_count: int,
    ) -> list[str]:
        insights: list[str] = []
        r = self._rules

        # Concentración crítica
        if max_asset["pct"] >= r["riesgo_critical_concentration"]:
            insights.append(
                f"{max_asset['ticker']} concentra el {max_asset['pct']:.1f}% del patrimonio "
                f"— riesgo de sobreexposición."
            )

        # Tickers con señal SELL
        sell_tickers = [s["ticker"] for s in signals if s["signal"] == "SELL"]
        if sell_tickers:
            lista = ", ".join(sell_tickers)
            insights.append(
                f"{sell_count} activo{'s' if sell_count > 1 else ''} con señal SELL: {lista}."
            )

        # Tickers con señal BUY
        buy_tickers = [s["ticker"] for s in signals if s["signal"] == "BUY"]
        if buy_tickers:
            lista = ", ".join(buy_tickers)
            insights.append(
                f"{buy_count} activo{'s' if buy_count > 1 else ''} con baja exposición (BUY): {lista}."
            )

        # Concentración FX
        if max_currency and max_currency["pct"] >= r["riesgo_currency_dominance"]:
            insights.append(
                f"{max_currency['pct']:.1f}% del patrimonio en {max_currency['currency']} "
                f"— alta dependencia de una sola moneda."
            )

        # Diversificación sana (insight positivo)
        if not insights:
            total = len(signals)
            insights.append(
                f"Cartera distribuida en {total} activos con exposición equilibrada."
            )

        return insights[:4]  # máximo 4 insights

    def _build_action(self, status: str, signals: list[dict], max_asset: dict) -> str:
        if status == "RIESGO":
            sell_tickers = [s["ticker"] for s in signals if s["signal"] == "SELL"]
            if sell_tickers:
                return f"Reducir exposición en: {', '.join(sell_tickers)}. Rebalancear hacia activos con menor concentración."
            return f"Diversificar: {max_asset['ticker']} concentra {max_asset['pct']:.1f}% del patrimonio. Considerar rebalanceo."

        if status == "EXPANSIÓN":
            buy_tickers = [s["ticker"] for s in signals if s["signal"] == "BUY"]
            if buy_tickers:
                return f"Oportunidad de reforzar posiciones en: {', '.join(buy_tickers)}."
            return "Mantener estrategia actual. Cartera con buen perfil de oportunidades."

        return "Monitorear concentración. Cartera dentro de parámetros normales."
