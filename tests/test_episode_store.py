"""Tests for the episode store (docs/EPISODE_STORE.md): scripts/apply_episode_delta.py,
the validated all-or-nothing writer (gate g2), and scripts/query_episodes.py, the
deterministic retrieval surface plus issue #301's cross-session / cross-worktree
acceptance exercise (gate g3).

Every test writes to a throwaway temp store root (mirroring
tests/test_apply_lessons_delta.py's tempfile.TemporaryDirectory shape), never the real
episodes/ directory, so the repo stays clean and the suite is order-independent.
"""

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "episodes"
WRITER_SCRIPT = ROOT / "scripts" / "apply_episode_delta.py"
QUERY_SCRIPT = ROOT / "scripts" / "query_episodes.py"


def load():
    spec = importlib.util.spec_from_file_location("apply_episode_delta", WRITER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_query():
    spec = importlib.util.spec_from_file_location("query_episodes", QUERY_SCRIPT)
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

    def test_artifact_ref_with_trailing_whitespace_round_trips(self):
        # Carried defect from the g2 review (fixed at g3): every other agent-supplied
        # mechanical string is .strip()ed before storage, but artifact-ref entries were
        # stored verbatim — while parse_episode() strips the whole line before matching.
        # So an artifact-ref with trailing whitespace validated, wrote, and then silently
        # lost that whitespace on the NEXT parse: render(parse(text)) != text, with no
        # error anywhere. A round-trip over already-clean input could never catch it;
        # the input has to be dirty.
        op = create_op()
        op["mechanical"]["artifact-ref"] = [
            "docs/EPISODE_STORE.md   ",
            "  scripts/apply_episode_delta.py  ",
        ]
        self.run_delta({"work_id": "issue-1", "ops": [op]})
        text = (self.root / "governor-268-001.md").read_text(encoding="utf-8", newline="")

        self.assertIn("- artifact-ref: docs/EPISODE_STORE.md\n", text)
        self.assertIn("- artifact-ref: scripts/apply_episode_delta.py\n", text)
        self.assertNotIn("- artifact-ref: docs/EPISODE_STORE.md ", text)

        # The invariant the defect broke.
        self.assertEqual(self.m.render_episode(self.m.parse_episode(text)), text)

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


# ===================================================================================
# Gate g3 — scripts/query_episodes.py: deterministic retrieval, and issue #301's
# acceptance exercise (cross-session, cross-worktree, non-foreclosure).
# ===================================================================================


class QueryTestCase(EpisodeStoreTestCase):
    """Adds the retrieval module and a seeding helper to the writer's temp-store setup.
    Deliberately a subclass rather than an edit of EpisodeStoreTestCase, so the g2 tests
    keep exactly the setup they were written against."""

    def setUp(self):
        super().setUp()
        self.q = load_query()

    def seed(self, run="governor-268", **mechanical):
        """Write one episode through the ONLY write path (g2's validated delta writer)
        and return its assigned id. Retrieval is never tested against a hand-authored
        file — a fixture the writer could not have produced would prove nothing about
        retrieval over the real store."""
        op = create_op(run=run)
        op["mechanical"].update(mechanical)
        before = set(self.q.enumerate_episode_ids(self.root))
        self.run_delta({"work_id": "seed", "ops": [op]})
        after = set(self.q.enumerate_episode_ids(self.root))
        new = after - before
        self.assertEqual(len(new), 1, f"expected exactly one new episode, got {new}")
        return new.pop()

    def run_query(self, *args, expect_rc=0):
        """Drive query_episodes.py's CLI in-process and return its parsed JSON envelope.
        (The genuinely cross-process exercise is CrossSessionRetrievalTests below — this
        helper is for the ordinary unit-level checks.)"""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.q.main(["--store-root", str(self.root), *args])
        self.last_stderr = err.getvalue()
        self.assertEqual(rc, expect_rc, self.last_stderr)
        text = out.getvalue().strip()
        return json.loads(text) if text else None


class QueryFetchTests(QueryTestCase):
    """Fetch by id — EPISODE_STORE.md section 8's first primitive, routed through the
    resolve_episode_path() seam so the retirement layout stays unbound (section 7)."""

    def test_fetch_by_id_returns_the_whole_record(self):
        episode_id = self.seed()
        episode = self.q.fetch_episode(episode_id, self.root)
        self.assertIsNotNone(episode)
        self.assertEqual(episode.episode_id, episode_id)
        self.assertEqual(episode.role, "implementer")
        self.assertEqual(len(episode.agent_supplied), 5)

    def test_fetch_calls_the_resolve_episode_path_seam_rather_than_building_a_path(self):
        # The seam is the point: g4 binds the retirement layout by swapping this
        # function's adapter, so retrieval must ASK it, never construct <root>/<id>.md.
        episode_id = self.seed()
        calls = []
        original = self.m.resolve_episode_path

        def spy(eid, root):
            calls.append(eid)
            return original(eid, root)

        self.m.resolve_episode_path = spy
        try:
            self.assertIsNotNone(self.q.fetch_episode(episode_id, self.root))
        finally:
            self.m.resolve_episode_path = original
        self.assertEqual(calls, [episode_id])

    def test_fetch_unknown_id_is_a_visible_failure_not_an_empty_answer(self):
        self.seed()
        self.assertIsNone(self.q.fetch_episode("governor-268-999", self.root))
        self.run_query("fetch", "governor-268-999", expect_rc=2)
        self.assertIn("no such episode", self.last_stderr)

    def test_fetch_cli_emits_a_deterministic_json_envelope(self):
        episode_id = self.seed()
        payload = self.run_query("fetch", episode_id)
        self.assertEqual(payload["query"], "fetch")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["ids"], [episode_id])
        self.assertEqual(payload["results"][0]["id"], episode_id)
        self.assertEqual(payload["pid"], os.getpid())


class QueryEnumerateTests(QueryTestCase):
    """Enumerate every episode — routed through the iter_episode_ids() seam, never a
    glob at the call site."""

    def test_enumerate_returns_every_seeded_episode(self):
        ids = sorted([self.seed(), self.seed(), self.seed(run="admiral-298")])
        self.assertEqual(self.q.enumerate_episode_ids(self.root), ids)
        self.assertEqual([e.episode_id for e in self.q.enumerate_episodes(self.root)], ids)

    def test_enumerate_calls_the_iter_episode_ids_seam(self):
        self.seed()
        calls = []
        original = self.m.iter_episode_ids

        def spy(root, include_retired):
            calls.append(include_retired)
            return original(root, include_retired)

        self.m.iter_episode_ids = spy
        try:
            self.q.enumerate_episode_ids(self.root)
        finally:
            self.m.iter_episode_ids = original
        self.assertEqual(len(calls), 1)

    def test_enumerate_on_an_absent_store_root_is_empty_not_an_error(self):
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [])

    def test_enumerate_cli_envelope(self):
        ids = sorted([self.seed(), self.seed()])
        payload = self.run_query("enumerate")
        self.assertEqual(payload["query"], "enumerate")
        self.assertEqual(payload["ids"], ids)
        self.assertEqual(payload["count"], 2)


