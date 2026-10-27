# Identidad visual MINOS Capital
Actualizada 27/10/2026 por pedido de Tori.

## Ingreso
- Título de pestaña y encabezado: Minos Capital.
- Símbolo M y paleta institucional de la base editable de marca v0.1 de Drive: ink #172B32, petrol #24545B, paper #F4F2EC, sand #C7B58A.
- Contraseña e Ingresar en español. Atribución Powered by Wealthfolio en pie separado.
- CSS limitado a .minos-login con tokens semánticos. No cambia las pantallas internas ni contratos de autenticación.
- El logo existente en Drive está documentado como propuesta editable, no como marca definitiva.

## Reproducción y actualización
En la instalación TORO, colocar el script como branding/build.cjs, login.css junto al script y assets/symbol.svg. El original tokens.json se conserva como referencia.
Copiar /app/dist limpio de la imagen Wealthfolio 3.11.0 a branding/upstream y ejecutar node branding/build.cjs. Se genera branding/dist.
El script valida anclas de login, corrige tanto el texto hardcodeado del encabezado como la traducción y renombra referencias de JS con .minos-v3 para invalidar caché.
Montar dist de sólo lectura en /app/dist mediante el override de Compose. Recrear el contenedor tras reconstruir: el script reemplaza el directorio dist.
Al cambiar imagen, revisar anclas y reconstruir. El script aborta ante estructura diferente.
Fuente upstream: https://github.com/wealthfolio/wealthfolio/tree/v3.11.0.
Conservar los créditos y licencia originales. El CSS, script y símbolo se versionan junto a este documento.

## Validación
node --check del build y de los dos bundles cambiados; docker compose config --quiet.
HTTP200 para HTML, CSS, símbolo y JS. Login200 y tres cuentas presentes.
La captura del usuario evidenció que la primera revisión cambió descripción pero no el encabezado hardcodeado; corregido expresamente en v2/v3.
Verificación visual desktop/móvil pendiente: navegador de esta sesión bloqueado por política de acceso. La CSS incluye estilos responsive, focus-visible, disabled y altura reducida; no se presentan como pruebas visuales realizadas.

## Rollback
Retirar el override de frontend y ejecutar docker compose up -d para usar dist oficial. Preservar /data y todos los volúmenes.
