# LIFECYCLE CONTRACT — the frozen design the gates build to

**Work id:** `epic-559/c3-lifecycle` · **Frozen at the `plan` step, base `293b7721`.**
Where this contract and a crew's judgment disagree, this contract wins. Where it is silent, the crew
decides and says so in its result.

## 0. How this was decided, and why there is no `g0` gate

Two plan candidates ran under distinct constraints (`smallest-diff` and `best-seam-placement`);
`DESIGN_IT_TWICE_BRIEF.md` records the contract and the untaken roads, and the two results sit beside
this file. Both candidates proposed a `g0` reasoning gate producing this document, copying C2's
`DESIGN_NOTE.md` precedent.

**Rejected, by the deletion test.** Delete `g0` and ask whether complexity reappears: it does not. C2
needed `g0` because its design was authored *inside* the run; here the Admiral's launch order asks for
these four answers **in the plan I float**, so the contract *is* plan output. A gate whose only
deliverable is a document the plan step already owes is ceremony. This document is that deliverable,
frozen here, and the plan carries five crew gates rather than six.

## 1. Convergence — a named hybrid

**Candidate B's seam, candidate A's scope discipline, and A's identity-pin finding, which B missed.**

The deciding evidence is that **A argued for B's structure in its own hurt section.** A scored its own
seam placement "Medium-low", wrote that putting `close_work` in `init_work_area.py` makes that file's
name stop describing its contents, and conceded that `best-seam-placement` "would very plausibly
centralize [the naming convention] as an interface guarantee, which is a genuine ergonomic win this
candidate declines to buy." When the minimal candidate names the other candidate's structure as the
thing it is giving up, that is convergence, not a tie.

Adopted from **B**:

- **A dedicated module, `scripts/spine_lifecycle.py`.** Open and close are its interface.
- **The worktree path and branch are derived from `work_id` inside the module.** A required them as
  caller-supplied strings and admitted that `spine_open` then "does not, by itself, fully answer 'how do
  I open work'." The mission is *one call*; a call that requires the caller to already know the
  convention is not one call.
- **`origin` carries `parent`, and `close_work` reads `origin.worktree` instead of asking
  `durable_root()`.** This is B's strongest single insight and it is the answer to the launch order's
  own complaint: the two-answer behaviour of `durable_root` (`scripts/agent_work_root.py:110`) stops
  being close's problem because close never asks the question. `durable_root` is **untouched** and
  remains the path for spines not opened this way.
- **Reuse `run_crew.spine_terminal`** rather than re-deriving terminality.

Adopted from **A**:

- **The identity-pin scoping finding** (§6 below). B did not find it. Verified independently:
  `tests/test_mcp_identity.py:998-999` iterates `module.TOOLS` and indexes
  `TOOL_MINIMAL_ARGS[tool["name"]]`, so adding a tool to `TOOLS` breaks that test on a `KeyError`.
- **The `not_yet_written` fix as a refusal, not a coercion.** Both candidates reached this
  independently — a strong signal. It is stricter than the launch order's literal "add the `isinstance`
  guard", and §7 states the deviation and its reason.
- **Two-dimensional occupied refusal**, the archive-already-exists refusal, and the stage-by-name source
  guard with a mutated positive control.

**Rejected from B: the shell CLI.** B shipped it only because its own constraint demanded a second
adapter, and admitted "nothing in this run's own measurements shows an EXISTING caller." Worse, B named
the real hazard itself: the standing ruling is *"the agents should not know about the cli. period"*, so
a CLI is a surface that, if a handoff ever named it, **is** the defect class this epic exists to close.
Paying a live risk to satisfy a structural aesthetic is the wrong trade. Deletion test: delete the CLI
— nothing reappears, because there is no second caller.

The honest consequence, stated rather than hidden: **one adapter is a hypothetical seam, not a proven
one.** The module ships with a single production adapter (the door). The second caller that exercises
the interface is the test suite, which calls `open_work`/`close_work` directly with no MCP transport in
the loop — which is exactly why B scored testability 5/5. If a second production adapter is ever
wanted, the seam is already where it needs to be.

## 1b. The cold critic, and what it changed

