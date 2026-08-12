# Implementer Handoff — `g2` rework round 2 · make Property 2 honest on a survey

**Work id:** `epic-559/c2-generate-the-spine` · **Gate:** `g2-implement` (reopened, rework 1/3)
**Model:** Sonnet · **Dispatched by:** the Commander (delegated) under Admiral
`admiral-epic-418-followon`.

Your round-1 work was **not** rejected. Both specs, both generated spines, the `notes-2.md` findings and
the carried cleanup all stood up to independent re-running by the cold reviewer, and your
settling-question report was verified accurate down to the residual. **One thing blocked, and it is a
defect in my frozen design note, not in your work.** You are being asked to fix my mistake.

## What the cold reviewer found

Read it in full first:
`.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-review-result.md`, criterion 7.

Summary. It copied the generated reviewer survey to scratch, resolved the tokens, drove every item
through `record`, and consolidated. **The survey consolidated `APPROVE` with `r6-fowler`'s injected
`c-escalation` postcondition still unsatisfied and no `review-result` ever attached.** The engine
explains why, and it is deliberate, pre-existing behaviour (#422/#328):

- `checklist_engine.record()` on a `survey` item evaluates **only `command`-kind** postconditions.
  `artifact`-kind and `null`-kind are left unevaluated.
- `consolidate()` is flatter still — it reads each item's `result` field and nothing else.
- `advance()` (the `gated` closing verb) checks **every** postcondition with no kind filter.

So the large-claim escalation works exactly as DESIGN_NOTE §6 claims **on a gated gate**, and is
**silently inert on a survey gate**. That is not a narrow residual — it means Property 2, one of the two
non-optional properties of this whole mission, does not hold for *any* survey-type role spec: this
reviewer spec, and every future reviewer or interrogator spec the format is ever asked to generate.

DESIGN_NOTE §6 named a *different and narrower* residual (a determined agent could attach a spoofed
APPROVE). The real gap is worse: **nothing needs to be attached at all.**

## The decision, made by me — implement it, do not redesign it

The engine is **not** changed. That is a float to the Admiral and it is outside both our latitudes.

**On a `gated` spec: unchanged.** `magnitude = "large"` injects `c-escalation` exactly as today.

**On a `survey` spec: do not inject a postcondition the engine provably never consults.** Instead make
the non-enforcement loud, in the substrate that renders:

1. **Inject nothing** into `postconditions` for a large claim on a `survey`.
2. `directives.claim` on that item gains an **`enforcement`** field stating plainly that it is not
   machine-enforced here and why — naming `record()`'s command-kind-only scope and `consolidate()`'s
   result-only read, and saying the tier above must adjudicate it.
3. The `claims_rollup` entry for that claim carries the same `enforcement` value, so a reader of the
   terminal item sees which claims are gated and which are not.
4. On a `gated` spec, `directives.claim` gains the same field with the enforced reading (naming the
   injected `c-escalation`), so the two cases are told apart by content rather than by absence.

### Why not the obvious alternative — read this, it is the point

The tempting fix is to emit the survey escalation as a **`command`-kind** check, since `record` *does*
evaluate those. Do not. There is no artifact in this corpus that a command could honestly check for
"an independent reviewer approved this survey item", so the check would have to invent a file convention
with **no producer anywhere** — turning a gate that cannot fail into one that **cannot pass**.

That is not a hypothetical. It is prior-wave verdict B, cited in this run's launch order: a gate
promising "no unresolved blockers" while checking only that some artifact arrived was "fixed" by
constraining it to `match: {"status": "complete"}`, and a census of 122 real records found only 23% had
that shape. **The fix flipped the defect's sign rather than removing it**, and shipped in the template
every Commander instantiates. We are not doing that again.

Stating a limit truthfully beats enforcing it falsely.

## Close Criteria

Everything from round 1 still holds. New:

1. **A large claim on a `survey` spec injects no postcondition**, and `directives.claim.enforcement`
   states the non-enforcement, naming the mechanism (`record` evaluates only command-kind postconditions
   on a survey item; `consolidate` reads only `result`).
2. **A large claim on a `gated` spec still injects `c-escalation`**, and its `directives.claim.enforcement`
   states the enforced reading.
3. **The rollup carries `enforcement` per claim**, so the terminal item distinguishes gated from
   ungated claims.
4. **A test that would have caught this**, and it must *drive* the engine, not inspect JSON: build a
   generated survey carrying a large claim, drive every item through `record`, `consolidate`, and assert
   the outcome matches what `directives.claim.enforcement` says it will be. The round-1 evidence gap was
   exactly that the escalation's shape was dumped but never driven — close that gap with a test, so no
   future change can reopen it silently.
5. **A falsification-floor test for the new branch**, in the style of the one you already wrote: remove
   the survey/gated distinction and a named test must go red.
6. `specs/reviewer.spine.toml` regenerated, both generated spines still `OK` with **zero undecidable**.
7. `notes-2.md` gains a finding recording the engine asymmetry as measured behaviour, with the commands
   that show it — this is evidence going to the Admiral, so make it reproducible by someone else.
8. `--sweep` still exactly **23** fault lines; the full suite passes (baseline now **2767 passed, 3
   skipped, 1121 subtests**).

## Allowed Scope

- **Modify** `scripts/generate_spine.py`, `tests/test_generate_spine.py`, `specs/reviewer.spine.toml`
  (and `specs/implementer.spine.toml` if the gated-side `enforcement` field needs it), the two files
  under `.agent-work/epic-559/c2-generate-the-spine/generated/`, and `notes-2.md`.
- Nothing else.

## Specific Exclusions

- **Do not modify `scripts/checklist_engine.py`.** The asymmetry is real, pre-existing and out of scope.
  It is being floated to the Admiral by me.
- **Do not modify `scripts/validate_spine.py`.** Hard stop.
- Do not edit any shipped template.
- **Do not invent a command check with no producer.** See "Why not the obvious alternative" above.
- Do not update `DESIGN_NOTE.md` — it is the Commander's artifact and I will correct §6 myself, along
  with the `r0-context` factual error the reviewer confirmed you were right about.

## Test Mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

`python`, not `python3`. Unset the three spine variables — `mcp_spine_server.py` reads `SPINE_FILE` at
import time. Baseline: **2767 passed, 3 skipped, 1121 subtests**.

## Required Evidence

1. The driven test from close criterion 4 — the actual `record`/`consolidate` run and its outcome.
2. The falsification floor going red with the distinction removed, green restored.
3. The emitted `directives.claim` for both a survey claim and a gated claim, side by side.
4. The rollup showing `enforcement` per claim.
5. Both generated spines `OK`, zero undecidable.
6. `--sweep` count; the full suite.

## Stop Conditions

- If you conclude the decision above is wrong, **say so and stop** — do not implement a third design. I
  would rather spend a round trip than ship a mechanism neither of us believes in.
- The oracle would have to move: hard stop, return.

## Return Format

Write to `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-implement-result.md`
(overwriting round 1 — the reviewer's own copy of round 1 is preserved in its result file) **before you
end your turn**.

Open with **`Return status: complete`** on its own line, lowercase. Then the evidence above, what
changed since round 1, any finding, and a **Workflow Feedback** section — including, plainly, whether
this rework handoff gave you a decision you could implement or one you had to guess at.
