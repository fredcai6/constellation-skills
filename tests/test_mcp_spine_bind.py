"""`spine_bind` -- binding the door to a spine that ALREADY EXISTS
(epic #567 lane A, gate `g2-implement`).

The previous lane made the door able to REBIND safely (`_bind_process_to`, one
named binder, one AST pin, late-bound telemetry, an uncached `_unbound_refusal`).
What it had was one trigger: `spine_open`, which MINTS. So a door launched with
no `SPINE_FILE` onto a spine that already exists -- an Admiral in its own
process, a crew whose launcher did not pass `--spine`, an `IMPLEMENTER_PLAN.json`
sitting beside a Commander's `spine.json` -- had no in-band way to drive it.
`spine_bind` is that trigger.

Three properties this file measures, in the order they matter:

1. **The containment root is the door's OWN checkout, not the primary
   checkout.** `_primary_checkout_for_lifecycle` resolves
   `git rev-parse --git-common-dir`, which jumps to the PRIMARY checkout from
   any worktree -- and `.worktrees/` nests INSIDE the primary checkout, so that
   root admits every sibling lane's work area. Measured in the live tree while
   this gate was implemented: the `--git-common-dir` root reached 6102 readable
   JSON objects under an `.agent-work/` carrying a derivable `work_id` (307 with
   an active lease); the door's own `--show-toplevel` checkout reached 1014 (51
   with an active lease). `spine_bind` uses the second, and confines further to
   `<that checkout>/.agent-work/`. `SiblingWorktreeIsRefusedTests` and
   `ReachDeltaTests` are what make that a fact rather than a paragraph.

2. **The session is the spine's own, never the caller's.** Derived
   `origin.work_id` when present, else the spine's top-level `work_id`, through
   `spine_lifecycle.session_id_for` -- the same function `open_work` returns
   `SPINE_SESSION` from. `TwoDoorRoundTripTests` is the load-bearing test: it is
   the only one that measures "bound by binding" and "bound at launch" being the
   same thing.

3. **Fail closed.** Nine refusals, each a pure function of
   `(args, SPINE, filesystem)`, each reachable on its own.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"
SOURCE = SERVER.read_text(encoding="utf-8")

HAS_GIT = shutil.which("git") is not None
requires_git = pytest.mark.skipif(not HAS_GIT, reason="git not available")


# --------------------------------------------------------------------------- #
# Harness
# --------------------------------------------------------------------------- #

def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "--allow-empty", "-m", "init"],
        check=True, capture_output=True,
    )


def _load_module(spine: Path | None, session: str = ""):
    """A FRESH server module bound to `spine` (or unbound when `spine` is None).

    Same pattern as `tests/test_mcp_lifecycle.py::_load_module`: a fresh module
    object per call, because "bound at import" is only testable with one, and
    because `_spine_bind` MUTATES module state -- a cached import would carry one
    test's binding into the next.

    Telemetry is redirected under the spine's own directory (or a scratch dir
    when unbound) so this suite never writes into the repo it is testing.
    """
    env_patch = {
        "SPINE_ENGINE": str(ENGINE),
        "SPINE_SESSION": session,
        "SPINE_PARENT": "unknown",
    }
    if spine is None:
        env_patch["SPINE_FILE"] = ""
    else:
        spine.parent.mkdir(parents=True, exist_ok=True)
        if not spine.exists():
            spine.write_text("{}", encoding="utf-8")
        env_patch["SPINE_FILE"] = str(spine)
        env_patch["SPINE_CALLLOG"] = str(spine.parent / "bind_calls.jsonl")
        env_patch["SPINE_START_MARKER"] = str(spine.parent / "bind_started")
        env_patch["SPINE_REJECTION_LOG"] = str(spine.parent / "bind_rejections.jsonl")
    saved = {k: os.environ.get(k) for k in env_patch}
    os.environ.update(env_patch)
    try:
        spec = importlib.util.spec_from_file_location(
            f"_bind_door_{abs(hash((str(spine), session))) % 1000000}", SERVER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _spine_payload(work_id: str, *, origin_work_id: str | None = None,
                   session: dict | None = None, top_level: bool = True) -> dict:
    """A minimally spine-shaped payload. `spine_bind` asks only three questions
    of the content -- is it a JSON object, is a `work_id` derivable, is the
    derived identity live -- so the gate plan itself is deliberately thin here:
    a fatter fixture would suggest the tool validates more than it does."""
    payload: dict = {"type": "gated", "items": ["g1"],
                     "tasks": {"g1": {"status": "pending", "title": "t"}}}
    if top_level:
        payload["work_id"] = work_id
    if origin_work_id is not None:
        payload["origin"] = {"work_id": origin_work_id}
    if session is not None:
        payload["engine_session"] = session
    return payload


def _write_spine(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def _text(result: dict) -> str:
    return "".join(b.get("text", "") for b in result["content"])


def _norm(p) -> str:
    """One comparable spelling of a path.

    `normcase` folds Windows drive-letter and separator casing; `normpath` folds
    separator direction and redundant components. On POSIX both are near no-ops, so
    this changes nothing there.
    """
    return os.path.normcase(os.path.normpath(os.fspath(p)))


def _paths_named_in(message: str) -> list[str]:
    """Every quoted token in `message`, recovered to a real path and normalized.

    The door's refusals interpolate paths with `!r`, so on Windows the message
    carries a REPR: `'C:\\\\Users\\\\runneradmin\\\\...'` with the backslashes
    doubled. A raw `str(path) in message` substring test therefore fails on Windows
    even though the refusal names exactly the right path — which is precisely what CI
    reported for nine tests in this module while the refusals themselves were
    correct. `ast.literal_eval` undoes the repr so the comparison is path-to-path
    rather than text-to-text.

    The quoted token must LOOK like an absolute path — start with a separator or a
    drive letter — because these messages also contain ordinary apostrophes
    ("checkout's work area"), and naive quote-pairing matches those instead, which
    silently yields garbage candidates like `"s work area ("` and then fails with a
    misleading message.
    """
    candidates = re.findall(
        r"""('(?:[A-Za-z]:)?[\\/][^']*'|"(?:[A-Za-z]:)?[\\/][^"]*")""", message
    )
    found: list[str] = []
    for raw in candidates:
        try:
            value = ast.literal_eval(raw)  # undoes the repr's doubled backslashes
        except (ValueError, SyntaxError):
            value = raw[1:-1]
        if isinstance(value, str) and value:
            found.append(_norm(value))
    return found


#: The stable, PATH-INDEPENDENT signature of each containment decision. Asserting
#: one of these proves WHICH rule fired, which is the boundary DECISION — a
#: different and stronger property than "the refusal named the offending path", and
#: the only one of the two that survives any path-spelling difference at all.
_RULE_SIGNATURES = {
    # rejection_class="path-escape": resolved outside `<own checkout>/.agent-work`.
    "path-escape": "may only bind a spine inside its OWN checkout's work area",
    # rejection_class="cross-checkout": lexically inside, but a different checkout.
    "cross-checkout": "sits inside a DIFFERENT checkout",
}


def assert_refusal_rule(case: unittest.TestCase, message: str, rule: str) -> None:
    """Assert the refusal came from `rule`, without reference to any path.

    Added after CI (issue #567 lane A). Nine tests in this module asserted only that
    the refusal named a path, by raw substring — which failed on Windows for a
    spelling difference while the refusals were correct. Fixing the spelling proves
    the refusal FIRES and NAMES the path. It does not by itself prove the boundary
    DECISION is computed correctly under Windows path semantics, because a wrong
    decision can still name a path correctly. This assertion covers that second
    property: `path-escape` and `cross-checkout` are two different rules reaching
    two different conclusions, and only one of them is right for a given input.
    """
    signature = _RULE_SIGNATURES[rule]
    case.assertIn(
        signature, message,
        f"expected the {rule!r} rule to fire (signature {signature!r}); "
        f"got: {message!r}",
    )
    for other, other_sig in _RULE_SIGNATURES.items():
        if other != rule:
            case.assertNotIn(
                other_sig, message,
                f"the {other!r} rule fired as well as {rule!r}; the two decisions are "
                f"mutually exclusive, so a message carrying both means the boundary "
                f"was evaluated twice with different answers",
            )


