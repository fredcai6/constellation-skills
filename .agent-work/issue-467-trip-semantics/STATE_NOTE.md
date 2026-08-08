# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-c` at the g1-integrate seam.** Read this together with
`execute.json current`. Its DIGEST is accurate but was written one task ago (at the `g1-review`
advance), so **this file carries the delta since then** — see "Why the DIGEST is one task behind".

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g1-integrate` (in-progress)**.
  `e0-context`, `g1-implement`, `g1-review` are **complete**. `g1-integrate` is **one condition short**
  and that condition needs an Admiral ruling — see below.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`
- **next command:**
  `python C:/Programs/constellation-skills/scripts/checklist_engine.py --file .agent-work/issue-467-trip-semantics/execute.json current`
  — then apply the Admiral's c3 ruling (waive or amend), `advance g1-integrate`, and open `g2`.
- **pid:** none — foreground, no crew running.
  `recover_crews.py issue-467-trip-semantics` → **2 crews, 0 unresolved**.
- **expected artifact:** none pending. Everything g1 produced is committed at `3b8f7535`.
- **engine lease:** **RELEASED cleanly.** Claim without `--force`, on **both** `spine.json` and
  `execute.json` (both are leased separately; I had to claim each).

---

## THE ONE THING BLOCKING g1-integrate — do not solve it yourself

`g1-integrate` c3 is `{kind: artifact, evidence_type: review-result, match: {verdict: "APPROVE"}}` —
the **literal string** `APPROVE`. The reviewer handoff frozen at the g1 seam prescribes a *different*
vocabulary: `ACCEPT` / `ACCEPT WITH FINDINGS` / `REJECT`, and says in terms that
`ACCEPT WITH FINDINGS` is the healthy outcome and a bare `ACCEPT` on this gate would itself read as a
check that could not fail. The reviewer obeyed its handoff and returned `ACCEPT WITH FINDINGS` with
**0 blocking findings**.

So **the frozen plan and the frozen handoff disagree on the word**, and c3 cannot pass as written.

**I attached the verdict as the reviewer actually wrote it** (`e-g1-integrate-1`). **I did not attach a
second artifact reading `APPROVE`** — that is fabricating evidence to satisfy a check, which is the
exact defect this epic exists to kill. Do not do it either.

**Floated to the Admiral (team-lead) and unanswered when I stopped.** Options put to them:
(a) `waive g1-integrate --cond c3 --authority human --reason ...` on the ground that
`ACCEPT WITH FINDINGS` + 0 blocking *is* approval; (b) `amend` c3 to the handoff's vocabulary;
(c) something else. **Apply their ruling; do not pick one on your own judgement.**

`c1` and `c2` both **pass in my hands** and will pass on `advance`:
- c1 `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py`
  → **394 passed, 30 subtests, real exit 0**
- c2 `test -z "$(git diff --stat -- scripts tests)"` → **real exit 0**

---

## Why the DIGEST is one task behind — and it is the epic's own defect, live

`advance` is the only writer of the why-trail. **I cannot `advance g1-integrate` because c3 cannot
pass.** So I cannot write my handoff DIGEST through the normal channel — **not because of the
governor, but because a postcondition is unpassable.**

That is #431's cousin and it is worth recording: the why-trail's single writer is gated behind
*every* postcondition of the step it closes, so **any** unpassable check silently costs the run its
cold-start surface, exactly as the governor did. My predecessor could not write the spine's DIGEST
because `execute` spans 16 gates; I cannot write `g1-integrate`'s because one of its checks is
malformed. Same failure, two unrelated causes. This file is the workaround both times.

The `execute.json` DIGEST you will read is the one I wrote at the `g1-review` advance. **It is
accurate and complete about g1's evidence** — trust it. It is missing only what this file adds.

---

## What is done since that DIGEST was written