def naive_select_dict_collapse(root, field, value):
    """A NAIVE select, written the way a reasonable person writes one: read each
    episode's ## Mechanical block into a dict of `- key: value` lines, then compare.

    It is wrong, and wrong in the worst available way. artifact-ref is REPEATED — one
    line per ref — so folding the block into a dict keeps only the LAST occurrence and
    silently discards every earlier one. Query for a ref that is not an episode's final
    ref and that episode simply is not in the answer: no exception, no warning, no
    partial-result flag, just a candidate set one or more records short. This function
    exists so the store's own test suite can DEMONSTRATE the omission rather than
    assert that it was avoided.
    """
    matched = []
    for path in sorted(Path(root).glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8", newline="")
        mechanical = {}
        for line in text.splitlines():
            if line.startswith("- ") and ": " in line:
                key, _, val = line[2:].partition(": ")
                mechanical[key] = val  # last one wins — the whole defect, in one line
        if mechanical.get(field) == value:
            matched.append(path.stem)
    return sorted(matched)


def naive_select_substring(root, field, value):
    """A second naive select: a bare substring search over the file text. This one does
    not omit — it over-returns, matching any episode whose field value merely CONTAINS
    the query (so a query for a value that is a prefix of another episode's value drags
    that episode in too). The exact-match primitive must do neither."""
    matched = []
    for path in sorted(Path(root).glob("*.md")):
        if path.name == "README.md":
            continue
        if f"- {field}: {value}" in path.read_text(encoding="utf-8", newline=""):
            matched.append(path.stem)
    return sorted(matched)


class QuerySelectTests(QueryTestCase):
    """Select by exact field value / set membership — EPISODE_STORE.md section 8. Exact
    and set-membership only: no ranking, no scoring, no similarity."""

    def test_select_matches_a_scalar_field_exactly(self):
        a = self.seed(role="implementer")
        b = self.seed(role="reviewer")
        self.assertEqual(self.q.select_episode_ids(self.root, "role", ["implementer"]), [a])
        self.assertEqual(self.q.select_episode_ids(self.root, "role", ["reviewer"]), [b])

    def test_select_is_set_membership_over_several_values(self):
        a = self.seed(role="implementer")
        b = self.seed(role="reviewer")
        self.seed(role="cartographer")
        self.assertEqual(
            self.q.select_episode_ids(self.root, "role", ["implementer", "reviewer"]),
            sorted([a, b]),
        )

    def test_select_on_a_list_field_matches_on_intersection(self):
        a = self.seed(**{"artifact-ref": ["docs/EPISODE_STORE.md", "scripts/x.py"]})
        b = self.seed(**{"artifact-ref": ["scripts/y.py"]})
        self.assertEqual(self.q.select_episode_ids(self.root, "artifact-ref", ["docs/EPISODE_STORE.md"]), [a])
        self.assertEqual(self.q.select_episode_ids(self.root, "artifact-ref", ["scripts/y.py"]), [b])

    def test_select_matches_whole_values_not_prefixes(self):
        exact = self.seed(**{"spine-step": "g1"})
        longer = self.seed(**{"spine-step": "g1-implement"})
        self.assertEqual(self.q.select_episode_ids(self.root, "spine-step", ["g1"]), [exact])
        self.assertEqual(self.q.select_episode_ids(self.root, "spine-step", ["g1-implement"]), [longer])
        # ...whereas a substring search drags the longer value in. Over-returning is the
        # other half of "exact": both directions are wrong answers.
        self.assertEqual(naive_select_substring(self.root, "spine-step", "g1"), sorted([exact, longer]))

    def test_select_on_an_unknown_field_fails_visibly_rather_than_returning_nothing(self):
        self.seed()
        with self.assertRaises(self.q.QueryError):
            self.q.select_episode_ids(self.root, "not-a-field", ["x"])
        self.run_query("select", "--field", "not-a-field", "--value", "x", expect_rc=1)
        self.assertIn("not a selectable field", self.last_stderr)

    def test_select_with_no_matches_is_an_empty_set_not_an_error(self):
        self.seed(role="implementer")
        payload = self.run_query("select", "--field", "role", "--value", "admiral")
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["ids"], [])

    def test_select_cli_envelope_carries_the_query_and_matched_ids(self):
        a = self.seed(role="implementer")
        self.seed(role="reviewer")
        payload = self.run_query("select", "--field", "role", "--value", "implementer")
        self.assertEqual(payload["query"], "select")
        self.assertEqual(payload["ids"], [a])


