"""Tests for scripts/verify_episode_observations.py — the guard that keeps episode
records reading as observations rather than instructions (issue #460).

The load-bearing tests here are the two RED PROOFS. A guard that has only ever been
seen passing is indistinguishable from a guard that cannot fail, which is the exact
defect class several of the records this guard protects were filed about. So both red
proofs build a store the guard must REFUSE, and assert the refusal names the offender —
not merely that the exit code was non-zero, since a stale exception entry can also
produce a non-zero exit.

Stores are built through scripts/apply_episode_delta.py, the store's only write path,
into a throwaway temp root. The one test that reads the real episodes/ store reads it
and never writes to it.
"""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD_SCRIPT = ROOT / "scripts" / "verify_episode_observations.py"
WRITER_SCRIPT = ROOT / "scripts" / "apply_episode_delta.py"
REAL_STORE = ROOT / "episodes"

# The verbatim pre-rewrite statement of issue-308-001.a5, recovered from the commit
# before gate g2's restatement. It is the issue's own worked BEFORE, and the record the
# #447 handoff pointed a crew at as its migration precedent.
ISSUE_308_001_BEFORE = (
    "Give the harness the same fail-safe discipline as the production code under test: "
    "wrap per-iteration work in try/except with a guaranteed stop-signal in `finally`, "
    "and mark helper threads daemon=True as a backstop."
)


