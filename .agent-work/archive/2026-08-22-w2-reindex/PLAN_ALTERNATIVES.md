# Design-it-twice Brief: w2-reindex pre-commit hook mechanism

## The one thing being designed twice

The gate plan for making `map/INDEX.md`/`map/ids.jsonl` correct by construction via a git
pre-commit hook — specifically, **how the hook decides what to (re)build and whether it is safe to
stage**, which is the load-bearing decision the rest of the plan hangs off.

## Count and panel — a surfaced choice

N=2, single pass (not a panel). This is a fairly-easy, bounded mechanism call (one hook, three
fenced files/dirs, no architecture-spanning interface) — not a load-bearing corpus interface or an
architecture-touching plan. Panel-vs-single record: **single**, per the weight-scaling guidance
("a fairly-easy call may run two candidates"). Untaken road: a 3-candidate panel was not run; the
two constraints below already produce maximal contrast on the one load-bearing decision (skip vs.
snapshot), so a third candidate was judged to add cost without adding a genuinely new axis.

## The constraints (one per agent, each distinct and named)

- **smallest-diff** — minimize new moving parts and diff size.
- **most-testable** — maximize how much of the new behavior is unit-testable in isolation, without
  a real `git commit` subprocess for every case.

Both candidates independently investigated the repo (not just the brief) and independently
reproduced, with real scratch-git experiments, the exact partial-commit hazard the launch order
named as the sharpest known risk — this convergence is decided with two independent confirmations
of the same underlying mechanism, not one agent's untested claim.

## Compared on

- **Depth** — does the mechanism hide the right complexity, or leak it upward into every caller?
- **Locality** — is the change contained, or does it fan out?
- **Seam placement** — is the boundary drawn where callers/tests actually want it?
- **Testability** — can each pathway (fresh / stale / partial-pathspec-commit / partial-hunk-commit
  / unrelated-dirty-file) be exercised and falsified on its own?

## Candidates, side by side