class SilentOmissionTests(QueryTestCase):
    """The failure mode this store's whole design fears: not a crash, not an error — a
    candidate set one record short, with nothing anywhere signalling that it is short.

    Each test here runs a NAIVE implementation and the real primitive over the SAME
    adversarial store and asserts the naive one omits. A round-trip over well-formed
    input would prove nothing (lesson:round-trip-tests-prove-artifacts-not-parsers);
    the input has to be built to make the naive answer wrong.
    """

    TARGET = "docs/EPISODE_STORE.md"

    def seed_ref_position_fixture(self):
        """Three episodes that all genuinely carry TARGET as an artifact-ref — first,
        middle, and last in their respective lists. Every one of them is a correct
        answer to "which episodes reference TARGET"."""
        first = self.seed(**{"artifact-ref": [self.TARGET, "scripts/a.py", "scripts/b.py"]})
        middle = self.seed(**{"artifact-ref": ["scripts/c.py", self.TARGET, "scripts/d.py"]})
        last = self.seed(**{"artifact-ref": ["scripts/e.py", "scripts/f.py", self.TARGET]})
        return sorted([first, middle, last]), last

    def test_naive_dict_collapse_silently_omits_two_of_three_matching_episodes(self):
        all_three, only_last = self.seed_ref_position_fixture()

        naive = naive_select_dict_collapse(self.root, "artifact-ref", self.TARGET)
        ours = self.q.select_episode_ids(self.root, "artifact-ref", [self.TARGET])

        # The naive version keeps only the LAST artifact-ref line per episode, so the
        # two episodes whose matching ref is not final vanish — no error, no crash.
        self.assertEqual(naive, [only_last])
        self.assertEqual(len(naive), 1)
        # Ours returns the complete set.
        self.assertEqual(ours, all_three)
        self.assertEqual(len(ours), 3)
        # Stated as the property, not just the numbers: the naive answer is a strict
        # subset of the truth, which is exactly what "silent omission" means.
        self.assertTrue(set(naive) < set(ours))

    def test_field_values_returns_every_artifact_ref_not_just_the_last(self):
        # The single design decision that closes the hole: field_values() is list-valued
        # for EVERY field, so a repeated field can never be collapsed on the way in.
        episode_id = self.seed(**{"artifact-ref": ["a.md", "b.md", "c.md"]})
        episode = self.q.fetch_episode(episode_id, self.root)
        self.assertEqual(self.q.field_values(episode, "artifact-ref"), ["a.md", "b.md", "c.md"])
        self.assertEqual(self.q.field_values(episode, "role"), ["implementer"])

    def test_a_bare_string_is_refused_rather_than_matched_character_by_character(self):
        # Found by the g3 reviewer, fixed under fix-now triage. `set("implementer")` is a
        # set of eleven CHARACTERS, so a bare string silently matched single-character
        # values and silently MISSED the value the caller named — a wrong answer, from the
        # most natural caller idiom there is. Refusing beats wrapping: wrapping fixes this
        # call while leaving the character-set trap live for bytes or a str subclass.
        self.seed(role="implementer")
        self.seed(role="i")

        with self.assertRaises(self.q.QueryError) as caught:
            self.q.select_episodes(self.root, "role", "implementer")
        self.assertIn("not a bare", str(caught.exception))

        # The correct idiom still works, and returns ONLY the whole-value match — the
        # single-character episode must not come back.
        selected = self.q.select_episodes(self.root, "role", ["implementer"])
        roles = {self.q.field_values(e, "role")[0] for e in selected}
        self.assertEqual(roles, {"implementer"})

    def test_enumeration_returns_every_episode_including_ones_a_run_glob_would_miss(self):
        # A second omission shape: enumerating by a run-prefix glob (the id scheme makes
        # that tempting — section 2 calls the filename a free run-lookup key) silently
        # misses every episode from any other run.
        governor = [self.seed(run="governor-268") for _ in range(2)]
        admiral = [self.seed(run="admiral-298")]
        naive = sorted(p.stem for p in self.root.glob("governor-268-*.md"))
        ours = self.q.enumerate_episode_ids(self.root)
        self.assertEqual(naive, sorted(governor))
        self.assertEqual(ours, sorted(governor + admiral))
        self.assertTrue(set(naive) < set(ours))


def naive_neighbours_first_key_wins(query_module, root, episode_id):
    """A NAIVE neighbour enumeration: try each join key in turn and return as soon as
    one of them yields anything.

    It reads perfectly reasonably — "find the episodes that share an artifact, and if
    none do, fall back to the ones from the same role and step" — and it silently omits
    every neighbour joined on a LATER key whenever an earlier key matched anything at
    all. The candidate set handed to the downstream sensor is short, and nothing says
    so. The real primitive takes the UNION over every join key."""
    episode = query_module.fetch_episode(episode_id, root)
    others = [e for e in query_module.enumerate_episodes(root) if e.episode_id != episode_id]
    by_ref = sorted(
        e.episode_id for e in others if set(e.artifact_refs) & set(episode.artifact_refs)
    )
    if by_ref:
        return by_ref
    return sorted(
        e.episode_id
        for e in others
        if (e.role, e.spine_step) == (episode.role, episode.spine_step)
    )


class QueryNeighbourTests(QueryTestCase):
    """Enumerate neighbours — for episode E, every OTHER episode sharing at least one
    exact join key with E (EPISODE_STORE.md section 8). The union IS the candidate set a
    downstream sensor consumes: complete by construction, unranked, self excluded."""

    def test_neighbours_by_shared_artifact_ref(self):
        anchor = self.seed(**{"artifact-ref": ["docs/EPISODE_STORE.md"], "role": "implementer"})
        sharer = self.seed(**{"artifact-ref": ["docs/EPISODE_STORE.md", "x.md"], "role": "reviewer", "spine-step": "g9"})
        self.seed(**{"artifact-ref": ["unrelated.md"], "role": "admiral", "spine-step": "gz"})
        self.assertEqual(self.q.neighbour_ids(self.root, anchor), [sharer])

    def test_neighbours_by_shared_role_and_spine_step_pair(self):
        anchor = self.seed(**{"artifact-ref": ["a.md"], "role": "implementer", "spine-step": "g3"})
        same_pair = self.seed(**{"artifact-ref": ["b.md"], "role": "implementer", "spine-step": "g3"})
        # same role, DIFFERENT step -> the pair does not match, so not a neighbour
        self.seed(**{"artifact-ref": ["c.md"], "role": "implementer", "spine-step": "g4"})
        self.assertEqual(self.q.neighbour_ids(self.root, anchor), [same_pair])

    def test_an_episode_is_never_its_own_neighbour(self):
        anchor = self.seed(**{"artifact-ref": ["a.md"]})
        self.assertNotIn(anchor, self.q.neighbour_ids(self.root, anchor))
        self.assertEqual(self.q.neighbour_ids(self.root, anchor), [])

    def test_neighbours_of_an_unknown_episode_fails_visibly(self):
        self.seed()
        with self.assertRaises(self.q.QueryError):
            self.q.neighbour_ids(self.root, "governor-268-999")
        self.run_query("neighbours", "governor-268-999", expect_rc=2)

    def test_naive_first_key_wins_silently_omits_the_other_join_key(self):
        # The adversarial fixture: the anchor has exactly one neighbour per join key.
        anchor = self.seed(
            **{"artifact-ref": ["docs/EPISODE_STORE.md"], "role": "implementer", "spine-step": "g3"}
        )
        by_ref = self.seed(
            **{"artifact-ref": ["docs/EPISODE_STORE.md"], "role": "admiral", "spine-step": "gz"}
        )
        by_pair = self.seed(
            **{"artifact-ref": ["something-else.md"], "role": "implementer", "spine-step": "g3"}
        )

        naive = naive_neighbours_first_key_wins(self.q, self.root, anchor)
        ours = self.q.neighbour_ids(self.root, anchor)

        self.assertEqual(naive, [by_ref])  # stops at the first key that matched
        self.assertEqual(ours, sorted([by_ref, by_pair]))  # the union
        self.assertTrue(set(naive) < set(ours))

    def test_neighbours_cli_envelope(self):
        anchor = self.seed(**{"artifact-ref": ["shared.md"], "spine-step": "g1"})
        sharer = self.seed(**{"artifact-ref": ["shared.md"], "spine-step": "g2"})
        payload = self.run_query("neighbours", anchor)
        self.assertEqual(payload["query"], "neighbours")
        self.assertEqual(payload["ids"], [sharer])


