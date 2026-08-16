# Implementer Handoff

## Gate
`g1-implement`

## Task
Make a crew's model tier an explicit, mandatory choice at the seam every fresh/relaunch dispatch
passes through in `scripts/run_crew.py`, and forward the already-recorded `reasoning_effort`
metadata into the launcher's real `--effort` flag on the `cli` backend. Both changes land in the
same patch, in owned files only.

## Protected Intent
No existing crew's *effective* tier may change as a side effect (`decision:do-not-change-what-anything-runs-at`).
This makes the choice explicit; it does not repick tiers for any dispatch that already names one.

## Test Mode
TDD-adjacent / test-after allowed: the seams are pure-function/dataclass-level and already have an
extensive existing test suite (`tests/test_crew_launcher.py`) whose conventions you extend rather
than invent. Every new behavior needs a red/green pair.

## Close Criteria
- `CrewSpec.__post_init__` (`scripts/run_crew.py:1350-1364`) refuses a falsy `self.model`, raising
  `CrewLaunchError`, same style as its two existing invariant checks (missing job, missing
  completion contract) immediately above it in the same method.
- Refusal fires for every fresh `CrewSpec` construction (`main()`'s fresh-launch branch ~2092,
  its `--abandon --relaunch` branch ~2068, `launch_crew` ~1773, `record_external_attempt` ~1839)
  and does NOT fire for `--resume`/`--verify-result`/a bare `--abandon` (none of these construct a
  `CrewSpec` — confirmed by reading `CliBackend.resume` and `abandon_crew` directly, not assumed).
- `--abandon --relaunch` requires an explicit `--model` — RULED, do not re-litigate: no fallback to
  `abandoned.get("model")`, intentionally asymmetric with `reasoning_effort`'s existing
  inherit-on-relaunch fallback (`main()` ~2071), which stays untouched.
- The refusal fires before `CliBackend.dispatch` reserves scratch / writes the running registry
  entry (issue #525 ordering) — a refused fresh launch leaves no half-written entry.
- `build_crew_argv` gains `effort: str | None = None`; `if effort: argv += ["--effort", effort]`,
  mirroring the existing `model` line (813-814) exactly.
- `CliBackend.dispatch` (~1542) passes `effort=spec.reasoning_effort`; `CliBackend.resume` (~1612)
  passes `effort=entry.get("reasoning_effort")` — both call sites.
- `build_entry`'s existing `if model: entry["model"] = model` / `if reasoning_effort: entry["reasoning_effort"] = reasoning_effort`
  is confirmed (by reading, not re-implementing) to already satisfy `decision:record-the-resolved-tier`
  once `model` is mandatory — pin with a test only, no new write path.
- `--model` stays OPTIONAL at the `argparse` layer (`build_parser`) — do not make it `required=True`;
  that would break the legitimately-tierless `--resume`/bare-`--abandon` shapes at the parser level,
  before the `CrewSpec`-level scoping can apply.
- Full clean-env suite green at gate close (see Verification Commands).

## Allowed Scope
- `scripts/run_crew.py` — `CrewSpec.__post_init__`, `build_crew_argv`, `CliBackend.dispatch`,
  `CliBackend.resume`. Docstring correction on `build_entry`'s `reasoning_effort` note (~1129-1130,
  "never emitted as a CLI flag" is now false) — logic there is unchanged.