1. **`g1-integrate` p1 attested**, gate started, honest review-result attached.
2. **I re-ran the repro myself** (the gate's own imperative): `repro_431.py --all` →
   **24 ASSERT OK / 0 FAIL, real exit 0**, and the engine's own `CONTEXT 30% (>= hard)` line is in my
   transcript. The RED reproduces in my hands.
3. **Guards re-verified in my own shell:** `git diff --stat -- scripts tests` **empty** *and*
   `git diff --stat main...HEAD -- scripts tests` **empty**. Live `spine.json`/`execute.json` md5s
   **unchanged** across the repro run.
4. **`triage-candidates/g1-candidates.md`** written — six candidates, **none filed**.
5. **`RESUME_OBSERVATION.md`** — my second-resume section appended (I did not edit my predecessor's).
6. **`REPLAN_INPUT.json`** written and **verified**:
   `verify_iterative_role_artifacts.py commander --work-id issue-467-trip-semantics` → **real exit 0**.
   6 wave-evidence claims, 7 classified discrepancies.

Commits: `e4092af8` (g1-review closure + artifacts), `3b8f7535` (REPLAN_INPUT).

---

## Carry these forward — they do not decay

- **STANDING TRAP 1:** DC6's observable is **"did anyone BEGIN work while over the line"**, never "did
  a handoff artifact appear" — the latter is true by construction and green in both worlds.
- **STANDING TRAP 2:** at/over hard, `advance --mechanical` must be **refused** and `why_exempt`
  **suspended**, because `_latest_why_record` skips mechanical markers and would otherwise reproduce
  #431 after the fix.
- **NEW, AND g2–g4 MUST CARRY IT:** the reviewer's PROBE 2 shows the post-attach `advance` **SUCCEEDS
  and writes a fresh DIGEST**. **#431 is an instruction-conformance defect, not a mechanical
  deadlock** — the engine *permits* the advance while telling the agent in the same breath not to run
  it. A fix verified as "the advance is no longer blocked" verifies something that was never blocked.
  Recorded as discrepancy **D2**.
- **`REPLAN_INPUT.json` schema gotcha**, so you do not rediscover it: G2 requires completed and open
  issue ids to be **disjoint**, so `completed_outcomes` **must stay empty** while #467 is open. Gate
  progress lives in `wave_evidence`. Also required and easy to miss: `appetite` and `hitl_reason` on
  the issue, `issue_id` (not `id`) on outcomes, and `blocks` may only name issues **in the wave**.

## Environment invariants — reachable from NO projection, so they are copied here

These live in `LO-467.md` under the Admiral's `.agent-work/epic-418-redux/launch-orders/` in the
**main** repo, which the launch order fences you out of writing to. **Nothing in `spine.json current`
or `execute.json current` points at them.** Both my predecessor and I flagged this; copying them here
is the current stopgap.

- **Never run pytest via `py`** — #454 gives a false `HARNESS ERROR`. Use
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`.
- **A piped command's `$?` is the PIPE's exit code.** Use `${PIPESTATUS[0]}`, or redirect to a file
  and read the code separately. This has already produced one false "verified" in this epic.
- **Never infer merge state from an exit code.**
- **`gh` issue/PR bodies:** pass markdown via a file, not inline.
- **No writes** under `.agent-work/epic-418-redux/**` (the Admiral's), and **never** touch
  `.claude/settings.json` (#458).
- **`CRITIC_TRIAGE.md` supersedes `LO-467.md` where they conflict** — it carries three binding Admiral
  rulings *and* a binding retraction of LO-467 item 2 (the 17–21% vs 44% role-blindness reading,
  **withdrawn**). Nothing marks that retraction where the LO itself lives, so a successor that reads
  the LO and not `CRITIC_TRIAGE.md` will cite retracted evidence as current.
- **`MISSION_FRAME.md` line 85 is STALE** — it still reads "the band refuses `start`/`resume`, never
  `advance`". Critic finding 4 **dropped** the `resume` guard and finding 3 **added** `reopen`. The
  DIGEST is right; the frame is wrong.

## Engine mechanics that cost me refusals

- Every mutating verb needs **`--session-id`**, including `claim` itself.
- `advance` requires the task to be **`in-progress`**: a gate sitting at `pending` needs `start` first,
  even though `current`'s `next:` line points straight at `attest`.

_Updated: 2026-08-08T11:15:00Z by commander-w4-467-c — lease released, nothing running._
