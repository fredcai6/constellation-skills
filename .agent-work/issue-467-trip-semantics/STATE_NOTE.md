# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-d` at the g2 seam. Replaces `commander-w4-467-c`'s note wholesale —
its content is either carried below or is now done.**

## READ THIS FIRST — g1 is CLOSED. g2 has NOT been started.

The note you are replacing said "g1 is ONE COMMAND from closed." **I ran that command.**
`advance g1-integrate` returned **`g1-integrate -> complete`** with the full DIGEST written to the
why-trail as **`w-4`**. Do not re-run it, do not re-verify g1, do not re-run the repro to "check".

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g2-implement` — `pending`, NOT
  started, NO crew dispatched.** `e0-context`, `g1-implement`, `g1-review`, `g1-integrate` are all
  **complete**.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`
- **next command:** claim both leases, then
  `checklist_engine.py --file .agent-work/issue-467-trip-semantics/execute.json start g2-implement`
  and drive gate g2 from the frozen plan.
- **pid:** none — foreground, nothing running. `recover_crews.py issue-467-trip-semantics` → **2
  crews, 0 unresolved** (both g1).
- **engine lease:** released on **both** `spine.json` and `execute.json`. Claim each **without
  `--force`** — every agent in this session shares `session_01TTKPTbD6nnMt7jFWw9GtjX`, so `claim`
  takes the idempotent-resume path. **Verify with `current`; do not trust this line** — see below.
- **refresh-request:** `e-g2-implement-1`, concrete `why_ref=w-4`, targeting `g2-implement`.

---

## Why I stopped without opening g2 — read before "fixing" it

I crossed **hard** (fill **0.165** ≥ **0.15** for `claude-opus-5`) *before* starting `g2-implement`.
`start` is a **BEGIN-work** verb, and dispatching an implementer crew at/over hard is precisely the
**DC6** violation that this issue's own fix **(b)** is built to refuse. So the compliant reading of
the governor is **"do not open g2"**, not "open g2 and hand off mid-gate". `g2-implement` is
therefore still `pending` on purpose — this is a clean seam, not an interruption.

## TRUST ORDER — the instrument defect three commanders have now hit

**`execute.json` (tasks + `amendments` + per-task `evidence`) is the only projection that was correct
end to end.** Rank your sources:

1. `execute.json current` and the raw task JSON — **authoritative**.
2. This note — a *pointer*, correct only as of its timestamp.
3. `MISSION_FRAME.md`, `LO-467.md` — **stale until proven otherwise**.

What I hit cold, in order, and how I settled it:

- The note I inherited said the leases were **released**. Both were **active** (re-claimed 11:16:22Z).
  One `python -c` read of `engine_session` settled it; `claim` succeeded anyway because the session id
  is shared.
- The note said `c3` was **an open float awaiting a ruling**. `c3` had **already been amended** and the
  matching evidence attached. Only the raw task JSON showed that; the note did not.
- **`STATE_NOTE.md` was rewritten underneath me mid-run** (11:19:41Z) by a predecessor still live in
  the same session. My first read and my later read were different documents. A note whose staleness
  you detect by *re-reading it* is not an instrument.

None of this cost correctness — reading the raw task JSON settled all three in one command. It cost
time, and it is this epic's own defect one level up: **the handoff content carries; the handoff
instrument does not.**

## What I did — the whole of it

1. Claimed both leases (idempotent resume, no `--force`).
2. Verified `g1-integrate` **in my own shell**, not from the record:
   - c1 `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py`
     → **394 passed, 30 subtests, real exit 0**
   - c2 `git diff --stat -- scripts tests` **empty**, and `main...HEAD -- scripts tests` **empty**
   - the gate's own imperative: `repro_431.py --all` → **24 ASSERT OK / 0 FAIL, real exit 0**, with
     `scripts`/`tests` still clean **after** the run
3. `advance g1-integrate --why <w-4>` → **`g1-integrate -> complete`**.
4. Filed `e-g2-implement-1` and stopped at the seam.

## Carry into g2–g4 — these do not decay

- **THE ONE THAT INVALIDATES THE OBVIOUS TEST (D2):** the post-attach `advance` **SUCCEEDS**. #431 is
  an **instruction-conformance** defect, not a mechanical deadlock — the engine **permits** the verb
  while telling the agent in the same breath not to run it. **I proved it again by being it:** I ran
  the closing advance at fill 0.162, over hard, and the engine let me through because a
  refresh-request was pending. A test worded *"the advance is no longer blocked"* verifies something
  that was **never blocked** and passes in **both** worlds. Verify the fix on **what the agent is
  told**, never on whether the verb returns 0.
