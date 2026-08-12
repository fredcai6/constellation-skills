# Implementer Handoff — g4: the dispatch is emitted, not remembered

**Work id:** `epic-559/c3-lifecycle` · **Gate:** `g4` · **Role:** `implementer` · **Model:** sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` (you are already in it)
**Parent:** `constellation/epic-559/c3-lifecycle/execute/commander/attempt-1` — the Commander.
**Result artifact (this write IS the delivery):**
`.agent-work/epic-559/c3-lifecycle/crew-handoffs/g4-implementer-result.md`

## Read first

`.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` — **§5 is your specification.**
`.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` — the generator's frozen contract, especially
**§4 (the closed kind vocabulary), §6 and its `### CORRECTION` block, §7 (the fault vocabulary), and §9
(the guard-fixture standard)**. Then read `scripts/generate_spine.py`: `_cond_faults`,
`spec_shape_faults`, `_compile_gate` (the `[gate.claim]` injection is the pattern you are following), and
`_escalation_postcondition`.

## Why this exists — the failure it closes

Last wave, six sub-crews were dispatched naming the **Admiral** as parent rather than the dispatching
Commander, and none carried an explicit `--model`. **Both instructions were in the launch order**, and one
appeared nine more times in the Commander's own frozen plan. The mechanism was never broken — `parent`
reaches the registry only from `args.parent` and works fine. What failed was *remembering*.

The human's ruling, verbatim: *"the regressions are disappointing, that's literally point of having a
template, once it's there it takes effort to remove, not effort to remember."*

So: **a spec declares the crews a gate dispatches, and the generator emits the dispatch with parent and
model already in it.** Removing them then requires editing a committed file and shows up in a diff.

## Task

### 1. The spec extension

`[[gate.dispatch]]`, with `role` **required** and `model` **required**. `parent` is **not** declared per
entry — it is filled from the spec's existing **top-level** `parent`, the same value
`_handback_contract`'s `hand_back_to` already uses, so one spec cannot name two different parents.

### 2. Three new spec-shape faults, refused before any probe

- **`spec-dispatch-missing-field`** — a declared dispatch missing `role` or `model`. Name the gate and the
  field.
- **`spec-dispatch-unresolved-parent`** — a dispatch declared while the spec's own top-level `parent` is
  absent. Refuse rather than emit a dispatch naming `"unknown"`.
- **`spec-dispatch-undeclared`** — a gate whose `imperative` names a dispatch marker (`run_crew.py`,
  `constellation-implementer`, `constellation-reviewer`) but declares no `[[gate.dispatch]]`.

**Be honest about what the third one does, in the fault text and in your result.** Detection is
**textual**, so an imperative phrased with none of the markers ("hand this to an implementer crew") stays
invisible. It **narrows** the hole; it does not close it. The defect goes from "a crew forgets `--parent`,
invisible for a wave" to "an author phrases a dispatch with none of three markers, invisible for a wave" —
a strictly smaller surface, not an empty one. **Do not write a fault message or a doc line claiming it is
closed.** Closing it fully needs the engine to know what a dispatch is, which is out of scope.

### 3. The emission

In `_compile_gate`, for each declared dispatch:

- render it into `directives.dispatch` (a list of `{role, model, parent}`), so a crew reading the gate
  sees exactly what to dispatch and under what identity;
- **inject one `command`-kind postcondition per entry** that reads `crew-runs.json` and refuses `advance`
  unless a **non-abandoned** entry for that gate and role carries the declared `parent` and `model`.

