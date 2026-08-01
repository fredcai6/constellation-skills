# Latitude Contract: `epic-267`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent

Make the Context Governor actually work. It is code-complete and operationally inert: the
measurement is correct (verified live 2026-07-27 — `claude-opus-5`, 89,481 tok → `0.089481`), but
nothing writes a gauge in any consuming project, and a session that did not personally run `claim`
never gauges at all.

The outcome that must not be violated: **a fail-safe must never become a silent failure.** Every
band in this system correctly declines to force on a missing reading — and that correctness is
exactly what let it be dead for weeks without anyone noticing. Fixes must preserve fail-safe
behavior while making silence visible.

## Success Shape

1. A gauge written and read in a consuming project that is **not** constellation-skills.
2. One real Trip on a correct reading that hands off to a successor which is **itself gauged**
   (today the successor would be blind — see the note under Pre-Rulings).
3. The #252 class — a well-formed but wrongly-scaled reading — is caught by something other than a
   human noticing the number looked odd.

**Honest nulls are complete deliverables.** #263 returning "Agent-tool subagents are measured
correctly, no defect" is a full success, not a failed issue. Per scoped-nulls doctrine, any null
must state what was tested and what was not.

## Checkpoint Protocol

**Stop-and-present at every wave boundary.** Between boundaries, run ahead without checking in.

What reaches the user at a checkpoint: a plain-English summary of what shipped and what it cost,
any decision asks, and anything that changed my read of the epic. Evidence on demand, not by
default.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | delegated *(surfaced if it changes the gauge record schema — it is frozen and shared with the reader)* |
| Scope change (issue added / dropped / re-scoped) | **surfaced** |
| Merge to main | delegated *(green + reviewed only)* |
| Issue filing / closing | delegated |
| Fix-now triage (bounded fix applied immediately) | delegated |
| Spend / budget / model tier | delegated |
| Production defaults / user-visible behavior | **surfaced** |
| **Governor threshold values** (soft/hard caps, any model row) | **surfaced — always** |
| **Anything writing to the user's `~/.claude/settings.json`** | **surfaced — always** |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated. Applies are logged as RULINGs in ADMIRAL_LOG;
  constellation lessons are always exported, never silently confirmed.

## Permission prerequisites

Pre-cleared now, because the auto-mode classifier vetoes exactly these mid-run and the veto only
surfaces after dispatch (grounded: #145, and a repeat noted in this repo's memory — commanders have
lacked `gh issue create` pre-clearance three times running).

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Issue filing / closing | `gh issue create`, `gh issue comment`, `gh issue close` | **pre-cleared** — commanders file findings to the tracker directly; never bank them worktree-locally for harvest |
| Merge to main | `gh pr create`, `gh pr checks`, `gh pr merge` | **pre-cleared** for green+reviewed. Fallback if vetoed: one human approval in the moment, remaining merges batched to the next wave checkpoint |
| Fix-now triage | full test suite (`py -m pytest`), `git push` to a `governor/*` branch | **pre-cleared** |
| Architecture / structural | editing `.claude/settings.local.json` **inside the commander's own worktree** for wiring tests | **pre-cleared** — worktree-local only. Editing `~/.claude/settings.json` is surfaced, always |
| Spend / model tier | dispatching subagents at the tiers named below | **pre-cleared** |

## Float-Up Routing

A Commander that floats a **decision**: adjudicate inside delegated classes and log a RULING;
escalate surfaced classes and out-of-taxonomy to the human. A Commander that floats a **context
query**: answer from epic knowledge and continue it — a return-and-relaunch round trip, not a
recovery drill. Reach the human out-of-band when the answer is beyond my knowledge or latitude.

Per-class nuance: a Commander proposing **any** threshold number, even as a test fixture, must
surface it rather than pick one. That is the decision this epic exists downstream of.

## Comms

Plain English by default; technical depth on demand. No invented project dialect in anything
user-facing.

## Budget / Model Parameters

| Issue | Dispatch | Tier |
|---|---|---|
| #261 bind-on-resume | implementer-with-plan | Sonnet |
| #262 install + opt-in wiring | full Commander (real design questions, installer surface) | Opus |
| #202 binding single-slot | fold into #261's commander — same file, same question | Sonnet |
| #263 subagent measurement | investigation, implementer-with-plan | Sonnet |
| #264 end-to-end assertion | full Commander | Opus |
| #265 visible non-reading | implementer-with-plan | Sonnet |
| #235 / #257 / #266 / #214 / #248 | tier set at their wave boundary | — |

**Usage-limit budget.** Treat the account session pool as a wave-sizing input. Wave 1 is at most
three concurrent commanders. If a limit reset is near, defer the next wave's dispatch past the
reset rather than launching into it — a wave that trips the limit mid-flight strands its Commanders
worse than one that waited.

## Pre-Rulings

Each overridable by the human at any checkpoint.

- decision:261-goes-first — #261 (bind on resume) ships and merges **before any other issue in this
  epic is dispatched**, alone. Reason: the Governor's own refresh path relaunches a fresh agent that
  runs `current`, not `claim`, so today a Trip hands off to a successor that is permanently blind.
  Until #261 lands, every downstream trip is self-defeating and this epic cannot supervise its own
  repair.
  `@grade: settled/human · leans wave-1`

