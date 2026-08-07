# Crash-resume state note — issue-308

> **READ THIS BANNER FIRST. #308 WAS RE-SCOPED BY TOMMY MID-RUN.** The engine's
> `execute.json` was frozen under the OLD scope, and several of its gates, constraints and
> **check scripts now encode withdrawn rules**. Where this note and `execute.json` disagree,
> **this note is right** — it is newer. The corrections are itemized below. **Do not start
> from `current` alone.**

- **step:** execute · `e0-context`, `g1`, `g2` complete. Next work is the **migration**, which the frozen plan still calls `g4-disposition-lessons`.
- **slug:** work-id `issue-308`, branch `epic-298/308`, worktree `C:/Programs/constellation-skills-wt/e298-308`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-308/execute.json current --session-id commander-308-e298`
- **pid:** none — foreground
- **expected artifact:** every active lesson present as an episode under `episodes/active/`; cap gone; read path cut; #322 folded; spine driven to `archive`, lease released last.

Everything through `182a9fa` is committed and pushed. Nothing of value is worktree-local.
Two leases, same session id `commander-308-e298`, on `spine.json` and `execute.json`.

---

## THE RE-SCOPE — what #308 is now

**The issue is: get the observations into the episode store without losing any of them.
That is the whole job.** The updated issue body on GitHub is authoritative.

### WITHDRAWN — do NOT do these

| withdrawn | note |
|---|---|
| **The consolidation (`g6`)** | **WITHDRAWN, not blocked.** There is no bin ruling and there never will be one. **Do not wait for it.** |
| **The two-bin routing question** | dead. `ROUTING_QUESTION.md` is a historical artifact, not a pending decision. |
| **Graduating anything to `docs/agents/`** | no doctrine lines, no `ORCHESTRATOR_CONTEXT.md` additions. |
| **Deleting any lesson** | deletion is off entirely. |

**Why**, so you can apply it to cases nobody foresaw: deciding which observation deserves a
doctrine line **is** an importance judgement, and Tommy ruled importance requires a global
view built from recurrence across runs and roles. The store is far too small for that.
Landing doctrine now would be a local call dressed as a global one.

Tommy, verbatim: *"there are no catastrophic failures, just workarounds and inefficiencies"*;
*"fundamentally the thing that is finding the episodes cannot make a call on the
importance... we just want observations of what happened and how they worked around it."*

### STANDS — the actual job

1. **Migrate EVERY active lesson into an episode.** A lesson already *is* an observation:
   what happened plus how someone worked around it. **Migrate it; do not judge it.**
   Deletion applies **only** to a genuine duplicate of another episode, and that is a
   **MERGE, not a drop** — preserve the recurrence signal, because frequency is now the
   field that matters most.
2. **Drop the 20-entry cap** (`g3`), naming the curator's regular cleanup as its
   replacement. No substitute numeric cap.
3. **Cut live agents off from lessons** (`g5`) — the READ path only.
4. **Keep the writer.** Cutover, not demolition. Ratified and unchanged.
5. **#322** — already done at `g2`.

---

## TWO ARTIFACTS I LEFT THAT NOW ASSERT WITHDRAWN RULES

**1. `checks/dispositions_done.py` ENFORCES THE OPPOSITE OF THE REQUIREMENT. Do not trust
it.** It requires **exactly one** surviving active lesson
(`verify-launch-order-claims-against-code`) and **fails on zero**. That was correct under the
old scope, where disposing that lesson *was* bin 2. Under the new scope **zero active entries
is the correct end state**, because every lesson becomes an episode. The script must be
rewritten or replaced before `g4` can pass. It is wired as `g4-disposition-lessons` c1.

**2. `notes-308.md`'s "PROPOSED dispositions for g4" table is OBSOLETE.** Its 20 rows route
lessons to GRADUATE / DELETE / RETIRE. **Graduation and deletion are both withdrawn.** Its
only surviving value is as a per-lesson summary of what each lesson contains. **Do not
execute it.** A correction banner is appended to that file.

Neither is deleted — deleting them would lose the record of what was decided and why. They
are flagged instead.

---

## The schema rule that governs the migration

From Tommy, and it decides field questions without asking:

> **A required field is an instruction. Anything an agent MUST fill, it WILL fill —
> including when it does not know.**
> - **Required fields must be OBSERVABLE** — what happened, where, how many times.
> - **Anything needing judgement must be OPTIONAL and must NOT be SOLICITED BY NAME.**

The naming half matters as much as the optionality half: an optional `other-notes` invites
what the agent actually noticed; an optional `severity` / `root-cause` / `bin` **manufactures
a confident one-run guess**, because naming the subject solicits the answer.

**Applied to the migration:**

- Extra fields are **fine** — add `other-notes` free text where the three fields do not fit.
- Put anything that does not fit into `other-notes` **verbatim from the lesson**. Do not
  paraphrase it into a judgement.
- If a lesson reads as a severity or cause claim, **carry it as the original author's words,
  attributed** — do not promote it to a field, do not strip it. It is an observation that
  someone once wrote that.
- **A blank is a valid value.** Report unknown counts as a headline number, not a defect.
- **#342: `create` requires `observed-behavior`. NEVER back-fill a plausible-sounding
  observation to satisfy it.** Record what exists, mark the gap unknown, and if the schema
  refuses an honest gap, **report that as a finding rather than inventing content.** Twenty
  episodes with visible holes are worth more than twenty that read complete and are not.
- If the schema forces a judgement anywhere else, **file it** — a second instance beyond
  #342 would show the shape of the problem rather than just an instance.

## Deliverable numbers

**Report the migration count, and how many episodes carry an unknown field.** Those two
numbers are the deliverable.

---

## MUST BE MIGRATED AS AN EPISODE — this run's own observation

The Admiral asked for this explicitly and it must not be lost. In my own words:

> While planning the consolidation of a cluster whose shared failure mode is *an
> under-inclusive or stale secondhand claim taken as premise*, **I committed that exact
> failure mode twice.** First, my `g5` imperative enumerated **5** live-agent lesson-intake
> sites as though complete; a command over the corpus finds **6 across 5 files** (the missed
> one is in `ADMIRAL_SPINE.template.json`, in the `latitude` task, not `context`). Second,
> **one revision later, inside the guard written to fix that**, I used the character class
> `[^.\n]`, which excludes the dot and so could never match any phrase containing
> `.agent-work/` — it went green against three live intake sites.

- **recurrence count: 2**, within roughly one hour, by the same agent.
- **context:** corpus at `4cec87a`, role commander, spine step `plan`.
- **effect / workaround:** both caught — the first by a cold plan critic, the second by
  running the guard and reading which sites it named. Workaround: replace the hand-written
  list with a script that enumerates the corpus and asserts the enumeration is non-empty
  (`checks/lesson_intake_is_cut.py`).
- **why it may matter more than the two episodes it was consolidating:** it happened under
  **maximal awareness** — the agent had just finished writing down that this is a recurring
  failure.
- **`other-notes`, recorded as an observation and NOT as a judgement, per the rule above:**
  the author concluded at the time that this argued for mechanism over prose. That
  conclusion is exactly the kind of importance call Tommy has now ruled a local agent should
  not make. It is recorded as *something the author wrote*, not as a finding.

Cluster A and cluster B also become episodes, minus any read on how bad they are. The two
coverage numbers (mechanism 1/3, prose 3/3) stay as **observed facts about the remedies**,
used to decide nothing.

---

## Environment facts that still bite

- Interpreter is `python` (3.14, has pytest). **`py` has no pytest** and reads as a silently
  green suite. Full suite ≈ 415s; green at `4cec87a`, `1dd83a1`, `182a9fa`.
- **Backticks inside a double-quoted shell string are executed** — this broke a postcondition
  and made it fail for entirely the wrong reason. Single-quote grep patterns.
- **`git checkout <file>` to undo a test mutation reverts the real edit too.** Snapshot to a
  scratch copy instead. Cost one full redo of the `EPISODE_STORE.md` edit.
- `g5` must also update `tests/test_context_manifest.py` (~line 550), which pins the spine
  declaration list including `(".agent-work/LESSONS.md", False)` as an exact literal.
  Dropping the manifest entry without that edit reds the suite.
- Never touch the main checkout `C:/Programs/constellation-skills` — the human's uncommitted
  work is there.

## Kept, pending Tommy

`docs/agents/CREW_CONTEXT.md` (landed at `g1`) **stays for now.** The Admiral reads the
"no `CREW_CONTEXT.md`" instruction narrowly on purpose: what landed is **observable
environment facts** (`py` has no pytest, Windows encoding, the CRLF / `text=auto` trap), not
importance judgements distilled from episodes. Flagged to Tommy; if he wants it out, it comes
out in one commit.

## #304 map-contract confirmation (for #307's measurement arm)

This run's `map_orient` returned, verbatim:

```
DEGRADED-NO-MAP
```

at commit `4cec87a`, discharged with 5 hash-pinned substitutes plus an unmapped gap and an
escalation (receipt `.agent-work/issue-308/map-orientation.json`). Per the Admiral this is
**#304's map-input contract firing in a real dispatch for the first time** — the code was
merged and reviewed but absent from the installed corpus until shortly before this run.

_Updated: 2026-08-02T22:05:00Z_
