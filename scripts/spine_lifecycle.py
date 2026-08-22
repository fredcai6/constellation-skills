#!/usr/bin/env python
"""Open and close Constellation work in one call each: `open_work` builds a
worktree, a branch, a scaffolded work area, and a compiled, origin-stamped
spine; `close_work` moves that work area into the archive, spine last, once
the caller has already driven it to a released, terminal close -- instead of
a caller that must already know the worktree/branch/archive conventions and
hand-drive `git worktree add`, `init_work_area.py`, `generate_spine.py` and
the close-ordering rules itself.

Frozen contract: `.agent-work/archive/2026-08-12-epic-418-followon-closeout/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md`, sections
2-4. No MCP door wiring happens here (g3).

Pure/impure split at FUNCTION granularity, matching `generate_spine.py`,
`validate_spine.py` and `checklist_engine.py`:

- `worktree_path_for`, `branch_name_for`, `archive_name_for`, `build_origin`,
  `closeout_refusal` are PURE: dict/str in, dict/str out, no `Path`, no `open`,
  no `subprocess`.
- `open_work` is impure and does the real work: it validates, refuses an occupied
  worktree or an already-active engine session, runs `git worktree add`, scaffolds
  the work area, compiles the spine (`generate_spine`, imported, never
  re-implemented), injects `origin`, re-validates, and self-verifies isolation --
  rolling back everything it created on any failure at or after `git worktree add`.
- `done_refusal` is PURE on the same terms and covers the two checks the spine
  dict cannot answer on its own (a clean tree, a captured episode) -- called on
  the CURRENT state, before `_advance_and_release` runs, while the lease is
  still active by definition. It does NOT call `closeout_refusal`:
  `closeout_refusal`'s own first check refuses unless the lease has already
  been released, so folding it in here would refuse every legitimate call.
  `closeout_refusal`'s lease/terminality/archive logic stays exclusively in
  `close_work`, downstream, after release. One actionable refusal, never a
  ritual to re-derive (#574).
- `_engine_call` is impure and is the SINGLE place this module calls
  `checklist_engine.main(argv)` in-process (the pattern
  `mcp_spine_server.run_engine` sets), returning `(output, exit_code)` and never
  raising -- `SystemExit` from `argparse` is caught alongside `EngineError`.
- `_advance_and_release` is impure and is the CLOSE half: it advances the gate
  the run is inside (`--why` when one is given, else `--mechanical`) and then
  releases the lease, through `_engine_call` only. A refused advance comes back
  verbatim and the release is never attempted.
- `close_work` is impure: it calls `closeout_refusal` and, if refused, does
  nothing at all; otherwise it `git mv`s every top-level entry under the work
  area except the bound spine and its journal, then `git mv`s those two last,
  then commits. It never advances, releases, opens a PR, or removes a
  worktree -- those are the caller's, before and after this call.
- `force_reap` is impure and is the REAP half (#552): a library call into
  `spine_rail._binding_transaction` with an identity mutate, forcing an
  immediate persist of the already-reaped binding-store map instead of
  waiting on some future unrelated session's touch. Zero edits to
  `spine_rail.py` -- it is called, never re-derived.
- `_release_child_plans` is impure and is the other #552 half: it releases
  the lease of every CHILD plan a bound spine's tasks declare via
  `child_checklist` (lineage, never directory proximity), as an explicit
  forced NON-owner (`--force --reason`, through `_engine_call`, never by
  echoing a child's own `session_id` back as the caller id), refusing any
  candidate whose `realpath` escapes the work directory. An undeclared
  active-leased file is left alone and reported, never seized.
- `finish_work` is impure and is the ONE-CALL COMPOSITION (#574): verify
  (`done_refusal`) -> release every child plan (`_release_child_plans`, before
  anything else) -> release the top-level lease (`_advance_and_release`) ->
  reap (`force_reap`, only after every release above -- reaping first would
  leave a still-active child's binding entry stale, reproducing #552 inside
  this very function) -> archive (`close_work`, unmodified) -> push -> an
  optional PR. Never raises for a normal closeout refusal; returns a
  structured `{"ok": False, "refusal": ..., "stage": ...}` instead.
- `open_pr` is impure, independently callable, and NOT invoked by `finish_work`
  unless `open_pr=True` is passed explicitly -- the launch order's PR-opening
  question (`decision:pr-opening-question-is-not-yours`) is floated, not
  ruled, so this module ships both the default (a wrapper calls `open_pr`
  itself) and the opt-in (`finish_work(open_pr=True)`) without needing to
  guess which a later ruling picks. Writes the PR body via a temp file and
  `--body-file`, never a heredoc `--body` string.
- `scripts/spine_done_cli.py` (a sibling file, not this module) is the thin,
  reachable-today CLI door over `finish_work` -- usable without waiting on
  `mcp_spine_server.py`'s concurrent rewrite to wire an actual `spine_done`
  MCP tool.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import checklist_engine  # noqa: E402
import generate_spine  # noqa: E402
import init_work_area  # noqa: E402
import run_crew  # noqa: E402
import validate_spine  # noqa: E402
import verify_worktree_isolation  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent / "hooks"))
import spine_rail  # noqa: E402


class SpineLifecycleError(Exception):
    """A refusal: `open_work` could not proceed. Nothing it created survives."""


# --------------------------------------------------------------------------- #
# pure helpers -- dict/str in, dict/str out; no Path, no open, no subprocess
# --------------------------------------------------------------------------- #

def worktree_path_for(work_id: str, *, wt_root: str) -> str:
    """`<wt_root>/<last segment of work_id>`. The worktree name is the FINAL
    `/`-separated segment only -- `epic-559/c3-lifecycle` names a worktree
    called `c3-lifecycle`, matching the live convention measured against this
    run's own worktree.

    Joined with a literal `/`, never `os.path.join`: this is a pure string
    function (the docstring above already promises `<wt_root>/<segment>`,
    not a platform-dependent join), and its result is compared, elsewhere,
    against `git worktree list --porcelain` -- which git always renders with
    forward slashes, even on Windows (git's own documented convention, not
    this repo's choice). `os.path.join` on `ntpath` would give a
    backslash-joined answer that git's own porcelain output never produces,
    so any existing backslashes in `wt_root` are folded to `/` too, keeping
    the whole answer in the one convention it is actually compared against.
    """
    last_segment = work_id.rsplit("/", 1)[-1]
    return wt_root.replace("\\", "/").rstrip("/") + "/" + last_segment


def branch_name_for(work_id: str) -> str:
    """The branch name: `work_id` verbatim -- matches every branch in this
    epic."""
    return work_id


def session_id_for(work_id: str) -> str:
    """The lease identity a spine for `work_id` is driven under:
    `constellation/<work_id>`. **The ONE definition.**

    Two callers, deliberately: `open_work` returns it as `SPINE_SESSION` when it
    MINTS a spine (step 9 below), and the door's `spine_bind`
    (`mcp_spine_server.py::_spine_bind`) recovers it from a spine that already
    exists, so binding a spine yields byte-identical identity to having been
    launched bound to it. Two copies of one f-string would let "the identity a
    spine was opened under" and "the identity a spine is bound under" disagree
    while both looked right, and the engine matches session ids by plain string
    equality -- there is nothing downstream that would notice.

    Pure on purpose: no clock, no environment, no filesystem. A session id
    derived from ambient state could not be reproduced by a second process
    binding the same spine, which is exactly the property `spine_bind` needs.

    NOT `run_crew.assignment_session_name` (`constellation/<work-id>/<gate>/<role>`),
    which names an ASSIGNMENT and cannot be derived from a spine at all -- `gate`
    and `role` are knowledge only the dispatcher has. The launch-time path keeps
    using that one; this is the coarser, spine-shaped identity a door that binds
    itself must take, because nobody handed it an assignment."""
    return f"constellation/{work_id}"


def archive_name_for(work_id: str, *, today: str) -> str:
    """The archive directory name: `<today>-<work_id with "/" replaced by "-">`.

    `today` is a caller-supplied `YYYY-MM-DD` string, never read from the clock
    inside this function, so a test never needs to freeze one. (g2's `close_work`
    is this function's only impure caller; it ships here because it is pure and
    belongs with its siblings.)"""
    return f"{today}-{work_id.replace('/', '-')}"


def build_origin(
    work_id: str, *, branch: str, worktree: str, base: str, opened_at: str, parent: str,
) -> dict:
    """The top-level `origin` block (LIFECYCLE_CONTRACT.md section 3). `parent` is
    the dispatching session, or the literal `"unknown"` -- the caller's job to
    resolve, never guessed here.

    This is PROVENANCE and nothing else. `worktree` in particular is written
    here and read by nothing that decides anything: the engine's
    `origin_worktree_refusal` used to compare it against its own ambient cwd,
    and that comparison is retired (#609 g2). The engine now reads no location
    at all, ambient or derived: the lexical rule that derives a worktree from a
    spine's path lives only in the stdlib-only hook, as
    `spine_rail._worktree_from_spine`. Ownership is the lease, but only where a
    lease is actually held -- on a spine with no active lease, never claimed or
    claimed and since released, that comparison was the sole refusal, so
    removing it WIDENED the leaseless path. The widening is accepted and
    deliberate: a `cd <worktree> &&` prefix defeated the comparison, so it was
    never a boundary, but a forgeable guard is not the same as no guard. Under
    an active lease held by another session, nothing changed
    (`ADMIRAL_RULING-1` R1; `checklist_engine`'s module header carries the full
    statement). Keep writing it accurately anyway,
    because a human or a reconciler reading a spine afterwards has no other
    record of where it came from. `tests/test_spine_origin_isolation.py` pins
    both halves of that pairing."""
    return {
        "work_id": work_id,
        "branch": branch,
        "worktree": worktree,
        "base": base,
        "opened_at": opened_at,
        "opened_by": "spine_open",
        "parent": parent,
    }


_TERMINAL_STATUSES = ("complete", "skipped")


def closeout_refusal(spine: dict, *, archive_exists: bool) -> str | None:
    """The whole close-ordering predicate (`LIFECYCLE_CONTRACT.md` section 4):
    `None` when `close_work` may proceed, else the refusal message naming why.
    `close_work` calls this and does nothing else about ordering.

    It computes terminality from the dict it is given and does NOT call
    `run_crew.spine_terminal` -- that function takes a PATH and reads the
    file (`run_crew.py:317`), so a function typed dict-in and forbidden I/O
    cannot call it. A differential test pins agreement with `spine_terminal`
    instead (same `TERMINAL` notion: `complete`/`skipped`, plus a survey's
    recorded `consolidation`).

    Checks, in order, refusing on the first that fails:

    - `engine_session.status == "released"`.
    - every id in `items` carries a terminal task status.
    - the archive directory does not already exist (`archive_exists` is
      `False`) -- never overwrite a prior archive.
    """
    session = spine.get("engine_session")
    status = session.get("status") if isinstance(session, dict) else None
    if status != "released":
        return "close refused: the lease is still active"

    items = spine.get("items")
    tasks = spine.get("tasks")
    if not items or not isinstance(tasks, dict):
        return "close refused: no gates recorded to close"
    for iid in items:
        task = tasks.get(iid)
        task_status = task.get("status") if isinstance(task, dict) else None
        if task_status not in _TERMINAL_STATUSES:
            return f"close refused: gate {iid!r} is not terminal (status {task_status!r})"
    if spine.get("type") == "survey" and spine.get("consolidation") is None:
        return "close refused: the survey has no recorded consolidation"

    if archive_exists:
        return "close refused: the archive directory already exists"

    return None


def done_refusal(
    spine: dict, *, tree_clean: bool, episodes_captured: bool,
) -> str | None:
    """The two checks a spine dict cannot answer on its own: `None` when both
    pass, else ONE refusal message naming why. PURE -- dict/bool in,
    str-or-None out; no `Path`, no `open`, no `subprocess`, so it sits beside
    its pure siblings above.

    ONE actionable refusal, never a ritual to re-derive (#574). The caller
    finishing a run gets a single sentence naming the one thing to fix, and the
    checks run in a fixed order so the message is deterministic:

    1. `tree_clean` -- the working tree has no uncommitted changes.
    2. `episodes_captured` -- this run captured at least one episode.

    `spine` is accepted (matching the calling convention of the rest of this
    module's refusal predicates) but is not consulted by either check above --
    neither the git working tree nor this run's episode capture is derivable
    from the spine dict, so both are the caller's to resolve and pass in.

    THIS FUNCTION MUST NOT CALL OR FOLD IN THE OTHER REFUSAL PREDICATE FARTHER
    UP THIS FILE (the one gating the lease/terminality/archive-directory move),
    and takes no `archive_exists` argument. `done_refusal` is called on the
    CURRENT state, BEFORE the advance-then-release step runs -- the lease is BY
    DEFINITION still active at that point (that is the condition that later
    step exists to fix). That other predicate's own first check refuses unless
    the lease has already been marked released, so a `done_refusal` that
    included it would refuse on every legitimate call, before the step that
    would actually release the lease ever runs. That predicate is not
    re-derived here and not skipped either -- it still runs, unchanged, exactly
    once, downstream in the move-to-archive step (unmodified, called after
    release) -- that is the one and only place lease/terminality/archive-exists
    gets checked.
    """
    if not tree_clean:
        return "close refused: the working tree has uncommitted changes"
    if not episodes_captured:
        return "close refused: this run captured no episode"
    return None


# --------------------------------------------------------------------------- #
# open_work -- impure. Order per LIFECYCLE_CONTRACT.md section 3; nothing
# survives a failure at or after `git worktree add`.
# --------------------------------------------------------------------------- #

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_wt_root(root: Path) -> str:
    """Nested under the main checkout at `<root>/.worktrees` -- measured against
    the live tree: `/home/tommy/projects/constellation-skills` pairs with
    `/home/tommy/projects/constellation-skills/.worktrees`."""
    return str(root / ".worktrees")


def _active_engine_session_spine(root: Path, work_id: str) -> Path | None:
    """The path of the first spine under `root/.agent-work/<work_id>/` (any
    depth, any filename) carrying an `engine_session` whose `status` is
    `"active"`, or `None`. `checklist_engine` only ever writes `"active"`
    (`:1033`) or `"released"` (`:1076`) -- no staleness gate, no other status.

    Read-only and fully defensive, in the style of
    `agent_work_root._active_epic_lease`: a missing directory, an unreadable or
    non-JSON file, a non-dict payload, or a missing/non-dict `engine_session`
    is skipped rather than raised. Structural (any JSON file with the field),
    not filename-based -- this epic's own driving spine is `execute.json`, not
    `spine.json`."""
    work_dir = root / ".agent-work" / work_id
    try:
        candidates = list(work_dir.rglob("*.json"))
    except OSError:
        return None
    for candidate in candidates:
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        session = data.get("engine_session")
        if not isinstance(session, dict):
            continue
        if str(session.get("status", "")).strip().lower() == "active":
            return candidate
    return None


def _git(args: list[str], *, cwd: Path) -> str:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SpineLifecycleError(f"git {' '.join(args)} failed in {cwd}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _best_effort_git(args: list[str], *, cwd: Path) -> None:
    """Runs a git command and ignores the outcome -- never raises, exit code
    unchecked. Rollback's only caller: best-effort cleanup must never itself
    fail the rollback it is part of."""
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _is_ignored(path: Path, *, cwd: Path) -> bool:
    """Whether `path` itself matches a gitignore rule -- `git check-ignore`,
    never a hand-maintained pattern list, so this tracks whatever `.gitignore`
    actually says. Independent of tracked status: a tracked file whose path
    happens to match a pattern still reads `True` here, which is why callers
    check `tracked` first -- `git add` never refuses an already-tracked path,
    ignored-looking or not."""
    proc = subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=str(cwd), capture_output=True, text=True)
    return proc.returncode == 0


def _rollback(worktree: str, branch: str, root: Path) -> None:
    """Best-effort, never raises: removes the worktree this call created and
    deletes the branch this call created. Scoped to what THIS call created --
    a pre-existing unrelated worktree or branch is never touched, because the
    only arguments here are the ones this call itself derived."""
    _best_effort_git(["worktree", "remove", "--force", worktree], cwd=root)
    _best_effort_git(["worktree", "prune"], cwd=root)
    _best_effort_git(["branch", "-D", branch], cwd=root)


@contextlib.contextmanager
def _chdir(path: Path):
    previous = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(previous)


def _compile_spine(spec: dict, *, repo_root: Path) -> dict:
    """`generate_spine.main()`'s steps 2-5 (spec-shape, compile, probe,
    validate), reused as a library rather than re-implemented -- everything
    `main()` does short of writing a file and printing to stdout."""
    shape_faults = generate_spine.spec_shape_faults(spec, repo_root=repo_root)
    if shape_faults:
        raise SpineLifecycleError("spec-shape refused: " + "; ".join(str(f) for f in shape_faults))

    compiled = generate_spine.compile_spec(spec)

    probe_faults, probe_undecidable = generate_spine.probe_spec(spec, repo_root=repo_root)
    blocking_undecidable = [u for u in probe_undecidable if u.blocking]
    if blocking_undecidable:
        raise SpineLifecycleError(
            "undecidable -- could not tell: " + "; ".join(str(u) for u in blocking_undecidable)
        )
    if probe_faults:
        raise SpineLifecycleError("probe refused: " + "; ".join(str(f) for f in probe_faults))

    result = validate_spine.validate(compiled, repo_root=repo_root)
    if result.undecidable or result:
        raise SpineLifecycleError(f"generated spine failed validation: {result}")
    return compiled


def open_work(
    work_id: str, spec: dict, *, root: str | os.PathLike[str], base: str, parent: str,
    wt_root: str | None = None,
) -> dict:
    """One call: validate, refuse an occupied worktree or an already-active
    engine session for this `work_id`, create the worktree and branch, scaffold
    the work area, compile the spine, inject `origin`, re-validate, self-verify
    isolation, and return the crew-binding values.

    Nothing survives a failure at or after `git worktree add` -- any exception
    from that point on rolls back the worktree and the branch this call
    created, then re-raises."""
    root = Path(root).resolve()

    # 1. Validate work_id -- reuse run_crew's existing validator, never a second one.
    try:
        run_crew.validate_work_id(work_id)
    except run_crew.CrewLaunchError as exc:
        raise SpineLifecycleError(str(exc)) from exc

    effective_wt_root = wt_root if wt_root is not None else _default_wt_root(root)
    worktree = worktree_path_for(work_id, wt_root=effective_wt_root)
    branch = branch_name_for(work_id)

    # 2. Refuse an occupied worktree path.
    if Path(worktree).exists():
        raise SpineLifecycleError(f"worktree path already exists: {worktree}")

    # 3. Refuse a work_id with an already-active engine session.
    offending = _active_engine_session_spine(root, work_id)
    if offending is not None:
        raise SpineLifecycleError(
            f"work id {work_id!r} already has an active engine session recorded at {offending}"
        )

    try:
        # 4. git worktree add <worktree> -b <branch> <base>
        _git(["worktree", "add", worktree, "-b", branch, base], cwd=root)

        # 5. Scaffold the work area.
        work_dir = init_work_area.init_work_area(Path(worktree), work_id)

        # 6. Compile the spine (generate_spine, imported, never re-implemented).
        compiled = _compile_spine(spec, repo_root=Path(worktree))

        # 7. Inject origin, then re-run validate_spine.validate on the result.
        base_sha = _git(["rev-parse", "HEAD"], cwd=Path(worktree))
        origin = build_origin(
            work_id, branch=branch, worktree=str(Path(worktree)), base=base_sha,
            opened_at=_now_iso(), parent=parent,
        )
        compiled["origin"] = origin
        result = validate_spine.validate(compiled, repo_root=Path(worktree))
        if result.undecidable or result:
            raise SpineLifecycleError(f"origin injection produced an invalid spine: {result}")

        # 8. Self-verify. `git` returning 0 is not evidence.
        with _chdir(root):
            ok, reason = verify_worktree_isolation.check_distinct_real(
                [worktree],
                verify_worktree_isolation.registered_worktrees(),
                verify_worktree_isolation.primary_checkout(),
            )
        if not ok:
            raise SpineLifecycleError(f"worktree isolation self-verify failed: {reason}")

        spine_path = work_dir / "spine.json"
        spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8", newline="\n")
    except Exception:
        _rollback(worktree, branch, root)
        raise

    # 9. Return the crew-binding values.
    return {
        "SPINE_FILE": str(spine_path),
        "SPINE_SESSION": session_id_for(work_id),
        "SPINE_PARENT": parent,
        "branch": branch,
        "worktree": worktree,
    }


# --------------------------------------------------------------------------- #
# close_work -- impure. Order per LIFECYCLE_CONTRACT.md section 4, and it is
# NOT this function's latitude: satisfying the closeout gate's postconditions,
# the final `advance`, and `release` are the CALLER's, through the door tools
# that already exist. `close_work` starts at "move the work area, spine file
# last."
# --------------------------------------------------------------------------- #

def _has_any_file(path: Path) -> bool:
    """Whether `path` is a file, or a directory holding at least one file at
    any depth. Git tracks files, never directories -- an empty directory (or
    a directory holding only further empty directories) has nothing `git
    add`/`git mv` can ever see, no matter how it is staged."""
    if path.is_file():
        return True
    if path.is_dir():
        return any(child.is_file() for child in path.rglob("*"))
    return False


def close_work(
    spine_path: str | os.PathLike[str], *, root: str | os.PathLike[str], today: str,
) -> dict:
    """Move a closed-out work area into the archive, spine and journal last,
    and commit the move.

    Refuses via `closeout_refusal` and does NOTHING AT ALL if the lease is
    still active, any gate is non-terminal, or the archive directory already
    exists.

    Otherwise: moves every top-level entry directly under the spine's own
    directory (the work area) except the bound spine file and its journal,
    each call naming its own paths; THEN moves those two, last; then
    `git commit`s. Never `git add -A`, never a bare `.` -- each entry is
    staged by its own explicit path (`git add <path>`, a no-op for content
    already tracked) before `git mv`, because a scaffolded work area routinely
    holds directories nothing has been committed into yet, and `git mv`
    refuses an entry with no tracked content. An entry with no trackable
    content at all (an empty directory -- git tracks no directory, ever) is
    moved on the filesystem directly, since there is nothing for git to stage
    either way.

    Every entry is classified first: TRACKED (`git ls-files` already sees it)
    or UNTRACKED, and if untracked, whether it is itself gitignored (`git
    check-ignore`). A real work area always carries gitignored top-level
    entries beside the spine (the MCP door's `mcp_calls.jsonl` and
    `mcp_server_started`) -- `git add` refuses an untracked path that matches
    a gitignore rule, so an ignored entry is moved on the filesystem directly,
    the same as an empty directory. Tracked and untracked-not-ignored entries
    both go through `git add` (a no-op for the former) then `git mv` (or a
    filesystem rename if nothing trackable landed under it).

    The "everything else" batch is wrapped: if any of its entries' moves
    raises, every entry already moved in this batch -- including a
    gitignored one moved on the filesystem, and any partially-staged git
    rename -- is restored to its original path before the exception
    propagates, so a failure mid-batch never leaves the work area split
    across the original directory and the archive. The spine/journal step
    is deliberately NOT covered by this rollback: a failure there already
    leaves a directly resumable state (spine and journal still at their
    original path, everything else already archived), which a retry finds
    and continues from -- this is the property that let the real run this
    defect was found on recover from its own interruption.

    The excluded names are DERIVED from `spine_path`'s own basename, never the
    literal strings `"spine.json"`/`"spine.json.journal"` -- a spine opened by
    `open_work` is always named `spine.json`, but this Commander's own driving
    spine is `execute.json`, and a literal hardcode would sweep a live driving
    checklist into the "everything else" batch before the spine-last step.

    The work id -- and so the archive name (`archive_name_for`) -- is derived
    structurally from `spine_path`'s location relative to `root/.agent-work`,
    never read from an `origin` field that a hand-authored spine might lack.

    Reports a verdict naming the branch, the new `HEAD`, and "ready to PR."
    Never opens a PR, never removes a worktree, never judges the work good.
    """
    root = Path(root).resolve()
    spine_path = Path(spine_path)
    absolute_spine_path = spine_path if spine_path.is_absolute() else root / spine_path

    spine = json.loads(absolute_spine_path.read_text(encoding="utf-8"))

    work_dir = absolute_spine_path.resolve().parent
    agent_work_dir = (root / ".agent-work").resolve()
    work_id = work_dir.relative_to(agent_work_dir).as_posix()

    archive_dir = root / ".agent-work" / "archive" / archive_name_for(work_id, today=today)

    refusal = closeout_refusal(spine, archive_exists=archive_dir.exists())
    if refusal is not None:
        raise SpineLifecycleError(refusal)

    spine_name = absolute_spine_path.name
    journal_name = spine_name + ".journal"
    journal_path = absolute_spine_path.parent / journal_name

    other_entries = sorted(
        p.name for p in work_dir.iterdir() if p.name not in (spine_name, journal_name)
    )

    moved: list[tuple[Path, Path, bool]] = []  # (src, dest, via_git)

    def _stage_and_move(src: Path, dest: Path) -> None:
        """Move one top-level work-area entry, staged by its own explicit
        path (never `-A`, never a bare `.`). Classified first: an entry that
        is untracked AND itself gitignored (the MCP door's `mcp_calls.jsonl`,
        `mcp_server_started`) is moved on the filesystem directly, since `git
        add` refuses an untracked ignored path outright. Otherwise `git add
        <src>` first, so content `git mv` has never seen committed (a freshly
        scaffolded work area routinely holds some) is tracked before the
        move -- a no-op for content already tracked. If `src` has no
        trackable content at all (an empty directory), `git add` stages
        nothing and `git mv` would refuse it outright ("source directory is
        empty"); there is nothing for git to know about either way, so the
        entry is moved on the filesystem directly. Every successful move is
        recorded in `moved` so a later failure can restore it."""
        tracked = bool(_git(["ls-files", str(src)], cwd=root))
        if not tracked and _is_ignored(src, cwd=root):
            shutil.move(str(src), str(dest))
            moved.append((src, dest, False))
            return
        _git(["add", str(src)], cwd=root)
        try:
            if _has_any_file(src):
                _git(["mv", str(src), str(dest)], cwd=root)
                moved.append((src, dest, True))
            else:
                src.rename(dest)
                moved.append((src, dest, False))
        except Exception:
            _best_effort_git(["reset", "--", str(src)], cwd=root)
            raise

    def _undo_moved() -> None:
        """Best-effort: restores every entry `moved` recorded, most recent
        first, so a failure partway through the batch never leaves the work
        area split across the original directory and the archive."""
        for src, dest, via_git in reversed(moved):
            if via_git:
                _best_effort_git(["mv", str(dest), str(src)], cwd=root)
            elif dest.exists():
                shutil.move(str(dest), str(src))
            _best_effort_git(["reset", "--", str(src)], cwd=root)

    archive_dir.mkdir(parents=True)
    try:
        for name in other_entries:
            _stage_and_move(work_dir / name, archive_dir / name)
    except Exception:
        # Restore the batch -- never leave the work area split. The
        # spine/journal step below is deliberately OUTSIDE this wrapping: a
        # failure there already leaves a directly resumable state (the spine
        # and journal still at their original path, everything else already
        # in the archive) and a retry finds them there -- the property that
        # saved the real run this defect was found on.
        _undo_moved()
        if archive_dir.exists() and not any(archive_dir.iterdir()):
            archive_dir.rmdir()
        raise

    # Spine and journal, LAST -- so an interruption before this point leaves
    # them findable at their original path for a retry.
    _stage_and_move(absolute_spine_path, archive_dir / spine_name)
    if journal_path.exists():
        _stage_and_move(journal_path, archive_dir / journal_name)

    _git(["commit", "-m", f"chore: close {work_id} -- archive under {archive_dir.relative_to(root)}"], cwd=root)

    new_head = _git(["rev-parse", "HEAD"], cwd=root)
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=root)

    return {
        "work_id": work_id,
        "branch": branch,
        "head": new_head,
        "archive": str(archive_dir),
        "message": (
            f"closed {work_id}: branch {branch} at {new_head}, "
            f"archived under {archive_dir} -- ready to PR."
        ),
    }


# --------------------------------------------------------------------------- #
# closeout primitives (#574 g1) -- impure. `_engine_call` is the ONE place this
# module talks to the engine; `_advance_and_release` is the close half of
# "finish this run" (the verify half is `done_refusal`, pure, above), and it
# goes through `_engine_call` and nothing else.
#
# LIBRARY REUSE, NOT A FILE EDIT (decision:library-reuse-over-file-edit): these
# call `checklist_engine.main(argv)` in-process rather than adding anything to
# `checklist_engine.py`, mirroring how this module already imports
# `generate_spine`/`init_work_area`/`run_crew`/`validate_spine` instead of
# re-implementing them.
# --------------------------------------------------------------------------- #

def _engine_call(argv: list[str]) -> tuple[str, int]:
    """Call the real engine's `main(argv)` in-process and return
    `(captured_output, exit_code)`. NEVER RAISES.

    The pattern is `mcp_spine_server.run_engine`'s, deliberately (its module
    docstring: "Every tool builds an argv and calls `checklist_engine.main(argv)`,
    capturing stdout, stderr and the exit code"): stdout and stderr are
    redirected into one `io.StringIO` and the exit code is returned alongside
    the text. One buffer, not two, because the caller wants the engine's
    MESSAGE whichever stream carried it -- `main()` prints a success message to
    stdout and a `REFUSED:` line to stderr, and a caller that has to know which
    is which is a caller that can drop a refusal.

    THE SINGLE CHOKE POINT, and every caller in this module goes through it, so
    there is exactly one place where "what the engine said" is captured and one
    place where its failure modes are handled.

    `SystemExit` is caught as well as `EngineError`, and that is load-bearing
    rather than defensive tidiness. `argparse` calls `sys.exit(2)` on an argv it
    cannot parse, and `checklist_engine.main()`'s own try/except catches only
    `EngineError` -- so an argv-shape mismatch (a typo here, or a flag renamed
    upstream) escapes as `SystemExit` and would bypass every `(output, code)`
    check the callers below make. `SystemExit` is a `BaseException`, so no
    `except Exception` can stand in for this clause. On it, the captured output
    is returned with `int(exc.code or 0)`.

    The broad clause after it keeps the never-raises promise total: `main()`
    handles `EngineError` internally, but the work it does BEFORE that handler
    -- `parse_args`, then `load()` on the path -- can still raise anything from
    an `OSError` (no such file) to a `ValueError` (unparseable JSON), and a
    closeout primitive that dies on a missing spine instead of reporting it is
    the swallowed-refusal defect wearing a different hat. Ordered
    `EngineError` first, since it is an `Exception` subclass.
    """
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            code = checklist_engine.main(argv)
    except SystemExit as exc:  # argparse rejected the argv (e.g. an unknown flag)
        code = int(exc.code or 0)
    except checklist_engine.EngineError as exc:
        buffer.write(f"{type(exc).__name__}: {exc}")
        code = 1
    except Exception as exc:  # noqa: BLE001 - surface everything, never swallow
        buffer.write(f"{type(exc).__name__}: {exc}")
        code = 1
    return buffer.getvalue().strip(), code


def _advance_and_release(
    spine_path: str | os.PathLike[str], session_id: str, *,
    root: str | os.PathLike[str], why: str | None = None,
) -> dict:
    """Close the gate this run is inside, then release the lease -- the two
    engine steps `close_work` deliberately does not do, in the one order that
    is legal.

    Sequence: read the spine; resolve the active gate with
    `checklist_engine.active_id` (reused, never a second terminality rule);
    `start` it if it is still `pending`; `advance` it -- with `--why <why>` when
    `why` is a non-empty string, else `--mechanical`; then `release
    --session-id`. When `active_id` is `None` every gate is already terminal, so
    only the release is left.

    Returns `{"ok": True, "output": <every step's output>}` or
    `{"ok": False, "refusal": <verbatim engine text>, "stage":
    "start"|"advance"|"release"}`.

    A REFUSAL IS RETURNED VERBATIM AND THE RELEASE IS NOT ATTEMPTED. Not
    re-worded, not wrapped in a sentence of our own, exit code not swallowed:
    the engine's message already names the exact fix, and an agent finishing a
    run needs that one actionable line rather than a ritual to re-derive it
    (#574). A release that happens after a refused advance is the same defect
    with worse consequences -- it would leave the lease closed on a gate that
    never closed.

    `--mechanical` IS NEVER ASSUMED TO SUCCEED. `advance`'s `require_why` is
    computed live at the engine's CLI boundary from
    `checklist_engine._trip_hard_band_reading` (`_run_verb`, ~:3369) -- it is
    not derived from anything passed in here -- and at/over the HARD context
    band the engine refuses `--mechanical` outright. That refusal comes straight
    back as `stage: "advance"`, carrying the engine's own instruction to re-run
    with `--why`, which is plausibly the exact scenario #574 cites ("an
    Admiral's closeout was refused at 23% context").

    `root` resolves a relative `spine_path`, the same way `close_work` does it,
    so a caller may hand either form.
    """
    root = Path(root).resolve()
    spine_path = Path(spine_path)
    absolute_spine_path = spine_path if spine_path.is_absolute() else root / spine_path

    spine = json.loads(absolute_spine_path.read_text(encoding="utf-8"))
    file_args = ["--file", str(absolute_spine_path)]
    session_args = ["--session-id", session_id]
    outputs: list[str] = []

    gate = checklist_engine.active_id(spine)
    if gate is not None:
        task = (spine.get("tasks") or {}).get(gate)
        status = task.get("status") if isinstance(task, dict) else None
        if status == "pending":
            output, code = _engine_call([*file_args, "start", gate, *session_args])
            if code != 0:
                return {"ok": False, "refusal": output, "stage": "start"}
            outputs.append(output)

        why_args = ["--why", why.strip()] if (why or "").strip() else ["--mechanical"]
        output, code = _engine_call([*file_args, "advance", gate, *why_args, *session_args])
        if code != 0:
            # Verbatim, and NO release: see the docstring. The engine's own
            # message is the actionable one.
            return {"ok": False, "refusal": output, "stage": "advance"}
        outputs.append(output)

    output, code = _engine_call([*file_args, "release", *session_args])
    if code != 0:
        return {"ok": False, "refusal": output, "stage": "release"}
    outputs.append(output)

    return {"ok": True, "output": "\n".join(outputs)}


# --------------------------------------------------------------------------- #
# force_reap -- reap + child-plan release (#552's mechanism), g2. A LIBRARY
# call into spine_rail's existing transaction helper, not a re-derivation of
# it: `spine_rail.py` is edited nowhere in this module.
# --------------------------------------------------------------------------- #

def force_reap(project_dir: str | os.PathLike[str]) -> dict | None:
    """Force an immediate persist of the binding store's already-reaped map,
    rather than waiting on some future unrelated session's touch to trigger
    it.

    A LIBRARY call into `spine_rail._binding_transaction` with an IDENTITY
    mutate (`lambda reaped: reaped`) -- `_binding_transaction` already loads
    the registry, reaps it UNDER THE LOCK (`_reap_binding_entries` drops any
    entry whose target reads `engine_session.status == "released"`), hands the
    ALREADY-REAPED map to `mutate`, and persists exactly when the result
    differs from what it loaded. Handing the reaped map straight back is
    therefore sufficient to make the reap durable NOW -- an identity mutate
    is not a no-op here, because what changed is the registry's OWN load-time
    reap being written out rather than discarded at the end of this call.

    Returns `None` on any fail-open path inside `_binding_transaction` (lock
    contention, lock timeout, a lock-API error, or a replace failure) -- that
    IS a real answer on those paths, not an error, and is propagated
    verbatim; see `_binding_transaction`'s own docstring for the full list.

    `project_dir` is always a `tmp_path` fixture in tests -- never this
    repo's own root, so no test call can mutate the real
    `.agent-work/.spine-rail-binding.json`.
    """
    return spine_rail._binding_transaction(Path(project_dir), lambda reaped: reaped)


# --------------------------------------------------------------------------- #
# _release_child_plans -- the other half of #552's mechanism: reaping the
# binding store only removes entries for spines that already read
# `released`; a child plan whose own lease is still `active` is invisible to
# that reap and must be released explicitly before an archive can claim zero
# active leases. Three safety properties, each SHIPPED runtime guard:
#
# 1. LINEAGE, not directory proximity -- a child is identified structurally:
#    a JSON file whose realpath is strictly inside `work_dir` AND which some
#    task in the parent spine names in its `child_checklist` field.
# 2. HONEST NON-OWNER RELEASE -- released via `release --force --reason`,
#    never by echoing the child's own `engine_session.session_id` back as the
#    caller id (that would make the ownership check tautological).
# 3. ESCAPE REFUSAL -- every candidate is resolved with `realpath` and
#    refused unless strictly inside `work_dir`, so a symlink inside the work
#    area cannot reach a spine outside it.
# --------------------------------------------------------------------------- #

def _release_child_plans(
    spine_path: str | os.PathLike[str], work_dir: str | os.PathLike[str], *,
    root: str | os.PathLike[str], reason: str,
) -> dict:
    """Release the lease of every CHILD plan of the spine at `spine_path`,
    and report what was left alone.

    Returns `{"released": [str, ...], "unclaimed_active": [str, ...]}` --
    absolute-path strings, in the order `work_dir` is walked.

    A "child" is identified STRUCTURALLY (property 1), never by directory
    proximity: a `*.json` file under `work_dir`, resolved via
    `Path.resolve()` and refused unless strictly inside `work_dir`
    (`is_relative_to`, property 3 -- a symlink escape is refused the same
    way at both the declaration and the scan), that SOME task in the parent
    spine's `tasks` names in its `child_checklist` field (resolved relative
    to `work_dir`, matching the live convention -- `interrogation.json`,
    `execute.json`, ... sit directly beside the parent spine). The bound
    spine at `spine_path` itself is excluded from the scan (mirroring
    `close_work`'s spine/journal exclusion) -- it is not its own child, and
    at call time its own lease is BY DEFINITION still active (the same
    reason `done_refusal` runs before `_advance_and_release`, not after).

    Only a declared child whose OWN `engine_session.status == "active"` is
    touched. An active-leased JSON under `work_dir` that no task declares is
    left alone entirely and reported in `unclaimed_active` -- releasing it
    would seize a lease a different, still-working agent genuinely holds,
    which is explicitly not this function's call to make (widening the
    child-identification predicate or releasing an `unclaimed_active` file
    needs authority this run does not have).

    Each declared, active child is released as the explicit NON-OWNER it is
    (property 2): `release --session-id <caller> --force --reason <reason>`
    through `_engine_call` -- the SAME single choke point `_advance_and_release`
    uses, never a second call path. `<caller>` is the PARENT spine's OWN
    `engine_session.session_id` (falling back to a synthetic label only if
    the parent carries none) -- NEVER a read of the CHILD's own
    `session_id`. Echoing the child's id back would make `release`'s
    ownership check (`session_id != sess.get("session_id")`,
    `checklist_engine.py:1133-1147`) tautological, forging an ownership this
    run does not have; it would also falsify the journal's own
    `session_id` field, the audit trail `--force --reason` exists to keep
    honest. A release the engine still refuses (e.g. an empty `reason`) is
    NOT silently dropped -- the child is reported in `unclaimed_active`
    instead, since its lease did in fact remain active.

    `reason` is passed straight through to `--reason`; naming the parent
    `work_id` and stating this is a parent closeout is the CALLER's
    responsibility (`finish_work`, g3), not derived here.
    """
    root = Path(root).resolve()
    spine_path = Path(spine_path)
    absolute_spine_path = spine_path if spine_path.is_absolute() else root / spine_path
    resolved_work_dir = Path(work_dir).resolve()

    spine = json.loads(absolute_spine_path.read_text(encoding="utf-8"))
    tasks = spine.get("tasks")
    tasks = tasks if isinstance(tasks, dict) else {}

    parent_session = spine.get("engine_session")
    caller_id = (
        parent_session.get("session_id")
        if isinstance(parent_session, dict) and parent_session.get("session_id")
        else f"parent-closeout:{absolute_spine_path}"
    )

    excluded: set[Path] = set()
    try:
        excluded.add(absolute_spine_path.resolve())
    except OSError:
        pass

    declared_children: set[Path] = set()
    for task in tasks.values():
        if not isinstance(task, dict):
            continue
        child_ref = task.get("child_checklist")
        if not isinstance(child_ref, str) or not child_ref.strip():
            continue
        child_path = Path(child_ref)
        candidate = child_path if child_path.is_absolute() else resolved_work_dir / child_path
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if not resolved.is_relative_to(resolved_work_dir):
            continue  # property 3: escape refusal, even at declaration time
        declared_children.add(resolved)

    released: list[str] = []
    unclaimed_active: list[str] = []

    try:
        candidates = sorted(resolved_work_dir.rglob("*.json"))
    except OSError:
        candidates = []

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if not resolved.is_relative_to(resolved_work_dir):
            continue  # property 3: a symlink walking outside work_dir, refused
        if resolved in excluded:
            continue  # the bound spine itself -- not a child

        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        session = data.get("engine_session")
        if not isinstance(session, dict) or session.get("status") != "active":
            continue  # no active lease here -- nothing to reap

        if resolved not in declared_children:
            # property 1: proximity alone is not lineage -- leave it alone.
            unclaimed_active.append(str(candidate))
            continue

        output, code = _engine_call([
            "--file", str(candidate),
            "release", "--session-id", caller_id,
            "--force", "--reason", reason,
        ])
        if code == 0:
            released.append(str(candidate))
        else:
            # A declared child the engine still refused to release keeps its
            # active lease -- report it rather than silently dropping it.
            unclaimed_active.append(str(candidate))

    return {"released": released, "unclaimed_active": unclaimed_active}


# --------------------------------------------------------------------------- #
# finish_work + open_pr (#574 g3) -- "I'm done" as one call, composing g1's
# verify/close primitives (done_refusal, _advance_and_release) and g2's reap +
# child-plan release (_release_child_plans, force_reap) with close_work
# (unmodified) in the ONE order the plan critique and its cold-critic
# duplicate both fix: verify -> release children -> release the top-level
# lease -> reap -> archive -> push -> (optional) open a PR.
#
# NEITHER close_work NOR any of g1/g2's functions is edited here -- this is
# composition only, through the same _engine_call choke point they already
# use internally, never a second call path.
# --------------------------------------------------------------------------- #

def finish_work(
    spine_path: str | os.PathLike[str], *, root: str | os.PathLike[str],
    session_id: str, today: str, tree_clean: bool, episodes_captured: bool,
    why: str | None = None, push: bool = True, open_pr: bool = False,
) -> dict:
    """One call: "I'm done." An agent that has genuinely finished a run should
    never need to hand-sequence release -> reap -> archive -> push, and a run
    that is NOT ready should get one clean, actionable refusal -- never a
    partial mutation, never a swallowed exception, never a call into
    `close_work` that spuriously refuses because the ordering was wrong.

    `tree_clean`/`episodes_captured` are not part of the handoff's headline
    signature line, but ARE structurally required: step 2 below passes them
    straight to `done_refusal`, and the CLI (`spine_done_cli.py`) collects
    them as `--tree-clean`/`--episodes-captured` flags precisely so it has
    something to pass here. Treated as a signature gap in the handoff, not a
    license to invent a different check -- see this run's IMPLEMENTER_RESULT.

    THE COMPOSITION ORDER IS LOAD-BEARING (PLAN_CRITIQUE.md finding 1/2,
    PLAN_CRITIC.md's matching findings 1-3, and g1/g2's own independent
    re-discoveries of the same facts):

    1. Load the spine dict from `spine_path` (resolved against `root`, the
       same pattern `close_work`/`_advance_and_release` already use).
    2. `done_refusal(spine, tree_clean=tree_clean, episodes_captured=episodes_captured)`.
       If refused: return `{"ok": False, "refusal": ..., "stage": "verify"}`
       immediately. NOTHING has been touched at this point -- no mutation on
       this path.
    3. `_release_child_plans(...)` -- BEFORE the top-level release and BEFORE
       any reap. Its own refusal path (an engine refusal on one specific
       child) does not raise; that child comes back in `unclaimed_active`,
       per its own docstring, and this function does not special-case it.
    4. `_advance_and_release(...)` -- the top-level spine's own close. A
       refusal here returns `{"ok": False, "refusal": ..., "stage":
       f"advance-release:{substage}"}` and STOPS -- but step 3's releases are
       NOT unwound. A run whose top-level gate isn't ready to close but whose
       children already finished is a real, valid intermediate state, not a
       rollback candidate.
    5. `force_reap(root)` -- AFTER every release in steps 3 and 4, never
       before: `_reap_binding_entries` only drops an entry whose target
       already reads `released`, so reaping before children are released
       would leave every child's binding-store entry stale -- reproducing
       the exact #552 defect this gate exists to close. A `None` return
       (`force_reap`'s fail-open path) is not a `finish_work` failure -- it
       is logged in the return (`"reap": None`) and the run continues.
    6. `close_work(...)` -- existing, UNMODIFIED. The one and only place
       `closeout_refusal` (lease/terminality/archive-exists) is checked; by
       now the lease is already released (step 4), so it will not spuriously
       refuse. A `SpineLifecycleError` here is caught and returned as
       `{"ok": False, "refusal": str(exc), "stage": "archive"}` -- NEVER
       propagated. `finish_work`'s whole contract is "one call, one clean
       result or one clean refusal," never a raised exception on a normal
       "not ready yet" outcome.
    7. `git push origin <branch>` (branch read from `close_work`'s own return)
       when `push=True`. A push failure is reported (`"pushed": False`, plus
       `"push_error"` naming the git error text) but does NOT unwind steps
       1-6 -- the archive move already committed locally; a failed push is a
       network/auth problem to retry, not a reason to fail the whole call.
    8. `open_pr(...)` -- called ONLY when `open_pr=True`. Not called by
       default. `open_pr` is a separate, independently-callable helper
       (below) -- this is the floated PR-opening question
       (`decision:pr-opening-question-is-not-yours`): Tommy has not ruled
       whether PR-opening belongs in the engine verb or a wrapper script,
       and this design adopts either answer without rework.

    Returns, on success: `{"ok": True, "work_id", "branch", "head", "archive",
    "pushed": bool, "push_error": str | None, "pr": None | str,
    "child_plans_released": [...], "unclaimed_active": [...], "reap": dict |
    None}`. On any of steps 2/4/6 refusing: `{"ok": False, "refusal": <the
    verbatim engine or closeout text>, "stage": "verify" |
    "advance-release:<substage>" | "archive"}`. Never raises for a normal
    closeout refusal -- `SpineLifecycleError` stays reserved for genuine
    faults elsewhere in the stack (e.g. `close_work`'s own git-command
    failures), not the ordinary "not ready yet" outcome.
    """
    # The module-level `open_pr` function is captured via the module
    # namespace, NOT the local scope: this function's own `open_pr: bool`
    # parameter shadows the module-level `open_pr` name for the rest of this
    # body -- deliberate, per the handoff's own signature (part (b) is
    # "called only when open_pr=True"). `globals()` reads the module's
    # namespace dict directly, so it is unaffected by the local shadowing.
    open_pr_fn = globals()["open_pr"]

    root = Path(root).resolve()
    given_spine_path = Path(spine_path)
    absolute_spine_path = given_spine_path if given_spine_path.is_absolute() else root / given_spine_path

    work_dir = absolute_spine_path.resolve().parent
    agent_work_dir = (root / ".agent-work").resolve()
    work_id = work_dir.relative_to(agent_work_dir).as_posix()

    # 1. Load the spine dict.
    spine = json.loads(absolute_spine_path.read_text(encoding="utf-8"))

    # 2. Verify -- refuse and stop; nothing mutated on this path.
    refusal = done_refusal(spine, tree_clean=tree_clean, episodes_captured=episodes_captured)
    if refusal is not None:
        return {"ok": False, "refusal": refusal, "stage": "verify"}

    # 3. Release every declared child plan's lease -- BEFORE the top-level
    # release and BEFORE any reap.
    child_result = _release_child_plans(
        absolute_spine_path, work_dir, root=root,
        reason=f"closeout: child plan swept by finish_work for {work_id}",
    )

    # 4. The top-level spine's own close: advance the active gate, then
    # release the lease. A refusal here is returned verbatim; steps 3's
    # releases already happened and are NOT unwound (see docstring).
    advance_result = _advance_and_release(absolute_spine_path, session_id, root=root, why=why)
    if not advance_result["ok"]:
        return {
            "ok": False,
            "refusal": advance_result["refusal"],
            "stage": f"advance-release:{advance_result['stage']}",
        }

    # 5. Reap -- AFTER every release above, never before (#552's ordering
    # fix). A None return is a real, fail-open answer, not a failure here.
    reap_result = force_reap(root)

    # 6. Archive -- the one and only place closeout_refusal is checked.
    # SpineLifecycleError is caught, never propagated: this is a normal
    # "not ready" outcome, not a fault.
    try:
        close_result = close_work(absolute_spine_path, root=root, today=today)
    except SpineLifecycleError as exc:
        return {"ok": False, "refusal": str(exc), "stage": "archive"}

    # 7. Push -- reported, never fatal to the already-committed archive move.
    pushed = False
    push_error: str | None = None
    if push:
        proc = subprocess.run(
            ["git", "push", "origin", close_result["branch"]],
            cwd=str(root), capture_output=True, text=True,
        )
        pushed = proc.returncode == 0
        if not pushed:
            push_error = (proc.stderr or proc.stdout or "").strip()

    # 8. Open a PR -- only when explicitly requested. Not called by default.
    pr_url = open_pr_fn(work_id, close_result["branch"], root=root) if open_pr else None

    return {
        "ok": True,
        "work_id": close_result["work_id"],
        "branch": close_result["branch"],
        "head": close_result["head"],
        "archive": close_result["archive"],
        "pushed": pushed,
        "push_error": push_error,
        "pr": pr_url,
        "child_plans_released": child_result["released"],
        "unclaimed_active": child_result["unclaimed_active"],
        "reap": reap_result,
    }


def open_pr(
    work_id: str, branch: str, *, root: str | os.PathLike[str],
    title: str | None = None, body: str | None = None,
) -> str | None:
    """A separate, independently-callable helper -- `finish_work` does NOT
    call this unless `open_pr=True`. Takes no spine path at all, only
    `work_id`/`branch`, so there is nothing here to accidentally mutate.

    `gh pr create --title <title> --body-file <tmp file> --head <branch>` via
    `subprocess.run`, cwd `root`. The PR body is ALWAYS written to a
    `tempfile.NamedTemporaryFile` and passed with `--body-file` -- NEVER a
    heredoc or a `--body` string -- per this repo's own Windows-shell
    doctrine (`skills/_shared/windows.md`): a heredoc/here-string fails `gh
    pr create --body` on at least one platform this repo supports.

    Returns the PR URL parsed from the last non-blank line of `gh`'s stdout
    (what `gh pr create` prints on success), or `None` if `gh` fails -- NEVER
    raises. A failed PR-open is a reportable fact, not a fault.
    """
    root = Path(root).resolve()
    pr_title = title if title is not None else f"chore: close {work_id}"
    pr_body = body if body is not None else ""

    fd, body_file = tempfile.mkstemp(suffix=".md", prefix="spine-pr-body-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(pr_body)
        proc = subprocess.run(
            ["gh", "pr", "create", "--title", pr_title, "--body-file", body_file, "--head", branch],
            cwd=str(root), capture_output=True, text=True,
        )
    finally:
        with contextlib.suppress(OSError):
            os.unlink(body_file)

    if proc.returncode != 0:
        return None

    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else None
