"""Transcript analysis: full / pruned / ignored / re-read."""
from __future__ import annotations

import json
import unittest

from support import load_api, row

API = load_api()


def tool_calls(*names):
    return json.dumps(
        [
            {
                "id": "c-" + name,
                "type": "function",
                "function": {"name": "skill_view", "arguments": json.dumps({"name": name})},
            }
            for name in names
        ]
    )


def view_row(name, content, ts=2.0):
    return row(
        id=abs(hash((name, ts))) % 10_000,
        role="tool",
        tool_call_id="c-" + name,
        tool_name="skill_view",
        content=content,
        timestamp=ts,
    )


OK = json.dumps({"success": True, "name": "x", "content": "# body"})
FAILED = json.dumps({"success": False, "error": "not found"})


class AnalyseTests(unittest.TestCase):
    def test_full_then_pruned_then_reloaded(self):
        rows = [
            row(id=1, role="assistant", tool_calls=tool_calls("alpha")),
            view_row("alpha", OK, ts=2.0),
            row(
                id=3,
                role="user",
                content="[Context summary]\n[SKILL_PRUNED: content lost in compression; "
                "reload with skill_view(name='alpha')]",
                timestamp=3.0,
            ),
        ]
        got = {s["name"]: s["state"] for s in API.analyse(rows)}
        self.assertEqual(got, {"alpha": "pruned"})

        rows.append(view_row("alpha", OK, ts=4.0))
        got = {s["name"]: s["state"] for s in API.analyse(rows)}
        self.assertEqual(got, {"alpha": "full"}, "a re-read after a prune wins")

    def test_failed_load_is_not_listed(self):
        rows = [
            row(id=1, role="assistant", tool_calls=tool_calls("ghost")),
            view_row("ghost", FAILED),
        ]
        self.assertEqual(API.analyse(rows), [])

    def test_failed_summary_stub_is_not_listed(self):
        rows = [
            row(id=1, role="assistant", tool_calls=tool_calls("ghost")),
            view_row("ghost", "[skill_view] ghost (pruned) FAILED"),
        ]
        self.assertEqual(API.analyse(rows), [])

    def test_multiple_skills_keep_first_seen_order(self):
        rows = [
            row(id=1, role="assistant", tool_calls=tool_calls("beta", "alpha")),
            view_row("beta", OK, ts=2.0),
            view_row("alpha", OK, ts=3.0),
        ]
        self.assertEqual([s["name"] for s in API.analyse(rows)], ["beta", "alpha"])

    def test_other_tools_are_ignored(self):
        rows = [
            row(id=1, role="tool", tool_name="terminal", content="hi", tool_call_id="c-x"),
            row(id=2, role="tool", tool_name="skill_view", content=OK, tool_call_id="c-unknown"),
        ]
        # A skill_view whose call id maps to no known name cannot be attributed.
        self.assertEqual(API.analyse(rows), [])

    def test_payload_counts_only_full(self):
        rows = [
            row(id=1, role="assistant", tool_calls=tool_calls("alpha", "beta")),
            view_row("alpha", OK, ts=2.0),
            view_row("beta", OK, ts=3.0),
            row(id=4, role="user", content="[SKILL_PRUNED: content lost in compression; reload with skill_view(name='beta')]"),
        ]
        payload = API._payload("s1", API.analyse(rows), False)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["loaded"], ["alpha"])
        self.assertEqual(payload["pruned"], ["beta"])


if __name__ == "__main__":
    unittest.main()
