# Review: issue #183 (Refresh reach-up flow, Module 4, doctrine wiring)

## VERDICT: APPROVE

On doctrine-faithfulness, drill-reproducibility, and file-fence grounds. The qualitative "did the fresh
agent resume without re-deriving?" judgment is explicitly NOT rendered here — that is the human's call, and
the drill's own Human-verdict block is confirmed blank (see item 2).

## Isolation

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-183-rev
worktree OK: in C:/Programs/constellation-wt-183-rev
```

## Item 1 — Doctrine faithfulness

Read all 8 edited files against the launch order's frozen build spec
(`.agent-work/epic-178/crew-handoffs/183-launch-order.md`):

- **Uniform reach-up mechanism** (`skills/_shared/global-everyone.md` new `## Reach-up: refresh, not
  re-derive`, lines 68–107): correctly encodes write-refresh-request-via-`attach`-then-go-idle, invoker
  reads via `current`, relaunches a fresh agent cold-starting from `DIGEST:` + `ACTIVE <gate> —
  <imperative>` alone. No separate handoff document is described anywhere — the text is explicit that
  "no separate handoff document is ever written or read for this."
- **Job-file-not-agent-file** (same file, lines 91–96): stated plainly — the engine work file belongs to
  the job, is reused (never copied/recreated) across agent swaps, and grounds the append-only `why_trail`.
- **Symmetric recovery**: `global-everyone.md` lines 98–102 and `fleet-doctrine.md`'s new paragraph
  (lines 107–115) both state crash and intentional refresh read the identical `current`, differing only in
  whether the `REFRESH REQUESTED:` line is present — matches the merged #179 primitives and my own probe
  (item 3 below).
- **Uniform across every tier**: `global-everyone.md` line 98 states it outright ("crew reaching up to
  Commander, Commander reaching up to Admiral, Admiral reaching up to the human"), and this is echoed
  concretely in each tier file (`commander-core.md` new bullet, `admiral/SKILL.md` new bullet,
  `implementer/SKILL.md` new paragraph, `reviewer/SKILL.md` new paragraph).

**CUT items confirmed genuinely absent.** Searched the full diff for the three items the launch order
named out-of-scope:

```
$ git diff e2b8005...HEAD | grep -iE "SF4|pi.self.refresh|pre-emptive.handoff|preemptive.handoff|crew-edge"
(no output, exit 1)
```

No crew-edge extra robustness (SF4), no pi self-refresh adapter, no pre-emptive-handoff-at-specific-gates
anywhere in the changed text. Confirmed absent, not just unmentioned by omission — the diff has no trace of
any of the three.

## Item 2 — Not self-certified (HITL)

Read `docs/superpowers/drills/symmetric-recovery-refresh.md` lines 97–104 in full:

```
## Human verdict

