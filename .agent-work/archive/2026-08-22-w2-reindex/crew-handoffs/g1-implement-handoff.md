# Implementer Handoff

## Gate
g1 (g1-implement) — precommit library: index-snapshot build, staleness/stage, fail-open shim

## Task
Build the library that makes `map/INDEX.md` and `map/ids.jsonl` correct by construction: a
plain-importable `build()` seam, an index-snapshot mechanism that regenerates the map from exactly
what is about to be committed (never the live working tree), and a fail-open git-hook shim that
calls it. This is gate 1 of 3 in a larger mission (epic #569, "w2-reindex") — gates 2 (installer
wiring) and 3 (end-to-end proof) come after and depend on what you build here, but you do not touch
`scripts/install_constellation.py` or run a real `git commit` against the real repo in this gate.

## Protected Intent
`tests/test_code_map.py::MapTreeFreshnessTests` (~line 4656) is the existing backstop that keeps
`map/INDEX.md`/`ids.jsonl` honest — it rebuilds from tracked source and byte-compares against the
committed files. It must stay byte-identical to its current form. This gate's whole job is to make
staleness rare by construction, never to weaken the thing that catches it when it happens anyway.

## Test Mode
TDD not required, but every new function must be covered by a real test against a disposable
scratch git repo before this gate closes — see Required Evidence. Test-after is fine; untested is
not.

## Close Criteria
- `scripts/code_map/build.py` exists: `build(root, *, artifacts=None, out=None) -> int`, a plain
  Python function (no `argparse`) wrapping the same `extract`/`render` calls
  `scripts/code_map/cli.py`'s `_build(args)` makes. `cli._build` is refactored to call this new
  `build()` — one build path, not two that can drift. Byte-identical output to today's CLI for this
  repo's own tree (prove it).
- `scripts/code_map/precommit.py` exists and owns the mechanism below, end to end.
- `scripts/hooks/code_map_precommit.py` exists: the fail-open shim, no CLI args, resolves
  `repo_root` via `git rev-parse --show-toplevel` from `cwd` at run time (dynamic, per invoking
  worktree — never a path baked in at install time; a hook shared across sibling worktrees on
  different branches must always import each worktree's own copy of this module).
- `tests/test_code_map.py` has **zero byte changes** — `git diff -- tests/test_code_map.py` is
  empty at this gate's close.
- Zero changes to `scripts/code_map/discovery.py`, `extract.py`, `render.py` internals (read-only).

## Mechanism — exact specification (do not redesign; every piece below closes a specific gap a
cold plan critic found in an earlier draft — implement precisely, do not improvise a substitute)

1. Opportunistically run `git worktree prune` first (self-heals admin residue from any prior
   crashed run).
2. Snapshot the **index**, not the working tree: `git write-tree` → `git commit-tree <tree> -p HEAD
   -m <marker>` (a dangling, non-ref-touching commit — never touches any ref) → `git worktree add
   --detach <unique-path> <that commit>`, where `<unique-path>` comes from
   `tempfile.mkdtemp(prefix="code-map-precommit-")` **every invocation** (never a fixed name — this
   is what makes two concurrent invocations from sibling worktrees collision-free: each gets a
   distinct worktree-admin entry, and `git worktree add` with distinct target paths does not
   collide even under concurrent load).
