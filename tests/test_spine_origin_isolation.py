"""Engine-native worktree isolation: the `origin` stamp and the refusal it feeds (#315/#568).

Three things are asserted here, each with a failing side as well as a passing one:

  1. `init_work_area.instantiate_spine` stamps a top-level `origin` block when
     it writes a spine, so a spine carries its own repo reference from creation.
  2. `checklist_engine.origin_worktree_refusal` is a pure refusal-or-`None`
     predicate over that stamp: guarded verbs refuse from a cwd that is neither
     the stored worktree nor inside it, every other shape falls back to the
     pre-change behaviour, and no shape raises.
  3. `main()` reaches the predicate for real -- a guarded verb driven from a
     foreign cwd returns non-zero and leaves the spine byte-identical, while
     `current` still works from anywhere.

These tests exist because `tests/test_worktree_precondition_wiring.py` cannot
carry this: every fixture in that file builds an `origin`-LESS spine by hand,
so it is green by construction under this change and is evidence for the
fallback branch only.

**What this guard does NOT do.** It does not survive a forwarded cwd. The
engine reads its own `Path.cwd()`, and a check command authored as
`cd <origin.worktree> && ...` still satisfies it. The property gained is
coverage (every verb on every spine, not only where a check was wired into a
template), unbypassability from the spine's own text, and an expected side that
comes from the creation-time stamp rather than a literal inside a check.

Every fixture is built in a `tempfile.TemporaryDirectory()` -- never against
this worktree's own `.git` or the shared checkout.
"""

from __future__ import annotations

import importlib.util
import json
import os
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
# 2. The read side: the pure predicate
# --------------------------------------------------------------------------- #


def _spine_with_origin(worktree: str) -> dict:
    return {
        "work_id": "w1", "type": "gated", "items": [], "tasks": {},
        "origin": {"work_id": "w1", "worktree": worktree, "opened_by": "init_work_area"},
    }


class GuardedVerbScope(unittest.TestCase):
    """The guarded set is data, derived from `MUTATING_VERBS` so a verb added
    there is guarded automatically -- asserted for membership AND non-membership."""

    def setUp(self):
        self.E = _load_engine()

    def test_guarded_is_the_mutating_set_plus_claim_and_heartbeat(self):
        self.assertEqual(
            self.E.ORIGIN_GUARDED_VERBS,
            self.E.MUTATING_VERBS | {"claim", "heartbeat"},
        )
        # Membership: `heartbeat` is guarded because it WRITES; `claim` takes the
        # lease. Both are lease verbs, so neither rides in on MUTATING_VERBS.
        for verb in ("claim", "heartbeat", "start", "advance", "attest", "attach", "amend"):
            self.assertIn(verb, self.E.ORIGIN_GUARDED_VERBS)
        # Non-membership: `current` is the only genuinely read-only verb, and
        # doctrine has an invoker read a subordinate's `current` cross-tree.
        # `release` is the single recovery escape hatch -- a lease on a spine
        # whose worktree was removed at closeout must stay clearable.
        for verb in ("current", "release"):
            self.assertNotIn(verb, self.E.ORIGIN_GUARDED_VERBS)
            self.assertIn(verb, self.E.ORIGIN_EXEMPT_VERBS)

    def test_the_two_sets_partition_every_verb_the_parser_accepts(self):
        """Enumerated from the live parser, not a hand-kept list: a new verb
        must be classified deliberately rather than defaulting to unguarded."""
        import contextlib
        import io
        import re

        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
            self.E.parse_args(["--file", "x", "zzz-not-a-verb"])
        choices = re.search(r"\{([a-z,\-]+)\}", err.getvalue())
        self.assertIsNotNone(choices, f"could not read the verb list from {err.getvalue()!r}")
        verbs = set(choices.group(1).split(","))

        self.assertGreaterEqual(len(verbs), 18, f"only enumerated {sorted(verbs)}")
        self.assertEqual(verbs, self.E.ORIGIN_GUARDED_VERBS | self.E.ORIGIN_EXEMPT_VERBS)
        self.assertEqual(self.E.ORIGIN_GUARDED_VERBS & self.E.ORIGIN_EXEMPT_VERBS, set())