A cold critic read this contract, `GATE_PLAN.json` and `MISSION_FRAME.md` with no authoring context and
returned five confirmed findings and three suspicions. **All eight are accepted**; the sections below are
the revised text, and `plan-critic-result.md` holds the originals. Four changed the design:

- **The spine filename was going to be hardcoded** (§4). Accepted, and it is the single most likely way
  this plan would have produced a green run that is wrong.
- **`closeout_refusal` could not be both pure and a reuser of `run_crew.spine_terminal`** (§2, §4) —
  that function takes a *path* and reads the file. Resolved a third way, below.
- **The `TOOLS` trap has three coupled sites, not one** (§6).
- **"non-abandoned `engine_session`" named a status that does not exist** (§3).

**One correction back to the critic, which is the same discipline in the other direction.** Its headline
finding rested on `execute.json` outnumbering `spine.json` "20 to 7" under `.agent-work/`. Re-measured:
**48 vs 40** at depth 3, **98 vs 93** overall, **43 vs 42** excluding the archive. `spine.json` is a slight
*majority*, not a minority. **The finding survives its own wrong number** — the two conventions are
roughly even, this Commander's own driving spine is named `execute.json`, and no planned test would have
caught a hardcode either way. The mechanism was right and the value it carried was wrong, which is
exactly what this wave's review standard says to look for; it is recorded here rather than quietly fixed.

## 2. The module — `scripts/spine_lifecycle.py`

Pure/impure split at **function** granularity, matching `generate_spine.py`, `validate_spine.py` and
`checklist_engine.py`.

**Pure** (dict/str in, dict/str out; no `Path`, no `open`, no `subprocess`):

- `worktree_path_for(work_id, *, wt_root) -> str` — the derived worktree path.
- `branch_name_for(work_id) -> str` — the derived branch.
- `archive_name_for(work_id, *, today) -> str` — the archive directory name. **`today` is a parameter,
  never read inside**, so the function is testable without freezing a clock.
- `build_origin(...) -> dict` — the `origin` block.
- `closeout_refusal(spine: dict, *, archive_exists: bool) -> str | None` — `None` when close may
  proceed, else the refusal message. **This is the whole close-ordering predicate, pure and directly
  testable**; the impure `close_work` calls it and does nothing else about ordering.

  **It computes terminality from the dict it is given, and does NOT call `run_crew.spine_terminal`.**
  The critic was right that the two cannot be reconciled: `spine_terminal(spine, root)`
  (`scripts/run_crew.py:317`) takes a **path** and reads the file, so a function typed dict-in and
  forbidden I/O cannot call it. Splitting the terminality check out into `close_work` would make the
  claim "this is the whole predicate" false, which is the version of this the critic warned goes green
  while the wiring is unproven. So: one pure predicate, **plus a differential test** asserting
  `closeout_refusal`'s terminality verdict agrees with `run_crew.spine_terminal` on the same spine, over
  a terminal case and a non-terminal one. That pins the agreement the "never re-derive" instruction was
  reaching for, without pretending a pure function can do I/O.

**Impure**: `open_work(...)`, `close_work(...)`.

### Naming, derived from `work_id`

- Branch: `work_id` verbatim (`epic-559/c3-lifecycle`) — matches every branch in this epic.
- Worktree: `<wt_root>/<last segment of work_id>` where `wt_root` defaults to a sibling of the main
  checkout named `<repo-dir>-wt` — matches `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`,
  measured against the live tree.
- **Refuse any `work_id` that is unsafe as a path or a branch.** Reuse `run_crew`'s existing work-id
  validator; never write a second one.

## 3. Open

`open_work(work_id, spec, *, root, base, parent, wt_root=None)`.

Order, and **nothing survives a failure**:

1. Validate `work_id`. Refuse an unsafe one by name.
2. **Refuse if the derived worktree path already exists on disk.**
3. **Refuse if any spine for this `work_id` carries an `engine_session` whose `status` is `"active"`.**
   No staleness gate and no other status — `checklist_engine` only ever writes `"active"` (`:1033`) or
   `"released"` (`:1076`), which the critic verified by exhaustive grep. An earlier draft said
   "non-abandoned"; **that word was borrowed from the wrong registry** — `abandoned` is a `crew-runs.json`
   dispatch-attempt field (`run_crew.py:249`), not an `engine_session` one, and an implementer would have
   had to invent a meaning for it. Read-only scan in the defensive style of
   `agent_work_root._active_epic_lease`, which reads the same field the same way.
