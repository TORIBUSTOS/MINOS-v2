# MINOS Capital: landing y plataforma

Estado de trabajo al 31/10/2026. Este documento recoge la dirección conversada con Tori; no acredita un despliegue ni aprueba un diseño final.

## Dos piezas distintas

- **Landing pública:** presenta MINOS Capital, su identidad y visión. Puede incluir un enlace «Acceder a la plataforma».
- **Plataforma privada:** consulta y gestión de la cartera, posiciones, movimientos y resultados. La línea de base documentada es Wealthfolio self-hosted, sin ejecución de órdenes. Consultar el README para el estado registrado el 27/10; verificar el estado real antes de operar.

Comparten marca, pero tienen funciones y desarrollos separados. El código FastAPI/Next.js de este repositorio es un antecedente, no la aplicación Wealthfolio desplegada. Este repositorio contiene documentación y recursos de personalización, no una copia completa verificada de esa instalación.

## Dirección creativa de la landing

La intro propuesta recorre un laberinto oscuro en primera persona y desemboca en un salón financiero monumental. Un hilo dorado guía el recorrido. El salón combina arquitectura clásica, mármol negro, detalles dorados, mapa mundial, pantallas financieras y una presencia discreta de Minos. Los acentos verdes y rojos se reservan para algunas cotizaciones. La referencia conversada propone una toma continua de aproximadamente ocho segundos, con giros suaves y llegada pausada.

El cierre utiliza «MINOS» grande y «Capital» debajo, centrados. El título se agrega como capa independiente del video. El diseño, el movimiento y el material final requieren revisión de Tori; no se consideran aprobados por este documento.

## Material pendiente

- Localizar el video de referencia `gemini_generated_video_f33a521f.mp4` y la imagen del salón financiero sin título. Su disponibilidad y contenido no fueron verificados en este repositorio.
- Confirmar si existe código actual de la landing o si debe iniciarse. Este repositorio no demuestra la existencia de una landing terminada.
- Definir el destino real del enlace a la plataforma y su integración sin exponer datos privados.
- Conservar separadas la dirección de la landing y la propuesta anterior de ingreso/carga de la aplicación, descrita en [MINOS_ENTRY_DIRECTION.md](MINOS_ENTRY_DIRECTION.md).

## Para continuar

Revisar este documento, el [README](../README.md) y [MINOS_ENTRY_DIRECTION.md](MINOS_ENTRY_DIRECTION.md). Recuperar e inspeccionar los originales antes de diseñar o implementar la experiencia. No incluir credenciales, carteras ni información financiera privada en este repositorio público.
