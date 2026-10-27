# Minos · pasada Impeccable · 27/10/2026

Se aplicaron las guías oficiales Impeccable4.8.0 de Operate, adapt, polish, layout y typeset. Fuente: https://github.com/pbakaus/impeccable/tree/cli-v4.8.0 , commit414603bf14c7a344edb466bb1f85690c77ce8b7d. Es la versión oficial consultada del26/10; no se instaló una skill personal ni hooks automáticos.

Evidencia inicial: captura aportada por Tori a zoom reducido (980×609) y fuentes actuales de Wealthfolio3.11.0. Se hizo revisión independiente de jerarquía, ancho, zoom, texto largo y áreas táctiles. El cargador automático se descargó con comprobación de checksum, pero no pudo ejecutar el motor por Permission denied; se siguió la ruta manual prevista por SKILL.md, leyendo docs/PRD.md, DESIGN_SYSTEM.md, THEMES.md y guías oficiales. No se ejecutó detector ni se declara un resultado automático limpio.

Cambios publicados v7:
- Ajustes aprovecha la ventana con márgenes fluidos y máximo generoso centrado para evitar listas excesivamente largas en4K.
- La marca acompaña al encabezado; Cuentas y Añadir cuenta lideran el recorrido.
- El bloque hero y su eyebrow se reemplazan por cantidad/monedas compactas basadas en cuentas reales.
- Tipografía propia en rem, selección/caret/foco desde tokens, elevación simple.
- Nombres y grupos largos permiten contracción y quiebre; el menú conserva sus handlers.
- Buscador y controles táctiles reciben mínimos de44px. Se conserva navegación móvil y orden DOM.
- Se elimina maximum-scale/user-scalable=no del viewport, conservando safe areas.

Verificado: build por etapas; node --check de generadores y JS resultante; existencia de recursos; prueba de componente con nombre/grupo sintéticos largos y preservación de callbacks de acciones; rutas de Ajustes y recursos v7 HTTP200; autenticación200; tres cuentas existentes; API sin sesión401; Compose válido. CSS incorpora breakpoints móvil, intermedio y ancho, pero esos layouts NO fueron recorridos visualmente.

Pendiente: render posterior en claro/oscuro,320px/intermedio/ancho/zoom, teclado, menús abiertos, estados vacío/error/carga y gestos reales. La sesión de browser interno no es accesible desde esta ejecución. No confundir las comprobaciones de fuente y HTTP con cierre visual o accesibilidad completa.

Marca: branding/assets/tokens.json. Semántica/temas/geometría: branding/themes.json. Reglas: branding/app.css y login.css. Backups de la capa previa: backups/ui-polish-before-20261027. Datos de cartera y módulos habilitados no se modificaron.
