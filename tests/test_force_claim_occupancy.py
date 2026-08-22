"""#369 (resume side): a force takeover reports what the artifacts around the
spine say about who else has been here, as counts and ages, with no verdict.

The dispatcher's half of the recovery drill is written everywhere in the corpus;
the resuming agent's half was written nowhere. These tests pin the shape that
fills it: information delivered at the moment of the takeover, never a refusal.
"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "checklist_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("checklist_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load_engine()


def _spine():
    return {
        "kind": "gated",
        "order": ["g1"],
        "tasks": {"g1": {"id": "g1", "status": "pending", "check": "do the thing",
                          "why_exempt": True}},
        "engine_session": {
            "session_id": "predecessor",
            "status": "active",
            "claimed_at": E._now(),
            "last_heartbeat": E._now(),
            "claimed_by": "commander",
            "worktree": ".",
        },
    }


def _ago(seconds):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


def _force_claim(path):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = E.main(["--file", str(path), "claim", "--session-id", "successor",
                       "--claimed-by", "commander", "--force",
                       "--reason", "told the predecessor was dead"])
    return code, out.getvalue(), err.getvalue()


class ForceClaimOccupancyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.spine = self.dir / "spine.json"
        E.save(self.spine, _spine())

    def _journal(self, *entries):
        (self.dir / "spine.json.journal").write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")

    def test_force_claim_succeeds_and_reports_a_live_looking_occupant(self):
        """The epic-298 shape: someone drove this plan 38 seconds ago under a
        session that is not yours. The takeover still SUCCEEDS -- this is
        information, not permission -- and the room is described."""
        self._journal(
            {"seq": 1, "ts": _ago(300), "session_id": "predecessor", "verb": "start", "task": "g1"},
            {"seq": 2, "ts": _ago(38), "session_id": "predecessor", "verb": "attest", "task": "g1"},
        )
        code, out, _ = _force_claim(self.spine)
        self.assertEqual(code, 0, "the report must never turn a force claim into a refusal")
        self.assertIn("FORCED takeover of predecessor", out)
        self.assertIn("OCCUPANCY", out)
        self.assertIn("2 entries", out)
        self.assertIn("'predecessor'", out)
        self.assertIn("38s ago", out)

    def test_report_carries_no_verdict(self):
        """Counts and ages only. A verdict built on these signals would misfire,
        and a misfire is worse than the silence it replaces."""
        self._journal({"seq": 1, "ts": _ago(10), "session_id": "predecessor",
                       "verb": "advance", "task": "g1"})
        _, out, _ = _force_claim(self.spine)
        report = out[out.index("OCCUPANCY"):].lower()
        for verdict in ("someone is live", "is alive", "do not resume", "abort",
                        "occupied", "unsafe", "safe to"):
            self.assertNotIn(verdict, report, f"report adjudicates: {verdict!r}")

    def test_non_terminal_crew_entries_are_counted_and_routed_to_recover_crews(self):
        (self.dir / "crew-runs.json").write_text(json.dumps([
            {"crew_id": "c/one", "status": "completed", "last_heartbeat": _ago(9000)},
            {"crew_id": "c/two", "status": "abandoned", "last_heartbeat": _ago(9000)},
            {"crew_id": "c/three", "status": "running", "pid": 4242,
             "last_heartbeat": _ago(45)},
        ]), encoding="utf-8")
        self._journal({"seq": 1, "ts": _ago(45), "session_id": "predecessor",
                       "verb": "start", "task": "g1"})
        _, out, _ = _force_claim(self.spine)
        self.assertIn("3 recorded, 1 not terminal", out)
        self.assertIn("c/three", out)
        self.assertIn("pid=4242", out)
        self.assertIn("recover_crews.py", out)
        self.assertNotIn("c/one", out)

    def test_absence_is_stated_rather_than_left_blank(self):
        """A silent report is indistinguishable from a report that found nothing.
        Both artifacts say 'none' out loud when they are not there."""
        _, out, _ = _force_claim(self.spine)
        self.assertIn("OCCUPANCY", out)
        self.assertIn("no prior driven verbs recorded here", out)
        self.assertIn("crew-runs    none", out)

    def test_falsified_signals_are_named_as_not_checked(self):
        """#369 proposed git authorship and worktree mtimes. Authorship was
        measured constant (every agent commits as the human) and mtimes are a
        tree walk. Saying so keeps the report's silence honest."""
        _, out, _ = _force_claim(self.spine)
        self.assertIn("not checked:", out)
        self.assertIn("git authorship", out)

    def test_malformed_artifacts_do_not_break_the_takeover(self):
        (self.dir / "spine.json.journal").write_text(
            'not json\n{"seq":1,"ts":"garbage","session_id":"x","verb":"start"}\n',
            encoding="utf-8")
        (self.dir / "crew-runs.json").write_text("{}", encoding="utf-8")
        code, out, _ = _force_claim(self.spine)
        self.assertEqual(code, 0)
        self.assertIn("unparseable timestamp", out)
        self.assertIn("crew-runs.json unreadable", out)

    def test_an_ordinary_claim_gets_no_report(self):
        """The report rides `--force` only -- the one moment an agent is
        deliberately stepping into a room it did not clear."""
        E.save(self.spine, {**_spine(), "engine_session": None})
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = E.main(["--file", str(self.spine), "claim",
                           "--session-id", "first", "--claimed-by", "commander"])
        self.assertEqual(code, 0)
        self.assertNotIn("OCCUPANCY", out.getvalue())


if __name__ == "__main__":
    unittest.main()
