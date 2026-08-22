# Review Result

## Assigned Gate
g1 (g1-review) — precommit library: index-snapshot build, staleness/stage, fail-open shim

## Result
`APPROVE`

## Handoff compliance
Yes. `scripts/code_map/build.py::build(root, *, artifacts=None, out=None) -> int` is a plain-importable
seam wrapping `extract.run`/`render.run`; `cli.py`'s `_build(args)` now delegates to it (one build path).
`scripts/code_map/precommit.py::run_precommit`/`main` implement the pinned 6-step index-snapshot
mechanism end to end. `scripts/hooks/code_map_precommit.py` is the fail-open shim with dynamic
per-worktree `repo_root` resolution and dynamic import. All required evidence is present and I
independently reproduced the load-bearing pieces of it (see Evidence verdict).

## Scope drift
None. `git status --porcelain` shows exactly the allowed scope: `scripts/code_map/cli.py` modified
(one-line `_build` delegation, read in full — genuinely mechanical, not a rewrite), plus the four new
files the handoff names. `git diff --stat` on `discovery.py`/`extract.py`/`render.py` is empty
(untouched). `git diff -- tests/test_code_map.py` is empty. `install_constellation.py`,
`generate_spine.py`, `specs/`, `checklist_engine.py`, and every spine template are untouched. No real
`git commit` or `.git/hooks/` install against this repo's own state.

## Evidence verdict
Satisfied, independently re-verified rather than trusted:
- `python -m pytest tests/test_code_map_precommit.py tests/test_code_map.py -q` → **161 passed, 65
  subtests passed** (re-run just now, matches the claim exactly).