def assert_names_path(case: unittest.TestCase, message: str, expected, why: str = "") -> None:
    """Assert `message` NAMES `expected`, comparing normalized paths.

    This proves the refusal fires and names the offending path. It deliberately does
    NOT prove the confinement boundary itself computes correctly under Windows path
    semantics — `assert_refusal_class` covers the decision, path-independently.
    """
    want = _norm(expected)
    got = _paths_named_in(message)
    if want in got:
        return
    case.fail(
        f"the refusal does not name {want!r}"
        + (f" ({why})" if why else "")
        + f"\n  paths it does name: {got!r}\n  full message: {message!r}"
    )


class _BoundInARepo(unittest.TestCase):
    """Base for the in-process cases: a throwaway git repo, a door BOUND to a
    driving spine inside its `.agent-work/`.

    Bound rather than unbound on purpose. An unbound in-process door anchors its
    containment root on THIS SCRIPT's own directory, which is the developer's
    real checkout -- so every success case would have to write a spine into the
    repo under test. Binding into a tmp repo moves the anchor to `SPINE.parent`
    and makes the whole boundary disposable. The genuinely-unbound path is
    covered by `TwoDoorRoundTripTests`, which stages a checkout and spawns the
    real server, which is the only way to observe an unbound process at all.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.repo = self.dir / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.work = self.repo / ".agent-work"
        self.driving = _write_spine(
            self.work / "driving" / "spine.json", _spine_payload("driving-work"))
        self.module = _load_module(self.driving, "constellation/driving-work")
        self.boundary = self.work.resolve()

    def bind(self, spine_file, **extra):
        args = {} if spine_file is None else {"spine_file": spine_file}
        args.update(extra)
        return self.module._spine_bind(args)


# --------------------------------------------------------------------------- #
# 1. The tool exists, is routed, and is reachable with nothing bound.
# --------------------------------------------------------------------------- #

class SpineBindIsWiredTests(unittest.TestCase):
    """A tool that is declared but not routed, or routed but refused by the
    uniform unbound gate, is shipped-inert: it passes review, passes tests, and
    nothing reaches it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.module = _load_module(Path(self.tmp.name) / "w" / "spine.json", "s")

    def test_spine_bind_is_declared_on_the_tool_surface(self):
        names = [t["name"] for t in self.module.TOOLS]
        self.assertIn("spine_bind", names)
        self.assertIn("spine_bind", self.module.LIFECYCLE_TOOL_NAMES,
                      "spine_bind must be a LIFECYCLE tool -- it never calls run_engine, so "
                      "routing it through call_tool would put it under a pin written for "
                      "engine pass-throughs")

    def test_its_one_argument_is_named_spine_file(self):
        """Not `work_file`, not `plan_path`. Renaming it would slip past
        `tests/test_mcp_identity.py`'s identity-argument pin, which is the
        spelling game `_identity_violation`'s docstring records losing six
        times -- turned by the author against his own test. The honest diff
        names it `spine_file` and amends IDENTITY_TRADE.md."""
        tool = next(t for t in self.module.TOOLS if t["name"] == "spine_bind")
        props = tool["inputSchema"]["properties"]
        self.assertEqual(["spine_file"], list(props))
        self.assertEqual(["spine_file"], tool["inputSchema"]["required"])
        self.assertFalse(tool["inputSchema"]["additionalProperties"])

    def test_the_description_names_the_isolation_property(self):
        """`decision:isolation-not-fencing`: the replacement property is named
        where the caller reads it, not only in a design document."""
        tool = next(t for t in self.module.TOOLS if t["name"] == "spine_bind")
        self.assertIn("one checkout", tool["description"].lower())

    def test_it_is_exempt_from_the_uniform_unbound_gate(self):
        """`main()` refuses the WHOLE surface when nothing is bound. Without
        this entry, `spine_bind` is refused before its dispatch is ever reached
        -- a bind tool that only works on an already-bound door."""
        self.assertIn("spine_bind", self.module.BINDS_WITHOUT_A_BOUND_SPINE)

    def test_call_lifecycle_tool_routes_it(self):
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "call_lifecycle_tool")
        segment = ast.get_source_segment(SOURCE, fn)
        self.assertIn("_spine_bind(args)", segment)

    def test_the_dispatch_calls_the_one_binder_and_assigns_nothing_itself(self):
        """`_bind_process_to` stays the only identity mutator. The module-wide
        AST pin (`tests/test_mcp_lifecycle.py::OneBinderPinTests`) enforces this
        globally; this is the local, readable half of the same claim."""
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_spine_bind")
        segment = ast.get_source_segment(SOURCE, fn)
        self.assertIn("_bind_process_to(", segment)
        assigned = set()
        for node in ast.walk(fn):
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                targets = [node.target]
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                targets = [node.target]
            for t in targets:
                assigned |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
        self.assertEqual(set(), assigned & {"SPINE", "SESSION"},
                         "_spine_bind assigns an identity global itself -- route it through "
                         "_bind_process_to instead")


# --------------------------------------------------------------------------- #
# 2. The reach delta: the containment root, and what it refuses.
# --------------------------------------------------------------------------- #

