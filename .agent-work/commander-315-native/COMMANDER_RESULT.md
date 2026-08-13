# COMMANDER_RESULT — commander-315-native

Epic 568, wave 1 recut. Branch `epic-568/c2-native-isolation`, base `9bb8c1b6`.
Launch order: `.agent-work/epic-568/LAUNCH_ORDER-wave1-recut.md`.

## Verdict

**Incomplete — governed idle at a HARD context trip, with the design finished and frozen.**

The spine is driven through `plan` (init, context, understand, plan all complete). `execute`
was **refused by the engine's own context governor** before any code was written. This is
the sanctioned reach-up, not a stall and not a failure to finish: a `refresh-request` is
pending on the spine and a **fresh** Commander resumes the same job file.

No source file was modified. The change is designed, costed, criticised and frozen; it is
not implemented. **No PR is open**, because a PR carrying only planning artifacts for a
change whose central ruling is "both halves land as ONE change" would be noise.

Two things need the Admiral before or during the resume; neither blocks implementation.

## Worktree isolation output (first git-adjacent action)

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
     --here /home/tommy/projects/constellation-skills-wt/epic-568-315-native
worktree OK: in /home/tommy/projects/constellation-skills-wt/epic-568-315-native
EXIT=0
```

## Why the run stopped

`claude-opus-5` is profiled (1M window, 80K soft, 150K hard). The `execute` gate declares
`context_headroom_tokens: 30000` (#467), so its begin-work line is **12%**. The reading was
**23.8%** — roughly 238K tokens, over the 150K hard cap even ignoring the gate's reserve.

```
REFUSED: execute: context at 24% is at/over the hard limit, so this is not the moment
to BEGIN work here — finish and close the gate you are already in, then request a
refresh so a fresh agent starts this one.
```

I checked whether this was a false positive before obeying it: `gauge_reader.py:93` records
an old defect where an uncalibrated `claude-opus-5` "read ~5x high". That was #252 and it is
fixed — `gauge.json` names `claude-opus-5`, so the reading resolved against the real 1M
window, not the 200K default. The trip is correct.

**Where the context went, honestly.** Front-loading. A full design-it-twice (two parallel
cold candidates) plus a cold critic that returned 17 confirmed findings, all triaged, plus
reading a 3352-line engine module. That work is durable and committed; the cost of it is
that this agent cannot also drive execute. See "Workflow feedback".

## Before / after repro

`.agent-work/commander-315-native/repro_native.py` builds a throwaway main checkout and a
real registered worktree, instantiates spines with this tree's own `init_work_area.py`, and
drives `claim` from four positions. **BEFORE** (captured at `REPRO-before.txt`, HEAD
`9bb8c1b6`, source tree clean):

```
origin stamped in spine: (none -- stamp not landed yet)

A  origin spine, cwd = WORKTREE ROOT -> PASS     (want PASS)
B  origin spine, cwd = MAIN CHECKOUT -> PASS     (want REFUSED after the change)
C  no-origin,    cwd = MAIN CHECKOUT -> PASS     (want PASS in both worlds -- the fallback)
D  origin spine, cwd = WT SUBDIR     -> PASS     (want PASS -- containment, not equality)

B refused AND took no lease (state fact): False
GATE ARMED: False
```

Case B is the defect, reproduced: an engine standing in the main checkout claims the lease
on a worktree's spine and the engine has no idea. **AFTER is not measured** — the change was
never written.

The repro asserts B on a **state fact** (the spine carries no `engine_session` afterwards),
not on a substring of the refusal prose. It did match prose in its first version; the cold
critic caught it as an instance of "assert against the behaviour, never against text
describing the behaviour", and it was rewritten.

## Open floats — the Admiral's calls

### Float 1 — mission item 3 (delete `init.c0`) collides with the merged tripwire

Measured, not argued. Deleting the `init.c0` precondition from
`skills/commander/templates/COMMANDER_SPINE.template.json` and running the tripwire:

```
3 failed, 4 passed in 0.23s
  EnumerationDeliberateBreakage::test_refuses_broken_copy_and_passes_real_fixed_tree
  EnumerationGeneralizesPastOneEntry::test_refuses_new_second_entry_without_naming_known_fixed_entry
  EnumerationGeneralizesPastOneEntry::test_passes_once_new_entry_carries_the_precondition
