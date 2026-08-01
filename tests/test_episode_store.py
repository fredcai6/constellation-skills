"""Tests for scripts/apply_episode_delta.py — the validated, all-or-nothing writer for
the episode store (docs/EPISODE_STORE.md). Every test writes to a throwaway temp store
root (mirroring tests/test_apply_lessons_delta.py's tempfile.TemporaryDirectory shape),
never the real episodes/ directory, so the repo stays clean and the suite is
order-independent.
"""

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "episodes"


def load():
    spec = importlib.util.spec_from_file_location(
        "apply_episode_delta", ROOT / "scripts" / "apply_episode_delta.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def create_op(run="governor-268", **overrides):
    op = {
        "op": "create",
        "mechanical": {
            "run": run,
            "project": "constellation-skills",
            "role": "implementer",
            "spine-step": "g1-implement",
            "context-manifest-ref": "ctx-governor-268-g1@a1b2c3d",
            "refusals": 0,
            "reopens": 1,
            "rework-count": 1,
            "failed-commands": 2,
            "artifact-ref": [
                "skills/admiral/references/fleet-doctrine.md",
                "docs/superpowers/drills/dogfood-context-paths-absent.md",
            ],
        },
        "agent_supplied": {
            "task-intent": {
                "strength": "strong",
                "statement": "Fix the STATE_NOTE-fallback wording gap named in the launch order for the Commander spine.",
            },
            "expected-behavior": {
                "strength": "medium",
                "statement": "The named launch-order defect is the only place carrying the missing-fallback wording.",
            },
            "observed-behavior": {
                "strength": "strong",
                "statement": "The Admiral spine carries the identical missing-fallback defect, unnamed by the launch order.",
            },
            "impact-cost": {
                "strength": "medium",
                "statement": "One extra sweep pass needed to find the sibling.",
            },
            "workaround": {
                "strength": "strong",
                "statement": "none.",
            },
        },
    }
    op.update(overrides)
    return op


class EpisodeStoreTestCase(unittest.TestCase):
    """Shared setup: a fresh temp store root per test, module loaded fresh."""

    def setUp(self):
        self.m = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "episodes"

    def tearDown(self):
        self.tmp.cleanup()

    def run_delta(self, delta, expect_rc=0):
        delta_path = Path(self.tmp.name) / "delta.json"
        delta_path.write_text(json.dumps(delta), encoding="utf-8")
        rc = self.m.main(["--delta", str(delta_path), "--store-root", str(self.root)])
        self.assertEqual(rc, expect_rc)

    def run_fixture(self, fixture_name, expect_rc=1):
        rc = self.m.main(
            ["--delta", str(FIXTURES / fixture_name), "--store-root", str(self.root)]
        )
        self.assertEqual(rc, expect_rc)


class RoundTripTests(EpisodeStoreTestCase):
    def test_create_writes_well_formed_episode_and_round_trips(self):
        self.run_delta({"work_id": "issue-1", "ops": [create_op()]})
        files = sorted(p.name for p in self.root.glob("*.md") if p.name != "README.md")
        self.assertEqual(files, ["governor-268-001.md"])

        path = self.root / "governor-268-001.md"
        text = path.read_text(encoding="utf-8", newline="")

        # header + heading
        self.assertIn(
            "<!-- episode-state: schema=1 id=governor-268-001 status=active -->", text
        )
        self.assertIn("# episode: governor-268-001", text)

        # partition headings always present
        self.assertIn("## Mechanical", text)
        self.assertIn("## Agent-supplied", text)
        self.assertIn("## Retirement", text)
        # no diagnosis supplied -> heading absent entirely (not empty)
        self.assertNotIn("## Diagnosis", text)

        # fixed a1..a5 kind order, per EPISODE_STORE.md section 3
        self.assertIn("### assertion:governor-268-001.a1", text)
        self.assertIn("- kind: task-intent", text)
        self.assertIn("### assertion:governor-268-001.a5", text)
        self.assertIn("- kind: workaround", text)
        a1_idx = text.index("### assertion:governor-268-001.a1")
        a5_idx = text.index("### assertion:governor-268-001.a5")
        self.assertLess(a1_idx, a5_idx)

        # every agent-supplied assertion starts active
        self.assertEqual(text.count("- lifecycle-standing: active"), 5)

        # round-trip: parse(render(...)) is byte-identical (idempotent render)
        episode = self.m.parse_episode(text)
        self.assertEqual(self.m.render_episode(episode), text)

    def test_second_create_same_run_increments_sequence(self):
        self.run_delta({"work_id": "issue-1", "ops": [create_op()]})
        self.run_delta({"work_id": "issue-2", "ops": [create_op()]})
        files = sorted(p.name for p in self.root.glob("*.md") if p.name != "README.md")
        self.assertEqual(files, ["governor-268-001.md", "governor-268-002.md"])

    def test_create_rejects_explicit_id_in_op(self):
        # The writer assigns ids itself (EPISODE_STORE.md section 2, zero agent effort) —
        # an op should not be able to smuggle one in.
        op = create_op()
        op["id"] = "governor-268-999"
        self.run_delta({"work_id": "issue-1", "ops": [op]}, expect_rc=1)


class PartitionEnforcementTests(EpisodeStoreTestCase):
    """C2 — a per-bin field-name allowlist rejects a misfiled field from EITHER
    direction, not merely documents the partition (EPISODE_STORE.md section 4)."""

    def test_misfiled_field_fixture_rejected(self):
        # C7's exact fixture path: an agent-supplied concept (lifecycle-standing) filed
        # under ## Mechanical — the precise violation section 5 warns about.
        self.run_fixture("misfiled-field-delta.json", expect_rc=1)
        # nothing written
        self.assertEqual(list(self.root.glob("*.md")) if self.root.exists() else [], [])

    def test_mechanical_field_under_agent_supplied_rejected(self):
        # The other direction: a mechanical field name (run) smuggled into the
        # agent-supplied bin instead of one of the five real kinds.
        op = create_op()
        op["agent_supplied"]["run"] = {"strength": "strong", "statement": "not a real kind"}
        self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)

    def test_agent_supplied_missing_a_required_kind_rejected(self):
        op = create_op()
        del op["agent_supplied"]["workaround"]
        self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)

    def test_unknown_mechanical_field_rejected(self):
        op = create_op()
        op["mechanical"]["not-a-real-field"] = "x"
        self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)