class ReachDeltaTests(_BoundInARepo):
    """`decision:isolation-not-fencing` requires the reach delta be measured,
    not asserted. A green suite is not a substitute: these tests fail if the
    confinement is deleted, which is what makes them evidence."""

    def test_a_spine_outside_the_boundary_is_refused_and_the_refusal_names_it(self):
        outside = _write_spine(self.dir / "elsewhere" / "spine.json", _spine_payload("other-work"))
        result = self.bind(str(outside))
        self.assertTrue(result["isError"])
        text = _text(result)
        assert_names_path(self, text, self.boundary,
                      "the refusal does not NAME the boundary it enforced")
        assert_names_path(self, text, outside.resolve(),
                      "the refusal does not name what the path resolved to")
        self.assertIn("outside", text)

    def test_the_refusal_offers_the_cli_escape_hatch(self):
        """Every containment refusal in this module ends the same way, so a
        caller meets one consistent way out rather than three."""
        outside = _write_spine(self.dir / "elsewhere" / "spine.json", _spine_payload("other-work"))
        self.assertIn("CLI", _text(self.bind(str(outside))))

    def test_the_binding_did_not_move(self):
        """A refusal that refused and bound anyway is worse than no refusal."""
        outside = _write_spine(self.dir / "elsewhere" / "spine.json", _spine_payload("other-work"))
        self.bind(str(outside))
        self.assertEqual(self.driving.resolve(), self.module.SPINE)
        self.assertEqual("constellation/driving-work", self.module.SESSION)
        # `_bind_process_to` mirrors both roots into `os.environ`, so a refusal
        # that leaked halfway through would show up there even if the globals
        # looked clean. (The loader restores the environment after import, so
        # what is asserted is the ABSENCE of the escape, not the bound value.)
        self.assertNotEqual(str(outside.resolve()), os.environ.get("SPINE_FILE"))
        self.assertNotEqual("constellation/other-work", os.environ.get("SPINE_SESSION"))

    def test_the_boundary_is_the_work_area_not_the_whole_checkout(self):
        """A spine-shaped file loose in the checkout but OUTSIDE `.agent-work/`
        is refused. This is the difference between "my checkout" and "my
        checkout's work area", and it is the narrower of the two."""
        loose = _write_spine(self.repo / "notes" / "spine.json", _spine_payload("loose-work"))
        result = self.bind(str(loose))
        self.assertTrue(result["isError"])
        assert_names_path(self, _text(result), self.boundary)
        assert_refusal_rule(self, _text(result), "path-escape")

    def test_the_confinement_predicate_is_resolve_confined_reused(self):
        """Reuse, not a second differently-shaped check -- the failure
        `_identity_violation`'s docstring records six times over."""
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_spine_bind")
        calls = {n.func.id for n in ast.walk(fn)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertIn("_resolve_confined", calls)

    def test_a_relative_path_cannot_traverse_out_of_the_boundary(self):
        outside = _write_spine(self.dir / "elsewhere" / "spine.json", _spine_payload("other-work"))
        traversal = str(self.work / ".." / ".." / "elsewhere" / "spine.json")
        result = self.bind(traversal)
        self.assertTrue(result["isError"], "a `..` traversal escaped the boundary")
        assert_names_path(self, _text(result), outside.resolve(),
                      "the refusal reports the pre-resolution spelling, not what it resolves to")

    def test_the_root_is_show_toplevel_never_git_common_dir(self):
        """The one flag that is the whole difference between "my checkout" and
        "the primary checkout and every worktree nested under it". Text-level,
        because the two differ only in a string and a wrong one is invisible in
        behaviour until a sibling lane's spine is bindable."""
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_own_checkout_for_binding")
        # The CODE, not the docstring. That helper's docstring names
        # `--git-common-dir` and `_primary_checkout_for_lifecycle` on purpose --
        # explaining what it must NOT do is exactly the note a future editor
        # needs, and a text pin that punished the explanation would delete it.
        body = [n for n in fn.body if not (isinstance(n, ast.Expr)
                                           and isinstance(n.value, ast.Constant))]
        code = "\n".join(ast.unparse(n) for n in body)
        self.assertIn("--show-toplevel", ast.unparse(ast.parse(SOURCE)),
                      "no --show-toplevel anywhere in the module")
        self.assertNotIn("--git-common-dir", code)
        self.assertNotIn("_primary_checkout_for_lifecycle", code)

    def test_the_root_resolves_to_this_doors_own_checkout(self):
        self.assertEqual(self.repo.resolve(), self.module._own_checkout_for_binding().resolve())


@requires_git
class SiblingWorktreeIsRefusedTests(_BoundInARepo):
    """`DESIGN_CONVERGENCE.md` said, 18 lines apart, both "including a sibling
    worktree's live spine may become the spine this process drives" and "what an
    agent still cannot do: drive a spine in another checkout." A linked worktree
    IS another checkout, so the second was false under the designed root. These
    tests are what make it true."""

    def _sibling_worktree(self) -> Path:
        sib = self.repo / ".worktrees" / "sibling"
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "-q",
                        "-b", "sibling-branch", str(sib)], check=True, capture_output=True)
        return sib

    def test_a_live_spine_in_a_sibling_worktree_is_refused(self):
        sib = self._sibling_worktree()
        theirs = _write_spine(
            sib / ".agent-work" / "their-work" / "spine.json",
            _spine_payload("their-work", session={
                "session_id": "constellation/their-work", "status": "active",
                "last_heartbeat": "2999-01-01T00:00:00+00:00"}))
        result = self.bind(str(theirs))
        self.assertTrue(result["isError"],
                        "a sibling worktree's LIVE spine was bindable -- `.worktrees/` nests "
                        "inside the checkout, so a root that stops at the checkout admits "
                        "every other lane")
        assert_names_path(self, _text(result), self.boundary)
        assert_refusal_rule(self, _text(result), "path-escape")

    def test_a_nested_checkout_inside_the_work_area_is_refused_by_the_cross_checkout_rule(self):
        """Lexical containment alone is not enough: a checkout can be NESTED
        under `.agent-work/`, at which point a path inside the boundary is still
        in another repository. The candidate's own `--show-toplevel` is asked and
        compared, which is what makes the isolation claim true rather than
        aspirational."""
        nested = self.work / "nested-repo"
        nested.mkdir(parents=True)
        _init_repo(nested)
        theirs = _write_spine(nested / ".agent-work" / "n" / "spine.json", _spine_payload("n-work"))
        result = self.bind(str(theirs))
        self.assertTrue(result["isError"],
                        "a spine in a checkout NESTED inside the work area was bindable -- "
                        "lexical containment passed and nothing asked which repo it is in")
        text = _text(result)
        # The DECISION, path-independently: the cross-checkout rule must be the one
        # that fired, not the plain containment rule -- this path IS lexically inside
        # the boundary, so `path-escape` firing here would be the wrong answer
        # reached for the wrong reason.
        assert_refusal_rule(self, text, "cross-checkout")
        assert_names_path(self, text, self.repo.resolve(),
                      "the refusal does not name the checkout this door belongs to")


@requires_git
class TheRootMustBeTheDoorsOwnWorktreeTests(unittest.TestCase):
    """**The discriminating topology, and the only one that separates the two
    roots.** Everything else in this file would pass with either.

    `--git-common-dir` and `--show-toplevel` return the SAME directory when asked
    from a PRIMARY checkout. They part company only when the asking door is inside
    a LINKED WORKTREE -- and that is the production case, because `.mcp.json`
    launches `scripts/mcp_spine_server.py` relative to the client's own cwd, so a
    crew working in `.worktrees/<lane>` runs that worktree's copy of the door.

    This class was written because a mutation experiment caught the gap. Swapping
    `_own_checkout_for_binding()` for `_primary_checkout_for_lifecycle()` -- the
    root the design document originally named, and the entire defect this gate
    exists to avoid -- left the rest of this file GREEN, because every other
    fixture binds a door inside a primary checkout where the two roots agree. A
    negative test that cannot tell the wrong root from the right one is not
    evidence that reach did not widen.

    Topology, all inside one tmp repo:

        repo/                              <- primary checkout
          .agent-work/primary-work/        <- ANOTHER lane's work, in the primary
          .worktrees/lane-a/               <- THIS door's worktree
            .agent-work/mine/spine.json    <- bound
            .agent-work/other/spine.json   <- legitimately bindable
          .worktrees/lane-b/
            .agent-work/theirs/spine.json  <- a sibling lane's work

    Under `--git-common-dir` the boundary is `repo/.agent-work/`, which admits
    `primary-work`. Under `--show-toplevel` it is
    `repo/.worktrees/lane-a/.agent-work/`, which does not.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.repo = self.dir / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self.lane_a = self._worktree("lane-a")
        self.lane_b = self._worktree("lane-b")
        self.mine = _write_spine(self.lane_a / ".agent-work" / "mine" / "spine.json",
                                 _spine_payload("mine-work"))
        self.module = _load_module(self.mine, "constellation/mine-work")

    def _worktree(self, name: str) -> Path:
        path = self.repo / ".worktrees" / name
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "-q",
                        "-b", name, str(path)], check=True, capture_output=True)
        return path

    def bind(self, path: Path) -> dict:
        return self.module._spine_bind({"spine_file": str(path)})

    def test_the_two_roots_genuinely_disagree_here(self):
        """The premise. If this fails, every assertion below is vacuous -- they
        would be measuring a boundary that happens to be the same either way."""
        own = self.module._own_checkout_for_binding().resolve()
        designed = self.module._primary_checkout_for_lifecycle().resolve()
        self.assertEqual(self.lane_a.resolve(), own)
        self.assertEqual(self.repo.resolve(), designed)
        self.assertNotEqual(own, designed,
                            "the fixture does not reproduce the linked-worktree topology, so "
                            "it cannot tell the right root from the wrong one")

    def test_the_doors_own_worktree_work_area_is_bindable(self):
        """The non-vacuity control, first. A tool that refused everything would
        satisfy every other assertion in this class while being useless."""
        other = _write_spine(self.lane_a / ".agent-work" / "other" / "spine.json",
                             _spine_payload("other-work"))
        result = self.bind(other)
        self.assertFalse(result["isError"], _text(result))
        self.assertEqual(other.resolve(), self.module.SPINE)
        self.assertEqual("constellation/other-work", self.module.SESSION)

    def test_a_spine_in_the_PRIMARY_checkout_is_refused(self):
        """THE assertion. This path is INSIDE the boundary the design document's
        root would have drawn, and outside the one this door draws. A door in a
        linked worktree has no business driving the primary checkout's work."""
        theirs = _write_spine(self.repo / ".agent-work" / "primary-work" / "spine.json",
                              _spine_payload("primary-work"))
        result = self.bind(theirs)
        self.assertTrue(
            result["isError"],
            "a spine in the PRIMARY checkout's work area was bindable from a door inside a "
            "linked worktree -- that is `--git-common-dir` behaviour, and it admits every "
            "lane in the repository")
        text = _text(result)
        assert_names_path(self, text, (self.lane_a / ".agent-work").resolve(),
                      "the refusal names a boundary other than this door's own worktree")
        self.assertNotIn(str((self.repo / ".agent-work").resolve()) + "'", text)
        self.assertEqual(self.mine.resolve(), self.module.SPINE, "the binding moved anyway")

    def test_a_spine_in_a_SIBLING_worktree_is_refused(self):
        theirs = _write_spine(self.lane_b / ".agent-work" / "theirs" / "spine.json",
                              _spine_payload("theirs-work"))
        result = self.bind(theirs)
        self.assertTrue(result["isError"],
                        "a sibling lane's spine was bindable from this door")
        assert_names_path(self, _text(result), (self.lane_a / ".agent-work").resolve())
        self.assertEqual(self.mine.resolve(), self.module.SPINE)

    def test_the_measured_reach_is_the_narrow_set_not_the_wide_one(self):
        """The reach delta as a COUNT, on a topology small enough to enumerate by
        hand -- the same measurement the live tree gives as 1014 against 6102,
        reduced to 3 against 1 so it can be asserted rather than cited."""
        wide = {
            _write_spine(self.repo / ".agent-work" / "primary-work" / "spine.json",
                         _spine_payload("primary-work")),
            _write_spine(self.lane_b / ".agent-work" / "theirs" / "spine.json",
                         _spine_payload("theirs-work")),
            _write_spine(self.lane_a / ".agent-work" / "other" / "spine.json",
                         _spine_payload("other-work")),
        }
        bindable = set()
        for candidate in sorted(wide):
            # A fresh module per candidate: a successful bind MOVES the boundary
            # anchor to the new spine's directory, so reusing one module would
            # measure a boundary that the previous iteration changed.
            module = _load_module(self.mine, "constellation/mine-work")
            if not module._spine_bind({"spine_file": str(candidate)})["isError"]:
                bindable.add(candidate)
        self.assertEqual(
            {self.lane_a / ".agent-work" / "other" / "spine.json"}, bindable,
            f"reach is {sorted(str(p) for p in bindable)}; exactly one of these three "
            f"spines is in this door's own worktree's work area and the other two are "
            f"other lanes' work")


