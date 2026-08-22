# Implementation Result

## Assigned gate
g1 (g1-implement) — precommit library: index-snapshot build, staleness/stage, fail-open shim

## Completed slice
`scripts/code_map/build.py` (new `build(root, *, artifacts=None, out=None) -> int` seam),
`scripts/code_map/cli.py`'s `_build(args)` refactored to delegate to it, `scripts/code_map/precommit.py`
(the index-snapshot mechanism, end to end), and `scripts/hooks/code_map_precommit.py` (the fail-open
git hook shim) — plus `tests/test_code_map_precommit.py` covering every case the handoff named.

## Scope
**Files changed:**
- `scripts/code_map/build.py` (new)
- `scripts/code_map/cli.py` (one-line `_build` delegation)
- `scripts/code_map/precommit.py` (new)
- `scripts/hooks/code_map_precommit.py` (new)
- `tests/test_code_map_precommit.py` (new)

**Specific exclusions touched:** no — `scripts/install_constellation.py`, `tests/test_code_map.py`,
`generate_spine.py`, `specs/`, `scripts/checklist_engine.py`, and no real `git commit`/`.git/hooks/`
install against this repo's own state.

## Behavior changed
Yes — new capability, no existing behavior altered. `cli.py`'s `build` subcommand keeps its exact
observable behavior (proven byte-identical, see Evidence); nothing outside `scripts/code_map/` and
`scripts/hooks/` was touched.

## Map Impact
- **Structural anchors touched:** `scripts/code_map/cli.py:_build` — now a two-line delegation to
  the new `scripts/code_map/build.py:build` seam; `scripts/code_map/build.py` and
  `scripts/code_map/precommit.py` are new structural units under `scripts/code_map/`;
  `scripts/hooks/code_map_precommit.py` is a new structural unit under `scripts/hooks/` (existing
  precedent directory, alongside `gauge_writer_hook.py`/`spine_rail.py`).
- **Capabilities added:** a plain-importable `build()` library seam (previously CLI-only); an
  index-snapshot pre-commit mechanism (`precommit.run_precommit`/`precommit.main`) that rebuilds
  `map/INDEX.md`/`map/ids.jsonl` from exactly the git INDEX about to be committed, never the working
  tree; a fail-open git hook shim with dynamic per-worktree module resolution.
- **Constraints/assumptions touched:** `tests/test_code_map.py::MapTreeFreshnessTests` (the
  Protected Intent) stays byte-identical and green — this gate's whole point is to make the
  staleness it catches rare by construction, never to weaken it. `scripts/code_map/discovery.py`
  reads corpus membership from `git ls-files` (index/tracked-aware) while `extract.py` reads file
  *bodies* straight off disk (`os.path.join(root, rel)`) — that mismatch between the two is exactly
  why a real working tree can't be built against directly for a partial commit, and is the reasoning
  the index-snapshot mechanism exists to close.
- **Decision candidates / resolved decisions:** confirmed live (not just asserted) that
  `render.py:repo_name()` names a build after the git-common-dir's parent directory, not the
  building worktree's own directory — this is what makes build output byte-identical between a
  build run directly against a repo and a build run against an ephemeral worktree snapshot of that
  same repo, which the whole copy-back mechanism depends on.
- **Trust limitations / drift found:** none in shipped code. One planning-time ambiguity resolved by
  measurement, not left open: see Workflow Feedback's first two entries (the "build() call if it
  shells out" timeout clause, and the threading-based concurrency test hazard).
- **Triage candidates:** `scripts/code_map/discovery.py:tracked_python_files`'s `git ls-files`
  subprocess call has no `timeout=`. Out of this gate's scope (discovery.py is read-only reference
  material here) but worth a follow-up if `build()` is ever called somewhere a hang would matter
  more than it does inside this mechanism's own already-bounded worktree.

## Test mode
**Required:** test-after
**Satisfied:** yes — every new function is covered by a real test against a disposable scratch git
repo (`tempfile.TemporaryDirectory()`); none touches this repo's own git state.

## Evidence

```bash
python -m pytest tests/test_code_map_precommit.py tests/test_code_map.py -q
```
**Result:** pass — `161 passed, 65 subtests passed` (run just before this write; the precommit suite
alone: `13 passed, 2 subtests passed`).

```bash
git diff -- tests/test_code_map.py
```
**Result:** empty (zero byte changes), as required.

**Wiring grep** (from the handoff):
```bash
grep -rn "build(" --include=*.py scripts/code_map/ | grep -v "def build"
grep -rn "code_map_precommit\|scripts\.code_map\.precommit" --include=*.py . | grep -v "def \|tests/test_code_map_precommit.py"
```
- `build(` real call sites (excluding prose/docstrings): **2** — `scripts/code_map/cli.py:91`
  (`_build`'s refactor) and `scripts/code_map/precommit.py:111` (the mechanism's own call). Matches
  the handoff's expectation exactly.
- `code_map_precommit`/`scripts.code_map.precommit` real (non-docstring) references outside the new
  test file: **1** — `scripts/hooks/code_map_precommit.py`'s own `importlib.import_module(...)`
  call. As the handoff names explicitly, installer wiring (gate 2) is what gives the shim a real
  caller (`git commit`) — zero external-to-this-gate callers is expected, not a defect, at this gate.

