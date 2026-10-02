#!/usr/bin/env python3
"""Regenerates the derived assets that build.py serves (spec §6.2, §6.3, §6.4).

Run it by hand when a source changes and commit the result; the Docker build
only needs the standard library and `markdown`.

    pip install -r requirements-dev.txt
    python3 tools/make_assets.py

Needs ImageMagick 7 with librsvg (`magick`) for the favicons.

Outputs:
- fonts/*.woff2: Lora and Nunito Sans (roman and italic), Latin subset;
- src/img/<shot>-{240,432}.webp: the screenshots of spec §5;
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
SHOTS = ROOT / "docs" / "referencias" / "capturas"
IMG = ROOT / "src" / "img"
BRAND = ROOT / "brand"

# Latin subset (Google Fonts "latin" range) plus the arrows used in links.
LATIN = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
    "U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2212,"
    "U+2215,U+FEFF,U+FFFD"
)
FONT_FILES = {
    "Lora-Variable.ttf": "lora.woff2",
    "Lora-Italic-Variable.ttf": "lora-italic.woff2",
    "NunitoSans-Variable.ttf": "nunito-sans.woff2",
    "NunitoSans-Italic-Variable.ttf": "nunito-sans-italic.woff2",
}
SHOT_NAMES = [
    "lector-pagina",
    "biblioteca-inicio",
    "lector-ajustes-oscuro",
    "diario-editor",
    "ajustes-exportar",
    "libro-de-silente-portada",
]
SHOT_WIDTHS = [240, 432]
# Only the weight axis stays variable, limited to the weights the CSS uses;
# the rest is pinned to its default (Nunito Sans: wdth, opsz, YTLC).
WEIGHTS = (400, 700)
NIGHT_BLACK = "#121014"
IVORY_MIST = "#EDEBE6"
ASH_GRAY = "#A6A3AA"


def make_fonts() -> None:
    for source, target in FONT_FILES.items():
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
        limits["wght"] = WEIGHTS
        font = instancer.instantiateVariableFont(font, limits)
        subset.save_font(font, str(FONTS / target), options)
        print(f"fonts/{target}: {(FONTS / target).stat().st_size // 1024} KB")


def make_shots() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    for name in SHOT_NAMES:
        with Image.open(SHOTS / f"{name}.jpg") as shot:
            for width in SHOT_WIDTHS:
                height = round(shot.height * width / shot.width)
                out = IMG / f"{name}-{width}.webp"
                shot.resize((width, height), Image.LANCZOS).save(out, "WEBP", quality=80, method=6)
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


def main() -> int:
    make_fonts()
    make_shots()
    make_favicons()
    make_og()
    return 0


if __name__ == "__main__":
    sys.exit(main())
