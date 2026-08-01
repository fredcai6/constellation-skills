# Implementer Handoff — issue-304 gate g2: wire the contract at context and plan

## Assigned task

Add `verify-frame` to `scripts/map_orient.py`, wire the contract into
`skills/commander/templates/COMMANDER_SPINE.template.json` as engine-checked command postconditions,
and register the script in `install_constellation.py`.

Work ONLY in `C:/Programs/constellation-skills-wt/e298-304`. Never touch `C:/Programs/constellation-skills`
or `C:/Programs/constellation-skills-wt/e298-331`. **`C:/Programs/f1Brainz` is READ-ONLY — and note that
`orient` WRITES a receipt into whatever `--root` you give it.** Your commander already made this mistake
and had to clean it up. Do not point `orient` at f1Brainz.

## Protected intent

This gate makes the contract **load-bearing** rather than requested. The seam: **anchor ids exist only in
the map**, so citing them is set-membership proof the map was read. That turns "did the map inform the
plan" into a question a machine can answer with no stochastic judgement.

**Know what this does and does not achieve, and do not overclaim it in any comment or docstring.**
Measured against the epic's baseline five, this check has **sensitivity 0/4 and specificity 0/1**: four
runs cited map artifacts while exhibiting the defect (they would pass), and the one run that would fail
it was correct to disengage. It ships as a **regression floor** so map-*ignoring* cannot silently return.
It is **not** the fix for the measured defect, which is map-*lateness* and needs a harness hook the
corpus does not own. Say so plainly if you document it.

## Deliverables

### 1. `verify-frame` in `scripts/map_orient.py`

```
map_orient.py verify-frame --root ABS --work-id ID
```

Reads the mission frame at `.agent-work/<work-id>/MISSION_FRAME.md` and the receipt written at context.

- **RESOLVED mode:** every anchor id cited in the frame must exist in the map inventory computed by
  `orient`. An id that does not resolve → refuse, naming it.
- **DEGRADED mode:** anchors are checked against the **hash-pinned substitutes declared in the receipt**.
  This is the point of the pinning — the frame is compared against a *committed prior declaration*, not
  a same-breath assertion by the same agent. A substitute cited in the frame but absent from the receipt
  → refuse.
- **A frame whose anchors are all source paths** (`src/foo.py`, `scripts/bar.py`) is a frame cut from
  code → refuse.
- **An ABSENT frame REFUSES.** It must never vacuously pass. This is the single most important negative
  case in this gate — write the test first.
- Reuse the frozen exit-code vocabulary from g1. Do not invent new codes.

### 2. Wiring into `COMMANDER_SPINE.template.json`

**The wiring is explicit and asymmetric — read this twice.** The first draft of this plan was ambiguous
here and the cold critic BLOCKed it, because the cheap resolution silently destroys the anti-vacuity
property:

- **`verify-orientation` goes at the CONTEXT step**, as a new postcondition `c2`.
- **`verify-frame` goes at the PLAN step.**
- **`verify-frame` must NOT run at context** — no frame exists there yet, and making "absent frame at
  context = pass" would defeat deliverable 1's ABSENT-frame refusal.

Both as `{"kind": "command", "command": "python <commander-skill-dir>/scripts/map_orient.py <sub> --root <repo-root> --work-id <work-id>"}`.

Use `<repo-root>` (added in g1) — **not** a relative path. Command checks inherit the launcher's cwd; the
existing relative checks are fragile, not broken (filed as #341 — **do not fix them here**).

Give the plan-step check an `override_policy` of `{"allowed": true, "authority": "human",
"reason_required": true}` so the trivial-change escape survives as a **recorded waiver** rather than a
silent skip. Keep the context check's policy tighter.

**Keep the gate-vs-report choice flag-flippable** — a ruling to gate or un-gate should be a flag flip,
not a rebuild.

### 3. `install_constellation.py`

Add `map_orient.py` to `SKILL_SCRIPT_BUNDLES` for the commander bundles. If it has a runtime-companion
mechanism, use it so the script cannot be shipped without whatever it needs.

### 4. Tests

- `verify-frame` matrix: resolved-and-valid → pass; unknown anchor → refuse naming it; all-source-path
  anchors → refuse; **absent frame → refuse**; degraded-with-declared-substitute → pass;
  degraded-citing-an-undeclared-substitute → refuse.
- **`orient` must NEVER print an anchor id.** Assert its stdout contains no
  `^(struct|capability|event|constraint|assumption|claim|decision):` token. If it prints them, the
  citation check becomes self-satisfying — an agent could paste back what the tool told it. This test is
  load-bearing; do not drop it.
- **Template wiring assertions:** context `c2` is a command check naming `verify-orientation`; the plan
  check names `verify-frame`; **neither uses a relative root**.
- Extend the mutation floor with at least one mutation against `verify-frame` — and keep the
  **applied-before-red** discipline (assert the substitution landed via a strict count delta; a
  non-matching anchor must raise a loud harness error, never be credited as a kill).

## Allowed scope

`scripts/map_orient.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`,
`scripts/install_constellation.py`, `tests/test_map_orient.py`, `tests/test_mutation_floor.py`, and a new
test file if you prefer to separate the wiring assertions.

## Specific exclusions

- **No prose deletion** — that is g3. Leave the dead-path block alone this gate.
- **No bootstrap/CLAUDE.md stanza.** Ruled OUT: the map is orchestrator content, not implementer content.
  Placing content at a broader tier than its audience is a defect.
- Do not touch `reconcile` — wiring is context and plan **only**.
- Do not fix #341 (fragile relative checks), #342 (episode store), or the `--receipt-dir` triage item.
- Do not modify `checklist_engine.py`.

## Constraints

- Windows: `encoding='utf-8', newline='\n'`.
- `python -m pytest` (local 3.14 vs CI 3.12 — **no 3.13+-only APIs**; `Path.read_text(newline=...)` cost
  39 CI failures on PR #320).
- **`COMMANDER_SPINE.template.json` is pinned by several tests** — `test_context_manifest.py` pins
  `tasks.context.context_refs` as a literal list, `test_context_declaration_lint.py` requires every
  declared `context_refs` path to appear verbatim in that task's imperative, and
  `test_context_determinism.py` overlays the template into fresh checkouts. If you add a `context_refs`
  entry you must also make the path appear in the imperative. Run all three.
- Two-bin rule: machinize the mechanizable; the rest stays prose. No third bin.

## Required evidence

```
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_install_constellation.py -q
python scripts/map_orient.py --self-test
```

Both green. Plus paste: the exact JSON of the two new checks as they appear in the template, and the
output of `verify-frame` refusing an absent frame.

## Stop conditions

Stop and report if: wiring `verify-frame` at plan cannot be done without also running it at context; the
template's pinning tests cannot be satisfied without changing what they pin; or a required negative case
cannot be written so it fails. **Report "this specific thing failed", never "this approach is
impossible."** Never fabricate evidence.

## Return format

Write `IMPLEMENTER_RESULT` to `.agent-work/issue-304/crew-handoffs/g2-result.md` with evidence pasted
verbatim, every deviation and its reason, and any unresolved blocker. **Only claim a cleanup you have
verified** — g1's result asserted a removal that had not happened. Return thin.
