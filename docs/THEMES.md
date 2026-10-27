# Temas Minos Capital

La identidad usa una única capa semántica conectada a los componentes oficiales de Wealthfolio 3.11.0, sin cambiar cartera, importaciones, autenticación ni interruptores de módulos.

- `assets/tokens.json`: nombre, paleta base, tipografías y ruta del símbolo. Para cambiar el símbolo, reemplazar el archivo indicado por `asset.symbol`; el mismo recurso se usa en ingreso, navegación, carga y favicon.
- `themes.json`: registro claro/oscuro, colores semánticos, espaciado, radios, tamaños, foco y movimiento. `$paper` y similares referencian la paleta base. Los tokens específicos de oscuro tienen valores propios.
- `theme.cjs`: traduce esos tokens a las variables existentes de Wealthfolio y agrega la introducción de Cuentas con datos del listado actual. No suma saldos ni mezcla monedas.
- `app.css` y `login.css`: consumen variables, sin colores ni medidas de marca dispersos en componentes.
- `build.cjs`: ejecutarlo desde `branding/` con los archivos anteriores y `ui-modules.cjs/json` juntos, conservando los nombres originales de este directorio. En el repositorio público el archivo de entrada se llama `wealthfolio-branding-build.cjs`; copiarlo como `build.cjs` al instalar. `node branding/build.cjs --check` prepara `dist-next` sin publicar. Sin `--check` publica recursos primero e índice al final; conserva versiones anteriores para sesiones abiertas.

En la app: Configuración → Apariencia → Claro, Oscuro o Sistema. Se reutiliza la preferencia persistida oficial, sin un segundo selector ni almacenamiento paralelo. `default` documenta la dirección inicial; la preferencia de usuario oficial prevalece. Los temas claro y oscuro permanecen habilitados para respetar ese selector. Una dirección nueva se agrega primero al registro; exponer una tercera elección requiere ampliar también el selector oficial. Para retirar una dirección se debe migrar su preferencia antes de deshabilitarla.

La dirección anterior del ingreso queda preservada en el historial git y en el respaldo de despliegue. Se conserva la atribución Powered by Wealthfolio y los créditos originales.

Validación 27/10/2026 por Rosario: compilación sobre upstream oficial y anclas verificadas, sintaxis JS, referencias locales, autenticación HTTP y contraste de texto/acciones de ambos temas ≥4.5:1. No hubo revisión visual interactiva en navegador de escritorio o móvil; la sesión del browser interno no está accesible desde esta ejecución. El CSS incluye adaptación móvil y foco visible; su recorrido visual queda pendiente.

Las anclas de los bundles son específicas de esta versión. Una actualización que cambie componentes debe detener el build para revisar la adaptación, sin publicar un parche parcial.

## Recarga de rutas internas
Se corrigió el 404 de navegación directa con middleware Traefik minos-spa: sólo rutas de UI conocidas se sirven desde el índice; /api, /mcp y assets quedan fuera. Verificado HTTP200 en /settings/accounts y /settings/appearance, API sin sesión401, autenticación200 y tres cuentas existentes preservadas. No hay cambios a /data.