3. Run `build()` (from step/Close-Criteria item 1) against that ephemeral worktree.
4. **Copy-back is plain file I/O, not git plumbing**: read the built `map/INDEX.md` and
   `map/ids.jsonl` bytes from the ephemeral worktree, write those bytes to the same two paths in
   the REAL working tree (`repo_root` from step 2's dynamic resolution), comparing against the
   currently staged blobs (`git show :map/INDEX.md`, `git show :map/ids.jsonl`) to decide which of
   the two actually changed.
5. `git add -- map/INDEX.md map/ids.jsonl` in the real repo, naming **only** the paths that
   changed — never a directory or glob add, never any other path. This is what makes "exactly two
   paths, never an unrelated file" true by construction: no step in this mechanism ever writes or
   stages any other path.
6. Remove the ephemeral worktree (`git worktree remove --force <unique-path>`) in a `finally` block
   **inside** the outer `try/except` (see Timeout/fail-open below), so cleanup runs on every path
   including the fail-open path; a cleanup failure is itself swallowed and logged, never allowed to
   propagate or block anything.

## Timeout — exact specification
Every subprocess call in the mechanism (`write-tree`, `commit-tree`, `worktree add`, the `build()`
call if it shells out, `worktree remove`, `worktree prune`) passes an explicit `timeout=10`
(seconds) to `subprocess.run`. A `subprocess.TimeoutExpired` is caught by the same outer
`try/except` as any other exception → the same fail-open exit. A hang must never block a commit any
more than a crash does — this is the single most important property of this gate; test it directly
(see Required Evidence).

## Fail-open contract — exact specification
The shim's entire body (including the `finally`-block cleanup) is wrapped in one broad `try/except
Exception`. Any exception, including `subprocess.TimeoutExpired`, results in exit 0 — never
nonzero, never a hang past the timeout budget. On every fail-open exit, print exactly one
diagnostic line to stderr naming what was swallowed (git shows hook stderr on a normal commit
without failing it — zero UX cost). On the no-op path (nothing stale), print nothing. On the
fixed-staleness path, print one line naming the two paths staged.

## Allowed Scope
- New files: `scripts/code_map/build.py`, `scripts/code_map/precommit.py`,
  `scripts/hooks/code_map_precommit.py`, `tests/test_code_map_precommit.py`.
- One mechanical edit: `scripts/code_map/cli.py`'s `_build(args)` delegates to the new `build()`
  (behavior-preserving refactor, not a rewrite).
- Everything else in `scripts/code_map/` is read-only reference material.

## Specific Exclusions
- Do not touch `scripts/install_constellation.py` (gate 2's job).
- Do not touch `tests/test_code_map.py` (any byte).
- Do not run a real `git commit` against this actual repo's own git state, or install anything
  into this actual repo's real `.git/hooks/` — every test operates on disposable scratch repos
  under `tempfile.TemporaryDirectory()`. Real-installed-hook proof is gate 3's job.
- Do not touch `generate_spine.py`, `specs/`, the spec-to-template migration, `scripts/checklist_engine.py`,
  or any shipped spine template — out of this mission's scope entirely.
- Stdlib only — no new third-party dependency.

## Constraints
- Every git call inside `precommit.py` goes through an injectable `runner` parameter (default
  `subprocess.run`) — no bare module-level `subprocess.run` call — so a test can substitute a
  recording or a raising/sleeping fake without a real git binary for the fail-open/timeout tests.
- Honest-Null escape hatch: if the concurrent-invocation test or the forced-timeout test cannot be
  made to pass with the mechanism above (e.g. unique tempfile paths still collide under real
  concurrent load, or the timeout does not actually bound a real hang), STOP and return with Return
  status `blocked`, attaching the negative evidence — do not ship a hook whose own tests demonstrate
  it can corrupt state or hang under load. This has not been observed in prior investigation of this
  mechanism; it is a named contingency, not the expected outcome.

## Map Anchors (inbound)
This repo's map is DEGRADED-UNPARSEABLE (no citable anchor ids) — path anchors instead.
- **Map entry point:** `scripts/code_map/cli.py` (read `_build`/`HANDLERS["build"]` first), then
  `scripts/hooks/gauge_writer_hook.py` (the existing fail-open precedent to mirror), then
  `tests/test_code_map.py` lines ~4656+ (`MapTreeFreshnessTests` — read before writing anything,
  so you know exactly what must stay byte-identical).
- **Structural:** `scripts/code_map/` (checks.py, cli.py, discovery.py, extract.py, render.py,
  thresholds.py, `__main__.py`), `scripts/hooks/` (gauge_writer_hook.py, spine_rail.py).
- **Constraints/assumptions:** freshness test unweakened (hard); hook must never fail/block a
  commit (hard); staging must be auditable to exactly two paths (hard).
- **Decision anchors:** index-snapshot mechanism chosen over a simpler skip-on-dirty-sibling
  alternative, because only the snapshot approach is correct on every commit shape (partial
  pathspec commit, partial hunk commit, unrelated dirty sibling), not just the common case.
  `@grade: settled/measured · leans g1-implement,g1-review · settle: this gate's own
  concurrent-invocation and forced-timeout tests are the settlement evidence`
- **Evidence expectations:** the build is fast and deterministic (2.9s baseline, measured on the
  base commit) — re-time the real mechanism including worktree materialization in your evidence; do
  not assume it stays 2.9s.

## Deliverable Path Check
- **Committed** — `scripts/code_map/build.py`; verified `git check-ignore scripts/code_map/build.py` exit 1 (not ignored).
- **Committed** — `scripts/code_map/precommit.py`; verified `git check-ignore scripts/code_map/precommit.py` exit 1.
- **Committed** — `scripts/hooks/code_map_precommit.py`; verified `git check-ignore scripts/hooks/code_map_precommit.py` exit 1.
- **Committed** — `tests/test_code_map_precommit.py`; verified `git check-ignore tests/test_code_map_precommit.py` exit 1.
- All four are new files: they appear in `git status` as untracked until you `git add` them (not
  yet tracked at dispatch time).

## Required Evidence
New test file `tests/test_code_map_precommit.py`, every case its own disposable scratch git repo
under `tempfile.TemporaryDirectory()` — never this repo's own git state. Load-bearing (prove
rigorously): concurrent-invocation, forced-timeout, partial-commit (both shapes), auditable-boundary.
Confirmatory (a solid single test suffices): fresh/no-op, fail-open-on-exception, cleanup,
worktree-run-time-resolution.

- **Fresh/no-op**: map already matches the index → no stage, `git status` clean after.
- **Stale/rebuild-and-stage**: a staged source change makes the map stale → hook rebuilds, stages
  exactly the two paths.
- **Pathspec-restricted partial commit**: two tracked files change, only one staged via `git add
  <one>`, mechanism called directly → built map reflects only the staged file's effect; the
  unstaged sibling is untouched.
- **Hunk-restricted partial commit**: one file, two hunks, only one staged via `git apply --cached`
  (the same net index state `git commit -p` produces) → built map excludes the unstaged hunk's
  effect.
- **Unrelated-dirty-file audit**: a third tracked file dirty (staged or unstaged) throughout →
  `git diff --cached --name-only` after the mechanism runs is a subset of
  `{map/INDEX.md, map/ids.jsonl}`, never includes the third file.
- **Concurrent-invocation**: two mechanism calls launched against the same scratch repo at
  effectively the same time (e.g. via `threading`) → both complete successfully, no `git worktree
  add` collision, `git worktree list` shows zero residue afterward from either.
- **Forced-timeout**: a fake `runner` that sleeps past 10s on one subprocess call → shim still
  exits 0 within a bounded wall-clock window (assert under ~15s).
- **Forced-exception**: a fake `runner` that raises → shim exits 0, working tree otherwise
  unmodified, zero worktree/dangling-commit residue.
- **Worktree-run-time-resolution**: invoke the shim from a second worktree of the scratch repo
  whose checkout predates this feature (lacks `scripts/code_map/precommit.py` at that commit) →
  shim still exits 0 (fail-open covers the `ImportError` cleanly).
- Every exercised case asserts `returncode == 0` explicitly (the hook never exits nonzero under any
  condition tested).

A claimed test-failure distribution, if any test fails during development, must be derived
mechanically (`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), not summarized from
a glance.

