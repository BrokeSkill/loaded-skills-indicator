"""The three inline skill-payload shapes, and the near-misses that must not count."""
from __future__ import annotations

import unittest

from support import load_api

API = load_api()

SINGLE = (
    '[IMPORTANT: The user has invoked the "pdf" skill. The full skill content is loaded below.]\n\n'
    "# PDF\nbody"
)
BUNDLE = (
    '[IMPORTANT: The user has invoked the "alpha / beta" skill bundle, loading 2 skills.]\n'
    "Skills loaded: alpha, beta\n\n# alpha"
)
AUTO = '[IMPORTANT: The "channel-skill" skill is auto-loaded. Follow its instructions for this session.]\nhi'


class ScaffoldTests(unittest.TestCase):
    def test_single_skill(self):
        self.assertEqual(API._scaffold_skills(SINGLE), ["pdf"])

    def test_bundle(self):
        self.assertEqual(API._scaffold_skills(BUNDLE), ["alpha", "beta"])

    def test_auto_load(self):
        self.assertEqual(API._scaffold_skills(AUTO), ["channel-skill"])

    def test_lookalike_text_is_not_a_load(self):
        self.assertEqual(API._scaffold_skills('[IMPORTANT: The "config" file is broken]'), [])
        self.assertEqual(API._scaffold_skills('[IMPORTANT: The user has invoked the "x" skill, but no marker.]'), [])

    def test_plain_text(self):
        self.assertEqual(API._scaffold_skills("just a message about the pdf skill"), [])

    def test_non_string(self):
        self.assertEqual(API._scaffold_skills(None), [])
        self.assertEqual(API._scaffold_skills({"content": SINGLE}), [])


if __name__ == "__main__":
    unittest.main()