- `tests/test_crew_launcher.py` — pre-authorized for reconciliation of every existing test whose
  scenario the new mandatory `--model` invalidates (see Required Evidence's named list), not just
  new tests. This file's tests already assert the PRE-mission contract in several places and their
  scenario is exactly what this change now forbids — expect to reseed them, not just add alongside.

## Specific Exclusions
- `skills/commander/references/crew-dispatch.md` and the two handoff templates — gate `g2`, not
  this gate.
- Fenced, never touch: `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
  `scripts/spine_lifecycle.py` and their tests (lane F is live in all three).
- Fenced, never touch: `skills/commander/templates/COMMANDER_SPINE.template.json`,
  `skills/admiral/templates/LAUNCH_ORDER.template.md`, `skills/admiral/references/fleet-doctrine.md`,
  `skills/_shared/**`, `scripts/install_constellation.py` (belong to queued #610).
- Do not touch `#607`'s parent-lease-heartbeat thread (`_parent_lease_heartbeat`) start/stop/join
  ordering — load-bearing, unrelated to this gate.
- Do not fix a caller outside `scripts/run_crew.py`/`tests/test_crew_launcher.py` that the
  caller-list survey finds — report it in `IMPLEMENTER_RESULT` instead.

## Constraints
- `CrewLaunchError`, exit 1, `REFUSED: {exc}` prefix — the launcher's existing error shape; do not
  invent a new exception type or exit code.
- No invented default for a missing tier anywhere (`decision:refuse-a-tierless-dispatch`) — fail
  closed.
- `ExternalBackend` gets no `argv`/subprocess change — it spawns no process; out of scope by
  construction (its own `CrewSpec` construction still goes through the same `__post_init__` refusal,
  which is in scope and expected).

## Map Anchors (inbound)
Map DEGRADED-UNPARSEABLE (`.agent-work/cleanup-g-crew-tier/map-orientation.json`) — no packet map
exists; anchors below are direct file:line citations, independently re-confirmed by two plan
candidates and a cold plan critic against the live source, not map node ids.
- **Map entry point:** `scripts/run_crew.py` (start at `CrewSpec.__post_init__`, ~line 1350).
- **Structural:** `scripts/run_crew.py:755-818` (`build_crew_argv`), `:1337-1364` (`CrewSpec`),
  `:1092-1199` (`build_entry`), `:1490-1638` (`CliBackend`), `:1974-2109` (`main()`).
- **Decision anchors:**
  - `decision:refuse-a-tierless-dispatch` — fail closed, no invented default; report legitimately-tierless callers instead of silently exempting them.
    `@grade: settled/human · leans g1-implement,g1-review · settle: n/a, ruled`
  - `decision:do-not-change-what-anything-runs-at` — explicit choice only, no side-effect retiering.
    `@grade: settled/human · leans g1-implement,g1-review`
  - `decision:record-the-resolved-tier` — resolved tier lands on the registry entry; already mechanical via `build_entry`, confirm don't reimplement.
    `@grade: settled/measured · leans g1-implement`
  - `decision:reasoning-effort-follows-tier` — forward as the launcher's real `--effort` flag; confirmed present (`claude --effort <low|medium|high|xhigh|max>`).
    `@grade: settled/measured · leans g1-implement,g1-review`
- **Evidence expectations:** re-confirm the `build_crew_argv`/`CrewSpec`/`build_entry` line numbers cited above against your own read before editing — this handoff's numbers were correct as of plan time but drift is possible.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; `git check-ignore -v scripts/run_crew.py` exit 1 (not ignored), confirmed at handoff time.
- **Committed** — `tests/test_crew_launcher.py`; `git check-ignore -v tests/test_crew_launcher.py` exit 1 (not ignored), confirmed at handoff time.

## Required Evidence
Load-bearing (prove rigorously):
- Refusal red/green: a fresh dispatch with no `--model` refused (`CrewLaunchError`/exit 1, no
  registry entry written); one with `--model` succeeds and the registry entry carries it.
- `--effort` forwarding red/green on BOTH `CliBackend.dispatch` and `.resume`.
- Full clean-env, cache-cleared suite green (`find . -name __pycache__ -type d -exec rm -rf {} + ;
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`).
- Caller-list survey: the full enumerated list of every call site that needed a `model=` added to
  keep passing, with confirmation each is inside `tests/test_crew_launcher.py` (owned) — or, if any
  is found outside owned files, name it and do NOT fix it.

Confirmatory (spot-check suffices):
- The four named tests (`test_reasoning_effort_is_metadata_only_and_recorded` ~2588,
  `test_cli_resume_reads_reasoning_effort_from_registry` ~2605,
  `test_legacy_resume_without_reasoning_effort_does_not_crash` ~2623,
  `test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted` ~955) flipped from
  `assertNotIn("--reasoning-effort", ...)` to asserting `--effort <value>` presence/absence
  correctly, docstrings corrected.
- `build_entry` docstring correction.

A claimed test-failure distribution, if any transient red occurs mid-work, must be derived
mechanically (`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), never summarized
from a glance.

## Wiring Grep
```bash
grep -rn "build_crew_argv(" --include=*.py . | grep -v "def build_crew_argv"
grep -rn "\.reasoning_effort\b" --include=*.py scripts/run_crew.py tests/test_crew_launcher.py
```
State the count of call sites found for each. `build_crew_argv`'s two production call sites
(`CliBackend.dispatch`, `CliBackend.resume`) must both show `effort=` in the diff.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-g-crew-tier
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

## Suggested Model Tier
Stronger — reason: control-flow change to the crew-dispatch launcher every implementer/reviewer in
this corpus routes through; a subtle refusal-scoping bug (e.g. firing on `--resume`) would be a
correctness regression across the whole fleet, not just this repo. This run's own tier is Sonnet 5
per the launch order's Budget; dispatch this crew at `sonnet`.

## Authority
The refusal seam (`CrewSpec.__post_init__`, not `build_crew_argv`, not `argparse required=True`),
the relaunch semantics (no inherit fallback for `model`), and the `--effort` flag name are already
decided — do not re-derive or re-litigate them, implement as specified above. If you find a fact
that contradicts one of these (e.g. the `claude` CLI no longer accepts `--effort`), STOP and report
rather than silently substituting a different mechanism.

## Stop Conditions
Stop and return if: the refusal cannot be scoped to fresh/relaunch without touching `--resume`; a
caller outside owned files needs a code fix (report instead); the `claude` launcher's `--effort`
flag is absent when you check `claude --help` yourself; a decision outside this Authority section is
needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(including the full caller-list enumeration), assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-implement-implementer-result.md` before ending
your turn.
