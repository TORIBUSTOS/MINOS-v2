# MINOS PRIME — SPECS

## 1. Contexto

MINOS PRIME representa la evolución de una base previa orientada al diagnóstico por activo hacia un sistema de consolidación patrimonial multi-fuente con capa de inteligencia.

La versión anterior resolvía análisis por activo. MINOS PRIME amplía ese alcance hacia una visión patrimonial completa, integrando información dispersa y transformándola en una base operativa para control y decisión.

---

## 2. Objetivo del sistema

MINOS PRIME debe consolidar patrimonio, no solo listar activos.

Debe permitir responder:
- qué patrimonio existe;
- dónde está;
- cómo se distribuye;
- cómo evoluciona;
- qué decisiones requieren atención.

---

## 3. Alcance del MVP

Incluye:
- consolidación multi-fuente;
- carga manual y por archivo;
- soporte de capturas;
- validación antes de guardar;
- normalización básica;
- lectura patrimonial consolidada;
- capa inicial de inteligencia;
- perfiles de captura.

No incluye:
- automatización total;
- soporte universal de plataformas;
- interpretación perfecta de cualquier imagen;
- ejecución automática.

---

## 4. Fuentes de datos

### 4.1 Estructuradas
- APIs
- CSV / Excel
- exports
- registros manuales

### 4.2 Visuales
- capturas
- tickets
- balances
- resúmenes

### 4.3 Principio
Estructurado = base  
Visual = complemento operativo

---

## 5. Modelo de consolidación

### 5.1 Unidades
- activos
- posiciones
- saldos
- cuentas
- plataformas
- moneda

### 5.2 Resultado
Vista patrimonial total con:
- distribución
- exposición
- evolución

### 5.3 Normalización
- nombres de activos
- tickers
- moneda
- duplicados
- trazabilidad

---

## 6. Capa de inteligencia

Debe:
- detectar concentración
- exposición por moneda
- inconsistencias
- cambios
- alertas
- estado general

Basado en:
- reglas
- métricas
- comparaciones

---

## 7. Captura visual

### Flujo
1. subir imagen
2. interpretar
3. proponer datos
4. validar
5. guardar

Nunca guardar automático sin validación.

---

## 8. Perfiles de captura / templates

### Función
Reutilizar formatos visuales conocidos.

### Flujo
- primera vez → guardar template
- siguientes → reconocer y aplicar

### Objetivo
- velocidad
- precisión
- menor costo

---

## 9. Validación y trazabilidad

Cada dato debe tener:
- fuente
- tipo
- fecha
- validación

Tipos:
- API
- archivo
- manual
- captura

---

## 10. Outputs

- patrimonio total
- distribución
- exposición
- posiciones
- alertas
- estado general

---

## 11. Límites del MVP

- no cubrir todo
- no automatizar todo
- no predicción avanzada
- no contabilidad completa

---

## 12. Éxito v1

- consolidación real
- baja fricción
- claridad patrimonial
- base escalable

---

## 13. Consolidación por cartera y unificación de tickers

### 13.1 Modelo de carteras

MINOS debe permitir múltiples carteras dentro de una misma fuente.

Ejemplo:
- Balanz | Cartera 1
- Balanz | Cartera 2

Cada cartera:
- es independiente
- tiene nombre editable
- mantiene sus posiciones

---

### 13.2 Vista consolidada

Permite:
- suma patrimonial
- distribución total
- exposición

---

### 13.3 Vista unificada de tickers

No suma nominales.  
Unifica activos.

Ejemplo:

- Balanz 1 → MELI 10  
- Balanz 2 → MELI 2  

Resultado:

- MELI  
- presente en 2 carteras  
- estado: BUY  

---

### 13.4 Tabla sugerida

| Ticker | Presente en | Cartera(s) | Estado |
|--------|------------|-----------|--------|
| MELI   | 2          | Balanz 1, Balanz 2 | BUY |
| NVDA   | 1          | Balanz 1 | HOLD |

---

### 13.5 Separación clave

A. Datos por cartera  
B. Lectura unificada por ticker  

---

### 13.6 Propósito

- simplificar lectura
- evitar duplicaciones
- facilitar decisiones

---

## 14. Definición final

MINOS PRIME consolida patrimonio, integra múltiples fuentes y transforma información dispersa en una base clara para decidir.
---

### 14.2 Vista consolidada patrimonial

MINOS PRIME debe consolidar todas las carteras en una vista global del patrimonio, permitiendo:

- distribución total por activo;
- distribución por plataforma;
- exposición por moneda;
- lectura agregada del patrimonio.

Esta vista puede incluir sumas de valuación y exposición, pero no debe perder trazabilidad de origen por cartera.

---

### 14.3 Vista unificada de tickers

Además de la consolidación patrimonial, el sistema debe ofrecer una vista simplificada basada en activos únicos.

Esta vista no debe sumar nominales entre carteras, sino identificar la presencia de cada ticker dentro del sistema.

#### Objetivo

Permitir una lectura estratégica rápida del conjunto de activos sin duplicaciones por cartera.

