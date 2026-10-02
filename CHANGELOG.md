# Changelog

Cambios visibles de la web de Silente. Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versiones según [SemVer](https://semver.org/lang/es/). La versión está en `VERSION` y se muestra en el pie de la web.

## [Sin publicar]

### Añadido

- Imagen Docker (nginx sin privilegios) con las cabeceras de seguridad de la web, caché larga para los recursos, redirecciones a las URL canónicas y logs sin la IP completa.
- Vista previa local en `http://localhost:9020` y compose de producción para nomadservernw.

## [0.1.0] - 2026-10-02

### Añadido

- Página de inicio con las secciones del spec §5: presentación, «Qué es Silente», privacidad, «Pensado para leer», el libro de Silente, Silente+ (próximamente) y preguntas frecuentes.
- Política de privacidad (`/privacidad`) y términos de uso (`/terminos`), generados sin cambios desde `legal/`.
- Página 404 propia, `/salud`, `robots.txt` y `sitemap.xml`.
- Tema claro y oscuro según el sistema, sin JavaScript.
- Fuentes Lora y Nunito Sans servidas desde la propia web.
- Capturas de la app tomadas para la web en tema claro y oscuro: cada visitante ve las de su tema.