@requires_git
class ASymlinkCannotHideAnotherCheckoutTests(unittest.TestCase):
    """**The gate's reviewer defeated R6 with a symlink, and this class is what
    closes it.**

    R4 (`_resolve_confined`) computes containment on `p.resolve()`, so symlinks
    ARE followed there -- but it returns the candidate UNRESOLVED. R6 then asked
    git which checkout `candidate.parent` belongs to, and for a link at
    `<our work area>/link.json` that parent is our OWN work area, which trivially
    matches. So a symlink sitting inside the door's own `.agent-work/` and
    pointing at a spine in a DIFFERENT checkout passed both guards: R4 saw a
    resolved target inside the boundary, R6 saw our own directory. The reviewer
    bound a nested linked worktree's spine and a wholly separate repository's
    spine exactly that way, and `_bind_process_to` then resolved the link, so the
    door really did end up driving the other checkout's spine.

    `_identity_violation`'s own docstring records six guards "each defeated by a
    shape it had not enumerated" and concludes "enumerating spellings is the
    defect". R6 enumerated one spelling of "which checkout is this path in". This
    class asserts the OTHER spelling, and does it on genuine topologies -- a real
    `git worktree add` nested under the work area and a real `git init` beside it
    -- because that is the only kind of fixture that can see the bug at all:

        repo/                                     <- primary checkout
          .worktrees/lane-a/                      <- THIS door's checkout
            .agent-work/mine/spine.json           <- bound
            .agent-work/other/spine.json          <- legitimately bindable
            .agent-work/nested/                   <- `git worktree add`, NESTED
              .agent-work/n/spine.json
            .agent-work/alien-repo/               <- `git init`, unrelated repo
              .agent-work/a/spine.json
            .agent-work/link-nested.json  ->  nested/.agent-work/n/spine.json
            .agent-work/link-alien.json   ->  alien-repo/.agent-work/a/spine.json
            .agent-work/link-sibling.json ->  ../lane-b/.agent-work/theirs/spine.json
          .worktrees/lane-b/
            .agent-work/theirs/spine.json         <- a sibling lane's work

    Every link's own parent directory is inside this door's work area, which is
    the whole point: the defeated guard asked about that parent.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir(parents=True)
        _init_repo(self.repo)
        self.lane_a = self._worktree("lane-a", self.repo / ".worktrees" / "lane-a")
        self.lane_b = self._worktree("lane-b", self.repo / ".worktrees" / "lane-b")
        self.work = self.lane_a / ".agent-work"
        self.mine = _write_spine(self.work / "mine" / "spine.json", _spine_payload("mine-work"))

        # A linked worktree of the SAME repository, nested inside our work area.
        self.nested = self._worktree("nested-branch", self.work / "nested")
        self.nested_spine = _write_spine(
            self.nested / ".agent-work" / "n" / "spine.json", _spine_payload("nested-work"))

        # A wholly unrelated repository, also nested inside our work area.
        self.alien = self.work / "alien-repo"
        _init_repo(self.alien)
        self.alien_spine = _write_spine(
            self.alien / ".agent-work" / "a" / "spine.json", _spine_payload("alien-work"))

        # A sibling lane's work, outside our checkout entirely.
        self.theirs = _write_spine(
            self.lane_b / ".agent-work" / "theirs" / "spine.json", _spine_payload("theirs-work"))

        self.link_nested = self._link("link-nested.json", self.nested_spine)
        self.link_alien = self._link("link-alien.json", self.alien_spine)
        self.link_sibling = self._link("link-sibling.json", self.theirs)

        self.module = _load_module(self.mine, "constellation/mine-work")

    def _worktree(self, branch: str, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "-q",
                        "-b", branch, str(path)], check=True, capture_output=True)
        return path

    def _link(self, name: str, target: Path) -> Path:
        link = self.work / name
        link.symlink_to(target)
        return link

    def bind(self, path: Path) -> dict:
        return self.module._spine_bind({"spine_file": str(path)})

    def _classes(self) -> list[str]:
        log = self.module._rejectionlog()
        if not log.exists():
            return []
        return [json.loads(x)["class"] for x in log.read_text(encoding="utf-8").splitlines()
                if x.strip() and json.loads(x)["tool"] == "spine_bind"]

    def test_the_fixture_is_the_discriminating_topology(self):
        """The premise. If any of this fails the assertions below are vacuous:
        they would be measuring a symlink that does not actually cross a checkout
        boundary, or a link whose parent is not our own work area."""
        own = self.module._own_checkout_for_binding().resolve()
        self.assertEqual(self.lane_a.resolve(), own)
        self.assertEqual(
            self.nested.resolve(),
            self.module._checkout_containing(self.nested_spine.parent).resolve(),
            "the nested `git worktree` does not answer with itself, so it is not a "
            "different checkout and there is nothing here to escape")
        self.assertEqual(
            self.alien.resolve(),
            self.module._checkout_containing(self.alien_spine.parent).resolve())
        for link in (self.link_nested, self.link_alien, self.link_sibling):
            self.assertTrue(link.is_symlink(), f"{link} is not a symlink")
            self.assertEqual(
                self.work.resolve(), link.parent.resolve(),
                "the link's own parent is not this door's work area -- which is the "
                "directory the defeated guard asked git about")

    def test_the_doors_own_work_area_is_still_bindable(self):
        """The non-vacuity control, first. A guard that refused everything would
        satisfy every assertion below while making the tool useless."""
        other = _write_spine(self.work / "other" / "spine.json", _spine_payload("other-work"))
        result = self.bind(other)
        self.assertFalse(result["isError"], _text(result))
        self.assertEqual(other.resolve(), self.module.SPINE)

    def test_a_symlink_to_the_bound_spine_is_still_an_idempotent_no_op(self):
        """The second non-vacuity control, and the one that proves resolving in R6
        did not break R0: a link is a spelling of the bound spine, not a rebind."""
        link = self._link("link-mine.json", self.mine)
        result = self.bind(link)
        self.assertFalse(result["isError"], _text(result))
        self.assertTrue(json.loads(_text(result))["already_bound"])

    def test_a_nested_checkout_via_the_DIRECT_path_is_refused(self):
        """The spelling R6 already caught, kept as the paired half: the direct and
        symlinked spellings of ONE path must get the SAME answer."""
        result = self.bind(self.nested_spine)
        self.assertTrue(result["isError"], _text(result))
        self.assertEqual(["cross-checkout"], self._classes())

    def test_a_nested_checkout_reached_THROUGH_A_SYMLINK_is_refused(self):
        """THE assertion. The link is inside our work area, so R4 passes and the
        UNRESOLVED parent is our own checkout -- the exact shape that bound
        another checkout's spine before R6 learned to resolve first."""
        result = self.bind(self.link_nested)
        self.assertTrue(
            result["isError"],
            "a spine in a NESTED checkout was bound through a symlink whose parent is "
            "this door's own work area -- R4 resolved and saw a path inside the boundary, "
            "and R6 asked git about the link's parent rather than the target's")
        self.assertEqual(
            ["cross-checkout"], self._classes(),
            "the symlink was refused, but not BY the cross-checkout guard -- the direct "
            "and symlinked spellings of one path must be refused for the same reason")
        self.assertEqual(self.mine.resolve(), self.module.SPINE, "the binding moved anyway")
        self.assertEqual("constellation/mine-work", self.module.SESSION)

    def test_an_UNRELATED_REPOSITORY_reached_through_a_symlink_is_refused(self):
        """The same escape into a repository this door knows nothing about, under
        an identity that repository dictates. `IDENTITY_TRADE.md` §7's "what an
        agent still cannot do: drive a spine in another checkout" is this
        sentence, and it was false."""
        result = self.bind(self.link_alien)
        self.assertTrue(result["isError"],
                        "a wholly separate repository's spine was bound through a symlink")
        self.assertEqual(["cross-checkout"], self._classes())
        self.assertEqual(self.mine.resolve(), self.module.SPINE)

    def test_a_symlink_to_a_SIBLING_worktree_is_refused(self):
        """This one is refused by R4 rather than R6, because the resolved target is
        outside the boundary lexically too -- asserted so the two guards' division
        of labour is recorded rather than assumed."""
        result = self.bind(self.link_sibling)
        self.assertTrue(result["isError"], "a sibling lane's spine was bound through a symlink")
        self.assertEqual(["path-escape"], self._classes())
        self.assertEqual(self.mine.resolve(), self.module.SPINE)

    def test_the_refusal_names_the_RESOLVED_target_not_the_link(self):
        """A refusal that named the link would tell an agent its own work area is
        "a different checkout", which is false and unactionable. R4's symlink
        refusals already name the resolved target; R6 matches them."""
        result = self.bind(self.link_nested)
        # Asserted first: a SUCCESS payload also names all three of these paths,
        # so without this the assertions below would pass on the escape itself.
        self.assertTrue(result["isError"], _text(result))
        text = _text(result)
        assert_names_path(self, text, self.nested_spine.resolve(),
                      "the refusal does not name the spine that would actually be driven")
        assert_names_path(self, text, self.nested.resolve(),
                      "the refusal does not name the checkout the target belongs to")
        assert_names_path(self, text, self.lane_a.resolve(),
                      "the refusal does not name this door's own checkout")

    def test_the_reach_including_symlinked_spellings_is_still_one_spine(self):
        """The reach delta re-measured with the symlinked spellings in the
        candidate set -- a count on a topology small enough to enumerate by hand.
        Exactly one of these six is in this door's own checkout's work area."""
        legit = _write_spine(self.work / "other" / "spine.json", _spine_payload("other-work"))
        candidates = [legit, self.nested_spine, self.alien_spine, self.theirs,
                      self.link_nested, self.link_alien, self.link_sibling]
        bindable = set()
        for candidate in candidates:
            # A fresh module per candidate: a successful bind MOVES the boundary
            # anchor to the new spine's directory.
            module = _load_module(self.mine, "constellation/mine-work")
            if not module._spine_bind({"spine_file": str(candidate)})["isError"]:
                bindable.add(candidate.resolve())
        self.assertEqual(
            {legit.resolve()}, bindable,
            f"reach is {sorted(str(p) for p in bindable)}; only this door's own work area "
            f"is in it, by any spelling")


