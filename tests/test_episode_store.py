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
STORE_TEMPLATE = ROOT / "episodes"  # the REAL tracked store — read from, never written to
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


def episode_path(root, episode_id, retired=False):
    """The on-disk path of an episode under the layout ratified at g4: `active/` for the
    ordinary-search set, `retired/` for the archive.

    Tests name the directories literally on purpose — the shipped primitives may not
    (close criterion C2 forbids any literal `active/`/`retired/` outside the seam block),
    so a test that also went through the seam would be asserting the implementation
    against itself. Here the literal IS the assertion."""
    return Path(root) / ("retired" if retired else "active") / f"{episode_id}.md"


def read_exact(path):
    """Read a store file with newline translation disabled, as the store itself does.
    Not Path.read_text(newline=...) — that kwarg is Python 3.13+ and CI pins 3.12."""
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return handle.read()


_CLASSIFIER = None


def classifier():
    """The store's own episode classifier (`episode_id_for`), loaded once.

    Tests ask the SHIPPED classifier "is this file an episode?" rather than answering it
    themselves. The g4 review found the opposite in this file — two helpers each carrying
    an inline comparison of `p.name` against the literal README filename — and that
    hand-filtering is exactly why no test
    could see that the shipped store's own placeholders were being minted into a phantom
    episode id. A test that re-implements the predicate under test is testing itself."""
    global _CLASSIFIER
    if _CLASSIFIER is None:
        _CLASSIFIER = load()
    return _CLASSIFIER


def episode_files(root):
    """Every episode file in the store, by name, across BOTH directories. Replaces the
    pre-g4 `root.glob("*.md")` idiom, which under the ratified layout would silently
    match nothing — trap 1, in the tests' own vocabulary. Non-episode files are excluded
    by the store's classifier, never by a name this helper knows."""
    root = Path(root)
    if not root.exists():
        return []
    return sorted(
        p.name for p in root.rglob("*.md") if classifier().episode_id_for(p) is not None
    )


