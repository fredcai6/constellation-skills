"""A work-id may NEST, and four tools used to disagree about that.

The epic/commander convention writes one nested segment:
`epic-418-followon/commander-424` names the work area
`.agent-work/epic-418-followon/commander-424/`. It is a shipped convention -- the
archived commander's own `spine.json` carries that string as its `work_id`, and the
Admiral launch order prescribes the directory. Four tools each answered the `/`
differently, by accident:

  * `run_crew.py` parsed the work-id out of a session name from the LEFT
    (`split("/")[1]`), truncating a nested id to its first segment and addressing a
    DIFFERENT run's registry -- for a commander under an epic, the Admiral's own.
    The commander's finished crew was then never finalized and sat `running` with
    its result artifact present on disk.
  * `verify_iterative_role_artifacts.py` refused a `/` at the door and so never
    reached the G1/G2 check it exists to run. A verifier that refuses before
    verifying reports nothing about the artifact at all.
  * `apply_episode_delta.py` forbade a `/` in an episode's `run` while
    `verify_episode_captured.py` demanded exactly the work-id the closeout spine
    passes it. The store's only sanctioned write path could not satisfy the gate
    that mandates it.
  * `episode_capture.manifest_root()` stripped ONE path segment for a work-id that
    `context_manifest.manifest_path()` re-appends in full, writing the run's
    provenance to `.agent-work/<epic>/<epic>/<commander>/context/` -- the doubled
    path this defect was first seen as.

THE PRINCIPLE, applied identically in all four: a work-id is a `/`-separated
sequence of safe segments. Support it, validate every segment, refuse anything
unsafe LOUDLY, and where a work-id must become a single filename component flatten
it by an explicit injective encoding -- never by dropping segments.

Every test here carries its FLAT twin as the positive control. The twin is not
decoration: without it, "the nested id works" is satisfiable by a tool that has
simply stopped checking anything, and "the unsafe id is refused" is satisfiable by a
tool that refuses everything. The twin pins the check to its specific condition.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NESTED = "epic-418-followon/commander-424"
FLAT = "commander-424"


def load_module(name: str, filename: str | None = None):
    path = ROOT / "scripts" / (filename or f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# 1. run_crew.py -- the session name is parsed back to the RIGHT work-id
# --------------------------------------------------------------------------- #
RC = load_module("run_crew")


def _record_external(root: Path, work_id: str, gate="g2", role="reviewer"):
    """Record one external crew through the real wrapper, returning its entry."""
    handoff = f".agent-work/{work_id}/crew-handoffs/{gate}-{role}.md"
    (root / handoff).parent.mkdir(parents=True, exist_ok=True)
    (root / handoff).write_text("handoff\n", encoding="utf-8")
    result = f".agent-work/{work_id}/{gate}-review/RESULT.md"
    return RC.record_external_attempt(
        work_id=work_id, gate=gate, role=role, handoff=handoff, result=result,
        worktree=".", model=None, attempt=1, root=root,
        entries=RC.load_registry(RC.registry_path(work_id, root)),
    )


class CrewRegistryAddressingTests(unittest.TestCase):
    """`--verify-result` must find the registry its own launch wrote."""

    def _verify_round_trip(self, work_id: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = _record_external(root, work_id)
            self.assertEqual(
                "running", entry["status"],
                "the wrapper did not record a running crew, so 'verify finalizes it' "
                "is impossible to fail -- the fixture, not the tool, is broken",
            )
            registry = RC.registry_path(work_id, root)
            self.assertTrue(
                registry.is_file(),
                f"no registry was written at {registry}; the addressing assertion "
                "below would then be about nothing",
            )
            # The crew finishes: its result artifact appears on disk.
            (root / entry["result"]).parent.mkdir(parents=True, exist_ok=True)
            (root / entry["result"]).write_text("done\n", encoding="utf-8")

            entries = RC.load_registry_for_resume(entry["session_name"], root)
            fresh, verified = RC.verify_external_result(entries, entry["session_name"], root)
            self.assertTrue(fresh, "the result artifact was written, so it must read fresh")
            return json.loads(registry.read_text(encoding="utf-8"))[0]

    def test_nested_work_id_finalizes_its_own_registry(self):
        """RED before the fix: `load_registry_for_resume` read
        `.agent-work/epic-418-followon/crew-runs.json` (the epic's registry, not the
        commander's), found no such session, and raised `cannot verify: no crew
        recorded` -- leaving this entry `running` forever."""
        self.assertEqual("completed", self._verify_round_trip(NESTED)["status"])

    def test_flat_work_id_finalizes_identically(self):
        """The positive control. A flat id took the same path before the fix and
        still does; if this ever fails, the test above proves nothing about
        nesting."""
        self.assertEqual("completed", self._verify_round_trip(FLAT)["status"])

    def test_work_id_is_parsed_from_the_right_not_the_left(self):
        session = RC.session_name(NESTED, "g2", "reviewer", 1)
        self.assertEqual(NESTED, RC.work_id_from_session(session))
        self.assertEqual(FLAT, RC.work_id_from_session(RC.session_name(FLAT, "g2", "reviewer", 1)))

    def test_deeper_nesting_round_trips_too(self):
        """Two segments is the convention, not the limit -- the parse counts the
        fixed tail rather than assuming a depth."""
        deep = "epic-1/wave-2/commander-3"
        self.assertEqual(deep, RC.work_id_from_session(RC.session_name(deep, "g2", "rev", 7)))

    def test_unsafe_work_id_is_refused_loudly(self):
        for bad in ("../escape", "epic/../..", "epic//x", "/abs", "epic\\win", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(RC.CrewLaunchError) as caught:
                    RC.validate_work_id(bad)
                self.assertIn(repr(bad), str(caught.exception),
                              "the refusal must name the id it refused")

    def test_a_separator_in_gate_or_role_is_refused_at_the_boundary(self):
        """Right-anchored parsing is only sound while gate/role stay flat, so the
        name-minting boundary refuses a separator there rather than writing a session
        name that cannot be parsed back."""
        with self.assertRaises(RC.CrewLaunchError):
            RC.session_name(NESTED, "g2/sneaky", "reviewer", 1)
        with self.assertRaises(RC.CrewLaunchError):
            RC.session_name(NESTED, "g2", "rev/iewer", 1)
        # Control: the same call with flat components is accepted, so the refusal
        # above is about the separator and not about the call shape.
        self.assertTrue(RC.session_name(NESTED, "g2", "reviewer", 1))

    def test_a_malformed_session_name_is_refused_not_guessed(self):
        for bad in ("constellation/epic/commander", "elsewhere/a/b/c/attempt-1",
                    "constellation/a/b/c/nope-1"):
            with self.subTest(bad=bad):
                with self.assertRaises(RC.CrewLaunchError):
                    RC.work_id_from_session(bad)


# --------------------------------------------------------------------------- #
# 2. verify_iterative_role_artifacts.py -- refusing at the door hid a real G2 break
# --------------------------------------------------------------------------- #
ROLE_VERIFIER = ROOT / "scripts" / "verify_iterative_role_artifacts.py"


class RoleArtifactWorkAreaTests(unittest.TestCase):
    """The verifier must reach the artifact before it can report on it."""

    #: A REPLAN_INPUT that genuinely violates G2 (`schema_version` must be int 1).
    BROKEN_PACKET = {
        "schema_version": "1", "current_plan": {}, "completed_outcomes": [],
        "wave_evidence": [], "discrepancies": [], "open_current_wave_issue_ids": [],
        "unlaunched_items": [], "repo_state": "clean",
    }

    def _run(self, tmp: Path, work_id: str):
        skills_root = tmp / "skills-root"
        (skills_root / "constellation-replan" / "scripts").mkdir(parents=True, exist_ok=True)
        (skills_root / "CORPUS.json").write_text("{}", encoding="utf-8")
        (skills_root / "constellation-replan" / "scripts" / "verify_replan.py").write_bytes(
            (ROOT / "skills" / "replan" / "scripts" / "verify_replan.py").read_bytes()
        )
        area = tmp.joinpath(".agent-work", *work_id.split("/"))
        area.mkdir(parents=True, exist_ok=True)
        (area / "REPLAN_INPUT.json").write_text(json.dumps(self.BROKEN_PACKET), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(ROLE_VERIFIER), "commander", "--work-id", work_id,
             "--skills-root", str(skills_root)],
            cwd=str(tmp), capture_output=True, text=True,
        )
        return proc.returncode, (proc.stderr or "") + (proc.stdout or "")

    def test_nested_work_id_reaches_the_g2_check(self):
        """RED before the fix: the output was `work-id contains unsafe path
        characters` and said nothing at all about G2, so a real schema violation in
        a commander's replan packet stayed invisible."""
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self._run(Path(tmp), NESTED)
        self.assertEqual(1, code)
        self.assertIn("violates G2", out)
        self.assertNotIn("unsafe path segment", out)

    def test_flat_work_id_reports_the_same_violation(self):
        """The positive control. The flat id always reached G2; if the two outputs
        ever disagree, the assertion above is about the id and not about the packet."""
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self._run(Path(tmp), FLAT)
        self.assertEqual(1, code)
        self.assertIn("violates G2", out)

    def test_unsafe_segments_are_still_refused_loudly(self):
        for bad in ("epic/../../etc", "epic//x", "/abs", "epic/.."):
            with self.subTest(bad=bad):
                with tempfile.TemporaryDirectory() as tmp:
                    code, out = self._run(Path(tmp), bad)
                self.assertEqual(1, code)
                self.assertIn("unsafe path segment", out)
                self.assertNotIn("violates G2", out,
                                 "an unsafe id must never be resolved far enough to "
                                 "read an artifact")


# --------------------------------------------------------------------------- #
# 2b. the work-id pair -- run_crew and verify_iterative_role_artifacts must
# agree on what one SEGMENT of a work-id may look like
# --------------------------------------------------------------------------- #
VIRA = load_module("verify_iterative_role_artifacts")


class WorkIdGrammarPinTests(unittest.TestCase):
    """`run_crew.WORK_ID_SEGMENT_RE` and `verify_iterative_role_artifacts.SAFE_ID`
    express the same per-segment work-id grammar and both apply it with
    `.fullmatch()` (`validate_work_id` above; the verifier's own segment
    check). Nothing pinned the two together
    (`grep -rn "WORK_ID_SEGMENT_RE\\|SAFE_ID" tests/` returned nothing before
    this test) -- this is `test_the_two_run_grammars_are_the_same_grammar`'s
    twin for the work-id pair."""

    def test_the_two_work_id_grammars_are_the_same_grammar(self):
        # SAFE_ID spells its pattern with explicit `^...$` anchors;
        # WORK_ID_SEGMENT_RE relies on `.fullmatch()` for the same anchoring
        # (both call sites use fullmatch, never search/match) -- strip the
        # anchors before comparing so this pins the CHARACTER CLASS the two
        # agree on, not an anchor-spelling difference.
        self.assertEqual(
            RC.WORK_ID_SEGMENT_RE.pattern,
            VIRA.SAFE_ID.pattern.removeprefix("^").removesuffix("$"),
        )


# --------------------------------------------------------------------------- #
# 3. the episode pair -- writer and gate must be mutually SATISFIABLE
# --------------------------------------------------------------------------- #
WRITER = ROOT / "scripts" / "apply_episode_delta.py"
GATE = ROOT / "scripts" / "verify_episode_captured.py"
AED = load_module("apply_episode_delta")


def _create_delta(run: str) -> dict:
    return {
        "work_id": run,
        "ops": [{
            "op": "create",
            "mechanical": {
                "run": run, "project": "constellation-skills", "role": "commander",
                "spine-step": "feedback", "context-manifest-ref": "none",
                "refusals": 0, "reopens": 0, "rework-count": 0, "failed-commands": 0,
            },
            "agent_supplied": {
                kind: {"strength": "strong", "statement": "what happened"}
                for kind in ("task-intent", "expected-behavior", "observed-behavior",
                             "impact-cost", "workaround")
            },
        }],
    }


@contextlib.contextmanager
def _store():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "episodes" / "active").mkdir(parents=True)
        (root / "episodes" / "retired").mkdir(parents=True)
        yield root


def _write(root: Path, run: str):
    delta = root / f"delta-{abs(hash(run))}.json"
    delta.write_text(json.dumps(_create_delta(run)), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(WRITER), "--delta", str(delta),
         "--store-root", str(root / "episodes")],
        cwd=str(root), capture_output=True, text=True,
    )


def _gate(root: Path, work_id: str, phase="feedback"):
    return subprocess.run(
        [sys.executable, str(GATE), work_id, "--store-root", str(root / "episodes"),
         "--phase", phase],
        cwd=str(root), capture_output=True, text=True,
    )


class EpisodeWriterGatePairTests(unittest.TestCase):
    """The sharpest of the four: the writer forbade the id the gate demanded, so a
    mandated closeout step could not be completed correctly by any sanctioned path."""

    def _round_trip(self, work_id: str):
        with _store() as root:
            wrote = _write(root, work_id)
            self.assertEqual(0, wrote.returncode,
                             f"writer refused {work_id!r}: {wrote.stderr}{wrote.stdout}")
            gated = _gate(root, work_id)
            return wrote, gated, sorted(p.name for p in (root / "episodes" / "active").glob("*.md"))

    def test_nested_work_id_is_writable_and_then_passes_the_gate(self):
        """RED before the fix, on BOTH sides: the writer answered
        `create.mechanical.run: '...' must be kebab-case` (exit 1) and the gate
        answered `BLOCKED -- no episode ... records run '...'` (exit 1). Neither
        could be satisfied while the other held."""
        wrote, gated, names = self._round_trip(NESTED)
        self.assertEqual(0, gated.returncode, gated.stderr)
        self.assertIn("1 episode(s) recorded", gated.stdout)
        self.assertEqual(["epic-418-followon_commander-424-001.md"], names)

    def test_flat_work_id_round_trips_identically(self):
        """The positive control -- the flat pair always worked, which is what makes
        the nested failure a disagreement between the two tools rather than a broken
        store."""
        _, gated, names = self._round_trip(FLAT)
        self.assertEqual(0, gated.returncode, gated.stderr)
        self.assertEqual(["commander-424-001.md"], names)

    def test_the_record_keeps_the_work_id_verbatim(self):
        """The id is FLATTENED for the filename; the record is not. The gate matches
        on `- run:`, so a normalized run would be a different work-id wearing this
        one's name."""
        with _store() as root:
            self.assertEqual(0, _write(root, NESTED).returncode)
            text = (root / "episodes" / "active" /
                    "epic-418-followon_commander-424-001.md").read_text(encoding="utf-8")
        self.assertIn(f"- run: {NESTED}\n", text)

    def test_episode_files_stay_flat_inside_active(self):
        """The store's layout invariant (`_layout_episode_ids` refuses a record one
        level deeper) is not weakened by supporting a nested run."""
        with _store() as root:
            self.assertEqual(0, _write(root, NESTED).returncode)
            found = [p.relative_to(root / "episodes").as_posix()
                     for p in (root / "episodes").rglob("*.md")]
        self.assertEqual(["active/epic-418-followon_commander-424-001.md"], found)

    def test_sequence_numbers_increment_for_a_nested_run(self):
        """A prefix scan over the raw run would find nothing on disk and hand out
        `-001` forever, overwriting the previous episode in silence."""
        with _store() as root:
            self.assertEqual(0, _write(root, NESTED).returncode)
            self.assertEqual(0, _write(root, NESTED).returncode)
            names = sorted(p.name for p in (root / "episodes" / "active").glob("*.md"))
        self.assertEqual(
            ["epic-418-followon_commander-424-001.md",
             "epic-418-followon_commander-424-002.md"], names)

    def test_two_epics_sharing_a_commander_segment_do_not_collide(self):
        """The flattening must be injective, or one epic's record overwrites
        another's."""
        with _store() as root:
            self.assertEqual(0, _write(root, "epic-a/commander-424").returncode)
            self.assertEqual(0, _write(root, "epic-b/commander-424").returncode)
            names = sorted(p.name for p in (root / "episodes" / "active").glob("*.md"))
        self.assertEqual(["epic-a_commander-424-001.md", "epic-b_commander-424-001.md"], names)

    def test_flattening_is_injective_because_a_run_cannot_hold_the_separator(self):
        """`_` is the flattening character precisely because `RUN_RE` excludes it;
        if that ever stops holding, two distinct runs can mint one id."""
        self.assertIsNone(AED.RUN_RE.fullmatch("epic_a"))
        self.assertIsNotNone(AED.RUN_RE.fullmatch("epic-a/commander-424"))
        self.assertEqual("epic-a_commander-424", AED.run_to_id_stem("epic-a/commander-424"))

    def test_writer_still_refuses_an_unsafe_run(self):
        for bad in ("../escape", "a//b", "a/../b", "/abs", "Epic/Commander"):
            with self.subTest(bad=bad):
                with _store() as root:
                    proc = _write(root, bad)
                self.assertEqual(1, proc.returncode)
                self.assertIn("create.mechanical.run", proc.stderr + proc.stdout)

    def test_gate_refuses_an_id_the_writer_could_never_record(self):
        """REFUSED (2), not BLOCKED (1). "Capture one with apply_episode_delta.py" is
        advice that cannot be followed for an ungrammatical id, and a block that can
        never be cleared reads as a missing record rather than a mismatched id."""
        with _store() as root:
            self.assertEqual(0, _write(root, NESTED).returncode)  # a real record exists
            refused = _gate(root, "epic/../escape")
            blocked = _gate(root, "never-ran-here")
        self.assertEqual(2, refused.returncode, refused.stderr)
        self.assertIn("ungrammatical run id", refused.stderr)
        # The control that keeps the line meaningful: a WELL-FORMED id with no
        # episode is still BLOCKED, so the refusal above is about the grammar and not
        # about every unmatched id.
        self.assertEqual(1, blocked.returncode, blocked.stderr)
        self.assertIn("BLOCKED", blocked.stderr)

    def test_the_two_run_grammars_are_the_same_grammar(self):
        """The gate names the writer's grammar literally rather than importing it
        (the valve). Literal duplication is only safe while the two agree."""
        gate = load_module("verify_episode_captured")
        self.assertEqual(AED.RUN_RE.pattern, gate.RUN_RE.pattern)


# --------------------------------------------------------------------------- #
# 4. episode_capture.manifest_root -- the doubled path in the tree
# --------------------------------------------------------------------------- #
EC = load_module("episode_capture")
CM = load_module("context_manifest")


class ManifestRootNestingTests(unittest.TestCase):
    """`manifest_path` re-appends every work-id segment, so the root must have every
    one of them stripped."""

    def _manifest(self, work_id: str) -> str:
        base = Path(os.path.abspath("/repo")).joinpath(".agent-work", *work_id.split("/"))
        return CM.manifest_path(EC.manifest_root(base, work_id), work_id, "plan").as_posix()

    def test_nested_work_id_writes_beside_its_own_spine(self):
        """RED before the fix: `.agent-work/epic-418-followon/epic-418-followon/
        commander-424/context/plan.json` -- the doubled path, written in silence
        because nothing on this path raises."""
        self.assertTrue(self._manifest(NESTED).endswith(
            "/.agent-work/epic-418-followon/commander-424/context/plan.json"),
            self._manifest(NESTED))
        self.assertNotIn("epic-418-followon/epic-418-followon", self._manifest(NESTED))

    def test_flat_work_id_is_unchanged(self):
        """The positive control -- the flat case was always right and must stay
        byte-for-byte where it was."""
        self.assertTrue(self._manifest(FLAT).endswith(
            "/.agent-work/commander-424/context/plan.json"), self._manifest(FLAT))

    def test_mechanical_snapshot_lands_in_the_same_work_area(self):
        base = Path(os.path.abspath("/repo")).joinpath(".agent-work", *NESTED.split("/"))
        self.assertTrue(EC.snapshot_path(base, NESTED, "plan").as_posix().endswith(
            "/.agent-work/epic-418-followon/commander-424/mechanical/plan.json"))

    def test_without_a_work_id_the_answer_is_the_historical_one(self):
        """The backward-compatibility control, and the only assertion in this class
        that holds BOTH before and after the fix: with no work-id to strip there is
        nothing to get wrong, so the old parent-of-base_dir answer must survive
        untouched. If this ever moves, the change stopped being scoped to nesting."""
        base = Path(os.path.abspath("/repo")).joinpath(".agent-work", "commander-424")
        self.assertEqual(base.parent, EC.manifest_root(base))

    def test_a_checklist_not_under_its_own_work_id_keeps_the_old_answer(self):
        """Scratch spines really do sit under an evidence directory whose name has
        nothing to do with their work-id. That is a different question, and guessing
        at it is how the doubled path was written; those keep parent-of-base_dir."""
        base = Path(os.path.abspath("/repo")).joinpath(
            ".agent-work", "issue-467", "red-repro", "scratch", "face-a")
        self.assertEqual(base.parent, EC.manifest_root(base, "red-repro-431-face-a"))

    def test_a_worktree_root_with_no_agent_work_ancestor_refuses_rather_than_escapes(self):
        """RED before the fix (#585): the real defect, reproduced with the real
        function and no mocking. Handed a WORKTREE ROOT -- not a work area, no
        `.agent-work` anywhere in its ancestry -- the old unconditional
        `base.parent` climbed OUT of the worktree into `.worktrees/`, a directory
        shared by every worktree in the repo, and silently composed a sibling of
        the worktree it was asked about. This is the exact call shape that put
        `.worktrees/probe`, `/s` and `/t` on disk: `manifest_root(worktree_root,
        work_id)` for each placeholder work-id. It must now refuse instead of
        guessing."""
        worktree_root = Path(os.path.abspath("/repo")).joinpath(
            ".worktrees", "epic-568-510")
        for work_id in ("probe", "s", "t"):
            with self.assertRaises(ValueError):
                EC.manifest_root(worktree_root, work_id)

    def test_the_refusal_does_not_fire_on_the_legitimate_scratch_spine_case(self):
        """The positive control beside the refusal above: a base_dir that DOES sit
        under `.agent-work` -- so it is somewhere inside a real work area, even if
        not exactly under its own work-id -- keeps working exactly as
        `test_a_checklist_not_under_its_own_work_id_keeps_the_old_answer` already
        proves. Restated here, next to the refusal, so the boundary between "refuse"
        and "keep the old answer" is visible in one place rather than split across
        the file."""
        base = Path(os.path.abspath("/repo")).joinpath(
            ".agent-work", "issue-1", "scratch")
        self.assertEqual(base.parent, EC.manifest_root(base, "unrelated-work-id"))


if __name__ == "__main__":
    unittest.main()
