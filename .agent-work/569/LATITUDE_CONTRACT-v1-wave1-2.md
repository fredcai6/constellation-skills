# Latitude Contract: `569`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent

Make a green qualitative gate mean something — **by telling the agent what would count, not by
telling it that it got it wrong**.

The measured hole is that 65 of 105 conditions in the shipped spine templates (62%) are
`check: null`, so at attest time the agent must invent the standard itself, cold, at the end of a
long gate. That is undelegated judgment dumped at the most expensive moment in the run. Moving the
basis to plan time turns attest into *pointing* rather than *composing*: work comes off the agent's
plate, and refusability is the side effect rather than the product.

The outcome that must not be violated: **this epic must not add machinery that is itself unwired.**
The epic's own foundation (`generate_spine.py`, which already requires a `because` per qualitative
condition) has zero callers in `skills/`, and 13 of 26 verifier scripts are referenced nowhere in
`skills/`. #345 wrote the warning in its own words — *"Do not fix this by adding another unwired
checker. That failure mode is available here and would be funny exactly once."*

## Success Shape

- A qualitative condition declares, at plan time, what evidence would satisfy it.
- A wedged verdict is impossible to express silently (a list-valued `match` either works or is refused).
- The journal distinguishes a repaired fail from a gate that never failed.
- Every check this epic ships is reachable from a template `command` check, or is on an allowlist
  with a stated reason.

**Honest null is a complete deliverable.** If wave 1 measures that most of the 19 unwired scripts
are genuinely dead rather than genuinely unwired, "delete them and ship no lint" is a successful
outcome, not a failed wave. Same for `generate_spine.py`: if no live path needs a compiler, deleting
it is a valid answer and closes the dependency WP1 was resting on.

## Checkpoint Protocol

**Cleared autonomous through wave 2. Stop-and-present before wave 3.**

Waves 1 and 2 run without checkpointing. I present once after wave 2 merges: what landed, what the
report-only checks actually measured against a real run, and what I would launch for waves 3–4.
Waves 3 and 4 revert to stop-and-present at each boundary unless cleared again at that checkpoint.

What reaches the user at a checkpoint: plain-English summary, the decision asks, measured numbers
where a claim rests on one, evidence on demand.

## Wave Plan (delivery-first inversion — human ruling, this contract)

| Wave | Issues | Why here |
|---|---|---|
| **1 — delivery guarantee + the pure hole** | #345, #444, #368 (registration lint + vocabulary rule); #371 (verdict mechanism) | Nothing later is trustworthy until "built" stops meaning "not wired". #371 is a check that cannot *pass* — smallest real hole in the epic. **#558 pulled**: it is a design question, not an implementation issue. |
| **2 — declared basis + evidence locators** | #556, #557 | The epic's core value. Runs *after* wave 1 so the locator machinery lands on ground that guarantees delivery. |
| **— CHECKPOINT —** | **#558 discussed here (human ruling)** | Present; re-clear or redirect. Contract expires here. #558's review-level doctrine is settled with the human BEFORE wave 3 dispatches. |
| **3 — plan-freeze validation + journal fidelity** | #518, #524, #381, #382, #459; #515, #390; #558 if the checkpoint discussion makes it runnable | Plan-time catches (a dead selector, an unpinned red-proof) are cheap-moment fixes and fit the intent. Journal fidelity serves the auditor rather than the agent — real, low burden, low priority. |
| **4 — reviewer machinery** | #375, #358, #363, #259, #223, #388, #376, #221 | Kept in 569 by human ruling despite sharing no mechanism with attestation. |

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | **surfaced** |
| Scope change (issue added/dropped/re-scoped) | **delegated** |
| Merge to main | **delegated** |
| Issue **closing** | **delegated** |
| Issue **filing** | **surfaced** — see the filing pre-ruling below; filing is the disfavoured exit |
| Fix-now triage (bounded fix applied immediately, not filed) | **delegated** |
| Spend / budget / model tier | **delegated** |
| Production defaults / user-visible behavior | **surfaced** |
| Making a new check blocking rather than report-only | **surfaced** |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated for this epic's own subject matter (verdict
  vocabulary, condition shape, enforcement wording), since the epic *is* a doctrine edit. Every
  apply is logged as a RULING in ADMIRAL_LOG. Constellation lessons are always exported, never
  silently confirmed.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Fix-now triage, scope change | Edit `skills/*/templates/*.json` (the shipped spine templates the epic measures) | **Pre-cleared by human, this contract.** Commanders edit templates directly. Compact-format JSON is edited as raw text, never round-tripped through `json.load`/`json.dump`. |
