#!/usr/bin/env python3
"""Checks the legal texts in legal/ before they are published (spec §3.2, §6.1):
no data still to be filled in, such as "[CORREO DE CONTACTO]", and a
"Última actualización" line.

    python3 tools/check_legal_placeholders.py   # exit 1 if anything is wrong

Adapted from tool/check_legal_placeholders.py in the app (same pattern).
build.py runs the same check and refuses to build.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"\[[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ]+\]")
UPDATED = re.compile(r"^Última actualización: \S.*$", re.MULTILINE)


def legal_problems(legal_dir: Path) -> list[str]:
    problems = []
    paths = sorted(legal_dir.glob("*.md"))
    if not paths:
        problems.append(f"{legal_dir}: no hay textos legales")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            for match in PATTERN.findall(line):
                problems.append(f"{path.name}:{number}: marcador pendiente {match}")
        if not UPDATED.search(text):
            problems.append(f"{path.name}: falta la línea «Última actualización: …»")
    return problems


def main() -> int:
    problems = legal_problems(ROOT / "legal")
    for problem in problems:
        print(f"✗ {problem}")
    if problems:
        return 1
    print("✓ Textos legales sin marcadores pendientes y con fecha")
    return 0


if __name__ == "__main__":
    sys.exit(main())
