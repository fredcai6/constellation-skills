# Delegated/Autonomous Commander Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Commander runnable autonomously under an Admiral (checkpoints satisfied by citing the frozen launch order; context reachable via the Admiral), fix three commander-spine papercuts, all as documented readings of the existing spine — zero engine code.

**Architecture:** Pure doctrine/template edits across the Commander, Interrogator, Admiral, and Reviewer skills plus the spine/contract templates. The engine already accepts the evidence and attestations these readings need, so nothing in `scripts/` changes. Decomposed by **file ownership**: each task owns a disjoint set of files.

**Tech Stack:** Markdown skill/reference docs; JSON `.template.json` files (validated with `py -c "import json; json.load(...)"`); `unittest` suite run via `py -m pytest` as the regression guard that template JSON still parses.

**Spec:** `docs/superpowers/specs/2026-06-27-delegated-autonomous-commander-design.md`

## Global Constraints

- **Documented-reading only.** No new engine fields, gate markers, or spine variants; **zero changes under `scripts/`**. Every fix is skill/template/doctrine text.
- **No stale absolute left unqualified** anywhere it appears: the Interrogator's "wait for the answer" (Task 1), the commander SKILL's "Each gate has three tasks" / "Never hand-launch a crew" (Task 1), the spine `compact` "Run /compact" (Task 1), and the fleet-doctrine "skip with reason" compact quirk bullet (Task 2).
- **Verify-from-artifacts judges the *verdict*, not liveness.** It must NOT weaken "confirm dead before you reuse/sweep the worktree" — idle ≠ dead for worktree reuse (Task 2).
- **Delegate is not a replacement.** Asking *up* is sanctioned at every tier; the chain terminates at the human. The Commander floats decisions / queries the Admiral for context (Task 1); the Admiral fields those and, when its own knowledge and latitude run out, reaches the human ("I need to talk to my human" is a first-class move) (Task 2).
- **`COMMANDER_SPINE.template.json` must remain valid JSON** after editing (it is `json.load`-ed by the suite).
- **Full suite stays green:** 222 passed / 1 skipped on this branch's base (forks from main, independent of the open #35 PR).
- **Only the named files change.** No engine, no test files, no other skills.

## Cross-Task Interfaces

- **Compact wording (Task 1 ↔ Task 2).** The spine `compact` step reframe (Task 1, `COMMANDER_SPINE.template.json`) and the fleet-doctrine "Engine/platform quirks" compact bullet (Task 2, `fleet-doctrine.md`) must describe the **same** conditional behavior: run a compaction command if the harness exposes one, else rely on auto-compaction; always reload the skill. Both exact texts are given below so they agree regardless of task order.
- **Back-channel language (Task 1 ↔ Task 2).** Task 1's commander "Delegated/autonomous mode" section describes the Commander *floating a decision* / *querying for context*; Task 2's admiral doctrine is the receiver. Both use the phrasing "float a decision / query for context."

---

### Task 1: Commander-side delegated/lean doctrine