| Apply a lesson / fold doctrine | Edit `skills/_shared/global-*.md` (canonical doctrine) | **Pre-cleared by human, this contract.** Launch orders must cite `skills/_shared/global-*.md`, never `skills/<role>/references/global-*.md` — the latter is an install-time copy that `install_constellation.py` silently overwrites. |
| Merge to main | `gh pr merge`, `git push` | Fallback if the classifier vetoes: one human approval in the moment, remaining equivalent merges batched to the next checkpoint rather than re-litigated one at a time. |
| Issue closing | `gh issue close`, `gh issue comment` | Fallback: batch the closes to the checkpoint. |
| Spend / model tier | Agent dispatch at the tiers below | No external action. |

## Float-Up Routing

A Commander that floats a **decision**: adjudicate inside the delegated classes and log a RULING;
escalate surfaced classes and out-of-taxonomy to the human. A Commander that floats a **context
query**: answer from epic knowledge and continue it; reach the human out-of-band when the answer
exceeds my knowledge or this contract.

Per-class nuance: a Commander asking to **file an issue** is answered with the filing pre-ruling
below — fix it, or write an episode. Only a high-certainty run impact that cannot be fixed in the
wave comes to the human as a filing ask.

## Comms

Plain English by default. Technical depth and evidence on demand. Numbers stated as measured, with
what was measured named — no claim rests on the epic body where I can measure the ground myself.

## Budget / Model Parameters

**Sonnet for every commander and crew slot, all four waves.** Human ruling, this contract.

This is not only a cost call: it is a live test of the epic's own thesis. 569 argues that declaring
at plan time what would count takes work off the agent's plate. If a well-specified launch order
cannot let a smaller model do this work, the checklist is not taking enough off the plate — and that
is a finding this epic should want. Running it at opus would hide the answer.

The compensating investment is **launch-order specificity, not model tier**. The Admiral runs opus;
the thinking goes into the order — named files, named shape, pre-ruled ambiguities — rather than
into the commander.

**Recorded escalation fallback (`decision:double-block-escalation`).** A commander that returns
blocked **twice on the same obstacle** is re-dispatched at opus rather than left to grind. Bounded
and named, not open-ended. Every use is logged as a RULING and is itself evidence about where the
launch order was underspecified — which is the measurement this tiering choice exists to produce.

