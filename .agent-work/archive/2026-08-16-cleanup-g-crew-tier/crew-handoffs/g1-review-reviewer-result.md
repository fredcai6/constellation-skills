# Review Result

## Assigned Gate
`g1-review` (verifying `g1-implement`, work_id `cleanup-g-crew-tier`)

## Result
`APPROVE`

Full survey driven through the engine at
`.agent-work/cleanup-g-crew-tier/g1-review/review.json` (own session,
`spine: null` per this crew's own `crew-runs.json` entry — see Workflow
Feedback), consolidated to `APPROVE`, 0 findings. Fowler pass recorded at
`.agent-work/cleanup-g-crew-tier/g1-review/FOWLER_PASS.json`,
`verify_fowler_pass.py` exits 0.

## Handoff compliance
Every close criterion independently reproduced against the live source, not
trusted from `IMPLEMENTER_RESULT`'s claims:

- `CrewSpec.__post_init__` (`scripts/run_crew.py:1375-1380`) raises
  `CrewLaunchError` on a falsy `self.model`, as a third invariant check, same
  style, placed immediately after the two existing checks (job,
  completion-contract) — read directly.
- Refusal scoping: read `CliBackend.resume` (1580-1636) and `abandon_crew`
  (1873-1882) in full — neither constructs a `CrewSpec`, so the refusal is
  structurally unreachable from `--resume` or a bare `--abandon`. Fresh
  launch (`main()` ~2109) and `--abandon --relaunch` (~2085) both construct a
  `CrewSpec` before `backend.dispatch` is called.
- `--abandon --relaunch` requires an explicit `--model` (`model=args.model`,
  main() ~2087) with **no** fallback to `abandoned.get("model")` — confirmed
  by reading the literal call, not a test's assertion. `reasoning_effort` on
  the same call **does** fall back
  (`args.reasoning_effort or abandoned.get("reasoning_effort")`), the
  required asymmetry.
- Ordering (issue #525): `launch_crew` constructs `CrewSpec` (line 1790,
  raising here on falsy model) strictly before calling
  `CliBackend().dispatch` (line 1795); inside `dispatch`, `scratch.mkdir`/
  registry writes happen at 1532-1555, only reachable after spec
  construction already succeeded. The refusal is structurally impossible to
  reach after scratch reservation, not merely untested.
- `--effort` forwards symmetrically: `build_crew_argv` gained
  `effort: str | None = None` (755-757), emits `["--effort", effort]` only
  when truthy (819-820), mirroring the `model` line exactly.
  `CliBackend.dispatch` (1562) passes `effort=spec.reasoning_effort`;
  `CliBackend.resume` (1636) passes `effort=entry.get("reasoning_effort")`.
  `claude --effort <level>` confirmed present on the installed CLI via
  `claude --help` myself.
- `build_entry`'s write path (`if reasoning_effort: entry["reasoning_effort"]
  = reasoning_effort`, 1205-1206) is byte-identical to before; only its
  docstring (1136-1140) was corrected.
- `--model` stays optional at the `argparse` layer:
  `p.add_argument("--model")` (1906), no `required=True`.
- `ExternalBackend.dispatch` (1671-1717) calls `build_entry` only, never
  `build_crew_argv` — confirmed no argv/subprocess change there, matching the
  handoff's "out of scope by construction."

## Scope drift
None. `git status --porcelain` shows exactly 3 tracked-file modifications
(`scripts/run_crew.py`, `tests/test_crew_launcher.py`, `map/INDEX.md`) and
zero untracked additions. `scripts/run_crew.py`'s diff (20 insertions / 3
deletions) touches only `CrewSpec.__post_init__`, `build_crew_argv`,
`CliBackend.dispatch`/`resume`, and `build_entry`'s docstring.
`tests/test_crew_launcher.py`'s diff is entirely `model=None` →
`model="sonnet"` reconciliation, the new `MandatoryModelTests` class
(6 tests, counted directly), and the 4 named `--effort` flip tests;
`SessionNameTests`'s 17 direct `build_crew_argv` calls and
`BuildEntryTests::test_falsy_model_is_not_stored` are confirmed **absent**
from the diff (grepped the diff text directly) — correctly left untouched.

`map/INDEX.md`: confirmed genuinely mechanical. I re-ran
`python -m scripts.code_map build --root .` myself and the regenerated file
produced **zero further diff** against the committed one. The diff is
limited to entity counts (`tests`: 4848→4855; `tests.test_crew_launcher`:
287→294 entities / 225→226 holes); the `scripts` section (58 modules / 1224
entities) is unchanged, consistent with no new top-level entities in
`run_crew.py`. `tests/test_code_map.py::MapTreeFreshnessTests` passes
(2 passed) against the current map.

All named exclusions confirmed untouched via `git status`/`git diff`:
`skills/commander/references/crew-dispatch.md`, the two handoff templates,
`scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`scripts/spine_lifecycle.py` (+ their tests),
`skills/commander/templates/COMMANDER_SPINE.template.json`,
`skills/admiral/templates/LAUNCH_ORDER.template.md`,
`skills/admiral/references/fleet-doctrine.md`, `skills/_shared/**`,
`scripts/install_constellation.py`. `#607`'s `_parent_lease_heartbeat`:
grepped `scripts/run_crew.py`, all 4 references (definition + 2 call sites +
naming comment) are unchanged context lines in the diff.