class OriginRefusalPredicate(unittest.TestCase):
    """`origin_worktree_refusal` refuses a guarded verb whose cwd is neither the
    stored worktree nor inside it -- and stays silent everywhere else."""

    def setUp(self):
        self.E = _load_engine()

    def test_the_worktree_root_itself_passes(self):
        spine = _spine_with_origin("/w/repo")
        self.assertIsNone(self.E.origin_worktree_refusal(spine, cwd="/w/repo", verb="claim"))

    def test_a_subdirectory_of_the_worktree_passes(self):
        """Containment, not equality: the superseded check compared
        `git rev-parse --show-toplevel`, which succeeds from any subdirectory,
        so demanding equality would be a regression."""
        spine = _spine_with_origin("/w/repo")
        for sub in ("/w/repo/scripts", "/w/repo/.agent-work/w1", "/w/repo/a/b/c"):
            self.assertIsNone(
                self.E.origin_worktree_refusal(spine, cwd=sub, verb="start"), sub
            )

    def test_a_foreign_tree_refuses_and_names_both_sides(self):
        spine = _spine_with_origin("/w/repo")
        reason = self.E.origin_worktree_refusal(spine, cwd="/w/other", verb="advance")
        self.assertIsInstance(reason, str)
        self.assertIn("/w/repo", reason)
        self.assertIn("/w/other", reason)

    def test_a_sibling_sharing_a_name_prefix_is_not_inside(self):
        """`/w/repo-2` is not inside `/w/repo`. A `startswith` comparison would
        say it is; `is_relative_to` is segment-wise and says it is not."""
        spine = _spine_with_origin("/w/repo")
        self.assertIsNotNone(self.E.origin_worktree_refusal(spine, cwd="/w/repo-2", verb="start"))
        self.assertIsNotNone(
            self.E.origin_worktree_refusal(spine, cwd="/w/repo-2/scripts", verb="start")
        )

    def test_the_parent_of_the_worktree_refuses(self):
        spine = _spine_with_origin("/w/repo")
        self.assertIsNotNone(self.E.origin_worktree_refusal(spine, cwd="/w", verb="start"))

    def test_an_exempt_verb_never_refuses_even_from_a_foreign_tree(self):
        spine = _spine_with_origin("/w/repo")
        for verb in sorted(self.E.ORIGIN_EXEMPT_VERBS):
            self.assertIsNone(
                self.E.origin_worktree_refusal(spine, cwd="/w/other", verb=verb), verb
            )

    def test_every_guarded_verb_refuses_from_a_foreign_tree(self):
        spine = _spine_with_origin("/w/repo")
        checked = 0
        for verb in sorted(self.E.ORIGIN_GUARDED_VERBS):
            self.assertIsNotNone(
                self.E.origin_worktree_refusal(spine, cwd="/w/other", verb=verb), verb
            )
            checked += 1
        self.assertEqual(checked, len(self.E.ORIGIN_GUARDED_VERBS))
        self.assertGreaterEqual(checked, 16)

    def test_it_is_pure(self):
        """No filesystem, no clock, no subprocess, no ambient cwd read: the
        impure half lives at the one call site in `main()`. Read off the
        compiled code object -- every global and attribute name the function
        actually references -- rather than off its source text, which would
        also match the docstring describing what it does not do."""
        names = set(self.E.origin_worktree_refusal.__code__.co_names)
        self.assertIn("ORIGIN_GUARDED_VERBS", names)  # the loop asserted what it looked at
        for forbidden in ("cwd", "getcwd", "subprocess", "run", "open", "exists",
                          "resolve", "read_text", "write_text", "datetime", "time",
                          "_now", "save", "load"):
            self.assertNotIn(forbidden, names, f"{forbidden} referenced by a pure predicate")

    @unittest.skipUnless(os.name == "nt", "case folding is a Windows property")
    def test_case_and_separator_folding_on_windows(self):
        """The two producers normalize differently: `spine_lifecycle` stores
        `str(Path(worktree))` (native separators) and `init_work_area` stores
        `as_posix()`. `os.path.normcase` folds both."""
        spine = _spine_with_origin("C:/w/repo")
        self.assertIsNone(
            self.E.origin_worktree_refusal(spine, cwd="C:\\W\\REPO\\scripts", verb="start")
        )


