# Worktree-Isolation Real Fix Design

**Issue:** [#33](https://github.com/fredcai6/constellation-skills/issues/33) — Dispatch doctrine: Agent-tool worktree isolation is a no-op on Windows — verify or serialize

**Date:** 2026-06-24

## Problem

The Agent-tool `isolation:"worktree"` parameter is a **harness primitive**, and on
Windows it is silently a **no-op**: subagents launched with it run in the shared
checkout instead of receiving their own git worktree. The Admiral dispatches a
parallel wave believing each Commander is isolated; on Windows they all collide in
the single checkout. Two **independent** field projects hit this:

1. **network_elo** — two Commanders launched in one turn both operated in the
   shared checkout; one left staged-only work, the other pushed (a near-race).
2. **story_time** — three parallel subagents shared the main checkout and collided
   on `git checkout -b`; one commit landed on a sibling's branch.

This is a correctness / data-loss risk, not friction: any Admiral run relying on
`isolation:"worktree"` for parallel dispatch on Windows will collide.

Constellation cannot patch the harness. The Agent-tool dispatch does **not** pass
through the checklist engine or `run_crew.py`, so there is no chokepoint at which a
hard gate could refuse — enforcement here is necessarily Admiral discipline,
backed by a mechanical check.

**Why not detect-and-serialize.** The issue's first proposal was to verify
isolation after launch and, if absent, fall back to sequential dispatch. That
permanently surrenders parallel throughput on the main development platform — a
workaround, the exact "confirmed into a permanent workaround instead of fixed"
pattern the fold-back arc exists to stop. It also cannot be preflight-verified: a
git-level probe (`git worktree add` in a temp dir) tests *git's* worktree support,
which is fine on Windows — it is the Agent *tool* that skips provisioning — so a
git probe returns a false GREEN.

## Strategy

**Stop trusting the flag; provision worktrees explicitly.** `git worktree add`
works fine on Windows. The Admiral runs it itself before a parallel wave, creating
one real worktree per Commander, and hands each Commander its **absolute workspace
path** in the LAUNCH_ORDER. Isolation becomes real and parallelism is preserved.

Manual provisioning dissolves the silent-no-op problem: `git worktree add` either
succeeds (a real, distinct worktree) or errors loudly. The residual risk shifts
from "did isolation take?" to **"is each Commander actually operating inside its
assigned worktree, or did it ignore the cwd and run git in the shared checkout?"**
A small verify helper turns that — and the Admiral's pre-wave "are these N
worktrees real and distinct?" check — into clean mechanical assertions.

## Behavior

### Component 1 — `scripts/verify_worktree_isolation.py`

Named to parallel the existing `scripts/verify_state_note.py`. Two modes:

- **`verify_worktree_isolation.py PATH [PATH ...]`** — the Admiral's post-provision
  gate, run before launching the wave. Assert every PATH:
  - exists on disk, and
  - is a **registered** git worktree (parsed from `git worktree list --porcelain`),
    and
  - all PATHs are **distinct** from each other **and from the primary (main)
    checkout**.

  Exit `0` on pass; exit `1` with a human-readable reason on the first failure
  (e.g. `"<path> is not a registered worktree"`, `"<path> is the main checkout — not
  an isolated worktree"`, `"paths <a> and <b> resolve to the same worktree"`).

- **`verify_worktree_isolation.py --here EXPECTED`** — the per-Commander first-step
  self-check. Assert `git rev-parse --show-toplevel` equals EXPECTED. Answers "am I
  really in my worktree, or did I land in the shared checkout?" Exit `0`/`1`; on
  mismatch the message names both the actual and expected toplevel and instructs
  the Commander to run all git ops in its assigned worktree.

**Internals as pure, separately-testable units** (the gate-vs-stamp aesthetic from
\#32):

- `normalize_path(p) -> str` — resolve to an absolute real path and fold Windows
  case and separators (`C:/Programs/x` and `C:\Programs\X` must compare equal). The
  fiddliest, most bug-prone piece; tested directly.
- `parse_worktree_list(porcelain) -> list[str]` — the registered worktree paths
  (the `worktree ` lines of `git worktree list --porcelain`).
- `primary_worktree(porcelain) -> str` — the primary/main checkout (the first
  entry).
- `check_distinct_real(expected, registered, primary) -> (ok: bool, reason: str)` —
  the pure decision for the multi-path mode.
- `check_here(actual_toplevel, expected) -> (ok: bool, reason: str)` — the pure
  decision for `--here`.

The CLI `main(argv)` shells out to git (`git worktree list --porcelain`,
`git rev-parse --show-toplevel`) and delegates to the pure helpers, returning the
exit code. The decision logic is therefore unit-testable without git; one
integration test exercises a real `git worktree add`.

### Component 2 — doctrine + template

- **`skills/admiral/references/fleet-doctrine.md`** — a new dedicated section
  stating the doctrine: worktree isolation is a harness no-op on Windows; the
  Agent-tool `isolation:"worktree"` flag does **not** provision; the Admiral runs
  `git worktree add` itself, hands off the absolute path, verifies with
  `verify_worktree_isolation.py`, and sweeps worktrees on closeout. Framed as
  correctness / data-loss doctrine, not a buried engine quirk.

- **`skills/admiral/templates/LAUNCH_ORDER.template.md`** — upgrade the existing
  `## Workspace` field from a vague `<worktree path, branch name, base commit>` to:
  the **provisioned** absolute worktree path + branch + base commit, plus an
  explicit first-step instruction to run
  `verify_worktree_isolation.py --here <path>` before any git operation. This
  replaces the issue's "add a `worktree isolation verified: yes/no — if no,
  sequential required` pre-ruling field": under manual provisioning isolation is
  always real, so the field becomes a self-check, not a sequential-fallback flag.

- **`skills/admiral/SKILL.md`** — line 38 ("One Commander per issue, each in an
  isolated worktree") updated to reflect explicit provisioning + verify rather than
  relying on the Agent-tool flag; the closeout sweep (line 54, "worktrees swept")
  reinforced with `git worktree remove` + `git worktree prune`.

## Testing

- **Task 1 (TDD).** Unit tests for the pure helpers:
  - `normalize_path` folds a `C:/`-form vs `C:\`-form path to equal, and folds
    case on Windows.
  - `parse_worktree_list` extracts exactly the registered paths from porcelain
    text; `primary_worktree` returns the first entry.
  - `check_distinct_real` passes for N distinct registered non-primary paths;
    fails when a path is unregistered, when a path equals the primary checkout,
    and when two expected paths resolve to the same worktree.
  - `check_here` passes on a match and fails on a mismatch, naming both paths.
  - One integration test: `git worktree add` a real worktree in a temp repo and
    assert the multi-path mode passes for it and `--here` passes from inside it.

- **Task 2.** Doc fidelity — the three doctrine/template edits reviewed against
  this spec; the LAUNCH_ORDER `## Workspace` field and the fleet-doctrine section
  must name `verify_worktree_isolation.py` and the `git worktree add` provisioning
  step exactly.

## Out of scope (YAGNI)

- **No detect-and-serialize fallback.** Manual provisioning makes isolation real,
  so a sequential-dispatch fallback is unnecessary.
- **No `worktree_pool.py` lifecycle tool.** Provisioning and cleanup are plain
  `git worktree add` / `remove` / `prune` commands in doctrine; a wrapper would be a
  thin shell over git.
- **No change to `run_crew.py`'s registry.** Its dedup keys on
  `work_id/gate/role/worktree`; it is not a dispatch chokepoint and the collision
  cases (Commander-level and crew-level) are addressed by provisioning + verify.
- **No `--json` output** from the verify helper; a human-readable message plus exit
  code is sufficient for its callers (the Admiral and each Commander).
