# Implementer Handoff

## Gate
`g2-implement` — issue #467, epic #418. Work area `.agent-work/issue-467-trip-semantics/`,
branch `epic-418/a2-467-trip-semantics`, worktree `C:/Programs/constellation-skills-wt/epic418-a2-467`.

## Task

Move the Trip HARD guard off the verb that **closes** a gate and onto the verbs that **begin** work
at one, and make the trip advisory read as a changed instruction rather than an alarm.

Five parts, all in this one gate:

**(a) Remove the HARD pre-`advance` guard from `dispatch`.** Today `scripts/checklist_engine.py`
line 2679-2680 calls `_trip_hard_gate(...)` when `v == "advance"`. Closing the gate you are already
in must never be governor-refused.

**(b) Add the guard to `start` AND `reopen`** — the two verbs that BEGIN work at a gate. `start`
opens a `pending` gate; `reopen` drives a `complete` gate back to `in-progress` and cascades
downstream. Refuse at/over the resolved hard threshold until a non-superseded `refresh-request`
targets that gate keyed to `_latest_why_record`'s id. **Preserve #190's identity check exactly** as
`_trip_hard_gate` implements it today (lines 1453-1461), including the `wid is None` degradation to
a gate-only match that keeps existing Trip tests green.

**(c) At/over hard, refuse an `advance` that would record NOTHING.** `--mechanical` is refused and
`why_exempt` is suspended, so the gate cannot be closed without a real running understanding.

This is **not** a refusal of the advance. It is a refusal of *silence*, and its message must name
the compliant form (`advance <id> --why "<understanding>"`). Without it, a tripped agent closes its
gate with a mechanical marker, `_latest_why_record` skips it (line 1129 drops records where
`mechanical` is true or `why is None`), the DIGEST stays pre-trip, and **#431 is reproduced after
the fix**.

**(d) Rewrite the HARD branch of the advisory** (`_trip_advisory`, line 1399) so it reads as a
CHANGED INSTRUCTION — "you did well; close this gate carrying your handoff, request a refresh, and
stop" — never as "you are unsafe". And make `_refresh_attach_hint` (line 1254) emit the **concrete
current why-record id** instead of the literal `<why-id>` placeholder.

**(e) Update `docs/CHECKLIST_SCHEMA.md`**, section "Trip — two-band context-gauge gate policy", so
it describes the shipped behaviour rather than the old refusal.

## Protected Intent

An agent that is running out of context must be able to **finish and hand off the gate it is
already inside**, and must be **told** to do that in words that read as a normal instruction. It
must not be able to **start new work** it cannot finish, and it must not be able to close its gate
**silently**.

HARD means "wrap up". It has never meant "you are unsafe", and it must not read that way after
this change.

## The trap that invalidates the obvious test — READ THIS BEFORE YOU WRITE A SINGLE TEST

**#431 is an instruction-conformance defect, not a mechanical deadlock.**

This was established on the record at g1 and re-proved twice. The g1 reviewer's PROBE 2 showed the
post-attach `advance` **succeeds** and writes a fresh DIGEST. The commander who closed g1 then
proved it a second way by being it: it ran that very `advance` at fill **0.162**, over the hard
line of 0.15, and **the engine let it through**, because a refresh-request was pending and the
guard lifts (line 1460-1461).

**The advance was never blocked.** So a test worded *"the advance succeeds after the fix"* passes
in both worlds — before the change and after it — and proves nothing.

Verify the fix on **what the agent is TOLD**, and on **whether anyone BEGAN work while over the
line**. Two concrete consequences you must honour:

- The DC6 observable is **"did anyone BEGIN work while over the line"** — never "did a handoff
  artifact appear". The latter is true by construction and green in both worlds.
- A test asserting only that a message is non-empty, or that a verb returns 0, is worthless here.
  Assert on the **content** of what the agent is told.

## Test Mode

**TDD required**, with mutation testing on every guard shipped. Each new test must be red against
today's code for the right reason before you make it green.

## Close Criteria

- (a) `dispatch` no longer calls the HARD guard on `advance`. Closing a gate is never refused for
  being over the line.
- (b) `start` and `reopen` are both guarded at/over hard, with the #190 identity check preserved.
  **`resume` is NOT guarded** — see Constraints.
- (c) At/over hard: `advance --mechanical` is refused, and `why_exempt` is suspended so an exempt
  gate still requires a `--why`. The refusal message names the compliant form.
- (d) The HARD advisory reads as a changed instruction, and `_refresh_attach_hint` emits the real
  why-record id.
- (e) `docs/CHECKLIST_SCHEMA.md`'s Trip section describes shipped behaviour.
- **THE PERMANENT DC2 GUARD** (the single most important test in this gate): the "not refused" half
  is pinned at `fill >= hard` with **NO pending refresh-request anywhere in the spine**, and
  asserts the advance completes **AND** the digest updates to the why written at that gate. That
  test is red against today's code and green only after this change, so it stands as the permanent
  regression guard against the deadlock returning. It does not depend on the disposable RED repro.
