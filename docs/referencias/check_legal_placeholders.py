#!/usr/bin/env python3
"""Lists data still to be filled in the legal texts (assets/legal/*.md),
such as "[CORREO DE CONTACTO]" (ROADMAP P-09).

    python3 tool/check_legal_placeholders.py          # exit 1 if any (release)
    python3 tool/check_legal_placeholders.py --warn   # CI annotation, exit 0

A release must not ship with placeholders (F8 checklist). Same pattern as
legalPlaceholders() in lib/features/settings/domain/legal_document.dart.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"\[[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ ]+\]")


def main() -> int:
    warn = "--warn" in sys.argv
    found = []
    for path in sorted((ROOT / "assets" / "legal").glob("*.md")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in PATTERN.findall(line):
                found.append((path.relative_to(ROOT), number, match))
    for path, number, match in found:
        if warn:
            print(f"::warning file={path},line={number}::Texto legal sin completar: {match}")
        else:
            print(f"✗ {path}:{number}: {match}")
    if not found:
        print("✓ Textos legales sin marcadores pendientes")
        return 0
    return 0 if warn else 1


if __name__ == "__main__":
    sys.exit(main())
