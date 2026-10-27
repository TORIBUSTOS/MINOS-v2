# MINOS: interruptores de interfaz
27/10/2026. Pedido de Tori: inventariar la UI y habilitar módulos mediante valores true/false independientes. Sus ejemplos no constituyen una secuencia obligatoria.

## Configuración
branding/ui-modules.json en TORO; copia pública docs/ui-modules.json.
true muestra la opción; false la oculta de las superficies cubiertas. Editar el booleano y reconstruir con node branding/build.cjs. No hay dependencias automáticas entre interruptores.
No desinstala módulos, elimina datos ni revoca permisos. Las URLs directas y API siguen disponibles; es visibilidad de interfaz, no un control de autorización.

## Inventario
| Interruptor | Superficie | Inicial |
|---|---|---|
| cuentas | Cuentas de Balanz y administración | true |
| carteras | Agrupaciones de cuentas/portfolios | false |
| resumen | Dashboard y patrimonio | false |
| analisis | Insights y estadísticas | false |
| tenencias | Posiciones e instrumentos en cartera | false |
| importacion | Importación y alta de tenencias desde atajos | false |
| movimientos | Operaciones, dividendos y demás actividades | false |
| objetivos | Goals, ahorro y planificación | false |
| asistente | Chat interno y proveedores de IA | false |
| connect | Servicio opcional Wealthfolio Connect | false |
| instrumentos | Catálogo de activos | false |
| clasificaciones | Taxonomías y clasificación | false |
| mercado | Proveedores de precios y acción actualizar cotizaciones | false |
| limites | Límites de aportes | false |
| gastos | Gastos y presupuestos | false |
| extensiones | Addons y navegación aportada por addons | false |
| preferencias | General y apariencia | true |
| respaldos | Exportación y respaldos | true |
| agentes | Agent Access/MCP | true |
| creditos | Acerca de, licencia y créditos | true |

Los ajustes de soporte permanecen visibles para operar la instalación. Cuentas aparece como acceso directo principal.
MCP y n8n no se deshabilitan; habilitar la lectura de cartera es trabajo independiente.

## Cobertura y límites
Se filtra la navegación compartida (sidebar, flotante y móvil), secciones de Settings (desktop y móvil), acciones del launcher y el enlace Connect independiente.
Se conserva la página actual si el usuario llegó por URL directa. No se agregaron redirecciones que interrumpan formularios.
No se afirma cobertura de cada botón interno de una pantalla oculta ni bloqueo de URLs o motores de fondo.
Inventario basado en fuentes oficiales tag v3.11.0: app-navigation.tsx, settings-layout.tsx, app-launcher.tsx, mobile-navbar.tsx y app-sidebar.tsx. El código instalado compilado se contrastó con dichas fuentes.

## Verificación
Pruebas de política para rutas activas/ocultas y atajos. Prueba de independencia: activar tenencias e importación no activa asistente.
Navegación principal compilada evaluada con stubs de iconos: sólo /settings/accounts.
node --check de bundle y Compose config --quiet. HTML y CSS HTTP200 con assets v4.
Inspección visual de esta sesión pendiente por indisponibilidad del navegador interno compartido; actualizar pestaña del usuario.