# --------------------------------------------------------------------------- #
# 3. The remaining refusals, each reachable on its own.
# --------------------------------------------------------------------------- #

class RefusalSetTests(_BoundInARepo):

    def test_a_missing_argument_refuses_by_name(self):
        result = self.bind(None)
        self.assertTrue(result["isError"])
        self.assertIn("spine_file", _text(result))
        self.assertIn("missing required argument", _text(result))

    def test_a_non_string_argument_refuses(self):
        # A plain loop, deliberately not `subTest`: under pytest's unittest
        # integration an exception raised inside a `subTest` block can be
        # recorded as a subtest failure while the OUTER test still reports
        # PASSED -- measured on this very file before `_spine_bind` existed, when
        # four such tests reported green against a function that was not there.
        # A test that can pass while its body raises is not evidence.
        for bad in (17, {"path": "x"}, ["x"], True):
            result = self.bind(bad)
            self.assertTrue(result["isError"], f"{bad!r} was accepted")
            self.assertIn("non-empty path", _text(result), f"for {bad!r}")

    def test_an_empty_or_whitespace_argument_refuses(self):
        for bad in ("", "   ", "\t\n"):
            result = self.bind(bad)
            self.assertTrue(result["isError"], f"{bad!r} was accepted")

    def test_a_path_that_will_not_RESOLVE_refuses_instead_of_raising(self):
        """A NUL byte makes `Path(raw).resolve()` raise `ValueError: embedded null
        byte`, and `main()`'s lifecycle branch catches only `KeyError` -- so before
        this guard the exception unwound out of `main()` and killed the door,
        taking all twelve tools with it. `spine_bind` is the first lifecycle tool
        to take a caller-supplied filesystem path AND is reachable with nothing
        bound, so it is reachable at the moment an agent has no other way in.
        "Fail closed" means refuse, not die.

        `NulByteDoesNotKillTheDoorTests` is the half that proves the process
        survives; this is the half that proves the refusal is a refusal, in the
        module's own voice, with a `rejection_class` so it lands in the log."""
        log = self.module._rejectionlog()
        result = self.bind(str(self.work / "x\x00evil" / "spine.json"))
        self.assertTrue(result["isError"], "a NUL byte in spine_file was accepted")
        self.assertIn("spine_file", _text(result))
        classes = [json.loads(x)["class"] for x in log.read_text(encoding="utf-8").splitlines()
                   if x.strip()]
        self.assertEqual(["bad-argument-type"], classes,
                         f"the unresolvable path did not land in the rejection log as "
                         f"bad-argument-type: {classes}")
        self.assertEqual(self.driving.resolve(), self.module.SPINE, "the binding moved")

    def test_the_unresolvable_path_guard_covers_the_UNBOUND_door_too(self):
        """R0 -- the only earlier resolve -- runs only when something is bound, so
        a guard placed after it would leave the unbound door still dying. The
        unbound door is the one `spine_bind` exists for."""
        module = _load_module(None)
        result = module._spine_bind({"spine_file": "/tmp/x\x00evil/spine.json"})
        self.assertTrue(result["isError"])
        self.assertIsNone(module.SPINE, "an unbound door bound something")

    def test_a_directory_is_refused_with_the_doors_own_wording(self):
        target = self.work / "a-directory"
        target.mkdir(parents=True)
        result = self.bind(str(target))
        self.assertTrue(result["isError"])
        self.assertIn("that path is a directory, not a spine file", _text(result))

    def test_a_missing_file_is_refused_with_the_doors_own_wording(self):
        result = self.bind(str(self.work / "nope" / "spine.json"))
        self.assertTrue(result["isError"])
        self.assertIn("no file exists at that path", _text(result))

    def test_the_usability_ladder_is_the_doors_one_ladder_not_a_second_one(self):
        """`_unbound_refusal`'s five-input ladder is EXTRACTED and shared, so the
        `why` clauses a caller meets are byte-identical whichever refusal
        produced them. A second ladder would drift in wording, which is how a
        caller learns to distrust the words."""
        self.assertIsNone(self.module._unusable_spine_reason(self.driving))
        self.assertEqual("no file exists at that path",
                         self.module._unusable_spine_reason(self.work / "nope.json"))
        self.assertEqual("that path is a directory, not a spine file",
                         self.module._unusable_spine_reason(self.work))
        tree = ast.parse(SOURCE)
        for caller in ("_unbound_refusal", "_spine_bind"):
            fn = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == caller)
            self.assertIn("_unusable_spine_reason(", ast.get_source_segment(SOURCE, fn),
                          f"{caller} does not use the shared ladder")

    def test_a_file_that_is_not_json_is_refused(self):
        target = self.work / "junk" / "spine.json"
        target.parent.mkdir(parents=True)
        target.write_text("not json at all", encoding="utf-8")
        result = self.bind(str(target))
        self.assertTrue(result["isError"])
        self.assertIn("does not hold a JSON object", _text(result))

    def test_a_json_file_that_is_not_an_object_is_refused(self):
        for payload in ("[]", '"a string"', "17", "null"):
            target = self.work / "notobj" / "spine.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payload, encoding="utf-8")
            result = self.bind(str(target))
            self.assertTrue(result["isError"], f"{payload} was accepted as a spine")
            self.assertIn("does not hold a JSON object", _text(result), f"for {payload}")

    def test_a_spine_with_neither_work_id_is_refused_and_says_why_it_matters(self):
        """The fail-closed posture the census says is currently never taken:
        0 of 60 live spine-shaped files lack both fields. It is still the right
        refusal, because a door bound with no session cannot `claim`, and a door
        that cannot claim is not a bound door."""
        target = _write_spine(self.work / "anon" / "spine.json",
                              _spine_payload("x", top_level=False))
        result = self.bind(str(target))
        self.assertTrue(result["isError"])
        text = _text(result)
        self.assertIn("work_id", text)
        self.assertIn("claim", text,
                      "the refusal does not explain that a door bound with no session "
                      "cannot claim -- which is the reason it refuses at all")

    def test_an_empty_work_id_is_the_same_class_as_a_missing_one(self):
        for payload in ({"work_id": ""}, {"work_id": "  "}, {"work_id": None},
                        {"origin": {"work_id": ""}}, {"origin": "not-a-dict"}):
            body = _spine_payload("x", top_level=False)
            body.update(payload)
            target = _write_spine(self.work / "anon2" / "spine.json", body)
            self.assertTrue(self.bind(str(target))["isError"], f"{payload} was accepted")

    def test_every_refusal_lands_in_the_rejection_log(self):
        """Each refusal returns through `_tool_error` with a `rejection_class`,
        so the door's own rejections are durably traceable -- the only trace
        that path has, because nothing reaches the engine's refusal counter."""
        # `_rejectionlog()` is late-bound and env-override-first, and the loader
        # restores the environment after import -- so the live destination is the
        # default one, beside the bound spine. Asked of the module rather than
        # reconstructed, so this cannot drift from where the door actually writes.
        log = self.module._rejectionlog()
        self.bind(None)
        self.bind(17)
        # Outside the boundary. Note the ORDER this proves: containment is asked
        # before existence, so a path outside is refused as an escape whether or
        # not anything is there -- a boundary that first told a caller whether a
        # file exists outside it would be an existence oracle.
        self.bind(str(self.dir / "elsewhere" / "spine.json"))
        self.bind(str(self.work / "nothing-here.json"))
        junk = self.work / "junk.json"
        junk.write_text("{", encoding="utf-8")
        self.bind(str(junk))
        self.bind(str(_write_spine(self.work / "anon" / "spine.json",
                                   _spine_payload("x", top_level=False))))
        lines = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()]
        classes = [r["class"] for r in lines if r["tool"] == "spine_bind"]
        self.assertEqual(
            ["missing-required-argument", "bad-argument-type", "path-escape",
             "no-spine-there", "not-a-spine", "no-derivable-identity"], classes,
            f"unexpected rejection classes: {classes}")
        for record in lines:
            self.assertTrue(record["detail"].strip(), "a rejection was logged with no detail")
            self.assertTrue(record["ts"], "a rejection was logged with no timestamp")