- Every mutation in the log turns its **named** test red, with counts stated.
- Full suite green against the baseline: **1793 passed, 2 skipped, 683 subtests** at `d376b786`.
  Any delta explained.

### Test naming — load-bearing, the gate cannot close without it

The `g2-integrate` closeout runs this exact command, and `pytest` exits **5** on an empty
collection, so a gate that ships tests under other names **fails to close**:

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'trip_begin or begin_work or handoff'
```

**Every new test you add must have a name matching `trip_begin`, `begin_work`, or `handoff`.** This
is not a style preference; it is the frozen closeout selector.

## Allowed Scope

- `scripts/checklist_engine.py` — `dispatch` (:2649, the chokepoint), `_trip_hard_gate` (:1439, the
  guard being moved), `_trip_advisory` (:1399), `_refresh_attach_hint` (:1254),
  `has_pending_refresh_request` (:1146), `start` (:1821), `reopen` (:2058), `advance` (:1854 and
  its why/mechanical branch at :1899).
- `tests/test_checklist_engine.py` — new tests, plus **re-aiming** existing Trip tests.
- `docs/CHECKLIST_SCHEMA.md` — Trip section only.
- `.agent-work/issue-467-trip-semantics/g2-mutation-log.md` — the mutation log.

**Existing Trip tests that pin HARD-refuses-`advance` must be re-aimed, not deleted.** State the
COUNT of tests you changed and, per test, why the change is the fix rather than collateral. A test
deleted because it became inconvenient is a stop condition.

## Specific Exclusions

- **Do NOT guard `resume`** (:1999). It restores a BLOCKED gate to the status it held before
  (`pending`/`in-progress`). For an `in-progress` prior it returns the agent to the gate it is
  already mid-way through — exactly the "closing your gate" case this design promises never to
  refuse. This was verified against the source and corrected by the cold-critic panel; it is a
  ruling, not a preference.
- **Do NOT change the global default thresholds in `gauge_reader._PROFILES`.** Production default,
  out of scope.
- **Do NOT add validation to `attach`.** A dangling `why_ref` already fails CLOSED — the identity
  predicate returns False and the agent stays guarded — so a refusal there is unasked scope on the
  highest-risk gate. Three cold critics converged on dropping it.
- Do not build a mid-gate handoff channel (see Authority, triage candidate).

## Constraints

- **The bands ride the CLI boundary in `dispatch`.** `start`, `reopen` and `advance` stay PURE —
  their return values must not change, so the existing exact-equality tests keep passing. Do not
  move the seam; move which chokepoint on it the guard hangs from. Note the existing comment at
  :2681-2683: a refused verb must raise **before** the liveness stamp, so a refusal never
  refreshes the lease and never mutates state. Preserve that ordering for the new guard.
- **FIXED, not renegotiable:** a missing or failed reading never forces a handoff; HARD means "wrap
  up", never "you are unsafe"; the reading is PUSHED by the engine, never fetched by the agent.
- **Fail-safe on a None reading must survive.** `_trip_hard_gate` no-ops on `reading is None`
  (:1448-1449) and on surveys (:1445). Both bands stay empty for surveys and no-op on a missing
  reading, at the new guard sites too.
- `refresh-request` payloads stay **POINTERS ONLY**: `{seam, why_ref}`. No copies of state.
- **MUTATION-TEST EVERY GUARD YOU SHIP.** For each new test: break the exact source branch it
  defends, and record (i) the branch you broke, (ii) that **THE NAMED TEST** failed, and (iii) the
  **total count** of tests that failed. A mutation that breaks forty unrelated tests does not
  demonstrate that this test defends that branch — it demonstrates the opposite. Log to
  `.agent-work/issue-467-trip-semantics/g2-mutation-log.md`.

## Map Anchors (inbound)

- **Structural:** `scripts/checklist_engine.py` — `dispatch` (:2649), `_trip_hard_gate` (:1439),
  `_trip_advisory` (:1399), `_refresh_attach_hint` (:1254), `has_pending_refresh_request` (:1146),
  `start` (:1821), `reopen` (:2058), `resume` (:1999), `advance` (:1854, why/mechanical branch
  :1899), `_latest_why_record` (:1121). `docs/CHECKLIST_SCHEMA.md` section "Trip — two-band
  context-gauge gate policy" — the structural record this change makes stale.
- **Capability:** Trip two-band gate policy, HARD band — enforcement point moves; SOFT unchanged.
  why-capture / reach-up — unchanged in shape, reachable at a trip for the first time.
- **Constraints/assumptions:** `constraint:fail-safe-on-no-reading` — both bands no-op on a None
  reading. `constraint:gated-only` — both bands are empty for surveys.
  `constraint:gate-boundaries-only` — no mid-gate check. `constraint:pure-verbs` — verb return
  strings unchanged.
- **Decision anchors:**
  - `decision:hard-guards-begin-not-close` — HARD refuses `start` and `reopen`, never `advance`;
    closing the gate you are in is the handoff. Converged from a 3-candidate design-it-twice panel,
    then corrected by the cold-critic panel (resume dropped, reopen added). Recorded in
    `DIT_CONVERGENCE.md` and `CRITIC_TRIAGE.md`.
    `@grade: settled/measured · leans g2-implement,g2-review,g4-implement`
  - `decision:no-silent-close-at-hard` — at/over hard, `--mechanical` is refused and `why_exempt`
    is suspended. Without it the tripped agent writes a mechanical marker, `_latest_why_record`
    skips it, and the DIGEST stays pre-trip — #431 reproduced after the fix. Found by the
    intent-fit critic.
    `@grade: settled/measured · leans g2-implement`
- **Evidence expectations:** `claim:dc2-two-way` — an advance carrying a handoff is not refused
  at/over hard with no pending request; beginning new work at/over hard IS refused. Both directions
  tested, and the first is the permanent deadlock guard. `claim:dc3-digest-fresh` — after the
  handoff-carrying advance, the digest names the understanding written AT the tripping gate, not
  the one before it.
- **Map confidence flags:** none.

## Deliverable Path Check

All four deliverables are **Committed**. `git check-ignore <path>` run for each before dispatch;
every one exited **1** (not ignored). Note `.agent-work/` is tracked in this repo — the mutation log
belongs in the diff.

- **Committed** — `scripts/checklist_engine.py` (`git check-ignore` exit 1)
- **Committed** — `tests/test_checklist_engine.py` (`git check-ignore` exit 1)
- **Committed** — `docs/CHECKLIST_SCHEMA.md` (`git check-ignore` exit 1)
- **Committed** — `.agent-work/issue-467-trip-semantics/g2-mutation-log.md` (`git check-ignore`
  exit 1). This file is **new**: it is untracked until staged, so `git diff` shows three files and
  the fourth appears in `git status`.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. **The permanent DC2 guard test**, shown red against unmodified source and green after. Paste
   both runs. Show explicitly that the fixture has `fill >= hard` and **no** pending
   refresh-request anywhere in the spine — if it has one, the test passes on both sides of the fix
   and is worthless.
2. **The mutation log**, one entry per new guard: branch broken, the NAMED test that went red, and
   the TOTAL failure count for that mutation.
3. **The `--mechanical`-at-hard refusal**, with the exact refusal message quoted, and a test
   proving the digest cannot go stale after the fix.
4. **`reopen` guarded / `resume` NOT guarded**, both directions tested.
5. **The count of re-aimed existing tests**, with a per-test reason.

**Confirmatory — a spot-check suffices:**

6. Fail-safe on a `None` reading survives at the new guard sites.
7. Verb return strings unchanged (the existing exact-equality tests staying green is the proof).
8. `docs/CHECKLIST_SCHEMA.md` describes shipped behaviour.

Quote the **exact** expected strings your tests assert on, so they assert equality rather than a
substring guess. If you report any failure distribution, derive it mechanically
(`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), never from a glance at the tail.

