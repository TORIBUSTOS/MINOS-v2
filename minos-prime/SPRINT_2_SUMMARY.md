# Sprint 2 — Broker-Grade Valuation Core

**Estado:** CERRADO  
**Fecha de cierre:** 2026-05-01  
**Objetivo rector:** primero verdad financiera, después inteligencia.

---

## Qué se logró

- Se agregó resolución explícita de instrumentos BYMA para acciones argentinas usando sufijo `.BA`.
- Market data dejó de devolver solo números sueltos y pasó a exponer quotes trazables con `input_ticker`, `resolved_symbol`, `source`, `price`, `currency`, timestamps, `instrument_type`, `exchange`, `status` y errores.
- PortfolioEngine incorporó valuación tipo broker para instrumentos soportados:
  - `market_value`
  - `cost_basis`
  - `pnl_absolute`
  - `pnl_percentage`
  - `portfolio_weight`
  - `valuation_trace`
  - `valuation_status`
- Intelligence quedó subordinada a la calidad de valuación: si `valuation_status != OK`, la señal no es accionable y queda bloqueada con motivo explícito.
- La vista de Instrumentos del frontend muestra una tabla broker-like con nominales, precio, fecha de precio, PPC, valor actual, valor inicial, rendimiento, peso de cartera y estado de valuación.

---

## Problemas resueltos

- Evita resolver acciones argentinas como símbolos incompletos cuando requieren `.BA`.
- Evita fallbacks silenciosos tipo `price = 0`.
- Permite auditar de dónde salió cada precio y cuándo fue obtenido.
- Separa valuación financiera de inteligencia accionable.
- Evita que MINOS emita recomendaciones accionables cuando el pricing o la valuación no son confiables.
- Hace visible en UI el estado de valuación antes que la señal BUY/HOLD/SELL.

---

## Riesgos que quedan

- La cobertura broker-grade está acotada a instrumentos soportados explícitamente; CEDEAR avanzado, bonos complejos y FX avanzado siguen fuera de scope.
- La calidad del pricing depende de disponibilidad y consistencia de yfinance.
- `valuation_status` depende de que el flujo de datos clasifique correctamente tipo de instrumento y exchange.
- La UI usa los campos disponibles de `portfolio summary / by_asset`; si faltan trazas de valuación, muestra campos vacíos en vez de inferir datos.
- DecisionEngine y ReallocationEngine siguen dependiendo de señales crudas en algunos flujos; el bloqueo accionable ya existe, pero Sprint 3 debería revisar la propagación completa.

---

## Próximos pasos — Sprint 3

- Definir soporte explícito para CEDEAR, bonos y FX con reglas de pricing separadas.
- Mejorar la clasificación de instrumentos desde ingestion y carga manual.
- Propagar `valuation_status` a todos los motores de decisión y reasignación.
- Agregar endpoints o vistas dedicadas de auditoría de valuación.
- Incorporar tests frontend/E2E para la tabla broker-like.
- Evaluar integración con fuentes broker reales cuando el contrato de datos esté estable.