class IdentityHeldRefusalTests(_BoundInARepo):
    """The "two agents on one lease" failure `IDENTITY_TRADE.md` §3 names,
    closed rather than inherited: two processes that bind one spine derive the
    same session string, so the second binder is refused while the first is
    demonstrably live."""

    def _candidate(self, session: dict | None) -> Path:
        return _write_spine(self.work / "theirs" / "spine.json",
                            _spine_payload("theirs-work", session=session))

    def test_a_live_lease_under_the_derived_identity_refuses(self):
        target = self._candidate({"session_id": "constellation/theirs-work",
                                  "status": "active",
                                  "last_heartbeat": "2999-01-01T00:00:00+00:00"})
        result = self.bind(str(target))
        self.assertTrue(result["isError"])
        text = _text(result)
        self.assertIn("constellation/theirs-work", text)
        self.assertIn("release", text, "the refusal does not name the remedy")
        self.assertEqual(self.driving.resolve(), self.module.SPINE)

    def test_a_stale_lease_does_not_block_a_genuine_respawn(self):
        """`run_crew.assignment_session_name`'s docstring records that a respawn
        MUST reproduce its predecessor's session string. A genuine respawn
        follows a DEAD predecessor, whose lease is stale -- so staleness is what
        keeps the legitimate case open."""
        target = self._candidate({"session_id": "constellation/theirs-work",
                                  "status": "active",
                                  "last_heartbeat": "2000-01-01T00:00:00+00:00"})
        result = self.bind(str(target))
        self.assertFalse(result["isError"], _text(result))
        self.assertEqual(target.resolve(), self.module.SPINE)

    def test_a_released_lease_does_not_block(self):
        target = self._candidate({"session_id": "constellation/theirs-work",
                                  "status": "released",
                                  "last_heartbeat": "2999-01-01T00:00:00+00:00"})
        self.assertFalse(self.bind(str(target))["isError"])

    def test_a_live_lease_under_a_DIFFERENT_identity_does_not_block(self):
        """Scoped to the identity this bind would ASSUME, not to any active
        lease at all. Another session's lease is not this door's to collide
        with, and refusing on it would make an unrelated agent's lease block a
        legitimate bind. The engine's own ownership refusal still governs what
        happens next."""
        target = self._candidate({"session_id": "somebody/else", "status": "active",
                                  "last_heartbeat": "2999-01-01T00:00:00+00:00"})
        self.assertFalse(self.bind(str(target))["isError"])

    def test_it_reuses_the_engines_own_notion_of_live(self):
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_spine_bind")
        segment = ast.get_source_segment(SOURCE, fn)
        self.assertIn("_active_lease(", segment)
        self.assertIn("_is_stale(", segment)


class IdempotencyAndRebindTests(_BoundInARepo):

    def test_binding_the_already_bound_spine_succeeds_and_changes_nothing(self):
        result = self.bind(str(self.driving))
        self.assertFalse(result["isError"], _text(result))
        payload = json.loads(_text(result))
        self.assertTrue(payload["already_bound"])
        self.assertEqual(self.driving.resolve(), self.module.SPINE)
        self.assertEqual("constellation/driving-work", self.module.SESSION)

    def test_idempotency_survives_a_lease_this_door_holds(self):
        """The ordering that is easy to get backwards. `_rebind_refusal` refuses
        whenever this process holds an active lease -- so an agent that binds,
        claims, then re-binds the SAME path would be refused for rebinding to
        where it already is. The idempotency check runs FIRST."""
        _write_spine(self.driving, _spine_payload(
            "driving-work", session={"session_id": "constellation/driving-work",
                                     "status": "active",
                                     "last_heartbeat": "2999-01-01T00:00:00+00:00"}))
        self.assertIsNotNone(self.module._rebind_refusal(),
                             "the fixture does not actually hold a lease, so this proves nothing")
        result = self.bind(str(self.driving))
        self.assertFalse(result["isError"], _text(result))
        self.assertTrue(json.loads(_text(result))["already_bound"])

    def test_a_differently_spelled_path_to_the_bound_spine_is_still_a_no_op(self):
        spelling = str(self.driving.parent / "." / self.driving.name)
        self.assertTrue(json.loads(_text(self.bind(spelling)))["already_bound"])

    def test_a_DIFFERENT_spine_is_refused_while_this_door_holds_a_lease(self):
        _write_spine(self.driving, _spine_payload(
            "driving-work", session={"session_id": "constellation/driving-work",
                                     "status": "active",
                                     "last_heartbeat": "2999-01-01T00:00:00+00:00"}))
        target = _write_spine(self.work / "other" / "spine.json", _spine_payload("other-work"))
        result = self.bind(str(target))
        self.assertTrue(result["isError"])
        text = _text(result)
        self.assertIn("still holds an active lease", text)
        self.assertIn("spine_bind", text,
                      "_rebind_refusal still tells the caller to retry `spine_open` -- it must "
                      "name the tool that was actually called")
        self.assertEqual(self.driving.resolve(), self.module.SPINE)

    def test_the_rebind_is_a_move_not_an_addition(self):
        """`decision:one-spine-per-process-stands`. The count never rises above
        one: the previously bound spine stops being addressable."""
        target = _write_spine(self.work / "other" / "spine.json", _spine_payload("other-work"))
        self.assertFalse(self.bind(str(target))["isError"])
        self.assertEqual(target.resolve(), self.module.SPINE)
        self.assertEqual("constellation/other-work", self.module.SESSION)
        self.assertIsNotNone(
            self.module._identity_violation(["--file", str(self.driving.resolve()), "current"]),
            "the door still answers for TWO spines after spine_bind")
        self.assertIsNone(
            self.module._identity_violation(["--file", str(target.resolve()), "current"]),
            "the door does not answer for the spine it just bound")


