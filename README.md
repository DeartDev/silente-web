# silente-web

Landing page de **Silente** — *Tu espacio de lectura*. Se publica en https://silente.nordirwork.com (pendiente de desplegar).

Web estática, sin JavaScript, sin cookies y sin analítica, servida con nginx en un contenedor y desplegada en `nomadservernw` según su contrato de dockerización.

## Estado

- ✅ Generador, plantillas, CSS, tests del sitio y CI (spec §11, paso 2).
- ⏳ `nginx.conf`, `Dockerfile` y `deploy/nomad/`; Lighthouse; despliegue.

Ver [`CLAUDE.md`](CLAUDE.md) para el contexto y los siguientes pasos.

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
| `tools/` | `make_assets.py` y las guardias `check_legal_placeholders.py` y `check_brand_name.py`, adaptadas de la app |
| `.github/workflows/ci.yml` | Build, tests, guardias y gitleaks |

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

Las cabeceras HTTP (CSP, sin `Set-Cookie`, 404 real) se comprueban cuando exista `nginx.conf`.

## Índice

| Documento | Descripción |
|---|---|
| [docs/spec.md](docs/spec.md) | Especificación completa: contenido, requisitos, despliegue y criterios de aceptación |
| [CHANGELOG.md](CHANGELOG.md) | Cambios de cada versión de la web |
| [docs/capturas.md](docs/capturas.md) | Cómo se tomaron las capturas y su revisión (LP-11) |
| [CLAUDE.md](CLAUDE.md) | Contexto del proyecto, decisiones, principios y valores del servidor |
| [legal/](legal/) | Política de privacidad y términos de uso (copia exacta de la app) |
| [brand/](brand/) | Logo de Silente (SVG, color y monocromo) |
| [fonts/](fonts/) | Lora, Nunito Sans y Literata (TTF variables + licencias OFL) y los WOFF2 que sirve la web (Lora y Nunito Sans, subconjunto latino) |
| [docs/referencias/](docs/referencias/) | Copias de solo lectura: glosario, marca, revisión de seguridad, guía de Google Play, monetización, colores, contrato de nomad_server y sus plantillas, scripts de guardia de la app y capturas |

## Licencias de terceros

Las tipografías se distribuyen bajo la SIL Open Font License 1.1 (`fonts/OFL-*.txt`). La web sirve las licencias de las que usa en `/licencias/`.
