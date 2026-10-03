# silente-web

Landing page de **Silente** — *Tu espacio de lectura*. Se publica en https://silente.nordirwork.com (pendiente de desplegar).

Web estática, sin JavaScript, sin cookies y sin analítica, servida con nginx en un contenedor y desplegada en `nomadservernw` según su contrato de dockerización.

## Estado

- ✅ Generador, plantillas, CSS, tests del sitio y CI (spec §11, paso 2).
- ✅ nginx, `Dockerfile` y `deploy/nomad/`, con la auditoría del contrato en verde en simulación (salvo el DNS).
- ✅ Lighthouse y revisión con teclado (LP-08, LP-09): [docs/accesibilidad.md](docs/accesibilidad.md). ⚪ Falta TalkBack en el g31.
- ⏳ Despliegue en el servidor.

Ver [`CLAUDE.md`](CLAUDE.md) para el contexto y los siguientes pasos.

## Verla en local

```sh
docker compose up -d --build      # → http://localhost:9020
SILENTE_URL=http://localhost:9020 .venv/bin/python -m unittest tests.test_http -v
npm ci --prefix tests/a11y && SILENTE_URL=http://localhost:9020 npm test --prefix tests/a11y
npx --yes @lhci/cli@0.15.1 autorun     # Lighthouse con los presupuestos
docker compose down
```

El `compose.yaml` de la raíz es solo para verla en local: publica el puerto 9020 en `127.0.0.1` y usa el mismo endurecimiento que producción. El de producción está en [`deploy/nomad/`](deploy/nomad/README.md) y no publica puertos.

## Generar y probar el sitio

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py                                # → dist/
.venv/bin/python -m unittest discover -s tests -t .      # tests del sitio
.venv/bin/python tools/check_brand_name.py dist          # guardia del nombre antiguo
```

`build.py` solo usa la biblioteca estándar y `markdown`. Falla si los textos legales tienen marcadores pendientes o les falta «Última actualización».

Los recursos derivados (fuentes WOFF2, capturas en WebP, favicons e imagen Open Graph) se generan a mano con `tools/make_assets.py` y se versionan. Hace falta `requirements-dev.txt` e ImageMagick 7 con librsvg:

```sh
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python tools/make_assets.py          # todo
.venv/bin/python tools/make_assets.py shots    # solo las capturas (también fonts, favicons, og)
```

Para publicar la insignia de Google Play cuando la app esté en la tienda, se rellena `PLAY_URL` en `build.py` y se añade la insignia oficial en `src/img/google-play-badge.svg`.

## Estructura

| Ruta | Contenido |
|---|---|
| `build.py` | Generador: inicio, `/privacidad`, `/terminos`, 404, `/salud`, `robots.txt` y `sitemap.xml`. Recursos con *hash* en el nombre, en `/assets/` |
| `src/templates/` | Plantillas HTML (`base`, `index`, `legal`, `404`) con marcadores `{{ … }}` |
| `src/css/site.css` | Estilos con los colores como variables CSS; tema claro y oscuro con `prefers-color-scheme` |
| `src/capturas/` | Capturas originales del g31, en tema claro y oscuro ([revisión](docs/capturas.md)) |
| `src/img/` | Capturas en WebP (240 y 432 px, de cada tema) e imagen Open Graph |
| `tests/test_site.py` | Comprobaciones del sitio generado (ver abajo) |
| `tools/` | `make_assets.py`; las guardias `check_legal_placeholders.py` y `check_brand_name.py`, adaptadas de la app; y `check_app_notes.py` ([sincronía con la app](docs/spec.md#12-sincronía-con-la-app-l-09)) |
| `nginx/` | `nginx.conf` y las cabeceras de seguridad que añade nginx (CSP, COOP, CORP) |
| `Dockerfile` | Multi-etapa: build con `python:3.14.8-alpine3.24` → `nginxinc/nginx-unprivileged:1.30.5-alpine3.24`, puerto 8080 |
| `compose.yaml` | Vista previa local en `http://localhost:9020` |
| `deploy/nomad/` | Compose de producción, `.env.example` y [procedimiento de despliegue](deploy/nomad/README.md) |
| `tests/test_http.py` | Comprobaciones del contenedor en marcha (necesita `SILENTE_URL`) |
| `tests/a11y/` | Revisión con teclado en Chrome real (puppeteer-core): foco, interruptor, visor, reflow y tamaño de los objetivos |
| `lighthouserc.json` | Presupuestos de Lighthouse del CI (spec §7.1) |
| `.github/workflows/ci.yml` | Build, tests, guardias, imagen Docker con tests HTTP, accesibilidad con teclado, Lighthouse y gitleaks |

