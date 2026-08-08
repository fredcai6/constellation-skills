# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-f` immediately before dispatching the g3 reviewer. Replaces
`commander-w4-467-e`'s note wholesale — its content is either carried below or is now done.**

## READ THIS FIRST — g3-review is IN FLIGHT. Do not re-dispatch it blind.

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g3-review` — `in-progress`,
  reviewer crew DISPATCHED.** **9/17 tasks complete** (`e0-context`, all three `g1-*`, all three
  `g2-*`, `g3-implement`) — 17, not 16, because of the `g3b-glossary` amend below.
  `amendments: 2`.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`.
- **engine lease:** **CLAIMED, active** on both `spine.json` and `execute.json`, session
  `session_01TTKPTbD6nnMt7jFWw9GtjX`. Every agent in this session shares that id, so `claim` takes
  the idempotent-resume path — **claim without `--force`**. Mutating verbs need
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX`. **Verify with the raw JSON, not with this line.**
- **pid:** none — crew backend is `external` (record-only registry + Agent-tool subagent). There is
  no process to kill or resume.
- **expected artifact:**
  `.agent-work/issue-467-trip-semantics/crew-handoffs/g3-reviewer-result.md`, crew id
  `constellation/issue-467-trip-semantics/g3-review/reviewer/attempt-1`.
- **next command:** `py .../recover_crews.py issue-467-trip-semantics` first. If the g3 reviewer is
  COMPLETE, verify with `run_crew.py --verify-result <crew id>`, attach the `review-result`
  evidence, `advance g3-review`, then drive `g3-integrate`. If it is unresolved, recover it — do
  not launch a second one.

## THE AMEND YOU NEED TO KNOW ABOUT — `g3b-glossary` (new pending gate)

`amend` added **one** pending gate, `g3b-glossary`, positioned **after `g3-integrate`** and before
`g4-implement`. Authority: **Admiral, epic #418 latitude contract**, ruling delivered at this seam.

It fixes `docs/agents/GLOSSARY.md:13` — the `trip` row's Usage-notes cell, which still reads
*"HARD blocks `advance` until the agent requests a context refresh."* That is **false** against the
engine shipped in this branch at `38f0b448`: HARD now refuses the **begin-work** verbs
(`start`, `reopen`) and deliberately does **not** refuse `advance`.

- It is a **reasoning gate** — no implement crew, no review crew, waiver reason stated in the
  imperative. One line, one cell.
- `c1` is a **command** check and it is **failable**: I ran it before the edit and it **exits 1**.
- `c2`/`c3` are attested — blast radius (one line, one file, proved by `git diff --numstat`) and
  wording accuracy against the code.
- **Do not `reopen` anything to place it differently.** `reopen` cascade-resets every downstream
  gate including the completed `g3-implement`, and it is itself a begin-work verb the g2 fix now
  guards at hard. The Admiral overruled its own earlier "pull it into g2's scope" instruction
  precisely because that route is no longer mechanically available.
- If correcting the line accurately turns out to require touching neighbouring text: **stop and
  float**, do not expand.

## TRUST ORDER — the instrument defect five commanders have now hit

**`execute.json` (tasks + `amendments` + per-task `evidence`) is the only projection correct end to
end.** One `python -c` read settles in a single command what the prose disagrees about.

1. The raw task JSON and `current` — **authoritative**.
2. This note — a *pointer*, correct only as of its timestamp.
3. `MISSION_FRAME.md`, `LO-467.md` — **stale until proven otherwise**.

## STANDING TRAPS — do not spend context rediscovering these

1. **The obvious test proves nothing.** #431 is an **instruction-conformance** defect, not a
   mechanical deadlock. The advance was **never** blocked. A test worded "the advance succeeds after
   the fix" passes in **both** worlds. Verify on **what the agent is TOLD** and on **whether anyone
   BEGAN work over the line**. g2's PROBE D is the model: run the scenario on both engines side by
   side, rebuilding the pre-change engine from `git show 38f0b448^`.
2. **DC6's observable** is "did anyone BEGIN work while over the line", never "did a handoff
   artifact appear".
3. **The literal `<why-id>`.** The engine's refresh hint printed a literal `why_ref=<why-id>`;
   attaching that literal **exits 0 and silently does nothing**. Read the real id from the raw
   `why_trail`. **g3 shipped the fix** (`_refresh_attach_hint` now emits the concrete id), but keep
   reading the raw trail until you have seen the fixed hint work.
4. **A negative-only test cannot fail.** It passes with the mechanism dead-coded. g3 proved this
   empirically: mutation M5 dead-coded the resolver and all twelve negative assertions still passed.
5. **Write reviewer handoffs in `APPROVE` / `BLOCK`.** That is what the template prescribes and what
   every `*-integrate.c3` matches. The ACCEPT / ACCEPT-WITH-FINDINGS / REJECT vocabulary in the g1
   handoff was a one-off authoring slip, already amended; it is **not** a propagated defect. Copy
   the g2 or g3 reviewer handoff's Return Format section verbatim.

## MODEL TIERS — Admiral ruling, binding, forward-looking only

Standing default is **Sonnet**; **Opus needs a named reason stated in the dispatch text.**
Sanctioned reasons: a genuine design choice the plan left open; **engine-semantics work where being
subtly wrong is invisible**; **adversarial review, where the job is to attack a claim rather than
build to a spec**. "This gate feels important" is not a reason.

- **`g3-review`, `g4-review`, `g5-review` — Opus** (adversarial-review carve-out). Applied to the
  g3 reviewer already dispatched.
- **`g4-implement` — Opus**, and the reason must be named in the dispatch: it ships an engine-only
  append-only trip ledger at mutating chokepoints — engine-semantics work where being subtly wrong
  is invisible.
- **`g3b-glossary` — no crew at all.** Reasoning gate.
- Anything more mechanical — **Sonnet**.

## ENVIRONMENT CHANGE since `commander-w4-467-e` ran

The Admiral **re-installed `constellation-reviewer` from this repo**. Its bundled engine was three
weeks stale and **refused `amend` on surveys**, which is why the g1 reviewer force-waived its Fowler
postcondition. It is now byte-identical to the repo engine. **A reviewer hitting that postcondition
should fill it properly — it should not force-waive.** This retires instrument defect #1 below.

## OPEN, for the Admiral — carry these up, do not decide them

- **`decision:execute-gate-reserve-value` (30000) is `@grade: guess`, and its authored settle
  experiment is NOT RUNNABLE.** Confirmed independently three times now: `gauge.json` keeps only the
  **latest** reading, and the per-gate context manifests under `.agent-work/*/context/` carry **no
  fill value**. **A cheaper replacement experiment exists and should be routed:** log
  `(gate, fill_fraction)` at each gate boundary; after a handful of commander runs the number
  becomes measurable. The Admiral asked for this to be named explicitly in the return — it is.
- **`tc2`** mid-gate handoff channel · **`tc3`** the stray ±1 full-suite subtest (**not** this
  diff — the implementer measured 682 with its diff stashed against the 683 recorded at g2) · plus
  three from the g2 review survey · plus the gauge-attribution defect in `RESUME_OBSERVATION.md`.
- **`docs/CHECKLIST_SCHEMA.md` now under-documents the Task object by one optional key**
  (`context_headroom_tokens`). The g3 implementer flagged it; natural home is this run's `reconcile`
  step, not a new gate.

**`tc1` is CLOSED as an open question** — ruled in scope, placed as `g3b-glossary`. Do not re-float it.

## REMAINING INSTRUMENT DEFECT FOR THE EPIC LEDGER

**The two review surveys share item ids**, so their mechanical sidecars collide — g1's were
overwritten by g2's run (visible in `git status` as modified `r0`–`r6` files). Expect g3's survey to
do the same. Cosmetic for the verdict, corrupting for the audit trail.

## If you trip

Commit at the seam, file the `refresh-request` with the **concrete** why-id read from the raw
`why_trail`, rewrite this note, release **both** leases, go idle. Six predecessors have now done
this cleanly and none lost work. Do not push through, and **do not `start` new work over the line**.
