# Funcionalidad: Marca (logo, icono y splash)

- **Estado:** Disponible. Logo de **Silente** desde el 2026-10-01 ([ADR-011](../adr/011-cambio-de-nombre-a-silente.md), etapa 1), elegido y validado por el usuario frente a Moon+ Reader. El nombre visible de la app cambia en la etapa 2.
- **Fase del ROADMAP:** F7 (bloque 6) · ADR-011, etapa 1
- **Última actualización:** 2026-10-01
- **Relacionado:** ROADMAP D-07, H-07, P-05 · [ADR-011](../adr/011-cambio-de-nombre-a-silente.md) · [Design system](design-system.md) · [El libro de Umbra](libro-de-silente.md) · [guía](../guias/marca-e-iconos.md) · comparación [`comparativa-logos-silente.png`](../mockups/comparativa-logos-silente.png)

## 1. Objetivo

Dar a la app una identidad propia y coherente: el mismo símbolo en el icono del teléfono, en el arranque, dentro de la app y en las portadas de sus libros. Desde el ADR-011, ese símbolo es el de Silente y deja atrás la luna de Umbra, que se parecía al logo de Moon+ Reader.

## 2. Alcance

- **Incluye:**
  - **Logo vectorial** (`brand/silente-mark.svg`), dirección C3, «puntos suspensivos»:
    - un libro abierto en oro (`#C8A86B`, la página derecha con opacidad 0,82);
    - encima, dos líneas lila (`duskLavender`) que se acortan y se apagan, terminadas en «…».
    - Significa que el ruido se apaga y el texto termina en silencio. Sin luna ni estrellas.
  - **Variante monocromática** (`brand/silente-mark-mono.svg`): el mismo dibujo en blanco, conservando las opacidades, para los iconos temáticos de Android 13+.
  - **Icono de Android:**
    - adaptativo (API 26+): el logo sobre `#121014`, dentro de la zona segura para que ninguna máscara lo recorte, con capa monocromática;
    - clásico (API < 26): el logo sobre un cuadrado redondeado.
  - **Splash nativo:**
    - API 31+: el logo sobre el fondo del tema (`parchmentWhite` en claro, `#121014` en oscuro) con la SplashScreen API;
    - antes de API 31: el mismo logo centrado en `launch_background`.
  - **En la app:** el logo en la primera pantalla de la bienvenida y en Acerca de (`SilenteMark`).
  - **Portadas** del libro de la app y del libro técnico, con el logo. El texto de las portadas cambia en la etapa 3.
- **No incluye:**
  - el logotipo con el nombre como imagen: el nombre siempre es texto (Lora), accesible y localizable;
  - un icono animado en el splash.

## 3. Criterios de aceptación

| ID | Criterio | Estado | Cómo se verifica |
|---|---|---|---|
| ADR-011 | Logo sin luna ni estrellas, solo con los colores de la marca | ✅ | `silente_brand_test.dart` (colores, título, monocromo blanco, sin rastro del logo anterior) |
| ADR-011 | Todo el dibujo dentro de la zona segura (radio 61 de 100) | ✅ | Comprobación en `make_mark.py`: 60,0 de 61 |
| D11 | No se confunde con Moon+ Reader a tamaño real | ✅ | [Comparación](../mockups/comparativa-logos-silente.png) sobre la captura del usuario: «se distingue bien» (usuario, 2026-10-01) |
| P-05 | El icono de la app muestra el logo, sin recortes | ✅ | moto g31 (release firmado): «Información de la aplicación» dibuja el icono adaptativo en círculo, completo |
| P-05 | El splash usa el fondo del tema | ✅ | moto g31 (Android 12), modo claro y oscuro |
| P-05 | El splash muestra el logo en Android 12+ | ⚪ no evaluado | En el moto g31 la ventana de arranque aparece sin icono con cualquier forma de lanzarla, igual que con el logo anterior, aunque el APK incluye `windowSplashScreenAnimatedIcon`. Pendiente de otro dispositivo; el g84 está excluido de las pruebas |
| P-05 | Icono temático (Android 13+) | ⚪ no evaluado en el dispositivo | El g31 tiene Android 12. La versión monocroma se revisó renderizada (a 48 px se lee bien) |
| P-05 | Logo en la bienvenida y en Acerca de, decorativo para los lectores de pantalla | ✅ | `silente_mark_test.dart` + moto g31 con el tema claro y el oscuro |
| P-12 | Portadas de los libros con el logo | ✅ | `silente_book_test.dart` y `silente_tec_test.dart` + generadores |