- `git diff -- tests/test_code_map.py` → empty (re-run, confirmed).
- Wiring grep re-run: `build(` real call sites = 2 (`cli.py:91`, `precommit.py:111`); real
  `precommit`-module references outside the test file = 1 (the shim's own `importlib.import_module`).
  Matches the implementer's claim exactly.
- Re-ran `ConcurrencyTimeoutTests` specifically (the handoff's named safety-critical pair): 3 passed —
  `test_forced_timeout_still_exits_zero_within_bounded_window` took ~10s and the assertion (`< 15s`)
  held; `test_concurrent_invocations_do_not_collide` passed and re-ran clean 5× in a row.
- Went beyond re-running: patched a **scratch copy** of `precommit.py` to use a fixed worktree path
  instead of `tempfile.mkdtemp(...)` and launched two real concurrent subprocess invocations against two
  sibling worktrees (mirroring the test's own topology). This **did** collide — `git worktree add` failed
  with `fatal: '...' already exists` — proving the unique-tempfile-path property is genuinely load-bearing
  (the guard can fail) and that the shipped code's use of `tempfile.mkdtemp` is what prevents it, not a
  vacuously-green test. No residue left in this repo's own git state from that experiment (verified via
  `git worktree list`).
- Confirmed the concurrency test's topology claim directly by reading
  `test_concurrent_invocations_do_not_collide`/`_spawn_precommit_subprocess`: two real OS subprocesses
  (`subprocess.Popen`) against two `git worktree add --detach` siblings sharing one `.git`, not threads
  against one shared path — matches the implementer's Workflow Feedback reasoning about why threading
  would manufacture false hazards (`extract.py` module-level globals, index-lock contention) a real
  deployment never hits.
- Every subprocess call in `precommit.py` funnels through the single `_run(runner, ...)` helper with
  `timeout=_TIMEOUT` (10s); `subprocess.run` appears only as the `runner=` keyword default, never as a
  bare call. Confirmed by grep, not assumed.
- Fail-open contract confirmed by direct inspection and by the re-run forced-timeout/forced-exception
  tests: exactly one stderr line on the fail-open path, one line naming staged paths on the
  fixed-staleness path, nothing on true no-op.

## Code/doc quality
Minimal, matches the pinned mechanism precisely, stdlib-only (grep confirms), and the injectable-`runner`
constraint holds throughout. Fowler baseline pass run and rail-verified
(`scripts/verify_fowler_pass.py .agent-work/w2-reindex/FOWLER_PASS.json` exits 0): 10 of 12 smells
absent; `long-method` (`run_precommit`, ~60 lines) overridden — the handoff pins an exact numbered
6-step sequential mechanism ("implement precisely, do not improvise a substitute") and
`global-everyone.md`'s "no speculative abstraction" posture argues against splitting a single-caller
procedure into helpers with no second caller to justify the seam; `duplicated-code` flagged as a minor
observation (the fail-open diagnostic string is repeated verbatim between `precommit.py` and
`code_map_precommit.py`) — not a blocker, since the two catches guard genuinely different failure
domains per each file's own docstring, but worth noting as drift risk if the message format ever
changes in one copy and not the other.

## Map impact verdict
- **Evidence supports claimed change:** yes — independently confirmed, not just trusted.
- **Constraints not violated:** yes — `MapTreeFreshnessTests` untouched/green; the hard constraints
  (freshness test unweakened, hook never blocks a commit, staging auditable to exactly two paths) all
  hold under direct inspection and re-run tests.
- **Notes match the diff:** yes. I independently verified the specific mechanism claim in Map Impact
  (that `render.py:repo_name()`'s use of `git rev-parse --git-common-dir` — not the building worktree's
  own directory name — is what makes build output byte-identical between a direct build and a build run
  against an ephemeral worktree snapshot) by reading `render.py:599` directly rather than trusting the
  assertion.
- **Decision candidates surfaced:** none needed; no new decision required beyond what the handoff already
  settled.
- **Durable context routed:** yes — the out-of-scope triage candidate (`discovery.py:tracked_python_files`'s
  untimed `git ls-files` call) is flagged in this survey (`tc1`) and carried below, not fixed silently or
  dropped.

## Reconciliation check
No unreconciled divergence. Map is DEGRADED-UNPARSEABLE at this repo (no citable map anchors), so this
gate reconciles against path anchors only, as the handoff frames it.

## Blockers
- none

## Out-of-scope observations
- `scripts/code_map/discovery.py:tracked_python_files`'s `git ls-files` subprocess call has no
  `timeout=`. Read-only reference material at this gate; worth a follow-up if `build()` is ever called
  somewhere a hang would matter more than it does inside this mechanism's already-bounded ephemeral
  worktree. (Also flagged by the implementer; reconfirmed independently and carried as triage candidate
  `tc1` in the review survey.)
- Minor: the fail-open diagnostic string `"code-map-precommit: fail-open, swallowed: {exc!r}"` is
  duplicated verbatim between `scripts/code_map/precommit.py` and `scripts/hooks/code_map_precommit.py`.
  Not a blocker (see Code/doc quality), but a future edit to one copy's wording could silently drift from
  the other.

## Workflow Feedback

- **Handoff gaps:** none of substance. The implementer's own Workflow Feedback flagged that the Timeout
  spec's phrase "the `build()` call if it shells out" doesn't quite fit since `build()` ended up as an
  in-process call — I confirmed this reading is correct (no `subprocess.run` inside `build.py`) and agree
  the spec wording is worth tightening for the next crew that reads it literally.
- **Context rediscovered:** none — the g1-implement handoff, PLAN_ALTERNATIVES.md-derived rationale, and
  the implementer's result together carried enough context that nothing had to be dug up independently.
- **Instructions improvised around:** this crew's `SPINE_FILE`/`SPINE_SESSION` env resolved to the
  Commander's own `execute` gate, not a spine bound to this reviewer crew (`crew-runs.json`'s own entry
  for this crew records `spine: null`, `door_bound: true` — the third observed shape of this dispatch
  defect: no refusal on `spine_status`, but the mismatch is confirmed by the crew registry, not by the
  door). Per this project's own doctrine (`references/checklist-engine.md` §MCP door: "do not drive the
  door you can see — it is pointed at your dispatcher's spine"), I did not drive the Commander's `execute`
  gate. Instead I authored my own survey at the handoff's named Survey State Location
  (`.agent-work/w2-reindex/g1-review/review.json`) and drove it through `scripts/checklist_engine.py`'s
  CLI (the sanctioned path this same reference names for a dispatched crew driving its own plan when no
  door is bound to it). This is a dispatch-wiring defect for `run_crew.py`/Commander to fix, not something
  this crew's own review work needed to route around further.
- **What would have made this easier:** nothing else — the handoff's pinned mechanism spec, evidence
  list, and constraints were precise enough to verify directly against the code with no guessing.

## Return status
`complete`