def copy_store_scaffolding(dest):
    """Reproduce the REAL tracked store's non-episode files inside a throwaway store
    root, and return how many were copied.

    Read from `episodes/` rather than hand-written here, so a test store carries whatever
    scaffolding the repository actually ships — if someone adds, renames or removes a
    placeholder, the tests inherit it instead of drifting away from it. Real episode files
    (there are none today) are skipped so the temp store still starts empty. Copy only:
    the real store is never written to by any test."""
    dest = Path(dest)
    copied = 0
    for src in sorted(STORE_TEMPLATE.rglob("*")):
        if not src.is_file() or classifier().episode_id_for(src) is not None:
            continue
        target = dest / src.relative_to(STORE_TEMPLATE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        copied += 1
    classifier().ensure_store_layout(dest)
    return copied


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
        # A temp store starts with the LAYOUT, exactly as the tracked store ships it: two
        # directories and no episodes. Read seams refuse a store whose layout is absent
        # (trap 5), so a test store that skipped this would be exercising a state the
        # real store cannot be in. AbsentStoreTests covers the absent case deliberately.
        self.m.ensure_store_layout(self.root)

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
        self.assertEqual(episode_files(self.root), ["governor-268-001.md"])

        path = episode_path(self.root, "governor-268-001")
        text = path.open(encoding="utf-8", newline="").read()

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
        text = episode_path(self.root, "governor-268-001").open(encoding="utf-8", newline="").read()

        self.assertIn("- artifact-ref: docs/EPISODE_STORE.md\n", text)
        self.assertIn("- artifact-ref: scripts/apply_episode_delta.py\n", text)
        self.assertNotIn("- artifact-ref: docs/EPISODE_STORE.md ", text)

        # The invariant the defect broke.
        self.assertEqual(self.m.render_episode(self.m.parse_episode(text)), text)

    def test_second_create_same_run_increments_sequence(self):
        self.run_delta({"work_id": "issue-1", "ops": [create_op()]})
        self.run_delta({"work_id": "issue-2", "ops": [create_op()]})
        self.assertEqual(
            episode_files(self.root), ["governor-268-001.md", "governor-268-002.md"]
        )

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
        self.assertEqual(episode_files(self.root), [])

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
        self.assertEqual(episode_files(self.root), [])

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
        self.assertEqual(episode_files(self.root), [])

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
        path = episode_path(self.root, "governor-268-001")
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
        self.assertEqual(episode_files(self.root), ["governor-268-001.md"])

    def test_atomic_structurally_invalid_op_in_multi_op_delta_also_leaves_files_unchanged(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        path = episode_path(self.root, "governor-268-001")
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

        # Fail exactly the SECOND write commit() performs, simulating a real OS-level
        # failure -- disk full, permission denied, a locked file -- partway through a
        # multi-file delta.
        #
        # Patch the module's OWN named write seam, not Path.write_text. An earlier
        # version patched the stdlib method and claimed to work "either way"; that
        # stopped being true the moment the writer moved off Path.write_text (it now
        # goes through write_text_exact, because Path.write_text(newline=...) is Python
        # 3.13+ and CI pins 3.12). The patch then never fired, no failure was injected,
        # and the test asserted an exit code that could not happen -- it went red for a
        # reason unrelated to what it was testing. Patching the seam the writer actually
        # calls makes this test track the implementation instead of a stdlib detail.
        original_write = self.m.write_text_exact
        calls = {"n": 0}

        def flaky_write(path, text):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("simulated write failure (e.g. disk full) on the second touched file")
            return original_write(path, text)

        self.m.write_text_exact = flaky_write
        try:
            rc = self.m.main(["--delta", str(delta_path), "--store-root", str(self.root)])
        finally:
            self.m.write_text_exact = original_write

        self.assertEqual(rc, 1, "a mid-write I/O failure must still exit non-zero")
        self.assertGreaterEqual(calls["n"], 2, "the test did not actually reach a second write")

        after = self._snapshot()
        self.assertEqual(
            before, after,
            "store mutated (or a stray file left behind) despite a write-phase "
            "failure on the second of two touched files",
        )


class RetirementSeamTests(EpisodeStoreTestCase):
    """C8 — the retire op's CONTENT effect routes only through apply_retirement() and its
    LAYOUT effect only through destination_for(); the field diff matches
    EPISODE_STORE.md section 7's worked example, and no assertion's own
    lifecycle-standing is touched."""

    def test_retire_field_diff_matches_worked_example(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        # The content effect is asserted at the RATIFIED destination: under the bound
        # layout the retired record only ever exists in the archive.
        path = episode_path(self.root, "governor-268-001", retired=True)

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

        text = path.open(encoding="utf-8", newline="").read()
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

        self.assertTrue(path.exists())

    def test_retire_moves_the_file_from_active_into_retired(self):
        # The ratified layout effect (was: a test that flipped an adapter switch to
        # prove the seam was swappable; the decision is bound, so there is no switch and
        # nothing to flip — this asserts the bound behavior directly).
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        active = episode_path(self.root, "governor-268-001")
        self.assertTrue(active.exists())

        self.run_delta(
            {
                "work_id": "i1",
                "ops": [{"op": "retire", "id": "governor-268-001", "reason": "superseded"}],
            }
        )
        retired = episode_path(self.root, "governor-268-001", retired=True)
        self.assertTrue(retired.exists(), "retirement did not move the file into the archive")
        self.assertFalse(active.exists(), "the old active/ path should be gone after the move")
        self.assertIn("- status: retired", retired.open(encoding="utf-8", newline="").read())
        # Retained in history, never deleted or truncated: the whole record survives.
        self.assertEqual(len(self.m.parse_episode(read_exact(retired)).agent_supplied), 5)


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
        path = episode_path(self.root, "governor-268-001")
        before_text = path.open(encoding="utf-8", newline="").read()
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

        after_text = path.open(encoding="utf-8", newline="").read()
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
        # amending an already-retired episode breaks now that Option A is bound (the file
        # lives under retired/, not the flat root).
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        self.run_delta(
            {"work_id": "i1", "ops": [{"op": "retire", "id": "governor-268-001", "reason": "superseded"}]}
        )
        # file now lives in the archive, not the ordinary-search set
        self.assertFalse(episode_path(self.root, "governor-268-001").exists())
        self.assertTrue(episode_path(self.root, "governor-268-001", retired=True).exists())

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
        text = read_exact(episode_path(self.root, "governor-268-001", retired=True))
        self.assertIn("- lifecycle-standing: superseded", text)
        # ...and amending an archived episode does not resurrect it into ordinary search.
        self.assertFalse(episode_path(self.root, "governor-268-001").exists())


class RestateAssertionTests(EpisodeStoreTestCase):
    """The `restate-assertion` op (issue #460): rewrite exactly ONE assertion's statement
    and append ONE history line carrying the ORIGINAL statement verbatim.

    Why the op exists at all, since these tests are the only place it is pinned down:
    amend-assertion accepts no `statement` and changes only lifecycle-standing, so an
    assertion written as an instruction and then marked `superseded` still STANDS as the
    live statement — an agent opening the record still finds an instruction. Restating it
    is the only way to make the record read as an observation, and EPISODE_STORE.md
    section 5 ("the record grows rather than getting rewritten") is satisfied by keeping
    the original wording verbatim in the assertion's own history."""

    # A prescriptive statement of exactly the shape issue #460 is rewriting, and the
    # observation it becomes.
    PRESCRIPTIVE = "Always pass --store-root episodes when invoking the writer."
    OBSERVATION = "The run passed --store-root episodes on every writer invocation."
    REASON = "restated as an observation (issue #460, gate g2)"

    def _seed(self, run="governor-268", workaround=None):
        """One episode whose `workaround` assertion (a5) carries a prescriptive
        statement. a5 is the real target: `workaround` is the bin issue #460 rewrites."""
        op = create_op(run=run)
        op["agent_supplied"]["workaround"]["statement"] = workaround or self.PRESCRIPTIVE
        self.run_delta({"work_id": "seed", "ops": [op]})
        return episode_path(self.root, f"{run}-001")

    def _restate_op(self, episode_id="governor-268-001", assertion="a5", **overrides):
        op = {
            "op": "restate-assertion",
            "id": episode_id,
            "assertion": assertion,
            "statement": self.OBSERVATION,
            "history": self.REASON,
        }
        op.update(overrides)
        return op

    def _snapshot(self):
        """Every file under the store root as raw bytes, keyed by path -- content AND the
        exact set of files present, so a stray write anywhere in the store is caught, not
        just a change to the file under test."""
        return {p: p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}

    def _history_lines(self, text, aid):
        return [
            line
            for line in _assertion_block(text, aid).splitlines()
            if line.startswith("- history: ")
        ]

    # --- (a) --------------------------------------------------------------------------

    def test_restate_changes_only_the_named_assertions_statement(self):
        path = self._seed()
        before = read_exact(path)

        self.run_delta({"work_id": "i1", "ops": [self._restate_op()]})
        after = read_exact(path)

        # Every SIBLING assertion is byte-identical.
        for aid in ("a1", "a2", "a3", "a4"):
            self.assertEqual(
                _assertion_block(before, aid),
                _assertion_block(after, aid),
                f"sibling assertion {aid} changed under a restatement of a5",
            )

        # The ## Mechanical bin is byte-identical.
        self.assertEqual(
            before[before.index("## Mechanical") : before.index("## Agent-supplied")],
            after[after.index("## Mechanical") : after.index("## Agent-supplied")],
        )
        # The ## Retirement block (to end of file) is byte-identical.
        self.assertEqual(
            before[before.index("## Retirement") :], after[after.index("## Retirement") :]
        )

        # Within the target itself: kind, strength and lifecycle-standing are untouched.
        a5_before, a5_after = _assertion_block(before, "a5"), _assertion_block(after, "a5")
        self.assertIn("- kind: workaround", a5_after)
        self.assertIn("- strength: strong", a5_after)
        self.assertIn("- lifecycle-standing: active", a5_after)

        # The statement is replaced -- the prescriptive sentence no longer STANDS as the
        # statement, which is the whole point the amend-assertion route could not deliver.
        self.assertIn(f"- statement: {self.OBSERVATION}", a5_after)
        self.assertNotIn(f"- statement: {self.PRESCRIPTIVE}", a5_after)

        # Exactly ONE history line is appended, where there were none.
        self.assertEqual(self._history_lines(before, "a5"), [])
        self.assertEqual(len(self._history_lines(after, "a5")), 1)

        # And the record still parses and still carries all five agent-supplied kinds.
        self.assertEqual(len(self.m.parse_episode(after).agent_supplied), 5)

    def test_restate_targets_a_diagnosis_assertion_too(self):
        # The op's `assertion` field accepts a<n> or d<n>; the diagnosis bin is reachable
        # through the same all_assertions() map amend-assertion uses.
        op = create_op()
        op["diagnosis"] = [
            {"kind": "proposed-remedy", "strength": "medium", "statement": self.PRESCRIPTIVE}
        ]
        self.run_delta({"work_id": "seed", "ops": [op]})
        path = episode_path(self.root, "governor-268-001")

        self.run_delta({"work_id": "i1", "ops": [self._restate_op(assertion="d1")]})
        d1 = _assertion_block(read_exact(path), "d1")
        self.assertIn(f"- statement: {self.OBSERVATION}", d1)
        self.assertIn(self.PRESCRIPTIVE, self._history_lines(read_exact(path), "d1")[0])

    # --- (b) --------------------------------------------------------------------------

    def test_the_appended_history_line_carries_the_original_statement_verbatim(self):
        path = self._seed()
        self.run_delta({"work_id": "i1", "ops": [self._restate_op()]})

        line = self._history_lines(read_exact(path), "a5")[0]
        self.assertIn(self.PRESCRIPTIVE, line)  # verbatim, character for character
        self.assertIn(self.REASON, line)  # the caller's value supplies only the reason

    def test_the_history_line_quotes_the_record_not_the_caller(self):
        """The protected property, stated as an experiment rather than an assertion about
        the format: run the SAME op text -- same statement, same history value -- against
        two records whose originals differ, and the two history lines must differ exactly
        by the original. A line assembled from anything the caller supplied would come out
        identical, so this fails against any implementation that lets the caller author or
        influence the quoted text."""
        first = self._seed(run="governor-268", workaround=self.PRESCRIPTIVE)
        other_original = "Re-run the sweep by hand until the flake stops."
        second = self._seed(run="governor-269", workaround=other_original)

        self.run_delta(
            {
                "work_id": "i1",
                "ops": [
                    self._restate_op(episode_id="governor-268-001"),
                    self._restate_op(episode_id="governor-269-001"),
                ],
            }
        )

        line_one = self._history_lines(read_exact(first), "a5")[0]
        line_two = self._history_lines(read_exact(second), "a5")[0]
        self.assertNotEqual(line_one, line_two)
        self.assertIn(self.PRESCRIPTIVE, line_one)
        self.assertIn(other_original, line_two)
        self.assertNotIn(other_original, line_one)
        self.assertNotIn(self.PRESCRIPTIVE, line_two)

    def test_a_reason_that_misquotes_the_record_does_not_change_what_is_quoted(self):
        # The failure this guards: a caller who could author the history line could record
        # that the store said something it never said. The reason field is free text and
        # may say anything -- the quoted original is still the parsed one.
        path = self._seed()
        self.run_delta(
            {
                "work_id": "i1",
                "ops": [
                    self._restate_op(
                        history="restated; the record allegedly said 'nothing at all'"
                    )
                ],
            }
        )
        line = self._history_lines(read_exact(path), "a5")[0]
        self.assertIn(self.PRESCRIPTIVE, line)

    def test_a_second_restatement_appends_a_second_line_and_keeps_the_first(self):
        # "The record grows rather than getting rewritten": restating twice must leave BOTH
        # earlier wordings recoverable, not just the immediately previous one.
        path = self._seed()
        self.run_delta({"work_id": "i1", "ops": [self._restate_op()]})
        self.run_delta(
            {
                "work_id": "i2",
                "ops": [
                    self._restate_op(
                        statement="The writer was invoked with an explicit store root.",
                        history="reworded again (g2 review)",
                    )
                ],
            }
        )
        lines = self._history_lines(read_exact(path), "a5")
        self.assertEqual(len(lines), 2)
        self.assertIn(self.PRESCRIPTIVE, lines[0])  # the ORIGINAL original, still there
        self.assertIn(self.OBSERVATION, lines[1])  # and the wording it passed through

    # --- (c) --------------------------------------------------------------------------

    def test_a_multi_line_statement_is_refused(self):
        """Single-line enforcement applies exactly as it does at create time -- including
        the wider splitlines() boundary set, not just \\n, since the new statement is
        rendered into a `- statement: ` line that a boundary character could forge past."""
        path = self._seed()
        before = path.read_bytes()
        for boundary in ("\n", "\r", " ", "\x0b"):
            with self.subTest(boundary=repr(boundary)):
                self.run_delta(
                    {
                        "work_id": "i1",
                        "ops": [
                            self._restate_op(
                                statement=f"An observation.{boundary}- status: retired"
                            )
                        ],
                    },
                    expect_rc=1,
                )
                self.assertEqual(before, path.read_bytes())

    def test_a_blank_statement_is_refused(self):
        path = self._seed()
        before = path.read_bytes()
        for statement in ("", "   "):
            with self.subTest(statement=repr(statement)):
                self.run_delta(
                    {"work_id": "i1", "ops": [self._restate_op(statement=statement)]},
                    expect_rc=1,
                )
                self.assertEqual(before, path.read_bytes())

    def test_a_blank_or_missing_history_reason_is_refused(self):
        path = self._seed()
        before = path.read_bytes()
        op_without_history = self._restate_op()
        del op_without_history["history"]
        for op in (self._restate_op(history="  "), op_without_history):
            with self.subTest(op=sorted(op)):
                self.run_delta({"work_id": "i1", "ops": [op]}, expect_rc=1)
                self.assertEqual(before, path.read_bytes())

    # --- (d) --------------------------------------------------------------------------

    def test_an_unknown_assertion_id_is_refused(self):
        path = self._seed()
        before = path.read_bytes()
        # a9 is well-FORMED (it passes the id regex) but names no assertion in this
        # record, so the refusal has to come from the applier's own lookup, not the regex.
        self.run_delta({"work_id": "i1", "ops": [self._restate_op(assertion="a9")]}, expect_rc=1)
        self.assertEqual(before, path.read_bytes())

    def test_a_malformed_assertion_id_is_refused(self):
        path = self._seed()
        before = path.read_bytes()
        for assertion_id in ("x1", "a", "5", "a1.1", ""):
            with self.subTest(assertion=assertion_id):
                self.run_delta(
                    {"work_id": "i1", "ops": [self._restate_op(assertion=assertion_id)]},
                    expect_rc=1,
                )
                self.assertEqual(before, path.read_bytes())

    def test_an_unknown_episode_id_is_refused(self):
        path = self._seed()
        before = self._snapshot()
        self.run_delta(
            {"work_id": "i1", "ops": [self._restate_op(episode_id="governor-268-999")]},
            expect_rc=1,
        )
        self.assertEqual(before, self._snapshot())
        self.assertTrue(path.exists())

    # --- (e) --------------------------------------------------------------------------

    def test_a_two_op_delta_with_an_invalid_second_op_leaves_the_first_ops_file_unchanged(self):
        first = self._seed(run="governor-268")
        second = self._seed(run="governor-269")
        before = self._snapshot()

        # op1 is individually valid and would, on its own, have rewritten governor-268-001.
        # op2 fails only once apply_delta REACHES it (the episode does not exist), so this
        # proves the write plan defers every filesystem write until every op has succeeded
        # -- not merely that structural validation runs before any of them.
        self.run_delta(
            {
                "work_id": "i1",
                "ops": [
                    self._restate_op(episode_id="governor-268-001"),
                    self._restate_op(episode_id="governor-268-404"),
                ],
            },
            expect_rc=1,
        )

        self.assertEqual(before, self._snapshot(), "the first op's write landed anyway")
        self.assertIn(f"- statement: {self.PRESCRIPTIVE}", read_exact(first))
        self.assertEqual(self._history_lines(read_exact(first), "a5"), [])
        self.assertEqual(self._history_lines(read_exact(second), "a5"), [])

    def test_the_two_op_atomicity_exercise_is_not_vacuous(self):
        # The same two-op delta with a VALID second op does mutate both files -- so the
        # test above is watching a write that would really have happened, not an op that
        # was never going to write in the first place.
        first = self._seed(run="governor-268")
        second = self._seed(run="governor-269")
        self.run_delta(
            {
                "work_id": "i1",
                "ops": [
                    self._restate_op(episode_id="governor-268-001"),
                    self._restate_op(episode_id="governor-269-001"),
                ],
            }
        )
        for path in (first, second):
            self.assertIn(f"- statement: {self.OBSERVATION}", read_exact(path))
            self.assertEqual(len(self._history_lines(read_exact(path), "a5")), 1)

    # --- (g) --------------------------------------------------------------------------

    def test_a_misfiled_extra_field_on_the_op_is_refused(self):
        """The op takes EXACTLY id, assertion, statement and history. The dangerous inputs
        are the plausible ones -- a caller who assumes a restatement also carries epistemic
        status, or who files amend-assertion's or retire's own fields here."""
        path = self._seed()
        before = path.read_bytes()
        for field_name, value in (
            ("lifecycle-standing", "superseded"),  # amend-assertion's field
            ("strength", "weak"),
            ("kind", "workaround"),
            ("reason", "because"),  # retire's field
            ("retired-at", "2026-08-07"),
            ("statment", "typo'd key, so the real one is missing too"),
        ):
            with self.subTest(field=field_name):
                self.run_delta(
                    {"work_id": "i1", "ops": [self._restate_op(**{field_name: value})]},
                    expect_rc=1,
                )
                self.assertEqual(before, path.read_bytes())

    # --- (f) --------------------------------------------------------------------------

    def _main(self, delta, *extra_argv):
        """Run the writer's CLI and return (exit code, stdout). Captures stdout because
        the dry-run contract is about what the caller is TOLD, not only about what does or
        does not land on disk."""
        delta_path = Path(self.tmp.name) / "dry-run-delta.json"
        delta_path.write_text(json.dumps(delta), encoding="utf-8")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            rc = self.m.main(
                ["--delta", str(delta_path), "--store-root", str(self.root), *extra_argv]
            )
        return rc, buffer.getvalue()

    def test_a_restate_under_dry_run_logs_the_op_and_writes_nothing(self):
        """The defect this exists to prevent: apply_delta() and _dry_run_log() dispatch on
        op kind through SEPARATE if/elif chains. Registering the op in only the first left
        --dry-run silently skipping it -- no log line, no error, exit 0, and a cheerful
        "DRY RUN — no write". A caller would read that as "your op is fine" when the op had
        never been looked at, in the store's only write path."""
        self._seed()
        before = self._snapshot()

        rc, out = self._main({"work_id": "i1", "ops": [self._restate_op()]}, "--dry-run")

        self.assertEqual(rc, 0)
        self.assertIn("restated governor-268-001.a5", out)  # the op WAS dispatched
        self.assertIn("DRY RUN — no write", out)
        self.assertEqual(before, self._snapshot(), "a dry run wrote to the store")

    def test_the_dry_run_log_line_matches_the_one_a_real_apply_emits(self):
        # Otherwise a dry run could "log the op" with text no real apply would ever
        # produce, and still read as registered.
        self._seed()
        _, dry = self._main({"work_id": "i1", "ops": [self._restate_op()]}, "--dry-run")
        wet_rc, wet = self._main({"work_id": "i2", "ops": [self._restate_op()]})
        self.assertEqual(wet_rc, 0)
        dry_lines = [line for line in dry.splitlines() if line != "DRY RUN — no write"]
        self.assertEqual(dry_lines, wet.splitlines())

    def test_a_dry_run_of_an_invalid_restate_still_refuses(self):
        # A dry run answers about the store that is really there: an op a real apply would
        # refuse must be refused here too, not waved through because nothing writes.
        self._seed()
        rc, out = self._main(
            {"work_id": "i1", "ops": [self._restate_op(assertion="a9")]}, "--dry-run"
        )
        self.assertEqual(rc, 1)
        self.assertNotIn("DRY RUN", out)

    # --- both dispatch sites carry an else ---------------------------------------------

    def test_an_op_kind_in_op_kinds_but_absent_from_a_dispatch_site_fails_visibly(self):
        """The silent-skip defect itself, reproduced: admit a kind to OP_KINDS (so
        validate_delta lets it through) that neither dispatch chain has a branch for.

        Without the `else: raise`, apply_delta() returns an empty log and commits, and
        _dry_run_log() returns only "DRY RUN — no write" -- both exit 0, both silent. Each
        now raises and names the site that missed it, so the next op added to this module
        cannot repeat the defect. Both sites are asserted SEPARATELY: one else does not
        imply the other, and that asymmetry is exactly what went wrong the first time."""
        self._seed()
        delta = {"work_id": "i1", "ops": [{"op": "future-op", "id": "governor-268-001"}]}

        original_kinds = self.m.OP_KINDS
        self.m.OP_KINDS = original_kinds + ("future-op",)
        try:
            # The premise: validate_delta now ACCEPTS this kind, so the refusals below have
            # to come from the dispatch chains, not from the OP_KINDS membership check.
            self.m.validate_delta(delta)

            for site, call in (
                ("apply_delta", lambda: self.m.apply_delta(self.root, delta)),
                ("_dry_run_log", lambda: self.m._dry_run_log(self.root, delta)),
            ):
                with self.subTest(site=site):
                    with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                        call()
                    self.assertIn(site, str(caught.exception))
                    self.assertIn("future-op", str(caught.exception))
        finally:
            self.m.OP_KINDS = original_kinds

    def test_every_op_kind_is_dispatched_at_both_sites(self):
        """Define the guard by the consumer's own behaviour rather than a hand-kept list:
        drive EVERY member of the shipped OP_KINDS through both dispatch chains and assert
        none of them reaches the else. A future op added to OP_KINDS and wired into only
        one chain fails here without anyone remembering to extend this test."""
        minimal = {
            "create": create_op(run="probe-run"),
            "amend-assertion": {
                "op": "amend-assertion",
                "id": "governor-268-001",
                "assertion": "a5",
                "lifecycle-standing": "disputed",
                "history": "probe",
            },
            "restate-assertion": self._restate_op(),
            "retire": {"op": "retire", "id": "governor-268-001", "reason": "probe"},
        }
        # The list above is checked against the shipped tuple rather than trusted: an op
        # added to OP_KINDS with no entry here fails right now, instead of this loop
        # quietly probing three of four kinds.
        self.assertEqual(sorted(minimal), sorted(self.m.OP_KINDS))

        probed = 0
        for kind, op in minimal.items():
            for site, call in (
                ("apply_delta", self.m.apply_delta),
                ("_dry_run_log", self.m._dry_run_log),
            ):
                with self.subTest(kind=kind, site=site):
                    # A fresh store per probe so the ops cannot interfere with each other.
                    with tempfile.TemporaryDirectory() as tmp:
                        root = Path(tmp) / "episodes"
                        self.m.ensure_store_layout(root)
                        seed = create_op()
                        seed["agent_supplied"]["workaround"]["statement"] = self.PRESCRIPTIVE
                        self.m.apply_delta(root, {"work_id": "seed", "ops": [seed]})
                        log = call(root, {"work_id": "probe", "ops": [op]})
                    self.assertTrue(
                        [line for line in log if line != "DRY RUN — no write"],
                        f"{kind} produced no log line at {site} — it was silently skipped",
                    )
                    probed += 1
        self.assertEqual(probed, 2 * len(self.m.OP_KINDS))

    # --- the allowlist itself is the guard, so pin it -----------------------------------

    def test_the_op_field_allowlist_is_pinned_to_its_exact_membership(self):
        """g1 review, mutation M4: adding an `original` key to RESTATE_ALLOWED_FIELDS and
        having the applier prefer op["original"] over the parsed statement ran GREEN --
        21 passed, exit 0. The shipped code has no such hole, but every other test here
        checks what the op REFUSES, and none of them notices the allowlist getting wider.
        A later widening would silently reopen the one risk this op exists to close: a
        caller able to supply the "original" can make the record claim it said something
        it never said.

        So pin the membership itself. If you are here because this assertion failed, the
        question is not "update the tuple" -- it is whether the field you added can carry,
        or influence, the previous statement. If it can, it does not belong on this op."""
        self.assertEqual(
            self.m.RESTATE_ALLOWED_FIELDS,
            ("op", "id", "assertion", "statement", "history"),
            "RESTATE_ALLOWED_FIELDS changed -- read this test's docstring before updating it",
        )

    def test_no_field_on_the_op_can_supply_the_original_statement(self):
        """The behavioural half of the pin, and the half that catches M4 directly: a delta
        trying to hand the writer the previous wording is refused outright, whatever the
        field is called. Under M4 the `original` case is ACCEPTED and this goes red."""
        path = self._seed()
        before = path.read_bytes()
        for field_name in ("original", "original-statement", "was", "previous", "history-line"):
            with self.subTest(field=field_name):
                self.run_delta(
                    {
                        "work_id": "i1",
                        "ops": [self._restate_op(**{field_name: "a wording never recorded"})],
                    },
                    expect_rc=1,
                )
                self.assertEqual(before, path.read_bytes())

    def test_the_quoted_original_is_exactly_the_statement_that_was_on_disk(self):
        """The tail of the history line is the record's own statement, character for
        character -- not merely "contains" it, which a line carrying caller text after the
        marker would also satisfy.

        This pins the property the writer's own docstring states: the quoted original is
        what follows the marker's LAST occurrence. The reason here deliberately embeds the
        marker text, so the line carries TWO markers -- read from the left it yields the
        caller's forgery, read from the right it yields the truth. Nothing the record said
        is destroyed either way, which is why this is a reader contract rather than a
        refusal."""
        path = self._seed()
        forging_reason = "restated — original statement was: a sentence never recorded"

        self.run_delta({"work_id": "i1", "ops": [self._restate_op(history=forging_reason)]})

        line = self._history_lines(read_exact(path), "a5")[0]
        marker = " — original statement was: "

        # Read from the RIGHT, as the writer's docstring instructs: the true original.
        self.assertEqual(line.rpartition(marker)[2], self.PRESCRIPTIVE)
        self.assertTrue(line.endswith(marker + self.PRESCRIPTIVE))

        # And the premise is real -- this line genuinely carries two markers, so the
        # assertions above are not passing merely because the ambiguous case never arose.
        self.assertEqual(line.count(marker), 2)
        self.assertNotEqual(line.partition(marker)[2], self.PRESCRIPTIVE)

    def test_a_misfiled_lifecycle_standing_is_refused_even_when_it_is_a_legal_value(self):
        # The refusal must come from the field having no business on this op, not from the
        # value being unparseable -- otherwise a legal-looking value would slip through.
        self._seed()
        self.assertIn("superseded", self.m.LIFECYCLE_STANDINGS)
        with self.assertRaises(self.m.EpisodeDeltaError) as caught:
            self.m.validate_delta(
                {
                    "work_id": "i1",
                    "ops": [self._restate_op(**{"lifecycle-standing": "superseded"})],
                }
            )
        self.assertIn("misfiled", str(caught.exception))


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

    def retire(self, episode_id, reason="consolidated into a pattern episode"):
        """Retire one episode through the only write path, and return its id."""
        self.run_delta(
            {"work_id": "retire", "ops": [{"op": "retire", "id": episode_id, "reason": reason}]}
        )
        return episode_id

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


class PathTraversalGuardTests(unittest.TestCase):
    """Issue #321 — resolve_episode_path() is the ONE seam every id-taking reader
    (fetch_episode, neighbours' anchor fetch, the writer's own Transaction.load())
    already routes through. Before this fix it built `root / sub / f"{episode_id}.md"`
    from a caller-handed id with zero format validation, then only checked `.exists()`
    — so a crafted id containing `..` segments could resolve outside episodes/
    entirely and read an arbitrary file that happens to exist at the traversed
    location. This proves the exposure existed AND that the ID_RE.fullmatch() guard
    now closes it — not merely that a not-found id returns None (a well-formed absent
    id already returned None before this fix too, which would be a check that cannot
    fail)."""

    TRAVERSAL_TARGET = ROOT / "SKILL_INDEX.md"

    def setUp(self):
        self.m = load()
        self.q = load_query()
        # Anchored directly under the repo root (dir=str(ROOT)), NOT the system
        # tempdir the other tests' EpisodeStoreTestCase.setUp uses — so a fixed,
        # small number of ".." segments deterministically reaches
        # ROOT/SKILL_INDEX.md regardless of where the OS places its temp
        # directory. self.root is 2 levels below ROOT (ROOT/tmpXXXX/episodes), so
        # root/active is 3 levels below ROOT.
        self.tmp = tempfile.TemporaryDirectory(dir=str(ROOT))
        self.root = Path(self.tmp.name) / "episodes"
        self.m.ensure_store_layout(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it(self):
        # 0. The assumption this whole test rests on: a real, tracked file sits at
        #    the repo root. Fail loudly rather than pass vacuously if that ever stops
        #    holding.
        self.assertTrue(
            self.TRAVERSAL_TARGET.exists(),
            f"{self.TRAVERSAL_TARGET} is assumed to exist at repo root for this "
            "adversarial test to be meaningful, but it does not -- pick another "
            "real, tracked file as the traversal target and update this test.",
        )

        episode_id = "../../../SKILL_INDEX"

        # 1. Prove the exposure: joined the OLD (pre-fix) way -- root / sub /
        #    f"{episode_id}.md", with no format check first -- the crafted id
        #    resolves to that real file, outside episodes/ entirely.
        old_style_path = self.root / "active" / f"{episode_id}.md"
        self.assertEqual(old_style_path.resolve(), self.TRAVERSAL_TARGET.resolve())
        self.assertTrue(old_style_path.exists())

        # 2. Prove the fix: the real, current resolve_episode_path() refuses the
        #    same id, for the same root, before returning any path for it. (Pre-fix,
        #    this line does not merely return the wrong Path -- because active/ and
        #    retired/ are same-depth sibling directories, a pure ".."-escape is
        #    symmetric across both branches and instead trips the half-retired
        #    guard, raising EpisodeDeltaError with the escaped path in its message.
        #    That is a second, independent symptom of the identical root cause --
        #    zero input validation -- and the guard below closes both at once.)
        self.assertIsNone(self.m.resolve_episode_path(episode_id, self.root))

        # 3. ...and the seam's caller-facing surface (fetch_episode) refuses it too.
        self.assertIsNone(self.q.fetch_episode(episode_id, self.root))


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
    for path in sorted((Path(root) / "active").glob("*.md")):
        text = path.open(encoding="utf-8", newline="").read()
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
    for path in sorted((Path(root) / "active").glob("*.md")):
        if f"- {field}: {value}" in path.open(encoding="utf-8", newline="").read():
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
        naive = sorted(p.stem for p in (self.root / "active").glob("governor-268-*.md"))
        ours = self.q.enumerate_episode_ids(self.root)
        self.assertEqual(naive, sorted(governor))
        self.assertEqual(ours, sorted(governor + admiral))
        self.assertTrue(set(naive) < set(ours))

    def test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped(self):
        """A third shape, found by sweeping for the class rather than by a review note.

        enumerate_episodes() turned the scan's ids into records with an `if ep is not
        None` filter on the end — so an id the scan returned and fetch could not resolve
        left the candidate set between two lines of one function, silently. It means the
        store changed underneath the query, or the enumeration and resolution seams
        disagree; both are facts, neither is "no match"."""
        live = self.seed()
        vanishing = self.seed(run="admiral-298")
        real_fetch = self.q.fetch_episode
        self.q.fetch_episode = lambda eid, root: (
            None if eid == vanishing else real_fetch(eid, root)
        )
        try:
            with self.assertRaises(self.q.QueryError) as caught:
                self.q.enumerate_episodes(self.root)
            self.assertIn(vanishing, str(caught.exception))
            # ...and the ids-only scan, which does not fetch, still answers.
            self.assertEqual(
                self.q.enumerate_episode_ids(self.root), sorted([live, vanishing])
            )
        finally:
            self.q.fetch_episode = real_fetch


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
        # A real, well-formed, EMPTY store — not a missing one. "The other store cannot
        # answer" has to come from the store being empty, not from it being absent, which
        # is now its own refusal (AbsentStoreTests).
        self.m.ensure_store_layout(empty_root)
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
        # Seed the origin with the store's REAL scaffolding — its README and the tracked
        # placeholders that keep active/ and retired/ alive in git — rather than a
        # hand-written stand-in. Section 9's whole claim is about the tracked store
        # crossing a worktree boundary, so the thing crossing it should be the shape the
        # repository actually commits.
        copy_store_scaffolding(self.origin / "episodes")
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
        self.assertFalse(episode_path(reader_wt / "episodes", episode_id).exists())
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
        writer_blob = self.git("rev-parse", f"HEAD:episodes/active/{episode_id}.md", cwd=writer_wt).strip()
        reader_blob = self.git("rev-parse", f"HEAD:episodes/active/{episode_id}.md", cwd=reader_wt).strip()
        self.assertEqual(writer_blob, reader_blob)
        # (c) Raw WORKING-TREE bytes may legitimately differ, but only in line endings
        #     — see test_working_tree_bytes_are_not_the_cross_worktree_identity below,
        #     which is where that hazard is pinned down.
        writer_bytes = episode_path(writer_wt / "episodes", episode_id).read_bytes()
        reader_bytes = episode_path(reader_wt / "episodes", episode_id).read_bytes()
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

        writer_bytes = episode_path(writer_wt / "episodes", episode_id).read_bytes()
        reader_bytes = episode_path(reader_wt / "episodes", episode_id).read_bytes()

        # The writer's own output is always LF-only, on every platform.
        self.assertNotIn(b"\r\n", writer_bytes)

        # Whatever the checkout did, these two things always hold:
        #   the records are equal, and the bytes differ by line endings at most.
        self.assertEqual(
            writer_bytes.replace(b"\r\n", b"\n"), reader_bytes.replace(b"\r\n", b"\n")
        )
        # And git's stored (index) content is LF either way — the stable identity.
        eol_info = self.git("ls-files", "--eol", f"episodes/active/{episode_id}.md", cwd=reader_wt)
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
        self.assertTrue(episode_path(writer_wt / "episodes", seed["episode_id"]).exists())
        self.assertFalse(episode_path(reader_wt / "episodes", seed["episode_id"]).exists())
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
        path = episode_path(self.root, episode_id)

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
        path = episode_path(self.root, episode_id)
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


class RatifiedLayoutTests(EpisodeStoreTestCase):
    """g4 — the retirement layout is RATIFIED and BOUND. Tommy's ruling, verbatim:

        "move the file, prefer to keep files clean of history unless they're
        historical. archives are available strats."

    So retirement MOVES the file: episodes/active/<id>.md -> episodes/retired/<id>.md
    (EPISODE_STORE.md section 7, Option A). Option B — a `status` field filtered
    negatively, with the file never moving — is rejected, and its adapters are gone.
    These tests assert the BOUND behavior directly, with no adapter switch to flip,
    because there is no longer a switch: a second adapter would re-open a decision the
    human has closed."""

    def test_a_new_episode_is_written_under_active(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        self.assertTrue((self.root / "active" / "governor-268-001.md").exists())
        # ...and NOT at the old flat path.
        self.assertFalse((self.root / "governor-268-001.md").exists())

    def test_retiring_moves_the_file_into_retired(self):
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        self.run_delta(
            {
                "work_id": "i1",
                "ops": [{"op": "retire", "id": "governor-268-001", "reason": "superseded"}],
            }
        )
        self.assertTrue((self.root / "retired" / "governor-268-001.md").exists())
        self.assertFalse((self.root / "active" / "governor-268-001.md").exists())

    def test_the_layout_adapter_switch_is_gone(self):
        # Removing the Option-B scaffolding is half of what this gate binds. A lingering
        # switch would mean the store still behaves as if the decision were open.
        for scaffolding in ("_LAYOUT_ADAPTER", "_LAYOUT_OPTION_A", "_LAYOUT_OPTION_B"):
            self.assertFalse(
                hasattr(self.m, scaffolding),
                f"{scaffolding} still present — the held-decision scaffolding must come out",
            )

    def test_membership_is_a_directory_fact_not_a_parsed_field(self):
        # The structural property the ruling buys: "which set is this episode in" is
        # answered by the filesystem, so a malformed, hand-edited or forged `status`
        # line cannot change it.
        self.run_delta({"work_id": "i0", "ops": [create_op()]})
        self.assertTrue(self.m.is_episode_in_ordinary_search("governor-268-001", self.root))
        self.run_delta(
            {
                "work_id": "i1",
                "ops": [{"op": "retire", "id": "governor-268-001", "reason": "superseded"}],
            }
        )
        self.assertFalse(self.m.is_episode_in_ordinary_search("governor-268-001", self.root))


class RetirementDependentRetrievalTests(QueryTestCase):
    """C3 — a retired episode is ABSENT from ordinary retrieval and PRESENT in
    history-inclusive retrieval. Both directions, because either one alone is satisfiable
    by a broken store: absence alone is also what deletion looks like, and presence alone
    is also what "retirement did nothing" looks like. Together they are the operational
    meaning of "excluded from ordinary rhyme-search, RETAINED in history"."""

    def test_a_retired_episode_leaves_ordinary_retrieval_and_stays_in_history(self):
        kept = self.seed()
        gone = self.retire(self.seed())

        # Direction 1 — ABSENT from ordinary retrieval.
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [kept])
        # Direction 2 — PRESENT in history-inclusive retrieval.
        self.assertEqual(
            self.q.enumerate_episode_ids(self.root, include_retired=True), sorted([kept, gone])
        )

    def test_the_archive_is_opt_in_not_opt_out(self):
        """The ruling's second half: retired/ is an archive, not a second live search
        space every query has to remember to exclude. So the DEFAULT — what a caller gets
        for asking nothing — is the ordinary set, and reaching the archive is a
        deliberate act. A default that included the archive would make every future
        caller's omission of a filter a silent correctness bug."""
        self.retire(self.seed())
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [])
        self.assertEqual(self.q.enumerate_episodes(self.root), [])

    def test_retirement_is_a_move_not_a_deletion(self):
        gone = self.retire(self.seed())
        archived = self.q.fetch_episode(gone, self.root)
        self.assertIsNotNone(archived, "retirement deleted the record")
        self.assertEqual(len(archived.agent_supplied), 5)
        self.assertEqual(archived.status, "retired")
        self.assertEqual(archived.retired_reason, "consolidated into a pattern episode")

    def test_fetch_by_id_reaches_the_archive_because_it_is_a_lookup_not_a_search(self):
        # Retirement excludes an episode from SEARCH. An addressed lookup by name is not
        # a search, and a cross-reference (consolidated-into:, superseded-by:) would
        # dangle if it were.
        gone = self.retire(self.seed())
        self.assertIsNotNone(self.q.fetch_episode(gone, self.root))
        self.assertEqual(self.run_query("fetch", gone)["ids"], [gone])

    def test_select_and_neighbours_respect_retirement_in_both_directions(self):
        kept = self.seed(**{"artifact-ref": ["shared.md"]})
        gone = self.retire(self.seed(**{"artifact-ref": ["shared.md"]}))

        self.assertEqual(self.q.select_episode_ids(self.root, "artifact-ref", ["shared.md"]), [kept])
        self.assertEqual(
            self.q.select_episode_ids(
                self.root, "artifact-ref", ["shared.md"], include_retired=True
            ),
            sorted([kept, gone]),
        )
        self.assertEqual(self.q.neighbour_ids(self.root, kept), [])
        self.assertEqual(self.q.neighbour_ids(self.root, kept, include_retired=True), [gone])

    def test_the_cli_states_which_universe_it_answered_from(self):
        kept = self.seed()
        gone = self.retire(self.seed())

        ordinary = self.run_query("enumerate")
        self.assertEqual(ordinary["ids"], [kept])
        self.assertIs(ordinary["include_retired"], False)

        historical = self.run_query("enumerate", "--include-retired")
        self.assertEqual(historical["ids"], sorted([kept, gone]))
        self.assertIs(historical["include_retired"], True)
        # An envelope that did not say would let a caller mistake an archive-excluding
        # answer for a complete one — a silent omission at the consumer's end.

    def test_retiring_the_only_episode_of_a_run_does_not_free_its_sequence_number(self):
        # The id-assignment scan is history-inclusive on purpose (section 2): a retired
        # episode's number is still taken, or a new episode would collide with an
        # archived one and two records would share an id.
        gone = self.retire(self.seed())
        self.assertEqual(gone, "governor-268-001")
        fresh = self.seed()
        self.assertEqual(fresh, "governor-268-002")


# --- the three RELOCATED silent-omission traps, one naive implementation each ---------
#
# Binding Option A made the ORIGINAL trap structurally impossible. Under Option B,
# "ordinary search" was a positive allowlist over a parsed field — enumerate the files
# whose `status` reads `active` — and that silently dropped an episode in any OTHER
# legitimate lifecycle state (a `disputed` core assertion on a perfectly un-retired
# episode). Membership is now a directory fact, so there is no field to enumerate and no
# allowlist to be wrong about.
#
# The CLASS did not go away with it. It moved. These three naive implementations are each
# a reasonable way to write the new code, and each is silently short.


def naive_flat_glob_enumeration(root):
    """Trap 1 — a glob that misses a subdirectory.

    This is the pre-g4 enumeration, unchanged: scan `episodes/*.md`. It was correct under
    the flat layout and is now silently, totally wrong — every episode lives one level
    down, so this returns NOTHING (or, worse, only strays) and reports no error at all.
    An empty candidate set is indistinguishable from "the store is empty", which is why
    this failure mode ships instead of getting caught.

    The naivety being modelled is the FLAT GLOB and nothing else, so non-episode files
    are excluded through the store's real classifier rather than by a filename this
    fixture knows — an inline comparison against the literal README filename here would
    quietly make the fixture immune to the very defect it is supposed to model."""
    return sorted(
        eid
        for eid in (classifier().episode_id_for(p) for p in Path(root).glob("*.md"))
        if eid is not None
    )


def naive_history_inclusive_forgetting_the_union(root):
    """Trap 2 — a history-inclusive enumeration that forgets to union both directories.

    The tempting shape: "history-inclusive means I also want the archive", written as a
    scan of the archive alone, or (as here) a scan that reaches for the ordinary set and
    never adds the archive to it. The caller explicitly ASKED for history and gets half
    of it back, silently. This one is nastier than trap 1 because the answer is
    non-empty and looks plausible."""
    return sorted(p.stem for p in (Path(root) / "active").glob("*.md"))


def naive_layout_listing_as_ids(root):
    """Trap 4 — a directory listing read as a list of episode ids.

    The shipped defect, in one expression: `{p.stem for p in (root/"active").glob("*.md")}`.
    Correct exactly while a layout directory holds nothing but episodes, and silently
    wrong the moment it holds anything else — which it always does, because git needs a
    tracked file in a directory to keep the directory at all. Every non-episode file then
    becomes a phantom id that no record backs, and (when the same name appears in both
    directories) trips the half-retirement guard on a store that was never retired."""
    return sorted(
        {p.stem for p in (Path(root) / "active").glob("*.md")}
        | {p.stem for p in (Path(root) / "retired").glob("*.md")}
    )


def naive_status_grep_membership(root):
    """The ORIGINAL trap, kept and adapted: ordinary search as a content-parsing
    operation over the `status` field, the way the REJECTED Option-B adapter would have
    had to do it. Unanchored, because that is how it gets written — and any episode whose
    free text merely QUOTES a status line is then silently excluded from ordinary search
    while being entirely active.

    EPISODE_STORE.md §7 named this exposure as the reason Option B needed a line-anchored
    filter. Option A needs no filter at all, so the exposure is gone rather than
    mitigated. This function exists to demonstrate that difference, not to be used."""
    kept = []
    for path in sorted((Path(root) / "active").glob("*.md")):
        if "- status: retired" not in read_exact(path):
            kept.append(path.stem)
    return sorted(kept)


class HalfRetirementSafetyTests(QueryTestCase):
    """C6 — the store is never left HALF-RETIRED.

    A retirement has two halves: the field update (`status`, `retired-reason`, …) and the
    file's move into the archive. A store where one landed and the other did not is
    corrupt in a specific, nasty way — it reads as retired while still being in the
    ordinary-search candidate set, or vice versa — and nothing about it is loud.

    Two independent defenses, proven separately below:

      1. **By construction.** The updated content is only ever rendered to the NEW path.
         "Fields updated but file not moved" has no representation in the write plan at
         all, and neither does its mirror image: there is one plan entry and it carries
         both halves. This is asserted directly against write_plan(), not inferred.
      2. **By compensation.** Binding the layout gave the placement phase a second step
         (place the archived file, remove the source), so a failure BETWEEN them would
         leave the id in both directories. Faults are injected at each step and the store
         is asserted consistent afterwards.
    """

    def _sets(self):
        """(ordinary-set ids, archive ids) read straight off the filesystem, without
        going through the code under test — otherwise a bug in the seams could hide
        itself from the very assertion meant to catch it."""
        return (
            sorted(p.stem for p in (self.root / "active").glob("*.md")),
            sorted(p.stem for p in (self.root / "retired").glob("*.md")),
        )

    def assert_consistent(self, episode_id):
        """The invariant, stated once: an id is in EXACTLY ONE of the two sets, and the
        `status` recorded inside the file agrees with the directory holding it."""
        live, archived = self._sets()
        in_live, in_archive = episode_id in live, episode_id in archived
        self.assertNotEqual(
            in_live, in_archive,
            f"{episode_id} is in {'both' if in_live else 'neither'} set — half-retired",
        )
        record = self.q.fetch_episode(episode_id, self.root)
        self.assertIsNotNone(record)
        expected = "retired" if in_archive else "active"
        self.assertEqual(
            record.status, expected,
            f"{episode_id} sits in the {expected} set but its status field says "
            f"{record.status!r} — the directory and the record disagree",
        )
        return expected

    def test_the_write_plan_cannot_express_a_half_retirement(self):
        # Defense 1, asserted against the plan itself rather than its effects.
        self.seed()
        tx = self.m._Transaction(self.root)
        episode = tx.load("governor-268-001")
        self.m.apply_retirement(episode, "consolidated")
        writes, deletes = tx.write_plan()

        self.assertEqual(
            [p.name for p in writes], ["governor-268-001.md"], "expected exactly one plan entry"
        )
        (destination,) = writes
        # The retired CONTENT is only ever rendered to the archive path...
        self.assertEqual(destination.parent.name, "retired")
        self.assertIn("- status: retired", writes[destination])
        # ...and the ordinary-set path is only ever removed, never left holding it.
        self.assertEqual([p.parent.name for p in deletes], ["active"])

    def test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired(self):
        live = self.seed()
        before = read_exact(episode_path(self.root, live))

        original = self.m._place

        def failing_place(tmp_path, final_path):
            raise OSError("simulated failure placing the archived file (e.g. locked file)")

        self.m._place = failing_place
        try:
            self.run_delta(
                {"work_id": "r", "ops": [{"op": "retire", "id": live, "reason": "consolidated"}]},
                expect_rc=1,
            )
        finally:
            self.m._place = original

        self.assertEqual(self.assert_consistent(live), "active")
        self.assertEqual(read_exact(episode_path(self.root, live)), before)

    def test_a_failure_removing_the_source_rolls_the_retirement_back_whole(self):
        """The window binding Option A actually opened, and the one this gate owes.

        The archived file has already landed. If removing the source then fails, the
        naive sequence leaves the id in BOTH directories: retired by content, still in
        the ordinary-search set by directory. The placement phase compensates instead —
        it restores the prior bytes of everything it disturbed and deletes what it newly
        created, so the retirement is undone whole rather than left half-applied."""
        live = self.seed()
        before = read_exact(episode_path(self.root, live))

        original = self.m._remove_superseded

        def failing_remove(path):
            # The archived file is already in place at this point — the assertion below
            # proves the injection really did land in the gap between the two steps,
            # rather than before the first one.
            self.assertTrue(
                episode_path(self.root, live, retired=True).exists(),
                "fault injected too early: the archived file was not placed yet",
            )
            raise OSError("simulated failure removing the source (e.g. permission denied)")

        self.m._remove_superseded = failing_remove
        try:
            self.run_delta(
                {"work_id": "r", "ops": [{"op": "retire", "id": live, "reason": "consolidated"}]},
                expect_rc=1,
            )
        finally:
            self.m._remove_superseded = original

        # Not half-retired: wholly un-retired, byte-for-byte as before.
        self.assertEqual(self.assert_consistent(live), "active")
        self.assertEqual(read_exact(episode_path(self.root, live)), before)
        self.assertFalse(episode_path(self.root, live, retired=True).exists())
        # No staged temp file left behind either.
        self.assertEqual(
            sorted(p.name for p in self.root.rglob("*") if p.is_file()),
            [f"{live}.md"],
        )

    def test_a_half_retired_store_is_reported_rather_than_answered_around(self):
        """Compensation covers every failure the process survives to observe; a hard kill
        between the two steps runs no compensation at all, and markdown-in-git offers no
        journal to close that. So the residual state is made LOUD rather than claimed
        impossible: retrieval refuses instead of returning an answer that silently picks
        one of the two copies."""
        live = self.seed()
        # Hand-build exactly the state an interrupted retirement would leave.
        archived = episode_path(self.root, live, retired=True)
        archived.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(episode_path(self.root, live), archived)

        # Detection lives in the enumeration SEAM, so the writer inherits it too: a
        # store in this state must not accept further deltas either.
        for kwargs in ({}, {"include_retired": True}):
            with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                self.q.enumerate_episode_ids(self.root, **kwargs)
            self.assertIn("half-retired store", str(caught.exception))
            self.assertIn(live, str(caught.exception))

        self.run_query("enumerate", expect_rc=1)
        self.assertIn("half-retired store", self.last_stderr)
        self.run_delta({"work_id": "later", "ops": [create_op()]}, expect_rc=1)

        # Completing the interrupted retirement by hand clears it, in the direction the
        # error message names.
        episode_path(self.root, live).unlink()
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [])
        self.assertEqual(self.q.enumerate_episode_ids(self.root, include_retired=True), [live])

    def test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan(self):
        """The other half of "loud", and the half that was missing.

        A scanning reader meets the enumeration seam and refuses. `fetch` does not scan —
        it resolves one path — and the writer's `retire` does not scan either, so both
        used to proceed against a store the store itself had already declared corrupt:
        `fetch` silently returned the `active/` copy with `status: active`, and a retire
        committed on top of it. Loud in one hand and silent in the other is worse than
        either, because the silent hand is the one #308's consolidation pass walks back
        through when it follows a `consolidated-into:` reference by id."""
        live = self.seed()
        other = self.seed(run="admiral-298")
        other_before = read_exact(episode_path(self.root, other))

        archived = episode_path(self.root, live, retired=True)
        archived.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(episode_path(self.root, live), archived)

        # The path-resolution seam refuses instead of preferring one copy...
        with self.assertRaises(self.m.EpisodeDeltaError) as caught:
            self.m.resolve_episode_path(live, self.root)
        self.assertIn("half-retired store", str(caught.exception))
        self.assertIn(live, str(caught.exception))
        # ...so fetch-by-id, which is built on it, refuses too — through the API and
        # through the CLI, which used to answer 0 with `status: active`.
        with self.assertRaises(self.m.EpisodeDeltaError):
            self.q.fetch_episode(live, self.root)
        self.run_query("fetch", live, expect_rc=1)
        self.assertIn("half-retired store", self.last_stderr)

        # And every writer op refuses, not only the ones whose own work happens to scan.
        # A retire of a DIFFERENT episode is the case that used to commit.
        self.run_delta(
            {"work_id": "r", "ops": [{"op": "retire", "id": other, "reason": "unrelated"}]},
            expect_rc=1,
        )
        self.run_delta(
            {
                "work_id": "a",
                "ops": [
                    {
                        "op": "amend-assertion",
                        "id": other,
                        "assertion": "a4",
                        "lifecycle-standing": "disputed",
                        "history": "disputed 2026-08-05 (reviewer-audit)",
                    }
                ],
            },
            expect_rc=1,
        )
        self.run_delta({"work_id": "c", "ops": [create_op(run="reviewer-301")]}, expect_rc=1)

        # The refusal happened before any write: the unrelated episode is byte-identical.
        self.assertEqual(read_exact(episode_path(self.root, other)), other_before)

        # Completing the interrupted retirement by hand clears every one of them.
        episode_path(self.root, live).unlink()
        self.assertIsNotNone(self.q.fetch_episode(live, self.root))
        self.run_delta(
            {"work_id": "r2", "ops": [{"op": "retire", "id": other, "reason": "now fine"}]}
        )

    def test_a_successful_retirement_is_whole(self):
        # The positive control: without an injected fault, both halves land together.
        live = self.seed()
        self.retire(live)
        self.assertEqual(self.assert_consistent(live), "retired")


class RelocatedSilentOmissionTests(QueryTestCase):
    """Option A relocated the silent-omission class; it did not remove it. One fixture per
    relocated trap, each run against the SAME store as the real primitive, so the naive
    answer's shortness is demonstrated rather than asserted."""

    def test_trap1_a_flat_glob_misses_the_subdirectory_and_says_nothing(self):
        ids = sorted([self.seed(), self.seed(run="admiral-298")])

        naive = naive_flat_glob_enumeration(self.root)
        ours = self.q.enumerate_episode_ids(self.root)

        self.assertEqual(naive, [], "the naive flat glob should find nothing under the layout")
        self.assertEqual(ours, ids)
        # The whole defect in one line: no exception, no warning — just an empty answer
        # that reads exactly like an empty store.
        self.assertTrue(set(naive) < set(ours))

    def test_trap2_history_inclusive_that_forgets_the_union_returns_half(self):
        kept = self.seed()
        archived = self.retire(self.seed())

        naive = naive_history_inclusive_forgetting_the_union(self.root)
        ours = self.q.enumerate_episode_ids(self.root, include_retired=True)

        # The caller asked for history and the naive answer silently omits the one
        # episode that is ONLY reachable historically — the exact record they asked for.
        self.assertEqual(naive, [kept])
        self.assertNotIn(archived, naive)
        self.assertEqual(ours, sorted([kept, archived]))
        self.assertTrue(set(naive) < set(ours))

    def test_trap3_a_stray_at_the_old_flat_path_is_surfaced_not_skipped(self):
        """The real migration hazard, and the one most likely to be missed.

        A file at `episodes/<id>.md` is in NEITHER set. Ordinary retrieval does not see
        it (it scans the ordinary set), and history-inclusive retrieval does not see it
        either (it unions two directories this file is in neither of). It is therefore
        invisible to every query while looking, to a human reading the directory, exactly
        like a stored episode. Skipping it is a silent omission with a physical file
        sitting right there as evidence."""
        live = self.seed()
        stray = self.root / "governor-268-777.md"
        shutil.copyfile(episode_path(self.root, live), stray)

        # A naive implementation of EITHER direction simply does not see it...
        self.assertNotIn("governor-268-777", naive_history_inclusive_forgetting_the_union(self.root))
        # ...while the file is unmistakably present.
        self.assertTrue(stray.is_file())

        # Ours refuses, naming the file, rather than answering around it.
        for kwargs in ({}, {"include_retired": True}):
            with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                self.q.enumerate_episode_ids(self.root, **kwargs)
            self.assertIn("governor-268-777.md", str(caught.exception))
            self.assertIn("malformed store", str(caught.exception))

        # The CLI fails visibly too, rather than printing a short answer with exit 0.
        self.run_query("enumerate", expect_rc=1)
        self.assertIn("malformed store", self.last_stderr)

        # And the writer refuses as well — otherwise it would mint governor-268-778 while
        # a file claiming 777 sat unaccounted for, or worse, re-mint an id the stray
        # already holds.
        self.run_delta({"work_id": "post-stray", "ops": [create_op()]}, expect_rc=1)

        # Once the stray is filed where it belongs, everything answers again.
        shutil.move(str(stray), str(episode_path(self.root, "governor-268-777")))
        self.assertEqual(
            self.q.enumerate_episode_ids(self.root), sorted([live, "governor-268-777"])
        )

    def test_trap3_the_stores_own_readme_is_excluded_deliberately_not_by_accident(self):
        """`episodes/README.md` already lives at the flat root, so the stray check above
        would fire on it unless something excludes it. That exclusion is a NAMED
        allowlist, not a glob shape — the test asserts the mechanism, because an accident
        that currently works is one rename away from either refusing the whole store or
        (worse) silently accepting a real stray."""
        live = self.seed()
        (self.root / "README.md").write_text("# episodes\n", encoding="utf-8")
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [live])

        # The mechanism itself: the allowlist is what does it.
        self.assertIn("README.md", self.m.NON_EPISODE_FILENAMES)
        self.assertEqual(self.m.stray_episode_paths(self.root), [])

        # Remove it from the allowlist and the very same file becomes a stray — proving
        # the exclusion is coming from the allowlist and nowhere else.
        original = self.m.NON_EPISODE_FILENAMES
        self.m.NON_EPISODE_FILENAMES = frozenset()
        try:
            self.assertEqual(
                [p.name for p in self.m.stray_episode_paths(self.root)], ["README.md"]
            )
        finally:
            self.m.NON_EPISODE_FILENAMES = original

    def test_trap4_a_non_episode_file_inside_a_layout_directory_is_refused(self):
        """The mirror image of trap 3, and the one that actually shipped.

        Trap 3 is an adversarial input: an episode id at a path where no episode belongs.
        Trap 4 is the direction that was missed — a NON-episode file at a path where the
        store treats everything as an episode. Membership moved from file content to file
        location, so a directory listing became the candidate set, and anything sitting in
        the directory (a README, a `.gitkeep`, a `CODEOWNERS`) is minted into an id that
        no record backs."""
        live = self.seed()
        placeholder = self.root / "active" / "README.md"
        placeholder.write_text("# active\n", encoding="utf-8")

        # A listing-based implementation promotes the filename to an episode id...
        self.assertIn("README", naive_layout_listing_as_ids(self.root))
        # ...and everything built on the candidate set then dies on a record that is not
        # there, or (with the same name in both directories) on a false half-retirement.
        for kwargs in ({}, {"include_retired": True}):
            with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                self.q.enumerate_episode_ids(self.root, **kwargs)
            self.assertIn("malformed store", str(caught.exception))
            self.assertIn("active/README.md", str(caught.exception))

        self.run_query("enumerate", expect_rc=1)
        self.assertIn("malformed store", self.last_stderr)
        # The writer inherits the refusal through the same seam.
        self.run_delta({"work_id": "post-placeholder", "ops": [create_op()]}, expect_rc=1)

        placeholder.unlink()
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [live])

    def test_trap6_a_markdown_file_in_a_nested_subdirectory_is_surfaced_not_omitted(self):
        """Every scan in this store is one level deep, so anything a level further down
        is invisible to all of them while looking exactly like a stored episode to a
        human reading the tree. Two shapes, one class:

          episodes/archive/<id>.md      — a directory nobody declared
          episodes/active/old/<id>.md   — a subdirectory inside a layout directory

        Neither is produced by anything today, which is precisely why it has to be
        refused now: a hand-moved file, a half-finished migration, or a future tool is
        what produces one, and by then the omission is silent and already shipped."""
        live = self.seed()
        source = episode_path(self.root, live)

        for nested in (
            self.root / "archive" / "governor-268-777.md",
            self.root / "active" / "old" / "governor-268-778.md",
        ):
            nested.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, nested)

            for kwargs in ({}, {"include_retired": True}):
                with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                    self.q.enumerate_episode_ids(self.root, **kwargs)
                self.assertIn("malformed store", str(caught.exception))
                self.assertIn(nested.name, str(caught.exception))
            self.run_query("enumerate", expect_rc=1)
            self.run_delta({"work_id": "nested", "ops": [create_op()]}, expect_rc=1)

            shutil.rmtree(nested.parent)
            self.assertEqual(self.q.enumerate_episode_ids(self.root), [live])

        # The flat-root allowlist is scoped to the flat root: a README one level down is
        # not a store file anyone declared, so it is surfaced rather than assumed benign.
        buried = self.root / "archive" / "README.md"
        buried.parent.mkdir(parents=True, exist_ok=True)
        buried.write_text("# archive\n", encoding="utf-8")
        with self.assertRaises(self.m.EpisodeDeltaError):
            self.q.enumerate_episode_ids(self.root)

    def test_the_classifier_is_the_stores_id_grammar_not_a_list_of_filenames(self):
        """The mechanism behind trap 4, asserted directly.

        "Is this file an episode?" is DERIVABLE from the id grammar the store already
        enforces at create time, so it is derived. A hand-maintained enumeration would
        have to be edited whenever anyone adds a file and is silent in one direction (a
        real stray accepted) and store-bricking in the other."""
        m = self.m
        for name in (
            "README.md", "notes.md", "index.md", "CODEOWNERS.md",
            "governor-268-1.md",       # too few digits to be an id
            "Governor-268-001.md",     # not kebab-case
            "governor-268-001.txt",    # not a Markdown record
            ".gitkeep",                # the shipped placeholder shape
        ):
            self.assertIsNone(m.episode_id_for(Path(name)), f"{name} must not be an episode")
        for name in ("governor-268-001.md", "epic-298-012.md", "a1-000.md"):
            self.assertEqual(m.episode_id_for(Path(name)), name[: -len(".md")], name)

        # And the flat-root allowlist has NO say inside a layout directory: adding a name
        # to it cannot make a non-episode `.md` acceptable there.
        original = m.NON_EPISODE_FILENAMES
        m.NON_EPISODE_FILENAMES = frozenset({"README.md", "notes.md"})
        try:
            (self.root / "active").mkdir(parents=True, exist_ok=True)
            (self.root / "active" / "notes.md").write_text("x\n", encoding="utf-8")
            with self.assertRaises(m.EpisodeDeltaError) as caught:
                self.q.enumerate_episode_ids(self.root)
            self.assertIn("active/notes.md", str(caught.exception))
        finally:
            m.NON_EPISODE_FILENAMES = original

    def test_the_original_trap_a_disputed_episode_is_not_a_retired_one(self):
        """The fixture that started this whole thread, carried forward. An episode whose
        core assertion is `disputed` is in a legitimate lifecycle state that is NEITHER
        active nor retired, and it must still appear in ordinary search — retirement is
        an episode-level search-visibility switch, `lifecycle-standing` is a per-assertion
        epistemic judgement, and conflating them is what dropped the record."""
        disputed = self.seed()
        self.run_delta(
            {
                "work_id": "audit",
                "ops": [
                    {
                        "op": "amend-assertion",
                        "id": disputed,
                        "assertion": "a3",
                        "lifecycle-standing": "disputed",
                        "history": "disputed 2026-08-05 (reviewer-audit) — re-read the transcript",
                    }
                ],
            }
        )
        record = self.q.fetch_episode(disputed, self.root)
        self.assertEqual(record.agent_supplied["observed-behavior"].lifecycle_standing, "disputed")
        self.assertEqual(record.status, "active")
        self.assertIn(disputed, self.q.enumerate_episode_ids(self.root))
        self.assertTrue(self.m.is_episode_in_ordinary_search(disputed, self.root))

    def test_a_forged_status_line_in_free_text_cannot_move_an_episode_between_sets(self):
        """Under the rejected Option B this needed a defense (a line-anchored filter, plus
        the writer's single-line enforcement). Under Option A it is structurally
        impossible — there is no status parse to fool, because membership is the
        directory. Asserted rather than assumed, because "structurally impossible" is a
        claim about the implementation, and implementations change."""
        forged = "the run kept quoting - status: retired at me from an old transcript"
        op = create_op()
        op["agent_supplied"]["observed-behavior"]["statement"] = forged
        self.run_delta({"work_id": "forge", "ops": [op]})
        episode_id = "governor-268-001"

        # The forged text really is stored, verbatim, on a line of the file.
        self.assertIn(forged, read_exact(episode_path(self.root, episode_id)))

        # A content-parsing membership check — what Option B would have had to do —
        # silently drops this entirely-active episode from ordinary search.
        self.assertEqual(naive_status_grep_membership(self.root), [])
        # Ours cannot: it never reads the file to decide.
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [episode_id])
        self.assertTrue(self.m.is_episode_in_ordinary_search(episode_id, self.root))