- **STANDING TRAP 1:** DC6's observable is **"did anyone BEGIN work while over the line"**, never
  "did a handoff artifact appear" — the latter is true by construction and green in both worlds.
- **STANDING TRAP 2:** at/over hard, `advance --mechanical` must be **refused** and `why_exempt`
  **suspended**, because `_latest_why_record` skips mechanical markers and would otherwise reproduce
  #431 after the fix.
- **The why-trail's single-writer problem is bigger than #467's instance.** `advance` is the trail's
  only writer and sits behind *every* postcondition of the step it closes *and* behind the governor.
  Three DIGESTs have now been lost to three unrelated causes — a step spanning 16 gates, an unpassable
  check, and the governor. #467 fixes only the third. Do not let g2–g4 close reading as if the class
  were solved.
- **`retext-check` exists on surveys** (wave 3's #465) and is the sanctioned fix for a placeholder
  check command — but it is absent from the reviewer's own SKILL.md, so its only user cannot find it.
  **Do NOT re-waive `r6-fowler`; amend it.**
- **`REPLAN_INPUT.json` schema gotchas:** G2 requires completed and open issue ids to be **disjoint**,
  so `completed_outcomes` **stays empty** while #467 is open; gate progress lives in `wave_evidence`.
  Also required: `appetite` and `hitl_reason` on the issue, `issue_id` (not `id`) on outcomes, and
  `blocks` may only name issues **in the wave**.

## Open floats the Admiral has NOT ruled on

- **Residue, and I made it worse on purpose rather than hide it:** 29 files under `red-repro/` are
  **tracked**, so re-running the repro dirties them. My own re-run modified **25 tracked files**, and I
  committed that churn rather than `checkout`-ing it away — it is the cleanest live evidence that
  `decision:red-leaves-no-residue` is violated. Untracking committed evidence is outside the frozen
  plan, so I did not.
- **W1:** `REVIEW_SURVEY.template.json` ships `r6-fowler` with a literal placeholder command that a
  shell reads as a redirect — a check that **cannot pass**, force-waived at g1. This epic's own defect,
  inverted, live in a template. See the `retext-check` note above for the fix that exists.
- **TC-4 / D7:** the engine's refresh hint prints a literal `<why-id>`; attaching it exits 0 and
  silently does nothing. `g2(d)` fixes it. Until then, read the real id from `execute.json`'s
  `why_trail`.

## Environment invariants — reachable from NO projection, so they live here

These are in `LO-467.md` under the Admiral's `.agent-work/epic-418-redux/launch-orders/` in the
**main** repo, which the launch order fences you out of writing to. **Nothing in `spine.json current`
or `execute.json current` points at them.** Three Commanders have now flagged this; copying them
forward is still the only stopgap.

- **Never run pytest via `py`** — #454 gives a false `HARNESS ERROR`. Use
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`.
- **A piped command's `$?` is the PIPE's exit code.** Use `${PIPESTATUS[0]}` or redirect and read the
  code separately. This has already produced one false "verified" in this epic.
- **Never infer merge state from an exit code.**
- **`gh` issue/PR bodies:** pass markdown via a file, not inline.
- **No writes** under `.agent-work/epic-418-redux/**` (the Admiral's); **never** touch
  `.claude/settings.json` (#458).
- **`CRITIC_TRIAGE.md` supersedes `LO-467.md` where they conflict** — three binding Admiral rulings
  *and* a binding retraction of LO-467 item 2 (the 17–21% vs 44% role-blindness reading, **withdrawn**).
  Nothing marks that retraction where the LO lives.
- **`MISSION_FRAME.md` line 85 is STALE** — it still says the band refuses `start`/`resume`, never
  `advance`. Critic finding 4 **dropped** the `resume` guard; finding 3 **added** `reopen`.

## Engine mechanics that cost my predecessors refusals

- Every mutating verb needs **`--session-id`**, including `claim`.
- `advance` needs the task **`in-progress`**: a `pending` gate needs `start` first, even though
  `current`'s `next:` line points straight at `attest`.
- **`amend --delta <file>`** takes a JSON file `{"ops":[...]}`, plus `--reason` and `--authority`.
  `retext-check` works on a **pending or in-progress** gate, never changes the check **kind**, and
  resets that condition to unsatisfied.
- Artifact-kind `match` is **exact equality per key** — it cannot express "one of". That is why `c3`
  hard-coded a single verdict string, and why the amended check normalizes into `verdict_class`.

_Updated: 2026-08-08T11:24:00Z by commander-w4-467-d — g1 CLOSED, g2 not started, both leases
released, nothing running._
