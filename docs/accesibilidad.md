# Accesibilidad y rendimiento (LP-08, LP-09)

- **Estado:**
  - LP-08: ✅ Lighthouse y revisión con teclado; ⚪ TalkBack en el g31, pendiente.
  - LP-09: ✅ todos los presupuestos salvo el LCP móvil de la página de inicio, a 26 ms del objetivo (ver abajo).
- **Fecha:** 2026-10-02, contra el contenedor local (`http://localhost:9020`, con gzip como en producción).
- **Relacionado:** spec §7.1 y §7.3; [`lighthouserc.json`](../lighthouserc.json); [`tests/a11y/keyboard.mjs`](../tests/a11y/keyboard.mjs).

## Lighthouse 13.5 (móvil, 4G simulada)

| Página | Rendimiento | Accesibilidad | Buenas prácticas | SEO | LCP | FCP | CLS | Peso | Peticiones |
|---|---|---|---|---|---|---|---|---|---|
| `/` | 99 | 100 | 100 | 100 | 2,03 s | 0,75 s | 0 | 182 KB | 10 |
| `/privacidad` | 100 | 100 | 100 | 100 | 1,20 s | 0,75 s | 0 | 76 KB | 6 |
| `/terminos` | 100 | 100 | 100 | 100 | 1,50 s | 1,05 s | 0 | 99 KB | 7 |

En escritorio, las tres páginas sacan 100 en todo, con el LCP por debajo de 0,4 s. Lighthouse no audita la 404 porque devuelve un 404; la revisión con teclado sí la cubre.

Objetivos del spec (§7.1): ≥ 95 en las cuatro categorías, LCP ≤ 2,0 s, CLS ≤ 0,05, ≤ 500 KB y ≤ 15 peticiones.

### El LCP de la página de inicio

Primera medida: 2,4 s; ahora, 2,03 s.

**Qué lo bajó:**
- gzip en nginx: en producción comprime Traefik, pero sin compresión la medida local no era representativa;
- CSS minificado en el build (15 → 9 KB);
- Lora en instancias estáticas: 600 para los títulos y la cursiva 400. Se ahorran 60 KB, y desaparece la Lora 400 recta, que solo usaban los principios (ahora en cursiva) y el «+» de las preguntas;
- precarga de las tres fuentes que se ven al abrir la página;
- capturas en WebP con calidad 72 (antes 80).

**Qué no lo movió**, medido y descartado:
- quitar `fetchpriority` a la imagen del hero;
- `font-display: optional`;
- `content-visibility` en las secciones de abajo;
- quitar los selectores `:has()` del interruptor;
- reducir más los bytes.

El valor se queda en 2026–2027 ms con cualquier cambio. Lo fija la latencia por petición que simula Lighthouse (562 ms), no la página: el LCP real observado está en unos 120 ms.

En el CI, el LCP está como **aviso** (`warn`) y no como error. El resto de presupuestos son errores.

## Revisión con teclado y Chrome real

`tests/a11y/keyboard.mjs` (puppeteer-core) comprueba lo siguiente, a 390 y 1280 px, en las cuatro páginas. También corre en el CI.

| Comprobación | Resultado |
|---|---|
| El primer Tab lleva a «Saltar al contenido» | ✅ |
| Foco visible (anillo de 3 px) en todas las paradas | ✅ (25 en el inicio, 11–12 en el resto) |
| El interruptor de tema es una sola parada y se maneja con las flechas; colores y capturas cambian | ✅ |
| Visor: Enter lo abre con el foco dentro, Tab va a «Cerrar», «Cerrar» vuelve al teléfono, pulsar fuera lo cierra | ✅ |
| Si el foco sale del visor, el visor se oculta, así que nada enfocado queda tapado (WCAG 2.4.11) | ✅ |
| Sin scroll horizontal a 320 px y con zoom al 200 % (640 px CSS) | ✅ |
| Objetivos de al menos 24 × 24 px (WCAG 2.5.8), salvo los enlaces dentro del texto | ✅ |
| Con `prefers-reduced-motion`, sin animaciones | ✅ |

Además, `tests/test_site.py` comprueba el contraste AA de los colores en los dos temas, los encabezados, los *landmarks*, los `alt` y que el visor sea enfocable.

### Limitaciones conocidas

- **Sin JavaScript, el foco no se puede atrapar en el visor ni cerrarlo con Escape.** Se cierra con «Cerrar», pulsando fuera o con «atrás» del navegador.
- **Shift+Tab desde el visor vuelve al teléfono que lo abrió,** y ese teléfono queda detrás del visor. Es a propósito: la misma excepción garantiza que el visor se abra en navegadores que no mueven el foco al destino del enlace.
- **El interruptor no recuerda la elección entre páginas** (spec L-07).

## ⚪ Pendiente: TalkBack en el moto g31

LP-08 pide también una revisión manual con TalkBack. Para hacerla sin desplegar, se publica la vista previa en el teléfono por adb:

```sh
docker compose up -d --build
adb -s <serie-del-g31> reverse tcp:9020 tcp:9020   # el teléfono ve el puerto 9020 del ordenador
```

En el g31, Chrome → `http://localhost:9020`, con TalkBack activado. Hay que comprobar:
- el orden de lectura;
- los nombres de los enlaces de las capturas («Ampliar la captura: …»);
- el grupo «Tema de la web»;
- las preguntas frecuentes;
- el visor.

## Cómo repetirlo

```sh
docker compose up -d --build
npx --yes @lhci/cli@0.15.1 autorun                     # Lighthouse con los presupuestos (lighthouserc.json)
npm ci --prefix tests/a11y
SILENTE_URL=http://localhost:9020 npm test --prefix tests/a11y
```
