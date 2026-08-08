# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-e` at the g3-review seam. Replaces `commander-w4-467-d`'s note
wholesale — its content is either carried below or is now done.**

## READ THIS FIRST — g2 is CLOSED, g3-implement is CLOSED. g3-review has NOT been started.

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g3-review` — `pending`, NOT
  started, NO crew dispatched.** **8/16 complete:** `e0-context`, all three `g1-*`, all three
  `g2-*`, and `g3-implement`. `amendments: 1` (the g1 `c3` retext — see the retraction below).
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467` · HEAD **`f9925be6`**, tree clean.
- **engine lease:** **RELEASED** on both `spine.json` and `execute.json`. Claim each **without
  `--force`** — every agent in this session shares `session_01TTKPTbD6nnMt7jFWw9GtjX`, so `claim`
  takes the idempotent-resume path. Mutating verbs need
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX` on the command line.
  **Verify with the raw JSON, not with this line.**
- **pid:** none — foreground, nothing running. Crew backend is `external` (record-only registry +
  Agent-tool subagent), so there is no process to kill or resume.
  `recover_crews.py issue-467-trip-semantics` → 5 crews, 0 unresolved.
- **refresh-request:** `e-g3-review-1`, concrete **`why_ref=w-8`**, targeting `g3-review`.
- **next command:** claim both leases, `attest g3-review --cond p1 --which preconditions` (the
  IMPLEMENTER_RESULT is attached as `e-g3-implement-1` and verified fresh), then
  `start g3-review` and dispatch the reviewer against the frozen g3-review imperative.

## Why I stopped without opening g3-review — read before "fixing" it

I crossed **hard** (fill **0.153181** ≥ **0.15** for `claude-opus-5`) *after* closing
`g3-implement` and *before* starting `g3-review`. `start` is a **BEGIN-work** verb, and dispatching
a crew at/over hard is precisely the **DC6** violation this issue's own fix **(b)** is built to
refuse. So the compliant reading is **"do not open g3-review"**, not "open it and hand off
mid-gate". `g3-review` is `pending` on purpose. **This is a clean seam, not an interruption.**

Note the dogfooding: the fix shipped in this very tree would now refuse me if I tried. I did not
need the engine to refuse me — I refused myself. Hold that standard.

## TRUST ORDER — the instrument defect four commanders have now hit

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
   side.
2. **DC6's observable** is "did anyone BEGIN work while over the line", never "did a handoff
   artifact appear".
3. **The literal `<why-id>`.** The engine's refresh hint printed a literal `why_ref=<why-id>`;
   attaching that literal **exits 0 and silently does nothing**. Read the real id from the raw
   `why_trail`. **g3 shipped the fix for this** (`_refresh_attach_hint` now emits the concrete id),
   but keep reading the raw trail until you have seen the fixed hint work.
4. **A negative-only test cannot fail.** It passes with the mechanism dead-coded. g3 proved this
   empirically: mutation M5 dead-coded the resolver and all twelve negative assertions still passed.

## RETRACTED — do not act on it (I raised it, then disproved it myself)

I floated to the Admiral that `*-integrate.c3`'s `match: {verdict: "APPROVE"}` was a structural trap
sitting in every gate. **It is not, and I withdrew it.** The reviewer handoff **template**
(`constellation-commander/templates/REVIEWER_HANDOFF.template.md`, Return Format) prescribes
**`APPROVE` / `BLOCK`**, which is exactly what `c3` matches. The ACCEPT / ACCEPT WITH FINDINGS /
REJECT vocabulary was hand-written into the **g1 reviewer handoff** by that commander
(`g1-reviewer-handoff.md:84`) — a one-off authoring slip, not a propagated defect.

**Standing rule for g3-g5: write the reviewer handoff in `APPROVE` / `BLOCK` and `c3` passes as
frozen. No amendment needed.** When a `c3` looks unpassable, check the handoff against the template
before concluding the plan is broken. My g2 reviewer handoff does this correctly — copy its Return
Format section.

## OPEN, for the Admiral — carry these up, do not decide them

- **`tc1` — `docs/agents/GLOSSARY.md:13`** still reads *"HARD blocks `advance` until the agent
  requests a context refresh."* **Now false**, and it is the glossary every constellation agent
  reads — it teaches the exact belief #431 came from. Confirmed independently by the g2 implementer
  and the g2 reviewer; root-caused as shotgun surgery (same fact mirrored in four hand-maintained
  places, three updated, one missed). **Both crews and I rate it must-fix before epic #418 closes.**
  Outside g2/g3's frozen scope. Floated; no ruling yet.
- **`decision:execute-gate-reserve-value` (30000) is `@grade: guess`, and its authored settle
  experiment is NOT RUNNABLE.** I confirmed this and the g3 implementer confirmed it again:
  `gauge.json` keeps only the **latest** reading, and the per-gate context manifests under
  `.agent-work/*/context/` carry **no fill value**. **A cheaper replacement experiment exists and
  should be routed:** log `(gate, fill_fraction)` at each gate boundary; after a handful of
  commander runs the number becomes measurable. The Admiral asked for this settle experiment to be
  named explicitly in the return — it is named here and in my return message.
- **`tc2`** mid-gate handoff channel · **`tc3`** the stray ±1 subtest (not this diff) · plus three
  from the g2 review survey.

## TWO INSTRUMENT DEFECTS FOR THE EPIC LEDGER

1. **The reviewer skill's INSTALLED engine bundle is stale** — it refuses `amend` on surveys, which
   is why the g1 reviewer force-waived its Fowler postcondition. The repo engine supports it and the
   g2 reviewer's `amend` worked first try. **Re-run `install_constellation.py`.**
2. **The two review surveys share item ids**, so their mechanical sidecars collide — g1's were
   overwritten by g2's run (visible in `git status` as modified `r0`–`r6` files).

## If you trip

Commit at the seam, file the `refresh-request` with the **concrete** why-id from the raw
`why_trail`, rewrite this note, release **both** leases, go idle. Five predecessors have now done
this cleanly and none lost work. Do not push through, and **do not `start` new work over the line**.
