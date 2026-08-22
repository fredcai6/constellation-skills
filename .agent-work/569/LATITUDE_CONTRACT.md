# Latitude Contract: `569` — v2 (wave 3)

**Refreshed `2026-08-22` at the wave-2 checkpoint.** v1 (waves 1–2) is preserved verbatim at
`LATITUDE_CONTRACT-v1-wave1-2.md`. v1 expired on its own terms — *"Event: the wave-2 checkpoint"* —
and this replaces it. Confirmed by Tommy: *"still sonnet, you got the latitude."*

The evidence base for this refresh is the wave-2 interrogation: `.agent-work/569/interrogation.json`
(consolidated `RESOLVED`) and `.agent-work/569/INTERROGATION_RECORD.json` (11 questions, 1 fact +
10 decisions, `verify_interrogation.py` exit 0, signed off by the human).

## What changed since v1, and why the contract had to be rewritten rather than extended

v1 was written against the epic's **filed** shape: one defect family, five work packages, four waves.
Waves 1–2 measured a different shape. The three changes that force a new contract:

1. **Three defect families, not one.** **A** = the check that cannot fail (vacuous; no re-run
   helps). **B** = evidence true when taken, false when relied on (fails correctly when re-pointed at
   live state). **C** = the instrument measures a different thing than the code does (fails loudly
   and correctly, against the wrong quantity). A's remedy does not fix C, and neither does B's.
2. **The wave plan is re-cut by family, not by work package.** WP5 dissolved: it was grouped by
   *subject* (reviewers) and its members land across A, B, both, and neither.
3. **The epic ends at wave 3.** v1's wave 4 is cancelled; the remainder is re-filed against the
   three-family model.

## Epic Intent (unchanged in substance, sharpened by measurement)

Make a green qualitative gate mean something — **by telling the agent what would count, not by
telling it that it got it wrong**. Work comes off the agent's plate; refusability is the side effect
rather than the product.

**The outcome that must not be violated, restated with teeth after wave 2:** this epic must not add
machinery that is itself unwired — *and must not add machinery at all where the hole is that an
existing mechanism is untrusted.* Lane 3 is the case in point: the defence against a PR that reds
main already exists, already runs on the merge ref, and already went red on #645. It was ignored
because CI is red on 100% of runs. The fix is to restore the signal, not to build a second one.

## Success Shape for wave 3

- ~31 of the 65 qualitative conditions become **real checks**, using check kinds that already exist.
- A red-proof, suite run, or review result **carries the basis it was taken against**, and drift
  makes it **fail** rather than skip.
- A red CI **means something**: at least one platform whose red is signal rather than noise.
- A crew dispatched without `--spine` **cannot** drive its dispatcher's spine.

**Honest null remains a complete deliverable.** If the promotion lane finds that the other templates
partition materially differently from `COMMANDER_SPINE`'s measured 9/19, saying so and promoting
fewer is a successful wave, not a failed one — and it is a **material exception** that triggers
replan rather than being absorbed silently.

## Checkpoint Protocol

**Cleared autonomous through wave 3, including merges. Present the epic summary at closeout for
acceptance.** Human ruling, this contract.

Surfaced decision classes still escalate mid-wave. What reaches the user: plain English, the decision
asks, measured numbers with what was measured named, evidence on demand.

## Wave 3 — four lanes, then the epic closes

| Lane | Family | Work |
|---|---|---|
| **`w3-promote`** | **A** | Promote bucket-2 qualitative conditions to real check kinds. ~9/19 measured in `COMMANDER_SPINE.template.json`, extrapolating to ~31 of 65. **No new mechanism** — the check kinds already exist. Highest-yield work identified in the interrogation. |
| **`w3-basis`** | **B** | Evidence carries the basis it was taken against; **fail-on-drift replaces skip-on-drift**. Re-pin `CommanderSpineBasisFields` to the template's **blob OID** (not repo `HEAD`) and make drift FAIL. Spec'd verbatim by #381. Must ship the **re-verify path alongside the guard**. |
| **`w3-ci`** | **C** | Add an `ubuntu-latest` job to `.github/workflows/ci.yml`. Leave `windows-latest` in place and red. Restores the merge-ref signal that already exists. |
| **`w3-door`** | plumbing | `scripts/run_crew.py` `_crew_door_env` **clears** `SPINE_FILE`/`SPINE_SESSION` on `spine=None` instead of inheriting the dispatcher's pair. Docstrings at `run_crew.py:1280`/`:1333-1341` must be edited too. |