class AbsentStoreTests(QueryTestCase):
    """Trap 5 — a store that is not there is REFUSED, never answered as empty.

    `Path.glob` over a missing directory returns nothing, so the naive reading of an
    absent store root is `count: 0, exit 0` — which is trap 1's own failure description
    ("an empty candidate set is indistinguishable from 'the store is empty'") arriving
    through a typo'd `--store-root` instead of through a wrong glob. It matters more
    after the layout was bound than before it: the store now REQUIRES two subdirectories,
    and git does not track empty directories, so "the layout never got committed" is a
    real way to arrive here.

    The writer is the deliberate exception: writing is a creating act, so it bootstraps
    the layout. Reading is not, so no read seam ever creates anything."""

    def test_a_store_root_that_does_not_exist_is_refused(self):
        missing = Path(self.tmp.name) / "typo-in-the-store-root"
        for kwargs in ({}, {"include_retired": True}):
            with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                self.q.enumerate_episode_ids(missing, **kwargs)
            # "the root is not there" is its own refusal, distinct from "the root is
            # there but a layout directory is missing" — asserted by wording, because
            # otherwise the two guards are indistinguishable and one of them is dead.
            self.assertIn("is not a directory", str(caught.exception))

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.q.main(["--store-root", str(missing), "enumerate"])
        self.assertEqual(rc, 1, out.getvalue())
        self.assertIn("missing store", err.getvalue())
        # A fetch against a store that is not there is "there is no store", not "there
        # is no such episode" — the two are different facts and only one is actionable.
        with self.assertRaises(self.m.EpisodeDeltaError):
            self.q.fetch_episode("governor-268-001", missing)

    def test_a_missing_layout_directory_is_refused_rather_than_read_as_empty(self):
        live = self.seed()
        archived = self.retire(self.seed(run="admiral-298"))
        shutil.rmtree(self.root / "active")

        for kwargs in ({}, {"include_retired": True}):
            with self.assertRaises(self.m.EpisodeDeltaError) as caught:
                self.q.enumerate_episode_ids(self.root, **kwargs)
            self.assertIn("missing store layout", str(caught.exception))
            self.assertIn("active", str(caught.exception))
        self.run_query("enumerate", expect_rc=1)
        self.assertIn("missing store layout", self.last_stderr)
        # The archived episode is still physically there; answering "0 episodes" would
        # have hidden a store that still holds records.
        self.assertTrue(episode_path(self.root, archived, retired=True).is_file())
        self.assertNotEqual(live, archived)

    def test_a_reader_never_creates_the_store_it_could_not_find(self):
        missing = Path(self.tmp.name) / "not-a-store"
        with self.assertRaises(self.m.EpisodeDeltaError):
            self.q.enumerate_episode_ids(missing)
        self.assertFalse(missing.exists(), "a read seam must not create the store")

    def test_the_writer_bootstraps_a_brand_new_store_root(self):
        """The other half of the rule: a create into a store root that does not exist yet
        must still work, because that is how a store comes into being at all."""
        fresh = Path(self.tmp.name) / "brand-new-store"
        delta_path = Path(self.tmp.name) / "bootstrap-delta.json"
        delta_path.write_text(
            json.dumps({"work_id": "bootstrap", "ops": [create_op()]}), encoding="utf-8"
        )
        self.assertEqual(
            self.m.main(["--delta", str(delta_path), "--store-root", str(fresh)]), 0
        )
        self.assertTrue((fresh / "active").is_dir())
        self.assertTrue((fresh / "retired").is_dir())
        self.assertEqual(self.q.enumerate_episode_ids(fresh), ["governor-268-001"])