class SeparateProcessMixin:
    """Launch a real, separately-booted Python interpreter and observe its OS pid.

    subprocess + sys.executable is the whole point: issue #301's acceptance criterion is
    that a seeded episode is retrievable ACROSS SESSIONS, and a test that calls a
    function twice in one interpreter has not crossed a session boundary — it has
    proved that a warm module still holds the value it was just handed. Every child
    below is started with Popen so the PARENT observes each child's pid directly, and
    the query child reports its own os.getpid() back inside its JSON answer, so the
    answer can be tied to the process that produced it rather than assumed.
    """

    CHILD_TIMEOUT = 120

    def run_in_separate_process(self, script, args, cwd):
        argv = [sys.executable, str(script), *args]
        proc = subprocess.Popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(cwd),
        )
        try:
            out, err = proc.communicate(timeout=self.CHILD_TIMEOUT)
        except subprocess.TimeoutExpired:
            # Guaranteed stop-signal: never leave a child running behind a failed test.
            proc.kill()
            out, err = proc.communicate()
            self.fail(f"child process timed out: {argv}\nstdout={out}\nstderr={err}")
        return {"argv": argv, "pid": proc.pid, "rc": proc.returncode, "out": out, "err": err}

    def seed_in_separate_process(self, store_root, work_dir, op):
        delta_path = Path(work_dir) / "cross-session-delta.json"
        delta_path.write_text(
            json.dumps({"work_id": "cross-session", "ops": [op]}), encoding="utf-8"
        )
        result = self.run_in_separate_process(
            WRITER_SCRIPT,
            ["--delta", str(delta_path), "--store-root", str(store_root)],
            cwd=work_dir,
        )
        self.assertEqual(result["rc"], 0, result["err"])
        match = re.search(r"created episode:(\S+)", result["out"])
        self.assertIsNotNone(match, result["out"])
        result["episode_id"] = match.group(1)
        return result


class CrossSessionRetrievalTests(QueryTestCase, SeparateProcessMixin):
    """C2 — the issue's headline acceptance criterion, EXERCISED: an episode seeded in
    one session is retrievable in a genuinely separate one."""

    def test_episode_seeded_in_one_process_is_retrievable_in_a_freshly_booted_one(self):
        statement = "Seeded by session 1; retrieved by session 2."
        op = create_op()
        op["agent_supplied"]["observed-behavior"]["statement"] = statement

        # --- session 1: a separately launched interpreter WRITES -------------------
        seed = self.seed_in_separate_process(self.root, self.tmp.name, op)
        episode_id = seed["episode_id"]

        # --- session 2: a second, separately launched interpreter READS ------------
        # It is handed nothing but the store root and the id. No shared module state,
        # no warm cache, no in-process handle survives from session 1 — that process
        # has already exited.
        query = self.run_in_separate_process(
            QUERY_SCRIPT,
            ["--store-root", str(self.root), "fetch", episode_id],
            cwd=self.tmp.name,
        )
        self.assertEqual(query["rc"], 0, query["err"])
        payload = json.loads(query["out"])

        # The boundary is real: three distinct OS processes.
        self.assertNotEqual(seed["pid"], query["pid"])
        self.assertNotIn(os.getpid(), (seed["pid"], query["pid"]))
        # And the answer really came from that other process — the retrieving child
        # reports its own getpid(), and it matches the pid the parent observed when it
        # launched it.
        self.assertEqual(payload["pid"], query["pid"])

        # The record crossed intact.
        self.assertEqual(payload["ids"], [episode_id])
        record = payload["results"][0]
        self.assertEqual(record["id"], episode_id)
        self.assertEqual(record["mechanical"]["role"], "implementer")
        observed = [a for a in record["agent-supplied"] if a["kind"] == "observed-behavior"]
        self.assertEqual(observed[0]["statement"], statement)
        self.assertEqual(observed[0]["lifecycle-standing"], "active")

    def test_the_cross_session_exercise_is_not_vacuous(self):
        """Falsification guard. The test above would be worthless if the retrieving
        process could answer without the store — so point an identical session 2 at a
        DIFFERENT, empty store root and confirm it fails to find the episode. What
        carries the episode across the boundary is the store on disk and nothing else.
        """
        seed = self.seed_in_separate_process(self.root, self.tmp.name, create_op())
        empty_root = Path(self.tmp.name) / "somewhere-else"
        empty_root.mkdir()
        query = self.run_in_separate_process(
            QUERY_SCRIPT,
            ["--store-root", str(empty_root), "fetch", seed["episode_id"]],
            cwd=self.tmp.name,
        )
        self.assertEqual(query["rc"], 2)
        self.assertIn("no such episode", query["err"])

    def test_a_third_session_enumerates_what_the_first_two_never_told_it_about(self):
        # Enumeration in a fresh process, with NO id supplied to it at all: the store
        # itself is the only channel.
        first = self.seed_in_separate_process(self.root, self.tmp.name, create_op())
        second = self.seed_in_separate_process(self.root, self.tmp.name, create_op(run="admiral-298"))
        listing = self.run_in_separate_process(
            QUERY_SCRIPT, ["--store-root", str(self.root), "enumerate"], cwd=self.tmp.name
        )
        self.assertEqual(listing["rc"], 0, listing["err"])
        payload = json.loads(listing["out"])
        self.assertEqual(payload["ids"], sorted([first["episode_id"], second["episode_id"]]))
        self.assertEqual(
            len({first["pid"], second["pid"], listing["pid"], os.getpid()}), 4,
            "each session must be its own OS process",
        )


def force_rmtree(path):
    """shutil.rmtree with the Windows read-only escape hatch. Git marks objects under
    .git/ read-only, and on Windows a read-only file cannot be unlinked — rmtree raises
    PermissionError instead of cleaning up, stranding temp repos. The handler clears the
    read-only bit and retries the operation that failed."""

    def on_error(func, target, _exc_info):
        try:
            os.chmod(target, stat.S_IWRITE)
            func(target)
        except OSError:
            pass  # best effort: a leaked temp dir must never fail a passing test

    shutil.rmtree(path, onerror=on_error)


