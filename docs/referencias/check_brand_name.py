#!/usr/bin/env python3
"""Fails if the old name (Umbra) appears in a versioned file or file name
outside the exceptions of ADR-011 (D9). Run in CI and pre-commit (D10).

Usage:
    python3 tool/check_brand_name.py [root]   # default: this repository
"""
import re
import subprocess
import sys
from pathlib import Path

# The old name as a word, inside identifiers (aboutUmbraBook) or constants
# (UMBRA_X); not the Spanish «umbral» or «penumbra».
OLD_NAME = re.compile(r"(?<![A-Za-z])umbra(?!l)|[a-z]Umbra", re.IGNORECASE)
# IGNORECASE also lets [a-z]Umbra match «penumbra»: checked separately.
CAMEL = re.compile(r"[a-z]Umbra")

# D9: lines that keep the old name on purpose.
LEGACY_LINE = re.compile(
    r"ADR-011|adr/011-"  # explains the rename
    r'|"UMBRA"|UMBRA\\x01|legacyUmbra|Umbra builds|umbra-backup'  # D3
    r"|umbra-key\.properties|umbra-upload"  # upload key files
    r"|umbra-mark|contains\('umbra'\)|umbra-tec"  # brand and book checks
)

# D9: files that tell the story of the rename, and this guard.
EXCEPT_FILES = re.compile(
    r"^docs/adr/011-cambio-de-nombre-a-silente\.md$"
    r"|^docs/superpowers/plans/[\d-]+-silente-etapa-\d[\w-]*\.md$"
    r"|^tool/check_brand_name\.py$"
    r"|^test/tool/check_brand_name_test\.dart$"
    r"|^test/core/rebrand_test\.dart$"
)


def is_old_name(text: str) -> bool:
    for m in OLD_NAME.finditer(text):
        word = m.group(0)
        if len(word) == 6 and not CAMEL.fullmatch(word):
            continue  # «penumbra» through IGNORECASE
        return True
    return False


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=root, text=True).split("\0")
    found = []
    for name in filter(None, files):
        if EXCEPT_FILES.search(name):
            continue
        if is_old_name(name) and not LEGACY_LINE.search(name):
            found.append(f"{name}: (nombre de archivo)")
        path = root / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data[:8192]:
            continue  # binary
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            if is_old_name(line) and not LEGACY_LINE.search(line):
                found.append(f"{name}:{i}: {line.strip()[:160]}")
    if found:
        print("✗ El nombre antiguo aparece fuera de las excepciones del ADR-011 (D9):")
        print("\n".join(found))
        return 1
    print("✓ Sin el nombre antiguo fuera de las excepciones del ADR-011")
    return 0


if __name__ == "__main__":
    sys.exit(main())
