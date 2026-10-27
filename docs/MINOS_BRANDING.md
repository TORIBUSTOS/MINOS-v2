# Identidad visual MINOS Capital
Aplicada el 27/10/2026 por pedido de Tori.
- Pestaña: Minos Capital.
- Ingreso: Minos Capital; Tu cartera privada · Powered by Wealthfolio.
- Se conserva el logo upstream hasta seleccionar el logo oficial de Minos.
- Runtime de aplicación y datos: Wealthfolio oficial 3.11.0. Personalización limitada a frontend estático.

## Construcción
branding/build.cjs toma una copia limpia de /app/dist del contenedor oficial en branding/upstream y genera branding/dist.
Reemplaza únicamente título/descripción de ingreso en el chunk inglés y título HTML/manifest. Renombra referencias de chunks JS con sufijo minos-v1 para evitar caché immutable anterior.
Los binarios generados no se versionan. Requieren reconstrucción y verificación al actualizar la imagen. El script aborta si cambia el texto esperado.
compose.override.yml monta branding/dist de sólo lectura en /app/dist. La ruta absoluta corresponde al host TORO; no usar /host/docker del contenedor de herramientas.
El código fuente upstream corresponde al tag v3.11.0: https://github.com/wealthfolio/wealthfolio/tree/v3.11.0.
La personalización no elimina créditos, licencia ni páginas About.

## Verificación
HTTP 200; HTML con título Minos Capital; entrada JS y chunk de auth 200; texto Minos Capital y Powered by Wealthfolio servidos; login 200 y tres cuentas presentes.
Verificación visual automatizada pendiente: navegador de esta sesión bloqueó recarga por política de acceso.
Actualizar la pestaña del usuario para comprobar apariencia.

## Rollback
Retirar compose.override.yml y ejecutar docker compose up -d para volver al frontend oficial. No borrar ni recrear volúmenes.

El script de referencia se conserva en wealthfolio-branding-build.cjs; en la instalación se ubica como branding/build.cjs junto a upstream/ y dist/.