## Wiring Grep
```bash
grep -rn "build(" --include=*.py scripts/code_map/ | grep -v "def build"
grep -rn "code_map_precommit\|scripts\.code_map\.precommit" --include=*.py . | grep -v "def \|tests/test_code_map_precommit.py"
```
State the count of call sites found for each. `build()` is called at minimum from `cli._build`
(the refactor) and from `precommit.py`; `code_map_precommit.py`/`precommit` module references are
expected only from the shim itself and the new test file at this gate — installer wiring (gate 2)
is what gives the shim a real caller (`git commit`); note that explicitly rather than treating zero
external-to-this-gate callers as a defect at this gate.

## Verification Commands
```bash
python -m pytest tests/test_code_map_precommit.py tests/test_code_map.py -q
git diff -- tests/test_code_map.py
```
The second command's output must be empty.

## Suggested Model Tier
stronger — reason: the index-snapshot/timeout/concurrency mechanism has several load-bearing
correctness properties (no data corruption under partial commits, no hang, no collision under
concurrency) that reward careful reasoning over a fast bounded edit.

## Authority
The mechanism design (index-snapshot, unique tempfile worktree paths, per-subprocess timeouts,
plain-file-I/O copy-back, fail-open with one-line stderr diagnostic) is already decided — see
`.agent-work/w2-reindex/PLAN_ALTERNATIVES.md` and `.agent-work/w2-reindex/PLAN_CRITIC.md`'s
Commander disposition section for the full reasoning. Do not re-litigate the choice of mechanism;
implement it. Implementation-shape details not pinned above (exact function names beyond what's
specified, internal helper structure) are yours to decide.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, the Honest-Null escape hatch above triggers, or a decision outside
this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT per `references/status-model.md`'s `Return status` field
(`complete | partial | blocked | out-of-scope | failed`, lowercase). Write the full result to
`.agent-work/w2-reindex/crew-handoffs/g1-implement-implementer-result.md` before ending your turn.