class ContentGuardTests(EpisodeStoreTestCase):
    """C3 — retire requires a non-empty reason (a); no agent-supplied value may embed a
    newline, the injection defense (b)."""

    def test_missing_retire_reason_fixture_rejected(self):
        # Pre-create governor-268-001 (the fixture's target id) so a rejection can only
        # be attributed to the missing reason, never to "no such episode" masking it —
        # the reason check is purely structural (validate_delta) and rejects before any
        # disk lookup happens either way.
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        self.run_fixture("missing-retire-reason-delta.json", expect_rc=1)

    def test_retire_with_absent_reason_field_rejected(self):
        # Episode exists (created first) so a failure can ONLY come from the missing
        # reason, never from a "no such episode" masking it.
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        self.run_delta({"work_id": "i1", "ops": [{"op": "retire", "id": "governor-268-001"}]}, expect_rc=1)

    def test_newline_injection_fixture_rejected(self):
        # EPISODE_STORE.md section 7's own worked warning: an observed-behavior value
        # quoting a transcript containing the literal line "- status: retired" must
        # never silently forge that line once rendered.
        self.run_fixture("newline-injection-delta.json", expect_rc=1)
        self.assertEqual(list(self.root.glob("*.md")) if self.root.exists() else [], [])

    def test_newline_in_task_intent_statement_rejected(self):
        op = create_op()
        op["agent_supplied"]["task-intent"]["statement"] = "line one\nline two"
        self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)

    def test_newline_in_amend_history_rejected(self):
        self.run_delta({"work_id": "i1", "ops": [create_op()]})
        op = {
            "op": "amend-assertion",
            "id": "governor-268-001",
            "assertion": "a4",
            "lifecycle-standing": "disputed",
            "history": "disputed 2026-08-05 (reviewer-audit)\n- status: retired",
        }
        self.run_delta({"work_id": "i2", "ops": [op]}, expect_rc=1)


