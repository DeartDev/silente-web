# Capturas de la web

- **Estado:** ✅ Revisadas (LP-11). Tomadas el 2026-10-02.
- **Relacionado:** spec §5 y §6.3; fuentes en [`src/capturas/`](../src/capturas/); conversión en [`tools/make_assets.py`](../tools/make_assets.py).

## Cómo se tomaron

| Dato | Valor |
|---|---|
| Dispositivo | moto g31, Android 12, por `adb` |
| App | Silente 0.1.0 (`com.nordirwork.silente`) |
| Temas | Claro y oscuro, con `cmd uimode night no/yes`; la app y el Lector en «Sistema» / «Como la app» |
| Barra de estado | Recortada: los 100 px de arriba (su alto real en el g31) |
| Botón flotante del menú de accesibilidad | Ocultado durante la sesión y restaurado al terminar |
| Fuentes | `src/capturas/{claro,oscuro}/*.jpg`, 540 × 1150 (la mitad de la resolución del g31), sin metadatos |

La web sirve cada captura en WebP:

- **En la página:** 240 y 432 px de ancho. Con «Sistema», un `<picture>` elige la variante del tema del sistema. Con «Claro» u «Oscuro» en el interruptor (spec L-07), el CSS muestra la variante elegida, que solo se descarga entonces.
- **En la vista ampliada** (L-08): 432 y 540 px. Se descarga al abrirla.

Las fuentes miden 540 px de ancho, así que en pantallas de alta densidad la vista ampliada se ve algo suave. Para más nitidez habría que repetir las capturas a resolución completa (1080 px). Para regenerar los WebP: `python3 tools/make_assets.py shots`.

## Revisión (spec §6.3)

| Captura | Qué muestra | Libros y textos | ✓ |
|---|---|---|---|
| `lector-pagina` | El comienzo del capítulo primero de *Don Quijote* en el Lector | Proyecto Gutenberg n.º 2000, dominio público | ✅ |
| `biblioteca-inicio` | «Continuar leyendo» con *Don Quijote* y los cuatro libros en «Mis libros» | *Don Quijote* (Gutenberg 2000), *El sombrero de tres picos* (Gutenberg 29506), *Lazarillo de Tormes* (Gutenberg 320) y *El libro de Silente*. Las portadas son las que genera Gutenberg | ✅ |
| `lector-ajustes` | El panel «Ajustes de lectura» sobre *Don Quijote*: desplazamiento, pasar página, tamaño, fuente, interlineado, alineación y márgenes | *Don Quijote* | ✅ |
| `diario-editor` | «Nueva reflexión», escrita en el capítulo primero de *Don Quijote*, sin teclado | Reflexión de ejemplo, escrita para la captura (sin tildes, por la limitación de `adb input text`) | ✅ |
| `ajustes-exportar` | El diálogo «Exportar mis datos» sobre Ajustes, con los campos de contraseña vacíos | — | ✅ |
| `libro-de-silente-portada` | La portada de *El libro de Silente*, con el logo y el lema | *El libro de Silente* (incluido en la app) | ✅ |

En ninguna captura hay notificaciones, nombres, cuentas ni datos del teléfono. Tampoco hay reflexiones reales.

Las capturas antiguas de `docs/referencias/capturas/` (copia del manual de la app) ya no se usan. Tenían un texto de prueba en el Diario, un libro de prueba en los ajustes de lectura y un libro de licencia no verificada en la Biblioteca.
