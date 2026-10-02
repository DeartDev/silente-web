# CLAUDE.md — Guía del proyecto silente-web

Landing page pública de **Silente**, el lector EPUB local-first con diario privado (app Flutter en `DeartDev/silente`, en local `~/Proyectos/Personal/silente`). Lema: *Tu espacio de lectura*.

Se publica en **https://silente.nordirwork.com**, dockerizada, en el servidor doméstico `nomadservernw`.

## Fuente de verdad

- **`docs/spec.md`** es la especificación completa y validada por el usuario (2026-10-02): objetivo, alcance, decisiones L-01…L-06, contenido y textos de cada sección, requisitos, despliegue y criterios de aceptación LP-01…LP-12. **Léela entera antes de empezar.**
- `docs/referencias/` son **copias de solo lectura** de documentos de la app y de `nomad_server`, para trabajar sin depender de otros repositorios. No se editan: si algo cambia, se cambia en su origen y se vuelve a copiar.
- Todo lo que no esté en el spec está **fuera de alcance** hasta que se añada explícitamente.

## Estado

- ✅ Spec validado (decisiones L-01…L-06 cerradas).
- ✅ Directorio preparado con los recursos: textos legales, logo, fuentes, capturas y referencias.
- ✅ Repositorio público [DeartDev/silente-web](https://github.com/DeartDev/silente-web) creado (2026-10-02): solo *squash merge* y borrado de ramas al fusionar. gitleaks limpio y capturas revisadas antes de publicarlo.
- ⏳ Falta proteger `main` en GitHub (gratis en repos públicos) cuando exista el CI, exigiendo sus checks.
- ✅ Generador (`build.py`), plantillas, CSS, tests del sitio y CI (rama `feat/generador`, 2026-10-02).
- ✅ nginx (`nginx/`), `Dockerfile`, `deploy/nomad/` y tests HTTP (rama `feat/docker`). `revisar_proyecto.sh` en verde en simulación, salvo el DNS.
- ⏳ Lighthouse (LP-08, LP-09) y despliegue en el servidor.
- **Vista previa local:** `docker compose up -d --build` → `http://localhost:9020`. Los proyectos personales usan puertos 9000+ en local. `nordirwork` ya ocupa el 9010 y el 9011; silente-web usa el 9020, solo en `127.0.0.1`. En producción no hay `ports:` (regla 1).
- Decisiones de implementación:
  - `--text-muted` claro es `warmGrayInk` (`#65626A`), no `warmGray`. `warmGray` se queda en 4,3:1 sobre `--surface`.
  - El foco es de dos tonos: anillo `--accent` más anillo interior `--text`, porque `duskLavender` se queda en 2,99:1 sobre `softLinen`.
  - Los recursos derivados (WOFF2, WebP, favicons, OG) se generan con `tools/make_assets.py` y se versionan, para que la imagen de Docker solo necesite `markdown`.

## Primeros pasos para la sesión que empiece el proyecto

1. Leer `docs/spec.md` y este archivo.
2. ✅ Repositorio creado. ✅ LP-11: capturas nuevas en claro y oscuro, tomadas en el g31 ([docs/capturas.md](docs/capturas.md)); las de `docs/referencias/capturas/` ya no se usan.
3. Seguir el plan del §11 del spec:
   - generador `build.py` + plantillas + CSS → `dist/`;
   - `nginx.conf` + `Dockerfile` multi-etapa (Python → `nginxinc/nginx-unprivileged:<versión fija>-alpine`, puerto 8080);
   - tests del sitio generado (LP-01…LP-04, LP-10, LP-12) y CI de GitHub Actions;
   - `deploy/nomad/` (compose, `.env.example`, README);
   - simulación local con `revisar_proyecto.sh` y levantar el contenedor de verdad;
   - Lighthouse y accesibilidad (LP-08, LP-09).
4. Para todo lo relacionado con el servidor, usar la skill **`desplegar-en-nomadservernw`**.

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