## Qué comprueban los tests

| Criterio | Comprobación |
|---|---|
| LP-01 | Cada párrafo, título y elemento de lista de `legal/*.md` aparece en su página, con su fecha. El build falla con marcadores pendientes o sin fecha |
| LP-02 | Ningún recurso (`src`, `srcset`, `link`, `og:image`, `url()` del CSS) de otro origen. Los únicos enlaces externos son `mailto:` y la ficha de Google Play |
| LP-03 | Sin `<script>`, formularios, `iframe`, estilos en línea ni atributos `on*` |
| LP-04 | Sin las palabras que evita el glosario (importar un libro, respaldo, entrada, premium…) |
| LP-10 | Sin el nombre antiguo en los archivos versionados ni en `dist/` |
| LP-12 | La 404 tiene el diseño de la web y `noindex` |
| §6.4 | `lang`, título, descripción y URL canónica en cada página; `robots.txt`, `sitemap.xml` y `/salud` |
| §7.1 | Peso de la página de inicio (≤ 500 KB) y número de peticiones (≤ 15) |
| §7.3 | Encabezados en orden, *landmarks*, enlace «Saltar al contenido», `alt` y tamaño en las imágenes, y contraste AA de los colores en los dos temas |
| L-07 | Interruptor de tema en cada página, con «Sistema» marcado; cada captura tiene variante clara y oscura, y las forzadas se cargan en diferido |
| L-08 | Cada captura abre su vista ampliada y tiene un enlace «Cerrar» que vuelve a ella; todos los enlaces internos (`#…`) existen |
| §12 | `tests/test_app_notes.py`: estados de las notas e índice |

`tests/test_http.py` comprueba el servidor de verdad (también en el CI):

- CSP, COOP y CORP en todas las respuestas, sin `Set-Cookie` y sin versión en `Server` (LP-03);
- 404 con la página de Silente para cualquier ruta desconocida, también `/404` y `/404.html` (LP-12);
- 301 de `/privacidad.html` y `/privacidad/` a `/privacidad`;
- solo `GET` y `HEAD`, con 405 y `Allow` para el resto;
- caché `immutable` en `/assets/` y `no-cache` en el HTML, y los `Content-Type` correctos;
- archivos ocultos denegados.

## Índice

| Documento | Descripción |
|---|---|
| [docs/spec.md](docs/spec.md) | Especificación completa: contenido, requisitos, despliegue y criterios de aceptación |
| [CHANGELOG.md](CHANGELOG.md) | Cambios de cada versión de la web |
| [docs/capturas.md](docs/capturas.md) | Cómo se tomaron las capturas y su revisión (LP-11) |
| [docs/accesibilidad.md](docs/accesibilidad.md) | Resultados de Lighthouse y de la revisión con teclado (LP-08, LP-09) |
| [docs/cambios-app/](docs/cambios-app/README.md) | Notas de la app con lo que cambia y lo que hay que tocar en la web |
| [CLAUDE.md](CLAUDE.md) | Contexto del proyecto, decisiones, principios y valores del servidor |
| [legal/](legal/) | Política de privacidad y términos de uso (copia exacta de la app) |
| [brand/](brand/) | Logo de Silente (SVG, color y monocromo) |
| [fonts/](fonts/) | Lora, Nunito Sans y Literata (TTF variables + licencias OFL) y los WOFF2 que sirve la web (Lora y Nunito Sans, subconjunto latino) |
| [docs/referencias/](docs/referencias/) | Copias de solo lectura: glosario, marca, revisión de seguridad, guía de Google Play, monetización, colores, contrato de nomad_server y sus plantillas, scripts de guardia de la app y capturas |

## Licencias de terceros

Las tipografías se distribuyen bajo la SIL Open Font License 1.1 (`fonts/OFL-*.txt`). La web sirve las licencias de las que usa en `/licencias/`.
