# CLAUDE.md — Guía del proyecto silente-web

Landing page pública de **Silente**, el lector EPUB local-first con diario privado (app Flutter en `DeartDev/silente`, en local `~/Proyectos/Personal/silente`). Lema: *Tu espacio de lectura*.

Se publica en **https://silente.nordirwork.com**, dockerizada, en el servidor doméstico `nomadservernw`.

## Fuente de verdad

- **`docs/spec.md`** es la especificación completa y validada por el usuario (2026-10-02): objetivo, alcance, decisiones L-01…L-09, contenido y textos de cada sección, requisitos, despliegue y criterios de aceptación LP-01…LP-12. **Léela entera antes de empezar.**
- `docs/referencias/` son **copias de solo lectura** de documentos de la app y de `nomad_server`, para trabajar sin depender de otros repositorios. No se editan: si algo cambia, se cambia en su origen y se vuelve a copiar.
- Todo lo que no esté en el spec está **fuera de alcance** hasta que se añada explícitamente.

## Estado (2026-10-02)

Hecho y en `main` (PR #1–#4, CI en verde):

- ✅ **Spec validado:** decisiones L-01…L-06; L-07…L-09 añadidas el 2026-10-02 (interruptor de tema, capturas ampliables y sincronía con la app).
- ✅ **Repositorio** público [DeartDev/silente-web](https://github.com/DeartDev/silente-web): solo *squash merge*, ramas borradas al fusionar. `main` protegida (ver Git).
- ✅ **Sitio:** generador (`build.py`), plantillas, CSS, tests del sitio (LP-01…LP-04, LP-10, LP-12) y CI (#1).
- ✅ **Capturas** nuevas del g31, en claro y oscuro (LP-11, [docs/capturas.md](docs/capturas.md)). Las de `docs/referencias/capturas/` ya no se usan.
- ✅ **Notas de la app** en `docs/cambios-app/` (#2).
- ✅ **Docker:** nginx (`nginx/`), `Dockerfile`, `deploy/nomad/` y tests HTTP (#3). `revisar_proyecto.sh` en verde en simulación, salvo el DNS.
- ✅ **Interfaz** (#4):
  - interruptor de tema solo con CSS (L-07);
  - capturas ampliables con `:target` (L-08);
  - diseño renovado;
  - guardia de las notas de la app (L-09, spec §12).

Pendiente:

- ✅ Lighthouse y revisión con teclado (LP-08, LP-09), en el CI: [docs/accesibilidad.md](docs/accesibilidad.md). El LCP móvil de la página de inicio se queda en 2,03 s, un aviso en el CI: lo fija la latencia simulada.
- ⚪ TalkBack en el g31: `adb reverse tcp:9020 tcp:9020` y Chrome → `http://localhost:9020`.
- ⏳ Despliegue en el servidor (spec §8.6) y cierre de LP-06 y LP-07; después, los cambios en la app que pide «Documentación».
- ⏳ `gitleaks/gitleaks-action@v2` usa Node 20, que está obsoleto: actualizarlo cuando haya versión nueva.
- ⚪ Las fuentes de las capturas miden 540 px. Para una vista ampliada nítida en pantallas de alta densidad, repetirlas a 1080 px.

## Cómo se trabaja

- **Transparencia con la app (finalidad de la web):** la web dice y muestra solo lo que la app hace.
  - Los cambios de la app llegan como notas en `docs/cambios-app/` (PR desde la app).
  - Al trabajar en la web se aplican las notas ⏳ pendientes (textos, preguntas frecuentes y capturas en los dos temas) y se marcan.
  - `tools/check_app_notes.py --strict` tiene que pasar antes de desplegar.
- **Vista previa local:** `docker compose up -d --build` → `http://localhost:9020`.
  - Los proyectos personales usan puertos 9000+ en local. `nordirwork` ya ocupa el 9010 y el 9011; silente-web usa el 9020, solo en `127.0.0.1`.
  - En producción no hay `ports:` (regla 1).
- **Tests:**
  - `python3 -m unittest discover -s tests -t .` para el sitio;
  - `SILENTE_URL=http://localhost:9020 python3 -m unittest tests.test_http` para el contenedor;
  - `npm test --prefix tests/a11y` para el teclado en Chrome;
  - `npx @lhci/cli@0.15.1 autorun` para Lighthouse.
- **Fuentes:** Lora va en instancias estáticas (600 y cursiva 400); no hay Lora 400 recta. Usarla añadiría una descarga y empeoraría el LCP.
- **Recursos derivados** (WOFF2, WebP, favicons, OG): se generan con `tools/make_assets.py <parte>` y se versionan, para que la imagen de Docker solo necesite `markdown`. Las fuentes y los PNG no son reproducibles byte a byte, así que solo se regenera la parte que cambia.
- **Decisiones de implementación:**
  - `--text-muted` claro es `warmGrayInk` (`#65626A`), no `warmGray`. `warmGray` se queda en 4,3:1 sobre `--surface`.
  - El foco es de dos tonos: anillo `--accent` más anillo interior `--text`, porque `duskLavender` se queda en 2,99:1 sobre `softLinen`.
  - Los colores son tokens `light-dark()` en `:root`. El interruptor fija `color-scheme` con `:has()`.
- Para todo lo relacionado con el servidor, usar la skill **`desplegar-en-nomadservernw`**.

## Valores reales del servidor

Tomados de `~/Proyectos/Personal/nomad_server/config/servidor.env` (2026-10-02). No usar `servidor.env.example`.

| Variable | Valor |
|---|---|
| `DOMINIO_PUBLICO` | `nordirwork.com` |
| `DOCKER_RED_PROXY` | `nomadservernw_proxy` |
| `DOCKER_RED_PROXY_SUBRED` | `172.30.0.0/24` |
| `DATOS_RAIZ` | `/srv/nomad` |
| `SERVIDOR_HOSTNAME` / dominio local | `nomadservernw.lan` |

- Host: `silente.nordirwork.com` (L-01). Proyecto, directorio, contenedor y router de Traefik: `silente` / `silente-web` (L-02). El ápice `nordirwork.com` y `www` pertenecen a otro proyecto.
- Comprobar en el servidor que el host y el router siguen libres antes de desplegar: `grep -rn 'Host(' /srv/nomad/*/docker-compose.yml`.
- `scripts/lib/entorno.sh` de `nomad_server` espera el repositorio en `~/nomad_server`. En este equipo está en `~/Proyectos/Personal/nomad_server` y el script falla al cargarlo desde ahí; los valores de arriba se leyeron directamente del `servidor.env`.

## Contrato de despliegue (resumen del anexo 96)

Copia completa en `docs/referencias/nomad-96-contrato-de-dockerizacion.md`. Las nueve reglas, todas comprobadas por `revisar_proyecto.sh`:

1. Sin `ports:`.
2. Sin socket de Docker.
3. Datos en `./datos/` (aquí, vacío) y nunca volúmenes con nombre.
4. Imágenes con versión fija (nunca `latest`).
5. `healthcheck` en el **compose** (uno en el `Dockerfile` no cuenta), con un `GET` real (`wget -q -O /dev/null`, no `--spider`).
6. `.env` con permisos 600 y fuera de git (`.env.example` sí se versiona).
7. Lo no publicado, en red interna.
8. Router con nombre único y prefijado.
9. Gancho de volcado si hay base de datos (aquí no hay).

Otros detalles del contrato:

- El middleware `publico@file` ya pone las cabeceras básicas de seguridad y la compresión; **no se redefine**. La CSP y las cabeceras COOP/CORP las añade nginx (spec §7.2).
- HSTS se activa en Cloudflare, no en Traefik.
- `git pull` en el servidor actualiza `codigo/`, **no** el `docker-compose.yml` copiado un nivel por encima.

## Principios (no negociables)

Son los de la app y su política de privacidad. La web los cumple igual:

- **Cero rastreo:** sin analítica (tampoco Cloudflare Web Analytics), sin cookies, sin píxeles.
- **Cero terceros:** nada de CDN, Google Fonts, iconos remotos ni vídeos incrustados. Todo desde el mismo origen.
- **Sin JavaScript.** La CSP lleva `script-src 'none'` (vía `default-src 'none'`). El tema claro/oscuro va con `prefers-color-scheme`.
- **Sin formularios.** El contacto es `mailto:pqrs@nordirwork.com`.
- **Verdad:** solo se afirma lo que la app hace hoy y está verificado (evidencia en `docs/referencias/revision-seguridad-f8.md`). Lo que no existe es «próximamente» o no se menciona.
- **Sin puertas traseras** ni nada de depuración accesible en producción. Sin secretos en el repositorio (gitleaks).
- Accesibilidad WCAG 2.2 AA.

## Textos legales

- `legal/politica-de-privacidad.md` y `legal/terminos-de-uso.md` son **copias exactas** de `assets/legal/` de la app (fuente de verdad). Fecha actual: 2 de octubre de 2026.
- No se editan aquí. Si cambian en la app, el mismo día se abren dos PR (app y web).
- En la app falta crear `tool/check_legal_sync.py`, que comparará en su CI los dos juegos de archivos. Es tarea del repositorio `silente`, no de este.

## Marca

- Nombre: **Silente**, siempre como texto en Lora (nunca como imagen). Producto de **NordirWork**.
- Logo: `brand/silente-mark.svg` (libro abierto en oro y dos líneas lila que terminan en «…»). Variante `brand/silente-mark-mono.svg`.
- Colores: tokens de `docs/referencias/app_colors.dart`, con la tabla claro/oscuro del spec §6.2. Definirlos como variables CSS en `:root`, sin colores sueltos en el CSS.
- Tipografías (OFL, en `fonts/`): Lora para títulos, Nunito Sans para el texto y Literata solo para un fragmento de lectura. Convertir a WOFF2 con subconjunto latino y servir las licencias.
- El nombre antiguo del proyecto (ver `docs/referencias/check_brand_name.py`) **no puede aparecer** en la web. Las copias de `docs/referencias/` pueden contenerlo y quedan excluidas de esa comprobación.
- Vocabulario según `docs/referencias/glosario.md`:
  - Diario y reflexión;
  - «añadir» un libro (no «importar»);
  - «copia» de los datos (no «respaldo»);
  - Silente+ (no «premium»).

## Idioma

- Comunicación, documentación, commits, PRs y textos de la web: **español**.
- Código (identificadores, nombres de archivo, comentarios técnicos): **inglés**.

## Git

- Conventional Commits en español: `feat(inicio): sección de privacidad`.
- Ramas `feat/*`, `fix/*`, `chore/*`, `docs/*` → PR hacia `main`; solo *squash merge*.
- `main` está protegida (2026-10-02):
  - todo entra por PR, también para los administradores;
  - hay que pasar los tres checks del CI («Build y tests del sitio», «Imagen Docker y tests HTTP», «Secretos (gitleaks)») con la rama al día respecto a `main`;
  - historial lineal, sin *force push* ni borrado, y con las conversaciones resueltas.
- PR apilados: antes de fusionar el de abajo, cambiar la base del siguiente a `main`; después, rebasarlo con `git rebase --onto origin/main <tip anterior> <rama>` y subirlo con `--force-with-lease`.
- En los commits y PR, la atribución que indique el sistema.

## Documentación

- La documentación forma parte de la definición de terminado y se escribe **después** de los tests en verde, en el mismo PR.
- `README.md` como índice; `docs/` en español con enlaces relativos.
- Lo no verificado se marca como ⚪ no evaluado.
- `CHANGELOG.md` en cada PR con cambios visibles.
- Al publicar la web, en la app (`silente`) hay que actualizar:
  - la guía de Play (paso 4: URL de privacidad `https://silente.nordirwork.com/privacidad`);
  - el ROADMAP §8.7;
  - el estado de `docs/producto/landing-page.md`, con un enlace a este repositorio.
