# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-c`, tripped at HARD on the advance that would have closed g1.**

## READ THIS FIRST — g1 is ONE COMMAND from closed. Do not redo any of it.

All three `g1-integrate` postconditions are **MET, not waived**. The c3 ruling is applied. The
evidence is attached. **The only thing missing is the `advance` itself**, which the governor refused
at 15%.

**Your first real command, after claiming the lease:**

```
python C:/Programs/constellation-skills/scripts/checklist_engine.py \
  --file .agent-work/issue-467-trip-semantics/execute.json \
  advance g1-integrate --session-id <yours> --why "<paste the DIGEST below>"
```

Then g1 is closed and you open **g2 — the fix itself**.

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g1-integrate` (in-progress, all
  postconditions met)**. `e0-context`, `g1-implement`, `g1-review` **complete**.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`
- **pid:** none — foreground, nothing running. `recover_crews.py issue-467-trip-semantics` → **2
  crews, 0 unresolved**.
- **engine lease:** **RELEASED** on both `spine.json` and `execute.json`. Claim without `--force`.
  Both are leased **separately** — claim each.
- **refresh-request:** filed as `e-g1-integrate-3` with the **concrete** `why_ref=w-3`.

---

## THE DIGEST I COULD NOT WRITE

`advance` is the why-trail's only writer and the governor refused it, so this text never reached the
trail. **Paste it as your `--why` on the advance above** — it is written to be that argument.

> g1 CLOSED end to end. All three postconditions MET, not waived: c1 engine+gauge suites 394 passed /
> 30 subtests / real exit 0; c2 no source change; c3 the AMENDED failable artifact check.
>
> THE RED IS GENUINE and the Commander reproduced it in its own hands: `repro_431.py --all` → 24
> ASSERT OK / 0 FAIL, real exit 0, with the engine's own `CONTEXT 30% (>= hard)` line in the
> transcript — the reading was READ, not absently no-opping. Guards re-verified: `git diff --stat --
> scripts tests` EMPTY *and* `main...HEAD` EMPTY; live `spine.json`/`execute.json` md5s UNCHANGED
> across the repro run.
>
> C3 RULING, so nobody re-litigates it: the Admiral ruled **AMEND, not waive** — a waiver hides the
> bug and leaves the gate permanently unpassable for every future reviewer following that handoff; an
> amend makes the check TRUE instead of SKIPPED. Binding condition: the amended check MUST still be
> able to FAIL. It can. **ACCEPT passes, ACCEPT WITH FINDINGS passes, REJECT FAILS** — twice over,
> once on `verdict_class` and independently on `blocking_findings=0`. Root cause, recorded in the
> amendment: artifact `match` is EXACT EQUALITY per key, so it cannot express "one of", which is why
> the original hard-coded a single verdict string. Loosening it to accept any verdict would have
> converted a check that cannot pass into a check that cannot fail — the same defect wearing the other
> mask, inside the wave hunting it.
>
> THE FINDING g2–g4 MUST CARRY: reviewer PROBE 2 proves the post-attach `advance` **SUCCEEDS** and
> writes a fresh DIGEST, so **#431 is an INSTRUCTION-CONFORMANCE defect, NOT a mechanical deadlock** —
> the engine PERMITS the advance while telling the agent in the same breath not to run it. A fix
> verified as "the advance is no longer blocked" verifies something that was NEVER blocked and passes
> in both worlds. Recorded as REPLAN_INPUT discrepancy D2.
>
> STANDING TRAPS UNCHANGED: (1) DC6's observable is "did anyone BEGIN work while over the line",
> NEVER "did a handoff artifact appear" — the latter is true by construction and green in both
> worlds; (2) at/over hard, `advance --mechanical` must be REFUSED and `why_exempt` SUSPENDED, since
> `_latest_why_record` skips mechanical markers and would otherwise reproduce #431 after the fix.
>
> For `r6-fowler`, do NOT re-waive: `amend`'s **`retext-check`** op IS available on surveys and is the
> sanctioned way to fill that `<fowler-pass-record-path>` placeholder — wave 3's #465 shipped it. The
> reviewer force-waived only because `retext-check` is documented in `docs/CHECKLIST_SCHEMA.md` and
> mentioned NOWHERE in the reviewer's own SKILL.md: built but not wired, the third such instance this
> epic.
>
> NEXT: g2 — the fix itself.

---

## What I hit, and why it is worth a paragraph in the record

