"""
Capital Reallocation Engine — BN-015.
Sugiere qué hacer con capital liberable cuando hay activos en SELL o liquidez ociosa.
Principio: MINOS nunca sugiere vender sin proponer destino del capital.
"""
from src.services.intelligence import IntelligenceEngine, _load_rules


class ReallocationEngine:
    """
    Evalúa el portfolio y produce sugerencias de reasignación de capital.

    Returns:
        releasable_capital: valuación total de los tickers con señal SELL
        liquidity_level:    ALTA | MEDIA | BAJA según fracción del patrimonio
        opportunities:      tickers con señal BUY (destinos posibles)
        rotations:          pares SELL → BUY con monto sugerido
        suggested_action:   texto accionable
    """

    def __init__(self, rules: dict | None = None) -> None:
        self._rules = rules or _load_rules()
        self._intel = IntelligenceEngine(rules=self._rules)

    @property
    def rules(self) -> dict:
        return self._rules

    # ── Public API ────────────────────────────────────────────────────────────

    def suggest(self, portfolio_data: dict) -> dict:
        """
        Recibe el output de portfolio_engine.consolidate() y retorna
        sugerencias de reasignación de capital.
        """
        by_asset = portfolio_data.get("by_asset", [])
        total    = portfolio_data.get("total_valuation", 0.0)

        if not by_asset or total == 0:
            return {
                "releasable_capital": 0.0,
                "liquidity_level": "BAJA",
                "opportunities": [],
                "rotations": [],
                "suggested_action": "Cargá posiciones para obtener sugerencias de reasignación.",
            }

        signals      = self._intel.evaluate_tickers(portfolio_data)
        signal_map   = {s["ticker"]: s for s in signals}

        sell_assets  = [a for a in by_asset if signal_map.get(a["ticker"], {}).get("signal") == "SELL"]
        buy_assets   = [a for a in by_asset if signal_map.get(a["ticker"], {}).get("signal") == "BUY"]

        releasable   = sum(a["valuation"] for a in sell_assets)
        liquidity    = self._compute_liquidity(releasable, total)
        opportunities = self._build_opportunities(buy_assets)
        rotations    = self._build_rotations(sell_assets, buy_assets, releasable)
        action       = self._build_action(sell_assets, buy_assets, rotations, releasable)

        return {
            "releasable_capital": releasable,
            "liquidity_level": liquidity,
            "opportunities": opportunities,
            "rotations": rotations,
            "suggested_action": action,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _compute_liquidity(self, releasable: float, total: float) -> str:
        pct = releasable / total * 100
        if pct >= self._rules["liquidity_high_threshold"]:
            return "ALTA"
        if pct >= self._rules["liquidity_low_threshold"]:
            return "MEDIA"
        return "BAJA"

    def _build_opportunities(self, buy_assets: list[dict]) -> list[dict]:
        return [
            {
                "ticker": a["ticker"],
                "current_pct": a["pct"],
                "suggested_action": f"Reforzar posición en {a['ticker']} (actualmente {a['pct']:.1f}%)",
            }
            for a in buy_assets
        ]

    def _build_rotations(
        self,
        sell_assets: list[dict],
        buy_assets: list[dict],
        releasable: float,
    ) -> list[dict]:
        if not sell_assets or not buy_assets:
            return []

        rotations = []
        # Distribuir el capital liberable equitativamente entre oportunidades BUY
        amount_per_buy = releasable / len(buy_assets)

        for sell in sell_assets:
            for buy in buy_assets:
                rotations.append({
                    "from": sell["ticker"],
                    "to": buy["ticker"],
                    "amount": round(amount_per_buy / len(sell_assets), 2),
                    "reason": (
                        f"Reducir {sell['ticker']} ({sell['pct']:.1f}% → sobreexposición) "
                        f"y reforzar {buy['ticker']} ({buy['pct']:.1f}% → subexposición)."
                    ),
                })

        return rotations

    def _build_action(
        self,
        sell_assets: list[dict],
        buy_assets: list[dict],
        rotations: list[dict],
        releasable: float,
    ) -> str:
        if not sell_assets:
            return "Cartera equilibrada. Sin capital liberable para reasignar."

        sell_names = ", ".join(a["ticker"] for a in sell_assets)

        if rotations:
            buy_names = ", ".join(a["ticker"] for a in buy_assets)
            return (
                f"Rotar capital liberado de {sell_names} "
                f"hacia oportunidades: {buy_names}. "
                f"Capital disponible para mover: ${releasable:,.0f}."
            )

        # SELL pero sin BUY disponibles — principio: proponer destino igual
        return (
            f"Reducir exposición en {sell_names}. "
            f"Sin oportunidades BUY activas: mantener capital como reserva de liquidez "
            f"hasta que aparezcan mejores destinos. Capital a resguardar: ${releasable:,.0f}."
        )
