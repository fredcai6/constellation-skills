# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-e` at the g2-implement dispatch. Replaces `commander-w4-467-d`'s note
wholesale — its content is either carried below or is now done.**

## READ THIS FIRST — g1 is CLOSED. g2 is OPEN and a crew is out.

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g2-implement` — `in-progress`**.
  `e0-context`, `g1-implement`, `g1-review`, `g1-integrate` are **complete** (4/16).
  `amendments: 1` (the g1 `c3` retext).
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`
- **engine lease:** **ACTIVE** on both `spine.json` and `execute.json`, held by
  `commander-w4-467-e` under `session_01TTKPTbD6nnMt7jFWw9GtjX`. Every agent in this session shares
  that session id, so `claim` takes the idempotent-resume path — **no `--force`**. Mutating verbs
  require `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX` on the command line.
- **pid:** none. The crew backend is **`external`** (record-only registry entry + Agent-tool
  subagent), not a spawned CLI subprocess — so there is no PID to kill and no process to resume.
- **expected artifact:**
  `.agent-work/issue-467-trip-semantics/crew-handoffs/g2-implementer-result.md`
- **next command:** `recover_crews.py issue-467-trip-semantics`, then integrate the
  IMPLEMENTER_RESULT and advance `g2-implement`.

## TRUST ORDER — three commanders have now hit this instrument defect

**`execute.json` (tasks + `amendments` + per-task `evidence`) is the only projection that has been
correct end to end.** Rank your sources:

1. The raw task JSON and `current` — **authoritative**. One `python -c` read settles in a single
   command what the prose artifacts disagree about.
2. This note — a *pointer*, correct only as of its timestamp.
3. `MISSION_FRAME.md`, `LO-467.md` — **stale until proven otherwise**.

I inherited this warning and it held: my briefing and this note were both right this time, but I
verified all of it against the raw JSON before acting, and that is the practice to keep.

## STANDING TRAPS — do not spend context rediscovering these

1. **The obvious test proves nothing.** #431 is an **instruction-conformance** defect, not a
   mechanical deadlock. The advance was **never** blocked: `commander-w4-467-d` ran the closing
   advance at fill **0.162** (over hard 0.15) and the engine let it through, because a
   refresh-request was pending and the guard lifts. A test worded "the advance succeeds after the
   fix" passes in **both** worlds. Verify on **what the agent is TOLD** and on **whether anyone
   BEGAN work while over the line**. (Discrepancy D2, digest `w-4`.)
2. **DC6's observable** is "did anyone BEGIN work while over the line", never "did a handoff
   artifact appear" — the latter is true by construction and green in both worlds.
3. **The literal `<why-id>`.** The engine's refresh hint prints a literal `why_ref=<why-id>`.
   Attaching that literal **exits 0 and silently does nothing**. Read the real id from
   `execute.json`'s raw `why_trail`. Four instances have confirmed this; `g2(d)` fixes it.
4. **At/over hard, `advance --mechanical` must be REFUSED and `why_exempt` SUSPENDED**, because
   `_latest_why_record` skips mechanical markers and would otherwise reproduce #431 after the fix.

## FLOATED, awaiting the Admiral — do not decide this yourself

`g2-integrate.c3` is `match: {verdict: "APPROVE"}` — character-identical to the g1 check that could
not pass, because the reviewer handoff vocabulary is ACCEPT / ACCEPT WITH FINDINGS / REJECT. The
same trap is very likely in g3, g4 and g5. I have floated to the Admiral a single amendment
covering every remaining `*-integrate.c3` in the shape already ratified at g1 (`verdict_class:
ACCEPTED` + `blocking_findings: 0`, kind unchanged, literal verdict carried verbatim for audit).

**If the ruling has not arrived when you reach `g2-integrate`, STOP at that seam and ask.** Do not
amend on your own judgement, and do not waive — a waiver hides the bug and leaves the gate
permanently unpassable for every future reviewer following that handoff.

## If you trip

Commit at the seam, file the `refresh-request` with the **concrete** why-id read from the raw
`why_trail`, rewrite this note, release **both** leases, go idle. Four predecessors have done this
cleanly and none lost work. Do not push through, and **do not `start` new work over the line** —
`start` is a BEGIN-work verb, and starting work over the line is the exact violation this issue's
fix exists to refuse.