class SessionDerivationTests(_BoundInARepo):
    """The correction that is the point of this gate. Candidate A derived the
    session from `origin.work_id` alone; measured over the live population that
    refuses 55 of 60 spine-shaped files, including the Admiral's own live spine
    and `IMPLEMENTER_PLAN.json` -- the two cases the mission exists for."""

    def _bind_and_read_session(self, payload: dict) -> str:
        target = _write_spine(self.work / "cand" / "spine.json", payload)
        result = self.bind(str(target))
        self.assertFalse(result["isError"], _text(result))
        return self.module.SESSION

    def test_origin_work_id_wins_when_present(self):
        session = self._bind_and_read_session(
            _spine_payload("top-level-id", origin_work_id="origin-id"))
        self.assertEqual("constellation/origin-id", session)

    def test_the_top_level_work_id_is_the_fallback(self):
        session = self._bind_and_read_session(_spine_payload("top-level-id"))
        self.assertEqual("constellation/top-level-id", session)

    def test_an_admiral_shaped_spine_binds(self):
        """`origin: None` with a top-level `work_id` -- literally the shape of
        `.agent-work/epic-567-door/spine.json` and of
        `.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json`. Under
        `origin.work_id` alone both refuse, and they are the mission."""
        body = _spine_payload("epic-567-door")
        body["origin"] = None
        session = self._bind_and_read_session(body)
        self.assertEqual("constellation/epic-567-door", session)

    def test_the_session_is_never_a_caller_supplied_argument(self):
        """`IDENTITY_TRADE.md` §3 Option B: any string a caller can supply, it
        can supply its parent's. An undeclared key must be ignored, not honoured
        -- the g1 reviewer's own mutation was a handler honouring an undeclared
        key with every schema pin green."""
        target = _write_spine(self.work / "cand" / "spine.json", _spine_payload("real-id"))
        result = self.bind(str(target), session="constellation/somebody-elses-lease",
                           session_id="constellation/somebody-elses-lease")
        self.assertFalse(result["isError"], _text(result))
        self.assertEqual("constellation/real-id", self.module.SESSION)

    def test_it_derives_through_session_id_for_not_a_second_f_string(self):
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_spine_bind")
        segment = ast.get_source_segment(SOURCE, fn)
        self.assertIn("session_id_for(", segment)
        self.assertNotIn('f"constellation/', segment)

    def test_both_identity_roots_move_or_neither_does(self):
        """"Bound" means both. Binding the spine without the session yields a
        door that cannot `claim`, which is not a bound door."""
        target = _write_spine(self.work / "cand" / "spine.json", _spine_payload("real-id"))
        self.assertFalse(self.bind(str(target))["isError"])
        self.assertEqual(target.resolve(), self.module.SPINE)
        self.assertEqual("constellation/real-id", self.module.SESSION)
        self.assertEqual(str(target.resolve()), os.environ["SPINE_FILE"])
        self.assertEqual("constellation/real-id", os.environ["SPINE_SESSION"])

    def test_the_success_payload_reports_what_was_bound(self):
        target = _write_spine(self.work / "cand" / "spine.json", _spine_payload("real-id"))
        payload = json.loads(_text(self.bind(str(target))))
        self.assertEqual(str(target.resolve()), payload["SPINE_FILE"])
        self.assertEqual("constellation/real-id", payload["SPINE_SESSION"])
        self.assertEqual("real-id", payload["work_id"])
        self.assertFalse(payload["already_bound"])


class RootResolutionFailureTests(_BoundInARepo):
    """A door that cannot resolve its own checkout must REFUSE, not die and not
    fall back to something wider. Same catch tuple `_spine_open` already uses,
    so this fails as a refusal rather than as a dead server."""

    def test_a_spine_outside_any_checkout_refuses_rather_than_crashing(self):
        loose = self.dir / "no-repo"
        loose.mkdir()
        module = _load_module(loose / "bound.json", "s")
        # A DIFFERENT path from the bound one, or the idempotency short-circuit
        # answers first and the root is never resolved -- which is correct
        # behaviour and would make this test vacuous.
        target = _write_spine(loose / "other.json", _spine_payload("loose-work"))
        result = module._spine_bind({"spine_file": str(target)})
        self.assertTrue(result["isError"])
        self.assertIn("could not resolve", _text(result))

    def test_the_catch_tuple_matches_spine_opens(self):
        tree = ast.parse(SOURCE)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "_spine_bind")
        caught = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.ExceptHandler) and node.type is not None:
                caught |= {n.id for n in ast.walk(node.type) if isinstance(n, ast.Name)}
        self.assertLessEqual({"OSError", "RuntimeError"}, caught)


# --------------------------------------------------------------------------- #
# 4. THE load-bearing test: the two-door round trip.
# --------------------------------------------------------------------------- #

def _stage_a_checkout(into: Path) -> Path:
    """A throwaway git checkout carrying this repo's own `scripts/`.

    Necessary, not a workaround. `spine_bind` on an UNBOUND door derives its
    containment root from the server script's OWN location, so a test running
    the repo's own script would bind within the developer's real checkout. An
    installed constellation really does ship `scripts/` inside the checkout it
    serves, and `.mcp.json` really does launch `scripts/mcp_spine_server.py`
    relative to the client's own cwd -- so a crew inside a linked worktree runs
    THAT worktree's copy of the door, which is exactly the topology reproduced
    here.
    """
    repo = into / "repo"
    repo.mkdir()
    shutil.copytree(ROOT / "scripts", repo / "scripts")
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True, capture_output=True)
    for key, value in (("user.email", "bind@example.invalid"), ("user.name", "Bind Test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"],
                   check=True, capture_output=True)
    return repo


class _Door:
    """One real server process, driven over real newline-delimited JSON-RPC.

    A subprocess rather than an imported module, because the property under test
    is about a PROCESS: "a door launched with no SPINE_FILE". An in-process load
    cannot be launched, and the environment is the thing being varied.
    """

    def __init__(self, script: Path, env: dict, cwd: Path):
        self.proc = subprocess.Popen(
            [sys.executable, str(script)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1, env=env, cwd=str(cwd))
        self._id = 0

    def call(self, name: str, **args) -> dict:
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": "tools/call",
               "params": {"name": name, "arguments": args}}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise AssertionError(f"no reply to {name}; stderr:\n{self.proc.stderr.read()}")
        return json.loads(line)["result"]

    def text(self, name: str, **args) -> tuple[bool, str]:
        r = self.call(name, **args)
        return bool(r.get("isError")), "".join(b.get("text", "") for b in r["content"])

    def close(self) -> None:
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:  # pragma: no cover
            self.proc.kill()


