# Implementer Handoff — g3: correct `docs/GAUGE_WRITER_HOOK.md`

**Work id:** issue-419-governor-identity · **Gate:** g3 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## Assigned task

`docs/GAUGE_WRITER_HOOK.md` is the governor write side's structural record. This repo has **no**
`docs/architecture/` map at all, so that document is the closest thing to an architecture packet for
this area — and it is **wrong in a load-bearing place today**. Gates g1 and g2 changed the code it
describes. Correct it.

Five edits, prose only:

**(a) The `isSidechain` row in the field table** currently says the field "must be falsy". That is now
only half true. Replace it with the polarity rule: **falsy** for a main-chain read, **truthy** for a
subagent's own transcript. Add an `agentId` row: top-level on the line, and it must equal the payload's
`agent_id`.

**(b) A short second table for the PAYLOAD fields the hook reads** — `transcript_path`, `session_id`,
`agent_id` and `agent_type`. Say plainly that `agent_id` appears **only** on a subagent's tool call and
is absent on a parent's. That single fact is what the whole fix rests on: identity is handed to the
hook by the harness, not discovered by it.

**(c) The session-to-spine binding section.** The outer key is now `session_id` for a top-level agent
and `session_id#agent_id` for a dispatched one; an **unusable** `agent_id` binds nothing at all; and
the "can only produce a reading for a session bound to exactly one spine" coupling now holds **per
agent**, which is what makes it true again for a dispatched agent.

**(d) The enumerated skip causes.** Add `subagent-transcript-missing`, and state the never-fall-back
rule in the document's own voice: when a subagent's derived transcript is absent, the writer writes
nothing rather than reading the parent's.

**(e) Name the TWO residuals that survive this change, beside each other.** The document already names
the first; the second is new and must not be left to be discovered:

1. A genuine orchestrator holding several spines under one bare key is **still** ambiguous and still
   silent. Unchanged by this work.
2. **New:** a subagent that never claims a spine now resolves to **zero** candidates and writes
   nothing — where before this change it would have resolved against the parent's bare key and, in a
   single-spine session, written a reading that was misattributed but present. That is a real coverage
   loss traded for correctness, and it is deliberate.

## Protected intent

Someone reading this document a year from now must be able to predict what the hook does without
reading the hook. The specific failure that made this gate necessary is that the document confidently
asserted a rule the code did not follow — so an agent that trusted it was misled. Every claim you leave
in it should be one you have checked against the code.

## Allowed scope

`docs/GAUGE_WRITER_HOOK.md` only. This is the **canonical source** — do not edit any installed copy
under `skills/`.

## Specific exclusions

No code change rides in this gate. If you find the code wrong, return it as a finding rather than
fixing it.

## Constraints

- Follow `constellation-how-to-talk`: plain words, one name per thing, no new coined vocabulary. Match
  the document's existing voice — it is written for an agent who has to act on it.
- **On the grep question**, because the plan was self-contradictory here and a cold critic caught it:
  use grep to **enumerate** occurrences and archive the count, then use **judgement** to adjudicate each
  one, and additionally read the field-table and skip-cause sections end to end. A token sweep alone
  cannot establish "no sentence still asserts the old polarity", because a sentence can assert it
  without using any of the swept words — "the parser reads only main-chain lines" is the shape to watch
  for.

## Close criteria — these are the pre-authored invariant chain, and they ARE the gate

This gate has no runtime test surface, so verify this frozen chain rather than inventing a
test-shaped proxy for "the document says what it should".

1. **No sentence in the document still asserts the pre-fix sidechain polarity.** Evidence is a **stated
   count** of occurrences of `isSidechain` / `sidechain` / `falsy` from an archived command, each
   adjudicated, **plus** an end-to-end read of the field-table and skip-cause sections.
2. **Every payload field the shipped hook reads appears in the document, and no field appears that the
   code does not read** — enumerated **by command** over the `data.get(...)` sites in both hook files,
   with the resulting field list archived. Not recalled from memory.
3. The document's stated binding key matches `spine_rail.binding_key`'s implementation, **including the
   bind-nothing case**, and **both** residuals in (e) are named.

## Required evidence

- The archived grep output with its **count**, and your adjudication of each hit.
- The archived field enumeration command and its output, and the comparison in both directions.
- The diff.

## Test mode

No test surface — this is prose. That is the stated rationale, not an exception being taken quietly:
the invariant chain above is what stands in for tests, which is why it is frozen in advance rather than
chosen by you.

