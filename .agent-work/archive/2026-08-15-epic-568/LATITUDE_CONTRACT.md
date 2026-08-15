# Latitude Contract: `epic-568`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent

Every piece of engine state — lease, binding, gauge reading, refresh request, strike count —
carries who it belongs to and dies when its owner does. This run builds the **ownership
substrate** that the rest of epic 568 reads from: the lease actually protects the gates, the
binding store survives concurrency, and a postcondition check runs where the spine lives.

The outcome that must not be violated: **the engine must stay drivable throughout.** This epic
edits the machinery every Commander in it is driving. A change that leaves the fleet unable to
run its own spines is worse than the defect it fixed.

## Success Shape

Each in-scope issue closes on a **live repro that fails before the fix and passes after**.
Targeted automated tests plus the relevant broader suite ride alongside (per
`docs/agents/ORCHESTRATOR_CONTEXT.md`); they do not replace the repro.

A **measured negative is a complete, successful deliverable**: a defect that does not reproduce,
or a fix judged not worth its cost, closes with the measurement stated — not as a failure.
Scoped nulls apply — every verdict names what was tested **and what was not**.

### In scope (substrate + the near-mechanical wins)

| Package | Issues |
|---|---|
| WP1 lease lifecycle | #552, #383, #357, #369, #318, #330, #208 |
| WP2 binding store | #441 |
| WP5 postcondition cwd | #315 |
| Near-mechanical, no substrate needed | #530, #510 |

**Deferred** to a follow-on with the substrate under it: WP3 stop-rail attribution beyond #530,
WP4 gauge/governor beyond #510, WP6 crew dispatch/liveness, WP7 pre-clearance and CLI hardening.

### Execution shape — two lanes

- **Serialized engine-core lane.** Any change touching `scripts/checklist_engine.py`,
  `scripts/hooks/spine_rail.py`, or `scripts/agent_work_root.py` runs **one Commander at a time**,
  with no concurrent Commander editing those three files.
- **Parallel lane.** Backfill scripts, the reaper, doctrine and advisory text, template edits —
  fan out around the serialized lane.

**Wave 1 is #315**, ahead of all other engine-core work: thread `cwd=` into
`_run_check_command` (`checklist_engine.py:775-799`, which today calls `subprocess.run` with no
`cwd=` at all) and repair the relative-check fallout across every shipped spine template. Fixing
it later would mean everything before it was verified under a check that cannot fail. Wave 1 must
**enumerate that blast radius by command and state the count** — never from memory.

## Checkpoint Protocol

**Stop-and-present at every wave boundary.** No wave is pre-cleared to run through. At each
boundary I present: what merged, what the evidence showed, what the next wave proposes. The human
clears the next launch.

What reaches the human: a plain-English summary, the decision asks, and evidence on demand.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced |
| Scope change (issue added / dropped / re-scoped) | surfaced |
| Merge to main | **delegated** |
| Issue filing / closing | delegated |
| Fix-now triage (bounded fix applied immediately, not filed) | delegated, except inside the three engine-core files → surfaced |
| Spend / budget / model tier | delegated within the envelope below |
| Production defaults / user-visible behavior | surfaced |
| **Editing an engine-core file outside the serialized lane's current issue** | surfaced |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — **surfaced** (the template default). Constellation lessons
  are always exported, never silently confirmed. Note the standing repo rule: an episode is a
  record, never a rule; promoting anything into `docs/agents/*` is the human's call.

**Merge to main is delegated** as an explicit pre-approval under the `ORCHESTRATOR_CONTEXT.md`
carve-out ("unless the human has pre-approved the action for the specified work"). Every merge is
logged as a `MERGE` entry and visible at the next checkpoint.