**`command`, never `artifact`, and the reason is measured, not stylistic.** `DESIGN_NOTE.md` §6's own
`### CORRECTION` records that `record()`/`consolidate()` never evaluate artifact-kind postconditions on a
survey item, so an artifact check would be **silently inert** there — Property 2 failing for every survey
spec. A `command` check has a real existing oracle (`crew-runs.json`, which records `parent` and `model`
per entry — verified against this run's own registry) and behaves the same on `gated` and `survey`.

Write the small reader it shells out to (`scripts/verify_declared_dispatch.py`). **Reuse
`run_crew.py`'s existing registry loading and `is_abandoned` — do not re-parse that JSON a second time.**
Anchor the emitted command `cd <repo-root> && …` and `shlex.quote` every token, exactly as every other
compiled check in this generator does.

## Protected intent

A forgotten `--parent` must stop being a thing a wave discovers later. It does not have to become
impossible — it has to become **refusable at the next gate boundary**.

## Close criteria

1. **VIOLATING** — a declared dispatch missing `model`; and one missing `role`. Each refused **by fault
   name**.
2. **VIOLATING** — a dispatch declared on a spec with no top-level `parent`, refused rather than emitting
   `"unknown"`.
3. **VIOLATING** — a gate whose imperative names `run_crew.py` with no declared dispatch, refused.
4. **VIOLATING** — a registry entry naming the **wrong parent** fails the injected postcondition. This
   reproduces the exact defect the launch order names; make the wrong parent *realistic* (a real-looking
   Admiral session id), not obviously garbage.
5. **VIOLATING** — a registry entry with the wrong `model`; and one with no matching entry at all.
6. **INNOCENT** — `role` + `model` + a concrete top-level `parent` compiles clean and injects the
   postcondition; a matching registry entry passes it.
7. **INNOCENT** — a gate with **no** `[[gate.dispatch]]` and no marker in its imperative gets no
   postcondition and no fault.
8. **ACCEPTED_FALSE_ALARM, populated not merely named** — an entry with the wrong parent but
   `abandoned: true` does **not** block. A naive first draft that ignored `abandoned` would flag it; this
   fixture pins that the shipped one does not.
9. The injected postcondition's **shape** is asserted: `command`-kind, not `artifact`.
10. **The two shipped specs declare no dispatch**, so nothing shipped moves:
    `python scripts/validate_spine.py --sweep --root .` still reports exactly **23**.
11. Suite green.

## Allowed scope

`scripts/generate_spine.py` · `scripts/verify_declared_dispatch.py` (new) ·
`tests/test_generate_spine.py` · `tests/test_declared_dispatch.py` (new) · `map/` (regenerated, never
hand-edited).

## Specific exclusions

- **Do not touch `scripts/spine_lifecycle.py` or `scripts/mcp_spine_server.py`** — g1, g2 and g3 own them
  and all three are reviewed.
- **`not_yet_written` is g5's, not yours.** You will see `cond.get("not_yet_written")` at
  `scripts/generate_spine.py:424` and `:673` read with bare truthiness. **Leave it alone.** Likewise
  `generate_spine.py:910`'s missing `newline="\n"` — g5 owns that file's carried findings.
- `scripts/validate_spine.py` is **not** changed. If you believe it must be, **block and say so.**
- Do not edit `DESIGN_NOTE.md`. g5 reconciles it, and it will add your new fault codes to §7 — just list
  them clearly in your result so g5 can.

## Constraints — a violation voids the gate

- `checklist_engine.py`'s on-disk format unchanged; `validate_spine.py` unchanged.
- `settings.json`, `.mcp.json`, `docs/agents/*` untouched. **If the harness refuses an `Edit`/`Write` on
  `.mcp.json`, that guard is deliberate — do not route around it with a `Bash` write. Block and ask.**
- `skills/**` untouched — a different crew owns it. If something there must change, **block and say so.**
- **`encoding="utf-8", newline="\n"` on EVERY write** (`docs/agents/CREW_CONTEXT.md:43`); CI runs
  `windows-latest`. g1 was BLOCKed for exactly this.
- Never run `scripts/install_constellation.py`. No merge and no push to `main`. Never `git add -A`.
  Never two crews in one worktree.

## Deliverable path check

- **Committed** — `scripts/verify_declared_dispatch.py` and `tests/test_declared_dispatch.py` (both new;
  `git check-ignore` exits 1, verified), plus the two edited files.
- **Local-only** — your result artifact under `.agent-work/`; the Commander commits it.

## Required evidence

Load-bearing — prove rigorously:

1. The wrong-parent fixture (criterion 4): the registry entry, the postcondition command actually run, and
   its non-zero exit with the message naming the offending entry.
2. The `ACCEPTED_FALSE_ALARM` abandoned-entry fixture (8).
3. One real `python scripts/generate_spine.py` run against a fixture spec carrying `[[gate.dispatch]]`,
   with the emitted `directives.dispatch` and the injected postcondition pasted verbatim.

Confirmatory: the fault names, the suite total, the sweep count.

```
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
cd /home/tommy/projects/constellation-skills-wt/c3-lifecycle && python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
```

**Baseline before your change: 2884 passed, 3 skipped, 1121 subtests; sweep exactly 23.** Use `python`,
never `python3`.

## Stop conditions

- A constraint above would have to be violated → **block**, name it, return.
- The injected postcondition cannot be made to fail on a wrong parent → that refutes the gate's whole
  premise. **Block and say so with the output.** A measured negative is a complete deliverable.
- Two failed attempts at the same check → block rather than a third.
- **Never waive.** `spine_halt` with `action=block`, name what you cannot satisfy, and return.

## Return format

Write the result artifact at the path above **before ending your turn**. Carry a **`Return status`** field
whose value is exactly `complete` (lowercase) when done, the evidence above pasted verbatim, **an explicit
list of every new fault code** (g5 needs it for `DESIGN_NOTE.md` §7), an honest statement of what
`spec-dispatch-undeclared` does and does not close, and a short **Workflow Feedback** section.
