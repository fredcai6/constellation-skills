# Commander Result — cleanup-g-crew-tier (#611)

## Verdict: SHIPPED

`scripts/run_crew.py` now refuses a fresh or relaunched crew dispatch that names no `--model`
(fail closed, no invented default), and forwards the already-recorded `reasoning_effort` metadata
into the launcher's real `--effort` flag on the `cli` backend, both dispatch and resume.
`skills/commander/references/crew-dispatch.md` now names the handoff's "Suggested Model Tier"
field as the thing a Commander resolves `--model` from. All five of the launch order's graded
Pre-Rulings are satisfied. Independent reviewer APPROVE on the code gate; self-attested red/green
on the doctrine gate. Full clean-env suite green at head modulo an explicitly reported,
out-of-ownership caller-list residue (6 tests, `recommend-and-defer`d to the Admiral, not fixed).

## 1. Red/green for the refusal

- A dispatch with no `--model`: **refused** (`CrewLaunchError`, exit 1,
  `REFUSED: a crew needs an explicit tier...`), and **no registry entry is written**
  (`test_fresh_dispatch_with_no_model_is_refused_and_writes_no_registry_entry` — proves the #525
  ordering: the refusal fires before `CliBackend.dispatch` reserves scratch/writes the running
  entry).
- A dispatch with `--model`: **accepted**, and the resolved tier is present on the registry entry
  afterward (`test_fresh_dispatch_with_model_records_it`).
- `--abandon --relaunch` with no `--model`: **refused**, even when the abandoned entry had one
  stored (`test_abandon_relaunch_with_no_model_is_refused_even_though_one_was_stored` — pins the
  Commander's own ruling: no inherit-from-abandoned-entry fallback, intentionally asymmetric with
  `reasoning_effort`'s existing fallback, which stays untouched).
- `--resume` and a bare `--abandon` construct no `CrewSpec` and correctly need no `--model` at all
  (`test_resume_needs_no_model_at_all`, `test_bare_abandon_needs_no_model_at_all` — negative
  controls).
- All 6 tests in `tests/test_crew_launcher.py::MandatoryModelTests`, independently reproduced by
  the reviewer via direct source reading (`CrewSpec.__post_init__`, `CliBackend.resume`,
  `abandon_crew`) — the scoping is structural, not merely tested.

## 2. The caller list

Full enumeration in `IMPLEMENTER_RESULT` and independently re-derived by the reviewer via
`grep -rln "CrewSpec(\|record_external_attempt(\|\.launch_crew(" --include=*.py .`:

- **~27 call sites in `tests/test_crew_launcher.py`** (owned) — fixed directly in `g1-implement`,
  by class, see the full breakdown in
  `.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-implement-implementer-result.md`.
- **6 call sites outside ownership**, found genuinely broken and **not fixed** (reported per the
  pre-ruling): `tests/test_crew_worktree_cwd.py` (4), `tests/test_work_id_nesting.py` (2). No
  design question — same mechanical `model=` addition already applied 27 times elsewhere. Routed
  `recommend-and-defer` at `triage` (candidate `tc1`,
  `.agent-work/cleanup-g-crew-tier/triage-candidates/tc1-tierless-callers-outside-ownership.md`) —
  clears all four Fix-Now Eligibility Ladder rungs but explicitly **not** fixed now, because the
  launch order reserves this exact question to the Admiral by name ("I will rule on it") and both
  files are outside this mission's File Ownership.
- **No production (non-test) caller** anywhere in the live tree constructs `CrewSpec` outside
  `scripts/run_crew.py` itself.
- **No legitimately-tierless caller was found or exempted beyond the two already structurally
  exempt** (`--resume`, bare `--abandon` — neither constructs a `CrewSpec`).

## 3. `reasoning_effort`

Forwarded as the launcher's real `--effort <level>` flag on the `cli` backend, both
`CliBackend.dispatch` (`effort=spec.reasoning_effort`) and `CliBackend.resume`
(`effort=entry.get("reasoning_effort")`) — mirroring the existing `model` line exactly in
`build_crew_argv`. The launcher's actual argument surface: `claude --help` (checked directly, by
both the Commander and independently by the reviewer) confirms `--effort <low|medium|high|xhigh|max>`
exists, resolving the launch order's open "if the launcher accepts it" question to yes. Nothing was
left alone — the flag exists and is now wired.