**Merge gate — amended 2026-08-12 by the human.** The original term was "a green check exit code
plus an independent reviewer APPROVE". That is unsatisfiable: `main`'s CI is red from pre-existing
Windows breakage (handoff W8, #555), so no PR in this repo can reach a green exit code. The human
ruled: *"okay with the independent red, we should be green except for the existing reds."*

The gate is now **no-new-failures against the `main` baseline**, plus an independent reviewer
APPROVE. Concretely, before each merge I must:

1. Fetch the failing-test set for the PR's own CI run.
2. Fetch the failing-test set for the latest `main` run.
3. Diff them. **Any test failing on the PR and not on `main` refuses the merge.**
4. State both counts and the diff in the `MERGE` log entry.

This replaces the exit-code gate for as long as `main` is red; it does not loosen the reviewer
requirement, and it is not "the checks look close enough" — it is a set difference that must be
empty. When `main` goes green, the original exit-code gate resumes and this amendment lapses.

## Permission prerequisites

The allowlist in `.claude/settings.local.json` currently holds only `Bash(gh issue *)` and two
python one-liners. Delegated merge authority would therefore be vetoed at the first ready PR —
#408 and #145 recurring on this epic's own Admiral, before wave 1.

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr create`, `gh pr view`, `gh pr checks`, `gh pr merge`, `git push` | **Pre-clear before wave 1** — entries drafted and shown to the human before they are written |
| Issue filing / closing | `gh issue create/close/comment` | Already allowlisted (`Bash(gh issue *)`) |
| Repo hygiene at closeout | `git branch -d`, `git branch -D`, `git worktree remove/prune` | **Pre-clear before wave 1** — `git branch -D` was refused in the post-418 run (handoff U3) |
| Spend / model tier | subagent dispatch | No external action |

**Recorded fallback for anything still vetoed:** one live human approval in the moment, remaining
equivalent actions batched to the next checkpoint rather than re-litigated one at a time. Logged
as an `ESCALATION`.

## Latitude widened while the human is away — 2026-08-13

The human went AFK mid-wave with: *"you can keep pushing through wave 1. you may follow reasonably
sized judgement calls. try to get through this."*

For the remainder of wave 1 this widens the delegated set: I may adjudicate **bounded structural
changes that serve an already-ruled direction** without surfacing — for example retiring a guard
that a ruled deletion makes incoherent — and log them as `RULING`s.

It does **not** widen to: changing the epic's direction or intent, adding or dropping a member
issue, changing production defaults or user-visible behavior, or anything out-of-taxonomy. Those
still wait. "Reasonably sized" is read as: reversible, inside wave 1's stated objective, and
explainable in one paragraph at the checkpoint. Anything I would struggle to justify in that
paragraph gets parked for the human rather than decided.

The stop-and-present checkpoint at the wave boundary still stands — this widens what I may decide
*within* the wave, not whether the human sees the boundary.

## Float-Up Routing

When a Commander floats a **decision**: adjudicate inside delegated classes and log a `RULING`;
escalate surfaced classes and out-of-taxonomy to the human. When a Commander floats a **context
query** (a fact or clarification its launch order did not settle): answer from epic knowledge and
**continue** it; reach the human out-of-band when the answer is beyond my knowledge or latitude.

A Commander that files a `refresh-request` and goes idle is neither a query nor a death: relaunch
a fresh Commander into the **same worktree and spine file**, cold-started from its `current` alone.

## Comms

Plain English by default, technical depth on demand.

## Budget / Model Parameters

- **Engine-core lane:** one Commander at a time, **Opus**.
- **Parallel lane:** up to **3–4 concurrent** Commanders, **Sonnet** by default, escalating to
  Opus per issue where complexity, ambiguity, or risk demands it. The tier is recorded in each
  launch order's Budget slot.
- **Usage-limit budget.** The session pool is a wave-sizing input, not just a per-issue budget.
  When a limit reset is near, **defer the next wave's dispatch past the reset** rather than
  launching into it — a wave that trips the limit mid-flight strands its Commanders worse than one
  that waited.

## Pre-Rulings

- `decision:wave-1-is-315-alone` — wave 1 is #315 plus its template blast-radius repair, run by a
  single Commander, before any other engine-core work.
  `@grade: settled/human · leans wave-1`
- `decision:engine-core-serialized` — `checklist_engine.py`, `spine_rail.py` and
  `agent_work_root.py` are edited by one Commander at a time; concurrent edits to them are refused.
  `@grade: settled/human · leans wave-1,wave-2`
- `decision:repro-before-and-after` — an issue closes on a repro that fails before and passes
  after; a stated honest null is a complete deliverable.
  `@grade: settled/human · leans all-waves`
- `decision:merge-delegated-on-green-plus-approve` — I merge on a green check exit code plus an
  independent reviewer APPROVE, gating on the exit code.
  `@grade: settled/human · leans all-waves`
- `decision:552-denominator` — the backfill's target set is the **tracked** spines
  (`git ls-files '*spine.json'` → 91 carrying a session, 24 still active), and the issue's "43 on
  disk" figure is reconciled against that before any backfill runs.
  `@grade: guess · leans wave-2 · settle: scan both sets once and state each count with its denominator`
- `decision:door-unusable-this-session` — the `spine` MCP door is bound to a foreign scratch spine
  and `spine-epic` is dead, so this Admiral drives its spine through the engine CLI with an
  explicit `--session-id`.
  `@grade: settled/measured · leans all-waves`

Each pre-ruling is overridable by the human at any checkpoint.

## Expiry

**After wave 1 merges.** Wave 1 is the change most likely to reshape what the rest of the tranche
should look like, so the refresh happens as soon as it lands. No dispatch past that point without
a confirmed contract refresh.

**Refreshed 2026-08-12, before wave 1 merged.** The ground shifted early: wave 1's filed target was
falsified, the human set a new direction, and the merge gate proved unsatisfiable. Rather than sail
on a stale contract, two terms were re-confirmed with the human mid-wave — the merge gate above, and
the wave re-cut recorded as a `replan` transition. **The expiry itself is unchanged and still binds:
when wave 1 merges, the contract is refreshed again before any further dispatch.**

A note on what counts as "wave 1 merges": PR #576 carries only the regression guard, not the fix, so
merging it does **not** close wave 1 and does not trigger the expiry. Wave 1 closes when the re-cut
change — the engine-native cwd comparison plus the `origin` stamp — lands. Recorded here rather than
decided silently, because the reading affects when the next refresh is owed.

## Confirmation

`2026-08-12 — confirmed by the human ("Confirmed as written") after the full drafted contract was
presented, including the items not ruled on directly: the remainder of the decision-classes table,
the added engine-core-outside-lane class, float-up routing, comms, and the #552 denominator
pre-ruling graded as a guess. Interrogation record:
.agent-work/epic-568-latitude/INTERROGATION_RECORD.json (10 questions, verify exit 0).`

## Wave 2 refresh — confirmed 2026-08-14

The human cleared all retained lanes to start: lease lifecycle, binding-store durability, #530,
#510, and the near-term harness addition that carries model tier/reasoning into Codex dispatch in
the same durable way the harness already carries Claude tier.

### Execution and float boundary

- Planning, source measurement, and non-overlapping test design may fan out immediately.
- Implementation in `checklist_engine.py`, `spine_rail.py`, and `agent_work_root.py` remains
  strictly serialized. One engine-core implementation Commander owns the lane at a time.
- Lifecycle is the first engine-core implementation candidate. If measurement shows a materially
  larger migration, ambiguous release semantics, destructive backfill, or decomposition that
  cannot be justified in one bounded wave, it floats to the human before implementation continues.
- #441 and #530 both implicate `spine_rail.py`; they may be measured concurrently but may not be
  implemented concurrently. #510 follows the same serialized rule if it touches
  `checklist_engine.py`.
- The model-tier harness addition is a parallel lane provided it does not edit the three serialized
  engine-core files.

### Model routing

- Engine-core implementation and independent high-risk review: Claude Opus or
  `gpt-5.6-sol`, normally high/xhigh reasoning.
- Bounded implementation: Claude Sonnet or `gpt-5.6-terra`, normally medium/high reasoning.
- Mechanical inventories, baseline comparisons, and narrowly specified verification:
  Claude Haiku where available or `gpt-5.6-luna`, normally low/medium reasoning.
- Lower-tier work receives a bounded assignment and explicit evidence requirements. It does not
  adjudicate architecture, production behavior, or the final review of engine-core changes.

### Evidence and merge gate

Every issue still closes on a live repro that fails before and passes after, or an honest measured
null. Targeted tests and the relevant Linux suite must pass, and an independent reviewer must
APPROVE. GitHub CI may remain red only for Windows jobs: Windows failures are explicitly
non-blocking for this wave, but their counts and node-set delta are still recorded. Any non-Windows
CI failure or local Linux failure blocks merge. Merges remain delegated with exact-head pinning and
verified remote state.

### Expiry

This refresh expires when all five authorized wave-2 items are dispositioned, or immediately when
the lifecycle float boundary above fires. No consumer package beyond the listed work is authorized.

### Lifecycle float ruling — confirmed 2026-08-14

The human approved the Admiral's recommended package after the float:

- Explicit release remains mandatory; terminal advance does not auto-release.
- Claim/release become provable journaled lifecycle acts and release is idempotent.
- No historical bulk backfill. Classification/reporting comes first and does not mutate history.
- Child references become contained relative paths inside the parent work area, with a legacy
  filename compatibility path during migration.
- Archive refuses a resolvable nonterminal child.
- #383's remaining missing-binding cleanup moves under #441; #208 moves to a separate
  harvest-completeness package.
- Actor identity, PID-less liveness, and durable-root policy are later high-risk waves.
- Resume #530, #510, and Codex tier/worktree routing now. #441 follows #530 in the serialized
  `spine_rail.py` lane.
- The Codex harness may add an optional repo-local MCP worktree root while preserving the existing
  sibling-worktree default for Claude.

This ruling resolves the float but narrows the immediately active implementation wave to the three
bounded items. It expires when those three are dispositioned.