**I tripped at HARD on the advance that closes the gate that proves #431 — which is #431.** The
governor refused the one verb that writes the handoff, at the exact moment the handoff mattered most,
in the run whose purpose is to fix that. I did not waive it. I filed the refresh-request and stopped.

Two things that made the recovery work, both of which are known defects:

1. **`why_ref=<why-id>` is a silent no-op.** The engine prints that literal placeholder in its own
   refusal; copy-pasting it attaches with exit 0 and does **not** release HARD. The real id is not
   recoverable from `current` or from the refusal text. I read it out of `execute.json`'s raw
   `why_trail` (`w-3`). This is TC-4 / discrepancy D7, with three independent confirmations, and
   **g2(d) already plans the fix** — emit the concrete why-id.
2. **The DIGEST had to go in this file instead of the trail**, for the second time in this run and
   the third time on this spine. See "Why the DIGEST keeps landing here" below.

## Why the DIGEST keeps landing here, and what it generalizes to

`advance` is the why-trail's only writer, and it sits behind **every** postcondition of the step it
closes **and** behind the governor. So the cold-start surface is lost whenever *any* of those refuse:

- **predecessor-a:** tripped mid-`execute`, which spans all 16 gates — no `advance` available at all.
- **me, first time:** `g1-integrate` c3 was **unpassable** (the vocabulary mismatch).
- **me, second time:** the **governor** refused at 15%.

Three losses, three unrelated causes, one consequence each time. The governor case is what #467 is
fixing; the class is larger than the instance. Worth saying plainly before g2–g4 land and everyone
concludes it is solved.

---

## Done this session (all committed, tree clean)

1. **`g1-review` CLOSED** — `ACCEPT WITH FINDINGS`, 0 blocking / 8 non-blocking, from an independent
   reviewer that wrote four purpose-built probes to break the RED and failed to.
2. **`g1-integrate`** — p1 attested, gate started, repro re-run by me, c3 **amended** per the Admiral's
   ruling, evidence `e-g1-integrate-2` attached, refresh-request `e-g1-integrate-3` filed.
3. **`REPLAN_INPUT.json`** — verified, `verify_iterative_role_artifacts.py commander` **real exit 0**.
   6 wave-evidence claims, 7 classified discrepancies.
4. **`triage-candidates/g1-candidates.md`** — six candidates, **none filed**.
5. **`RESUME_OBSERVATION.md`** — second-resume section plus an addendum carrying the Admiral's
   corrected framing of the gauge mechanism. Predecessor content untouched, deliberately.

---

## Carry forward — these do not decay

- **STANDING TRAP 1:** DC6's observable is **"did anyone BEGIN work while over the line"**, never "did
  a handoff artifact appear."
- **STANDING TRAP 2:** at/over hard, `advance --mechanical` must be **refused** and `why_exempt`
  **suspended**.
- **#431 is instruction-conformance, not a lock** (reviewer PROBE 2 / D2). Do not let g2–g4 verify the
  fix as "the advance is no longer blocked."
- **`REPLAN_INPUT.json` schema gotchas:** G2 requires completed and open issue ids to be **disjoint**,
  so `completed_outcomes` **stays empty** while #467 is open; gate progress lives in `wave_evidence`.
  Also required: `appetite` and `hitl_reason` on the issue, `issue_id` (not `id`) on outcomes, and
  `blocks` may only name issues **in the wave**.
- **`retext-check` exists on surveys** (wave 3's #465) and is the sanctioned fix for a placeholder
  check command — but it is absent from the reviewer's SKILL.md, so its only user cannot find it.

## Environment invariants — reachable from NO projection, so they live here

These are in `LO-467.md` under the Admiral's `.agent-work/epic-418-redux/launch-orders/` in the
**main** repo, which the launch order fences you out of writing to. **Nothing in `spine.json current`
or `execute.json current` points at them.** Copying them here is the current stopgap; two Commanders
have now flagged it.

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

## Engine mechanics that cost me refusals

- Every mutating verb needs **`--session-id`**, including `claim`.
- `advance` needs the task **`in-progress`**: a `pending` gate needs `start` first, even though
  `current`'s `next:` line points straight at `attest`.
- **`amend --delta <file>`** takes a JSON file `{"ops":[...]}`, plus `--reason` and `--authority`.
  `retext-check` works on a **pending or in-progress** gate, never changes the check **kind**, and
  resets that condition to unsatisfied.

_Updated: 2026-08-08T11:22:00Z by commander-w4-467-c — tripped at HARD, refresh-request filed with
concrete `why_ref=w-3`, both leases released, nothing running._
