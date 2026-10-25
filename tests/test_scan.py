"""SKILL.md scanning: frontmatter parsing, category fallback, dedupe."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import load_api

API = load_api()

SIMPLE = """---
name: alpha
description: Does the alpha thing.
---

# Alpha
"""

QUOTED = """---
name: "beta-skill"
description: 'A quoted description.'
category: tools
---

# Beta
"""

BLOCK = """---
name: gamma
description: >
  First line of a folded
  description.
---

# Gamma
"""

NO_FRONTMATTER = "# just a markdown file\n"


def write_skill(root: Path, rel: str, text: str) -> Path:
    path = root / rel / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class ScanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def scan(self, *roots):
        with mock.patch.object(API, "_skill_roots", lambda: list(roots or (self.root,))):
            return {s["name"]: s for s in API.scan_skills()}

    def test_frontmatter_fields(self):
        write_skill(self.root, "alpha", SIMPLE)
        got = self.scan()["alpha"]
        self.assertEqual(got["description"], "Does the alpha thing.")
        self.assertEqual(got["category"], "general", "a top-level skill has no category dir")

    def test_quoted_values_and_category(self):
        write_skill(self.root, "tools/beta", QUOTED)
        got = self.scan()["beta-skill"]
        self.assertEqual(got["description"], "A quoted description.")
        self.assertEqual(got["category"], "tools")

    def test_folded_block_description(self):
        write_skill(self.root, "gamma", BLOCK)
        self.assertEqual(self.scan()["gamma"]["description"], "First line of a folded description.")

    def test_file_without_frontmatter_is_skipped(self):
        write_skill(self.root, "notes", NO_FRONTMATTER)
        self.assertEqual(self.scan(), {})

    def test_first_root_wins_on_a_duplicate_name(self):
        other = self.root / "other"
        write_skill(self.root, "dup-one", "---\nname: dup\ndescription: from profile\n---\n")
        write_skill(other, "dup-two", "---\nname: dup\ndescription: from bundled\n---\n")
        got = self.scan(self.root, other)
        self.assertEqual(got["dup"]["description"], "from profile")

    def test_missing_root_is_not_an_error(self):
        with mock.patch.object(API, "_skill_roots", lambda: [self.root / "nope"]):
            self.assertEqual(API.scan_skills(), [])


if __name__ == "__main__":
    unittest.main()