#### Funcionamiento

- se identifican todos los tickers presentes en el sistema;
- se eliminan duplicados por símbolo;
- se registra en cuántas y cuáles carteras aparece cada activo;
- se asigna una señal o estado único por ticker;
- se construye una tabla unificada de activos.

#### Ejemplo

Si un activo aparece en múltiples carteras:

- Balanz Cartera 1 → MELI 10
- Balanz Cartera 2 → MELI 2

La vista unificada no mostrará "MELI 12".

Mostrará:

- Ticker: MELI
- Presencia: 2 carteras
- Estado: BUY (u otro según lógica del sistema)

---

### 14.4 Estructura sugerida

| Ticker | Presente en | Cartera(s) | Estado |
|--------|------------|-----------|--------|
| MELI   | 2          | Balanz 1, Balanz 2 | BUY |
| NVDA   | 1          | Balanz 1 | HOLD |
| TSLA   | 1          | Balanz 2 | SELL |

---

### 14.5 Separación conceptual

El sistema debe diferenciar claramente entre:

A. Datos patrimoniales por cartera:
- cantidades;
- valuación;
- moneda;
- composición específica;

B. Capa de lectura unificada por ticker:
- activo único;
- presencia transversal;
- señal simplificada;
- lectura estratégica.

---

### 14.6 Propósito

Esta funcionalidad permite:

- evitar duplicación visual de activos;
- simplificar la lectura del sistema completo;
- identificar rápidamente activos relevantes;
- facilitar la toma de decisiones a nivel patrimonial;
- separar la contabilidad de posiciones de la interpretación estratégica.

---

### 14.7 Consideraciones

- la señal por ticker debe definirse por lógica central (no por cartera individual);
- la vista unificada no reemplaza la vista patrimonial ni la vista por cartera;
- ambas deben coexistir como capas complementarias del sistema.

## 15. Motor de decisión patrimonial

MINOS PRIME no debe limitarse a analizar activos individuales. Debe interpretar el estado de la cartera en su conjunto y generar soporte a la decisión a nivel patrimonial.

### 15.1 Objetivo

Transformar información consolidada en decisiones accionables sobre la cartera del usuario.

### 15.2 Inputs

- composición de la cartera
- distribución por activo
- distribución por moneda
- presencia de activos en múltiples carteras
- estado de cada ticker (BUY / HOLD / SELL)
- cambios recientes

### 15.3 Evaluaciones

El sistema debe analizar:

- concentración por activo
- concentración por sector (si aplica)
- exposición por moneda
- capital inmovilizado
- duplicación entre carteras
- balance entre riesgo y liquidez
- coherencia general del portafolio

### 15.4 Output

MINOS debe devolver:

1. Estado general de la cartera:
   - EXPANSIÓN
   - NEUTRAL
   - RIESGO

2. Insights:
   - observaciones claras (2 a 4 puntos)

3. Acción sugerida:
   - ejemplo: reducir exposición
   - ejemplo: no agregar riesgo
   - ejemplo: rotar capital

### 15.5 Principio

MINOS no recomienda activos en abstracto.  
Recomienda acciones sobre la cartera real del usuario.

### 15.6 Relación con ARGOS

- ARGOS provee señales por activo
- MINOS usa esas señales para tomar decisiones patrimoniales
- MINOS debe poder funcionar sin ARGOS mediante reglas internas

## 16. Motor de oportunidades y reasignación de capital

MINOS PRIME no debe limitarse a señalar activos débiles o posiciones en estado SELL. Debe también asistir en la decisión sobre qué hacer con el capital disponible o potencialmente liberado.

### 16.1 Objetivo

Evitar que la cartera derive en liquidez ociosa por falta de criterio de reasignación.

### 16.2 Disparadores

Este módulo debe activarse cuando exista alguna de estas condiciones:

- activos en estado SELL;
- posiciones candidatas a reducción;
- exceso de liquidez;
- capital sin asignación clara;
- oportunidades relevantes detectadas dentro o fuera de la cartera actual.

### 16.3 Función

MINOS debe evaluar posibles destinos del capital y proponer alternativas razonables, incluyendo:

- reforzar posiciones existentes con buena señal;
- rotar hacia activos más sólidos;
- mantener liquidez táctica cuando no existan oportunidades claras;
- sugerir incorporación de nuevos activos si corresponde.

### 16.4 Principio

MINOS no debe recomendar vender sin ofrecer contexto de reasignación.

La decisión patrimonial completa requiere contemplar tanto la salida de capital como su posible destino.

### 16.5 Resultado esperado

El sistema debe poder devolver:

- capital potencialmente liberable;
- nivel actual de liquidez;
- nivel estimado de liquidez posterior;
- oportunidades prioritarias;
- acción sugerida sobre ese capital.

### 16.6 Relación con el sistema de señal

- el estado BUY / HOLD / SELL ayuda a detectar salidas o refuerzos;
- la capa de oportunidades patrimoniales define posibles usos del capital;
- el objetivo es equilibrar defensa, liquidez y crecimiento.