**Files:**
- Modify: `skills/commander/SKILL.md` (add a "Delegated/autonomous mode" section after "Human checkpoints (rigor dial)"; qualify the "Executing a gate" section for reasoning gates)
- Modify: `skills/commander/templates/COMMANDER_SPINE.template.json` (delegated clause on the `understand`/`plan`/`triage`/`review` imperatives; reframe the `compact` step)
- Modify: `skills/interrogator/SKILL.md` (delegated-context clause)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces (referenced by Task 2's Admiral doctrine): the Commander, in delegated mode, **floats a decision** or **queries the Admiral for context** when the launch order leaves a genuine gap. Task 2 is the receiver of those.

- [ ] **Step 1: Add the "Delegated/autonomous mode" section to `skills/commander/SKILL.md`**

In `skills/commander/SKILL.md`, the "Human checkpoints (rigor dial)" section is currently:

```markdown
## Human checkpoints (rigor dial)

Pause for a `user-decision` at the checkpoints the project enables at Charter time — typically plan-approved, architecture-change intent, and final accept. Human verification is a first-class step.
```

Immediately **after** that section (before "## Decision candidates"), insert:

```markdown
## Delegated/autonomous mode

You may be run **autonomously under an Admiral** rather than driven by a human at the keyboard. Running from an Admiral `LAUNCH_ORDER` **is** the signal: the human is not directly reachable this run, the Admiral is the human's delegate, and the frozen launch order is the ratified scope. The spine is unchanged — you read it differently:

- **`understand`.** Reconcile the ask against the frozen launch order (Mission, Pre-Rulings, Inherited Context, Inherited Latitude) as the source of truth rather than interrogating a human. The loaded Interrogator carries its own delegated reading (see `constellation-interrogator`).
- **The four `user-decision` checkpoints** (`understand`, `plan`, `triage`, `review`) are satisfied by **attaching a `user-decision` evidence item that cites the governing launch-order section** — `<engine> attach <step> --type user-decision --field cite="LAUNCH_ORDER:<section>"` — with the Admiral as ratifying authority and the human ratifying at the epic return boundary. The engine only requires the `user-decision` artifact to be present; the citation rides in the payload for audit.
- **This is not a licence to guess.** When the launch order leaves a genuine gap, take it **up to the Admiral** — **float a decision** that exceeds your inherited latitude, or **query the Admiral for context** you lack (a clarification, an epic-level fact, a read on intent the pre-rulings do not settle). Surface the specific need in your return/stop shape; the Admiral answers and continues you. A delegate is not a replacement: asking up is always sanctioned, never a failure — the chain terminates at the human, and the Admiral reaches them when its own knowledge and latitude run out.

Interactive (human-at-the-keyboard) runs are unchanged: pause for the `user-decision` and ask the human directly.
```

- [ ] **Step 2: Qualify the "Executing a gate" section for reasoning gates in `skills/commander/SKILL.md`**

In `skills/commander/SKILL.md`, the "Executing a gate" section opens:

```markdown
## Executing a gate

Each gate in `execute.json` has three tasks in order:
```

Change that opening line to:

```markdown
## Executing a gate

Each **crew gate** in `execute.json` has three tasks in order (a *reasoning gate* has none — see "Crew gate vs reasoning gate" below):
```

Then, immediately **after** the `gN-integrate` paragraph (the one beginning "**`gN-integrate`** — Check the verdict.") and **before** the "Closeout checks" paragraph, insert:

```markdown
**Crew gate vs reasoning gate.** The three-task shape above is a *crew gate*: it produces code or an independently-verifiable change, and its implement/review tasks dispatch crews. A gate whose deliverable is a **document or diagnosis**, and whose context you already hold, may instead be authored as a **reasoning gate** — **no** `gN-implement`/`gN-review` crew tasks, driven in your own context, with the crew-waiver reason stated in the gate. Its closeout postcondition is an attested (`check: null`) or `user-decision` artifact rather than a crew `review-result`. A crew on a pure design note is *shallower*, not safer; reserve crews for gates that produce code or an independently-verifiable change.
```

Finally, the "Never hand-launch a crew" paragraph currently begins:

```markdown
**Never hand-launch a crew.** Every implementer/reviewer dispatch goes through `scripts/run_crew.py`, not a raw CLI call.
```

Change its first sentence to scope the absolute to *how* a crew is launched (a reasoning gate launches none):

```markdown
**Never hand-launch a crew.** When a gate dispatches a crew, that dispatch goes through `scripts/run_crew.py`, not a raw CLI call (a reasoning gate dispatches no crew, so this does not apply to it).
```

- [ ] **Step 3: Add the delegated clause to the four `user-decision` step imperatives in `COMMANDER_SPINE.template.json`**

In `skills/commander/templates/COMMANDER_SPINE.template.json`, append the following sentence to the end of the `imperative` string (just before the closing `"`) of each of these four steps. Match on the existing imperative text; append inside the same JSON string (no new keys, no double-quotes that would break JSON — use the single-quoted `cite='...'` form shown).

`understand` step imperative — append:

```
 In delegated mode (running from an Admiral launch order, no reachable human), reconcile the ask against the frozen launch order instead of interrogating a human, and satisfy c1 by attaching a user-decision evidence item citing the launch order (attach understand --type user-decision --field cite='LAUNCH_ORDER:Mission'); take a genuine gap to the Admiral — float a decision outside latitude, or query for missing context — per Stop Conditions. See the commander skill's Delegated/autonomous mode.
```

`plan` step imperative — append:

```
 In delegated mode, satisfy c3 (plan approved) by attaching a user-decision evidence item citing the launch order's frozen plan and scope (attach plan --type user-decision --field cite='LAUNCH_ORDER:Mission'); surface a plan-invalidating discovery to the Admiral rather than blocking on the human. See the commander skill's Delegated/autonomous mode.
```

`triage` step imperative — append:

```
 In delegated mode, satisfy c2 (user approved issue creation) by attaching a user-decision evidence item citing the launch order's issue-filing authority (attach triage --type user-decision --field cite='LAUNCH_ORDER:Inherited Latitude'), or float to the Admiral when filing falls outside inherited latitude. See the commander skill's Delegated/autonomous mode.
```

`review` step imperative — append:

```
 In delegated mode, satisfy c1 (run summary accepted) by attaching a user-decision evidence item citing the launch order (attach review --type user-decision --field cite='LAUNCH_ORDER:Return Shape'); the Admiral ratifies at the epic return boundary. See the commander skill's Delegated/autonomous mode.
```

- [ ] **Step 4: Reframe the `compact` step in `COMMANDER_SPINE.template.json`**

In the same file, the `compact` step is currently:

```json
    "compact": {
      "id": "compact",
      "title": "Compact context and reload skills",
      "imperative": "Run /compact to compress conversation context. Then reload the constellation-commander skill into this context. Confirm it is active before proceeding to execute.",
      "preconditions": [{"id": "p1", "statement": "plan approved", "check": null, "satisfied": false}],
      "postconditions": [
        {"id": "c1", "statement": "context compacted", "check": null, "satisfied": false},
        {"id": "c2", "statement": "commander skill reloaded in this context", "check": null, "satisfied": false}
      ],
```

Change the `imperative` and the `c1` `statement` (leave ids, checks, and structure unchanged):

```json
    "compact": {
      "id": "compact",
      "title": "Ensure context headroom and reload skills",
      "imperative": "Ensure context headroom for the execute phase: if your harness exposes a compaction command (e.g. /compact), run it; otherwise rely on harness auto-compaction — either is fine. Then ALWAYS reload the constellation-commander skill into this context and confirm it is active before proceeding to execute. The skill-reload is mandatory regardless of whether a compaction command was available; the compaction itself is best-effort.",
      "preconditions": [{"id": "p1", "statement": "plan approved", "check": null, "satisfied": false}],
      "postconditions": [
        {"id": "c1", "statement": "context headroom ensured (compaction run if available, else auto-compaction relied on)", "check": null, "satisfied": false},
        {"id": "c2", "statement": "commander skill reloaded in this context", "check": null, "satisfied": false}
      ],
```

- [ ] **Step 5: Add the delegated-context clause to `skills/interrogator/SKILL.md`**

In `skills/interrogator/SKILL.md`, the paragraph at line 14 ends "...If a question can be answered from the code, explore the code instead of asking." Immediately **after** that paragraph (before "**FOLLOW THIS SKILL STRICTLY...**"), insert:

```markdown
**Delegated context (no reachable human).** When you are driven without a reachable human — a Commander running under an Admiral launch order, or any delegated dispatch — your "user" is the **frozen launch order / the dispatching delegate**. Answer each question from it, and `skip` questions it already settles. When the source does not answer and you cannot safely proceed, **take it to the delegate** rather than waiting on a human: a missing fact as a **context query**, a choice outside inherited latitude as a **float**. ("Wait for the answer" above is the interactive reading; in delegated mode the answer comes from the launch order or the delegate, never from blocking on an absent human.) The Admiral's own `latitude` interrogation, where the human *is* reachable, is unchanged.
```

- [ ] **Step 6: Validate JSON and run the consistency checks**

Run: `py -c "import json; json.load(open(r'skills/commander/templates/COMMANDER_SPINE.template.json', encoding='utf-8')); print('OK')"`
Expected: `OK` (valid JSON after the imperative/compact edits).

Run: `py -m pytest -q`
Expected: 222 passed, 1 skipped (no code changed; this confirms the spine JSON still loads in the template tests).

Then confirm no stale absolute remains in the edited files:

```bash
git grep -n "wait for the answer" -- skills/interrogator/SKILL.md   # must now sit beside the delegated clause, not unqualified
git grep -n "Each gate in" -- skills/commander/SKILL.md              # must now read "Each crew gate in"
git grep -n "Run /compact" -- skills/commander/templates            # must be gone (reframed to conditional)
```
Expected: `Run /compact` returns nothing; the others show the qualified wording.

- [ ] **Step 7: Commit**

```bash
git add skills/commander/SKILL.md skills/commander/templates/COMMANDER_SPINE.template.json skills/interrogator/SKILL.md
git commit -m "docs: commander delegated/autonomous mode + reasoning gate + compact reframe (#34, #36)

Delegated-mode section (checkpoints satisfied by citing the frozen launch order;
float decisions / query the Admiral for context); 4 user-decision spine imperatives
gain the delegated clause; compact step reframed conditional (skill-reload stays
mandatory); reasoning-gate reading reconciles the 'three tasks' / 'Never hand-launch
a crew' absolutes; interrogator gains a delegated-context clause.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Admiral-side delegation + adjudication doctrine

**Files:**
- Modify: `skills/admiral/SKILL.md` (Execute doctrine: field Commander context queries; verify-from-artifacts on idle)
- Modify: `skills/admiral/templates/LATITUDE_CONTRACT.template.md` (Float-Up Routing broadened to decisions + context queries)
- Modify: `skills/admiral/templates/LAUNCH_ORDER.template.md` (Stop Conditions add the context-query reason)
- Modify: `skills/admiral/references/fleet-doctrine.md` (verify-from-artifacts invariant; update the compact quirk bullet)

**Interfaces:**
- Consumes from Task 1: the Commander floats a decision / queries for context — this task is the receiver.
- Produces: nothing other tasks consume.

- [ ] **Step 1: Add the back-channel + verify-from-artifacts bullets to `skills/admiral/SKILL.md`**

In `skills/admiral/SKILL.md`, the "Execute (free middle)" doctrine list ends with the bullet about a Commander that "dies or stalls":

```markdown
- A Commander that dies or stalls: inspect its worktree (commits, workbench state, orphan processes) before acting; relaunch a continuation into the same worktree resuming from its engine state — don't restart from zero. Log every incident and recovery.
```

Change that bullet to add the idle/verify-from-artifacts reading (keep the existing recovery guidance):

```markdown
- A Commander that dies or stalls: inspect its worktree (commits, workbench state, orphan processes) before acting; relaunch a continuation into the same worktree resuming from its engine state — don't restart from zero. Log every incident and recovery. An **idle** commander (`idle_notification`, `idleReason: available`) that has produced complete artifacts is *done*, not stalled: verify from the artifact set (branch/commit/PR/files) + a clean-room reviewer subagent and accept the work — never block waiting on a verdict message it may have dropped. This judges the verdict, not liveness: still confirm it dead before you reuse or sweep its worktree. See `references/fleet-doctrine.md`, "Adjudication invariants".
```

Immediately **after** that bullet, add a new bullet for the back-channel:

```markdown
- **Field your Commanders' queries — you are their reachable tier.** A delegated Commander cannot reach the human; it floats decisions and **queries you for context** it lacks (a clarification, an epic-level fact, a read on intent its launch order didn't settle). Answer from your epic-level knowledge, then **continue** the Commander. A delegate is not a replacement: when your own knowledge and granted latitude run out, **"I need to talk to my human" is a first-class move, not a failure** — reach the human out-of-band (the latitude contract's out-of-taxonomy / expiry escalation provides for exactly this) before continuing the Commander.
```

- [ ] **Step 2: Broaden Float-Up Routing in `skills/admiral/templates/LATITUDE_CONTRACT.template.md`**

In `skills/admiral/templates/LATITUDE_CONTRACT.template.md`, the "Float-Up Routing" section is currently:

```markdown
## Float-Up Routing
When a Commander returns a `user-decision`: adjudicate inside delegated classes and log a RULING; escalate surfaced classes and out-of-taxonomy to the human. `<any per-class nuance>`
```

Replace it with:

```markdown
## Float-Up Routing
When a Commander floats — a `user-decision` **or a context query**: for a decision, adjudicate inside delegated classes and log a RULING, escalate surfaced classes and out-of-taxonomy to the human. For a **context query** (the Commander needs a fact or clarification it lacks), answer from epic knowledge and continue it; reach the human out-of-band when the answer is beyond your knowledge or latitude — a delegate is not a replacement, so "I need to talk to my human" is always available. `<any per-class nuance>`
```

- [ ] **Step 3: Add the context-query Stop Condition to `skills/admiral/templates/LAUNCH_ORDER.template.md`**

In `skills/admiral/templates/LAUNCH_ORDER.template.md`, the "Stop Conditions" section is currently:

```markdown
## Stop Conditions
Stop and return when: `<conditions — scope exceeded, decision outside inherited latitude needed, budget crossed, evidence impossible>`
```

Replace the placeholder line to add the context-query reason:

```markdown
## Stop Conditions
Stop and return when: `<conditions — scope exceeded, decision outside inherited latitude needed, budget crossed, evidence impossible>`, or when you need **context the launch order does not cover and cannot safely proceed without** — return-and-query the Admiral (it answers and continues you). Asking up is always sanctioned.
```

- [ ] **Step 4: Add the verify-from-artifacts invariant to `skills/admiral/references/fleet-doctrine.md`**

In `skills/admiral/references/fleet-doctrine.md`, the "Adjudication invariants (Admiral errors that bit)" section is a bulleted list. Append this bullet to the **end** of that list (after the "Re-validate after any promotion" bullet, before the "## Engine/platform quirks" heading):

```markdown
- **Verify an idle commander from artifacts; never block on a dropped verdict.** An Agent-tool commander sometimes ends with only an `idle_notification` (`idleReason: available`) and never emits its verdict text, even with the work complete. Artifacts are ground truth; the verdict message is a convenience it can silently drop. When a dispatched commander returns idle with no verdict, **verify from the artifact set** (branch / commit / PR / changed files) and a **clean-room reviewer subagent** pointed at them, and accept the work on that basis — do not hang waiting for a message. This judges the **verdict**, not liveness: it does **not** weaken the sleeper-hazard rule — an idle/"completed" commander may still resurrect, so **confirm it dead before you reuse, sweep, or launch a continuation into its worktree**. "The verdict is in the artifacts" is not "the process is gone."
```

- [ ] **Step 5: Update the stale compact quirk bullet in `skills/admiral/references/fleet-doctrine.md`**

In the same file, the "Engine/platform quirks" section's first bullet is currently:

```markdown
- The spine `compact` step invokes a user-level CLI the agent cannot run — skip
  with reason; harness auto-compaction covers it.
```

Replace it to match the reframed step (Task 1, Step 4) — compaction is conditional, the skill-reload always runs:

```markdown
- The spine `compact` step no longer mandates `/compact`: run a harness compaction
  command if one is exposed, else rely on harness auto-compaction — either is fine —
  and **always reload the commander skill** (the load-bearing half). It is a
  conditional step now, not a permanent skip-with-reason.
```

- [ ] **Step 6: Run the suite and consistency checks**

Run: `py -m pytest -q`
Expected: 222 passed, 1 skipped (no code changed).

```bash
git grep -n "skip with reason" -- skills/admiral/references/fleet-doctrine.md   # the compact quirk bullet must no longer say this
git grep -n "context query" -- skills/admiral                                   # appears in admiral SKILL + LATITUDE_CONTRACT
```
Expected: `skip with reason` no longer present in the compact bullet; `context query` present in both admiral files.

- [ ] **Step 7: Commit**

```bash
git add skills/admiral/SKILL.md skills/admiral/templates/LATITUDE_CONTRACT.template.md skills/admiral/templates/LAUNCH_ORDER.template.md skills/admiral/references/fleet-doctrine.md
git commit -m "docs: Admiral fields Commander context queries; verify-from-artifacts on idle (#34, #36)

Admiral execute doctrine: an idle commander with complete artifacts is done (verify
from artifacts + clean-room, don't block on a dropped verdict; still confirm dead
before touching the worktree); field Commander context queries and reach the human
when own knowledge/latitude run out. LATITUDE_CONTRACT float-up routing + LAUNCH_ORDER
Stop Conditions broadened to context queries. fleet-doctrine: new verify-from-artifacts
invariant; compact quirk bullet updated to the conditional reading.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Crew survey-state location convention (36.3)

**Files:**
- Modify: `skills/commander/templates/REVIEWER_HANDOFF.template.md` (add a "Survey State Location" field)
- Modify: `skills/reviewer/SKILL.md` (state the survey checklist lives under the issue workbench)

**Interfaces:**
- Consumes / Produces: nothing — isolated convention fix.

- [ ] **Step 1: Add the "Survey State Location" field to `skills/commander/templates/REVIEWER_HANDOFF.template.md`**

In `skills/commander/templates/REVIEWER_HANDOFF.template.md`, the "## Gate" section is currently:

```markdown
## Gate
`<gate id from execute.json, e.g. g1>`
```

Immediately **after** the "## Gate" section, insert:

```markdown
## Survey State Location
Create your review survey checklist at `.agent-work/<work-id>/<gate>-review/review.json` — under the issue workbench, **never at the worktree root**. This keeps the survey state with the run's artifacts so closeout leaves no orphan untracked scratch.
```

- [ ] **Step 2: Add the survey-location clause to `skills/reviewer/SKILL.md`**

In `skills/reviewer/SKILL.md`, the paragraph at line 12 begins "Start from the given criteria in `templates/REVIEW_SURVEY.template.json`..." and ends "...then `consolidate` to a verdict." Append to the end of that paragraph (same paragraph, after "consolidate to a verdict."):

```markdown
 Create the survey checklist at the path the handoff gives ("Survey State Location": `.agent-work/<work-id>/<gate>-review/review.json`) — under the issue workbench, never at the worktree root, so closeout finds no orphan untracked scratch.
```

- [ ] **Step 3: Run the suite**

Run: `py -m pytest -q`
Expected: 222 passed, 1 skipped (no code changed; doc-only).

- [ ] **Step 4: Commit**

```bash
git add skills/commander/templates/REVIEWER_HANDOFF.template.md skills/reviewer/SKILL.md
git commit -m "docs: crew review survey-state lives under the issue workbench, not the worktree root (#36)

The Commander dictates the survey path in REVIEWER_HANDOFF
(.agent-work/<work-id>/<gate>-review/review.json); the reviewer SKILL states it
creates the survey there. Kills the orphan untracked scratch closeout had to hunt down.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- §A delegated mode (commander section + 4 user-decision clauses + interrogator) → Task 1 Steps 1, 3, 5. ✓
- §A Admiral back-channel (admiral SKILL + LATITUDE_CONTRACT + LAUNCH_ORDER) → Task 2 Steps 1, 2, 3. ✓
- §B verify-from-artifacts (fleet-doctrine + admiral SKILL) → Task 2 Steps 1, 4. ✓ (judges verdict not liveness, preserves confirm-dead — both in the text)
- §C compact (COMMANDER_SPINE step + fleet-doctrine quirk bullet) → Task 1 Step 4 + Task 2 Step 5; cross-task wording pinned in Cross-Task Interfaces. ✓
- §D reasoning gate (commander SKILL "Executing a gate", reconciling the two absolutes) → Task 1 Step 2. ✓
- §E survey-state (REVIEWER_HANDOFF + reviewer SKILL) → Task 3. ✓
- Delegate-not-replacement principle → Task 1 Step 1 (Commander asks up) + Task 2 Steps 1, 2 (Admiral asks up to human). ✓
- Zero engine code → no task touches `scripts/`. ✓

**2. Placeholder scan:** No TBD/TODO. The `<work-id>` / `<gate>` / `<section>` / `<conditions ...>` tokens are literal template placeholders quoted from the real files, not plan gaps.

**3. Type/identifier consistency:** The compact reframe text is identical in intent across Task 1 Step 4 (spine) and Task 2 Step 5 (fleet-doctrine bullet) — both say "compaction conditional, skill-reload always." The `user-decision` `attach --field cite='LAUNCH_ORDER:...'` form is consistent across all four Task 1 Step 3 clauses. "float a decision / query for context" is the same phrase in Task 1 (Commander) and Task 2 (Admiral). The survey path `.agent-work/<work-id>/<gate>-review/review.json` is identical in Task 3 Steps 1 and 2.
