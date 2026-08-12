#!/usr/bin/env python
"""Open Constellation work in one call: a worktree, a branch, a scaffolded work
area, and a compiled, origin-stamped spine -- instead of a caller that must
already know the worktree/branch convention and hand-drive `git worktree add`,
`init_work_area.py` and `generate_spine.py` itself.

Frozen contract: `.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md`, sections 2
and 3. This gate ships `open_work` and the pure helpers only -- `close_work` is g2's,
and no MCP door wiring happens here (g3).

Pure/impure split at FUNCTION granularity, matching `generate_spine.py`,
`validate_spine.py` and `checklist_engine.py`:

- `worktree_path_for`, `branch_name_for`, `archive_name_for`, `build_origin` are
  PURE: dict/str in, dict/str out, no `Path`, no `open`, no `subprocess`.
- `open_work` is impure and does the real work: it validates, refuses an occupied
  worktree or an already-active engine session, runs `git worktree add`, scaffolds
  the work area, compiles the spine (`generate_spine`, imported, never
  re-implemented), injects `origin`, re-validates, and self-verifies isolation --
  rolling back everything it created on any failure at or after `git worktree add`.
"""

from __future__ import annotations

import contextlib
import json
import os
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
    unchecked. `_rollback`'s only caller: best-effort cleanup must never itself
    fail the rollback it is part of."""
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


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
