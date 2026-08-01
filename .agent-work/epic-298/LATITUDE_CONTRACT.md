# Latitude Contract: `epic-298`

**CONFIRMED by Tommy, 2026-07-31.** The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent

One closed vertical slice proving Constellation skills can natively enter, consume, and improve a
shared, observable knowledge substrate. Deliverables: the reworked one-framework lessons system
(**B1**) and the Commander map-first tracer (**B3**), under the B0 principles (stochastic boundary,
collate-before-reacting, two-bin rule, consequence-scaled review). The **B2 kernel-plus-fragments
break is CONDITIONAL** — decided at issue L (#310) on evidence gates, never assumed. B4 is not in
this cut. **Tommy is the standing adjudicator of every pathway verdict.**

Outcome that must not be violated: nothing stochastic lands directly in canon; every pathway verdict
is Tommy's; the near-term work must not foreclose the idea-substrate half (Stratum A).

## Success Shape

All 12 issues (#299–#310) dispositioned. Each testing pathway exercised at least once with its
evidence paired for Tommy's verdict. **Honest nulls are complete deliverables** — per the spec, "if
deletion alone suffices, the break is not taken — that outcome is success, not failure."
Falsification of a pathway triggers rework of that element, never silent continuation and never
project abandonment.

## Checkpoint Protocol

Stop-and-present at every wave boundary; run ahead freely between boundaries. What reaches Tommy:
plain-English summary, decision asks, changed reads of the epic; evidence on demand.

**HITL issues** (A #299, D #302, I #307, J #308, L #310): agents assemble the evidence/candidates;
Tommy makes the call live in this session. A and D open wave 0 with Tommy at the keyboard.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | delegated *(surfaced if it changes a load-bearing interface shape — episode record, projection manifest — outside the design-it-twice convergence Tommy already owns)* |
| Scope change (issue added/dropped/re-scoped) | **surfaced** |
| Merge to main | delegated *(green + reviewed only)* |
| Issue filing / closing | delegated *(commanders file findings to the tracker directly, never bank worktree-locally)* |
| Fix-now triage (bounded fix applied immediately) | delegated |
| Spend / budget / model tier | delegated *(within the table below)* |
| Production defaults / user-visible behavior | **surfaced** |
| **Two-bin routing rulings & pathway verdicts** | **surfaced — always** (Tommy is standing adjudicator; spec B0.3/B0.4) |
| **Design-it-twice convergence** (episode record, projection manifest) | **surfaced — always** (convergence is human-only) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated; logged as RULINGs in ADMIRAL_LOG; constellation
  lessons always exported, never silently confirmed.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Issue filing / closing | `gh issue create`, `gh issue comment`, `gh issue close` | **pre-cleared** (grounded: #145 + 3× recurrence of the gh-issue-create gap) |
| Merge to main | `gh pr create`, `gh pr checks`, `gh pr merge` | **pre-cleared** for green+reviewed; fallback: one human approval in the moment, rest batched to next checkpoint |
| Fix-now triage | full test suite (`py -m pytest`), `git push` to `epic-298/*` branches | **pre-cleared** |
| Measurement missions (I #307, K #309, G #305 negative control) | running the eval harness / representative Commander runs; **corpus surgery** — seeding known defects into a bounded corpus slice (K), inducing entrypoint/drift failures (B3 pathway) | **pre-cleared** — seeded/induced defects are reverted by the same issue that seeds them |
| Spend / model tier | dispatching subagents at the tiers below | **pre-cleared** |

## Float-Up Routing

Commander floats a **decision**: adjudicate inside delegated classes, log a RULING; escalate
surfaced classes and out-of-taxonomy. Commander floats a **context query**: answer from epic
knowledge and continue it. Per-class nuance: any two-bin routing question and any pathway-verdict
question goes to Tommy, always — that adjudication is the epic's spine.

## Comms

Plain English by default; technical depth on demand. No invented project dialect in anything
user-facing. Decision asks in plain text, never question dialogs.

## Budget / Model Parameters

| Issue | Dispatch | Tier |
|---|---|---|
| A #299 corpus + baselines | Tommy live + dispatched baseline runs | — |
| B #300 projection generator | full Commander (design-it-twice, cold panel) | Opus |
| C #301 episode record + store | full Commander (design-it-twice, cold panel) | Opus |
| D #302 invariant inventory | agent compiles candidates, Tommy adjudicates | Sonnet prep |
| E #303 confirm-gate refusal | implementer-with-plan | Sonnet |
| F #304 map-input contract | full Commander (cold panel) | Opus |
| G #305 episode capture | full Commander (cold panel) | Opus |
| H #306 drift check | full Commander (cold panel) | Opus |
| K #309 coherence sweep | Commander | Sonnet |
| I #307, J #308, L #310 | evidence by agents, verdicts Tommy's; tier set at their wave boundary | — |

No Fable subagents — every dispatch capped at Opus or lower, explicit model on every Agent call.
**Usage-limit budget**: at most 3 concurrent Commanders; if a limit reset is near, defer the next
wave's dispatch past the reset rather than launching into it.

## Pre-Rulings

Each overridable by Tommy at any checkpoint.

- decision:baselines-before-f-merge — A's baseline runs are captured before F's map-input contract
  change merges; the comparison arm for the B3 verdict must be pre-change.
  `@grade: settled/human · leans wave-0,#304,#307`
- decision:review-class-floor — B, C, F, G, H get the full cold-panel agentic review; a Commander
  may not downgrade to a light pass on them.
  `@grade: settled/inherited · leans wave-0,wave-1` (from spec B0.4)
- decision:design-it-twice-in-issue — B and C each run design-it-twice on their load-bearing
  interface (projection manifest, episode record); convergence surfaced to Tommy.
  `@grade: settled/inherited · leans #300,#301` (from spec, load-bearing interfaces section)
- decision:markdown-in-git — storage stays Markdown in git; no database, no query language.
  `@grade: settled/human · leans #300,#301` (Tommy's direction in the spec)
- decision:lessons-inbox-keeps-running — the existing LESSONS.md machinery stays operative for this
  epic's own runs; migration to the new episode store is settled at J (#308), not assumed by C.
  `@grade: guess · leans #301,#308 · settle: at J, run one consolidation on the new store and rule on cutover`

## Expiry

**End of wave 1**, or the first time a two-bin ruling or pathway verdict is actually due —
whichever is first. Crossing it forces a contract refresh (waves 2–3 are HITL-heavy and deserve a
fresh look at the evidence then).

## Confirmation

**Confirmed by Tommy, 2026-07-31** — verbatim: *"confirmed as reco"*. All five decision asks
(checkpoint protocol + HITL shape, decision classes, permission pre-clearances, tiers and wave
sizing, pre-rulings and expiry) adopted as recommended, with no amendments.

Interrogation record: `.agent-work/epic-298/INTERROGATION_RECORD.json`
(`verify_interrogation.py` exit 0; survey consolidated RESOLVED).

---

## Renewal — after wave 0 (Tommy, 2026-08-01)

The expiry fired as written: its second trigger was *"the first time a two-bin ruling or pathway
verdict is actually due"*, and the #302 escalation **is** a two-bin ruling. Presented with the four
outstanding decisions; Tommy ruled all four and said **"good to renew."**

### Rulings folded in as pre-rulings

- decision:manifest-lives-in-agent-work — the projection manifest lives under `.agent-work/`; **no
  separate committed per-role artifact**. Standing: a nice-to-have record, not a load-bearing diff
  surface. *"we shouldn't need to keep it but if it's available it's good to have."*
  `@grade: settled/human · leans #300,#306`
- decision:retirement-moves-the-file — a retired episode's file **moves**; files stay clean of
  history unless they are themselves historical, and archives are a legitimate separate strategy.
  `@grade: settled/human · leans #301,#308`
- decision:corpus-is-f1brainz — f1Brainz is the dogfood corpus.
  `@grade: settled/human · leans #299,#307`
- decision:baseline-task-set — Tommy delegated the task choice ("just pick up your favorite issue.
  I dont know them off hand"). Picked, all verified OPEN and unassigned on 2026-08-01:
  **#710** (repoint stale forward-refs across `segment_map/{store,identity,derivation/derive}.py`
  — multi-file inside one module family; a component boundary should beat a repo-wide grep),
  **#715** (export `instrument_panel_668_report` private helpers rather than duplicating them into
  `run_season_panel_670` — the purest "which boundary owns this" question, and the strongest single
  test), **#698** (store-API primitive-obsession — **scored on seam-finding only**, ignoring its
  packaging/hygiene sub-concerns, which are noise for this measurement), and **#704 as a deliberate
  NEGATIVE CONTROL** (single file, function-level, locatable by filename alone — a map should *not*
  help here, and if map-first "helps" on it too, the measurement is reading something other than
  map value). Rejected: **#696** (roadmap issue, epic-sized, wrong grain) and **#717** (rethink an
  observable — design work, not seam-finding).
  `@grade: settled/human · leans #299,#307 · settle: if the control shows the same lift as the real tests, the instrument is measuring something else and the task set needs re-cutting`
- decision:no-third-bin — **Assumption 6 stands; B0.3 is unchanged.** Both third-bin candidates are
  **aspirations, not catastrophic-class**. *"machinize the mechanizable. we don't need stochastic
  reasoning for predictable logic."* Note the precise shape: the human-authorization gap was not
  ruled *mechanizable*, it was ruled **not catastrophic**, on observed agent behaviour — it stays
  as prose and simply does not earn a bin of its own.
  `@grade: settled/human · leans #302,#304,B0.3`

### Communication — corrected, and this one is on me

State the **question** in plain terms first, then real **options** with honest costs, then a lean
if I have one. A recommendation is worthless to someone who has not been told what is being
decided. Epic-internal shorthand belongs in the ADMIRAL_LOG and agent-to-agent messages — which is
what those artifacts are *for* — and never in a decision ask. Grounded: I presented all five
decisions in co-invented dialect and cost a full round-trip.

### What carries forward unamended

Checkpoint protocol, decision classes, float-up routing, honest-null acceptability, model tiers and
the concurrent-commander cap, and the remaining original pre-rulings (`baselines-before-f-merge`,
`review-class-floor`, `design-it-twice-in-issue`, `markdown-in-git`, `lessons-inbox-keeps-running`).

### Open clarification, surfaced not assumed

Tommy's manifest ruling assumes `.agent-work/` is usually kept in git. **In this repo it is
gitignored (`.gitignore:1`, zero tracked files).** So as ruled, the manifest yields no reviewable
diff and #306's drift check has no committed comparison target. Put back to him; **not** resolved
by inference.

### New expiry

**End of wave 1**, or a ruling that would change B0.3 or the corpus choice — whichever is first.

### Permission delta

f1Brainz (`C:/Programs/f1Brainz`) is a **different repository** than the pre-cleared set. Baseline
runs there need read access plus an isolated worktree/branch that is never merged; `gh` operations
against `fredcai6/f1Brainz` are **not** yet pre-cleared and are surfaced on first need.
