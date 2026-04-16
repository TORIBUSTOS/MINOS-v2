# MINOS PRIME

> Sistema de inteligencia patrimonial de TORO

## Documentación

La especificación completa vive en el repo Trinity:
→ [github.com/TORIBUSTOS/Trinity](https://github.com/TORIBUSTOS/Trinity) — `projects/minos-prime/`

| Doc | Descripción |
|-----|-------------|
| VISION.md | Norte estratégico |
| MISSION.md | Alcance y propósito operativo |
| SPECS.md | Especificaciones funcionales del MVP |
| ARCHITECTURE.md | Arquitectura conceptual y técnica |
| MINOS_BN_BREAKDOWN.md | Bloques de ejecución |

## Setup

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001
```

## Estado

**Fase:** Sprint 1 — TRACK A: Data Layer
**BN activo:** BN-001 — Scaffold

Ver [CLAUDE.md](CLAUDE.md) para comandos, convenciones y boundaries.
