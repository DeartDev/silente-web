#!/usr/bin/env python3
"""Fails if the old name of the project appears in a versioned file or file
name (LP-10), or in the generated site when a directory is given.

    python3 tools/check_brand_name.py          # versioned files
    python3 tools/check_brand_name.py dist     # also the generated site

Same rule as tool/check_brand_name.py in the app. The read-only copies in
docs/referencias/ may contain the old name and are not published.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The old name as a word, inside identifiers or constants; not the Spanish
# «umbral» or «penumbra».
OLD_NAME = re.compile(r"(?<![A-Za-z])umbra(?!l)|[a-z]Umbra", re.IGNORECASE)
# IGNORECASE also lets [a-z]Umbra match «penumbra»: checked separately.
CAMEL = re.compile(r"[a-z]Umbra")

EXCEPT_FILES = re.compile(r"^docs/referencias/|^tools/check_brand_name\.py$")


def is_old_name(text: str) -> bool:
    for m in OLD_NAME.finditer(text):
        word = m.group(0)
        if len(word) == 6 and not CAMEL.fullmatch(word):
            continue  # «penumbra» through IGNORECASE
        return True
    return False


def file_hits(label: str, path: Path) -> list[str]:
    found = []
    if is_old_name(label):
        found.append(f"{label}: (nombre de archivo)")
    data = path.read_bytes()
    if b"\0" in data[:8192]:
        return found  # binary
    for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
        if is_old_name(line):
            found.append(f"{label}:{i}: {line.strip()[:160]}")
    return found


def versioned_hits(root: Path = ROOT) -> list[str]:
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=root, text=True).split("\0")
    found = []
    for name in filter(None, files):
        path = root / name
        if EXCEPT_FILES.search(name) or not path.is_file():
            continue
        found += file_hits(name, path)
    return found


def site_hits(site: Path) -> list[str]:
    found = []
    for path in sorted(p for p in site.rglob("*") if p.is_file()):
        found += file_hits(str(path.relative_to(site)), path)
    return found


def main() -> int:
    found = versioned_hits()
    if len(sys.argv) > 1:
        found += site_hits(Path(sys.argv[1]))
    if found:
        print("✗ El nombre antiguo aparece en la web o en el repositorio:")
        print("\n".join(found))
        return 1
    print("✓ Sin el nombre antiguo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