class LineBoundaryGuardTests(EpisodeStoreTestCase):
    """REWORK (g2 review BLOCK, defect 1): _reject_newline() must reject every
    character str.splitlines() treats as a line boundary, not just literal \\n/\\r --
    parse_episode() sections the file with splitlines(), so any gap between the
    guard's character set and splitlines()'s own definition is a silent-corruption
    hole. Covers the reviewer's exact reproduction (U+2028) plus every other
    splitlines() boundary character, the trailing-separator edge case, and one
    end-to-end proof that the forged-status-line attack the guard exists to prevent
    is actually rejected once it reaches the writer."""

    # Every character/sequence Python's str.splitlines() treats as a line boundary
    # (see the stdlib docs for str.splitlines) that is NOT a literal \n or \r --
    # the exact gap the old character-list guard missed.
    BOUNDARY_CHARS = {
        "vertical-tab": "\v",
        "form-feed": "\f",
        "file-separator": "\x1c",
        "group-separator": "\x1d",
        "record-separator": "\x1e",
        "next-line-nel": "\x85",
        "line-separator-u2028": " ",
        "paragraph-separator-u2029": " ",
    }

    def test_reject_newline_unit_rejects_every_splitlines_boundary_character(self):
        # Direct unit coverage of the predicate itself, one assertion per character,
        # so a future regression on any single boundary character fails precisely.
        for name, ch in self.BOUNDARY_CHARS.items():
            with self.subTest(name):
                with self.assertRaises(self.m.EpisodeDeltaError):
                    self.m._reject_newline(f"safe text{ch}more text", "test")

    def test_reject_newline_unit_rejects_trailing_separator(self):
        # "text " splitlines() to a SINGLE element (['text']), so a predicate
        # that only checked len(value.splitlines()) > 1 would wrongly accept it --
        # it is still unsafe because it is not equal to the original string.
        for name, ch in self.BOUNDARY_CHARS.items():
            with self.subTest(name):
                with self.assertRaises(self.m.EpisodeDeltaError):
                    self.m._reject_newline(f"trailing separator{ch}", "test")

    def test_reject_newline_unit_still_accepts_a_genuinely_single_line_value(self):
        # No regression on the happy path: an ordinary single-line value with no
        # boundary character anywhere is still accepted.
        self.assertEqual(self.m._reject_newline("an ordinary single-line value", "test"), "an ordinary single-line value")

    def test_u2028_forged_status_line_end_to_end_create_rejected(self):
        # END-TO-END: the reviewer's exact reproduction. A create op's
        # observed-behavior statement embeds a literal "- status: retired" line
        # using U+2028 instead of \n as the separator. Neither "\n" nor "\r" is in
        # the string, so the OLD character-list guard would accept it, write the
        # file successfully once, and then silently truncate the field on the very
        # next parse_episode() call (str.splitlines() DOES split on U+2028). The
        # fixed guard must reject this delta outright, before any file is written.
        op = create_op()
        op["agent_supplied"]["observed-behavior"]["statement"] = (
            "safe text - status: retired"
        )
        self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)
        # nothing written -- the attack never lands on disk even transiently
        self.assertEqual(list(self.root.glob("*.md")) if self.root.exists() else [], [])

    def test_u2028_forged_status_line_end_to_end_amend_history_rejected(self):
        # Same attack shape via amend-assertion's history field, which is also
        # newline-guarded.
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        op = {
            "op": "amend-assertion",
            "id": "governor-268-001",
            "assertion": "a4",
            "lifecycle-standing": "disputed",
            "history": "disputed 2026-08-05 (reviewer-audit) - status: retired",
        }
        self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)