class OriginRefusalFallback(unittest.TestCase):
    """Every origin-less / malformed-origin shape takes the pre-change behaviour
    and none raises. `scripts/validate_spine.py` guards none of them, so the
    engine handles every shape itself."""

    def setUp(self):
        self.E = _load_engine()

    def test_every_malformed_shape_falls_back_without_raising(self):
        base = {"work_id": "w1", "type": "gated", "items": [], "tasks": {}}
        shapes = {
            "origin absent": {},
            "origin null": {"origin": None},
            "origin is a string": {"origin": "/w/repo"},
            "origin is a list": {"origin": ["/w/repo"]},
            "origin is empty": {"origin": {}},
            "worktree absent": {"origin": {"work_id": "w1", "opened_by": "x"}},
            "worktree empty": {"origin": {"worktree": ""}},
            "worktree is null": {"origin": {"worktree": None}},
            "worktree is a number": {"origin": {"worktree": 7}},
            "worktree is a list": {"origin": {"worktree": ["/w/repo"]}},
        }
        checked = 0
        for name, extra in shapes.items():
            with self.subTest(shape=name):
                spine = {**base, **extra}
                self.assertIsNone(
                    self.E.origin_worktree_refusal(spine, cwd="/w/somewhere-else", verb="start"),
                    f"{name} did not fall back",
                )
                checked += 1
        self.assertEqual(checked, len(shapes))
        self.assertGreaterEqual(checked, 10)

    def test_a_string_origin_would_raise_a_naive_get(self):
        """Pins why the string/list shapes are in the table: `.get` on them
        raises `AttributeError`, which `main()` does not catch."""
        with self.assertRaises(AttributeError):
            "/w/repo".get("worktree")  # noqa: B018 - the defect being guarded


# --------------------------------------------------------------------------- #
# 3. The call site: main() reaches the predicate, and refuses without writing
# --------------------------------------------------------------------------- #


class _SpineOnDisk(unittest.TestCase):
    """A real spine carrying `origin`, plus a foreign directory to stand in."""

    def setUp(self):
        self.E = _load_engine()
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.worktree = base / "wt"
        self.foreign = base / "elsewhere"
        (self.worktree / ".agent-work" / "w1").mkdir(parents=True)
        self.foreign.mkdir()
        self.spine_path = self.worktree / ".agent-work" / "w1" / "spine.json"
        self._write_spine(self.worktree.as_posix())
        self._cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self._cwd)
        self.tmp.cleanup()

    def _write_spine(self, worktree: str) -> None:
        self.spine_path.write_text(json.dumps({
            "work_id": "w1", "type": "gated", "items": ["g1"],
            "origin": {"work_id": "w1", "worktree": worktree, "opened_by": "init_work_area"},
            "tasks": {"g1": {
                "id": "g1", "title": "g1", "imperative": "do g1",
                "preconditions": [], "postconditions": [],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }},
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }, indent=2), encoding="utf-8")

    def _digest(self) -> str:
        import hashlib

        return hashlib.sha256(self.spine_path.read_bytes()).hexdigest()

    def _main_from(self, cwd: Path, argv: list[str]) -> int:
        """Run the engine IN-PROCESS from `cwd` -- the `mcp_spine_server.py`
        shape: it calls `checklist_engine.main(argv)` directly and never
        chdirs, so the guard reads that process's cwd."""
        os.chdir(cwd)
        try:
            return self.E.main(["--file", str(self.spine_path), *argv])
        finally:
            os.chdir(self._cwd)


