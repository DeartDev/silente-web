#!/usr/bin/env python3
"""Regenerates the derived assets that build.py serves (spec §6.2, §6.3, §6.4).

Run it by hand when a source changes and commit the result; the Docker build
only needs the standard library and `markdown`.

    pip install -r requirements-dev.txt
    python3 tools/make_assets.py                 # everything
    python3 tools/make_assets.py shots og        # only some parts

Parts: fonts, shots, favicons, og. Fonts and PNGs are not byte-for-byte
reproducible, so regenerate only what changed.

Needs ImageMagick 7 with librsvg (`magick`) for the favicons.

Outputs:
- fonts/*.woff2: Lora and Nunito Sans (roman and italic), Latin subset;
- src/img/<shot>-<theme>-{240,432,540}.webp: the screenshots of spec §5, in the
  light (claro) and dark (oscuro) themes, from src/capturas/<theme>/*.jpg;
- brand/favicon-32.png, brand/apple-touch-icon.png, brand/favicon.ico;
- src/img/og.png: Open Graph image, 1200 × 630.
"""

import subprocess
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
SHOTS = ROOT / "src" / "capturas"
IMG = ROOT / "src" / "img"
BRAND = ROOT / "brand"

# Latin subset (Google Fonts "latin" range) plus the arrows used in links.
LATIN = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
    "U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2212,"
    "U+2215,U+FEFF,U+FFFD"
)
# target → (source, weight). A tuple keeps that range of the weight axis
# variable; a number makes a static instance, much smaller. Lora is static:
# the page uses 600 (titles, preloaded) and the italic 400 (the motto and the
# principles). Nunito Sans uses 400 to 700.
FONT_FILES = {
    "lora-600.woff2": ("Lora-Variable.ttf", 600),
    "lora-italic.woff2": ("Lora-Italic-Variable.ttf", 400),
    "nunito-sans.woff2": ("NunitoSans-Variable.ttf", (400, 700)),
    "nunito-sans-italic.woff2": ("NunitoSans-Italic-Variable.ttf", (400, 700)),
}
SHOT_THEMES = ["claro", "oscuro"]
SHOT_NAMES = [
    "lector-pagina",
    "biblioteca-inicio",
    "lector-ajustes",
    "diario-editor",
    "ajustes-exportar",
    "libro-de-silente-portada",
]
SHOT_WIDTHS = [240, 432, 540]  # 540: the full-size view (sources are 540 wide)
# 72: text in the screenshots stays sharp, ~12 % smaller than 80 (LCP, LP-09).
SHOT_QUALITY = 72
# Every axis but the weight is pinned to its default (Nunito Sans: wdth,
# opsz, YTLC).
NIGHT_BLACK = "#121014"
IVORY_MIST = "#EDEBE6"
ASH_GRAY = "#A6A3AA"


def make_fonts() -> None:
    for target, (source, weight) in FONT_FILES.items():
        options = subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.notdef_outline = True
        font = TTFont(FONTS / source, lazy=False)
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=subset.parse_unicodes(LATIN))
        subsetter.subset(font)
        limits = {axis.axisTag: None for axis in font["fvar"].axes}
        limits["wght"] = weight
        font = instancer.instantiateVariableFont(font, limits)
        subset.save_font(font, str(FONTS / target), options)
        print(f"fonts/{target}: {(FONTS / target).stat().st_size // 1024} KB")


def make_shots() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    for theme in SHOT_THEMES:
        for name in SHOT_NAMES:
            with Image.open(SHOTS / theme / f"{name}.jpg") as shot:
                for width in SHOT_WIDTHS:
                    height = round(shot.height * width / shot.width)
                    out = IMG / f"{name}-{theme}-{width}.webp"
                    shot.resize((width, height), Image.LANCZOS).save(out, "WEBP", quality=SHOT_QUALITY, method=6)
                    print(f"src/img/{out.name}: {width}×{height}, {out.stat().st_size // 1024} KB")


def render_mark(size: int, out: Path, background: str = "none", padding: int = 0) -> None:
    inner = size - 2 * padding
    subprocess.run(
        [
            "magick", "-background", "none", "-density", "384",
            str(BRAND / "silente-mark.svg"), "-resize", f"{inner}x{inner}",
            "-gravity", "center", "-background", background,
            "-extent", f"{size}x{size}", "-depth", "8", f"PNG32:{out}",
        ],
        check=True,
    )


def make_favicons() -> None:
    render_mark(32, BRAND / "favicon-32.png")
    # iOS adds its own rounded corners; dark background like the Android icon.
    render_mark(180, BRAND / "apple-touch-icon.png", NIGHT_BLACK, padding=18)
    subprocess.run(
        ["magick", str(BRAND / "favicon-32.png"), str(BRAND / "favicon.ico")], check=True
    )
    print("brand/favicon-32.png, brand/apple-touch-icon.png, brand/favicon.ico")


def variable_font(path: Path, size: int, weight: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size)
    font.set_variation_by_axes([weight])
    return font


def make_og() -> None:
    mark = BRAND / "og-mark.tmp.png"
    render_mark(300, mark)
    canvas = Image.new("RGB", (1200, 630), NIGHT_BLACK)
    with Image.open(mark) as logo:
        canvas.paste(logo, (110, 165), logo)
    mark.unlink()
    draw = ImageDraw.Draw(canvas)
    draw.text((470, 200), "Silente", font=variable_font(FONTS / "Lora-Variable.ttf", 136, 600), fill=IVORY_MIST)
    draw.text(
        (476, 372), "Tu espacio de lectura",
        font=variable_font(FONTS / "Lora-Italic-Variable.ttf", 54, 400), fill=ASH_GRAY,
    )
    out = IMG / "og.png"
    canvas.save(out, optimize=True)
    print(f"src/img/og.png: {out.stat().st_size // 1024} KB")


PARTS = {"fonts": make_fonts, "shots": make_shots, "favicons": make_favicons, "og": make_og}


def main() -> int:
    parts = sys.argv[1:] or list(PARTS)
    unknown = [part for part in parts if part not in PARTS]
    if unknown:
        print(f"Partes desconocidas: {', '.join(unknown)}. Válidas: {', '.join(PARTS)}")
        return 1
    for part in parts:
        PARTS[part]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