Both candidates converge on: a fail-open shim in `scripts/hooks/` mirroring
`gauge_writer_hook.py`'s documented always-exit-0 contract; an explicit two-path `git add --
map/INDEX.md map/ids.jsonl` (never a glob/`-A`) as the auditable-staging mechanism; installer
wiring in `install_constellation.py` guarded by the existing self-install pattern
(`is_self_install`, the precedent already used for `.mcp.json` wiring); resolving the hooks
directory via `git rev-parse --path-format=absolute --git-path hooks` (never a hardcoded
`<root>/.git/hooks` join) because **this very repo is itself a linked worktree** whose `.git` is a
pointer file into the main checkout's shared `.git/hooks/` — both candidates independently
discovered and empirically verified this, and a hardcoded join would have silently written into a
nonexistent path for this exact dev environment; and zero edits to
`tests/test_code_map.py::MapTreeFreshnessTests`.

They diverge on exactly one axis — **what the hook does when something else in the tree is dirty**:

- **smallest-diff**: computes `git status --porcelain=v1 --untracked-files=no -- ':!map/INDEX.md'
  ':!map/ids.jsonl'`; if **any** other tracked path shows worktree-vs-index divergence, the hook
  no-ops entirely (no build, no stage) and leaves that commit to the existing
  `MapTreeFreshnessTests` backstop. When nothing else is dirty, this is provably equivalent to
  building from what will be committed (reproduced against both `git commit -- <path>` and split-hunk
  `git commit -p`). Three gates, zero new files inside `scripts/code_map/`.
- **most-testable**: builds from an **index snapshot** — `git write-tree` → `git commit-tree` → `git
  worktree add --detach` — so the build input is provably the tree about to be committed,
  regardless of what else is dirty in the working tree. Reproduced correct against both
  partial-commit shapes AND against an unrelated dirty sibling file. Eight gates, a new
  `scripts/code_map/build.py` seam and `scripts/code_map/precommit.py` module.

## Framing block (presented at convergence, not before — both candidates already ran)

- **Constraints in play**: smallest-diff (fewest moving parts) vs. most-testable (each pathway
  independently falsifiable). Both held fixed: fail-open, exact-two-path staging, unmodified
  freshness test, self-install-only wiring, worktree-aware hooks-dir resolution.
- **Dependencies**: both touch only `scripts/hooks/`, `scripts/install_constellation.py`,
  `tests/`; most-testable additionally touches `scripts/code_map/` (a new seam + module), still
  inside the launch order's fence.
- **Illustrative sketch — not a proposal, offered only to prime the comparison**: a hook that
  "just reruns the build and stages if different" is the naive baseline both candidates started
  from and both rejected once the partial-commit reproduction showed it silently corrupts an
  intentionally-partial commit.

## Output — recommendation

**most-testable's mechanism wins on the merits of the mission itself, carried forward with
smallest-diff's leaner gate granularity.** Reasoning:

The launch order's mission is explicit: "so the index is correct by construction and **nobody
discovers staleness after a merge**." smallest-diff's skip-on-any-other-dirty-file rule means the
hook silently does nothing whenever the author has *any* unrelated unstaged edit sitting in the
tree — a common, ordinary state during real development (a half-finished edit in a second file,
notes left uncommitted), not an edge case. On that common path, the hook contributes nothing and
the exact failure this epic exists to close — a commit whose map silently goes stale, discovered
later — recurs, just less often than today rather than never. most-testable's index-snapshot
mechanism closes the same hazard **without** that conditional retreat: it produces a correct build
from exactly what is about to be committed on every commit shape, dirty-sibling-file or not. That
is the difference between "usually correct by construction" and "correct by construction," and the
mission asked for the latter.

The cost most-testable pays — `write-tree`/`commit-tree`/`worktree add` machinery — is git-native
(reuses git's own object model, not a hand-rolled staleness detector: hash manifests and mtime
tracking were the actual bespoke-machinery alternatives, and neither candidate proposed either),
and both candidates independently verified it works correctly from inside a linked worktree (this
repo's own layout), so the "smallest-diff" objection to it is weaker than it first appears — it is
more code, not more *kinds* of mechanism.

**Gate granularity is trimmed toward smallest-diff's 3-gate shape**, not most-testable's 8, for
practical reasons this brief is allowed to weigh even though they are not a comparison axis:
crew-dispatch cost scales with gate count (each gate is a real implement+review+integrate round
trip), and most-testable's 8 gates mostly split apart *tiers of tests over the same production
code* (Gates 1-4 are all "test the precommit library," Gates 5-8 are all "test the shim/installer/
end-to-end"), which one well-scoped implement+review pass per production unit can carry without
losing any of the individual test cases most-testable enumerated — they become one gate's
required-evidence list instead of four gates' close-criteria. Converged plan: **3 gates** — (1)
precommit library (build seam + index-snapshot mechanism + staleness/stage logic + fail-open shim,
unit-tested against scratch repos covering every pathway most-testable named), (2) installer wiring
(self-install guard, worktree-aware hooks-dir resolution, idempotent, refuse-clobber), (3)
end-to-end red/green proof against a real scratch clone of this repo at the shipped SHA (including
both partial-commit shapes and the shared-worktree-hooks case) plus the unmodified-backstop
regression check.

## Untaken roads — loud skips

- **A 3-candidate panel** was not run — single-pass-of-2 was judged sufficient for this weight (see
  Count and panel above).
- **smallest-diff's skip-on-dirty rule** was not carried forward as the shipped mechanism — it is a
  real, correct, much simpler design, but it does not fully satisfy the mission's "correct by
  construction" framing, only "usually correct." Its investigation (the `git status --porcelain`
  safety check, its empirical validation, and its exact reproduction commands) remains valuable
  and is preserved in `plan-candidate-smallest-diff.md` for the record.
- **most-testable's finer 8-gate split** was not carried forward as-is — merged into 3 gates for
  crew-dispatch economy; every individual test case either candidate named is preserved in
  `execute.json`'s required-evidence lists, none dropped.

## Panel-vs-single record

Single (N=2, no panel) — restated: a fairly-easy, bounded mechanism call, not architecture-touching
at the corpus scale, so a panel was judged unnecessary. This scaling call is open to the Admiral to
overturn if that read is wrong, per the delegated-mode surfacing requirement.
