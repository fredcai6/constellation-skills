# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-f` at the `g3b-glossary` seam. Replaces `commander-w4-467-e`'s note
wholesale — its content is either carried below or is now done.**

## READ THIS FIRST — all of g3 is CLOSED. `g3b-glossary` has NOT been started.

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g3b-glossary` — `pending`, NOT
  started.** **10/17 complete:** `e0-context`, all three `g1-*`, all three `g2-*`, and all three
  `g3-*`. `amendments: 2`. **17 gates, not 16** — see the amend below. Remaining 7: `g3b-glossary`,
  the three `g4-*`, and the three `g5-*`.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`, tree clean.
- **engine lease:** **RELEASED** on both `spine.json` and `execute.json`. Claim each **without
  `--force`** — every agent in this session shares `session_01TTKPTbD6nnMt7jFWw9GtjX`, so `claim`
  takes the idempotent-resume path. Mutating verbs need
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX`. **Verify with the raw JSON, not with this line.**
- **pid:** none — foreground, nothing running. Crew backend is `external` (record-only registry +
  Agent-tool subagent), so there is no process to kill or resume.
  `recover_crews.py issue-467-trip-semantics` → 8 crews, 0 unresolved (attempt-2 of the g3 reviewer
  was **abandoned deliberately** and relaunched as attempt-3 so the registry pointed at the right
  handoff file; that is not an unfinished crew).
- **refresh-request:** `e-g3-integrate-2`, concrete **`why_ref=w-9`**. The live why-record is now
  **`w-10`** (my g3-integrate close) — **read the raw `why_trail` for yourself, do not trust this
  line.**
- **next command:** claim both leases, then `start g3b-glossary` and do it in your own context. It
  is a **reasoning gate — no implement crew, no review crew.**

## Why I stopped here — read before "fixing" it

I crossed **hard** (fill **0.168164** ≥ **0.15** for `claude-opus-5`) while closing `g3-integrate`.
I closed that gate carrying my full understanding, then stopped. `g3b-glossary` is `pending` on
purpose: **`start` is a BEGIN-work verb**, and opening a gate at/over hard is the exact DC6 violation
this issue's fix **(b)** refuses. **This is a clean seam, not an interruption.**

## THE FINDING OF MY SHIFT — the instrument driving this run is the buggy one

**The INSTALLED workbench engine is PRE-#467.**

```
installed  ~/.claude/skills/constellation-workbench/scripts/checklist_engine.py
           140170 bytes   sha256 9c05192f0feb3d4d   NO TRIP_HARD_GUARDED_VERBS at all
repo       <worktree>/scripts/checklist_engine.py
           156060 bytes   sha256 ccbc247e0de0dcaa
