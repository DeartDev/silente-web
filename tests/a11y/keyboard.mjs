// Accessibility checks with a real Chrome (spec §7.3, LP-08): keyboard order
// and focus, the CSS theme switch, the screenshot viewer, reflow at 320 px and
// 200 % zoom, target size and reduced motion. Exits 1 on any failure.
//
//   docker compose up -d --build
//   npm ci --prefix tests/a11y
//   SILENTE_URL=http://localhost:9020 npm test --prefix tests/a11y
//
// CHROME_PATH chooses the browser (default: /usr/bin/google-chrome).

import puppeteer from "puppeteer-core";

const BASE = (process.env.SILENTE_URL || "http://localhost:9020").replace(/\/$/, "");
const PAGES = ["/", "/privacidad", "/terminos", "/no-existe"];
let failures = 0;

function check(ok, message) {
  console.log(`${ok ? "✓" : "✗"} ${message}`);
  if (!ok) failures++;
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
  headless: true,
  args: ["--no-sandbox"],
});
const page = await browser.newPage();

const focused = () =>
  page.evaluate(() => {
    const el = document.activeElement;
    // A radio button is hidden: its label carries the focus ring.
    const ring = el.tagName === "INPUT" ? document.querySelector(`label[for="${el.id}"]`) : el;
    const style = getComputedStyle(ring);
    const box = ring.getBoundingClientRect();
    return {
      id: el.id,
      tag: el.tagName.toLowerCase(),
      href: el.getAttribute("href") || "",
      ring: style.outlineStyle !== "none" && parseFloat(style.outlineWidth) >= 2,
      shown: box.width > 0 && box.height > 0,
    };
  });

// Keyboard: every stop has a visible focus ring; the theme switch is one stop.
for (const width of [390, 1280]) {
  await page.setViewport({ width, height: 900 });
  for (const path of PAGES) {
    await page.goto(BASE + path, { waitUntil: "networkidle0" });
    const stops = [];
    for (let i = 0; i < 60; i++) {
      await page.keyboard.press("Tab");
      const f = await focused();
      // The end of the page: focus leaves to the browser or wraps around.
      if (f.tag === "body" || (stops.length && f.href === stops[0].href && f.id === stops[0].id)) break;
      stops.push(f);
    }
    const label = `${width}px ${path}`;
    check(stops[0]?.href === "#contenido", `${label}: el primer Tab va a «Saltar al contenido»`);
    check(stops.every((s) => s.ring && s.shown), `${label}: foco visible en las ${stops.length} paradas`);
    check(stops.filter((s) => s.tag === "input").length === 1, `${label}: el interruptor de tema es una sola parada`);
  }
}

// Theme switch with the arrow keys: colours and screenshots follow.
await page.setViewport({ width: 1280, height: 900 });
await page.goto(BASE + "/", { waitUntil: "networkidle0" });
await page.focus("#tema-sistema");
const theme = () =>
  page.evaluate(() => ({
    value: document.querySelector('input[name="tema"]:checked').value,
    background: getComputedStyle(document.body).backgroundColor,
    shot: [...document.querySelectorAll("#captura-lector-pagina > picture, #captura-lector-pagina > img")]
      .filter((e) => getComputedStyle(e).display !== "none")
      .map((e) => e.className)
      .join(),
  }));
const expected = [
  ["claro", "rgb(245, 243, 239)", "shot-claro"],
  ["oscuro", "rgb(18, 16, 20)", "shot-oscuro"],
  ["sistema", "rgb(245, 243, 239)", "shot-auto"],
];
for (const [value, background, shot] of expected) {
  await page.keyboard.press("ArrowRight");
  const t = await theme();
  check(
    t.value === value && t.background === background && t.shot === shot,
    `Flecha derecha → «${value}»: fondo ${t.background}, captura ${t.shot}`,
  );
}

// Screenshot viewer: opens with Enter, «Cerrar» is next, leaving hides it.
const view = (id) =>
  page.evaluate(
    (id) => ({
      hash: location.hash,
      shown: getComputedStyle(document.getElementById(id)).display !== "none",
      focus: document.activeElement.id || document.activeElement.className,
    }),
    id,
  );
await page.focus("#captura-diario-editor");
await page.keyboard.press("Enter");
await wait(300);
let v = await view("ver-diario-editor");
check(v.shown && v.focus === "ver-diario-editor", "Enter abre el visor y lleva el foco dentro");
await page.keyboard.press("Tab");
v = await view("ver-diario-editor");
check(v.shown && v.focus === "lightbox-close", "Tab va a «Cerrar»");
await page.keyboard.press("Tab");
v = await view("ver-diario-editor");
check(!v.shown, "Si el foco sale del visor, el visor se oculta (nada queda tapado)");
await page.focus("#captura-diario-editor");
await page.keyboard.press("Enter");
await wait(300);
await page.keyboard.press("Tab");
await page.keyboard.press("Enter");
await wait(300);
v = await view("ver-diario-editor");
check(!v.shown && v.hash === "#captura-diario-editor", "«Cerrar» vuelve al teléfono");
await page.click("#captura-lector-ajustes");
await wait(300);
await page.mouse.click(20, 450);
await wait(300);
v = await view("ver-lector-ajustes");
check(!v.shown, "Pulsar fuera del visor lo cierra");

// Reflow: 320 px and 200 % zoom (a 1280 px window is 640 CSS px).
for (const width of [320, 640]) {
  await page.setViewport({ width, height: 800 });
  for (const path of PAGES) {
    await page.goto(BASE + path, { waitUntil: "networkidle0" });
    const [scroll, inner] = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
    check(scroll <= inner, `${width}px ${path}: sin scroll horizontal`);
  }
}

// Target size (WCAG 2.2, 2.5.8): 24 × 24 CSS px, except links inside text.
await page.setViewport({ width: 390, height: 844 });
for (const path of PAGES) {
  await page.goto(BASE + path, { waitUntil: "networkidle0" });
  const small = await page.evaluate(() =>
    [...document.querySelectorAll("a[href], label, summary")]
      .filter((e) => e.offsetParent !== null)
      .filter((e) => !(e.tagName === "A" && getComputedStyle(e).display === "inline" && e.closest("p")))
      .map((e) => [e.innerText.trim().slice(0, 30), e.getBoundingClientRect()])
      .filter(([, r]) => r.width < 24 || r.height < 24)
      .map(([text]) => text),
  );
  check(small.length === 0, `390px ${path}: objetivos de al menos 24 px${small.length ? ` (${small.join(", ")})` : ""}`);
}

// Reduced motion: the viewer opens without animation.
await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
await page.goto(BASE + "/#ver-diario-editor", { waitUntil: "networkidle0" });
const animation = await page.evaluate(() => getComputedStyle(document.getElementById("ver-diario-editor")).animationName);
check(animation === "none", "Con prefers-reduced-motion el visor no se anima");

await browser.close();
console.log(failures ? `\n✗ ${failures} comprobaciones fallidas` : "\n✓ Accesibilidad con teclado en orden");
process.exit(failures ? 1 : 0);
