# Guía: Publicar Silente en Google Play

- **Audiencia:** publicación
- **Última actualización:** 2026-10-01

## Objetivo

Llevar Silente desde el build firmado hasta Google Play, paso a paso y con una validación en cada paso. La guía sigue el orden real del proceso:

1. cuenta de desarrollador;
2. firma y AAB;
3. ficha de la tienda;
4. formularios de la Play Console;
5. pruebas cerradas;
6. revisión y producción.

> **Estado (2026-10-01):** NordirWork **aún no tiene cuenta** de Google Play (P-11). Esta guía se ha escrito con los requisitos oficiales comprobados en esa fecha. Los pasos que dependen de la Play Console aparecen como ⚪ no evaluados hasta que se recorran por primera vez; quien los recorra corrige aquí lo que cambie.

## Requisitos de Google Play que afectan a Silente

Comprobados en la documentación oficial el 2026-10-01:

| Requisito | Qué exige | Estado en Silente |
|---|---|---|
| **API objetivo** | Desde el 31 de agosto de 2026, las apps nuevas y las actualizaciones deben apuntar a **Android 16 (API 36)** o superior; se puede pedir una extensión hasta el 1 de noviembre de 2026 | ✅ `targetSdkVersion 36`, comprobado con `aapt2 dump badging` sobre el APK de release |
| **Versión mínima** | Decisión propia (revisión de seguridad de F8): el WebView solo recibe parches en Android 10+ | ✅ `minSdk 29`, comprobado por `tool/check_apk_manifest.py`; en la ficha, «Requiere Android 10 o superior» |
| **Formato** | Las apps nuevas se publican como **Android App Bundle** (AAB) | ✅ `tool/build_release.sh` genera el AAB |
| **Play App Signing** | Google guarda la clave con la que se firma la app y el equipo sube con su **clave de subida** | ✅ La clave de subida existe (`~/.android-keys/`, ver [Build de release](build-release.md)) |
| **Cuenta personal nueva** | Las cuentas personales creadas después del 13 de noviembre de 2023 deben hacer una **prueba cerrada con al menos 12 testers inscritos de forma continua durante 14 días** antes de pedir acceso a producción | ⚪ Depende del tipo de cuenta (ver el paso 1) |
| **Cuenta** | Pago único de **25 USD** con tarjeta (no se aceptan prepago); verificación de identidad con documento oficial y tarjeta a nombre del titular; las cuentas personales verifican también que tienen un dispositivo Android con la app Play Console | ⚪ |
| **Política de privacidad** | Una **URL pública** con la política, enlazada en la ficha | ⚪ Falta publicar los textos en una URL (ver el paso 4) |
| **Play Billing** (solo si algún día se cobra) | Desde el 31 de agosto de 2026, las apps nuevas y las actualizaciones que usen la biblioteca de facturación deben usar la **versión 8 o posterior** | No aplica: el MVP no cobra ([plan de monetización](../producto/monetizacion.md)) |

Fuentes: «Target API level requirements for Google Play apps», «Get started with Play Console» (crear la cuenta), «App testing requirements for new personal developer accounts» y «Play Billing Library deprecation FAQ», todas en la ayuda oficial de Google Play y de Android Developers.

## Requisitos previos

- El build de release firmado funciona en el moto g31 ([Build de release](build-release.md)).
- `tool/check_legal_placeholders.py` y `tool/check_apk_manifest.py` pasan (el script de release los ejecuta).
- Copia de seguridad de `~/.android-keys/` fuera del equipo. **Si se pierde la clave de subida**, se puede pedir a Google que la restablezca (con Play App Signing). Aun así, el proceso lleva días y bloquea las actualizaciones mientras dura.

## Pasos

### 1. Cuenta de desarrollador ⚪

