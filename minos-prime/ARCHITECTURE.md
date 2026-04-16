# MINOS PRIME — ARCHITECTURE

## 1. Visión general

MINOS PRIME es un sistema de inteligencia patrimonial que integra múltiples fuentes, consolida el patrimonio del usuario y genera soporte a la decisión y reasignación de capital.

La arquitectura separa claramente tres niveles:

1. Consolidación patrimonial
2. Decisión sobre la cartera
3. Reasignación de capital

---

## 2. Capas del sistema

### 2.1 Data Ingestion Layer

Entrada de datos desde:

- APIs
- CSV / Excel
- carga manual
- capturas visuales

Responsabilidad:

- recibir datos
- identificar tipo de fuente
- enviar a procesamiento

---

### 2.2 Processing & Normalization Layer

Transforma datos crudos en datos consistentes.

Funciones:

- limpieza
- normalización de activos
- unificación de tickers (vía Unified Ticker Layer)
- detección de duplicados
- validación previa

Output:
→ dataset patrimonial consistente

---

### 2.3 Unified Ticker Layer

Capa integrada dentro de Processing & Normalization.

Funciones:

- unificar tickers entre fuentes y carteras
- eliminar duplicados por símbolo
- detectar presencia en múltiples carteras
- asignar señal única por ticker

Output:
→ tabla unificada de activos con presencia y estado

---

### 2.4 Portfolio Engine (Consolidación)

Núcleo patrimonial.

Responsable de:

- manejar múltiples carteras
- mantener separación por cartera
- consolidar patrimonio total
- calcular distribución y exposición

Soporta:

- múltiples carteras por fuente
- múltiples fuentes simultáneamente

---

## 3. Capa de inteligencia

### 3.1 Intelligence Layer (Base)

Interpreta el estado de los activos y del patrimonio.

Funciones:

- estado por ticker (BUY / HOLD / SELL)
- detección de concentración
- exposición por moneda
- inconsistencias
- alertas básicas

Motor v1:

- reglas simples
- thresholds

Preparado para:

- integración futura con ARGOS

---

### 3.2 Portfolio Decision Engine

Interpreta la cartera completa.

Input:

- composición de cartera
- señales por activo
- distribución
- liquidez

Evalúa:

- concentración
- exposición
- coherencia
- activos débiles
- activos fuertes

Output:

1. Estado de cartera:
   - EXPANSIÓN
   - NEUTRAL
   - RIESGO

2. Insights:
   - observaciones clave (2 a 4 puntos)

3. Acción sugerida:
   - reducir riesgo
   - mantener
   - rotar

---

### 3.3 Capital Reallocation Engine

Responsable de sugerir qué hacer con el capital.

Se activa cuando:

- hay activos en SELL
- hay liquidez disponible
- hay capital liberable

Evalúa:

- nivel de liquidez
- oportunidades existentes
- activos fuertes en cartera
- oportunidades nuevas

Propone:

- reforzar posiciones
- rotar capital
- mantener liquidez
- nuevas entradas

Principio:
MINOS no vende sin sugerir destino del capital.

---

## 4. Captura visual

### Flujo

1. usuario sube imagen
2. sistema interpreta
3. detecta datos
4. propone estructura
5. usuario valida
6. se integra al sistema

Entrada: vía Data Ingestion Layer, como cualquier otra fuente.

---

## 5. Templates de extracción

- permiten reutilizar formatos visuales recurrentes
- mejoran precisión y velocidad
- evitan reprocesar desde cero

Flujo:

- primera vez → guardar template
- siguientes → reconocer y aplicar

---

## 6. Persistencia y estado

El sistema debe mantener estado entre sesiones.

Requerimientos:

- almacenamiento persistente del patrimonio consolidado
- historial de cargas y cambios
- trazabilidad por fuente y fecha
- templates de captura guardados

Definición técnica del mecanismo de persistencia: pendiente (fase de implementación).

---

## 7. Modelo de datos conceptual

Cada registro incluye:

- fuente
- cartera
- activo
- ticker
- cantidad
- moneda
- valuación
- fecha
- tipo de carga (API / archivo / manual / captura)
- estado de validación

---

## 8. Outputs

- patrimonio total
- distribución por activo y por plataforma
- exposición por moneda
- estado de cartera (EXPANSIÓN / NEUTRAL / RIESGO)
- tabla unificada de tickers
- alertas e inconsistencias
- oportunidades y reasignación sugerida

---

## 9. Principios de diseño

- separación entre datos y decisión
- validación antes de persistir
- tolerancia a datos incompletos
- independencia de servicios externos
- arquitectura modular
- MINOS funciona sin ARGOS (reglas internas), pero se potencia con él

---

## 10. Evolución futura

- integración con ARGOS (señales por activo)
- automatización de ingestión
- mejora de captura visual (OCR, reconocimiento de estructura)
- conexión con OIKOS
- análisis avanzado