@unittest.skipIf(shutil.which("git") is None, "git is required for the cross-worktree exercise")
class CrossWorktreeSharingTests(QueryTestCase, SeparateProcessMixin):
    """C3 — cross-worktree sharing, exercised THROUGH GIT (EPISODE_STORE.md section 9).

    This is the mechanism that actually provides cross-worktree durability now that the
    store is a tracked path, so it is exercised the way it really works: a real
    `git worktree add` against a real repository, a real commit in one worktree, the
    ordinary merge path, and retrieval from a SECOND worktree. A test that simulated a
    worktree with a directory name would pass while proving nothing — a store that
    silos per worktree passes a same-directory test too, and that is exactly the
    silently-wrong-but-green shape this exercise guards against.

    The reader worktree is created BEFORE the episode exists and queried BEFORE the
    merge, so the "absent, then present" transition is observed rather than assumed.
    """

    def setUp(self):
        super().setUp()
        self.repo_dir = Path(tempfile.mkdtemp(prefix="episode-store-worktrees-"))
        self.addCleanup(self.cleanup_repo)
        self.origin = self.repo_dir / "origin"
        self.origin.mkdir()
        self.git("init", "-b", "main", cwd=self.origin)
        # Local identity + no signing, so `git commit` cannot fail on an unconfigured
        # user or a signing key that is not available in a test environment.
        self.git("config", "user.email", "episode-store-test@example.invalid", cwd=self.origin)
        self.git("config", "user.name", "Episode Store Test", cwd=self.origin)
        self.git("config", "commit.gpgsign", "false", cwd=self.origin)
        (self.origin / "episodes").mkdir()
        (self.origin / "episodes" / "README.md").write_text(
            "# episodes\n", encoding="utf-8", newline=""
        )
        self.git("add", "episodes", cwd=self.origin)
        self.git("commit", "-m", "seed the tracked episodes/ path", cwd=self.origin)

    def cleanup_repo(self):
        force_rmtree(self.repo_dir)

    def git(self, *args, cwd):
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(result.returncode, 0, f"git {' '.join(args)} failed:\n{result.stderr}")
        return result.stdout

    def query_in(self, worktree, *args, expect_rc=0):
        """Run retrieval in a freshly booted interpreter whose CWD is that worktree,
        against that worktree's OWN episodes/ directory."""
        result = self.run_in_separate_process(
            QUERY_SCRIPT,
            ["--store-root", str(Path(worktree) / "episodes"), *args],
            cwd=worktree,
        )
        self.assertEqual(result["rc"], expect_rc, result["err"])
        return result

    def test_episode_committed_in_one_worktree_is_retrievable_from_another(self):
        # --- two REAL linked worktrees --------------------------------------------
        writer_wt = self.repo_dir / "wt-writer"
        reader_wt = self.repo_dir / "wt-reader"
        self.git("worktree", "add", "-b", "writer-branch", str(writer_wt), "main", cwd=self.origin)
        self.git("worktree", "add", "-b", "reader-branch", str(reader_wt), "main", cwd=self.origin)

        listing = self.git("worktree", "list", cwd=self.origin)
        self.assertIn("wt-writer", listing)
        self.assertIn("wt-reader", listing)
        # A linked worktree's .git is a FILE pointing into the main repo's
        # .git/worktrees/<name> — not a directory. This is the assertion that a
        # directory-name simulation cannot pass.
        for worktree in (writer_wt, reader_wt):
            self.assertTrue((worktree / ".git").is_file(), f"{worktree} is not a linked worktree")
            gitdir = (worktree / ".git").read_text(encoding="utf-8").strip()
            self.assertTrue(gitdir.startswith("gitdir:"), gitdir)
            self.assertIn(".git/worktrees/", gitdir.replace("\\", "/"))
        # ...and they are genuinely separate directories, not two names for one.
        self.assertNotEqual(writer_wt.resolve(), reader_wt.resolve())

        # --- BEFORE: the reader worktree has no such episode -----------------------
        before = self.query_in(reader_wt, "enumerate")
        self.assertEqual(json.loads(before["out"])["ids"], [])

        # --- worktree W: a commander writes and COMMITS inside its own worktree ----
        # (section 9 step 1 — every commander only ever writes inside the worktree it
        # owns; the episode reaches anyone else through git, never by reaching into
        # another worktree's files.)
        statement = "Written in wt-writer; read from wt-reader."
        op = create_op()
        op["agent_supplied"]["observed-behavior"]["statement"] = statement
        seed = self.seed_in_separate_process(writer_wt / "episodes", writer_wt, op)
        episode_id = seed["episode_id"]
        self.git("add", "episodes", cwd=writer_wt)
        self.git("commit", "-m", f"capture episode {episode_id}", cwd=writer_wt)

        # The reader worktree STILL cannot see it — the commit has not reached it.
        still_absent = self.query_in(reader_wt, "enumerate")
        self.assertEqual(json.loads(still_absent["out"])["ids"], [])
        self.assertFalse((reader_wt / "episodes" / f"{episode_id}.md").exists())
        self.query_in(reader_wt, "fetch", episode_id, expect_rc=2)

        # --- the ordinary git path (section 9 steps 2-3) ---------------------------
        self.git("merge", "--no-edit", "writer-branch", cwd=self.origin)  # onto main
        self.git("merge", "--no-edit", "main", cwd=reader_wt)             # into worktree R

        # --- AFTER: retrievable from the second worktree, in a fresh process -------
        after = self.query_in(reader_wt, "fetch", episode_id)
        payload = json.loads(after["out"])
        self.assertEqual(payload["ids"], [episode_id])
        self.assertNotIn(os.getpid(), (seed["pid"], after["pid"]))
        record = payload["results"][0]
        observed = [a for a in record["agent-supplied"] if a["kind"] == "observed-behavior"]
        self.assertEqual(observed[0]["statement"], statement)

        # --- what is identical across the worktree boundary, stated exactly --------
        # (a) The RECORD is identical. This is section 9's actual claim: the same
        #     logical file in every worktree of the same repo.
        writer_record = self.q.fetch_episode(episode_id, writer_wt / "episodes")
        reader_record = self.q.fetch_episode(episode_id, reader_wt / "episodes")
        self.assertEqual(
            self.q.episode_to_dict(writer_record), self.q.episode_to_dict(reader_record)
        )
        # (b) Git's own content address is identical — the durable cross-worktree
        #     identity, and the one section 8 leans on when it says any
        #     content-addressable artifact under git can be pinned to its blob hash.
        #     Git hashes the NORMALIZED index content, so this holds regardless of what
        #     any worktree's checkout did to line endings.
        writer_blob = self.git("rev-parse", f"HEAD:episodes/{episode_id}.md", cwd=writer_wt).strip()
        reader_blob = self.git("rev-parse", f"HEAD:episodes/{episode_id}.md", cwd=reader_wt).strip()
        self.assertEqual(writer_blob, reader_blob)
        # (c) Raw WORKING-TREE bytes may legitimately differ, but only in line endings
        #     — see test_working_tree_bytes_are_not_the_cross_worktree_identity below,
        #     which is where that hazard is pinned down.
        writer_bytes = (writer_wt / "episodes" / f"{episode_id}.md").read_bytes()
        reader_bytes = (reader_wt / "episodes" / f"{episode_id}.md").read_bytes()
        self.assertEqual(
            writer_bytes.replace(b"\r\n", b"\n"), reader_bytes.replace(b"\r\n", b"\n")
        )

    def test_working_tree_bytes_are_not_the_cross_worktree_identity(self):
        """A finding, pinned as a test rather than left as prose.

        On a machine with core.autocrlf=true (the Git-for-Windows default, and the
        setting on this one), git converts line endings on CHECKOUT. The writer emits
        LF-only bytes; a second worktree that materializes the same commit gets CRLF.
        So the episode's raw working-tree bytes are NOT stable across worktrees, even
        though the episode is.

        This does not weaken C3 — retrieval crosses the boundary intact either way,
        because the record, not the byte string, is what the store promises. It does
        mean anything downstream that wants a stable content address for an episode
        must use git's blob hash (computed on the normalized index content) and not a
        hash of the file it finds in its own worktree. That is exactly what
        EPISODE_STORE.md section 8's `<ref>@<revision>` pinning already prescribes, so
        the contract is intact — but a future consolidation/dedup pass (#308) that
        compares episodes by reading and hashing working-tree bytes would be silently
        wrong on Windows, which is why this is asserted here rather than assumed.
        """
        writer_wt = self.repo_dir / "wt-eol-writer"
        reader_wt = self.repo_dir / "wt-eol-reader"
        self.git("worktree", "add", "-b", "eol-writer", str(writer_wt), "main", cwd=self.origin)
        self.git("worktree", "add", "-b", "eol-reader", str(reader_wt), "main", cwd=self.origin)

        seed = self.seed_in_separate_process(writer_wt / "episodes", writer_wt, create_op())
        episode_id = seed["episode_id"]
        self.git("add", "episodes", cwd=writer_wt)
        self.git("commit", "-m", f"capture episode {episode_id}", cwd=writer_wt)
        self.git("merge", "--no-edit", "eol-writer", cwd=self.origin)
        self.git("merge", "--no-edit", "main", cwd=reader_wt)

        writer_bytes = (writer_wt / "episodes" / f"{episode_id}.md").read_bytes()
        reader_bytes = (reader_wt / "episodes" / f"{episode_id}.md").read_bytes()

        # The writer's own output is always LF-only, on every platform.
        self.assertNotIn(b"\r\n", writer_bytes)

        # Whatever the checkout did, these two things always hold:
        #   the records are equal, and the bytes differ by line endings at most.
        self.assertEqual(
            writer_bytes.replace(b"\r\n", b"\n"), reader_bytes.replace(b"\r\n", b"\n")
        )
        # And git's stored (index) content is LF either way — the stable identity.
        eol_info = self.git("ls-files", "--eol", f"episodes/{episode_id}.md", cwd=reader_wt)
        self.assertIn("i/lf", eol_info)

        if b"\r\n" in reader_bytes:
            # The hazard is live in this environment. Retrieval still works — that is
            # the point being certified — but a raw byte comparison across worktrees
            # would have been a false negative.
            self.assertNotEqual(writer_bytes, reader_bytes)
            self.assertEqual(
                self.q.episode_to_dict(self.q.fetch_episode(episode_id, writer_wt / "episodes")),
                self.q.episode_to_dict(self.q.fetch_episode(episode_id, reader_wt / "episodes")),
            )

    def test_the_two_worktrees_do_not_share_a_directory(self):
        """Falsification guard for the exercise above. If the two worktrees were secretly
        the same directory (or a symlink pair), the "retrievable from the second
        worktree" result would be trivially true and would prove nothing about git. Write
        an uncommitted file in one and confirm the other cannot see it: what crosses is
        the COMMIT, not the filesystem."""
        writer_wt = self.repo_dir / "wt-a"
        reader_wt = self.repo_dir / "wt-b"
        self.git("worktree", "add", "-b", "branch-a", str(writer_wt), "main", cwd=self.origin)
        self.git("worktree", "add", "-b", "branch-b", str(reader_wt), "main", cwd=self.origin)

        seed = self.seed_in_separate_process(writer_wt / "episodes", writer_wt, create_op())
        # Deliberately NOT committed.
        self.assertTrue((writer_wt / "episodes" / f"{seed['episode_id']}.md").exists())
        self.assertFalse((reader_wt / "episodes" / f"{seed['episode_id']}.md").exists())
        self.assertEqual(json.loads(self.query_in(reader_wt, "enumerate")["out"])["ids"], [])