*(left blank — the human or their delegated reviewer records the judgment here; the agent that built this
drill does not self-certify it, per the launch order for #183)*

- Resumed cleanly / re-derived: ****\_\_\_****
- Symmetry held: ****\_\_\_****
- Notes:
```

Confirmed genuinely blank — no PASS/FAIL, no filled-in verdict text. The implementer's result artifact
(`183-result.md`) also explicitly notes this differs from the repo's two prior self-certifying drills
(`gh-body-multiline-windows.md`, `dogfood-context-paths-absent.md`); that framing is accurate — I did not
find any pre-filled judgment.

## Item 3 — Drill reproducibility

`diff` between the two fixtures:

```
$ diff docs/examples/symmetric-recovery-refresh.json docs/examples/symmetric-recovery-crash.json
75,86c75
<       "evidence": [
<         {
<           "id": "e-g2-implement-helper-1",
<           "type": "refresh-request",
<           "payload": {
<             "seam": "g2-implement-helper",
<             "why_ref": "w-1"
<           },
<           "produced_by": "engine",
<           "ts": ""
<         }
<       ],
---
>       "evidence": [],
```

Exactly one JSON evidence object differs — the attached `refresh-request` — confirming the drill doc's
claim. `current` on both:

```
$ py scripts/checklist_engine.py --file docs/examples/symmetric-recovery-refresh.json current
ACTIVE g2-implement-helper [in-progress] — Implement the retry helper per the chosen backoff strategy.
DIGEST: chose exponential backoff with jitter (cap 30s) over fixed-delay retry: the upstream API only sometimes returns Retry-After on 429, and fixed-delay caused synchronized thundering-herd reconnects across workers on the days it did not
REFRESH REQUESTED: g2-implement-helper (why_ref w-1)

RAIL: The finish is a sequence, not an announcement. Final `advance` first, then `release` — the journal, not your prose, is the proof.

$ py scripts/checklist_engine.py --file docs/examples/symmetric-recovery-crash.json current
ACTIVE g2-implement-helper [in-progress] — Implement the retry helper per the chosen backoff strategy.
DIGEST: chose exponential backoff with jitter (cap 30s) over fixed-delay retry: the upstream API only sometimes returns Retry-After on 429, and fixed-delay caused synchronized thundering-herd reconnects across workers on the days it did not

RAIL: The finish is a sequence, not an announcement. Final `advance` first, then `release` — the journal, not your prose, is the proof.
```

Matches the drill doc's claim exactly: `DIGEST:` present in both, `REFRESH REQUESTED:` present only in the
refresh fixture, nothing else differs. Symmetric-recovery claim holds.

**Minor nit (LOW severity, not blocking):** the drill doc (`docs/superpowers/drills/symmetric-recovery-refresh.md:39-56`)
calls its pasted transcript "verbatim, reproduced from the checked-in fixtures" but omits the trailing
`RAIL:` line that real engine output includes (I confirmed the RAIL line appears on every live run above).
Cosmetic only — it doesn't change the acceptance signal (DIGEST/REFRESH lines match exactly), but "verbatim"
overclaims slightly. Not blocking.

## Item 4 — Fulfil-semantics claim

Advanced the tripped gate in a scratch copy of the refresh fixture (deleted after the check, not committed):

```
$ py scripts/checklist_engine.py --file <scratch-copy> advance g2-implement-helper --why "implemented retry helper using the exponential backoff with jitter (cap 30s) decided above"
g2-implement-helper -> complete

$ py scripts/checklist_engine.py --file <scratch-copy> current
DONE: no open items.
DIGEST: implemented retry helper using the exponential backoff with jitter (cap 30s) decided above
```

Confirmed: no `REFRESH REQUESTED:` line after advancing — the claim that completing the gate the request
named clears it with zero evidence mutation is verified true, not just asserted.

## Item 5 — Fence + no regression

```
$ git diff e2b8005...HEAD --stat
 docs/examples/symmetric-recovery-crash.json           |  92 +++++
 docs/examples/symmetric-recovery-refresh.json          | 103 ++++++
 docs/superpowers/drills/symmetric-recovery-refresh.md  | 104 +++++
 skills/_shared/global-everyone.md                      |  41 +++
 skills/_shared/global-orchestrator.md                  |  10 ++
 skills/admiral/SKILL.md                                |   1 +
 skills/admiral/references/fleet-doctrine.md             |  10 ++
 skills/commander/references/commander-core.md          |   3 +-
 skills/implementer/SKILL.md                             |   2 +
 skills/reviewer/SKILL.md                                |   2 +
 skills/workbench/references/checklist-engine.md        |  35 +++
 11 files changed, 402 insertions(+), 1 deletion(-)
```

Only doctrine `.md` + `docs/` fixtures/drill changed. `scripts/checklist_engine.py` diff is 0 lines
(untouched); no gauge module in the changed-file list.

```
$ py -m pytest tests/test_checklist_engine.py -q
166 passed, 18 subtests passed in 11.29s
```

Still 166 passed — confirms the doctrine-only change breaks nothing.

## Item 6 — Engine-gap floats (for Admiral triage)

**Float 1 — DIGEST/REFRESH REQUESTED display is `gated`-only: CONFIRMED REAL.**

Code inspection (`scripts/checklist_engine.py:814-829`, `_why_suffix`): the function returns `""`
immediately if `cl.get("type") != GATED` (line 819-820), before any digest/refresh logic runs. Empirically
probed with a minimal standalone `survey` checklist:

```
$ py scripts/checklist_engine.py --file <survey-test>.json current
ACTIVE r1-check [in-progress] — Check something and record pass/fail.
$ py scripts/checklist_engine.py --file <survey-test>.json attach r1-check --type refresh-request --field seam=r1-check --field why_ref=none
attached e-r1-check-1 (refresh-request) to r1-check
$ py scripts/checklist_engine.py --file <survey-test>.json current
ACTIVE r1-check [in-progress] — Check something and record pass/fail.
```

`current` is byte-identical before and after attaching the refresh-request — no DIGEST, no REFRESH
REQUESTED line, confirming the doctrine's own claim (`checklist-engine.md:105-112`,
`global-everyone.md:104-107`) that this is a real, verified gap, not a hypothetical caveat. Since the
frozen spec explicitly names reviewer (a survey-driving role) as a reach-up participant, this is a genuine
interface gap against #179 as merged that will bite the first time a reviewer trips — the `reviewer/SKILL.md`
workaround (read the survey JSON's evidence array directly) is a correct stopgap but not a substitute for
extending `_why_suffix`.

**Float 2 — `has_pending_refresh_request` is `why_ref`-blind/boolean-per-gate: CONFIRMED REAL.**

Code inspection (`scripts/checklist_engine.py:792-811`): the predicate loops evidence looking only for
`type == "refresh-request"`, `not superseded`, and `payload.seam == gate` — no comparison against a specific
`why_ref` or count of how many are pending. Empirically probed: attached a **second**, distinct
refresh-request (different `why_ref`) to the already-tripped `g2-implement-helper` gate in a scratch copy of
the refresh fixture:

```
$ py scripts/checklist_engine.py --file <scratch> attach g2-implement-helper --type refresh-request --field seam=g2-implement-helper --field why_ref=w-2-fake
attached e-g2-implement-helper-2 (refresh-request) to g2-implement-helper
$ py scripts/checklist_engine.py --file <scratch> current
ACTIVE g2-implement-helper [in-progress] — Implement the retry helper per the chosen backoff strategy.
DIGEST: ...
REFRESH REQUESTED: g2-implement-helper (why_ref w-1)
```

The second request is silently absorbed: `current` still shows only the first request's `why_ref` (`w-1`);
the raw evidence array does hold both objects, but nothing in `current` or the predicate surfaces or
distinguishes the second trip. This confirms the doctrine's own characterization (`checklist-engine.md:100-104`):
a second, unrelated trip on the same still-open gate is silently waved through on the first request's
coattails — exactly the collision risk the launch order asked the implementer to watch for against #182's
HARD-band use of this predicate. Real, and worth an Admiral fast-follow (predicate needs a `why_ref`-aware
identity check or a count, not a bare boolean).

Both floats are genuine, verified gaps in the *merged* engine (`checklist_engine.py`), correctly identified
as out of #183's fenced scope (doctrine-only) rather than fixed here.

## Findings summary

| Severity | File:line | Finding |
|---|---|---|
| LOW | `docs/superpowers/drills/symmetric-recovery-refresh.md:39-56` | "Run it" transcript is labeled "verbatim" but omits the trailing `RAIL:` line real engine output includes. Cosmetic only — does not affect the DIGEST/REFRESH-line acceptance signal. Not blocking. |

No other findings. No BLOCK-severity issues found; nothing here requires a minimal fix before merge.

## Cleanup note

All scratch probe files (`.scratch-review/`, temp fixture copies) used for items 4 and 6 were created and
removed inside my worktree during the review; none were committed.