class AllOrNothingAtomicTests(EpisodeStoreTestCase):
    """C4 — an invalid op ANYWHERE in a multi-op delta leaves the store byte-for-byte
    unchanged, even when an earlier op in the same delta is individually valid and
    would, on its own, have mutated a file."""

    def test_atomic_invalid_op_in_multi_op_delta_leaves_files_unchanged(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        path = self.root / "governor-268-001.md"
        before = path.read_bytes()

        # op1 is individually valid (a real dispute against the episode just created);
        # op2 targets an episode that does not exist, so it fails only once apply_delta
        # actually gets to it -- this proves the write-plan defers ALL filesystem writes
        # until every op has succeeded, not merely that structural validation runs
        # first.
        ops = [
            {
                "op": "amend-assertion",
                "id": "governor-268-001",
                "assertion": "a4",
                "lifecycle-standing": "disputed",
                "history": "disputed 2026-08-05 (reviewer-audit) — re-read found only one pass needed",
            },
            {"op": "retire", "id": "governor-268-999", "reason": "does not exist"},
        ]
        self.run_delta({"work_id": "i1", "ops": ops}, expect_rc=1)

        after = path.read_bytes()
        self.assertEqual(before, after, "file bytes changed despite the delta being rejected")
        # and no stray new file was created either
        self.assertEqual(
            sorted(p.name for p in self.root.glob("*.md")), ["governor-268-001.md"]
        )

    def test_atomic_structurally_invalid_op_in_multi_op_delta_also_leaves_files_unchanged(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        path = self.root / "governor-268-001.md"
        before = path.read_bytes()
        ops = [create_op(), {"op": "retire", "id": "governor-268-001", "reason": "  "}]
        self.run_delta({"work_id": "i1", "ops": ops}, expect_rc=1)
        after = path.read_bytes()
        self.assertEqual(before, after)


class WritePhaseAtomicityTests(EpisodeStoreTestCase):
    """REWORK (g2 review BLOCK, defect 2): AllOrNothingAtomicTests above proves
    all-or-nothing holds for every VALIDATION-time failure (a bad op anywhere in the
    delta). This class proves it also holds for a real OS-level failure DURING the
    write phase itself -- disk full, permission denied, a locked file -- which the
    old _Transaction.commit() (sequential path.write_text() per touched file, no
    staging) did not guarantee: a failure on the 2nd of 2 writes left the 1st file's
    write landed on disk."""

    def _snapshot(self):
        """Every file under the store root, by path, as raw bytes -- content AND
        the exact set of files present, so a stray leftover temp/staged file would
        also be caught, not just a content mismatch on an existing file."""
        return {p: p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}

    def test_forced_failure_on_second_of_two_writes_leaves_store_byte_for_byte_unchanged(self):
        # Seed one pre-existing, valid episode.
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        before = self._snapshot()

        # Two INDIVIDUALLY VALID ops that each touch a different file: op1 amends
        # the pre-existing episode (touches governor-268-001.md), op2 creates a
        # brand-new episode under a different run (touches governor-269-001.md).
        # Both pass validate_delta() cleanly -- the failure this test forces is
        # purely in the write phase, not a rejected op.
        ops = [
            {
                "op": "amend-assertion",
                "id": "governor-268-001",
                "assertion": "a4",
                "lifecycle-standing": "disputed",
                "history": "disputed 2026-08-06 (rework-301-g2) -- forcing a second-write failure",
            },
            create_op(run="governor-269"),
        ]
        delta_path = Path(self.tmp.name) / "racy-delta.json"
        delta_path.write_text(json.dumps({"work_id": "i1", "ops": ops}), encoding="utf-8")

        # Monkeypatch Path.write_text to raise on exactly the SECOND call made
        # after this point (the delta file itself is already written above, before
        # the patch is installed, so it is never counted). This simulates a real
        # OS-level failure -- disk full, permission denied, a locked file -- on
        # whichever write is second in commit()'s write order, independent of
        # whether the implementation writes directly to the final path (old code)
        # or to a staged temp path first (the fix): either way it is still the
        # second call to write_text.
        original_write_text = Path.write_text
        calls = {"n": 0}

        def flaky_write_text(path_self, *args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("simulated write failure (e.g. disk full) on the second touched file")
            return original_write_text(path_self, *args, **kwargs)

        Path.write_text = flaky_write_text
        try:
            rc = self.m.main(["--delta", str(delta_path), "--store-root", str(self.root)])
        finally:
            Path.write_text = original_write_text

        self.assertEqual(rc, 1, "a mid-write I/O failure must still exit non-zero")
        self.assertGreaterEqual(calls["n"], 2, "the test did not actually reach a second write")

        after = self._snapshot()
        self.assertEqual(
            before, after,
            "store mutated (or a stray file left behind) despite a write-phase "
            "failure on the second of two touched files",
        )


class RetirementSeamTests(EpisodeStoreTestCase):
    """C8 — the retire op's layout effect routes only through apply_retirement(); the
    field diff matches EPISODE_STORE.md section 7's worked example under whichever
    adapter is active, and no assertion's own lifecycle-standing is touched."""

    def test_retire_field_diff_matches_worked_example(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        path = self.root / "governor-268-001.md"

        self.run_delta(
            {
                "work_id": "i1",
                "ops": [
                    {
                        "op": "retire",
                        "id": "governor-268-001",
                        "reason": "consolidated into cluster governor-drill-sibling-coverage-1",
                        "retired-at": "2026-08-12 (audit-308-run-4)",
                        "consolidated-into": "governor-drill-sibling-coverage-1",
                    }
                ],
            }
        )

        text = path.read_text(encoding="utf-8", newline="")
        self.assertIn("status=retired", text)  # header token stays in sync
        self.assertIn("- status: retired", text)
        self.assertIn(
            "- retired-reason: consolidated into cluster governor-drill-sibling-coverage-1",
            text,
        )
        self.assertIn("- retired-at: 2026-08-12 (audit-308-run-4)", text)
        self.assertIn("- consolidated-into: governor-drill-sibling-coverage-1", text)
        self.assertIn("- superseded-by: ", text)

        # retirement never touches any assertion's own lifecycle-standing
        self.assertEqual(text.count("- lifecycle-standing: active"), 5)

        # under the default (Option-B) adapter the file never moves
        self.assertTrue(path.exists())

    def test_retire_under_option_a_adapter_moves_file_between_active_and_retired(self):
        # Flips the module's own live switch (not the source file) to prove the seam is
        # a REAL, swappable boundary -- two working adapters behind one call site, not
        # a hypothetical one. g4's eventual binding is exactly this flip.
        self.m._LAYOUT_ADAPTER = self.m._LAYOUT_OPTION_A
        try:
            self.run_delta({"work_id": "i0", "ops": [create_op()]})
            active_path = self.root / "active" / "governor-268-001.md"
            self.assertTrue(active_path.exists())

            self.run_delta(
                {
                    "work_id": "i1",
                    "ops": [{"op": "retire", "id": "governor-268-001", "reason": "superseded"}],
                }
            )
            retired_path = self.root / "retired" / "governor-268-001.md"
            self.assertTrue(retired_path.exists(), "Option-A adapter did not move the file")
            self.assertFalse(active_path.exists(), "old active/ path should be gone after the move")
            self.assertIn("- status: retired", retired_path.read_text(encoding="utf-8", newline=""))
        finally:
            self.m._LAYOUT_ADAPTER = self.m._LAYOUT_OPTION_B


def _assertion_block(text, aid):
    """Extract one "### assertion:<id>.<aid>" block's raw text, up to (not including)
    the next "###"/"##" heading -- used to prove a sibling assertion's stored lines are
    byte-identical across a dispute."""
    pattern = re.compile(
        r"### assertion:\S+\." + re.escape(aid) + r"\n(?:(?!\n##).)*", re.DOTALL
    )
    match = pattern.search(text)
    assert match, f"assertion {aid} not found"
    return match.group(0)


class SurgicalDisputeTests(EpisodeStoreTestCase):
    """C6 — amend-assertion disputes exactly ONE named field, changing only its
    lifecycle-standing plus one appended history line. A sibling assertion's stored
    lines must be byte-identical before and after (EPISODE_STORE.md section 5)."""

    def test_dispute_changes_only_the_named_assertion_sibling_untouched(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        path = self.root / "governor-268-001.md"
        before_text = path.read_text(encoding="utf-8", newline="")
        a3_before = _assertion_block(before_text, "a3")  # observed-behavior, untouched
        a4_before = _assertion_block(before_text, "a4")  # impact-cost, will be disputed

        self.run_delta(
            {
                "work_id": "i1",
                "ops": [
                    {
                        "op": "amend-assertion",
                        "id": "governor-268-001",
                        "assertion": "a4",
                        "lifecycle-standing": "disputed",
                        "history": "disputed 2026-08-05 (reviewer-audit-268) — re-read of the sweep transcript found only one pass was actually needed",
                    }
                ],
            }
        )

        after_text = path.read_text(encoding="utf-8", newline="")
        a3_after = _assertion_block(after_text, "a3")
        a4_after = _assertion_block(after_text, "a4")

        # the sibling (a3) is byte-identical, untouched by a4's dispute
        self.assertEqual(a3_before, a3_after)

        # a4 itself: kind/strength/statement lines unchanged, only lifecycle-standing
        # flips and one history line is appended
        self.assertIn("- kind: impact-cost", a4_after)
        self.assertIn(
            "- statement: One extra sweep pass needed to find the sibling.", a4_after
        )
        self.assertIn("- strength: medium", a4_after)
        self.assertIn("- lifecycle-standing: disputed", a4_after)
        self.assertNotIn("- lifecycle-standing: active", a4_after)
        self.assertIn("- history: disputed 2026-08-05", a4_after)
        self.assertNotIn("- history:", a4_before)

        # every OTHER assertion's lifecycle-standing is untouched (still active)
        for aid in ("a1", "a2", "a3", "a5"):
            block = _assertion_block(after_text, aid)
            self.assertIn("- lifecycle-standing: active", block)

        # mechanical + retirement sections are untouched too
        mech_before = before_text[before_text.index("## Mechanical") : before_text.index("## Agent-supplied")]
        mech_after = after_text[after_text.index("## Mechanical") : after_text.index("## Agent-supplied")]
        self.assertEqual(mech_before, mech_after)
        self.assertIn("## Retirement\n- status: active", after_text)

    def test_dispute_targets_a_retired_episode_via_resolve_episode_path(self):
        # The g1 reviewer finding this handoff carries forward: amend must resolve its
        # target through resolve_episode_path() too, not just retire/fetch -- otherwise
        # amending an already-retired episode breaks once Option A binds (the file may
        # live under retired/, not the flat root).
        self.m._LAYOUT_ADAPTER = self.m._LAYOUT_OPTION_A
        try:
            self.run_delta({"work_id": "i0", "ops": [create_op()]})
            self.run_delta(
                {"work_id": "i1", "ops": [{"op": "retire", "id": "governor-268-001", "reason": "superseded"}]}
            )
            # file now lives under retired/, not active/
            self.assertFalse((self.root / "active" / "governor-268-001.md").exists())
            self.assertTrue((self.root / "retired" / "governor-268-001.md").exists())

            self.run_delta(
                {
                    "work_id": "i2",
                    "ops": [
                        {
                            "op": "amend-assertion",
                            "id": "governor-268-001",
                            "assertion": "a3",
                            "lifecycle-standing": "superseded",
                            "history": "superseded 2026-08-06 (later-audit) — a newer episode covers this",
                        }
                    ],
                }
            )
            text = (self.root / "retired" / "governor-268-001.md").read_text(encoding="utf-8", newline="")
            self.assertIn("- lifecycle-standing: superseded", text)
        finally:
            self.m._LAYOUT_ADAPTER = self.m._LAYOUT_OPTION_B


if __name__ == "__main__":
    unittest.main()