4. `git worktree add <worktree> -b <branch> <base>`.
5. Scaffold the work area (reuse `init_work_area.init_work_area`).
6. Compile the spine (reuse `generate_spine`, imported, never re-implemented).
7. Inject `origin` into the written spine and **re-run `validate_spine.validate` afterward**, so the
   record cannot make the spine invalid.
8. **Self-verify** with `verify_worktree_isolation.check_distinct_real([worktree],
   registered_worktrees(), primary_checkout())`, called in-process. `git` returning 0 is not evidence.
9. Return the crew-binding values: `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT`, the branch, and the
   worktree.

**Rollback.** Any failure at or after step 4 removes the worktree (`git worktree remove --force`, then
`git worktree prune`) **and deletes the branch this call created**, then refuses with a legible reason.
Rollback is scoped to what this call created — a pre-existing unrelated worktree is never touched.

### `origin`

```json
"origin": {
  "work_id": "...", "branch": "...", "worktree": "<absolute>",
  "base": "<sha>", "opened_at": "<iso8601>", "opened_by": "spine_open",
  "parent": "<the dispatching session, or the literal \"unknown\">"
}
```

Top-level on the spine, on the measurement in `MISSION_FRAME.md` (an unknown top-level key survives
`claim → start → attest → advance` untouched, and `validate_spine` has no unknown-key fault).

**Two residuals, stated not patched.** Nothing in `checklist_engine.py` defends `origin` — no verb reads
it and none refuses a malformed one; the round-trip is pinned by a regression test and by nothing else.
And `checklist_engine.claim()` already writes a **different** `worktree` field onto `engine_session`
(`scripts/checklist_engine.py:1037`) — that one is lease-scoped, set by whoever claimed, and does not
survive a release. It is not this record and must not be mistaken for it.

## 4. Close

`close_work(spine_path, *, root, today)`.

The order is fixed by the launch order and is not latitude. Steps 1–3 are the **caller's**, through the
door tools that already exist; `close_work` neither performs nor re-implements them:

1. satisfy the closeout gate's postconditions
2. final `advance` — `spine_advance`
3. `release` — `spine_lease`
4. **then** move the work area, spine file **last** ← `close_work` starts here
5. commit the move
6. report readiness

`close_work` **refuses, doing nothing at all**, unless all of:

- `engine_session.status == "released"` — naming "the lease is still active" when not;
- every item in `items` is terminal (reuse `run_crew.spine_terminal`) — naming the offending gate;
- the archive directory does not already exist — never overwrite a prior archive.

Then: `git mv` every top-level entry under `.agent-work/<work-id>/` **except the bound spine and its
journal**, each call naming its own paths; then `git mv` those two, **last**; then `git commit`.
**Never `git add -A`, never a bare `.`.**

**The excluded names are derived, never literal.** They are `Path(spine_path).name` and that name plus
`.journal` — *not* the strings `"spine.json"` and `"spine.json.journal"`. The critic caught this, and it
is the finding most likely to have shipped a green-but-wrong run: both filenames are in heavy use
(measured: `spine.json` 48, `execute.json` 40 at depth 3 under `.agent-work/`; 43 vs 42 excluding the
archive), **and this Commander's own driving spine is named `execute.json`**. A literal hardcode would
sweep the live driving checklist into the "everything else" batch *before* the spine-last step — the
exact failure the fixed ordering exists to prevent.

It is untestable by every matched-pair fixture, because a spine `open_work` created is always named
whatever `open_work` names it. So `g2` carries a **mandatory** close criterion: close a spine whose
basename is **not** the one `open_work` writes, and assert it still moved last. (`open_work` writes
`spine.json`; the differing-name fixture is therefore an `execute.json`.)

Finally it reports a verdict naming the branch, the new `HEAD`, and: **ready to PR.** It does not open
the PR, does not remove the worktree, and does not judge the work good.

### Archive naming — a decision neither candidate made

**`.agent-work/archive/<YYYY-MM-DD>-<work_id with "/" replaced by "-">/`**, e.g.
`.agent-work/archive/2026-08-12-epic-559-c3-lifecycle/`.