class NonForeclosureTests(QueryTestCase):
    """C4 — the priority-1 obligation, exercised by retrieval.

    EPISODE_STORE.md section 5's whole claim is that disputing one agent-supplied
    assertion is a one-field, append-history mutation — never a record rewrite. "Never
    rewritten" is a claim about BYTES, so it is checked in bytes: the file is read with
    open(path, 'rb') before and after, with no decoding and no newline translation
    anywhere in the comparison path, because Python's universal-newline handling would
    happily make a CRLF and an LF file compare equal and hand back a false pass. (The
    writer itself reads and writes with newline="" for the same reason.)
    """

    def assertion_block(self, raw: bytes, episode_id: str, aid: str) -> bytes:
        """The exact bytes of one `### assertion:<id>.<aid>` block, from its heading up
        to the next blank-line-separated block. Sliced out of the raw bytes rather than
        reconstructed, so what is compared is what is genuinely on disk."""
        heading = f"### assertion:{episode_id}.{aid}".encode("utf-8")
        start = raw.index(heading)
        end = raw.index(b"\n\n", start)
        return raw[start:end]

    def test_disputing_one_assertion_leaves_its_siblings_byte_identical(self):
        episode_id = self.seed()
        path = self.root / f"{episode_id}.md"

        before_raw = path.read_bytes()
        before = self.q.fetch_episode(episode_id, self.root)
        self.assertEqual(before.agent_supplied["impact-cost"].lifecycle_standing, "active")
        self.assertEqual(before.agent_supplied["observed-behavior"].lifecycle_standing, "active")
        sibling_before = self.assertion_block(before_raw, episode_id, "a3")

        # Dispute exactly ONE agent-supplied field: a4 (impact-cost), section 5's own
        # worked walk-through.
        self.run_delta(
            {
                "work_id": "reviewer-audit-268",
                "ops": [
                    {
                        "op": "amend-assertion",
                        "id": episode_id,
                        "assertion": "a4",
                        "lifecycle-standing": "disputed",
                        "history": "disputed 2026-08-05 (reviewer-audit-268) — re-read of the sweep transcript found only one pass was needed",
                    }
                ],
            }
        )

        after_raw = path.read_bytes()
        after = self.q.fetch_episode(episode_id, self.root)

        # (a) the disputed field's standing changed...
        self.assertEqual(after.agent_supplied["impact-cost"].lifecycle_standing, "disputed")
        self.assertEqual(len(after.agent_supplied["impact-cost"].history), 1)
        self.assertIn("reviewer-audit-268", after.agent_supplied["impact-cost"].history[0])

        # (b) ...a sibling agent-supplied field's standing did not...
        self.assertEqual(after.agent_supplied["observed-behavior"].lifecycle_standing, "active")
        for kind in ("task-intent", "expected-behavior", "observed-behavior", "workaround"):
            self.assertEqual(after.agent_supplied[kind].lifecycle_standing, "active")
            self.assertEqual(after.agent_supplied[kind].history, [])

        # (c) ...and the sibling's stored line is BYTE-IDENTICAL before and after, so
        # the record was not rewritten to accommodate the dispute.
        sibling_after = self.assertion_block(after_raw, episode_id, "a3")
        self.assertEqual(sibling_before, sibling_after)
        self.assertEqual(
            sibling_after,
            b"### assertion:%s.a3\n- kind: observed-behavior\n- strength: strong\n"
            b"- lifecycle-standing: active\n- statement: The Admiral spine carries the "
            b"identical missing-fallback defect, unnamed by the launch order."
            % episode_id.encode("utf-8"),
        )
        # And the ONLY bytes that changed anywhere in the file are a4's.
        self.assertNotEqual(before_raw, after_raw)
        self.assertEqual(
            before_raw.replace(
                self.assertion_block(before_raw, episode_id, "a4"),
                self.assertion_block(after_raw, episode_id, "a4"),
            ),
            after_raw,
        )

    def test_the_mechanical_bin_and_retirement_block_are_untouched_by_a_dispute(self):
        # Section 5: a mechanical fact is never edited, and section 7: retirement and
        # lifecycle-standing are separate operations that a dispute never conflates.
        episode_id = self.seed(**{"artifact-ref": ["a.md", "b.md"]})
        path = self.root / f"{episode_id}.md"
        before_raw = path.read_bytes()
        mech_before = before_raw[before_raw.index(b"## Mechanical") : before_raw.index(b"## Agent-supplied")]
        retire_before = before_raw[before_raw.index(b"## Retirement") :]

        self.run_delta(
            {
                "work_id": "audit",
                "ops": [
                    {
                        "op": "amend-assertion",
                        "id": episode_id,
                        "assertion": "a4",
                        "lifecycle-standing": "disputed",
                        "history": "disputed by a later audit",
                    }
                ],
            }
        )

        after_raw = path.read_bytes()
        self.assertEqual(
            after_raw[after_raw.index(b"## Mechanical") : after_raw.index(b"## Agent-supplied")],
            mech_before,
        )
        self.assertEqual(after_raw[after_raw.index(b"## Retirement") :], retire_before)
        # Retrieval still finds it by every mechanical key it had before: disputing a
        # claim does not remove an episode from the candidate set.
        self.assertIn(episode_id, self.q.select_episode_ids(self.root, "artifact-ref", ["a.md"]))

    def test_a_disputed_episode_is_still_retrievable_and_reports_its_standing(self):
        # Non-foreclosure at the retrieval surface: the dispute is VISIBLE to a reader,
        # and the store does not quietly drop a disputed claim (or its episode).
        episode_id = self.seed()
        self.run_delta(
            {
                "work_id": "audit",
                "ops": [
                    {
                        "op": "amend-assertion",
                        "id": episode_id,
                        "assertion": "a4",
                        "lifecycle-standing": "disputed",
                        "history": "disputed by a later audit",
                    }
                ],
            }
        )
        payload = self.run_query("fetch", episode_id)
        standings = {a["kind"]: a["lifecycle-standing"] for a in payload["results"][0]["agent-supplied"]}
        self.assertEqual(standings["impact-cost"], "disputed")
        self.assertEqual(standings["observed-behavior"], "active")
        self.assertIn(episode_id, self.q.enumerate_episode_ids(self.root))


