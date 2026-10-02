# Revisión de seguridad pre-release (F8)

- **Fecha:** 2026-10-01
- **Alcance:** ROADMAP §8.6 (los cinco puntos) y el checklist §8.7, contra el **binario de release firmado** (no contra el código ni un build de depuración).
- **Dispositivo:** moto g31 (Android 12). El g84 no se usó.
- **Binario:** `tool/build_release.sh`. Primero el de `main` en `c661c60` (minSdk 24); después, con las correcciones de esta revisión, el de esta rama (minSdk 29 y logs de Android eliminados).
- **Relacionado:** [modelo de amenazas](modelo-de-amenazas.md) · [ROADMAP §8](../../ROADMAP.md#8-seguridad-y-privacidad) · [build de release](../guias/build-release.md)

## Resumen

| # | Punto (§8.6) | Resultado |
|---|---|---|
| 1 | Análisis estático con MobSF | ✅ El único hallazgo alto (minSdk 24) se corrigió. Los avisos son falsos positivos o código de terceros que ya no escribe logs (ver abajo) |
| 2 | Tráfico durante una sesión completa | ✅ **0 bytes**: el proceso no puede abrir sockets de red |
| 3 | Manifest final | ✅ Sin permisos reales, backups desactivados, sin `cleartext` ni `debuggable`; solo dos componentes exportados, los dos de la allowlist |
| 4 | Rutas de depuración en release | ✅ No existen en el binario |
| 5 | Corpus malicioso contra el release | ✅ Rechazado o neutralizado, sin cuelgues y con la Biblioteca intacta |

## 1. MobSF (análisis estático)

Se usó MobSF 4.5.4 en un contenedor local (`podman`, escuchando solo en `127.0.0.1`). El APK no salió del equipo.

| Severidad | Hallazgo | Análisis | Decisión |
|---|---|---|---|
| **Alta** | Se instala en Android 7.0 (`minSdk 24`) | Los EPUB son entrada no confiable y se muestran en el **WebView del sistema**. Desde Chrome/WebView 139 (agosto de 2025), el WebView solo se actualiza en **Android 10+**. El propio dispositivo informa `minSdkVersion=29` para su WebView actual. En Android 7–9, el Lector funcionaría sobre un motor sin parches | **Corregido:** `minSdk = 29` (decisión del usuario, 2026-10-01) y nueva comprobación en `tool/check_apk_manifest.py` |
| Aviso | `ProfileInstallReceiver` exportado con el permiso `DUMP` | Es el receptor de AndroidX para perfiles de compilación. `DUMP` es un permiso de firma o privilegiado: solo lo tienen el sistema y `adb shell` | Aceptado. Ya estaba en la allowlist de la guardia |
| Aviso | Lee o escribe en almacenamiento externo | El código es de `file_picker`, que resuelve rutas de Descargas. Silente no pide permisos de almacenamiento: los archivos se eligen con el selector del sistema (SAF) | Aceptado (sin permiso, la API no da acceso) |
| Aviso | «Secretos» en el código | Los 12 son identificadores de compilación: el *snapshot* de Dart, las revisiones del motor de Flutter, el *source id* de SQLite y tablas hexadecimales | Falso positivo |
| Info | La app escribe en el log | Son llamadas a `android.util.Log` de plugins. Algunas de `file_picker`, solo en caminos de error, incluyen un nombre de archivo o una URI | **Corregido:** R8 elimina todas las llamadas a `android.util.Log` del release (`proguard-rules.pro`) |
| Info | Copia al portapapeles | Es la selección de texto de Flutter, que solo se activa cuando la persona copia algo | Aceptado |
| Seguro | Sin rastreadores (0 de 432 conocidos) | — | — |

Otros resultados: el único permiso es `DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`, que añade la plataforma y no da capacidades. La configuración de red no tiene hallazgos y el certificado es el de subida (`CN=NordirWork`).

**Re-escaneo del binario corregido:** ver «Verificación de las correcciones».

## 2. Tráfico de red

La verificación no depende de capturar paquetes, sino de que el sistema **impide** la red:

- **Sin permiso `INTERNET`:** `dumpsys package` muestra solo el permiso de la plataforma.
- **El proceso no está en el grupo `inet` (gid 3003):** en `/proc/<pid>/status`, Silente tiene `Groups: 9997 20370 50370`. Chrome, como referencia, sí tiene 3003. Sin ese grupo, el kernel de Android rechaza cualquier socket de red, también los del WebView y los de las dependencias.
- **Contadores del sistema:** tras una sesión completa (abrir el libro de Silente, importar 8 EPUB, leer, abrir un libro con scripts, abrir un enlace externo hasta la confirmación, exportar una copia y cambiar de tema), `dumpsys netstats detail` tiene **0 entradas** para el UID de Silente. Otras apps sí aparecen.

## 3. Manifest de release

Revisado con `aapt2 dump xmltree` y con la guardia del CI:

- `allowBackup=false`, `fullBackupContent=false` y `dataExtractionRules`, que excluyen todo;
- ni `debuggable` ni `usesCleartextTraffic`;
- exportados: `MainActivity` (el lanzador) y `ProfileInstallReceiver` (protegido por `DUMP`). El `InitializationProvider` de AndroidX no está exportado;
- sin *deep links* ni otros *intent filters*;
- `targetSdk 36`.

**Nuevas comprobaciones en `tool/check_apk_manifest.py`:**
- `minSdk ≥ 29`;
- `debuggable` prohibido.

Se probaron contra el APK antiguo (falla por minSdk) y contra un APK de depuración (falla por `INTERNET`, minSdk y `debuggable`).

## 4. Rutas de depuración

Se buscaron cadenas en `libapp.so` (arm64) del release:

| Cadena | Qué demostraría | Resultado |
|---|---|---|
| `Design system (debug)` | La entrada de Ajustes de la galería de diseño | 0 apariciones |
| `/debug` | La ruta `/debug/design` | 0 |
| `SILENTE_DEBUG_TOOLS` | El flag de compilación | 0 |
| `SILENTE_JS` | El volcado de la consola JS del Lector (puede contener texto del libro) | 0 |

`AppFlags.debugTools` es una constante combinada con `kDebugMode`, así que el compilador elimina todo lo que protege. Las URL del binario son textos de error de librerías y la base local `https://silente.invalid/`. No hay *endpoints* ni configuración remota.

## 5. Corpus malicioso contra el release

Importados uno a uno desde el selector del sistema (`test/fixtures/epubs/generated/`):

| Archivo | Resultado en el g31 |
|---|---|
| `malicious-zip-bomb.epub` | Rechazado: «Este archivo no parece un EPUB seguro, así que no lo añadimos.» |
| `malicious-zip-many-entries.epub` | Rechazado con el mismo mensaje |
| `malicious-zip-slip.epub` | Rechazado con el mismo mensaje |
| `malicious-xxe.epub` | Añadido; la entidad **no se expande** (el título muestra `&xxe;` literal) |
| `malicious-image-bomb-cover.epub` | Añadido con la portada genérica: la portada no se decodifica |
| `malicious-scripted.epub` | Añadido y abierto en el Lector (ver abajo) |
| `malicious-remote-resources.epub` | Añadido. Sin red posible (punto 2) y con la CSP del Lector |
| `valid-simple-epub3.epub` (control) | Añadido y legible |

**Libro con scripts, abierto en el Lector:**
- el texto de control sigue en «Scripts bloqueados (correcto).», así que ni `<script>` ni `onerror` se ejecutaron;
- el enlace `https` pide confirmación y muestra el dominio y la URL completa;
- el enlace `javascript:` no hace nada;
- el formulario no navega.

En todas las pruebas el proceso fue el mismo (sin cierres) y en logcat no apareció ningún `FATAL` ni `ANR`.

## 6. Logs

Se revisaron las 263 líneas de logcat del proceso de Silente durante la sesión. Solo hay mensajes del sistema, del WebView y de `file_picker` (tipos MIME). **No hay** títulos, rutas, contraseñas ni contenido. Tras la corrección del punto 1, las líneas de `file_picker` desaparecen también.

## 7. Cadena de suministro

- `gitleaks git` sobre todo el historial (40 commits): sin secretos.
- `osv-scanner` sobre los `pubspec.lock` y el `package-lock.json` del renderer: sin vulnerabilidades conocidas.

## Verificación de las correcciones

Build de esta rama, firmado (SHA-256 del APK `2f35eeed…cd78`) e instalado sobre el anterior en el g31. Los datos se conservaron:

- **MobSF:**
  - **0 hallazgos altos**; la nota pasa de 54 a 67;
  - siguen los mismos avisos aceptados (ver punto 1);
  - el aviso «la app escribe en el log» persiste porque MobSF solo detecta referencias a la clase `Log`. En el dex no queda ninguna llamada a `Log.v/d/i/w/e/wtf/println`: antes había 265 y ahora 0, comprobado con `dexdump`. Solo queda `getStackTraceString`, que no escribe nada.
- **Guardia:** `tool/check_apk_manifest.py` → `✓ Manifest OK … minSdk=29`.
- **En el dispositivo:**
  - importar `malicious-zip-slip.epub`: rechazado y sin ninguna línea de `file_picker` en logcat;
  - el libro con scripts sigue neutralizado;
  - exportar una copia cifrada (cabecera `UMBRA` de entonces, hoy `SLNTE` según el ADR-011; 118 KB);
  - importarla: con una contraseña incorrecta, «La contraseña no es correcta o la copia está dañada.»; con la correcta, «Importación completada» sin duplicar nada (0 libros, 0 marcadores, 0 reflexiones).
  - Esto cierra el ⚪ de la importación con el build firmado de la [guía de build de release](../guias/build-release.md).
- Archivos de prueba borrados del teléfono al terminar.

## Riesgos residuales

- Los ya aceptados en el [modelo de amenazas §5](modelo-de-amenazas.md#5-riesgos-residuales-aceptados-mvp).
- **Android 7–9 sin soporte:** quien tenga esos dispositivos no podrá instalar Silente. Se acepta porque el Lector depende de un WebView con parches.
- ⚪ **No se evaluó:**
  - el análisis dinámico de MobSF (necesita un emulador con *root*);
  - una captura de paquetes con PCAPdroid o mitmproxy. No hace falta, porque el kernel impide los sockets (punto 2).