class ShippedStoreTests(QueryTestCase):
    """The tests that would have caught the g4 BLOCK, and the reason they did not exist.

    Every other test in this file builds its own store and then reads it. Not one of them
    read the store this repository actually SHIPS — so `episodes/active/README.md` and
    `episodes/retired/README.md`, placed by this same gate, made the tracked store
    unreadable by its own tooling while a green suite said otherwise. Two tests close
    that gap from both ends: one reproduces the shipped store's real non-episode files in
    a temp root and drives every primitive over it, and one runs the shipped CLI against
    the real `episodes/` directory itself."""

    def test_the_shipped_stores_own_placeholders_read_end_to_end(self):
        copied = copy_store_scaffolding(self.root)
        self.assertGreater(
            copied, 0, "the tracked store ships no non-episode files to reproduce"
        )

        # An empty store ANSWERS "empty" — it does not refuse, and it does not invent an
        # id out of a placeholder's filename.
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [])
        self.assertEqual(self.q.enumerate_episode_ids(self.root, include_retired=True), [])

        live = self.seed()
        archived = self.retire(self.seed(run="admiral-298"))

        self.assertEqual(self.q.enumerate_episode_ids(self.root), [live])
        self.assertEqual(
            self.q.enumerate_episode_ids(self.root, include_retired=True),
            sorted([live, archived]),
        )
        self.assertEqual(self.run_query("enumerate")["ids"], [live])
        self.assertEqual(
            self.run_query("enumerate", "--include-retired")["ids"], sorted([live, archived])
        )
        self.assertEqual(self.run_query("fetch", archived)["ids"], [archived])
        self.assertEqual(
            self.run_query("select", "--field", "role", "--value", "implementer")["ids"],
            [live],
        )
        self.run_query("neighbours", live)
        # ...and the writer can still add to it, which is what #305 will need to do.
        self.run_delta({"work_id": "after", "ops": [create_op(run="reviewer-301")]})
        self.assertEqual(len(self.q.enumerate_episode_ids(self.root)), 2)

    def test_the_real_tracked_store_is_readable_by_the_tooling_that_ships_with_it(self):
        """Read-only, against the REAL `episodes/` — no temp store, nothing written.

        This is the one-command check that was missing: does the thing being shipped
        work? A store whose own placeholders are indistinguishable from episodes fails
        here in a single line, three roles earlier than it otherwise would."""
        for extra in ([], ["--include-retired"]):
            result = subprocess.run(
                [sys.executable, str(QUERY_SCRIPT), "enumerate", *extra],
                capture_output=True, text=True, cwd=str(ROOT), timeout=120,
            )
            self.assertEqual(
                result.returncode, 0,
                f"the shipped store cannot be read by its own tooling:\n{result.stderr}",
            )
            envelope = json.loads(result.stdout)
            # Whatever is in the store, every id it reports is a well-formed episode id
            # and resolves to a real record — never a phantom minted from a filename.
            for episode_id in envelope["ids"]:
                self.assertIsNotNone(
                    self.m.ID_RE.fullmatch(episode_id),
                    f"{episode_id!r} is not a well-formed episode id",
                )
                self.assertIsNotNone(self.q.fetch_episode(episode_id, ROOT / "episodes"))