class MechanicalOnlyRetrievalTests(QueryTestCase):
    """C5 — retrieval is exact-match and set-membership only (EPISODE_STORE.md section
    8). No ranking, no scoring, no similarity, no embedding. What a downstream sensor
    receives is a complete, unordered candidate set; the stochastic judgment happens on
    top of this surface, never inside it (B0.1, the stochastic boundary)."""

    def test_the_candidate_set_does_not_depend_on_the_order_episodes_were_written(self):
        # Two stores with the same episodes written in opposite orders must yield the
        # same candidate SET. (Ids are run+sequence, so the two stores' ids differ —
        # compare the recovered content, which is what "the same set" means here.)
        def build(order):
            root = Path(self.tmp.name) / f"store-{order[0]}{order[-1]}"
            for step in order:
                op = create_op()
                op["mechanical"]["spine-step"] = step
                op["mechanical"]["artifact-ref"] = ["shared.md"]
                delta_path = Path(self.tmp.name) / "d.json"
                delta_path.write_text(json.dumps({"work_id": "o", "ops": [op]}), encoding="utf-8")
                self.assertEqual(
                    self.m.main(["--delta", str(delta_path), "--store-root", str(root)]), 0
                )
            return root

        forward = build(["g1", "g2", "g3"])
        backward = build(["g3", "g2", "g1"])
        steps = lambda root: sorted(
            e.spine_step for e in self.q.select_episodes(root, "artifact-ref", ["shared.md"])
        )
        self.assertEqual(steps(forward), steps(backward))
        self.assertEqual(steps(forward), ["g1", "g2", "g3"])

    def test_results_carry_no_score_rank_or_similarity_field(self):
        episode_id = self.seed()
        payload = self.run_query("fetch", episode_id)
        record = payload["results"][0]
        flattened = json.dumps(payload).lower()
        for forbidden in ("score", "rank", "similarity", "distance", "relevance", "embedding", "confidence"):
            self.assertNotIn(f'"{forbidden}"', flattened)
        self.assertEqual(
            set(record), {"id", "mechanical", "agent-supplied", "diagnosis", "retirement"}
        )

    def test_the_module_imports_no_ranking_or_embedding_machinery(self):
        source = QUERY_SCRIPT.read_text(encoding="utf-8")
        imports = [
            line.strip()
            for line in source.splitlines()
            if re.match(r"^\s*(import|from)\s", line)
        ]
        self.assertTrue(imports)
        for line in imports:
            for forbidden in ("numpy", "scipy", "sklearn", "difflib", "sentence", "embed", "faiss", "rapidfuzz"):
                self.assertNotIn(forbidden, line.lower(), f"ranking machinery imported: {line}")
        # No sorting by anything but the id, either — a "most shared keys first" order
        # would be scoring wearing a sort's clothes.
        self.assertNotIn("key=lambda", source)

    def test_neighbours_are_not_ordered_by_how_many_join_keys_they_share(self):
        anchor = self.seed(**{"artifact-ref": ["z.md"], "role": "implementer", "spine-step": "g3"})
        # `weak` shares one key; `strong` shares both. If anything ranked, `strong`
        # would come first — it does not; the answer is id-sorted.
        strong = self.seed(**{"artifact-ref": ["z.md"], "role": "implementer", "spine-step": "g3"})
        weak = self.seed(**{"artifact-ref": ["z.md"], "role": "admiral", "spine-step": "gz"})
        self.assertEqual(self.q.neighbour_ids(self.root, anchor), sorted([strong, weak]))


