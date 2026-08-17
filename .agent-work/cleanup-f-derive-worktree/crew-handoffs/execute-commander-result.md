# Commander result — `cleanup-f-derive-worktree` (#609 lane F), leg 5

## Assigned

`LAUNCH_ORDER-5.md` — the closeout. Close `g3` on the APPROVE already attached,
skip `g4` and `g5` on the recorded rulings, then reconcile → triage → review →
feedback → archive, parking at `archive` without merging.

## Return status

`partial` — **parked at a clean gate boundary, not blocked and not failed.**
`execute.json` is terminal, the spine's `execute` step is closed, and
`reconcile`'s whole substance is done, committed and attested. The engine's
context governor then refused to **begin** `reconcile` (`start` is hard-guarded;
fill 0.155 against a hard line of 0.15), so I filed the refresh-request it named
(`e-reconcile-1`, `seam=reconcile`, `why_ref=w-5`) and parked. **The lease is
deliberately NOT released** — the run is not done.

## What this leg completed

**`g3` is closed.** `g3-review` advanced on review 5 — APPROVE, 0 findings, 8 of
8 criteria, no blockers (`crew-handoffs/g3-reviewer-rework4-result.md`), which
`ADMIRAL_RULING-4` made the last round. `g3-integrate` closed with every
load-bearing number re-measured **by me at this gate**, not cited from leg 4:

| arm | result |
|---|---|
| `main` at `17c2cee5`, isolated clone named `constellation-skills` | **3171 passed / 7 skipped / 0 failed** |
| shipped tree, engine's own quiet `c2` run | **3192 passed / 5 skipped / 0 failed** |
| targeted class `OwnershipIsBindingKeyNotWorktree` | **23 passed**, where the same selector exits 5 on the pre-gate arm |

**Failure-set difference: empty against empty.** The 7→5 skip delta predates the
gate — the pre-gate arm `53c89ba1` already measured 5. Windows path handling is
stated explicitly in the `c4` attestation: everything compares through
`_same_path` (`normcase` + `normpath`, `True` on exception), both call sites fold
case identically, and because `normcase` is the identity on this host the case
expectation is **constructed**, not measured.

**`g4` is skipped as WITHDRAWN** (R2), not deferred — nothing re-homes from it.
The pre-ruling it implemented was itself the defect; the ruled behaviour is
already shipped, and I verified `_worktree_from_spine` returns `None` for an
unowned path by reading the function at the skip rather than citing g1.

**`g5` is skipped as RE-HOMED** (R3) — #315 stays open and moves to #610's wave.

**`reconcile` is done and attested, awaiting only a fresh agent's `start`.**

## Reconcile: four sites named, a fifth found

All prose. **No executable line moved** — the diff's only non-comment changes are
docstrings — and the suite is **3192 / 5 / 0**, identical to `g3`'s close.
Committed at `684502ab`.