class ConsolidationCompanionTests(QueryTestCase):
    """C5 — the #308 companion is not precluded.

    Consolidation is issue #308's job and is deliberately NOT built here. What this gate
    owes is that the store leaves it possible: with one member of a cluster retired, the
    surviving members stay findable by ordinary retrieval, and the retired member stays
    reachable — by id, by history-inclusive scan, and from its own neighbourhood.

    The failure this guards against is subtle. If retiring one member cost the cluster
    its findability, a consolidation pass would be a one-way door: consolidate once, and
    the evidence for whether the consolidation was right becomes unreachable."""

    def cluster(self, ref="docs/EPISODE_STORE.md"):
        """Three episodes joined on a shared artifact-ref — the join key section 6 already
        privileges, since a shared artifact is shared supporting evidence."""
        return [self.seed(**{"artifact-ref": [ref, f"unique-{i}.md"]}) for i in range(3)]

    def test_retiring_one_member_leaves_the_rest_findable_ordinarily(self):
        a, b, c = self.cluster()
        self.retire(c, reason="consolidated into cluster episode-store-retrieval-1")

        self.assertEqual(self.q.enumerate_episode_ids(self.root), sorted([a, b]))
        self.assertEqual(
            self.q.select_episode_ids(self.root, "artifact-ref", ["docs/EPISODE_STORE.md"]),
            sorted([a, b]),
        )
        # ...and they are still each other's neighbours: retiring a third member does not
        # break the join between the two that remain.
        self.assertEqual(self.q.neighbour_ids(self.root, a), [b])

    def test_the_retired_member_stays_reachable_three_ways(self):
        a, b, c = self.cluster()
        self.retire(c, reason="consolidated into cluster episode-store-retrieval-1")

        # 1. by id — the addressed lookup a `consolidated-into:` cross-reference needs.
        record = self.q.fetch_episode(c, self.root)
        self.assertIsNotNone(record)
        self.assertEqual(record.retired_reason, "consolidated into cluster episode-store-retrieval-1")
        # 2. by a deliberate history-inclusive scan.
        self.assertIn(c, self.q.enumerate_episode_ids(self.root, include_retired=True))
        self.assertIn(
            c, self.q.select_episode_ids(
                self.root, "artifact-ref", ["docs/EPISODE_STORE.md"], include_retired=True
            ),
        )
        # 3. from the neighbourhood of a surviving member, when history is asked for.
        self.assertEqual(self.q.neighbour_ids(self.root, a, include_retired=True), sorted([b, c]))

    def test_walking_back_from_an_archived_member_to_its_live_cluster(self):
        """The move #308 actually needs: start from a retired episode (the anchor is
        fetched by id, so retirement does not hide it from itself) and recover the live
        members it was consolidated with."""
        a, b, c = self.cluster()
        self.retire(c)
        self.assertEqual(self.q.neighbour_ids(self.root, c), sorted([a, b]))

    def test_retiring_every_member_loses_nothing(self):
        # Retirement is never deletion. A wholly-consolidated cluster is empty to
        # ordinary search and completely intact in history.
        cluster = self.cluster()
        for episode_id in cluster:
            self.retire(episode_id)
        self.assertEqual(self.q.enumerate_episode_ids(self.root), [])
        self.assertEqual(
            self.q.enumerate_episode_ids(self.root, include_retired=True), sorted(cluster)
        )
        for episode_id in cluster:
            self.assertEqual(len(self.q.fetch_episode(episode_id, self.root).agent_supplied), 5)