## Evidence verdict
Fully reproduces. `tests/test_crew_launcher.py` alone: 211 passed, 1 failed
— exact match. Confirmed the 1 failure
(`ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`)
is pre-existing/environmental via my own `git stash` + rerun on the
unmodified baseline (fails identically — `CREW_SCRATCH_DIR` leaks from this
crew's own ambient env into the fake child env dict); popped the stash back
cleanly, `git status` confirmed all 3 files restored before I resumed.

Full clean-env suite
(`find . -name __pycache__ -type d -exec rm -rf {} +` then
`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`):
**7 failed, 3163 passed, 6 skipped, 1172 subtests passed in 128.28s** — the
same 7 test ids and the same counts as `IMPLEMENTER_RESULT` claims. The 6
non-launcher failures (`test_crew_worktree_cwd.py` x4,
`test_work_id_nesting.py` x2) show the exact `CrewLaunchError("a crew needs
an explicit tier...")` traceback in my own run output — genuinely caused by
the new refusal, and exactly the Constraints section's expected "6 tests
total" deliverable, not a different regression.

Caller-list survey re-derived independently:
`grep -rln "CrewSpec(\|record_external_attempt(\|\.launch_crew(" --include=*.py .`
(excluding `.agent-work/archive`) returns 5 files: `scripts/run_crew.py`,
`tests/test_crew_launcher.py`, `tests/test_crew_delivery_addressing.py`,
`tests/test_crew_worktree_cwd.py`, `tests/test_work_id_nesting.py`. The 4th
file was **not** named in `IMPLEMENTER_RESULT`'s caller-list enumeration —
inspected it directly (line 150-154): its one `record_external_attempt` call
already passes `model="sonnet"` explicitly, so it needed no fix and
correctly falls outside the scoped claim ("every call site whose scenario
the new mandatory `--model` invalidated"). Not an omission — verified by
reading the call site myself, and this file is absent from the 7 `FAILED`
test ids in my own full-suite run. The implementer's narrower, separately
stated claim ("no production/non-test caller outside `scripts/run_crew.py`
constructs `CrewSpec`...") is also independently true — all 4 non-`run_crew.py`
hits are test files. `build_crew_argv(` wiring grep: 22 non-archive matches,
matching the claimed count.

## Code/doc quality
Meets inherited rules and the handoff's own constraints. `CrewLaunchError`,
exit 1, `REFUSED: {exc}` — confirmed pre-existing class (line 100), no new
exception type; the exit path is the pre-existing
`except CrewLaunchError as exc: print(f"REFUSED: {exc}"...); return 1`
wrapping `main()`, untouched. No invented default anywhere — grepped the
diff for any new `or "sonnet"`/`or DEFAULT_MODEL` style fallback, found
none. Tests assert behavior (argv index/value, exit code, registry
contents), not message text alone. Naming/doc conventions matched: the new
refusal message follows the same "a crew needs a X: refusing a dispatch
with no --Y given" template as its two siblings.

**Refactoring pass (Fowler).** Full record at
`.agent-work/cleanup-g-crew-tier/g1-review/FOWLER_PASS.json`
(`verify_fowler_pass.py` exit 0, smells=12). 10 smells **absent** — no
production duplication, feature envy, data clumps, primitive obsession,
divergent change, message chains, speculative generality, or
comments-as-deodorant introduced. 1 **overridden**: `long-parameter-list` on
`build_crew_argv` (7→8 keyword-only params) — the function's own docstring
names it a pure 1:1 metadata-to-CLI-flag mapping; a parameter object would
hide that mapping rather than clarify it, and the new `effort` param mirrors
`model`'s existing shape exactly per the handoff's own instruction. 1
**flagged**, non-blocking: `shotgun-surgery` — tightening `CrewSpec`'s
`--model` precondition required ~27 mechanical test-file edits plus 6 more
in two out-of-owned test modules (captured as triage candidate below),
confined to test fixtures exercising the constructor directly, not
production coupling.

## Map impact verdict
Map is DEGRADED-UNPARSEABLE per both handoffs (no packet map exists);
anchors were direct file:line citations, independently re-confirmed against
the live source with no drift found.

- **Evidence supports claimed change:** yes — the diff, the reproduced test
  run, and the reproduced `map/INDEX.md` rebuild all back the claimed
  behavior exactly.
- **Constraints not violated:** yes — `decision:do-not-change-what-anything-runs-at`
  holds: no existing crew's effective `--model` tier changed as a side
  effect; the only two behavior changes (the new refusal, and `--effort`
  forwarding) are both the explicitly authorized scope of this gate, not
  incidental side effects.
- **Notes match the diff:** yes — `IMPLEMENTER_RESULT`'s "Files changed"
  section names exactly the 3 changed files and the exact functions touched
  in `scripts/run_crew.py`; nothing overstated or missing.
- **Decision candidates surfaced:** n/a — the three governing decisions
  (`decision:refuse-a-tierless-dispatch`,
  `decision:do-not-change-what-anything-runs-at`,
  `decision:reasoning-effort-follows-tier`) were already `settled` before
  this gate; nothing here required new authority.
- **Durable context routed:** yes — the two out-of-owned-files test failures
  are reported as an out-of-scope observation (both by the implementer and
  by me, see below), not silently fixed or dropped.

## Reconciliation check
No divergence Commander must reconcile. `map/INDEX.md` is the mechanical
code-map index, not the architecture map, and its regeneration is
independently confirmed reproducible (zero further diff on rebuild) —
correctly not an architecture-significant change requiring reconciliation.

## Blockers
None.

## Out-of-scope observations
- `tests/test_crew_worktree_cwd.py` (4 tests: `CrewSpawnCwdTests`) and
  `tests/test_work_id_nesting.py` (2 tests: `CrewRegistryAddressingTests`)
  call `RC.launch_crew`/`RC.record_external_attempt` with `model=None` and
  now fail with `CrewLaunchError` post `decision:refuse-a-tierless-dispatch`.
  Both are outside this gate's owned files
  (`scripts/run_crew.py`, `tests/test_crew_launcher.py`), so the
  implementer correctly did not touch them (handoff exclusion). Independently
  confirmed via my own full-suite run: exactly these 6 tests fail, with the
  `CrewLaunchError` traceback naming the new refusal as cause. Mechanical
  follow-up needed: add an explicit `model=` (e.g. `"sonnet"`) at each of the
  6 call sites — same reconciliation pattern already applied across
  `tests/test_crew_launcher.py` in this gate, not a design question. (Filed
  as triage candidate `tc1` in my own survey.)

## Workflow Feedback

- **Handoff gaps:** None material. The reviewer handoff's "Survey State
  Location" instructed creating a checklist at
  `.agent-work/cleanup-g-crew-tier/g1-review/review.json`, but the loaded
  `constellation-reviewer` skill opens by assuming "a spine is bound for
  you" via the ambient `SPINE_FILE`/`SPINE_SESSION` env and instructs
  calling `spine_status` first, never building a survey. Those two
  instructions actively conflict for this dispatch shape.
- **Context rediscovered:** I had to check my own `crew-runs.json` entry
  (`backend: "external"`, `spine: null`) to discover that the ambient
  `SPINE_FILE`/`SPINE_SESSION` in my environment
  (`constellation/cleanup-g-crew-tier/execute/commander`) actually belong to
  the dispatching Commander's own `execute` gate, not to me — this crew was
  dispatched via `record_external_attempt`/`ExternalBackend` (the Agent-tool
  harness has no headless CLI to spawn its own bound door for), not via
  `run_crew.py`'s `CliBackend` subprocess path that binds a fresh door per
  crew. Per prior recorded guidance on this exact shape
  (`crew-dispatch-spine-null` memory ruling, and
  `constellation-workbench`'s own `references/checklist-engine.md` §"MCP
  door: default path, and who it is NOT for" — "A dispatched Task-tool
  Implementer or Reviewer subagent must drive its own... survey file through
  the CLI instead"), I built my own `REVIEW_SURVEY` from
  `.agent-work/templates/REVIEW_SURVEY.template.json` at the handoff's named
  path, claimed it with my **own** session id
  (`constellation/cleanup-g-crew-tier/g1-review/reviewer/attempt-1`, matching
  my `crew-runs.json` entry), and drove it through
  `scripts/checklist_engine.py` directly — never touching the Commander's
  `spine.json`. This context (crew-runs.json entry vs. ambient spine env) is
  not something the reviewer handoff or the loaded skill's own opening
  instructions surface; a reviewer without that prior context would likely
  have called `spine_status`/`spine_advance` against the Commander's live
  `execute` gate by mistake.
- **Instructions improvised around:** The `constellation-reviewer` skill's
  own text says "Do not author a survey of your own when a spine is already
  bound" — but "bound" there means bound *for this process*, and the
  ambient env vars alone don't distinguish that from "inherited from
  whatever dispatched me." I resolved the ambiguity by checking my own
  registry entry's `spine` field (`null` = not bound for me) before making
  any engine call, per the workbench doc's own distinguishing test
  ("`run_crew.py` launches a fresh headless `claude -p` process with its own
  `SPINE_FILE`/... bound in ITS OWN environment" vs. "A dispatched Task-tool
  ... subagent inherits its dispatching process's MCP scope wholesale").
- **What would have made this easier:** The `constellation-reviewer`
  skill's opening paragraph could name the `crew-runs.json`
  `spine`-field check as the disambiguating test up front, the same way
  the workbench checklist-engine reference already does — right now a
  reviewer has to already know to cross-reference a second doc to catch
  this before making a single (wrong-target) engine call.

## Return status
`complete`
