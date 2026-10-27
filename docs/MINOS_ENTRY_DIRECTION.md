# MINOS Capital · dirección visual de trabajo
Actualizado27/10/2026 por Rosario a pedido de Tori.

## Autoridad y fuentes
Tori es la autoridad de diseño. Leer este archivo y branding/references/GUIA_DE_MARCA_DRIVE.md antes de generar o revisar UI con Impeccable o TORO Frontend Operativo.
La guía original de Drive es una propuesta editable0.1 del21/10, NO una identidad definitiva aprobada. Los estilosv8 son pruebas: Tori considera que púrpura/lado oscuro son variaciones de dashboard y sólo el dorado resulta parcialmente convincente. No declararlos diseños aprobados.
La preferencia actual necesita riqueza de composición, planos, superficies, tipografía y detalles de marca, además de color. El dorado es punto de exploración, no aceptación final.

## Archivos de referencia existentes
- Guía Drive: https://drive.google.com/file/d/1KJaP_ReqF95I65Xhj4S4eEXCW1Q2Gexp/view
- Brandboard visual inspeccionado: https://drive.google.com/file/d/1-9mwfp-9WS6X4ikek75tc7w_FADmZ2Yo/view
- Fuente HTML de brandboard: https://drive.google.com/file/d/1dUuBhWBsjq8xlDF8JZUbKPmKiSgXWaPf/view
- Tokens fuente Drive: https://drive.google.com/file/d/1uIk9qpDoc4xZ4z86qykc7XvHMo3-Odiz/view
- Activos locales: branding/assets/logo.svg, symbol.svg y tokens.json.
- Estilos implementados: branding/themes.json, app.css, login.css; registro y selector: skins.cjs.
Conservar archivos de origen, atribución, procedencia y condición provisional. El logo es reemplazable, no redibujarlo incidentalmente.

## Inicio · hilo dorado y laberinto
Pedido explícito de Tori: usar la imagen existente de un laberinto con líneas doradas que conducen a un templo y una estatua monumental sentada. El hilo/camino dorado debe encenderse progresivamente y funcionar como loading de entrada de Minos.
El original de esa imagen todavía NO fue localizado ni inspeccionado. No sustituirlo silenciosamente ni afirmar que está incorporado. La descripción anterior viene de Tori, no de una imagen verificada.
La escena marca el ingreso: oscuridad, orientación del camino por luz dorada y llegada al templo/estatua. La animación debe conservar esa geografía y sentido, no usar brillo aleatorio.
Propuesta técnica a validar al tener el original: ilustración como base y recorrido vectorial SVG alineado como capa independiente. Animar avance por longitud de trazado y encendido acumulativo; controlar todo desde tokens/rutas reemplazables.
La señal de carga depende de hitos reales de inicialización; si no se conoce porcentaje, usar progreso por etapas sin publicar porcentajes ficticios. Al estar lista la app, completar recorrido y dejar entrar sin demora obligatoria. Ante error o timeout, conservar recuperación y mensaje de estado.
Dar una versión estática/reducida con prefers-reduced-motion y estado de carga accesible; no destellos ni animación que impida entrar.
El arte y trazado deben tener punto focal/encuadre configurables para desktop y móvil.

## Relación entre inicio y app
El inicio puede tener expresión cinematográfica. Dentro de la cartera, trasladar proporciones, lenguaje de bordes, materiales y jerarquía con legibilidad de datos y controles familiares.
No repetir una ilustración monumental detrás de tablas por defecto. No inventar rendimientos, movimientos o datos para llenar espacio.

## Tokens que deben producir efecto real
Ampliar el sistema existente para superficies, contornos, elevación, tipografía, densidad y estados. Cada token nuevo debe ser consumido; brand-detail y surface-outline-style en v8 requieren revisión porque app.css no los usa.
Documentar alcance y muestras claro/oscuro. Verificar el render real de escritorio/móvil antes de declarar cierre visual. Sintaxis/HTTP/contraste son evidencias parciales.