class _RealDoorInAStagedCheckout(unittest.TestCase):
    """Base for the cases that need a real server PROCESS in a throwaway
    checkout. Shared rather than copied so the two classes below cannot drift
    into two subtly different launch environments."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = _stage_a_checkout(Path(self.tmp.name))
        self.doors: list[_Door] = []
        self.addCleanup(lambda: [d.close() for d in self.doors])

    def _env(self, **extra) -> dict:
        env = {
            "PATH": os.environ.get("PATH", ""), "SPINE_PARENT": "unknown",
            "GIT_AUTHOR_NAME": "Bind Test", "GIT_COMMITTER_NAME": "Bind Test",
            "GIT_AUTHOR_EMAIL": "bind@example.invalid",
            "GIT_COMMITTER_EMAIL": "bind@example.invalid",
        }
        env.update(extra)
        return env

    def _door(self, script: Path, cwd: Path, **env) -> _Door:
        d = _Door(script, self._env(**env), cwd)
        self.doors.append(d)
        return d


@requires_git
class NulByteDoesNotKillTheDoorTests(_RealDoorInAStagedCheckout):
    """**A refusal that kills the server is not a refusal.** A NUL byte in
    `spine_file` raised `ValueError: embedded null byte` out of
    `Path(raw).resolve()`; `main()`'s lifecycle branch catches only `KeyError`, so
    the exception unwound out of `main()` and the process exited 1. Every one of
    the door's twelve tools was then gone for the rest of the session, and the
    next call got a `BrokenPipeError`.

    A real process, not an imported module: the property under test is that the
    PROCESS survives, and an in-process call cannot observe that. The pre-existing
    analogue (`spine_advance(from_child=<NUL>)`) already survives, because
    `_identity_violation` runs inside `run_engine`'s `except Exception` net --
    `spine_bind` is the first lifecycle tool to take a caller-supplied filesystem
    path, and the lifecycle path has no such net."""

    def test_a_nul_byte_in_spine_file_is_refused_and_the_door_stays_alive(self):
        door = self._door(self.repo / "scripts" / "mcp_spine_server.py", self.repo)

        # A healthy call first, so "the door replies" is a measured baseline.
        is_err, before = door.text("spine_status")
        self.assertTrue(is_err)
        self.assertIn("no spine is bound", before)

        is_err, text = door.text(
            "spine_bind", spine_file=str(self.repo / ".agent-work" / "x\x00evil" / "spine.json"))
        self.assertTrue(is_err, f"a NUL byte in spine_file was accepted: {text}")
        self.assertIn("spine_file", text)

        # THE assertion: the process is still there, and still answering.
        self.assertIsNone(door.proc.poll(),
                          "the door process exited on a NUL byte in spine_file")
        is_err, after = door.text("spine_status")
        self.assertTrue(is_err)
        self.assertEqual(before, after, "the door survived but its state changed")

    def test_the_door_also_survives_a_nul_byte_while_it_is_BOUND(self):
        """Bound, R0's `Path(raw).resolve()` runs before anything else -- so the
        bound door reaches the raising line by a different route than the unbound
        one, and both must refuse."""
        door = self._door(self.repo / "scripts" / "mcp_spine_server.py", self.repo)
        spec = {"work_id": "nul-probe", "type": "gated",
                "gate": [{"id": "m1", "title": "t", "imperative": "do",
                          "postconditions": [{"id": "c1", "statement": "s", "kind": "artifact",
                                              "evidence_type": "user-decision"}]}]}
        is_err, text = door.text("spine_open", work_id="nul-probe", spec=spec, base="HEAD")
        self.assertFalse(is_err, text)
        bound = json.loads(text)["SPINE_FILE"]

        is_err, text = door.text("spine_bind", spine_file=bound + "\x00evil")
        self.assertTrue(is_err, f"a NUL byte in spine_file was accepted: {text}")
        self.assertIsNone(door.proc.poll(),
                          "the bound door process exited on a NUL byte in spine_file")
        is_err, status = door.text("spine_status")
        self.assertFalse(is_err, status)
        self.assertIn("m1", status)


@requires_git
class TwoDoorRoundTripTests(_RealDoorInAStagedCheckout):
    """Required evidence, load-bearing. Door 1 MINTS work with `spine_open`.
    Door 2, launched with **no** `SPINE_FILE` and no `SPINE_SESSION`, binds the
    same spine with `spine_bind` and drives it to terminal.

    The assertion that carries the design: door 2's resulting `SPINE`/`SESSION`
    are BYTE-IDENTICAL to the pair `spine_open` handed door 1. That is the only
    check that measures "bound by binding" and "bound at launch" being the same
    thing -- everything else in this file measures a refusal.
    """

    def test_door_two_binds_what_door_one_minted_and_drives_it(self):
        work_id = "bind-roundtrip"
        spec = {
            "work_id": work_id, "type": "gated",
            "gate": [{
                "id": "m1", "title": "a gate to drive", "imperative": "do the thing",
                "postconditions": [{"id": "c1", "statement": "human decided",
                                    "kind": "artifact", "evidence_type": "user-decision"}],
            }],
        }

        # --- Door 1: unbound, mints. `spine_open` binds it to what it minted.
        door_one = self._door(self.repo / "scripts" / "mcp_spine_server.py", self.repo)
        is_err, text = door_one.text("spine_status")
        self.assertTrue(is_err, "door 1 was already bound; this proves nothing")
        self.assertIn("no spine is bound", text)

        is_err, text = door_one.text("spine_open", work_id=work_id, spec=spec, base="HEAD")
        self.assertFalse(is_err, text)
        opened = json.loads(text)
        minted_spine, minted_session = opened["SPINE_FILE"], opened["SPINE_SESSION"]
        self.assertTrue(Path(minted_spine).is_file())

        # --- Door 2: launched with NO SPINE_FILE and NO SPINE_SESSION, from the
        #     new worktree -- the topology `.mcp.json` produces for a crew whose
        #     launcher did not pass `--spine`.
        worktree = Path(opened["worktree"])
        door_two = self._door(worktree / "scripts" / "mcp_spine_server.py", worktree)

        is_err, text = door_two.text("spine_status")
        self.assertTrue(is_err, "door 2 was not launched unbound")
        self.assertIn("no spine is bound", text)
        self.assertIn("spine_bind", text,
                      "the unbound refusal does not name the tool that is now the way out")

        is_err, text = door_two.text("spine_bind", spine_file=minted_spine)
        self.assertFalse(is_err, f"spine_bind refused: {text}")
        bound = json.loads(text)

        # THE assertion. Byte-identical, both roots.
        self.assertEqual(str(Path(minted_spine).resolve()), bound["SPINE_FILE"])
        self.assertEqual(minted_session, bound["SPINE_SESSION"])

        # A read-only verb now works against the bound spine.
        is_err, status = door_two.text("spine_status")
        self.assertFalse(is_err, status)
        self.assertIn("m1", status)

        # And the MUTATING half, which is what proves SESSION moved with SPINE:
        # `claim` is refused outright with an empty --session-id.
        is_err, claimed = door_two.text("spine_lease", action="claim", claimed_by="implementer")
        self.assertFalse(is_err, f"claim failed after spine_bind -- SESSION did not move: {claimed}")
        self.assertIn(minted_session, claimed)

        is_err, status = door_two.text("spine_status")
        self.assertFalse(is_err, status)
        self.assertIn("LEASE active: " + minted_session, status)

        # Drive the gate to terminal and release, through the ordinary tools.
        for call in (("spine_start", {"task_id": "m1"}),
                     ("spine_evidence", {"action": "attach", "task_id": "m1",
                                         "evidence_type": "user-decision",
                                         "fields": {"decision": "go"}}),
                     ("spine_advance", {"task_id": "m1", "mechanical": True}),
                     ("spine_lease", {"action": "release"})):
            is_err, out = door_two.text(call[0], **call[1])
            self.assertFalse(is_err, f"{call[0]} failed: {out}")

        recorded = json.loads(Path(minted_spine).read_text(encoding="utf-8"))
        self.assertEqual("complete", recorded["tasks"]["m1"]["status"])
        self.assertEqual(minted_session, recorded["engine_session"]["session_id"],
                         "the lease on disk records an identity other than the spine's own")

    def test_an_unbound_door_cannot_bind_outside_its_own_checkout(self):
        """The reach-delta negative on the UNBOUND path specifically -- the path
        with no `SPINE.parent` to fall back to, which is where a wrong root does
        the most damage."""
        outside = Path(self.tmp.name) / "outside" / "spine.json"
        outside.parent.mkdir(parents=True)
        outside.write_text(json.dumps(_spine_payload("outside-work")), encoding="utf-8")

        door = self._door(self.repo / "scripts" / "mcp_spine_server.py", self.repo)
        is_err, text = door.text("spine_bind", spine_file=str(outside))
        self.assertTrue(is_err, "an unbound door bound a spine outside its own checkout")
        assert_names_path(self, text, (self.repo / ".agent-work").resolve())
        # And it is still unbound afterwards, not half-bound.
        is_err, text = door.text("spine_status")
        self.assertTrue(is_err)
        self.assertIn("no spine is bound", text)


if __name__ == "__main__":
    unittest.main()