Known risk, stated rather than hidden: `checklist_engine.py` is 4,101 lines and wave 2 (#556/#557)
is surgery inside it. That is where the double-block trigger is most likely to fire.

**Usage-limit budget.** The account session pool is a wave-sizing input, not just a per-issue
budget. Waves 1 and 2 run unattended, so they are the ones at risk of stranding Commanders
mid-flight: size each to what the pool can carry, and when a limit reset is near, defer the next
dispatch past the reset rather than launching into it.

## Pre-Rulings

Each is overridable by the human at any checkpoint.

- `decision:delivery-first-order` — wave 1 is the wiring guarantee (#345 cluster), not WP1. The epic
  as filed runs the built-not-wired sweep last, which would audit machinery the epic itself just added.
  `@grade: settled/human · leans wave-1`
- `decision:report-only-default` — a new check that *refuses* ships non-blocking and emits a finding.
  It is promoted to blocking only after a real epic has run against it and produced measured
  sensitivity/specificity. The corpus already carries this flag-flip pattern (`--report-only` on
  `map_orient.py verify-frame`).
  `@grade: settled/human · leans all-waves`
- `decision:report-only-is-staging-not-posture` — **refinement forced by commit `244665ee`**, which
  landed after the human answered and rules against the reflex directly: *"reciting sensitivity 0/4
  without its adjudication is what sends the next reader reaching for `--report-only`,"* and `plan.c6`
  was ratified **blocking** with weak numbers in hand. Reconciliation: report-only in 569 is a
  **staging state for a check whose signal is not yet measured**, never a verdict that weak numbers
  mean weak check, and never a substitute for adjudication. Consequence with teeth — **every
  report-only check this epic ships must name its promotion trigger in the same PR that ships it**
  (what measurement, taken when, promotes it to blocking). A check shipped report-only with no named
  trigger is this epic committing its own defect: shipping something that cannot fail and calling it
  delivered. Where the adjudication is already available at authoring time, the commander ships it
  blocking and says so.
  `@grade: guess/admiral · leans wave-1 · settle: confirm this reading with the human at the wave-2 checkpoint`
- `decision:558-is-a-design-question` — #558 (high-level vs low-level review doctrine) is pulled from
  wave 1 and is **not** dispatched to a commander of any tier. It is settled with the human in
  conversation before wave 3. Handing an open doctrine question to a commander produces doctrine
  written by whoever drew the card.
  `@grade: settled/human · leans wave-2-checkpoint`
- `decision:widening-is-not-a-new-check` — report-only governs new *refusals*, not widenings.
  #371's list-valued `match` support is a widening of a comparison that is currently silently
  unsatisfiable, so it lands live. `validate_spine` **rejecting** a mistyped match shape is a new
  refusal, so it lands report-only. This reading is mine, not the human's answer.
  `@grade: guess/admiral · leans wave-1 · settle: state it at the wave-2 checkpoint and take the correction`
- `decision:prefer-fix-or-episode-over-filing` — something a little wonky gets **fixed**, or gets an
  **episode**. Issues are reserved for high-certainty run impacts that cannot be fixed immediately.
  A wave that ends having filed nothing and fixed several things is the intended shape.
  `@grade: settled/human · leans all-waves`
- `decision:generate-spine-disposition` — `generate_spine.py` has zero callers in `skills/`. Wave 1
  determines whether any live path needs a compiler at all. Deleting it is a valid answer and is not
  a failed wave; if it is deleted, WP1 carries the `because` field through whatever path is actually
  live instead.
  `@grade: guess · leans wave-1 · settle: trace every live spine instantiation path in wave 1 before wave 2 authors anything`
- `decision:registration-lint-shape` — implement #345's own options (1) registration lint and
  (2) vocabulary rule. Not (3) a reviewer-handoff question, which is prose enforcing prose.
  `@grade: guess/admiral · leans wave-1 · settle: measure how many of the 19 unwired scripts are dead vs unwired; a corpus that is mostly dead wants deletion, not a lint`
- `decision:imperative-bloat-handled-out-of-band` — RESOLVED before wave 1. The human fixed the
  `commander/plan` imperative directly in commit `244665ee` (683 → 477 words, ordering defect
  corrected, editor-facing prose moved to a `map_check_note` sibling field). Not 569 scope. Two
  consequences wave 1 inherits: (a) `map_check_note` is a **new template-only task field** registered
  in `TemplateOnlyFieldAllowlist`, so #368's "eleven-field mechanical group across five sites" census
  is stale by one field and must be re-measured, not copied from the issue; (b) `waive()` hardcoding
  `produced_by: "human"` and `override_policy.authority` never being compared were deliberately left
  open and filed onto #557 — that is **wave 2 scope**, already ruled by the human as fix-not-paper-over.
  `@grade: settled/human · leans wave-1`

## Expiry

**Event: the wave-2 checkpoint.** Crossing it forces a contract-refresh decision before waves 3–4
dispatch. Also refreshes early if wave 1 measures that the unwired-script population is mostly dead
code, since that invalidates `decision:registration-lint-shape` and the shape of wave 1's deliverable.

## Confirmation

`2026-08-22` — confirmed by Tommy ("go forth"), after ruling on wave order, WP5 retention, report-only
posture, latitude breadth, corpus-surgery pre-clearance, sonnet tiering, and pulling #558.
Recorded as `user-decision` evidence on the latitude step.
