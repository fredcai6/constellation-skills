"""The `origin` stamp is PROVENANCE: written, and read by nothing (#315/#568/#609).

Stamp-and-compare is retired. This file used to assert that
`checklist_engine.origin_worktree_refusal` compared `origin.worktree` against a
worktree toplevel the engine resolved from its own ambient cwd, and refused
every guarded verb when the two disagreed. That predicate, the two verb sets
that fed it and the per-verb `git rev-parse --show-toplevel` behind it are all
gone (#609 g2), so the scenarios that tested them are gone with them.

Two things are asserted here now, each with a failing side as well as a
passing one:

  1. The stamp is still WRITTEN. `init_work_area.instantiate_spine` stamps a
     top-level `origin` block when it writes a spine, and
     `spine_lifecycle.build_origin` builds the fuller one -- so a spine still
     carries its own repo reference from creation.
  2. The stamp is read by NOTHING that decides anything. The differential in
     `TheStampIsProvenanceNotADecisionInput` drives the same guarded verbs
     against the same spine differing only in `origin.worktree`, from a cwd
     that is not the spine's worktree, and demands one answer for all of them.

**This supersedes the 2026-08-15 worktree-identity ruling**, which settled that
the comparison should be equality against a git-resolved toplevel rather than
containment. That ruling answered how to resolve the two sides of a comparison
that no longer exists. Nothing was left unguarded by removing it WHEREVER A
LEASE EXISTS -- and the leaseless path was WIDENED. The comparison answered
"where am I", never "is this mine" -- ownership is the LEASE, but only where one
is actually held. `checklist_engine.require_session` gates mutating verbs only
once an active lease exists and returns early otherwise, and `_active_lease`
reads a RELEASED lease as absent. So on a spine with NO ACTIVE LEASE -- never
claimed, or claimed and since released -- this comparison was the sole refusal,
and the engine now asserts nothing about location: measured from a foreign
worktree, `start` and `attach` on a never-claimed spine and `start` after a
release went from refused to accepted, writing state into a tree the agent is
not standing in. Under an active lease held by another session, nothing changed.

That widening is ACCEPTED and deliberate, not a no-op. A `cd <worktree> &&`
prefix defeated the comparison, so it was never a boundary -- but a forgeable
guard is not the same as no guard. The engine now reads no location at all,
ambient or derived: there is no second value that can disagree with the first,
and no ambient reading a check command could forge by `cd`-ing first, because
the engine no longer asks the question anywhere.

The lexical rule that derives a worktree from a spine's path is NOT retired --
only the engine's copy of it is. The rule lives in the stdlib-only hook, as
`spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s
case table is its specification. The engine-side copy was deleted in #609 g2
under `ADMIRAL_RULING-2` N2: three sound decisions in a row removed all three of
its consumers, and a definition nothing calls is not shipped. It re-lands in
#610's wave together with #315 -- the consumer that threads `cwd` into the
engine's check runner -- and re-derives against that same table.

Every fixture is built in a `tempfile.TemporaryDirectory()` -- never against
this worktree's own `.git` or the shared checkout.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_SCRIPT = ROOT / "scripts" / "checklist_engine.py"
INIT_WORK_AREA_SCRIPT = ROOT / "scripts" / "init_work_area.py"
COMMANDER_TEMPLATE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_init_work_area():
    return _load("init_work_area_origin_test", INIT_WORK_AREA_SCRIPT)


def _load_engine():
    return _load("checklist_engine_origin_test", ENGINE_SCRIPT)


# --------------------------------------------------------------------------- #
# 1. The write side: the stamp
# --------------------------------------------------------------------------- #


class StampsOriginAtInstantiation(unittest.TestCase):
    """`instantiate_spine` stamps `origin` into the spine it writes, from values
    it already holds -- never a guessed branch/base/parent."""

    def setUp(self):
        self.m = _load_init_work_area()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _instantiate_real_commander_spine(self) -> Path:
        out = self.m.instantiate_spine(
            self.root, "issue-7", COMMANDER_TEMPLATE, skill_dir=ROOT.as_posix()
        )
        self.assertIsNotNone(out)
        return out

    def test_stamps_exactly_work_id_worktree_and_opened_by(self):
        out = self._instantiate_real_commander_spine()
        data = json.loads(out.read_text(encoding="utf-8"))
        origin = data.get("origin")

        self.assertIsInstance(origin, dict, "the written spine carries no top-level origin")
        # Exactly these three: init_work_area does not know branch, base, parent
        # or the dispatching session, and a plausible wrong value is worse than
        # an absent one.
        self.assertEqual(set(origin), {"work_id", "worktree", "opened_by"})
        self.assertEqual(origin["work_id"], "issue-7")
        self.assertEqual(origin["worktree"], self.root.resolve().as_posix())
        self.assertEqual(origin["opened_by"], "init_work_area")

    def test_stamped_spine_still_parses_and_keeps_its_resolved_content(self):
        out = self._instantiate_real_commander_spine()
        text = out.read_text(encoding="utf-8")
        data = json.loads(text)  # would raise if the stamp corrupted the write

        self.assertEqual(data["work_id"], "issue-7")
        self.assertIn("init", data["tasks"])
        self.assertNotIn("<work-id>", text)
        self.assertNotIn("<commander-skill-dir>", text)

    def test_stamp_keys_are_a_subset_of_the_lifecycle_origin_block(self):
        """Key-compatible with `spine_lifecycle.build_origin` (a strict subset),
        so the two producers of `origin` cannot drift into two shapes."""
        lifecycle = _load("spine_lifecycle_origin_test", ROOT / "scripts" / "spine_lifecycle.py")
        full = lifecycle.build_origin(
            "issue-7", branch="b", worktree="/w", base="sha",
            opened_at="2026-01-01T00:00:00+00:00", parent="unknown",
        )
        out = self._instantiate_real_commander_spine()
        origin = json.loads(out.read_text(encoding="utf-8"))["origin"]

        self.assertTrue(set(origin) <= set(full), f"{set(origin) - set(full)} not in build_origin")
        self.assertEqual(origin["opened_by"], "init_work_area")
        self.assertEqual(full["opened_by"], "spine_open")

    def test_an_existing_origin_in_the_template_is_preserved(self):
        """setdefault posture: a template that already carries the block keeps
        its own values, so a future template can stamp a richer origin."""
        tpl = self.root / "SPINE.template.json"
        carried = {"work_id": "from-template", "worktree": "/somewhere/else",
                   "opened_by": "a-future-template", "branch": "b"}
        tpl.write_text(json.dumps({"work_id": "<work-id>", "origin": carried}), encoding="utf-8")

        out = self.m.instantiate_spine(self.root, "issue-7", tpl)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["origin"], carried)

    def test_the_placeholder_guard_still_runs_and_nothing_is_written(self):
        """The stamp must not move the validity guards aside: a spine carrying an
        unresolvable resolver-owned token still fails loudly, with no file left."""
        tpl = self.root / "SPINE.template.json"
        tpl.write_text('{"work_id": "<work-id>"}', encoding="utf-8")
        original = self.m.resolve_spine

        def regressed(*args, **kwargs):
            return original(*args, **kwargs).replace(
                '"issue-7"', '"issue-7", "cmd": "<commander-skill-dir>/x.py"'
            )

        self.m.resolve_spine = regressed
        try:
            with self.assertRaises(SystemExit) as caught:
                self.m.instantiate_spine(self.root, "issue-7", tpl)
        finally:
            self.m.resolve_spine = original
        self.assertIn("<commander-skill-dir>", str(caught.exception))
        self.assertFalse((self.root / ".agent-work" / "issue-7" / "spine.json").exists())

    def test_invalid_json_still_fails_before_any_write(self):
        tpl = self.root / "SPINE.template.json"
        tpl.write_text('{"work_id": "<work-id>",}', encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            self.m.instantiate_spine(self.root, "issue-7", tpl)
        self.assertFalse((self.root / ".agent-work" / "issue-7" / "spine.json").exists())


# --------------------------------------------------------------------------- #
# 2. Shared fixture helper
# --------------------------------------------------------------------------- #


def _git_in(cwd: Path, *args: str) -> None:
    """Run git in a test fixture repo, loudly: identity pinned so `commit`
    works on a bare CI account, output captured so `check=True` failures
    carry the message."""
    subprocess.run(
        ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", *args],
        cwd=str(cwd), check=True, capture_output=True, text=True,
    )


# --------------------------------------------------------------------------- #
# 3. Provenance: the stamp is WRITTEN, and read by NOTHING for a decision
# --------------------------------------------------------------------------- #


_ABSENT = object()

# Varied deliberately across a real path, a foreign path, and every shape a
# comparison would have had to handle. If ANY decision anywhere reads
# `origin.worktree`, at least one of these rows has to behave differently from
# the others -- that is the whole discriminating power of the table.
_STAMPS: dict[str, object] = {
    "the spine's own worktree": None,  # filled in with the real path at run time
    "a foreign tree": "/nonexistent/some/other/tree",
    "a sibling sharing a name prefix": None,  # filled in: <worktree>-2
    "not a path at all": "not-a-path",
    "an empty string": "",
    "a number": 7,
    "worktree key absent": _ABSENT,
    # Separators and case, constructed EXPLICITLY rather than inherited from
    # the platform. `os.path.normcase` is the identity function on POSIX, so a
    # folding expectation written against the host would assert nothing here.
    # The retired comparison needed the fold because the two producers
    # normalize differently -- `spine_lifecycle` stores `str(Path(worktree))`
    # (native separators), `init_work_area` stores `as_posix()`. Nothing
    # compares the stamp now, so a backslashed, drive-lettered, wrong-cased
    # value must be exactly as inert as every other row, on every platform.
    "a Windows-shaped path": "C:\\W\\REPO",
    "the same path, wrong case": None,  # filled in: the worktree, upper-cased
}


class TheStampIsProvenanceNotADecisionInput(unittest.TestCase):
    """`origin.worktree` keeps being WRITTEN, and is read by NOTHING that makes
    a decision (#609 g2, superseding the 2026-08-15 worktree-identity ruling).

    The pairing has two halves and this class fails if either breaks:

      * **Written** -- both producers still stamp it, so the provenance a human
        or a reconciler reads is still there.
      * **Never a decision input** -- the engine's behaviour is IDENTICAL for
        every value of it. The table below drives the same guarded verbs
        against the same spine differing ONLY in that one field, from a cwd
        that is not the spine's worktree, and demands one answer. A decision
        that read the stamp could not give the same answer to "my own
        worktree" and "/nonexistent/some/other/tree", so re-introducing one
        turns this red.

    Why the differential rather than a source scan: a scan for the string
    `origin` finds prose and provenance reads and cannot tell a decision from a
    display. Behaviour can."""

    def setUp(self):
        self.E = _load_engine()
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.worktree = base / "wt"
        self.foreign = base / "elsewhere"
        self.nogit = base / "nogit"
        (self.worktree / ".agent-work" / "w1").mkdir(parents=True)
        self.foreign.mkdir()
        self.nogit.mkdir()
        _git_in(self.worktree, "init", "-q")
        _git_in(self.foreign, "init", "-q")
        self.spine_path = self.worktree / ".agent-work" / "w1" / "spine.json"
        self._cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self._cwd)
        self.tmp.cleanup()

    def _stamps(self) -> dict:
        """The table with its two run-time paths filled in. The sibling row is
        `<worktree>-2`: unequal to the worktree under any comparison, but equal
        under a string-prefix one, so it also pins that a prefix comparison was
        not left behind."""
        table = dict(_STAMPS)
        table["the spine's own worktree"] = self.worktree.as_posix()
        table["a sibling sharing a name prefix"] = self.worktree.as_posix() + "-2"
        table["the same path, wrong case"] = self.worktree.as_posix().upper()
        return table

    def _write_spine(self, stamp) -> None:
        origin = {"work_id": "w1", "opened_by": "init_work_area"}
        if stamp is not _ABSENT:
            origin["worktree"] = stamp
        self.spine_path.write_text(json.dumps({
            "work_id": "w1", "type": "gated", "items": ["g1"],
            "origin": origin,
            "tasks": {"g1": {
                "id": "g1", "title": "g1", "imperative": "do g1",
                "preconditions": [], "postconditions": [],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }},
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }, indent=2), encoding="utf-8")
        journal = self.spine_path.parent / "spine.json.journal"
        if journal.exists():
            journal.unlink()

    def _observable(self, stamp, cwd: Path) -> dict:
        """Drive three guarded verbs -- the lease verb, a state verb and the
        write-only verb -- from `cwd` and return everything an agent could
        observe: the exit codes, whether anything was refused, and the state
        that landed. Timestamps are excluded on purpose; they differ between
        two identical runs and would drown the signal."""
        import contextlib
        import io

        self._write_spine(stamp)
        codes, refused = [], []
        os.chdir(cwd)
        try:
            for argv in (
                ["claim", "--session-id", "s1", "--claimed-by", "implementer", "--worktree", "."],
                ["start", "g1", "--session-id", "s1"],
                ["heartbeat", "--session-id", "s1"],
            ):
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    codes.append(self.E.main(["--file", str(self.spine_path), *argv]))
                refused.append("REFUSED:" in err.getvalue())
        finally:
            os.chdir(self._cwd)
        state = json.loads(self.spine_path.read_text(encoding="utf-8"))
        return {
            "codes": codes,
            "refused": refused,
            "gate status": state["tasks"]["g1"]["status"],
            "lease": (state.get("engine_session") or {}).get("status"),
        }

    def _assert_one_answer_for_every_stamp(self, cwd: Path) -> None:
        table = self._stamps()
        answers = {name: self._observable(stamp, cwd) for name, stamp in table.items()}
        first = answers["the spine's own worktree"]
        for name, answer in answers.items():
            with self.subTest(stamp=name):
                self.assertEqual(
                    first, answer,
                    f"{name!r} behaved differently from the spine's own worktree: "
                    f"something reads origin.worktree for a decision",
                )
        # A table that collapsed to one row would pass vacuously.
        self.assertGreaterEqual(len(answers), 9)
        # And the one answer must be the WORKING one: a table where every row
        # is refused identically would also be "identical".
        self.assertEqual([0, 0, 0], first["codes"], "every stamp was refused, not accepted")
        self.assertEqual([False, False, False], first["refused"])
        self.assertEqual("in-progress", first["gate status"])
        self.assertEqual("active", first["lease"])

    def test_provenance_the_stamp_is_written_by_both_producers(self):
        """Half one. `init_work_area.instantiate_spine` and
        `spine_lifecycle.build_origin` both still put a worktree in the spine.
        Delete either stamp and this goes red."""
        lifecycle = _load("spine_lifecycle_provenance_test", ROOT / "scripts" / "spine_lifecycle.py")
        built = lifecycle.build_origin(
            "issue-7", branch="b", worktree="/w/repo", base="sha",
            opened_at="2026-01-01T00:00:00+00:00", parent="unknown",
        )
        self.assertEqual("/w/repo", built.get("worktree"))

        init_work_area = _load_init_work_area()
        out = init_work_area.instantiate_spine(
            self.worktree, "issue-7", COMMANDER_TEMPLATE, skill_dir=ROOT.as_posix()
        )
        stamped = json.loads(out.read_text(encoding="utf-8"))["origin"]
        self.assertEqual(self.worktree.resolve().as_posix(), stamped.get("worktree"))

    def test_provenance_the_stamp_is_not_a_decision_input_from_a_foreign_tree(self):
        """Half two, at its most discriminating: a cwd that is a real git
        worktree and is NOT the spine's. Any decision reading the stamp has to
        separate these rows."""
        self._assert_one_answer_for_every_stamp(self.foreign)

    def test_provenance_the_stamp_is_not_a_decision_input_with_no_git_toplevel(self):
        """The same, from a directory git resolves no worktree toplevel for.
        This row is where a fail-closed reading would hide."""
        self._assert_one_answer_for_every_stamp(self.nogit)

    def test_provenance_the_stamp_is_not_a_decision_input_from_the_spines_own_worktree(self):
        """The cwd that makes the case and separator rows carry weight.

        From a foreign cwd no stamp can match, so a reading of the stamp
        refuses every row identically and `the same path, wrong case` proves
        nothing the plain foreign row does not. Standing in the spine's OWN
        worktree is the only cwd where that row separates on a case-sensitive
        filesystem -- so this is what makes the folding expectation
        constructed rather than inherited."""
        self._assert_one_answer_for_every_stamp(self.worktree)

    def test_provenance_the_engine_never_rewrites_the_stamp_it_does_not_read(self):
        """Written and left alone: driving guarded verbs preserves the stamp
        byte-for-byte, so the provenance survives the run that ignores it."""
        stamp = "/nonexistent/some/other/tree"
        self._observable(stamp, self.foreign)
        origin = json.loads(self.spine_path.read_text(encoding="utf-8"))["origin"]
        self.assertEqual(
            {"work_id": "w1", "opened_by": "init_work_area", "worktree": stamp}, origin
        )


class TheEngineTakesNoAmbientReading(unittest.TestCase):
    """The successor to `test_it_is_pure`, which asserted that the retired
    predicate referenced no impure name and was explicitly NOT transitive: it
    read only that one function's `__code__.co_names`, so impurity in a callee
    went unnoticed and the guarantee was inherited rather than made.

    There is no predicate to keep pure now. The property worth keeping is the
    one purity was in service of -- the engine takes NO ambient reading to
    decide whether a verb may run -- and it is asserted here directly, twice
    and by different means, neither of them inherited:

      * structurally, `main()` resolves no cwd and calls no retired predicate;
      * behaviourally, `TheStampIsProvenanceNotADecisionInput` gets one answer
        from three different working directories, which is what "no ambient
        reading" means where anyone can observe it.

    The structural half is deliberately a source assertion. `main()` is large
    and legitimately touches `Path`, so a `co_names` scan over it would be
    noise; the two names below are exactly the two that were removed."""

    def _main_body(self) -> str:
        return ENGINE_SCRIPT.read_text(encoding="utf-8").split("\ndef main(", 1)[1]

    def test_main_resolves_no_ambient_cwd(self):
        self.assertNotIn("Path.cwd()", self._main_body())

    def test_the_engine_runs_no_git_toplevel_read(self):
        source = ENGINE_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("--show-toplevel", source)

    def test_the_retired_predicate_and_its_verb_sets_are_gone_from_a_real_engine(self):
        """Named so a re-introduction is a deliberate act with a red test to
        answer for, not a quiet re-landing.

        The positive anchor matters as much as the absences: a test that only
        asserted absence would also pass on an empty file, on a truncated read,
        or on the wrong path entirely. The anchor used to be the definition of
        `worktree_from_spine_path`, the derivation that replaced the comparison
        -- but that definition was itself deleted in #609 g2 under
        `ADMIRAL_RULING-2` N2 once its last consumer went away, so it can no
        longer stand for "this is a real engine source".

        `MUTATING_VERBS` replaces it, and is chosen for three reasons. It is the
        surviving SIBLING of the two verb sets asserted absent just above, so the
        assertion reads as one statement about the same subject: which verbs the
        engine gates, and on what. It is load-bearing -- `require_session` gates
        exactly this set -- so it cannot quietly disappear the way an unused
        definition can. And nothing in flight moves it: #609 g3 is
        `scripts/hooks/spine_rail.py`, and #610's wave threads `cwd` into
        `_run_check_command`. Neither touches the verb vocabulary."""
        source = ENGINE_SCRIPT.read_text(encoding="utf-8")
        for gone in ("def origin_worktree_refusal(", "ORIGIN_GUARDED_VERBS =",
                     "ORIGIN_EXEMPT_VERBS ="):
            self.assertNotIn(gone, source, f"{gone!r} came back")
        self.assertIn("MUTATING_VERBS = {", source)


if __name__ == "__main__":
    unittest.main()