## Wiring Grep

Required. One command naming every symbol this slice adds, showing for each a call site outside its
own definition and outside any `--self-test` path. State the count of call sites found. **Zero
external call sites is a stop condition** — a guard function that only its own definition and its
own test reference is shipped-inert, which is precisely the failure mode this gate exists to fix.

```bash
grep -rn "<each new symbol>" --include=*.py . | grep -v "def <symbol>" | grep -v self_test
```

## Verification Commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'trip_begin or begin_work or handoff'
```

The third is the frozen `g2-integrate` closeout selector. Run it yourself and confirm it collects
your new tests — a non-zero collection is the whole point.

## Suggested Model Tier

**Stronger.** This gate changes a governor that every agent in the constellation runs under, the
obvious test for it passes in both worlds, and the failure mode is a silent one.

## Authority

Already decided; do not re-open:

- `decision:hard-guards-begin-not-close` and `decision:no-silent-close-at-hard`, both
  `settled/measured`, from the design-it-twice panel as corrected by the cold critics.
- `resume` is not guarded; `reopen` is.
- No validation added to `attach`; no change to `_PROFILES`.

**You must not decide alone:** any change to which verbs are guarded, any loosening of the
`--mechanical` refusal, any change to the pure-verb seam, or deleting rather than re-aiming an
existing test.

**TRIAGE CANDIDATE — raise it, do not build it:** whether the gate that trips with UNMET
postconditions needs a mid-gate handoff channel. `block --next` exists but `current` does not render
its text. Carries no grade. Report it in your out-of-scope observations.

## Stop Conditions

Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, a decision outside the given authority is needed, or the permanent DC2
guard cannot be made red-then-green for the right reason.

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this
handoff or the workflow made the work harder than it needed to be).

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g2-implementer-result.md`.