## 4. This Commander's own dispatch record

Every crew dispatched this run named an explicit tier from the first dispatch (the mission's own
"trap"), verified against the durable registry, not asserted:

| Dispatch | Mechanism | Model |
|---|---|---|
| `execute/commander` (this run, dispatched by the Admiral) | `run_crew.py` cli | `sonnet` |
| Plan candidate A (smallest-diff) | Agent tool (native subagent) | `sonnet` |
| Plan candidate B (most-testable) | Agent tool (native subagent) | `sonnet` |
| Cold plan critic | Agent tool (native subagent) | `sonnet` |
| `g1-implement` implementer | `run_crew.py --dispatch external` + Agent tool | `sonnet` |
| `g1-review` reviewer | `run_crew.py --dispatch external` + Agent tool | `sonnet` |

No default was inherited or invented at any point. Note (cold-critic finding #2, recorded in
`PLAN_CONVERGENCE.md`): the three plan-phase dispatches (both candidates, the critic) ran as native
Agent-tool subagents, not through `run_crew.py` — they never touch `crew-runs.json`. This is the
correct scope for `MISSION_FRAME.md`'s "the one seam every dispatch passes through" claim: that
line describes the `run_crew.py` implementer/reviewer crew-dispatch path this mission actually
fixes, not every subagent-spawn mechanism the harness offers. All six dispatches above are named
here regardless of which mechanism recorded them, so the dispatch record is complete even though
the registry alone is not.

## 5. Full-suite evidence

**This lane's head**, clean-env, cache cleared, `CREW_SCRATCH_DIR` also unset (this Commander's own
ambient env var — a false-failure source caught and fixed via `amend` at `g1-integrate`, see
`notes-g.md`/`REPLAN_INPUT.json` discrepancy for the parallel finding at the main-baseline
measurement):

```
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q
6 failed, 3166 passed, 6 skipped, 1172 subtests passed in 130.22s
```

The 6 failures are exactly the reported caller-list residue (Section 2) — `CrewLaunchError`
tracebacks in `tests/test_crew_worktree_cwd.py` (4) and `tests/test_work_id_nesting.py` (2), all
outside this mission's ownership.

**`main` baseline**, re-measured fresh at gate time (not carried from dispatch time) in a
disposably-cloned, correctly-named directory (a first attempt named the clone directory
differently and produced a false `MapTreeFreshnessTests` failure — the generated map header bakes
in the repo directory name; re-cloned correctly, see `REPLAN_INPUT.json` discrepancy `D0`):

```
main @ e0539903 (unchanged from the launch order's dispatch-time baseline -- lane F has not landed)
3163 passed, 7 skipped, 0 failed, 125.81s
```

**Failure-set difference**: exactly the 6 tests in Section 2, all directly and solely caused by
`decision:refuse-a-tierless-dispatch`. No other delta. Head also adds 2 new passing tests
(`tests/test_crew_dispatch_doctrine.py`).

**Not tested**: Windows. CI is the only Windows signal and is red at baseline per Inherited
Context; local Linux is the only real signal this run had.

## 6. Map impact, triage, workflow feedback, `--here`

**`--here` output** (run before any git operation, per the launch order):
```
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/cleanup-g-crew-tier
```