The launch order says `.agent-work/archive/<work-id>/`. Measured on disk, and **corrected by the critic**
from my own overstated first count of "39 of 41": **38** entries match the exact `YYYY-MM-DD-` form; one
more (`20260708-issue-87`) is date-prefixed in an older dash-less format; `curator-reports/` is a
recurring report directory and not an archived work area at all, so it does not belong in the
denominator; `issue-310` is the one genuinely non-conforming entry. None is nested. Following the
launch order's literal wording
would fragment the archive into two layouts. The archive path is not in the launch order's hard-
constraint list, so this is inside my latitude; it is recorded here and reported to the Admiral.

`today` is a parameter so the name is deterministic in a test.

## 5. The declared dispatch

Spec gains `[[gate.dispatch]]`: `role` **required**, `model` **required**. `parent` is **not** declared
per entry — it is filled from the spec's existing top-level `parent`, the same value
`_handback_contract`'s `hand_back_to` already uses, so one spec cannot name two different parents.

New spec-shape faults, refused before any probe:

- `spec-dispatch-missing-field` — a declared dispatch missing `role` or `model`.
- `spec-dispatch-unresolved-parent` — a dispatch declared while the spec's own `parent` is absent, so
  there is nothing concrete to fill in. Refuse rather than emit a dispatch naming `"unknown"`.