1. Decidir el tipo de cuenta:
   - **Organización (recomendada para NordirWork):**
     - ⚪ pide verificar la organización (en la fecha de esta guía no se comprobó qué documentos exige; se espera un número D-U-N-S y la web de la organización);
     - **no** le aplica la prueba cerrada de 12 testers × 14 días, que es solo para cuentas personales.
   - **Personal:**
     - el alta es más rápida;
     - pero obliga a la prueba cerrada antes de producción (paso 6);
     - y en la ficha aparece el nombre legal de la persona.
2. Registrarse en la Play Console con la cuenta de Google de NordirWork, pagar los 25 USD y completar la verificación de identidad.
3. Correo de contacto de desarrollador: `pqrs@nordirwork.com`, el mismo de los textos legales.

**Validación:** la Play Console permite «Crear aplicación».

### 2. Build y firma ✅ (local) / ⚪ (Play)

```bash
tool/build_release.sh          # AAB + APK firmados con la clave de subida
```

1. Comprobar que el script termina con `OK` y que imprime el SHA-256 del certificado de subida.
2. En la Play Console → **Crear aplicación**:
   - nombre «Silente», idioma predeterminado español;
   - tipo «Aplicación», gratuita.
3. Al subir el primer AAB, aceptar **Play App Signing** con una clave generada por Google. Nuestra clave queda como clave de **subida**.
4. Guardar los símbolos de `build/symbols/<versión>/` junto con la versión publicada. Sin ellos, los informes de errores ofuscados no se pueden leer.

**Validación:**
- en «Integridad de la app», el certificado de subida coincide con el SHA-256 que imprimió el script;
- `versionCode` es mayor que el del último AAB subido (`pubspec.yaml`, `version: x.y.z+N`).

> «Gratuita» no se puede cambiar a «de pago» más adelante. Silente es gratuita y Silente+ se ofrecería dentro de la app ([plan de monetización](../producto/monetizacion.md)), así que es la opción correcta.

### 3. Ficha de la tienda ⚪

| Elemento | Requisito | Origen en el repo |
|---|---|---|
| Nombre | Hasta 30 caracteres | «Silente» |
| Descripción breve | Hasta 80 caracteres | Lema: «Tu espacio de lectura» + lector EPUB con diario privado |
| Descripción completa | Hasta 4000 caracteres | Basada en el [libro de Silente](libro-de-silente.md) y los [manuales](../manual-usuario/) |
| Icono | 512 × 512 PNG | Exportar desde `assets/brand/` ([Marca e iconos](marca-e-iconos.md)) |
| Gráfico de funciones | 1024 × 500 | ⚪ Por diseñar |
| Capturas de teléfono | Mínimo 2 | Capturas del g31 **con libros de dominio público y reflexiones inventadas** |

Las reglas de las capturas son las de la documentación: nunca datos privados ni texto con copyright.

**Validación:** la descripción no promete nada que la app no haga. En particular:
- nada de sincronización ni de Silente+ como disponible;
- nada de «gratis para siempre» sin matices.

### 4. Textos legales en una URL pública ⚪

Google Play exige la URL de la política de privacidad, y también se enlaza desde el formulario de seguridad de los datos.

1. Publicar `assets/legal/politica-de-privacidad.md` y `terminos-de-uso.md`, **con el mismo texto que trae la app**, en una web de NordirWork (p. ej. `nordirwork.com/silente/privacidad`).
2. Cuando cambie un texto, se cambia en la app y en la web en el mismo release.

**Validación:** la URL abre sin iniciar sesión y su «Última actualización» coincide con la de la app.

### 5. Formularios de «Contenido de la aplicación» ⚪

| Formulario | Respuesta para Silente | Por qué |
|---|---|---|
| **Política de privacidad** | La URL del paso 4 | — |
| **Anuncios** | No contiene anuncios | Sin SDK de publicidad (CLAUDE.md, seguridad) |
| **Acceso a la app** | Toda la funcionalidad está disponible sin restricciones | No hace falta cuenta (AC-011) |
| **Seguridad de los datos** | **No recoge ni comparte datos** | No tiene permiso de red y todo se queda en el teléfono. Si las respuestas cambian, el modelo de amenazas también debe cambiar |
| **Público objetivo** | Mayores de 13 años (o de 18), sin dirigirse a menores | Evita la política de Familias. La política de privacidad ya dice que no recoge datos de menores |
| **Clasificación de contenido** (IARC) | Cuestionario: app de referencia o lectura, sin violencia ni compras, sin compartir contenido entre usuarios | La persona importa sus propios EPUB; Silente no ofrece contenido |
| **Apps de noticias, salud, etc.** | No aplica | — |

