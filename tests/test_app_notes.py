"""tools/check_app_notes.py: the notes from the app (docs/cambios-app/)."""

import tempfile
import unittest
from pathlib import Path

from tools.check_app_notes import note_states

NOTE = "# Nota\n\n- **Fecha:** 2026-10-02\n- **Estado en la web:** {state}\n\nTexto.\n"


class AppNotesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "_plantilla.md").write_text("- **Estado en la web:** ⏳ pendiente · ✅ aplicada\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name: str, state: str, indexed: bool = True) -> None:
        (self.dir / name).write_text(NOTE.format(state=state), encoding="utf-8")
        index = self.dir / "README.md"
        text = index.read_text(encoding="utf-8") if index.exists() else "| Fecha | Nota |\n"
        if indexed:
            text += f"| 2026-10-02 | [Nota]({name}) |\n"
        index.write_text(text, encoding="utf-8")

    def test_states(self):
        self.write("a.md", "⏳ pendiente en la web")
        self.write("b.md", "✅ aplicada en la web (PR #4)")
        self.write("c.md", "— sin impacto. Es la línea base")
        states, problems = note_states(self.dir)
        self.assertEqual(states, {"a.md": "pending", "b.md": "applied", "c.md": "none"})
        self.assertEqual(problems, [])

    def test_missing_or_unknown_state_is_a_problem(self):
        self.write("a.md", "quizá")
        (self.dir / "b.md").write_text("# Sin estado\n", encoding="utf-8")
        _, problems = note_states(self.dir)
        self.assertEqual(len([p for p in problems if "Estado en la web" in p]), 2)

    def test_note_must_be_in_the_index(self):
        self.write("a.md", "— sin impacto", indexed=False)
        _, problems = note_states(self.dir)
        self.assertEqual(problems, ["a.md: no aparece en el índice de README.md"])

    def test_no_notes_directory(self):
        self.assertEqual(note_states(self.dir / "no-existe"), ({}, []))

    def test_template_and_readme_are_not_notes(self):
        states, problems = note_states(self.dir)
        self.assertEqual((states, problems), ({}, []))


if __name__ == "__main__":
    unittest.main()
