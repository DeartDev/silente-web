# Changelog

Cambios visibles de la web de Silente. Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versiones según [SemVer](https://semver.org/lang/es/). La versión está en `VERSION` y se muestra en el pie de la web.

## [Sin publicar]

### Añadido

- Imagen Docker (nginx sin privilegios) con las cabeceras de seguridad de la web, caché larga para los recursos, redirecciones a las URL canónicas y logs sin la IP completa.
- Vista previa local en `http://localhost:9020` y compose de producción para nomadservernw.
- Interruptor de tema «Sistema · Claro · Oscuro» en la cabecera, sin JavaScript: cambia los colores y las capturas.
- Las capturas se amplían al pulsarlas.
- Diseño renovado:
  - las líneas del logo que se apagan en «…» abren el inicio y los principios;
  - halo cálido detrás del teléfono;
  - la privacidad, en una lista en dos columnas;
  - preguntas frecuentes junto a su título;
  - pie en dos columnas.
- Aviso en el CI cuando hay notas de la app pendientes de aplicar en la web.

### Corregido

- El texto del Lector decía que el scroll es una forma de pasar página. Ahora distingue cómo se lee (por páginas o en scroll) de cómo se pasa página (como un libro, deslizando o sin animación), como hace la app.

## [0.1.0] - 2026-10-02

### Añadido

- Página de inicio con las secciones del spec §5: presentación, «Qué es Silente», privacidad, «Pensado para leer», el libro de Silente, Silente+ (próximamente) y preguntas frecuentes.
- Política de privacidad (`/privacidad`) y términos de uso (`/terminos`), generados sin cambios desde `legal/`.
- Página 404 propia, `/salud`, `robots.txt` y `sitemap.xml`.
- Tema claro y oscuro según el sistema, sin JavaScript.
- Fuentes Lora y Nunito Sans servidas desde la propia web.
- Capturas de la app tomadas para la web en tema claro y oscuro: cada visitante ve las de su tema.