Al responder **Seguridad de los datos**, hay que contrastar cada respuesta con la realidad, no con lo que se pretende:
- `tool/check_apk_manifest.py` confirma que no hay permiso `INTERNET`;
- la revisión de seguridad de F8 (ROADMAP §8.6) confirma que no hay tráfico.

Si algún día se añade red (sincronización o Silente+), este formulario **se rehace antes** de publicar esa versión.

**Validación:** la Play Console no marca nada pendiente en «Contenido de la aplicación».

### 6. Pruebas antes de producción ⚪

1. **Prueba interna** (hasta 100 testers, disponible en minutos):
   - subir el AAB;
   - añadir al equipo;
   - instalar desde Play en el g31 y repetir la [matriz de QA](matriz-de-qa.md).
2. **Prueba cerrada**, obligatoria **solo con cuenta personal**:
   - lista de al menos **12 testers** que acepten la invitación y sigan inscritos **14 días seguidos**;
   - después, en el «Panel», pedir acceso a producción respondiendo el cuestionario sobre la prueba.
3. Revisar el **informe previo al lanzamiento** (Play lo ejecuta en dispositivos reales) y corregir los fallos y avisos de accesibilidad.

**Validación:**
- la app se instala desde Play y abre el libro de Silente en el primer arranque;
- la reanudación funciona igual que con el APK local.

### 7. Producción ⚪

1. Crear la versión de producción con el mismo AAB que pasó las pruebas.
2. Notas de la versión, sacadas del `CHANGELOG.md` y escritas para la persona lectora.
3. Elegir los países y, si se quiere, un **lanzamiento por fases** (p. ej. 20 %).
4. Enviar a revisión. La primera revisión puede tardar varios días.

## Checklist previo a cada publicación

- [ ] CI en verde en `main`; tests y CI local pasan.
- [ ] `version` del `pubspec.yaml` incrementado (nombre y `versionCode`).
- [ ] `tool/build_release.sh` termina en `OK`: firma de subida, manifest sin permisos y textos legales completos.
- [ ] Build firmado probado en el g31: abrir un libro, reanudar, una reflexión, exportar e importar una copia.
- [ ] Símbolos de `build/symbols/<versión>/` guardados.
- [ ] Textos legales de la web iguales a los de la app.
- [ ] Formulario de seguridad de los datos sigue siendo cierto (sin cambios de red ni de datos).
- [ ] `targetSdkVersion` cumple el requisito vigente de API objetivo (se revisa cada año, antes del 31 de agosto).
- [ ] Notas de la versión en español, sin datos privados.

## Verificación

- La ficha muestra «Sin anuncios» y la sección de seguridad de los datos dice «No se recogen datos».
- La versión instalada desde Play tiene el mismo comportamiento que el build verificado en el g31.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| «Tu app apunta a un nivel de API demasiado bajo» | `targetSdkVersion` por debajo del requisito vigente | Actualizar Flutter/AGP y comprobar con `aapt2 dump badging` |
| «El AAB está firmado con una clave incorrecta» | Se firmó con la clave de depuración o con otra | `tool/build_release.sh` falla sin la clave; no subir builds de `flutter build` a secas |
| «Version code ya usado» | No se incrementó `+N` en `pubspec.yaml` | Incrementarlo y volver a compilar |
| No aparece el botón de acceso a producción | Cuenta personal sin los 12 testers × 14 días | Completar la prueba cerrada (paso 6) |
| Rechazo por la política de privacidad | URL caída, con inicio de sesión o distinta de la app | Paso 4 |
