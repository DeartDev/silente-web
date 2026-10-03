#!/usr/bin/env python3
"""Generates the static site in dist/ (spec §2, §6, §8.1).

    python3 build.py              # → dist/
    python3 build.py --out DIR

Only needs the standard library and `markdown` (requirements.txt). The
derived assets (WOFF2, WebP, favicons) are made by tools/make_assets.py and
committed.

Templates use `{{ name }}` placeholders:
- `{{ asset:path }}` → URL of a hashed asset (`/assets/name.<hash>.ext`);
- `{{ absolute_asset:path }}` → the same, with the site origin;
- `{{ shot:name|alt[|eager] }}` → a screenshot `<picture>`: the light one by
  default and the dark one with `prefers-color-scheme: dark`;
- anything else → a value of the page context (already safe HTML).
A placeholder without a value fails the build.
"""

import argparse
import hashlib
import html
import os
import re
import shutil
import struct
import sys
import time
from pathlib import Path

import markdown

from tools.check_legal_placeholders import legal_problems

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
TEMPLATES = SRC / "templates"

SITE_URL = "https://silente.nordirwork.com"
# None until the app is published on Google Play (spec §5.2). When it is, set
# the store URL and add the official badge as src/img/google-play-badge.svg.
PLAY_URL = None

# Logical asset path → source file.
ASSETS = {
    "fonts/lora.woff2": ROOT / "fonts/lora.woff2",
    "fonts/lora-italic.woff2": ROOT / "fonts/lora-italic.woff2",
    "fonts/nunito-sans.woff2": ROOT / "fonts/nunito-sans.woff2",
    "fonts/nunito-sans-italic.woff2": ROOT / "fonts/nunito-sans-italic.woff2",
    "brand/silente-mark.svg": ROOT / "brand/silente-mark.svg",
    "brand/favicon-32.png": ROOT / "brand/favicon-32.png",
    "img/og.png": SRC / "img/og.png",
}
SHOT_WIDTHS = (240, 432)
SHOT_THEMES = ("claro", "oscuro")
# The phone frame is 240 px wide with a 10 px border.
SHOT_SIZES = "220px"

# Files served at a fixed path, outside /assets/.
ROOT_FILES = {
    "favicon.ico": ROOT / "brand/favicon.ico",
    "apple-touch-icon.png": ROOT / "brand/apple-touch-icon.png",
    "licencias/OFL-Lora.txt": ROOT / "fonts/OFL-Lora.txt",
    "licencias/OFL-NunitoSans.txt": ROOT / "fonts/OFL-NunitoSans.txt",
}

LEGAL_PAGES = [
    {
        "source": "politica-de-privacidad.md",
        "file": "privacidad.html",
        "path": "/privacidad",
        "description": "Qué datos guarda Silente, dónde están y qué control tienes sobre ellos. "
        "El mismo texto que trae la app.",
    },
    {
        "source": "terminos-de-uso.md",
        "file": "terminos.html",
        "path": "/terminos",
        "description": "Las condiciones de uso de Silente, el lector EPUB de NordirWork. "
        "El mismo texto que trae la app.",
    },
]

PLACEHOLDER = re.compile(r"\{\{\s*(.+?)\s*\}\}")


class BuildError(Exception):
    pass


def webp_size(path: Path) -> tuple[int, int]:
    """Width and height of a WebP file, from its header."""
    data = path.read_bytes()[:30]
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise BuildError(f"{path}: no es un WebP")
    chunk = data[12:16]
    if chunk == b"VP8 ":
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    raise BuildError(f"{path}: formato WebP desconocido")