---

## 11. Resumen

MINOS PRIME está estructurado en tres capas clave:

1. **Consolidación patrimonial** — integrar, normalizar y unificar
2. **Decisión de cartera** — interpretar estado y generar insights
3. **Reasignación de capital** — sugerir destino del capital liberado

Esto permite pasar de ver el patrimonio a entenderlo y actuar sobre él.
---

### 2.2 Processing & Normalization Layer

Transforma datos crudos en datos consistentes.

Funciones:

- limpieza
- normalización de activos
- unificación de tickers (vía Unified Ticker Layer)
- detección de duplicados
- validación previa

Output:
→ dataset patrimonial consistente

---

### 2.3 Unified Ticker Layer

Capa integrada dentro de Processing & Normalization.

Funciones:

- unificar tickers entre fuentes y carteras
- eliminar duplicados por símbolo
- detectar presencia en múltiples carteras
- asignar señal única por ticker

Output:
→ tabla unificada de activos con presencia y estado

---

### 2.4 Portfolio Engine (Consolidación)

Núcleo patrimonial.

Responsable de:

- manejar múltiples carteras
- mantener separación por cartera
- consolidar patrimonio total
- calcular distribución y exposición

Soporta:

- múltiples carteras por fuente
- múltiples fuentes simultáneamente

---

## 3. Capa de inteligencia

### 3.1 Intelligence Layer (Base)

Interpreta el estado de los activos y del patrimonio.

Funciones:

- estado por ticker (BUY / HOLD / SELL)
- detección de concentración
- exposición por moneda
- inconsistencias
- alertas básicas

Motor v1:

- reglas simples
- thresholds

Preparado para:

- integración futura con ARGOS

---

### 3.2 Portfolio Decision Engine

Interpreta la cartera completa.

Input:

- composición de cartera
- señales por activo
- distribución
- liquidez

Evalúa:

- concentración
- exposición
- coherencia
- activos débiles
- activos fuertes

Output:

1. Estado de cartera:
   - EXPANSIÓN
   - NEUTRAL
   - RIESGO

2. Insights:
   - observaciones clave (2 a 4 puntos)

3. Acción sugerida:
   - reducir riesgo
   - mantener
   - rotar

---

### 3.3 Capital Reallocation Engine

Responsable de sugerir qué hacer con el capital.

Se activa cuando:

- hay activos en SELL
- hay liquidez disponible
- hay capital liberable

Evalúa:

- nivel de liquidez
- oportunidades existentes
- activos fuertes en cartera
- oportunidades nuevas

Propone:

- reforzar posiciones
- rotar capital
- mantener liquidez
- nuevas entradas

Principio:
MINOS no vende sin sugerir destino del capital.

---

## 4. Captura visual

### Flujo

1. usuario sube imagen
2. sistema interpreta
3. detecta datos
4. propone estructura
5. usuario valida
6. se integra al sistema

Entrada: vía Data Ingestion Layer, como cualquier otra fuente.

---

## 5. Templates de extracción

- permiten reutilizar formatos visuales recurrentes
- mejoran precisión y velocidad
- evitan reprocesar desde cero

Flujo:

- primera vez → guardar template
- siguientes → reconocer y aplicar

---

## 6. Persistencia y estado

El sistema debe mantener estado entre sesiones.

Requerimientos:

- almacenamiento persistente del patrimonio consolidado
- historial de cargas y cambios
- trazabilidad por fuente y fecha
- templates de captura guardados

Definición técnica del mecanismo de persistencia: pendiente (fase de implementación).

---

## 7. Modelo de datos conceptual

Cada registro incluye:

- fuente
- cartera
- activo
- ticker
- cantidad
- moneda
- valuación
- fecha
- tipo de carga (API / archivo / manual / captura)
- estado de validación

---

## 8. Outputs

- patrimonio total
- distribución por activo y por plataforma
- exposición por moneda
- estado de cartera (EXPANSIÓN / NEUTRAL / RIESGO)
- tabla unificada de tickers
- alertas e inconsistencias
- oportunidades y reasignación sugerida

---

## 9. Principios de diseño

- separación entre datos y decisión
- validación antes de persistir
- tolerancia a datos incompletos
- independencia de servicios externos
- arquitectura modular
- MINOS funciona sin ARGOS (reglas internas), pero se potencia con él

---

## 10. Evolución futura

- integración con ARGOS (señales por activo)
- automatización de ingestión
- mejora de captura visual (OCR, reconocimiento de estructura)
- conexión con OIKOS
- análisis avanzado

---

## 11. Resumen

MINOS PRIME está estructurado en tres capas clave:

1. **Consolidación patrimonial** — integrar, normalizar y unificar
2. **Decisión de cartera** — interpretar estado y generar insights
3. **Reasignación de capital** — sugerir destino del capital liberado

Esto permite pasar de ver el patrimonio a entenderlo y actuar sobre él.