```

Baseline is 7 passed. The cold critic independently reproduced the same 3-of-7 by its own
experiment. Cause: `scripts/verify_worktree_precondition_coverage.py` exists to assert that
the Commander template's `init` gate wires a command check containing
`verify_worktree_isolation.py`, and three tests pin that contract — one of them by using the
real template as the known-good entry that must *not* be named in a failure. Deleting the
check makes the guard's own premise false.

Two instructions in the same launch order collide: item 3 says delete it; Inherited Context
says the tripwire must be green and must not be weakened, and that "a green run is evidence
both halves landed". I did not resolve that by picking an authority source.

`decision:delete-not-repair-init-c0` is graded `settled/measured`, and inherited doctrine for
that tier is "you may re-measure; a contradicting new measurement is evidence: revisit, and
log the new measurement as the new provenance." This is that measurement.

**Coherent deletion is a four-file change**: remove `init.c0`, retire
`verify_worktree_precondition_coverage.py`, and delete its three enumeration tests — because
per-template wiring coverage becomes the *wrong question* once enforcement is engine-native
and no template can omit it. Retargeting the coverage script instead would make it vacuous,
which is the exact defect it was written to prevent. That is a structural and scope change,
both on the launch order's must-float list.

**Cost of NOT deleting it, stated plainly:** after the native guard lands, `init.c0` is a
check that cannot fail *for the isolation reason* — `start` is guarded, so the guard has
already proved cwd is inside the stored root before the precondition runs, making
`git rev-parse --show-toplevel` necessarily equal to `<repo-root>`. Every Commander spine
minted afterwards carries a green check that proves nothing, in a repo whose named defect
class is exactly that. Filed as `tc4`.

### Float 2 — the launch order's non-forwardability claim overclaims

The order says: "the engine asking itself where it stands cannot be lied to by a child
process's cwd." True and narrow. It does not follow that the change is non-forwardable.

`_run_check_command` (`checklist_engine.py:786`) runs command checks with **no `cwd=`**, so
`verify_worktree_isolation.py --here` already measures the engine process's own ambient cwd.
The native comparison reads `Path.cwd()` — the *same* value, one indirection earlier. An
agent that prefixes `cd <origin.worktree> &&` to its engine call satisfies the guard and can
still do every edit in the wrong tree. The guard proves where the engine process stood, never
where the work happened.

**The change is still worth making** — it is strictly stronger than what it replaces — but
for three different reasons, which is what the resumed run should claim and no more:

- **Coverage** — every guarded verb on every spine carrying `origin`, not just the one gate an
  author remembered to wire.
- **Unbypassability from the spine** — the comparison cannot be deleted from a template, left
  out of a new role's spine, or pre-satisfied in JSON.
- **An independent expected side** — the expected value is state stamped at creation, not
  check text a spine author writes.

This is reported as a correction to the order's framing, not as a reason to stop. It also
means the honest-null clause is partially engaged: the mechanism is not *wrong*, but one
property the order attributes to it is not delivered.

## Decisions taken inside my latitude

**Verb scope: guard `MUTATING_VERBS` plus `claim` plus `heartbeat`; exempt `current` and
`release`.** The first cut exempted all three early-returned verbs as "read-only"; the cold
critic proved that wrong and it was corrected. Only `current` is genuinely read-only
(`main()` skips `save()` for it alone). `heartbeat` writes `last_heartbeat` and `release`
writes `status`/`released_at`, and `main()` persists on both the success and the refusal
path. So:

- `current` exempt — inherited orchestrator doctrine has an invoker read a subordinate's
  `current` cross-tree for a `REFRESH REQUESTED:` line. Refusing it breaks a doctrine-mandated
  workflow. (This run is itself an instance of that workflow.)
- `heartbeat` guarded — keeping a lease alive from the wrong tree defeats stale-lease reclaim,
  and it costs nothing real because heartbeating requires owning a lease and `claim` is guarded.
- `release` exempt **deliberately** — the single recovery escape hatch. A lease on a spine whose
  worktree was removed at closeout must stay clearable, and a non-owner release already demands
  `--force --reason` on the record. This is a hole that carries a bounded write; it is stated,
  not hidden.

**Backfill: none.** Two live spines pre-existed this run
(`.agent-work/commander-315/spine.json`, `examples/mcp-interactive-demo/spine.json`); this
run's own spine makes three. The launch order's "2" is correct as of `9bb8c1b6`. Reasons for
leaving all of them to the fallback, in order of force:

1. Hand-editing a spine is forbidden — the engine owns that file and stamps the provenance.
2. `examples/mcp-interactive-demo/spine.json` is a **tracked example**. Its correct
   `origin.worktree` is whatever checkout a user clones into, so any absolute path committed
   there would be wrong for every consumer and would refuse for all of them.
3. `.agent-work/commander-315/spine.json` is a completed run in the prior Commander's
   worktree, which I am forbidden to enter.
4. The fallback exists precisely for this and is the path the merged tripwire exercises.

**Guard placement: `main()` after `load()`, before `dispatch()`, refusing without persisting.**
Because `main()` saves on the `EngineError` path, a refusal raised inside `dispatch()` would
write into the very tree the guard protects — and would write back a spine loaded before the
refusal, clobbering a concurrent legitimate writer. A guard that writes into the tree it is
protecting contradicts itself.

**Containment, not equality.** `verify_worktree_isolation --here` compares
`git rev-parse --show-toplevel`, which succeeds from any subdirectory. Requiring
`cwd == root` would refuse from `<root>/scripts` or `<root>/.agent-work/<id>` — a regression
smuggled in under a mechanism change. The repro now carries a subdirectory case (D) that only
containment passes.

## Falsified inherited context

**"The wired hooks call the engine you are changing" is false.** Measured:
`scripts/hooks/spine_rail.py` states in its own docstring (line 16) "Read the spine STATE
FILE directly; do NOT subprocess the engine", and keeps it — it reconstructs `current`
in-process (`reconstruct_current`, line 280) and its one subprocess is `git worktree list`
(line 507). `scripts/hooks/gauge_writer_hook.py` writes `gauge.json` and never calls the
engine. So the hook hazard the launch order flagged does not exist for this change, and the
fresh-process validation it asked for has no subject.

The real cross-tree engine caller is **`scripts/mcp_spine_server.py:361`**, which calls
`checklist_engine.main(argv)` **in-process** and never `chdir`s anywhere in the file. Under
the chosen verb scope its `spine_status` (`current`) keeps working; guarded door calls from a
main-checkout server process against a worktree spine will refuse. That is the true positive,
but it will surface first as "the door broke", so the refusal text must name the mismatch.

## Failure set, diffed against main's baseline

Measured on Linux with the source tree clean at `9bb8c1b6` (`git status --porcelain` empty
for all non-`.agent-work` paths):

```
$ py -m pytest tests/ -q -p no:randomly
2934 passed, 5 skipped, 1121 subtests passed in 119.86s
PYTEST_EXIT=0
```

**main's Linux baseline failure set: empty.** The 76 failures the launch order names are
Windows-only (path separators, unset git identity on the runner) and do not reproduce here.

**This branch's failure set: empty** — no source file was modified, so it is identical to the
baseline by construction.

**Set difference: empty.**

That result is honest but weak, and it must not be read as merge evidence: it holds because
nothing was implemented. The comparison that matters is not yet runnable. Two things are known
in advance about it:

- `tests/test_explorer_templates.py:342-360` **will** go red once the stamp lands — it
  instantiates a spine into a tmpdir and then runs the engine with no `cwd=`, so `claim`
  refuses. Its reconciliation (standing the test's own subprocess in the stamped root) is
  pre-authorized in the frozen plan. Same exposure: `test_iterative_planning_doctrine.py`,
  `test_shipped_check_commands_resolve.py`, `test_install_constellation.py`,
  `test_generate_spine.py`, and the `test_mcp_*.py` family.
- The Windows set can only be diffed CI-run against CI-run, since it does not reproduce here.

## The merged guard

`tests/test_worktree_precondition_wiring.py`: **7 passed** at `9bb8c1b6`, and 7 passed now
(nothing changed). It was **not** weakened.

**But its greenness does not prove what the launch order says it proves.** Every fixture in
that file builds an origin-less spine dict by hand (`:278-282`, `:362-378`), so under this
change it is green *by construction* and is structurally blind to the origin-carrying path.
It is real evidence for the **fallback** and for nothing else. The order's "a green run is
evidence both halves landed" does not hold, and the resumed run must not lean on it — the new
path needs its own deliberate-breakage coverage, which the frozen plan requires in a new test
file so the merged guard is neither weakened nor rewritten.

Worth noting for the Admiral: `IsolationGateSurvivesThroughTheCLI`'s own docstring
(`:304-331`) anticipates this change and says that if such a contract lands, "this fixture is
what needs updating: teach it the new form and keep both sides asserted." The frozen plan
chose the more conservative reading — add coverage elsewhere, touch nothing — because the
launch order's do-not-weaken instruction is the stronger constraint. If the Admiral prefers
the docstring's reading, say so.

## Map impact

None yet, and little expected. The repo has **no architecture map**: `map_orient.py` returns
`DEGRADED-UNPARSEABLE` with anchor count 0 (`docs/architecture/` absent, `map/INDEX.md` an
unfilled template, `map/ids.jsonl` empty). Discharged on the record with five hash-pinned
substitutes, three unmapped gaps and an escalation to the Admiral; receipt at
`.agent-work/commander-315-native/map-orientation.json`. The mission frame verifies FRAME-OK
against it.

The one durable-record impact the change *will* have is documentary:
`docs/CHECKLIST_SCHEMA.md` enumerates the top-level keys and does not list `origin`, and the
`LIFECYCLE_CONTRACT.md` that `build_origin` cites exists only inside `.agent-work/archive/`.
The frozen plan adds a schema-doc deliverable. Filed as `tc5`.

## Triage candidates (recorded on the spine)

- **tc1** — extend the origin stamp to child checklists. `instantiate_spine` writes only
  `spine.json`; `review.json` and `IMPLEMENTER_PLAN.json` come from other paths and will never
  carry `origin`, so the guard is inert exactly where crew subagents edit. 541 engine-drivable
  checklists in the archive, only 98 named `spine.json`.
- **tc2** — `spine_lifecycle.py:311` stores `str(Path(worktree))`, unresolved and
  native-separator, unlike `init_work_area`'s resolved `as_posix()`. A symlinked worktree
  opened via `open_work` could false-refuse from inside its own tree.
- **tc3** — an archived spine whose worktree was removed at closeout can never satisfy the
  guard again, so `claim --force` cleanup on it is refused forever. History shows archived
  spines *are* driven later (`f4a6a786`: 24 archived spines still hold an active lease).
- **tc4** — `init.c0` becomes a check that cannot fail once the guard lands (Float 1).
- **tc5** — `origin` undocumented in `docs/CHECKLIST_SCHEMA.md` (see Map impact).

## Workflow feedback — what I observed, not a rule

- **The rigor mechanisms at `plan` cost more context than the `execute` gate is allowed to
  start with.** Design-it-twice plus a cold critic on an engine-core change consumed enough
  context that the governor then refused `execute` at 23.8% against a 12% line. Both
  mechanisms were bias-to-yes and both paid for themselves — the critic caught six material
  defects in the frozen plan, including one that would have shipped a false-refusing guard —
  but the same agent could not then do the work it had just planned well. I do not know
  whether the right reading is that planning should be cheaper, that `execute`'s 30K reserve
  is mis-set, or that a Commander is simply expected to hand off here. The `execute` reserve's
  own note calls 30000 "a GUESS, revisable in place" and names a settle experiment that is not
  runnable from existing artifacts. This run is one datapoint for it: fill at the moment
  `start execute` was attempted, on a small two-file change with heavy front-loaded rigor, was
  **0.237941**.
- **Two Plan-type subagents dispatched to write files had no write tool** and returned their
  candidates as message text instead. Both said so plainly and the content was complete, so
  nothing was lost, but the "write your result to this path, that write IS the delivery"
  contract in the dispatch prompt was unsatisfiable for that agent type. I wrote their
  artifacts for them.
- **The launch order's stated hook hazard did not exist**, and checking it cost real effort.
  The order was emphatic ("both call the engine you are changing", "validate with a fresh
  process"), which made it feel load-bearing; the code says the opposite in a docstring at the
  top of the file. An inherited-context claim that is falsifiable by one `grep` is worth
  falsifying before designing around it.
- **The first version of my own repro had the defect the repo names.** It decided its verdict
  with a prose substring match and, worse, its first form let case B "refuse" for an unrelated
  reason (a lease held by case A) and reported the gate armed. I caught the second; the cold
  critic caught the first. A harness written to prove a guard discriminates is itself a guard,
  and it deserves the same suspicion.
- **`current` output is very long.** The `execute` imperative alone runs to roughly 2000
  characters, and `current` reprints the full imperative every call. On a run that calls
  `current` at every step this is a material share of the context the governor then measures.

## What the fresh Commander should do

1. Claim the same spine with the same session id (idempotent re-claim, not a takeover).
2. Read `STATE_NOTE.md`, then `MISSION_FRAME.md`, `PLAN_ALTERNATIVES.md` and
   `PLAN_CRITIC_TRIAGE.md`. Do **not** re-run design-it-twice or the critic — both are done
   and their output is frozen into `execute.json`.
3. `start execute` and drive `execute.json`'s single crew gate through `run_crew.py`.
4. Arm the new tests by mutation at integrate: revert each half in turn and show the new tests
   go red. The plan requires this because `c1` otherwise runs a test file the implementer
   authored, with nothing proving it has a failing side.
5. Re-run `repro_native.py` and paste the AFTER block next to the BEFORE block above.
6. Open the PR then, not before.