class SeamContainmentTests(QueryTestCase):
    """C2 — the ratified layout is bound at the seam set and NOWHERE else.

    Pre-g4 this class read "the layout is held open, so nothing may bind it". The
    decision is now bound, and the identical assertions carry a different but equally
    load-bearing obligation: the binding lives in exactly ONE place. A retrieval call
    site that inlines `episodes/active/...`, or greps for a `status: retired` line,
    re-scatters the layout across the codebase — and it is precisely that inlining that
    would have turned "bind the layout at g4" into a retrieval rewrite instead of a
    four-adapter swap. The proof that it did not is that these bans still hold with the
    decision bound and retirement-dependent retrieval shipped."""

    def test_query_module_inlines_no_status_check_and_no_directory_check(self):
        source = QUERY_SCRIPT.read_text(encoding="utf-8")
        # Strip comments and docstrings: the module DISCUSSES retirement at length, and
        # a naive grep over prose would either fire on the documentation or, worse, be
        # quietly relaxed until it stopped firing.
        code = "".join(
            line.split("#", 1)[0]
            for line in source.splitlines(keepends=True)
        )
        code = re.sub(r'"""[\s\S]*?"""', "", code)

        # What is banned is the PREDICATE, not the word. Serializing the record's own
        # `retired-reason` field is data (the field diff is layout-invariant — section 7
        # keeps it under either option); comparing against the bare value "retired", or
        # naming an active/ or retired/ directory, is the layout check that must live
        # behind a seam. So the assertions target the exact literals a status check or a
        # directory check would have to use.
        # (assertTrue with a short message, not assertNotIn, so a failure names the
        # offending construct instead of dumping the whole module.)
        for banned in ('"retired"', "'retired'", '"active"', "'active'", "active/", "retired/"):
            self.assertTrue(
                banned not in code,
                f"layout check inlined in query_episodes.py: found {banned}",
            )
        # Branching on status was the REJECTED Option-B adapter's job. With Option A
        # bound there is no legitimate reason for retrieval to branch on it at all —
        # membership is a directory fact. Reading .status to SERIALIZE it is data.
        branch = re.search(r"\.status\s*(==|!=|\bin\b)|if[^\n]*\.status", code)
        self.assertIsNone(branch, f"episode status branched on here: {branch.group(0) if branch else ''}")
        self.assertTrue(".glob(" not in code, "store scanning must go through iter_episode_ids()")
        # ...and the seams it MUST use are actually used.
        for seam in ("resolve_episode_path", "iter_episode_ids", "parse_episode"):
            self.assertTrue(seam in code, f"{seam} seam not called")

    def test_retrieval_reaches_the_layout_only_through_the_seams(self):
        """The direct proof that the binding is contained: move the layout by replacing
        the SEAMS ONLY — no source edit, no adapter switch — and retrieval follows it.

        This is the successor to the pre-g4 test that flipped `_LAYOUT_ADAPTER` between
        two candidate adapters. That switch is gone with the decision it existed for, but
        the property it was proving is not: if any retrieval primitive had inlined the
        real directory names, substituting the seams below would leave it reading the
        wrong place and the assertions would fail.
        """
        root = Path(self.tmp.name) / "seam-store"
        op = create_op()
        op["mechanical"]["artifact-ref"] = ["shared.md", "other.md"]
        delta_path = Path(self.tmp.name) / "seam-delta.json"
        delta_path.write_text(json.dumps({"work_id": "o", "ops": [op]}), encoding="utf-8")
        self.assertEqual(self.m.main(["--delta", str(delta_path), "--store-root", str(root)]), 0)
        episode_id = self.q.enumerate_episode_ids(root)[0]

        # Relocate the whole store under a directory neither seam-free code nor the
        # ratified layout knows about, and re-point ONLY the seams at it.
        moved = Path(self.tmp.name) / "somewhere-else"
        moved.mkdir()
        shutil.move(str(root / "active"), str(moved / "live"))

        originals = {
            name: getattr(self.m, name)
            for name in ("iter_episode_ids", "resolve_episode_path", "is_episode_in_ordinary_search")
        }
        self.m.iter_episode_ids = lambda r, include_retired: sorted(
            p.stem for p in (moved / "live").glob("*.md")
        )
        self.m.resolve_episode_path = lambda eid, r: (
            (moved / "live" / f"{eid}.md") if (moved / "live" / f"{eid}.md").exists() else None
        )
        self.m.is_episode_in_ordinary_search = lambda eid, r: (
            moved / "live" / f"{eid}.md"
        ).exists()
        try:
            self.assertEqual(self.q.enumerate_episode_ids(root), [episode_id])
            self.assertEqual(self.q.fetch_episode(episode_id, root).role, "implementer")
            self.assertEqual(
                self.q.select_episode_ids(root, "artifact-ref", ["shared.md"]), [episode_id]
            )
            self.assertEqual(self.q.neighbour_ids(root, episode_id), [])
        finally:
            for name, original in originals.items():
                setattr(self.m, name, original)

    def test_the_writer_names_the_directories_only_inside_the_seam_block(self):
        """C2's other half. query_episodes.py may not name the directories at all; the
        writer must — it is where the seams live — but only THERE. A path, glob, or move
        that escaped into an op handler or the transaction would re-scatter the layout,
        which is exactly what the seam table exists to prevent.

        The record-grammar uses of the same two words are excluded by EXACT LINE, not by
        a loosened pattern: `lifecycle-standing: active` and an episode's default `status`
        are data that happen to share a vocabulary with the layout, and letting this check
        drift into accepting them by shape would let a real inlined path through with
        them."""
        source = WRITER_SCRIPT.read_text(encoding="utf-8")
        seam_start = source.index("# --- seams (EPISODE_STORE.md section 7's seam table)")
        seam_end = source.index("# --- id assignment (EPISODE_STORE.md section 2)")
        outside = source[:seam_start] + source[seam_end:]
        code = re.sub(
            r'"""[\s\S]*?"""',
            "",
            "".join(line.split("#", 1)[0] for line in outside.splitlines(keepends=True)),
        )

        grammar = (
            'LIFECYCLE_STANDINGS = ("active", "disputed", "superseded", "rejected")',
            'status: str = "active"',
            'lifecycle_standing="active",',
            '''"'active' and is never set here)"''',
        )
        banned = ('"active"', "'active'", '"retired"', "'retired'", "active/", "retired/",
                  "ACTIVE_DIR", "RETIRED_DIR")
        for line in code.splitlines():
            stripped = line.strip()
            if not stripped or any(ok in stripped for ok in grammar):
                continue
            for token in banned:
                self.assertNotIn(
                    token, stripped, f"layout literal {token} outside the seam block: {stripped}"
                )
        # ...and the seam block really is where they live, so the exclusion above is not
        # vacuously true because the module simply stopped naming them anywhere.
        inside = source[seam_start:seam_end]
        for token in ("ACTIVE_DIR", "RETIRED_DIR"):
            self.assertIn(token, inside)

    def test_the_membership_seam_answers_for_both_sets(self):
        # g4's composition rule — scan with iter_episode_ids(), then confirm each id
        # through is_episode_in_ordinary_search() — needs both halves present and
        # working. They are now wired up by the retirement-dependent primitives.
        episode_id = self.seed()
        self.assertTrue(self.m.is_episode_in_ordinary_search(episode_id, self.root))
        self.assertFalse(self.m.is_episode_in_ordinary_search("governor-268-999", self.root))