**Deferred to a successor epic, filed against the three-family model:** all of family C's issues
(#524, #459), the engine-change B issues (#390, #515), residual A (#518, #382), #221's provenance
tag, and the dissolved WP5 remainder (#375, #358, #363, #223, #388, #376). **Family C gets zero
wave-3 coverage beyond `w3-ci`, and the epic summary must say so explicitly.**

## Decision Classes (carried from v1; two rows changed)

| Class | Disposition |
|---|---|
| Architecture / structural change | **surfaced** |
| Scope change (issue added/dropped/re-scoped) | **delegated** |
| Merge to main | **delegated** |
| Issue **closing** | **delegated** |
| Issue **filing** | **delegated for the closeout re-file only** *(changed — see pre-ruling)*; otherwise **surfaced** |
| Fix-now triage (bounded fix applied immediately, not filed) | **delegated** |
| Spend / budget / model tier | **delegated** |
| Production defaults / user-visible behavior | **surfaced** |
| Making a new check blocking rather than report-only | **surfaced** *(unchanged — q6 explicitly declined to pre-clear this)* |
| CI workflow changes beyond the cleared `ubuntu-latest` job | **surfaced** *(new)* |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated for this epic's own subject matter. Every apply is
  logged as a RULING. Constellation lessons are always exported, never silently confirmed.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Fix-now triage, scope change | Edit `skills/*/templates/*.json` | **Pre-cleared, carried from v1.** Compact-format JSON edited as raw text, never round-tripped through `json.load`/`json.dump`; re-validated with `json.load` after. |
| Apply a lesson / fold doctrine | Edit `skills/_shared/global-*.md` | **Pre-cleared, carried from v1.** Cite `skills/_shared/global-*.md`, never `skills/<role>/references/global-*.md` (install-time copy, silently overwritten). |
| `w3-ci` | Edit `.github/workflows/ci.yml` | **Pre-cleared, this contract** — adding one `ubuntu-latest` job. Anything further is surfaced. |
| `w3-door` | Edit `scripts/run_crew.py`, the launcher the lane is itself dispatched through | **Pre-cleared, this contract.** Must be verified against a **real dispatched child**, not only a unit test of the env dict. |
| Merge to main | `gh pr merge`, `git push` | Fallback if the classifier vetoes: one human approval in the moment, remaining merges batched. |
| Issue closing / closeout re-filing | `gh issue close`, `gh issue create`, `gh issue comment` | **Pre-cleared, this contract**, for the closeout dispositions named above. |

## Float-Up Routing

Unchanged from v1. Adjudicate delegated classes and log a RULING; escalate surfaced and
out-of-taxonomy. Answer a Commander's **context query** from epic knowledge and continue it.

**New for wave 3 (`decision:poll-for-refresh-requested`):** the Admiral's monitor **must** poll each
lane's `current` for the `REFRESH REQUESTED:` line and **actually relaunch** a fresh commander into
the same worktree and spine file when it appears. Wave 2 raised 8 and answered 0.

## Budget / Model Parameters

**Sonnet for every commander and crew slot.** Human ruling, re-confirmed at this refresh: *"still
sonnet."* The reasoning from v1 stands and has now been tested: wave 2's three sonnet lanes merged
3-for-3, and `w2-basis` — the strongest artifact of the epic — independently invented the
fail-on-drift instinct that `w3-basis` now generalises. The compensating investment remains
**launch-order specificity, not model tier**.

**`decision:double-block-escalation` carries forward:** a commander returning blocked **twice on the
same obstacle** is re-dispatched at opus. Bounded, named, logged, and itself evidence about where the
launch order was underspecified.

## Pre-Rulings

- `decision:three-family-model` — the epic closes on A / B / C. A launch order must name which family
  its lane serves, and **must not let a lane collapse family B's evidence-basis work into the
  qualitative-condition population** — different populations, and 2-of-19 is a verdict on the
  backfill, not on the mechanism. `@grade: settled/human · leans wave-3`
- `decision:no-basis-backfill` — the `basis` field is **not** rolled out across the 65. Measured:
  8/19 can express no locator, 9/19 need no new mechanism, 2/19 gain. Shipping a field to ~65
  conditions to help ~7 is machinery for machinery's sake. `@grade: settled/human · leans wave-3`
- `decision:65-discharged-by-extrapolation` — no separate evaluate-the-65 mission runs. **Knowingly
  accepted risk:** all 19 came from one template, so the extrapolation is itself a family-B shape.
  `w3-promote` **must record, per condition it promotes, whether that condition's template matched
  the predicted partition**, and a material divergence triggers replan. `@grade: settled/human`
- `decision:558-closes-on-measurement` — #558 is closed with the measurement posted on it. Its
  executor/reviewer/invoker cut survives as one line of prose; the human-terminates line, the derived
  `n`, and the invoker-signs gate do not. `@grade: settled/human`
- `decision:fix-the-instrument-not-the-check` — **new, and the sharpest thing wave 2 taught.** Before
  building a guard, check whether one already exists and is merely untrusted. CI already tested the
  merge ref, already went red on #645, and was ignored because it is red on 100% of runs. A check
  that always fails carries exactly as much information as one that cannot fail.
  `@grade: settled/human · leans all-lanes`
- `decision:report-only-is-staging-not-posture` — carried from v1 **and now confirmed by the human**
  at q6, which was v1's named settle-point. Every report-only check must name its promotion trigger
  in the same PR that ships it. Where the adjudication is available at authoring time, ship it
  blocking and say so. `@grade: settled/human`
- `decision:prefer-fix-or-episode-over-filing` — carried from v1 unchanged, with the closeout
  re-filing as its one pre-cleared exception. `@grade: settled/human`
- `decision:poll-for-refresh-requested` — see Float-Up Routing. Wave 3 also **pre-declares** the
  comparison against wave 2's over-band lanes: per lane, record refresh-request count, whether a
  relaunch actually happened, `attempt`/`total_rework`, reviewer verdict and round count, and whether
  verify-before-merge caught anything the lane missed. Without pre-declaration the read is a post-hoc
  story — and per family C, an instrument that cannot distinguish the two worlds certifies nothing.
  `@grade: settled/human · leans wave-3`

## Expiry

**Event: wave 3's merges complete.** Crossing it forces a contract decision before anything further
dispatches — and since wave 3 is the last wave, the expected next step is closeout, not a refresh.
Also refreshes early if `w3-promote` measures a partition materially different from 9/19, since that
invalidates `decision:65-discharged-by-extrapolation`.

## Confirmation

`2026-08-22` — confirmed by Tommy: *"still sonnet, you got the latitude, let me know what else I can
clear up"*, plus explicit rulings this session on the lane-3 shape (add a Linux job, leave Windows
red) and the checkpoint protocol (autonomous through merge, present at closeout).