def load_guard():
    spec = importlib.util.spec_from_file_location("verify_episode_observations", GUARD_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def create_op(run="governor-268", **statements):
    """One well-formed create op. Every agent-supplied statement is overridable by
    keyword, using the field name with '-' spelled '_'."""
    defaults = {
        "task_intent": "Fix the STATE_NOTE-fallback wording gap named in the launch order.",
        "expected_behavior": "The named launch-order defect is the only place carrying the wording.",
        "observed_behavior": "The Admiral spine carries the identical defect, unnamed by the order.",
        "impact_cost": "One extra sweep pass needed to find the sibling.",
        "workaround": "none.",
    }
    defaults.update(statements)
    return {
        "op": "create",
        "mechanical": {
            "run": run,
            "project": "constellation-skills",
            "role": "implementer",
            "spine-step": "g1-implement",
            "context-manifest-ref": "ctx-governor-268-g1@a1b2c3d",
            "refusals": 0,
            "reopens": 0,
            "rework-count": 0,
            "failed-commands": 0,
            "artifact-ref": ["docs/EPISODE_STORE.md"],
        },
        "agent_supplied": {
            "task-intent": {"strength": "strong", "statement": defaults["task_intent"]},
            "expected-behavior": {"strength": "medium", "statement": defaults["expected_behavior"]},
            "observed-behavior": {"strength": "strong", "statement": defaults["observed_behavior"]},
            "impact-cost": {"strength": "medium", "statement": defaults["impact_cost"]},
            "workaround": {"strength": "strong", "statement": defaults["workaround"]},
        },
    }


class GuardTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "episodes"
        (self.root / "active").mkdir(parents=True)
        (self.root / "retired").mkdir(parents=True)
        self.guard = load_guard()

    def seed(self, *ops):
        delta_path = Path(self.tmp.name) / "delta.json"
        delta_path.write_text(json.dumps({"work_id": "t", "ops": list(ops)}), encoding="utf-8")
        rc = subprocess.run(
            [
                sys.executable,
                str(WRITER_SCRIPT),
                "--delta",
                str(delta_path),
                "--store-root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)

    def run_guard(self, root=None, strict=False):
        """The guard as a subprocess, so the exit code under test is a REAL process exit
        code and not a return value a caller could mistranslate."""
        argv = [sys.executable, str(GUARD_SCRIPT), "--store-root", str(root or self.root)]
        if strict:
            argv.append("--strict")
        proc = subprocess.run(argv, capture_output=True, text=True)
        return proc.returncode, proc.stdout + proc.stderr


class RedProofTests(GuardTestCase):
    """The guard OBSERVED REFUSING. Both cases assert the offender is NAMED, because a
    non-zero exit alone does not distinguish "it caught the prescription" from "an
    unrelated exception entry went stale"."""

    def test_r1_refuses_the_pre_rewrite_text_of_issue_308_001_verbatim(self):
        """RED PROOF 1 — drawn from the corpus: the exact statement issue #460 was filed
        about, before gate g2 restated it."""
        self.seed(create_op(run="issue-308", workaround=ISSUE_308_001_BEFORE))

        rc, out = self.run_guard(strict=True)

        self.assertEqual(rc, 1, out)
        offender_lines = [ln for ln in out.splitlines() if ln.strip().startswith("OFFENDER")]
        self.assertTrue(offender_lines, out)
        self.assertTrue(
            any("issue-308-001" in ln and " a5 " in ln for ln in offender_lines),
            f"the guard did not name the offending episode and assertion:\n{out}",
        )
        self.assertIn("imperative", out)

    def test_r2_refuses_a_prescription_not_drawn_from_the_corpus(self):
        """RED PROOF 2 — authored here, sharing no wording with any stored record, so the
        guard cannot be passing r1 by having memorised one sentence."""
        self.seed(
            create_op(
                run="synthetic-900",
                workaround=(
                    "Always verify the checksum before you trust the artifact, and never "
                    "ship a build whose provenance you cannot name."
                ),
            )
        )

        rc, out = self.run_guard(strict=True)

        self.assertEqual(rc, 1, out)
        self.assertTrue(
            any(
                "synthetic-900-001" in ln and " a5 " in ln
                for ln in out.splitlines()
                if ln.strip().startswith("OFFENDER")
            ),
            f"the guard did not name the offending episode and assertion:\n{out}",
        )

    def test_second_person_is_caught_in_any_kind_not_just_workaround(self):
        """The imperative rule is scoped to two kinds; the second-person rule is not. A
        record that addresses its reader in an `observed-behavior` field is still the
        store speaking to a future agent."""
        self.seed(
            create_op(
                run="synthetic-901",
                observed_behavior="The gate failed, so you have to re-run it after the fix.",
            )
        )

        rc, out = self.run_guard(strict=True)

        self.assertEqual(rc, 1, out)
        self.assertTrue(
            any(
                "synthetic-901-001" in ln and "second-person" in ln
                for ln in out.splitlines()
                if ln.strip().startswith("OFFENDER")
            ),
            out,
        )


class ReportVersusStrictTests(GuardTestCase):
    def test_report_mode_exits_zero_on_a_store_it_would_refuse_under_strict(self):
        """--strict is what makes this a gate. Report mode has to stay usable on a dirty
        store, or the honest-null branch could not ship alongside the red proof."""
        self.seed(create_op(run="issue-308", workaround=ISSUE_308_001_BEFORE))

        strict_rc, _ = self.run_guard(strict=True)
        report_rc, report_out = self.run_guard(strict=False)

        self.assertEqual(strict_rc, 1)
        self.assertEqual(report_rc, 0, report_out)
        self.assertIn("OFFENDER", report_out)

    def test_a_clean_store_passes_under_strict(self):
        self.seed(
            create_op(
                run="synthetic-902",
                workaround="The harness was given a guaranteed stop-signal in `finally`.",
            )
        )

        rc, out = self.run_guard(strict=True)

        self.assertEqual(rc, 0, out)
        self.assertNotIn("OFFENDER", out)


class ExceptionListTests(GuardTestCase):
    """The exception list is the part most able to become a loophole, so its failure
    modes are pinned rather than trusted."""

    def test_a_listed_offender_does_not_fail_the_guard(self):
        guard = self.guard
        self.seed(create_op(run="synthetic-903", workaround="Keep the cold critic as a floor."))
        offenders, _, _, _ = guard.scan_store(self.root, exceptions={})
        self.assertTrue(offenders)
        key = offenders[0].key

        _, stale, inapplicable, _ = guard.scan_store(
            self.root, exceptions={key: "a stated reason"}
        )

        self.assertEqual((stale, inapplicable), ([], []))

    def test_an_entry_naming_a_missing_assertion_of_a_present_episode_is_stale(self):
        """The episode is here; the assertion it exempts is not. That is an exemption
        pointing at nothing, and it fails."""
        self.seed(create_op(run="synthetic-904"))

        _, stale, inapplicable, _ = self.guard.scan_store(
            self.root, exceptions={("synthetic-904-001", "a99"): "a stated reason"}
        )

        self.assertEqual(inapplicable, [])
        self.assertEqual(len(stale), 1)
        self.assertIn("synthetic-904-001/a99", stale[0])
        self.assertIn("no such assertion", stale[0])

    def test_an_entry_for_an_episode_absent_from_this_store_is_inapplicable_not_stale(self):
        """A list authored for one store must not condemn every other store, or no
        fixture could ever pass and the guard would be untestable against a clean one.
        The deleted-in-the-real-store case is covered by RealStoreTests instead."""
        self.seed(create_op(run="synthetic-904"))

        _, stale, inapplicable, _ = self.guard.scan_store(
            self.root, exceptions={("no-such-episode-001", "a5"): "a stated reason"}
        )

        self.assertEqual(stale, [])
        self.assertEqual(inapplicable, ["no-such-episode-001/a5"])

    def test_an_entry_whose_record_no_longer_instructs_is_stale(self):
        """The entry names a live assertion that has since been restated. It is exactly
        the case where the list would quietly outlive its reason."""
        self.seed(
            create_op(
                run="synthetic-905",
                workaround="The cold critic was kept as a floor for every gate plan.",
            )
        )

        _, stale, inapplicable, _ = self.guard.scan_store(
            self.root, exceptions={("synthetic-905-001", "a5"): "a stated reason"}
        )

        self.assertEqual(inapplicable, [])
        self.assertEqual(stale, ["synthetic-905-001/a5"])

    def test_a_stale_entry_fails_the_guard_under_strict_through_the_cli(self):
        """Pinned end to end as a real process exit, not just through scan_store: a stale
        entry has to reach a non-zero exit or nothing enforces it.

        The store is seeded with an episode whose workaround plainly instructs, and the
        guard is run with that offender excepted AND with a second entry pointing at an
        assertion of the same episode that does not exist. The first entry keeps the
        offender quiet; the second is the stale one, so a non-zero exit here can only
        have come from staleness."""
        self.seed(create_op(run="synthetic-906", workaround="Keep the cold critic as a floor."))
        self.guard.EXCEPTIONS.clear()
        self.guard.EXCEPTIONS.update(
            {
                ("synthetic-906-001", "a5"): "the live offender, excepted",
                ("synthetic-906-001", "a99"): "points at an assertion that does not exist",
            }
        )

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            rc = self.guard.main(["--store-root", str(self.root), "--strict"])
        out = buffer.getvalue()

        # main()'s return value IS the process exit code: the module ends in
        # `raise SystemExit(main())`.
        self.assertIn("raise SystemExit(main())", GUARD_SCRIPT.read_text(encoding="utf-8"))
        self.assertNotIn("OFFENDER", out)
        self.assertIn("STALE EXCEPTION synthetic-906-001/a99", out)
        self.assertEqual(rc, 1, out)

    def test_every_shipped_exception_carries_a_non_empty_reason(self):
        self.assertTrue(self.guard.EXCEPTIONS, "the shipped exception list is empty")
        for key, reason in self.guard.EXCEPTIONS.items():
            self.assertTrue((reason or "").strip(), f"{key} has no reason")

    def test_an_empty_reason_is_refused_rather_than_silently_honoured(self):
        unexplained = self.guard._validate_exception_reasons({("e-001", "a5"): "   "})
        self.assertEqual(unexplained, ["e-001/a5"])


class MeasuredFalsePositiveTests(GuardTestCase):
    """Each case here is a real statement shape the naive detector flagged and this one
    must not. They are the measurement, pinned so a later widening of the lexicon cannot
    silently re-admit them."""

    def test_task_intent_in_the_bare_infinitive_is_not_flagged(self):
        """The store's own canonical worked record is in this form
        (docs/EPISODE_STORE.md). A detector that flags it flags the document defining the
        format — 31 of the naive detector's 41 imperative hits were exactly this."""
        hits = self.guard.triggers_for(
            "task-intent", "Fix the STATE_NOTE-fallback wording gap named in the launch order."
        )
        self.assertEqual(hits, [])

    def test_a_descriptive_modal_is_not_flagged(self):
        for kind, statement in (
            ("observed-behavior", "A gate that MUST prove a refusal has no direct expression here."),
            ("expected-behavior", "`git check-ignore -v` on the seeded path should exit 0."),
        ):
            with self.subTest(kind=kind):
                self.assertEqual(self.guard.triggers_for(kind, statement), [])

    def test_a_quoted_instruction_the_record_observed_is_not_flagged(self):
        """issue-308-023 records a candidate instruction verbatim as a cold sensor's own
        words. A record that QUOTES an instruction it observed is an observation."""
        statement = (
            "An independent cold sensor was dispatched, and the candidate instruction as "
            "the sensor phrased it, recorded as the sensor's words and deciding nothing: "
            "'before a check counts as evidence, state the condition under which it would "
            "FAIL and show it can reach that condition.'"
        )
        self.assertEqual(self.guard.triggers_for("workaround", statement), [])

    def test_second_person_inside_a_quotation_is_not_flagged(self):
        """issue-304-g3-005 quotes the context imperative under study. The record is not
        addressing its own reader."""
        statement = (
            "Determine, from an actual run, whether re-anchoring the context imperative "
            "to 'before you open any source file' moves orientation ordering."
        )
        self.assertEqual(self.guard.triggers_for("task-intent", statement), [])

    def test_an_appositive_list_is_not_read_as_an_imperative_clause(self):
        """issue-308-002: `(section heading, file path, anchor)` made `file` look like a
        clause-opening verb."""
        statement = (
            "Before planning, the launch order's NAMED defect was grepped against current "
            "code, and any named EDIT TARGET (section heading, file path, anchor) was "
            "checked for existence at the named address."
        )
        self.assertEqual(self.guard.triggers_for("workaround", statement), [])

    def test_a_command_placeholder_is_not_read_as_an_imperative_clause(self):
        """issue-304-g3-003: `git log --format=%h -- <file>` made `file` look like one."""
        statement = (
            "The question was answered with a command over git history: "
            "git log --format=%h -- <file>, then git show <sha>:<file> for each."
        )
        self.assertEqual(self.guard.triggers_for("workaround", statement), [])


class RealStoreTests(unittest.TestCase):
    """The guard run over the REAL episodes/ store. Without this the guard runs once at
    authoring time and never again, and the store can drift back with nothing noticing.

    Read-only: nothing here writes to episodes/.
    """

    def run_real(self, strict):
        argv = [
            sys.executable,
            str(GUARD_SCRIPT),
            "--store-root",
            str(REAL_STORE),
        ] + (["--strict"] if strict else [])
        proc = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout + proc.stderr

    def test_the_real_store_is_clean_under_strict(self):
        rc, out = self.run_real(strict=True)
        self.assertEqual(
            rc,
            0,
            "episodes/ carries a statement that reads as an instruction and is not on the "
            f"exception list:\n{out}",
        )

    def test_the_real_store_scan_actually_examined_the_records(self):
        """A guard that passes because it read nothing is the failure mode this whole
        issue is about. The count is asserted to be substantial and to match the store."""
        guard = load_guard()
        offenders, stale, inapplicable, examined = guard.scan_store(REAL_STORE)

        record_count = len(list((REAL_STORE / "active").glob("*.md")))
        self.assertGreaterEqual(examined, record_count * 5)
        self.assertEqual(stale, [])
        # Every shipped entry must still name a live offender in the REAL store.
        # This is where a DELETED episode is caught: the guard itself reports such
        # an entry as inapplicable rather than failing, and only a scan of the real
        # store can tell the two apart.
        self.assertEqual(inapplicable, [])
        self.assertTrue(
            offenders,
            "the shipped exception list names records that must still trip a trigger; "
            "no offender at all means the scan is not reaching them",
        )
        self.assertTrue(all(o.key in guard.EXCEPTIONS for o in offenders))


if __name__ == "__main__":
    unittest.main()