class FloorInterpreterPortabilityTests(unittest.TestCase):
    """The store must run on the OLDEST interpreter it claims to support, not merely on
    whatever the author happened to launch.

    Why this class exists. PR #320 went green locally on Python 3.14 and RED in CI on
    3.12: 39 failures from one root cause, `Path.read_text(newline="")`, a kwarg pathlib
    only gained in 3.13. The local suite could not have caught it, because the local
    interpreter was two minor versions AHEAD of CI — so "green here" was never evidence
    for "green there", and nothing said so out loud.

    The sting is that the skew came from following advice. Issue #313 documents that
    `py -m pytest` false-reds on this host (no pytest installed for it), which routes
    agents onto `python`. Here `python` is 3.14 and `py` is 3.12 — the CI version. The
    documented false-red and this false-green are the same underlying problem, two
    interpreters that are not the same environment, and the guidance is wrong in both
    directions.

    A CI matrix entry would not have helped: CI already ran the floor and already caught
    it. What was missing was a LOCAL check, so this drives the store on the floor
    interpreter in a real subprocess. It SKIPS rather than fails when no floor
    interpreter is discoverable, so it is a safety net and not a new environment
    requirement.

    Stated honestly, because a guard whose reach is overclaimed is worse than none. On CI
    the running interpreter IS the floor, so the round trip below genuinely exercises it
    (and `["python"]` resolves on the first try). On a developer host it runs only if a
    launcher name resolves to the floor or `EPISODE_STORE_FLOOR_PYTHON` points at one;
    otherwise it skips and the drift test below is the only protection left. So this
    class does not make local green equal CI green — it narrows the gap and names it.
    """

    def floor_interpreter(self):
        """A launcher that really is the declared floor version, or None.

        Every candidate is ACCEPTED ONLY IF it reports the floor version when asked, so
        bare launcher names are safe to probe — the version check, not the name, is what
        makes the answer trustworthy. That matters here: on this host `py` is not the
        Windows launcher but a shim pointing straight at a 3.12 runtime, and it rejects
        the `-3.12` selector outright. A candidate list that assumed the selector worked
        found nothing and skipped, which is the failure mode this whole class exists to
        prevent — a guard that silently never runs is worse than no guard, because it
        reads as coverage.
        """
        major, minor = load().REQUIRES_PYTHON
        candidates = []
        # Explicit override first: on a host where no launcher NAME resolves to the floor,
        # this is the only way to point the guard at one. Needed more often than it looks
        # — a launcher's meaning can differ between an interactive shell and a subprocess
        # spawned from the test runner (observed here: `py` is 3.12 from the shell and
        # 3.14 from inside pytest), so name-based discovery alone is not dependable.
        override = os.environ.get("EPISODE_STORE_FLOOR_PYTHON")
        if override:
            candidates.append([override])
        candidates += [
            ["py", f"-{major}.{minor}"],      # real Windows launcher, version selector
            [f"python{major}.{minor}"],       # POSIX versioned name
            ["py"],                           # a shim that may already BE the floor
            ["python3"],
            ["python"],                       # on CI the runner IS the floor, so this hits
        ]
        for cmd in candidates:
            try:
                probe = subprocess.run(
                    cmd + ["-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
                    capture_output=True, text=True, timeout=60,
                )
            except (OSError, subprocess.SubprocessError):
                continue
            if probe.returncode == 0 and probe.stdout.strip() == f"{major}.{minor}":
                return cmd
        return None

    def test_the_declared_floor_matches_the_version_ci_actually_pins(self):
        # Config drift: if CI's pin moves and REQUIRES_PYTHON does not, the floor this
        # suite exercises stops being the floor that gates the merge.
        ci = ROOT / ".github" / "workflows" / "ci.yml"
        if not ci.exists():
            self.skipTest("no CI workflow in this checkout")
        pinned = re.findall(
            r'python-version:\s*"?([0-9]+\.[0-9]+)"?', ci.read_text(encoding="utf-8")
        )
        self.assertTrue(pinned, "found no pinned python-version in ci.yml")
        major, minor = load().REQUIRES_PYTHON
        self.assertIn(
            f"{major}.{minor}", pinned,
            f"REQUIRES_PYTHON is {major}.{minor} but ci.yml pins {pinned} — the declared "
            "floor and the version that actually gates the merge have drifted apart",
        )

    def test_the_store_actually_runs_on_the_floor_interpreter(self):
        # The check that would have caught the 3.13-only kwarg before the push. Drives a
        # real create -> enumerate round trip, because merely importing the modules would
        # not have reached the failing call.
        interp = self.floor_interpreter()
        if interp is None:
            major, minor = load().REQUIRES_PYTHON
            self.skipTest(f"no Python {major}.{minor} interpreter available to probe")

        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "episodes"
            store.mkdir()
            delta = Path(tmp) / "delta.json"
            delta.write_text(
                json.dumps({"work_id": "floor-probe", "ops": [create_op()]}), encoding="utf-8"
            )

            wrote = subprocess.run(
                interp + [str(WRITER_SCRIPT), "--delta", str(delta), "--store-root", str(store)],
                capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(
                wrote.returncode, 0,
                f"writer failed on the floor interpreter:\n{wrote.stdout}\n{wrote.stderr}",
            )

            read_back = subprocess.run(
                # --store-root is a flag on the top-level parser, so it precedes the
                # subcommand; argparse rejects it after one.
                interp + [str(QUERY_SCRIPT), "--store-root", str(store), "enumerate"],
                capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(
                read_back.returncode, 0,
                f"query failed on the floor interpreter:\n{read_back.stdout}\n{read_back.stderr}",
            )
            self.assertIn("governor-268", read_back.stdout)


if __name__ == "__main__":
    unittest.main()
