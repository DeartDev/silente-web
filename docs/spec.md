# Landing page de Silente

- **Estado:** Especificación validada por el usuario (2026-10-02), incluida L-03: la web vive en un proyecto aparte y público, `DeartDev/silente-web`. No hay nada implementado ni desplegado.
- **Fase del ROADMAP:** posterior a F8. Resuelve el pendiente «textos legales en una URL pública» (§8.7) y el paso 4 de la [guía de publicación en Google Play](referencias/publicacion-play-store.md).
- **Última actualización:** 2026-10-02
- **Relacionado:**
  - [Contrato de dockerización de nomad_server (anexo 96)](referencias/nomad-96-contrato-de-dockerizacion.md), en el repositorio `nomad_server`;
  - [Política de privacidad](../legal/politica-de-privacidad.md) y [términos de uso](../legal/terminos-de-uso.md);
  - [Glosario](referencias/glosario.md), [marca](referencias/marca.md), design system (tokens en [app_colors.dart](referencias/app_colors.dart));
  - [Plan de monetización](referencias/monetizacion.md) y capturas del manual de usuario en [referencias/capturas/](referencias/capturas/).


> **Origen de este documento.** Es la copia de `docs/producto/landing-page.md` del repositorio de la app (`DeartDev/silente`, PR #50, 2026-10-02). **Desde aquí, esta copia es la especificación viva de la web**; la de la app queda como registro de la decisión y enlazará a este repositorio.
>
> Las rutas que nombran archivos de la app se refieren a `DeartDev/silente` (en local, `~/Proyectos/Personal/silente`). Sus copias en este proyecto:
>
> | En la app | Aquí |
> |---|---|
> | `assets/legal/*.md` | [`legal/`](../legal/) |
> | `brand/silente-mark*.svg` | [`brand/`](../brand/) |
> | `assets/fonts/` (TTF variables + OFL) | [`fonts/`](../fonts/) (falta convertir a WOFF2) |
> | `lib/core/theme/app_colors.dart` | [`docs/referencias/app_colors.dart`](referencias/app_colors.dart) |
> | `docs/manual-usuario/capturas/` (las seis del §5) | [`docs/referencias/capturas/`](referencias/capturas/) (sin revisar, LP-11) |
> | `tool/check_legal_placeholders.py`, `tool/check_brand_name.py` | [`docs/referencias/`](referencias/) (adaptar a este repositorio) |
> | Anexo 96 de `nomad_server` y sus plantillas | [`docs/referencias/nomad-*`](referencias/) |

## 1. Objetivo

Una web pública, pequeña y estática que:

1. **Presente Silente** a quien todavía no lo tiene: qué es, para quién es y en qué se diferencia.
2. **Publique los textos legales** en una URL pública y estable, con **el mismo texto que trae la app**. Es un requisito de Google Play (ficha de la tienda y formulario *Data Safety*) y el último punto abierto del checklist de seguridad (ROADMAP §8.7).
3. **Lleve a Google Play** cuando la app esté publicada. Hasta entonces, dice «Próximamente en Google Play» y no recoge nada.
4. **Practique lo que predica.** La web cumple las mismas reglas de privacidad que la app: sin analítica, sin cookies, sin recursos de terceros y sin formularios.

## 2. Alcance

**Incluye:**

- Página de inicio (`/`) con las secciones del §5.
- Política de privacidad (`/privacidad`) y términos de uso (`/terminos`), generados desde `assets/legal/`.
- Página 404 propia.
- Endpoint de salud (`/salud`) para el healthcheck.
- Tema claro y oscuro según el sistema.
- Despliegue en `nomadservernw` cumpliendo el anexo 96 (§8).

**No incluye:**

- blog, noticias o *changelog* público;
- formularios: ni contacto, ni lista de espera, ni boletín. El contacto es un enlace `mailto:`;
- cuentas, pagos o descarga directa del APK. La única vía de instalación es Google Play;
- analítica de cualquier tipo, incluida Cloudflare Web Analytics;
- versiones en otros idiomas: solo español, como la app;
- documentación técnica pública. «Silente Tec» y `docs/` no se publican.

## 3. Decisiones

### 3.1 Decisiones del usuario

| # | Decisión | Decisión | Por qué |
|---|---|---|---|
| L-01 | **Nombre de host** | `silente.nordirwork.com` | El ápice `nordirwork.com` (y `www`) ya lo reclama otro proyecto del servidor. El contrato publica todo lo demás en un subdominio, y `silente` no aparece en ningún compose conocido. Verificar en el servidor con `grep -rn 'Host(' /srv/nomad/*/docker-compose.yml` antes de desplegar |
| L-02 | **Nombre del proyecto en el servidor** | `silente` | Es el directorio `/srv/nomad/silente`, el prefijo de los contenedores y el nombre del router de Traefik. El contrato recomienda que coincida con el subdominio |
| L-03 | **Dónde vive el código** | ✅ **Proyecto aparte y público, `DeartDev/silente-web`** (usuario, 2026-10-02) | Ver §3.2. La primera propuesta era una carpeta `web/` en este repositorio |
| L-04 | **Capturas de pantalla** | Las del manual (`docs/manual-usuario/capturas/`), revisadas una a una | Solo pueden mostrar libros de dominio público o el libro de Silente, y ninguna reflexión personal (§6.3) |
| L-05 | **Ruta de los textos legales** | `https://silente.nordirwork.com/privacidad` y `/terminos` | La guía de Play proponía `nordirwork.com/silente/privacidad`, pero el ápice pertenece a otro proyecto. Si se acepta, se actualiza la guía |
| L-06 | **Mención de Silente+** | Sección breve, «Próximamente», sin precios | Las decisiones M-01…M-04 del [plan de monetización](referencias/monetizacion.md) siguen abiertas: no se anuncia nada que no esté decidido |

### 3.2 L-03: carpeta `web/` o proyecto aparte

El contrato de nomadservernw marca la diferencia: en producción todo se construye y se sirve **dockerizado**, y `deploy.sh` hace `git pull` del repositorio entero en `/srv/nomad/silente/codigo/` en cada despliegue. Con eso, la comparación queda así:

| Criterio | Carpeta `web/` en `DeartDev/silente` | Proyecto aparte `DeartDev/silente-web` |
|---|---|---|
| Acceso del servidor al código | El repositorio es **privado**: hace falta una deploy key en el servidor, con lectura de **todo** el código de la app | Puede ser **público** (no tiene secretos: todo lo que contiene se publica en la web). `git pull` sin credenciales |
| Lo que se clona en el servidor | Todo Silente: código Flutter, corpus EPUB, `docs/`, Silente Tec (~175 MB de trabajo, 14 MB de historial) para servir unos cientos de KB | Solo la web |
| Contexto de `docker build` | Todo el repositorio; depende de un `.dockerignore` correcto para no meter código privado en la imagen | Pequeño y sin riesgo de fugas |
| CI | Cada cambio de la web pasa por el CI de Flutter (~15 min) y cada cambio de la app «toca» el repositorio que despliega la web | CI propio de segundos: build de la imagen, tests del sitio, Lighthouse |
| Ciclo de versiones | Atado a la app (`pubspec.yaml`, CHANGELOG, ramas protegidas) | Independiente: la web puede cambiar sin una versión de la app y al revés |
| Textos legales | Una sola fuente, sin sincronizar | Copia en `silente-web/legal/` + **guardia de sincronización** (abajo) |
| Logo y fuentes | Compartidos | Copiados una vez; cambian muy poco |
| Encaje con el contrato | Funciona, pero con piezas de más (clave, `.dockerignore` crítico) | Es el caso normal del anexo 96: un repositorio, un `codigo/`, un `Dockerfile` |

**Decisión (usuario, 2026-10-02): proyecto aparte, `DeartDev/silente-web`, público.** La única ventaja real de `web/` es no duplicar los textos legales, y se resuelve con una guardia barata. A cambio, el proyecto aparte quita del servidor el acceso al código privado de la app (mínimo privilegio, ROADMAP §8.1) y deja el despliegue dockerizado en su forma más simple.

**Guardia de sincronización de los textos legales:**

- **Fuente de verdad:** `assets/legal/` en `DeartDev/silente`, que es lo que lleva la app.
- **En `DeartDev/silente`:** un script nuevo, `tool/check_legal_sync.py`, compara `assets/legal/*.md` con los mismos archivos de `silente-web` (descargados del repositorio público en el CI). Si difieren, el CI avisa de que hay que llevar el cambio a la web. Es una comprobación del CI; la app sigue sin red.
- **En `DeartDev/silente-web`:** el build falla si los textos tienen marcadores pendientes o no tienen la línea «Última actualización».
- **Procedimiento:** cuando cambian los textos legales, el mismo día se abren dos PR, uno en la app y otro en la web. Así la fecha de la web nunca va por detrás de la que muestra la app.

### 3.3 Decisiones técnicas propuestas

| Decisión | Propuesta | Alternativas descartadas |
|---|---|---|
| Tipo de sitio | **Estático**, generado en el build de la imagen | Un CMS o un servidor de aplicación: no hay nada dinámico que servir y cada pieza móvil es superficie de ataque |
| Generador | **Script propio en Python** (estándar + `markdown`) que rellena plantillas HTML y convierte `assets/legal/*.md` | Astro o Hugo: añaden un ecosistema entero para tres páginas. El proyecto ya genera los EPUB con Python (`tool/silente_book/`) |
| Servidor web | **`nginxinc/nginx-unprivileged:<versión fija>-alpine`**, puerto 8080 | `nginx` estándar: corre como root. Caddy: duplica lo que ya hace Traefik |
| Base de datos | **Ninguna** → no hace falta gancho de volcado (regla 9) | — |
| Estilos | CSS propio, sin framework, con los tokens de `lib/core/theme/` | Tailwind por CDN: viola «sin recursos de terceros» |
| JavaScript | **Ninguno.** El cambio de tema lo hace `prefers-color-scheme` | Un interruptor de tema: requiere JS y `localStorage`; no compensa |

## 4. Principios de la web

Son los mismos de la app (spec §1 y [política de privacidad](../legal/politica-de-privacidad.md)). Si una propuesta los rompe, se descarta.

1. **Cero rastreo.** Sin analítica, sin píxeles, sin *fingerprinting*, sin cookies (ni siquiera de consentimiento: no hay nada que consentir).
2. **Cero terceros.** Ni Google Fonts, ni CDN, ni iconos remotos, ni vídeos incrustados. Todo se sirve desde el mismo origen.
3. **Sin JavaScript.** Una política CSP `script-src 'none'` lo garantiza.
4. **Calma.** Sin *pop-ups*, sin banners, sin contadores, sin «¡Últimas plazas!». La web es tan tranquila como el Lector.
5. **Verdad.** Solo se afirma lo que la app hace hoy y está verificado. Lo que no existe se dice «próximamente» o no se dice.
6. **Accesible.** WCAG 2.2 AA, como la app (ver §7.3).

## 5. Contenido de la página de inicio

Los textos están **validados por el usuario** (2026-10-02) como base; se pulen al implementar sin cambiar lo que afirman. Siguen el [glosario](referencias/glosario.md) (Diario, reflexión, añadir, copia, Silente+) y el tono del libro de Silente, cercano y sin tecnicismos. 

### 5.1 Cabecera

- Logo (`brand/silente-mark.svg`) + «Silente» en Lora.
- Navegación mínima: «Qué es» · «Privacidad» · «Preguntas». En móvil, enlaces en línea; sin menú hamburguesa (no hay JS).

### 5.2 Hero

- **Título:** Silente
- **Lema:** *Tu espacio de lectura*
- **Entradilla:** «Un lector de libros EPUB tranquilo, con un diario privado para lo que te hacen pensar. Sin cuentas, sin anuncios y sin internet: tus libros y tu diario se quedan en tu teléfono.»
- **Llamada a la acción:**
  - antes de publicar: insignia «Próximamente en Google Play» (no enlazada, con `aria-disabled`);
  - después: insignia oficial de Google Play enlazando a la ficha (`https://play.google.com/store/apps/details?id=com.nordirwork.silente`), alojada en local y usada según sus [condiciones de marca](https://partnermarketinghub.withgoogle.com/).
- **Imagen:** una captura del Lector (`lector-pagina.jpg`) dentro de un marco de teléfono dibujado en CSS.

### 5.3 Qué es Silente (cuatro bloques)

| Bloque | Texto propuesto | Captura |
|---|---|---|
| **Biblioteca** | «Añade tus libros EPUB y encuéntralos siempre donde los dejaste. "Continuar leyendo" te lleva a la página exacta.» | `biblioteca-inicio.jpg` |
| **Lector** | «Una página limpia que desaparece mientras lees. Elige fuente, tamaño, márgenes y cómo pasar página: como un libro, deslizando o en scroll.» | `lector-ajustes-oscuro.jpg` |
| **Diario** | «Escribe una reflexión desde cualquier página. Tu Diario guarda el libro y el capítulo en que la escribiste.» | `diario-editor.jpg` |
| **Tu copia** | «Exporta una copia de tus libros y tu diario, cifrada con tu contraseña, y llévatela a otro teléfono.» | `ajustes-exportar.jpg` |

### 5.4 Privacidad (sección destacada)

Título: **«Lo que lees es tuyo»**. Cuatro afirmaciones, cada una verificada en la [revisión de seguridad de F8](referencias/revision-seguridad-f8.md):

- **Sin internet.** Silente no tiene el permiso de Android para conectarse: no puede enviar nada.
- **Sin cuenta.** No hace falta registrarse para usar nada.
- **Sin anuncios ni seguimiento.** Ni analítica, ni publicidad, ni herramientas de terceros.
- **Tu diario, protegido.** Con «Proteger mi diario» nadie puede hacer capturas de tus reflexiones.

Enlace: «Lee la política de privacidad completa →» (`/privacidad`).

### 5.5 Pensado para leer

Tres principios del producto en frases cortas:

- «La lectura va primero.»
- «La interfaz desaparece cuando lees.»
- «Nada de feeds infinitos ni retos: solo tú y tu libro.»

### 5.6 El libro de Silente

«Silente trae su propio libro: una guía corta que se lee con el mismo Lector y te enseña a usarlo mientras lo recorres.» Captura: `libro-de-silente-portada.jpg`.

### 5.7 Silente+ (L-06)

«Próximamente: sincronización entre dispositivos y más opciones para tu Diario, tu Biblioteca y la lectura. Todo lo que Silente hace hoy seguirá siendo gratis.» Sin precios ni fechas.

### 5.8 Preguntas frecuentes

Con `<details>`/`<summary>` (funciona sin JS):

| Pregunta | Respuesta propuesta |
|---|---|
| ¿Qué libros puedo leer? | Libros en formato EPUB sin DRM. Silente no vende ni descarga libros: añades los tuyos. |
| ¿Lee PDF? | No. Silente se centra en EPUB. |
| ¿Es gratis? | Sí. Sin anuncios y sin pagos dentro de la app. |
| ¿Necesito una cuenta? | No. Todo funciona sin cuenta y sin internet. |
| ¿Qué pasa si cambio de teléfono? | Exporta una copia desde Ajustes, cifrada con tu contraseña, e impórtala en el teléfono nuevo. |
| ¿En qué dispositivos funciona? | En Android 10 o superior. iOS llegará más adelante. |
| ¿Quién está detrás? | NordirWork. Escríbenos a pqrs@nordirwork.com. |

### 5.9 Pie

- «Silente es una app de NordirWork.»
- Enlaces: Política de privacidad · Términos de uso · Contacto (`mailto:pqrs@nordirwork.com`).
- «Esta web no usa cookies ni analítica.»
- Año y versión de la web (`v<semver>`), útil para comprobar qué se desplegó.

## 6. Páginas legales y recursos

### 6.1 `/privacidad` y `/terminos`

- Se generan en el build desde la copia de `assets/legal/politica-de-privacidad.md` y `assets/legal/terminos-de-uso.md` de la app (en `silente-web/legal/`), **sin editar el texto**. La fecha «Última actualización» es la del archivo, la misma que muestra la app (validación de la guía de Play, paso 4).
- Rutas sin extensión y canónicas (`/privacidad`, no `/privacidad.html`). `/privacidad/` y `/privacidad.html` redirigen con 301.
- Mismo diseño que el resto de la web, con un ancho de lectura cómodo (≈ 65 caracteres).
- El build **falla** si `python3 tool/check_legal_placeholders.py` encuentra marcadores pendientes.

### 6.2 Marca

- **Logo:** `brand/silente-mark.svg` en línea, decorativo (`aria-hidden`), con «Silente» como texto.
- **Favicon:** SVG del logo + PNG de 32 y 180 px (`apple-touch-icon`), generados desde `brand/make_brand_assets.sh` o un paso equivalente.
- **Fuentes:** las mismas de la app, empaquetadas desde `assets/fonts/` y convertidas a WOFF2 con subconjunto latino. Lora para títulos y Nunito Sans para el texto. Literata solo si se muestra un fragmento de lectura. Se incluyen sus licencias OFL.
- **Colores** (tokens de `lib/core/theme/app_colors.dart`, definidos como variables CSS en `:root`):

| Token CSS | Claro | Oscuro | Uso |
|---|---|---|---|
| `--bg` | `#F5F3EF` parchmentWhite | `#121014` nightBlack | Fondo |
| `--surface` | `#ECEAE4` softLinen | `#1C1A22` shadowGraphite | Tarjetas |
| `--text` | `#1C1A22` inkBlack | `#EDEBE6` ivoryMist | Texto |
| `--text-muted` | `#6E6B73` warmGray | `#A6A3AA` ashGray | Texto secundario |
| `--accent` | `#8C7FB8` duskLavender | `#8C7FB8` duskLavender | Marca, foco |
| `--gold` | `#7D6128` goldInk | `#C8A86B` pageGold | Enlaces y detalles (goldInk cumple 5,2:1 sobre claro) |

### 6.3 Capturas

- Se toman de `docs/manual-usuario/capturas/` y se exportan a WebP con `srcset` (1×, 2×) y `width`/`height` fijos para evitar saltos de maquetación.
- **Revisión obligatoria antes de publicar** (CLAUDE.md: sin datos privados ni contenido con copyright):
  - solo libros de dominio público (Gutenberg) o el libro de Silente;
  - ninguna reflexión real: los textos del Diario son de ejemplo;
  - barra de estado sin notificaciones, nombres ni datos del teléfono.
- Cada captura lleva un `alt` descriptivo («La Biblioteca de Silente con "Continuar leyendo" arriba»).

### 6.4 SEO y metadatos

- `<title>` y `meta description` por página; `lang="es"`.
- Open Graph y tarjeta de Twitter con una imagen propia (1200 × 630, logo + lema), servida en local.
- `robots.txt` que permite todo y `sitemap.xml` con las tres URLs.
- `<link rel="canonical">` en cada página.
- Sin datos estructurados de valoraciones (la app no las tiene, D-05).

## 7. Requisitos no funcionales

### 7.1 Rendimiento

| Métrica | Objetivo |
|---|---|
| Peso de la página de inicio | ≤ 500 KB transferidos, imágenes incluidas |
| Peticiones | ≤ 15, todas al mismo origen |
| LCP (móvil, 4G simulada) | ≤ 2,0 s |
| CLS | ≤ 0,05 |
| Lighthouse | ≥ 95 en Rendimiento, Accesibilidad, Buenas prácticas y SEO |

Las imágenes por debajo del pliegue usan `loading="lazy"`. Las fuentes se precargan solo para el título (`<link rel="preload">`), con `font-display: swap`.

### 7.2 Seguridad

El middleware `publico@file` de Traefik ya añade `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy` y quita `Server`/`X-Powered-By`. **No se redefine.** nginx añade solo lo que falta:

```nginx
add_header Content-Security-Policy "default-src 'none'; img-src 'self'; style-src 'self'; font-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Resource-Policy "same-origin" always;
server_tokens off;
```

- Sin estilos en línea (la CSP no permite `'unsafe-inline'`): el CSS va en un archivo.
- **HSTS**: Traefik no lo emite (el TLS termina en Cloudflare, ver `middlewares.yml`). Se activa en el panel de Cloudflare para el subdominio, sin `includeSubDomains`.
- Solo `GET` y `HEAD`; el resto devuelve 405.
- Sin listado de directorios; sin servir archivos ocultos (`location ~ /\. { deny all; }`).
- Caché: `Cache-Control: public, max-age=31536000, immutable` para recursos con hash en el nombre; `no-cache` para el HTML.
- Logs de nginx sin la IP completa: formato propio que la anonimiza (último octeto a 0) y sin `User-Agent`, coherente con «sin seguimiento».

### 7.3 Accesibilidad

- WCAG 2.2 AA: contraste comprobado con los tokens de §6.2 en los dos temas.
- Navegación con teclado, foco visible (`--accent`), enlace «Saltar al contenido».
- Encabezados en orden, *landmarks* (`header`, `main`, `footer`, `nav`).
- Respeta `prefers-reduced-motion` (sin animaciones si se pide) y el zoom del 200 % sin scroll horizontal.
- Funciona desde 320 px de ancho, con márgenes laterales de al menos 16 px.

### 7.4 Compatibilidad

Últimas dos versiones de Chrome, Firefox, Safari y Samsung Internet. Sin JS, no hay más requisitos.

## 8. Despliegue en nomadservernw (anexo 96)

Valores reales del servidor (`config/servidor.env`): red `nomadservernw_proxy` (172.30.0.0/24), raíz `/srv/nomad`, dominio `nordirwork.com`.

### 8.1 Estructura del repositorio `silente-web`

```text
silente-web/
├── src/                     plantillas HTML, CSS e imágenes de la web
├── legal/                   copia de assets/legal/ de la app (guardia de §3.2)
├── brand/                   logo SVG y favicons, copiados de la app
├── fonts/                   Lora y Nunito Sans en WOFF2 + licencias OFL
├── build.py                 genera dist/ (inicio, legales, 404, salud, sitemap)
├── nginx.conf               servidor, cabeceras, caché, 404
├── Dockerfile               multi-etapa: build en Python → nginx-unprivileged
├── tests/                   comprobaciones del sitio generado (§9)
├── .github/workflows/ci.yml build, tests, guardia de nombre, gitleaks
└── deploy/nomad/
    ├── docker-compose.yml   el compose de producción (se copia al servidor)
    ├── .env.example         sin secretos, documentado
    └── README.md            el procedimiento, sin depender de la skill
```

### 8.2 Estructura en el servidor

```text
/srv/nomad/silente/
├── docker-compose.yml       copia de deploy/nomad/docker-compose.yml
├── .env                     600, no versionado
├── datos/                   vacío: la web no escribe nada (se crea igualmente)
└── codigo/                  el repositorio clonado
```

Recordatorio: `git pull` actualiza `codigo/`, **no** el `docker-compose.yml` de arriba. Si cambia, hay que volver a copiarlo.

### 8.3 `docker-compose.yml`

```yaml
services:
  web:
    build:
      context: ./codigo
      dockerfile: Dockerfile
    image: silente-web:1.0.0            # versión fija; sube con cada cambio
    container_name: silente-web
    restart: unless-stopped
    env_file:
      - .env
    read_only: true
    tmpfs:
      - /tmp                            # nginx-unprivileged escribe aquí pid y cachés
    networks:
      - proxy
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    healthcheck:
      # GET real (no --spider) a un recurso que nginx sirve desde dist/
      test: ["CMD-SHELL", "wget -q -O /dev/null http://localhost:8080/salud || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.silente.rule=Host(`silente.nordirwork.com`)"
      - "traefik.http.routers.silente.entrypoints=web"
      - "traefik.http.routers.silente.middlewares=publico@file"
      - "traefik.http.services.silente.loadbalancer.server.port=8080"

networks:
  proxy:
    external: true
    name: nomadservernw_proxy
```

### 8.4 Cumplimiento de las nueve reglas

| # | Regla | Cómo se cumple |
|---|---|---|
| 1 | Sin `ports:` | Traefik llega por la red `proxy` al puerto 8080 interno |
| 2 | Sin socket de Docker | No se monta nada salvo `tmpfs` |
| 3 | Datos en `./datos/` | La web no tiene datos; el directorio existe vacío. Sin volúmenes con nombre |
| 4 | Versión fija | `nginx-unprivileged:<x.y.z>-alpine` y `python:<x.y>-alpine` fijados en el `Dockerfile` (comprobar la última estable al implementar); imagen propia `silente-web:<semver>` |
| 5 | Healthcheck | En el compose (uno en el `Dockerfile` **no cuenta**), con `GET` a `/salud` |
| 6 | Secretos en `.env` 600 | No hay secretos; `.env` existe vacío con permisos 600 y `.env` ya está en `.gitignore`. Si el `.gitignore` ignora `.env.*`, debe mantener la excepción `!.env.example` (como el de la app) para versionar `deploy/nomad/.env.example` |
| 7 | Red interna para lo no publicado | No hay servicios no publicados |
| 8 | Router único y prefijado | Router y servicio `silente` (verificar que nadie lo usa, L-01/L-02) |
| 9 | Gancho de volcado | No aplica: no hay base de datos |

### 8.5 Acceso al repositorio

`silente-web` es **público**, así que `deploy.sh` clona y hace `git pull` sin credenciales. El servidor no tiene acceso a `DeartDev/silente`, que sigue privado.

Antes de hacerlo público, gitleaks en todo su historial y revisión de que solo contiene lo que ya se publica en la web.

### 8.6 Despliegue, en orden

1. `./scripts/revisar_proyecto.sh silente` en verde (primero en local, con la simulación de la skill).
2. `./scripts/11_cloudflared.sh --ruta silente` y `dig +short silente.nordirwork.com` → IP de Cloudflare.
3. Sin gancho de volcado (no hay base de datos).
4. `./scripts/deploy.sh silente --check` y después `./scripts/deploy.sh silente`.
5. Desde fuera: `200` en `/`, `/privacidad` y `/terminos`; cabeceras `x-frame-options`, `x-content-type-options`, `referrer-policy` y `content-security-policy` presentes.
6. HSTS activado en Cloudflare para el subdominio.
7. Monitor en Uptime Kuma: HTTP(s), `https://silente.nordirwork.com/salud`, cada 60 s.

## 9. Criterios de aceptación

| ID | Criterio | Cómo se verifica |
|---|---|---|
| LP-01 | `/privacidad` y `/terminos` reproducen el texto de `assets/legal/` de la app y su fecha | Test del build: el HTML generado contiene cada párrafo del Markdown + `tool/check_legal_sync.py` en el CI de la app |
| LP-02 | Ninguna petición a otro origen | Test que analiza `dist/` (ningún `http(s)://` en `src`/`href` de recursos salvo enlaces de navegación a Google Play) + DevTools → Red en producción |
| LP-03 | Ni cookies ni JavaScript | Ningún `<script>` en `dist/`; respuesta sin `Set-Cookie`; CSP con `default-src 'none'` |
| LP-04 | Los textos siguen el glosario | Revisión con el [glosario](referencias/glosario.md); sin «importar un libro», «respaldo», «entrada», «premium» |
| LP-05 | Nada se afirma que la app no haga | Cada afirmación de §5 enlaza con su evidencia (revisión de F8, fichas) |
| LP-06 | Cumple el contrato | `revisar_proyecto.sh silente` en verde en el servidor |
| LP-07 | Publicada y protegida | `200` desde internet y cabeceras de seguridad presentes |
| LP-08 | Accesible | Lighthouse Accesibilidad ≥ 95 + revisión manual con teclado y TalkBack en el g31 |
| LP-09 | Rápida | Presupuestos de §7.1 con Lighthouse móvil |
| LP-10 | Sin el nombre antiguo | Guardia de nombre en el CI de `silente-web` (misma regla que `tool/check_brand_name.py`) |
| LP-11 | Capturas limpias | Revisión de §6.3 registrada en el PR |
| LP-12 | 404 propia | `/no-existe` devuelve 404 con la página de Silente |

## 10. Riesgos

| Riesgo | Mitigación |
|---|---|
| Los textos legales de la web y de la app se desvían | Guardia `tool/check_legal_sync.py` en el CI de la app y dos PR el mismo día (§3.2); LP-01 |
| La web promete algo que la app no hace | LP-05; revisión en cada cambio de la app que toque §5 |
| El `docker-compose.yml` del servidor queda viejo tras un `git pull` | Se documenta en `deploy/nomad/README.md`; `revisar_proyecto.sh` tras cada cambio |
| Algo privado acaba en el repositorio público | gitleaks en pre-commit y CI; el repositorio solo contiene lo que ya publica la web |
| Una captura expone datos privados o texto con copyright | Revisión §6.3 obligatoria en el PR (LP-11) |
| Google Play rechaza la ficha por la URL de privacidad | URL pública, sin inicio de sesión y con la misma fecha que la app (LP-01, LP-07) |

## 11. Plan de trabajo propuesto

1. ✅ El usuario valida L-01…L-06 y los textos de §5 (2026-10-02). El proyecto se prepara en `~/Proyectos/Personal/silente-web/`, con esta especificación y sus referencias.
2. Crear `DeartDev/silente-web` (público) con el generador, plantillas, CSS, tests y CI (LP-01…LP-04, LP-10, LP-12).
3. En `DeartDev/silente`: `tool/check_legal_sync.py` en el CI y enlace a la nueva web en la guía de Play.
4. `deploy/nomad/` con el compose, `.env.example` y README; simulación local con `revisar_proyecto.sh` y **levantar el contenedor de verdad** (no basta con `docker compose config`).
5. Lighthouse y revisión de accesibilidad (LP-08, LP-09).
6. Documentación tras los tests en verde. En `silente-web`: su README y la guía de despliegue. En la app: ficha en `docs/funcionalidades/`, la [guía de Play](referencias/publicacion-play-store.md) (paso 4), el ROADMAP (§8.7) y `CHANGELOG.md`.
7. Despliegue en el servidor (§8.6) y cierre de LP-06/LP-07.
