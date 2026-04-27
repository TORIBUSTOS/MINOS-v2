"""
Intelligence Layer — BN-013.
Asigna señales BUY / HOLD / SELL a cada ticker basado en reglas configurables.
"""
import json
from pathlib import Path

_RULES_PATH = Path(__file__).parent.parent / "config" / "rules.json"


def _load_rules() -> dict:
    with open(_RULES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


class ARGOSInterface:
    """Placeholder para integración futura con el sistema ARGOS."""

    def get_external_signal(self, ticker: str) -> dict | None:
        return None


class IntelligenceEngine:
    """
    Evalúa los tickers de una cartera y asigna señales basadas en reglas.

    Reglas v1:
    - pct > concentration_sell_threshold  → SELL  (sobreexposición)
    - pct < concentration_buy_threshold   → BUY   (subexposición)
    - entre ambos thresholds              → HOLD
    """

    def __init__(self, rules: dict | None = None) -> None:
        self._rules = rules or _load_rules()
        self._argos = ARGOSInterface()

    @property
    def rules(self) -> dict:
        return self._rules

    def evaluate_tickers(self, portfolio_data: dict) -> list[dict]:
        """
        Recibe el output de portfolio_engine.consolidate() y retorna señales.

        Returns:
            [
                {
                    "ticker": str,
                    "signal": "BUY" | "HOLD" | "SELL" | "NEUTRAL",
                    "reason": str,
                    "pct": float,
                }
            ]
        """
        by_asset: list[dict] = portfolio_data.get("by_asset", [])
        if not by_asset:
            return []

        sell_threshold = self._rules["concentration_sell_threshold"]
        buy_threshold = self._rules["concentration_buy_threshold"]

        results = []
        for asset in by_asset:
            ticker = asset["ticker"]
            pct = asset["pct"]

            if pct > sell_threshold:
                signal = "SELL"
                reason = (
                    f"Concentración alta: {pct:.1f}% del patrimonio "
                    f"(límite: {sell_threshold}%). Riesgo de sobreexposición."
                )
            elif pct < buy_threshold:
                signal = "BUY"
                reason = (
                    f"Baja exposición: {pct:.1f}% del patrimonio "
                    f"(mínimo sugerido: {buy_threshold}%). Posición subexplotada."
                )
            else:
                signal = "HOLD"
                reason = (
                    f"Exposición equilibrada: {pct:.1f}% del patrimonio. "
                    f"Dentro del rango [{buy_threshold}%, {sell_threshold}%]."
                )

            results.append({
                "ticker": ticker,
                "signal": signal,
                "reason": reason,
                "pct": pct,
            })

        return results