- decision:thresholds-untouched — no soft/hard cap changes in this epic. The 80K/150K values stay as
  they are; `gauge_reader.py:64` lists four open measurement questions against them that cannot be
  answered until a corpus of correct readings exists — which is what this epic produces.
  `@grade: settled/human · leans wave-3,#266 · settle: follow-on epic, once real readings accumulate`

- decision:wiring-is-opt-in — the installer never silently rewrites a user's `settings.json`.
  Without an explicit flag it detects and reports.
  `@grade: settled/human · leans #262`

- decision:design-it-twice-on-262 — #262's installed-hook-path question is a load-bearing interface
  (the documented snippet's `${CLAUDE_PROJECT_DIR}` only resolves inside this checkout) and gets a
  design-it-twice panel. The other issues are mechanical enough to run single with alternatives
  named as untaken roads.
  `@grade: guess · leans #262 · settle: if the panel's three candidates converge on one answer, single was right and record that`

- decision:record-schema-frozen — the four-field gauge record stays frozen. New signal rides as a
  sidecar, the way #252's `gauge-uncalibrated.json` does.
  `@grade: settled/inherited · leans #265`

## Expiry

**End of wave 2**, or the first time any threshold or `~/.claude/settings.json` decision comes up —
whichever is first. Crossing it forces a contract-refresh before further dispatch.

## Confirmation

**Confirmed by Fred, 2026-07-27**, as written — no amendments.

Ruling on the blocker: **option 1** — #261 ships alone and merges before any other issue in this
epic is dispatched, then the real Trip gets dogfooded against a successor that can actually gauge
itself. Options 2 (raise the caps) and 3 (waive HARD for this epic) were both declined, which
leaves `decision:thresholds-untouched` intact and means no trip in this epic is a waived trip.

The HARD block that forced this checkpoint cleared without a waiver and without a handoff: Fred
compacted the session manually, the writer hook observed the smaller transcript, and the reading
fell `0.157 → 0.057`. Verbatim: *"for admirals I'll just compact manually. I wish I could have you
do that yourself, but the harness doesn't allow."*

Two things follow, both carried into the epic rather than settled here:

- Manual human compaction is a **fourth, undocumented exit** from a HARD trip, alongside
  refresh-request handoff, `block`, and `waive`. It is the cheapest of the four and the only one
  that preserves the running agent. It is also the only one an agent cannot invoke — the harness
  exposes no self-compaction. Routes to #266.
- The self-defeating-handoff problem under `decision:261-goes-first` is now doubly grounded: the
  refresh path is not merely blind post-handoff, it is more expensive than an exit the human can
  perform in one keystroke.

---

## Refresh — wave 2 (Fred, 2026-07-28)

The expiry clause fired: #262 is the `~/.claude/settings.json` trigger by definition. Presented at
the wave-1 checkpoint with a recommendation on each of four parts. Fred: **"refresh as proposed"** —
all four recommendations adopted, no amendments.

1. **Wave-2 set and order.** #269, #262, #264, #265, #268. **#269 lands before or with #262** —
   worktree isolation does not isolate hook code, so a Commander testing installer wiring inside a
   worktree is not actually isolated from the rail it is editing, and #269 changes how #262 must be
   validated.
   `@grade: settled/human · leans wave-2`

2. **Wave sizing.** #269 dispatches alone; the remaining four dispatch concurrently once it lands.
   This supersedes wave 1's "at most three concurrent commanders" cap for wave 2 only. The
   usage-limit budget rule still applies: if a limit reset is near, defer the four-wide dispatch past
   the reset rather than launching into it.
   `@grade: settled/human · leans wave-2`

3. **`~/.claude/settings.json` stays surfaced-always.** Unchanged from the original contract, now
   re-confirmed with the cost understood: #262's Commander must come back to Fred for anything
   touching the real settings file, and that will cost turns. Editing
   `.claude/settings.local.json` **inside a Commander's own worktree** remains pre-cleared.
   `@grade: settled/human`

4. **Thresholds stay untouched.** `decision:thresholds-untouched` survives the refresh intact. Noted
   in passing, not acted on: the calibration corpus this epic exists to produce has started — this
   Admiral sits at ~82K on a 1M window, which the 150K hard cap would have tripped. That is data for
   the follow-on epic, not a reason to move a number now. Any Commander proposing any threshold
   value, including a test fixture, still surfaces it rather than picking one.
   `@grade: settled/human · settle: follow-on epic, once real readings accumulate`

**Everything else in this contract carries forward unamended** — decision classes, permission
prerequisites, float-up routing, comms, honest-nulls, and the remaining pre-rulings.

### New expiry

**End of wave 2**, or the first time a threshold value or a `~/.claude/settings.json` write is
actually proposed — whichever is first. The second condition is no longer hypothetical: #262 will
reach it. When it does, that is a surfaced decision inside this contract, not another full refresh.

### Wave-1 evidence carried into wave 2

- #261/#202 verified live against the Admiral session itself: real `SessionStart` hook subprocess
  wrote the binding, the real writer hook produced a reading, `gauge_reader.read()` returned a live
  `Reading` at band SOFT, and the value self-updated on the next tool call with no manual write.
- The malformed-payload finding, filed to #265: a fail-open that emits nothing is indistinguishable
  from a broken fix. This is the epic's own thesis reproduced against the epic's own verification.
