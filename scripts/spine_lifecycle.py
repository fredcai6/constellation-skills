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
- `close_work` is impure: it calls `closeout_refusal` and, if refused, does
  nothing at all; otherwise it `git mv`s every top-level entry under the work
  area except the bound spine and its journal, then `git mv`s those two last,
  then commits. It never advances, releases, opens a PR, or removes a
  worktree -- those are the caller's, before and after this call.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_spine  # noqa: E402
import init_work_area  # noqa: E402
import run_crew  # noqa: E402
import validate_spine  # noqa: E402
import verify_worktree_isolation  # noqa: E402


class SpineLifecycleError(Exception):
    """A refusal: `open_work` could not proceed. Nothing it created survives."""


# --------------------------------------------------------------------------- #
# pure helpers -- dict/str in, dict/str out; no Path, no open, no subprocess
# --------------------------------------------------------------------------- #

def worktree_path_for(work_id: str, *, wt_root: str) -> str:
    """`<wt_root>/<last segment of work_id>`. The worktree name is the FINAL
    `/`-separated segment only -- `epic-559/c3-lifecycle` names a worktree
    called `c3-lifecycle`, matching the live convention measured against this
    run's own worktree."""
    last_segment = work_id.rsplit("/", 1)[-1]
    return os.path.join(wt_root, last_segment)


def branch_name_for(work_id: str) -> str:
    """The branch name: `work_id` verbatim -- matches every branch in this
    epic."""
    return work_id


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
    resolve, never guessed here."""
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


# --------------------------------------------------------------------------- #
# open_work -- impure. Order per LIFECYCLE_CONTRACT.md section 3; nothing
# survives a failure at or after `git worktree add`.
# --------------------------------------------------------------------------- #

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_wt_root(root: Path) -> str:
    """A sibling of the main checkout named `<repo-dir>-wt` -- measured against
    the live tree: `/home/tommy/projects/constellation-skills` pairs with
    `/home/tommy/projects/constellation-skills-wt`."""
    return str(root.parent / f"{root.name}-wt")


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
        "SPINE_SESSION": f"constellation/{work_id}",
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
