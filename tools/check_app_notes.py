#!/usr/bin/env python3
"""Checks the notes that the app sends to the web (docs/cambios-app/): what
Silente does and what the landing says must not drift apart.

    python3 tools/check_app_notes.py            # pending notes: warning, exit 0
    python3 tools/check_app_notes.py --github   # the same, as CI annotations
    python3 tools/check_app_notes.py --strict   # pending notes: exit 1 (deploy)

Every note needs an «Estado en la web» line with one of the states of the
template and must be listed in the README index. Malformed notes always fail.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "docs" / "cambios-app"
STATE = re.compile(r"^- \*\*Estado en la web:\*\*\s*(.+)$", re.MULTILINE)
STATES = {"pendiente": "pending", "aplicada": "applied", "sin impacto": "none"}


def note_states(notes_dir: Path) -> tuple[dict[str, str], list[str]]:
    """{note: state} and the problems that make a note invalid."""
    states, problems = {}, []
    if not notes_dir.is_dir():
        return states, problems
    index_path = notes_dir / "README.md"
    index = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    for path in sorted(notes_dir.glob("*.md")):
        if path.name in ("README.md", "_plantilla.md"):
            continue
        match = STATE.search(path.read_text(encoding="utf-8"))
        found = [state for word, state in STATES.items() if match and word in match.group(1).lower()]
        if len(found) != 1:
            problems.append(f"{path.name}: «Estado en la web» falta o no es uno de: {', '.join(STATES)}")
        else:
            states[path.name] = found[0]
        if f"({path.name})" not in index:
            problems.append(f"{path.name}: no aparece en el índice de README.md")
    return states, problems


def main() -> int:
    github = "--github" in sys.argv
    strict = "--strict" in sys.argv
    states, problems = note_states(NOTES)
    for problem in problems:
        print(f"::error::{problem}" if github else f"✗ {problem}")
    pending = [name for name, state in states.items() if state == "pending"]
    for name in pending:
        message = f"Nota de la app pendiente de aplicar en la web: docs/cambios-app/{name}"
        print(f"::warning::{message}" if github else f"⚠ {message}")
    if problems or (strict and pending):
        return 1
    if not pending:
        print(f"✓ Notas de la app al día ({len(states)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
