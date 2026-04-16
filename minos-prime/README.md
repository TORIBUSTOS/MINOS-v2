# MINOS PRIME

> Sistema de inteligencia patrimonial de TORO

## Estado

**Fase actual:** Especificación completa — Listo para descomposición en bloques de ejecución

## Documentación

| Documento | Estado | Descripción |
|-----------|--------|-------------|
| [VISION.md](VISION.md) | ✅ Validado | Norte estratégico del sistema |
| [MISSION.md](MISSION.md) | ✅ Validado | Alcance y propósito operativo |
| [SPECS.md](SPECS.md) | ✅ Validado | Especificaciones funcionales del MVP |
| [ARCHITECTURE.md](ARCHITECTURE.md) | ✅ Validado | Arquitectura conceptual y técnica |

## Qué es MINOS PRIME

MINOS PRIME es el sistema de inteligencia patrimonial de TORO. Consolida patrimonio disperso entre brokers, bancos, fondos y registros manuales en una única vista coherente, con capa de inteligencia para control, análisis y soporte a la decisión.

No es un tracker de posiciones. Es una plataforma que entiende el patrimonio como sistema y lo convierte en criterio de decisión.

## Capas principales

1. **Consolidación patrimonial** — ingestión, normalización y unificación multi-fuente
2. **Decisión de cartera** — estado general (EXPANSIÓN / NEUTRAL / RIESGO) + insights
3. **Reasignación de capital** — destino sugerido para capital liberado

## Relación con el ecosistema

- **TAUROS** → operatoria financiera de SANARTE (empresa). Sin solapamiento.
- **ARGOS** → señales por activo. MINOS consume señales de ARGOS pero funciona sin él.
- **OIKOS** → conexión futura.

## Frase guía

> MINOS PRIME no solo muestra el patrimonio. Lo entiende.

## Pipeline

- **Rosario (ChatGPT):** Visión, Misión, Specs
- **Claude (CTO):** Validación, Architecture, README, implementación
- **Tori:** Dirección estratégica y decisiones de producto
> Estado: Planning — Esperando VISION.md de Rosario