## Verification commands

```
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
```

Should stay at **1667 passed, 2 skipped** — a doc edit must not move it. **`python -m pytest`, never
`py`** (the `py` launcher resolves to a codex runtime with no pytest).

## Inbound anchors

- **Structural:** `docs/GAUGE_WRITER_HOOK.md` — the field table (~line 202), the skip-cause
  enumeration (~233), the binding-assumption section (~308).
- **The code you are describing:** `scripts/hooks/spine_rail.py` (`binding_key`, `session_view`,
  `handle_post_tool_use`) and `scripts/hooks/gauge_writer_hook.py` (the derived-transcript helper,
  `find_latest_usage`, `handle_post_tool_use`), both as of `HEAD`.
- **Decision (settled/inherited):** with no packet map, this document **is** what the run's reconcile
  step folds into. It carries the weight an architecture packet would.

## Stop conditions

Stop and return if: the code contradicts what you were told to write; a close criterion cannot be met;
or you find the document asserts something else load-bearing and wrong that is outside these five
edits — record it, do not silently expand.

## Authority

Delegated Commander `cmdr-419-governor-identity` under the frozen epic-418 launch order. Local commits
fine; no push, no PR, no issues.

## Return format

`IMPLEMENTER_RESULT` at
`.agent-work/issue-419-governor-identity/results/g3-IMPLEMENTER_RESULT.md`: what you changed, the
archived command output with **real exit codes**, each of the three invariants met or not with its
evidence, anything you deliberately did not do, out-of-scope findings, and a **Workflow Feedback**
section (a bare "none" is not acceptable; if genuinely none, say what you checked).

---

# REWORK 1 — reviewer BLOCK, bounded scope addition

The reviewer confirmed **all three frozen invariants MET** and reproduced each against the code. The
BLOCK is one defect, and it is the same causal class the gate exists to remove: **a document claim
falsified by this issue's own upstream code change.**

`docs/GAUGE_WRITER_HOOK.md` still says the gauge record is **four fields** at **two** sites — around
**line 35** and around **line 164** — while `identity_resolution_ms` shipped in this issue's g2 commit
`5491bd4` (`git log -S identity_resolution_ms` returns exactly that one commit). The harm is concrete:
this is the section a human reads during the HITL eyeball check, so as written a human inspecting a
correct subagent gauge would judge it wrong.

**Note the original handoff named only ONE of the two sites.** Do not fix where you are pointed — find
every site. The reviewer's Fowler pass caught the general shape: this document asserts one code fact in
four-to-five places, so any anchor list framed as "the section to edit" misses sites systematically.
Enumerate by command and state the count.

## Scope, widened for this rework only

In addition to `docs/GAUGE_WRITER_HOOK.md`, you may now edit **comments only** in
`scripts/hooks/gauge_writer_hook.py`: its module docstring says the record is *"FROZEN, four fields
only"*, and there is a matching in-code comment. Both were made false by g2, and no other gate owns
them.

**Comments only. No behavior change, no logic edit, not one executable line.** The suite must stay at
exactly **1667 passed, 2 skipped** — a moved count means you changed behavior, and that is a stop
condition.

## What the corrected text has to say

The four fields are the **required** ones the reader validates, and `identity_resolution_ms` is an
**optional fifth** that rides the **dispatched-agent** record only — a top-level record still carries
exactly four, which is why the pre-existing tests still pass. Say what it measures and against what
budget. The eyeball-check section must tell a human that a fifth field on a subagent's gauge is
correct, not a defect.

## Also fix, same class, while you are in there

The reviewer recorded two further now-false code comments as triage candidates. If they are the same
four-field claim wearing different words, they are part of this fix. If they are a different claim
entirely, leave them and say so.

## Evidence required for the rework

- The **by-command enumeration** of every site claiming a four-field or frozen record, across the
  document **and** both hook files, with the **count stated** — before and after.
- The suite at exactly 1667 passed, 2 skipped, with its real exit code.
- `git diff --stat` showing only the document and comment lines changed.

## One observation from the reviewer, not a defect

Your archived post-edit sweep does not reproduce verbatim — its line numbers are stale by a few final
edits (offsets `[2,2,2,1,2]`). Counts and adjudications are sound, so this is not a blocker, but
re-archive the sweep **after** your last edit this time so no claim rests on a stale artifact.