- `spec-dispatch-undeclared` — a gate whose imperative names a dispatch marker (`run_crew.py`,
  `constellation-implementer`, `constellation-reviewer`) but declares no dispatch is refused.

  **The critic was right that this narrows the hole rather than closing it, and the earlier draft
  overclaimed.** Detection is textual, so an imperative phrased without any marker ("hand this to an
  implementer crew") stays invisible. The honest statement: the defect goes from "a crew forgets
  `--parent`, invisible for a wave" to "an author phrases a dispatch with none of three markers,
  invisible for a wave" — a strictly smaller surface, not an empty one. There is no way to close it
  fully without the engine knowing what a dispatch is, which is an engine change and outside a
  Commander's latitude. **This is the direct answer to the launch order's own open question: the defect
  is narrowed, not gone, and the residual is stated rather than dressed up.**

The compiler renders `directives.dispatch` on the gate **and injects one `command`-kind postcondition
per entry** that reads `crew-runs.json` and refuses `advance` unless a non-abandoned entry for that
gate and role carries the declared `parent` and `model`.

`command`, never `artifact`, and the reason is measured, not stylistic: `DESIGN_NOTE.md` §6's own
correction records that `record`/`consolidate` never evaluate artifact-kind postconditions on a survey
item, so an artifact check would be silently inert there. A `command` check has a real existing oracle
(`crew-runs.json`, which records both fields — verified against this run's own entry) and behaves the
same on `gated` and `survey`.

**The residual, stated plainly.** The rendered imperative is still prose a crew reads, so a forgotten
`--parent` is still *possible at dispatch time*. What changes is that it can no longer be advanced past
silently. The defect moves from "invisible for a wave" to "refuses at the next gate boundary."

## 6. The door — and the trap A found

Two tools, `spine_open` and `spine_close`, on the **already-registered** `spine` server. No `.mcp.json`
change; a tool is not a server.

**Two, not one.** Their identity postures are opposite: `spine_open` acts on a spine that does not exist
and must never touch `SPINE`/`SESSION`; `spine_close` acts on the bound spine and nothing else. An
`action: open|close` switch would put both postures inside one function body, which is precisely the
"a guard written for one hazard covers the other by accident" failure `_identity_violation`'s own
docstring records as history.

**Dispatched from `call_lifecycle_tool`, a module-level sibling of `call_tool`.** The choke-point pin
resolves `call_tool`'s own `ast.FunctionDef` node and walks only that subtree, so a sibling is
structurally outside it. `call_tool`'s body is **not touched** and the pin stays exactly as strict.

This is not routing around a guard, and the distinction must survive review: the pin exists because the
engine door is a pass-through, and its docstring says so. A lifecycle tool is **not** a pass-through and
must not pretend to be one. So it gets **its own** containment pin rather than inheriting one written
for a different hazard:

- an AST pin over `call_lifecycle_tool` restricting its returns the same way, with a mutated positive
  control proving the pin can fail;
- an assertion that `spine_open`'s path **never references** `SPINE`, `SESSION` or `run_engine` — the
  property that makes "it does not presuppose a bound spine" a checked fact rather than a claim;
- containment on every caller-supplied path, reusing `_resolve_confined`'s posture.

**How the tools are actually reached.** `main()`'s `tools/call` branch (`scripts/mcp_spine_server.py:962`)
routes every known name to `call_tool` unconditionally, so `main()` must grow a branch sending the two
lifecycle names to `call_lifecycle_tool` instead. The critic found this absent from an earlier draft and
was right that it is the one piece of plumbing that makes the separation reachable at all. It is named
here so it is not improvised: **route in `main()`, never inside `call_tool`.**

**The trap, and the wrong fix.** Adding two tools to `TOOLS` breaks **three** coupled sites in **three**
files — the earlier draft named one, and the critic found the other two. All are verified:

| Site | What it asserts |
|---|---|
| `tests/test_mcp_identity.py:998-999` | iterates `module.TOOLS`, indexes `TOOL_MINIMAL_ARGS[tool["name"]]` → `KeyError` |
| `tests/test_mcp_adoption.py:236,246` | `set(DOOR_TOOL_NAMES) == server.TOOL_NAMES` and `len(...) == 9` |
| `tests/test_crew_launcher.py:536,551` | derives the crew grant from `TOOL_NAMES` and asserts `len(...) == 9` |

The last two are deliberate regression pins that exist *because* the door once grew from 7 to 9 tools
while a hand-typed list froze — so they are working exactly as designed, and updating them is the
required work, not a workaround. `test_crew_launcher.py:536` also means the lifecycle tools must be
added to `CREW_ALLOWED_TOOLS`, or a dispatched crew cannot call them.

**The required fix** is to scope the identity sweep to the engine tools
(`TOOL_NAMES - LIFECYCLE_TOOL_NAMES`) and update the two counts and the grant. **The forbidden fix** is
to handle `spine_open`/`spine_close` inside `call_tool` to make the sweep pass — that is the exact
regression the pin exists to catch, arriving disguised as test maintenance. The gate handoff names both.

## 7. Deviations from the launch order's literal wording

Both are inside latitude; both are reported to the Admiral.

1. **`not_yet_written` refuses rather than coerces.** The order says "add the `isinstance` guard." A
   guard that silently reinterprets a TOML `"false"` as absent reproduces the exact silence
   `generate_spine.py` exists to end. It is refused as a spec-shape fault, naming the field and its
   type. Both plan candidates reached this independently.
2. **The archive path is date-prefixed** (§4), against the shipped convention rather than the order's
   shorthand.

## 7b. The plan is authored TDD-red, and the oracle has no word for that

`python scripts/validate_spine.py --root . .agent-work/epic-559/c3-lifecycle/GATE_PLAN.json` reports
**exactly five** `falsifiable-zero-collected` faults — one per gate's `c1`. Every one is a selector for
tests **this run's own gates write**. They collect zero today and will collect the declared minimum by
the time the engine runs them at `advance`.

This is not a shrug. It is the same situation `generate_spine.py`'s `not_yet_written` field exists for,
and **`validate_spine.py` has no equivalent concept** — so a legitimately-not-yet-written check and a
permanently-vacuous one are indistinguishable to the oracle. Measured while finding this, and worse than
the launch order's description of the carried finding: `not_yet_written = "false"` (a TOML *string*)
compiles the check to `None`, so the gate does not merely misread a declaration — **it silently loses
its check entirely.** `g5` fixes the truthiness read; the oracle's missing concept is a finding for the
return, not something this run changes (`validate_spine.py` is a no-go).

Attack this if it is wrong. The claim being made is narrow: these five are red **because the code does
not exist yet**, not because the selectors are wrong.

## 8. What this contract deliberately leaves out

`git worktree remove` · opening a PR · any change to `checklist_engine.py`'s on-disk format · any change
to `validate_spine.py` · a shell CLI (§1) · retrofitting `origin` onto spines opened by hand · the
survey artifact-postcondition gap and the evidence-provenance gap C2 floated (both engine changes, above
a Commander's latitude).