class LayoutIndependenceTests(QueryTestCase):
    """The retirement layout (EPISODE_STORE.md section 7) is HELD OPEN for human
    ratification and is bound at g4. This gate must not bind it — and that has to be
    true of the retrieval CODE, not merely of a primitive's name."""

    def test_query_module_inlines_no_status_check_and_no_directory_check(self):
        source = QUERY_SCRIPT.read_text(encoding="utf-8")
        # Strip comments and docstrings: the module DISCUSSES retirement at length (it
        # documents what g4 must do), and a naive grep over prose would either fire on
        # the documentation or, worse, be quietly relaxed until it stopped firing.
        code = "".join(
            line.split("#", 1)[0]
            for line in source.splitlines(keepends=True)
        )
        code = re.sub(r'"""[\s\S]*?"""', "", code)

        # What is banned is the PREDICATE, not the word. Serializing the record's own
        # `retired-reason` field is data (and is layout-invariant — section 7 keeps the
        # same field diff under both options); comparing against the bare value
        # "retired", or naming an active/ or retired/ directory, is the layout check
        # that must live behind a seam. So the assertions target the exact literals a
        # status check or a directory check would have to use.
        # (assertTrue with a short message, not assertNotIn, so a failure names the
        # offending construct instead of dumping the whole module.)
        for banned in ('"retired"', "'retired'", '"active"', "'active'", "active/", "retired/"):
            self.assertTrue(
                banned not in code,
                f"layout check inlined in query_episodes.py: found {banned}",
            )
        # Branching on status is the Option-B adapter's job, behind the membership
        # seam. Reading .status to SERIALIZE it is data, and layout-invariant.
        branch = re.search(r"\.status\s*(==|!=|\bin\b)|if[^\n]*\.status", code)
        self.assertIsNone(branch, f"episode status branched on here: {branch.group(0) if branch else ''}")
        self.assertTrue(".glob(" not in code, "store scanning must go through iter_episode_ids()")
        # ...and the seams it MUST use are actually used.
        for seam in ("resolve_episode_path", "iter_episode_ids", "parse_episode"):
            self.assertTrue(seam in code, f"{seam} seam not called")

    def test_retrieval_survives_flipping_the_layout_adapter(self):
        """The real proof that nothing is bound: run the identical retrieval under BOTH
        candidate adapters. Option A stores episodes under active/ and retired/; Option
        B keeps them flat. The primitives are told neither — they ask the seams — so the
        same queries must return the same answers under both."""
        results = {}
        for adapter in (self.m._LAYOUT_OPTION_B, self.m._LAYOUT_OPTION_A):
            original = self.m._LAYOUT_ADAPTER
            self.m._LAYOUT_ADAPTER = adapter
            root = Path(self.tmp.name) / f"store-{adapter}"
            try:
                op = create_op()
                op["mechanical"]["artifact-ref"] = ["shared.md", "other.md"]
                delta_path = Path(self.tmp.name) / f"d-{adapter}.json"
                delta_path.write_text(json.dumps({"work_id": "o", "ops": [op]}), encoding="utf-8")
                self.assertEqual(
                    self.m.main(["--delta", str(delta_path), "--store-root", str(root)]), 0
                )
                episode_id = self.q.enumerate_episode_ids(root)[0]
                results[adapter] = {
                    "ids": self.q.enumerate_episode_ids(root),
                    "fetched": self.q.fetch_episode(episode_id, root).role,
                    "selected": self.q.select_episode_ids(root, "artifact-ref", ["shared.md"]),
                    "neighbours": self.q.neighbour_ids(root, episode_id),
                }
            finally:
                self.m._LAYOUT_ADAPTER = original

        # Option A really did use a different on-disk layout...
        self.assertTrue((Path(self.tmp.name) / "store-A" / "active").is_dir())
        self.assertFalse((Path(self.tmp.name) / "store-B" / "active").exists())
        # ...and retrieval could not tell.
        self.assertEqual(results["A"], results["B"])

    def test_the_membership_seam_is_left_for_g4_and_still_answers(self):
        # Not called by any primitive here (no retirement-dependent retrieval is built
        # at this gate), but named so g4's composition rule — scan with
        # iter_episode_ids(), then confirm each id through is_episode_in_ordinary_search()
        # — has both halves present and working when it is wired up.
        episode_id = self.seed()
        self.assertTrue(self.m.is_episode_in_ordinary_search(episode_id, self.root))
        self.assertFalse(self.m.is_episode_in_ordinary_search("governor-268-999", self.root))


if __name__ == "__main__":
    unittest.main()