1. `scripts/hooks/spine_rail.py` and 2. `tests/test_spine_rail.py` cited the
   door's dead import-time contract `SPINE = Path(os.environ["SPINE_FILE"]).resolve()`.
   Current truth is `mcp_spine_server._spine_from_env`, which strips the value,
   collapses unset/empty/whitespace into `None`, and leaves readability to
   `_unbound_refusal` per call (#603/#604). **The test-file copy was wrapped
   across two lines** — `tc8`'s hazard, and why every citation here is by string.
3. `tests/test_explorer_templates.py` and 4. `tests/test_mcp_door_engine_cwd.py`
   asserted the engine still reads its ambient cwd and still enforces the
   `origin.worktree` comparison (`tc10`). Repaired in the past tense, each citing
   the 2026-08-15 worktree-identity ruling and saying plainly that **this lane
   supersedes it**.

**The fifth site is the finding.** Grepping the *claim* rather than the named
files turned up `scripts/init_work_area.py`'s `instantiate_spine` docstring
saying "`checklist_engine` compares `origin.worktree` against its own cwd on
every guarded verb" — falsified by this lane's own `g2`, in a file nobody had
listed. Repaired here under the rule that put `tc10` in this lane: **the change
that falsifies a claim owns the repair.** Recorded as `D28`. It is one file
beyond the order's list of three, prose only, and I am naming it rather than
burying it.

**`docs/CHECKLIST_SCHEMA.md` was already right** — `g2` wrote it, and it already
carries the supersession language. Reconcile here was bringing the *code prose*
into line with a design doc that was already current, not the reverse.

**One claim I refused to take on trust.** The repaired explorer comment says the
`cwd` no longer decides anything; rather than infer that from the deletion, I
measured it — `claim` from `/tmp` and `start` from `/` against a spine stamped
`origin.worktree: /totally/elsewhere` both return `rc=0` — and the measurement is
quoted in the comment it justifies.

## Why this leg stopped

`start reconcile` was refused: *"context at 15% is at/over the hard limit … finish
and close the gate you are already in, then request a refresh so a fresh agent
starts this one."* The shipped defaults are soft `0.08` / hard `0.15` and
`start`/`reopen` are the hard-guarded verbs. `attest` is not guarded, so
`reconcile.c1` carries its full evidence already; `advance` refused only because
a `pending` gate must be `in-progress`. **A fresh agent's first three commands
close it.**

Recorded as `D27`, because it is a planning fact rather than a complaint: at a
hard line of `0.15`, with re-orientation alone costing a leg roughly a tenth of
its window, **five remaining steps is closer to five dispatches than to one.**
Whether the tail steps deserve a larger headroom reserve, or whether close-only
legs should be exempt the way `advance` already is, is yours and not this lane's.

## What the next leg owes

`STATE_NOTE.md` is current and carries the detail. In order:

1. **`reconcile`** — `start`, then `advance`. `c1` is attested with its full
   evidence and the work is committed at `684502ab`. Nothing to do but close it.
2. **`triage`** — `tc1`–`tc12` in `execute.json` plus what the `g3` crews raised.
   Under `ADMIRAL_RULING-4`, **`tc1` (the SessionStart scan-bind) and the
   cross-session widening (B7) go to #610's wave as ONE package**, carrying the
   *question* — what the scan-bind is for when nobody has claimed the spine — not
   just the symptom. **Beware the id collision:** `execute.json`'s `tc1` is the
   empty `map/ids.jsonl`; the launch order's `tc1` is the scan-bind. They are
   different findings with the same name, which is `tc7`'s defect biting the
   closeout. Route by content, never by id.
3. **`review`**, **`feedback`**, **`archive`**. Park at `archive`, **do not
   merge**.

**`archive`'s `c2b` wants an OPEN or MERGED PR and there is none** — no upstream
is configured for this branch. Opening one is outward publication, which
`LAUNCH_ORDER-5` reserves to you ("Publication is mine"). **I did not push and
did not open a PR.** That is the one place where the frozen order and the spine's
own postcondition disagree, and it is yours to settle: authorize the push and PR,
or waive `c2b` with the fence as the reason.

## Feedback material, harvested for the `feedback` step

- **When a gate removes a guard, enumerate what the guard was incidentally
  preventing, not only what it was wrongly deciding.** Four of five `g3` reviews
  trace to nobody doing this.
- **Build your own instrument before you run theirs.** Every instrument on `g3`
  developed a shelf-life defect.
- **Cite content that cannot move under you** — stale line numbers and amended
  shas are one defect in two forms.
- **Measure the claim family, not the symbol, and not the file list.** This leg
  paid for that lesson once more, and got the fifth site for it.
- **An instrument can measure its observer.** The containment test failed for me
  and only for me: I polled the run ~15 times, every tool call fires the gauge
  chain, and the test was snapshotting the `.agent-work/` I was writing to. The
  identical command, run quiet by the engine, was green. That is `tc11` with a
  sharper cause than "a crew happened to write" (`D23`).

## Housekeeping

- **Lease held** at `commander-cleanup-f-derive-worktree`, re-claimed without
  `--force`. Not released — the run is not done.
- **`REPLAN_INPUT.json` verifies.** `g3` folded in as a completed outcome, the
  open-issue set is now empty, 23 wave-evidence rows, `D0`–`D28`. Nothing
  auto-filed.
- **`crew-runs.json` committed at every gate close**, per the #617 mitigation.
- **`recover_crews.py` run before this leg.** No crew dispatched — leg 5 needed
  none; the only ACTIVE entry is this commander leg, and legs 1–4 are my own
  parked predecessors, not crews to recover.
- **`main` has not moved** — still `17c2cee5`, re-measured here.