**Map impact**: No `docs/architecture` packet map exists (DEGRADED-UNPARSEABLE, corpus-wide —
`map/ids.jsonl` empty repo-wide, independently confirmed here and by `cleanup-c-liveness-rail`
before it). This mission's own generated code map (`map/INDEX.md`) was kept fresh: rebuilt during
`g1` (mechanical, tool-generated, entity-count-only diff, confirmed zero-further-diff by the
reviewer), reconfirmed fresh again during `g3-verify`'s baseline remeasurement. The structural
record for this seam lives in `scripts/run_crew.py`'s own docstrings and `crew-dispatch.md`
doctrine, both updated during execution (`reconcile` recorded a reasoned no-op — nothing further to
fold in).

**Triage candidates**: one (`tc1`), `recommend-and-defer` — see Section 2.

**Corpus-wide finding, not this lane's to fix**: `map/ids.jsonl` is empty repo-wide (zero authored
anchor tags exist anywhere in the corpus), so `map_orient.py` cannot resolve ANY run to a
packet-map entrypoint today, regardless of files touched. Independently reconfirmed here after
`cleanup-c-liveness-rail` first flagged it. Worth a corpus-level triage item at the epic level if
one does not already exist.

**Workflow feedback** (harvested from both crews' `Workflow Feedback` sections plus this
Commander's own observations):
- The `constellation-reviewer` skill's opening instructions assume "a spine is bound for you" via
  ambient `SPINE_FILE`/`SPINE_SESSION`, but for an `external`-backend dispatch (this harness's only
  viable backend — no headless `claude` CLI) those env vars actually belong to the *dispatching*
  Commander, not the crew. The reviewer had to cross-reference its own `crew-runs.json` entry
  (`spine: null`) against a second doc (`checklist-engine.md`'s door-binding distinction) to avoid
  mistakenly driving the Commander's own live spine. The skill's opening paragraph could name the
  `crew-runs.json` `spine`-field check as the disambiguating test up front (matches this session's
  own prior memory ruling, `crew-dispatch-spine-null`).
- `map_orient.py`'s degraded-mode discharge and `verify-frame`'s anchor-matching (the 7-keyword
  `ANCHOR_RE`, e.g. `decision:`) is a real trap for a DEGRADED-mode mission frame: the template's
  own suggested `decision:id` bullet syntax, used verbatim, would have caused every decision
  anchor in the frame to read as "cannot resolve" and refuse the gate. Worked around by describing
  decisions in prose without the `word:identifier` pattern; a DEGRADED-mode note in the template or
  the tool's own help text would save a future Commander the same investigation.
- A scratch-clone baseline remeasurement is silently wrong if the clone directory isn't named to
  match the repo — the generated map's header bakes in the directory name, producing a false
  `MapTreeFreshnessTests` failure that reads exactly like a real regression. Worth naming in
  `crew-dispatch.md` or the g3-verify gate template directly, since this is the second time (after
  `cleanup-c-liveness-rail`'s baseline work) a Commander has had to rediscover this scratch-clone
  measurement pattern from first principles.
- This Commander's own ambient `CREW_SCRATCH_DIR` leaking into a suite measurement (fixed via
  `amend` at `g1-integrate`) is the same class of defect as the scratch-clone naming issue above:
  a measurement's own environment silently contaminating the thing it measures. The launch order's
  standing clean-env recipe (`-u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`) predates the
  `CREW_SCRATCH_DIR` mechanism; worth updating that recipe corpus-wide.

## Sequencing (the trap), stated plainly

Every crew this run dispatched named an explicit tier from the very first dispatch (Section 4),
before `g1-implement`'s refusal made it mandatory. `g1-implement` and `g1-review` landed as one
atomic patch's implement/review pair with no gate boundary between "refusal exists" and "reviewer
needed" — so there was no window where a landed refusal could lock out this run's own next
dispatch. The cold plan critic caught that this discipline was never *written into* `execute.json`
itself (finding #1); fixed by adding explicit "pass `--model`" reminders to both `g1-implement` and
`g1-review`'s imperatives before either gate opened.

## Parked at `archive` — not merged

Per the launch order: "Park at `archive`. **Do not merge** — publication is the Admiral's class."
