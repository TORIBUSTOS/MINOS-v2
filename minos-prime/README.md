# MINOS PRIME

> Sistema de inteligencia patrimonial de TORO

## Estado actual

**MINOS PRIME v2:** Sprint 3 — Live Market Layer cerrado.

MINOS ya cuenta con:

- consolidacion patrimonial multi-fuente;
- ingestion por archivo, carga manual, PDF/capturas y parser Balanz;
- valuacion broker-grade para instrumentos soportados;
- trazabilidad de precios y estado de valuacion;
- inteligencia BUY/HOLD/SELL subordinada a calidad de valuacion;
- capa live con variacion diaria, impacto diario y frescura `LIVE/CACHE/STALE/UNAVAILABLE`;
- dashboard con sesion live y heatmap diario.

## Documentos fundadores

Estos documentos son la base conceptual del producto. Se preservan aunque el codigo avance, porque definen intencion, limites y criterio de continuidad.

| Documento | Importancia | Uso |
|-----------|-------------|-----|
| [VISION.md](VISION.md) | Fundacional | Norte estrategico de MINOS |
| [MISSION.md](MISSION.md) | Fundacional | Proposito operativo y alcance |
| [SPECS.md](SPECS.md) | Fundacional | Contrato funcional del MVP |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Fundacional | Arquitectura conceptual y tecnica |

## Gobierno de ejecucion

| Documento | Estado | Uso |
|-----------|--------|-----|
| [MINOS_BN_BREAKDOWN.md](MINOS_BN_BREAKDOWN.md) | Vigente | Mapa de BNs, sprints y estado ejecutivo |
| [SPRINT_2_SUMMARY.md](SPRINT_2_SUMMARY.md) | Cerrado | Resumen broker-grade valuation core |
| [SPRINT_3_LIVE_MARKET_LAYER.md](SPRINT_3_LIVE_MARKET_LAYER.md) | Cerrado | Scope y cierre de Live Market Layer |
| [SPRINT_2_EXECUTION_ORDER.md](SPRINT_2_EXECUTION_ORDER.md) | Historico | Orden de ejecucion y failover de Sprint 2 |
| [execution_log.txt](execution_log.txt) | Historico | Bitacora granular de ejecucion |

## Que es MINOS PRIME

MINOS PRIME consolida patrimonio disperso entre brokers, bancos, fondos y registros manuales en una vista coherente, con capa de inteligencia para control, analisis y soporte a la decision.

No es un tracker de posiciones. Es una plataforma que entiende el patrimonio como sistema y lo convierte en criterio de decision.

## Capas principales

1. **Consolidacion patrimonial** — ingestion, normalizacion y unificacion multi-fuente.
2. **Verdad financiera** — valuacion broker-grade, trazabilidad de pricing y estados de confianza.
3. **Live Market Layer** — movimiento diario, impacto en cartera y frescura de mercado.
4. **Decision de cartera** — estado general, insights y senales accionables solo cuando la valuacion es confiable.
5. **Reasignacion de capital** — destino sugerido para capital liberado.

## Relacion con el ecosistema

- **TAUROS** -> operatoria financiera de SANARTE. Sin solapamiento.
- **ARGOS** -> senales por activo. MINOS puede consumirlas, pero funciona sin ARGOS.
- **OIKOS** -> conexion futura.

## Frase guia

> MINOS PRIME no solo muestra el patrimonio. Lo entiende.