**Timing re-measurement** (handoff flagged the 2.9s build-only baseline as unverified for the full
mechanism): ran the full `run_precommit()` — write-tree, commit-tree, worktree add, `build()` over
this repo's own real corpus (175 modules, 176,954 statements), copy-back comparison, worktree
remove — against a local clone of this repo (never this repo's own git state), landing on a
no-op result to isolate mechanism overhead cleanly. Two runs: **3.77s** and **3.25s**. The
`build()` step itself was previously measured at ~2.9s baseline, so the worktree-lifecycle overhead
(write-tree/commit-tree/worktree add+remove) on top of it is on the order of a few hundred
milliseconds to under a second — still fast and well within what a pre-commit hook can absorb
without a perceptible UX cost.

## TDD evidence, if required
Test-after, not TDD — no red/green cycle required or performed. Each new function was implemented
first, verified manually against a real scratch repo end to end (write-tree/commit-tree/worktree
add/build/copy-back/stage/cleanup, fresh then stale), then covered by the corresponding test in
`tests/test_code_map_precommit.py`.

## Docs/contracts touched
- None. `build()`'s signature and `precommit.run_precommit`/`precommit.main`'s signatures are new
  public-ish surface but nothing external depends on them yet (gate 2 is the first real caller).

## Assumptions
- `MANAGED_PATHS = ("map/INDEX.md", "map/ids.jsonl")` is the complete and permanent set of
  git-tracked map artifacts in this repo (confirmed via `git ls-files map/`), matching
  `MapTreeFreshnessTests`'s own scope exactly.
- A real `git commit`'s pre-commit hook always runs as its own fresh OS process (never a persistent
  daemon reusing one Python interpreter across commits) — this is what makes the shim's per-worktree
  dynamic `sys.path`/`importlib.import_module` resolution safe without extra `sys.modules` cache
  invalidation; see Workflow Feedback for where this assumption surfaced.

## Stop conditions hit
None. The Honest-Null escape hatch was considered (see Workflow Feedback) but not triggered — the
mechanism's concurrency and timeout properties hold under the corrected, realistic test shape.

## Out-of-scope observations
- `scripts/code_map/discovery.py:tracked_python_files`'s `git ls-files` call has no `timeout=` (see
  Map Impact's Triage candidates line above) — read-only reference material at this gate, flagged
  for a future gate/triage rather than fixed silently.

## Workflow Feedback

- **Handoff gaps:** the Timeout spec's phrase "the `build()` call if it shells out" doesn't quite
  fit the shape `build()` ended up taking: it's a plain in-process Python call from `precommit.py`
  (no `subprocess.run` at that call site), so no `timeout=10` literally applies there — the timeout
  coverage is fully satisfied by the 5 git subprocess calls (`prune`, `write-tree`, `commit-tree`,
  `worktree add`, `git show` ×2, `git add`, `worktree remove`) that DO go through the injectable
  `runner`. Worth tightening the spec's wording for the next crew that reads it literally and
  wonders where `build()`'s own timeout parameter is supposed to live.
- **Context rediscovered:** the required-evidence line "two mechanism calls launched...via threading"
  reads as an implementation suggestion, but threading against ONE shared worktree path actually
  manufactures two hazards a real deployment never hits: `extract.py`'s module-level `TABLES`/`ROOT`
  globals cross-talking across threads sharing one interpreter, and two processes fighting over one
  shared `.git/index.lock` on `git write-tree` for the same worktree. Real concurrent `git commit`s
  are separate OS processes on separate SIBLING WORKTREES (the handoff's own framing throughout),
  each with its own per-worktree index since git 2.5 — so the test was built as two real subprocess
  invocations against two sibling worktrees instead, which is both realistic and reliably green
  (verified across 15+ consecutive runs). This took real investigation to track down (an initial
  green run, then an intermittent failure, then a reproducible one) rather than being obvious from
  the handoff text.
- **Instructions improvised around:** none beyond the timeout-wording note above — the mechanism
  spec (steps 1-6, the fail-open contract, the diagnostic-line rules) mapped onto working code
  directly with no redesign needed.
- **What would have made this easier:** naming the "two sibling worktrees, not two threads against
  one path" shape explicitly in the Required Evidence's concurrent-invocation bullet would have
  saved the one detour above; everything else in the spec was precise enough to implement without
  guessing.
- **Stop hook misfire (recorded, not acted on):** this crew's `SPINE_FILE`/`SPINE_SESSION` env pointed
  at the parent Commander's `spine.json` (lease held by `commander`), not at anything bound to this
  crew (`crew-runs.json` records `spine: null` for this attempt) — confirmed via `spine_status`
  before doing any planning work. I authored and drove my own `IMPLEMENTER_PLAN.json` via the CLI
  (`scripts/checklist_engine.py --file <own plan>`) instead, per the standing rule that a
  `run_crew.py`-dispatched crew with `spine: null` must never drive its dispatcher's spine. After
  this plan reached `DONE: no open items` and its lease was released, the Stop hook fired the
  Commander's `execute` gate imperative at this session repeatedly (reload the commander skill,
  drive `execute.json`, dispatch further crews via `run_crew.py`) — that is the Commander's own
  work, not this implementer's, and acting on it here would mean one dispatched crew mutating or
  driving its parent's live spine out from under it. Refusing and recording this here, per
  doctrine, rather than complying with the hook or seizing the parent's lease.

## Return status
`complete`