## 4. Diseño técnico

- **Fuente:** `brand/make_mark.py` (Python estándar).
  - Dibuja el logo en una rejilla de 200 × 200: dos rectángulos redondeados, tres círculos y dos hojas con curvas cúbicas.
  - **Falla si algo se sale de la zona segura**: un círculo de radio 61 alrededor del centro.
  - Escribe los dos SVG con `viewBox` de 400, escalando ese círculo al de radio 190.
- **Rasterizado:** `brand/make_brand_assets.sh` (ImageMagick 7 + librsvg) genera:
  - `mipmap-*/ic_launcher{,_foreground,_monochrome}.png`;
  - `drawable-*/splash_icon.png` (288 dp, con el contenido dentro del círculo de 192 dp);
  - `assets/brand/{,2.0x/,3.0x/}silente-mark.png` (96 dp).
  - Todo en PNG de 8 bits por canal.
- **Recursos Android escritos a mano** (sin cambios en la etapa 1):
  - `mipmap-anydpi-v26/ic_launcher.xml`;
  - `values{,-night}/colors.xml`;
  - `values-v31` y `values-night-v31/styles.xml`;
  - `drawable{,-v21}/launch_background.xml`.
- **Flutter:** `lib/shared/widgets/silente_mark.dart` (`SilenteMark`, con `ExcludeSemantics`), usado en `onboarding_screen.dart` y `settings_pages.dart`.
- **Dependencias nuevas:** ninguna.

## 5. Decisiones

- **Cambio de logo (ADR-011):** la luna con estrellas sobre un libro se parecía al icono de Moon+ Reader. Las direcciones consideradas fueron A (una S que pasa página), B (una pausa con marcapáginas) y C (el ruido que se apaga); el usuario eligió C y, de sus tres variantes, C3.
- **Sin `flutter_launcher_icons` ni `flutter_native_splash`.** Los recursos son pocos y estándar.
- **Iconos en PNG, no en *vector drawable*:** se mantiene la tubería existente, con todas las densidades generadas.
- **Fondo del icono `#121014`:** el oro y el lila destacan sobre el oscuro, como en la app.

## 6. Seguridad y privacidad

- Sin red, permisos ni componentes nuevos: la guardia de manifest del APK de release sigue en verde (`minSdk=29`, sin permisos).

## 7. Pruebas

| Tipo | Archivo | Qué cubre |
|---|---|---|
| Unitaria | `test/shared/silente_brand_test.dart` | SVG (colores, título, monocromo, sin la marca antigua); PNG generados con el tamaño de cada densidad; nada apunta a `umbra-mark` |
| Unitaria / widget | `test/shared/silente_mark_test.dart` | Variantes 1x/2x/3x empaquetadas; tamaño; decorativo para los lectores de pantalla |
| Widget | `test/features/onboarding/…`, `test/features/settings/…` | La bienvenida y Acerca de siguen funcionando con el logo |
| Unitaria | `silente_book_test.dart`, `silente_tec_test.dart` | Las portadas nuevas pasan el inspector y los libros están al día |
| Manual | moto g31 (release firmado) | Icono adaptativo, fondo del splash, bienvenida y Acerca de con los dos temas |

## 8. Limitaciones conocidas y trabajo futuro

- **Tamaños muy pequeños:** a 24 px, los «…» casi desaparecen. A partir de 48 px se leen bien.
- **Splash e icono temático:** falta verificar el icono del splash en Android 12+ y el icono temático de Android 13+ en otro dispositivo.
- **Libros ya añadidos:** un libro de la app añadido antes de este cambio conserva su portada anterior (limitación ya documentada en su ficha).
- **Etapas pendientes del ADR-011:**
  - el nombre visible y el identificador (etapa 2);
  - el texto de las portadas y los libros (etapa 3).