```

Every Commander on this run has driven the spine with the engine that **has** the #431 bug — and I
**hit that bug live**, in the run that fixes it. Closing `g3-integrate` was refused with:

> *"context at 17% is at/over the hard limit — advancing is blocked until you request a refresh"*

That is #431 verbatim: the refusal lands on the advance that **carries the handoff**. The repo engine
in this very worktree would have let it through and demanded only that it not be silent.

**I did not switch instruments to get around it.** Changing the engine mid-run is plan surgery
outside the frozen plan and it is the Admiral's call. I took the engine's own prescribed release
path — a `refresh-request` keyed to the concrete `w-9` — and then closed the gate carrying my
understanding, which is what the fix is *for*.

**Two consequences the next Commander must not miss:**

1. **This is the strongest acceptance evidence #467 could have, and it arrived free.** `g5-acceptance`
   plans a *staged* round trip with two dispatched agents. A real one already happened, to the
   Commander, on the real spine. **Float to the Admiral whether to cite it in `g5`** — I did not
   fold it in, because `g5`'s scope is frozen and that is not my call.
2. **Do not read a green run as proof the fix works.** Anything driven through the installed engine
   is testing the OLD code. `g5` must name which engine binary it exercises, by hash.

## THE AMEND — `g3b-glossary`, your next gate

`amend` added **one** pending gate, positioned **after `g3-integrate`**. Authority: **Admiral, epic
#418 latitude contract**, ruling delivered at the previous seam and adopted from
`commander-w4-467-e`'s proposal.

It corrects `docs/agents/GLOSSARY.md:13` — the `trip` row's Usage-notes cell, which still reads
*"HARD blocks `advance` until the agent requests a context refresh."* **False** against the engine
shipped in this branch at `38f0b448`. The accurate replacement, checked against
`TRIP_HARD_GUARDED_VERBS` / `_trip_hard_gate` and the band comment at `checklist_engine.py:1215-1232`:
HARD refuses the verbs that **BEGIN** work at a gate (`start`, `reopen`) until a refresh-request
exists; it does **not** refuse the `advance` that closes the gate you are already in, because that
advance IS the handoff.

- **Reasoning gate — no crews.** Waiver reason is in the imperative.
- **`c1` is a command check and it is FAILABLE** — I ran it before the edit and it **exits 1**.
- **`c2`/`c3` are attested**: blast radius (one line, one file, proved by a pasted
  `git diff --numstat`) and wording accuracy against the code read at `p1`.
- **One line. One cell.** If correcting it accurately requires touching neighbouring text, **stop
  and float** rather than expanding.
- **Do NOT `reopen` anything.** `reopen` cascade-resets every downstream gate and is itself a
  begin-work verb the g2 fix guards at hard.

## TRUST ORDER — the instrument defect six commanders have now hit

**`execute.json` (tasks + `amendments` + per-task `evidence`) is the only projection correct end to
end.** One `python -c` read settles in a single command what the prose disagrees about.

1. The raw task JSON and `current` — **authoritative**.
2. This note — a *pointer*, correct only as of its timestamp.
3. `MISSION_FRAME.md`, `LO-467.md` — **stale until proven otherwise**.

## STANDING TRAPS — do not spend context rediscovering these

1. **The obvious test proves nothing.** #431 is an **instruction-conformance** defect, not a
   mechanical deadlock. A test worded "the advance succeeds after the fix" passes in **both**
   worlds. Verify on **what the agent is TOLD** and on **whether anyone BEGAN work over the line**.
   Rebuild the pre-change engine from `git show 38f0b448^` and run both side by side.
2. **DC6's observable** is "did anyone BEGIN work while over the line", never "did a handoff
   artifact appear".
3. **The literal `<why-id>`.** Attaching the engine's printed placeholder **exits 0 and silently
   does nothing**. Read the real id from the raw `why_trail`. g3 shipped the fix for the hint, but
   **the installed engine does not have it** — keep reading the raw trail.
4. **A negative-only test cannot fail.** g3 proved it: M5 dead-coded the resolver and all twelve
   negative assertions still passed. Ask of every test, "what would this do if the mechanism were
   deleted?"
5. **Write reviewer handoffs in `APPROVE` / `BLOCK`.** That is what the template prescribes and what
   every `*-integrate.c3` matches. Copy the g3 or g3-rework reviewer handoff's Return Format.
6. **The gauge is discarded if `observed_at` is even slightly in the future** (clock skew) or older
   than 30 minutes — it collapses to "no gauge" and any scenario built on it goes **vacuously
   green**. This cost me a false negative while reproducing B-1. Patch `_read_gauge` in tests;
   generate timestamps from the clock, never by hand.

## MODEL TIERS — Admiral ruling, binding, forward-looking only

Sonnet by default; **Opus needs a named reason in the dispatch text**. Sanctioned: a genuine design
choice the plan left open; **engine-semantics work where being subtly wrong is invisible**;
**adversarial review**.

- **`g4-review`, `g5-review` — Opus** (adversarial-review carve-out). Both g3 reviews ran this way
  and both earned it: the first found a real blocking defect, the second falsified the rework's
  own numbers.
- **`g4-implement` — Opus**, and **name the reason in the dispatch**: an engine-only append-only
  trip ledger at mutating chokepoints is engine-semantics work where being subtly wrong is
  invisible.
- **`g3b-glossary` — no crew at all.**
- Anything more mechanical — **Sonnet**. The g3 rework implementer ran on Sonnet against a
  demonstrated target and did it cleanly.

## OPEN, for the Admiral — carry these up, do not decide them

- **The stale installed engine (above).** Reinstall, or rule that the run continues on it
  deliberately. Either way `g5` must pin the engine by hash. **This is the one I most want answered.**
- **Whether my live #431 trip can be cited as `g5` acceptance evidence.** Frozen scope; not my call.
- **`decision:execute-gate-reserve-value` (30000) is `@grade: guess` and its authored settle
  experiment is NOT RUNNABLE** — confirmed independently four times now. `gauge.json` keeps only the
  latest reading; the per-gate context manifests carry no fill. **Cheaper replacement, ready to
  route:** log `(gate, fill_fraction)` at each gate boundary; after a handful of commander runs the
  number becomes measurable.
- **`docs/CHECKLIST_SCHEMA.md` under-documents the Task object by one optional key**
  (`context_headroom_tokens`). Natural home is this run's `reconcile` step, not a new gate.
- **Six triage candidates** now on `execute.json`: `tc1` (**CLOSED** — placed as `g3b-glossary`),
  `tc2` mid-gate handoff channel, **`tc3` RESOLVED** (see below), `tc4` `block()`'s missing status
  guard, `tc5` the reopen-path advisory/guard divergence, `tc6` the survey sidecar collision. Plus
  three from the g2 review survey and the gauge-attribution defect in `RESUME_OBSERVATION.md`.

**`tc3` is RESOLVED and the cause was a handoff field**, not a flaky suite: the stated baseline
`d376b786` is **not** the diff's parent — it spans 15 commits including g1 and g2. Against the true
parent `5a69a30b` the deltas are exactly **+17 passed and +125 subtests**. The stray subtest lived in
the stated baseline. **Lesson for every future handoff: pin a baseline to the commit it was measured
at.**

## WHAT g3 ACTUALLY COST, so you can calibrate

g3 went **BLOCK → rework → APPROVE**. The first review found the mutation log's **M15 "EQUIVALENT"
declaration was false** — the reasoning enumerated `start` and `advance` but never `block()`, which
has no status guard while `blocked` sits outside `TERMINAL`, so `active_id()` moves **backwards**
behind a later in-progress gate. In that state the shipped engine correctly refuses a silent close
of the overridden gate and the mutant does not, so the gate argument g3 itself added at `:2857` had
**zero coverage**. I reproduced it at the CLI before accepting it. Rework was **one test and a log
correction, no source change**. I then applied the mutation myself and watched the new test go red
and green, and fixed one wrong number the re-review found in the corrected log entry.

**The pattern worth keeping:** every claim that decided something on this gate was re-run by hand.
Three of them did not survive first contact.

## REMAINING INSTRUMENT DEFECTS FOR THE EPIC LEDGER

1. **The stale installed workbench engine** — above. The reviewer bundle was reinstalled at the last
   seam; **the workbench bundle was not**, and it is the one driving the spine.
2. **Review surveys collide.** The two g3 reviews would have overwritten each other's sidecars; I
   avoided it only by naming the second survey directory `g3-rework-review/` by hand. The first g3
   review also left an orphan `.agent-work/issue-467-trip-semantics/issue-467-trip-semantics-g3-review/`
   tree with a duplicate `r0-context.json`. Filed as `tc6`.

## If you trip

Commit at the seam, file the `refresh-request` with the **concrete** why-id from the raw
`why_trail`, rewrite this note, release **both** leases, go idle. Seven predecessors have now done
this cleanly and none lost work. Do not push through, and **do not `start` new work over the line**.