class Site:
    def __init__(self, out: Path, legal_dir: Path):
        self.out = out
        self.legal_dir = legal_dir
        self.urls: dict[str, str] = {}
        self.version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        # Reproducible builds: SOURCE_DATE_EPOCH, if set, fixes the year.
        epoch = int(os.environ.get("SOURCE_DATE_EPOCH", time.time()))
        self.year = time.gmtime(epoch).tm_year

    # Assets

    def add_asset(self, logical: str, data: bytes) -> None:
        stem, dot, suffix = Path(logical).name.rpartition(".")
        digest = hashlib.sha256(data).hexdigest()[:10]
        name = f"{stem}.{digest}{dot}{suffix}"
        (self.out / "assets" / name).write_bytes(data)
        self.urls[logical] = f"/assets/{name}"

    def copy_assets(self) -> None:
        (self.out / "assets").mkdir(parents=True)
        for logical, source in ASSETS.items():
            self.add_asset(logical, source.read_bytes())
        for shot in sorted((SRC / "img").glob("*.webp")):
            self.add_asset(f"img/{shot.name}", shot.read_bytes())
        css = self.render(TEMPLATES.parent / "css/site.css", {})
        self.add_asset("css/site.css", css.encode("utf-8"))
        for target, source in ROOT_FILES.items():
            (self.out / target).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, self.out / target)

    def asset(self, logical: str) -> str:
        if logical not in self.urls:
            raise BuildError(f"recurso desconocido: {logical}")
        return self.urls[logical]

    def shot(self, spec: str) -> str:
        name, alt, *flags = spec.split("|")
        variants = {}
        for theme in SHOT_THEMES:
            widths = []
            for width in SHOT_WIDTHS:
                logical = f"img/{name}-{theme}-{width}.webp"
                widths.append((width, self.asset(logical), webp_size(SRC / logical)))
            variants[theme] = widths
        sizes = {widths[0][2] for widths in variants.values()}
        if len(sizes) != 1:
            raise BuildError(f"{name}: las capturas clara y oscura tienen tamaños distintos")
        (width, height) = sizes.pop()
        srcset = {t: ", ".join(f"{url} {w}w" for w, url, _ in v) for t, v in variants.items()}
        loading = 'fetchpriority="high"' if flags == ["eager"] else 'loading="lazy"'
        return (
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="{srcset["oscuro"]}" '
            f'sizes="{SHOT_SIZES}" width="{width}" height="{height}">'
            f'<img src="{variants["claro"][0][1]}" srcset="{srcset["claro"]}" sizes="{SHOT_SIZES}" '
            f'width="{width}" height="{height}" alt="{html.escape(alt)}" '
            f'{loading} decoding="async"></picture>'
        )

    # Templates

    def render(self, template: Path, context: dict[str, str]) -> str:
        def replace(match: re.Match) -> str:
            key = match.group(1)
            kind, _, value = key.partition(":")
            if kind == "asset":
                return self.asset(value)
            if kind == "absolute_asset":
                return SITE_URL + self.asset(value)
            if kind == "shot":
                return self.shot(value)
            if key not in context:
                raise BuildError(f"{template.name}: falta el valor de {{{{ {key} }}}}")
            return context[key]

        return PLACEHOLDER.sub(replace, template.read_text(encoding="utf-8"))

    def page(self, file: str, content: str, title: str, description: str, path: str | None) -> None:
        url = SITE_URL + (path or "/")
        if path is None:
            head_extra = '<meta name="robots" content="noindex">'
        else:
            head_extra = f'<link rel="canonical" href="{url}">'
        context = {
            "title": html.escape(title),
            "description": html.escape(description),
            "url": url,
            "head_extra": head_extra,
            "logo": self.logo(),
            "content": content,
            "year": str(self.year),
            "version": html.escape(self.version),
        }
        (self.out / file).write_text(self.render(TEMPLATES / "base.html", context), encoding="utf-8")

    def logo(self) -> str:
        svg = (ROOT / "brand/silente-mark.svg").read_text(encoding="utf-8")
        svg = re.sub(r"\s*<title>.*?</title>", "", svg)  # decorative: the name is text
        svg = svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
        return svg.strip()

    def play(self) -> str:
        if PLAY_URL is None:
            return '<p><a class="badge" role="link" aria-disabled="true">Próximamente en Google Play</a></p>'
        badge = SRC / "img/google-play-badge.svg"
        if not badge.is_file():
            raise BuildError("PLAY_URL necesita la insignia oficial en src/img/google-play-badge.svg")
        self.add_asset("img/google-play-badge.svg", badge.read_bytes())
        return (
            f'<p><a class="badge-image" href="{html.escape(PLAY_URL)}">'
            f'<img src="{self.asset("img/google-play-badge.svg")}" width="180" height="53" '
            'alt="Disponible en Google Play"></a></p>'
        )

    # Pages

    def build_home(self) -> None:
        content = self.render(TEMPLATES / "index.html", {"play": self.play()})
        self.page(
            "index.html",
            content,
            "Silente · Tu espacio de lectura",
            "Un lector de libros EPUB tranquilo, con un diario privado. Sin cuentas, "
            "sin anuncios y sin internet: tus libros y tu diario se quedan en tu teléfono.",
            "/",
        )

    def build_legal(self) -> None:
        problems = legal_problems(self.legal_dir)
        if problems:
            raise BuildError("textos legales sin completar:\n  " + "\n  ".join(problems))
        for legal in LEGAL_PAGES:
            text = (self.legal_dir / legal["source"]).read_text(encoding="utf-8")
            title = re.search(r"^# (.+)$", text, re.MULTILINE)
            if not title:
                raise BuildError(f"{legal['source']}: falta el título «# …»")
            body = markdown.markdown(text, extensions=["toc"], output_format="html")
            content = self.render(TEMPLATES / "legal.html", {"body": body})
            self.page(legal["file"], content, f"{title.group(1)} · Silente", legal["description"], legal["path"])

    def build_404(self) -> None:
        content = self.render(TEMPLATES / "404.html", {})
        self.page(
            "404.html", content, "Página no encontrada · Silente",
            "Esta página no existe en la web de Silente, el lector de libros EPUB de NordirWork.", None,
        )

    def build_text_files(self) -> None:
        (self.out / "salud").write_text("ok\n", encoding="utf-8")
        (self.out / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
        )
        urls = ["/"] + [legal["path"] for legal in LEGAL_PAGES]
        entries = "".join(f"  <url><loc>{SITE_URL}{url}</loc></url>\n" for url in urls)
        (self.out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{entries}</urlset>\n",
            encoding="utf-8",
        )

    def build(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True)
        self.copy_assets()
        self.build_home()
        self.build_legal()
        self.build_404()
        self.build_text_files()


def build(out: Path, legal_dir: Path = ROOT / "legal") -> None:
    Site(out, legal_dir).build()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        build(args.out)
    except BuildError as error:
        print(f"✗ {error}", file=sys.stderr)
        return 1
    print(f"✓ Sitio generado en {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