class RefusesAGuardedVerbFromAForeignTree(_SpineOnDisk):

    def test_claim_from_a_foreign_tree_is_refused_and_writes_nothing(self):
        before = self._digest()
        code = self._main_from(self.foreign, [
            "claim", "--session-id", "s1", "--claimed-by", "commander", "--worktree", ".",
        ])
        self.assertEqual(code, 1)
        # The spine is byte-identical: the refusal must not take main()'s
        # EngineError path, which calls save() into the very tree it protects.
        self.assertEqual(self._digest(), before)
        self.assertIsNone(
            json.loads(self.spine_path.read_text(encoding="utf-8")).get("engine_session")
        )

    def test_start_from_a_foreign_tree_is_refused_and_writes_nothing(self):
        before = self._digest()
        self.assertEqual(self._main_from(self.foreign, ["start", "g1"]), 1)
        self.assertEqual(self._digest(), before)
        self.assertEqual(
            json.loads(self.spine_path.read_text(encoding="utf-8"))["tasks"]["g1"]["status"],
            "pending",
        )

    def test_no_journal_sidecar_is_written_by_a_refusal(self):
        self._main_from(self.foreign, ["start", "g1"])
        self.assertFalse((self.spine_path.parent / "spine.json.journal").exists())

    def test_the_refusal_names_both_trees_on_stderr(self):
        import contextlib
        import io

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self._main_from(self.foreign, ["start", "g1"])
        message = err.getvalue()
        self.assertIn("REFUSED:", message)
        self.assertIn(self.worktree.as_posix(), message)
        self.assertIn(str(self.foreign), message)

    def test_the_same_verb_from_the_worktree_itself_succeeds(self):
        """The pass side, so the refusal above is a signal and not a gate that
        never opens."""
        self.assertEqual(self._main_from(self.worktree, [
            "claim", "--session-id", "s1", "--claimed-by", "commander", "--worktree", ".",
        ]), 0)
        session = json.loads(self.spine_path.read_text(encoding="utf-8"))["engine_session"]
        self.assertEqual(session["status"], "active")

    def test_the_same_verb_from_a_subdirectory_of_the_worktree_succeeds(self):
        self.assertEqual(self._main_from(self.spine_path.parent, [
            "claim", "--session-id", "s1", "--claimed-by", "commander", "--worktree", ".",
        ]), 0)

    def test_an_origin_less_spine_is_still_drivable_from_anywhere(self):
        """The fallback, end to end: every spine created before the stamp
        existed looks like this and must keep working."""
        data = json.loads(self.spine_path.read_text(encoding="utf-8"))
        data.pop("origin")
        self.spine_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.assertEqual(self._main_from(self.foreign, ["start", "g1"]), 0)


class TheInProcessMcpDoorShape(_SpineOnDisk):
    """`scripts/mcp_spine_server.py` calls `checklist_engine.main(argv)`
    in-process and never chdirs, so the guard reads the MCP server process's
    cwd. Commander ruling: the guard applies to that caller with no exemption,
    no env override and no bypass. `current` stays exempt, so `spine_status`
    keeps working cross-tree -- the read path the door is most used for."""

    def test_a_guarded_verb_is_refused_in_process_from_a_foreign_cwd(self):
        before = self._digest()
        os.chdir(self.foreign)
        try:
            code = self.E.main(["--file", str(self.spine_path), "start", "g1"])
        finally:
            os.chdir(self._cwd)
        self.assertEqual(code, 1)
        self.assertEqual(self._digest(), before)

    def test_current_is_permitted_in_process_from_the_same_foreign_cwd(self):
        os.chdir(self.foreign)
        try:
            code = self.E.main(["--file", str(self.spine_path), "current"])
        finally:
            os.chdir(self._cwd)
        self.assertEqual(code, 0)

    def test_release_is_permitted_in_process_from_a_foreign_cwd(self):
        """The recovery escape hatch: a lease on a spine whose worktree was
        removed at closeout must stay clearable."""
        self.assertEqual(self._main_from(self.worktree, [
            "claim", "--session-id", "s1", "--claimed-by", "commander", "--worktree", ".",
        ]), 0)
        self.assertEqual(
            self._main_from(self.foreign, ["release", "--session-id", "s1"]), 0
        )


class TheGuardIsReachedFromExactlyOneSite(unittest.TestCase):
    """Shipped-inert is the failure mode this pins: a read side never called
    from `main()` reports green while doing nothing."""

    def test_main_calls_the_predicate_exactly_once(self):
        source = ENGINE_SCRIPT.read_text(encoding="utf-8")
        body = source.split("\ndef main(", 1)[1]
        self.assertEqual(body.count("origin_worktree_refusal("), 1)

    def test_the_call_site_is_before_dispatch(self):
        body = ENGINE_SCRIPT.read_text(encoding="utf-8").split("\ndef main(", 1)[1]
        self.assertLess(
            body.index("origin_worktree_refusal("), body.index("dispatch(cl, args")
        )


if __name__ == "__main__":
    unittest.main()
