# Estilos visuales Minos · v8

Tori pidió tres direcciones más marcadas: Púrpura TORO, Lado oscuro y Armadura dorada (inspiración caballeros de Atena). Se conserva Minos clásico. No se incorporan personajes, emblemas ajenos ni afirmaciones sobre la cartera.

El selector **Estilo visual** está en el encabezado de Ajustes en escritorio; en Cuentas y Apariencia aparece también para pantallas pequeñas. Cada estilo se combina con Claro/Oscuro/Sistema del selector oficial de Apariencia. Púrpura es el estilo predeterminado si no hay elección guardada.

- Púrpura: fondos violeta, acentos lavanda, contornos suaves y tipografía sans.
- Lado oscuro: grafito, acentos carmesí, controles más angulares.
- Armadura dorada: azul noche/dorado en oscuro, marfil/oro en claro, tipografía serif en títulos y sans en operación.
- Clásico: paleta petrol/papel previa, conservada como alternativa.

## Configuración única

`branding/themes.json`: `skins.<id>.enabled`, `label`, tokens comunes del estilo y `modes.light/dark`. `defaultSkin` determina el inicio. `branding/assets/tokens.json` sigue centralizando la marca y el recurso del símbolo. Los estilos reutilizan fuentes que ya distribuye Wealthfolio; no se agregaron dependencias ni fuentes de terceros.

El atributo raíz `data-minos-theme` identifica el estilo. `skins.cjs` genera CSS y selector desde el registro; ninguna paleta se dispersa en componentes. La preferencia local se guarda como `minos-visual-theme`, independiente de la preferencia oficial de luminosidad. Sin acceso a almacenamiento funciona durante la sesión; un valor inválido o un estilo deshabilitado vuelve al predeterminado. Se sincroniza entre selectores y pestañas. Para agregar estilos: registrar una entrada, habilitarla y reconstruir; no editar el componente del selector. `build.cjs --check` prepara recursos sin publicarlos.

## Evidencia 27/10/2026

Build por etapas y node --check pasaron. Pruebas aisladas comprobaron inicialización de los cuatro estilos, preferencia inválida/ausente, persistencia, validación de selección y sincronización de eventos/pestañas; mantienen intacta la clase nativa dark. Se verificaron24 combinaciones de contraste (texto principal/secundario, superficies y botones) en los seis modos nuevos: mínimo5.38:1. No equivale a auditoría de todos los estados nativos.

En despliegue: rutas Cuentas/Apariencia y CSS/JSv8 HTTP200; autenticación200; tres cuentas existentes; API sin sesión401; Compose válido. Datos y módulos no se modificaron. Revisión visual posterior de escritorio/móvil y recorrido de teclado pendientes por falta de acceso al browser interno. No afirmar revisión visual completa ni detector Impeccable exitoso.

Respaldo anterior: backups/skins-before-20261027. Se conservan recursos previos para sesiones abiertas.
