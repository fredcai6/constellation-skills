# Review Result — `epic-568-510` g2-engine (independent falsifier)

Session `constellation/epic-568-510/g2-engine/reviewer/attempt-1` · parent
`constellation/epic-568-510/g3-engine/commander/attempt-1`.
Survey driven through the engine at
`.agent-work/epic-568-510/g2-engine-review/review.json` (14 items, all visited,
consolidated). Worktree `/home/tommy/projects/constellation-skills/.worktrees/epic-568-510`,
branch `epic-568/510-hard-advisory`, base `23ed6b70`. Nothing committed; I stayed
fenced from push, PR and merge.

## Assigned Gate

`g2-engine` — permit the `start` the HARD advisory instructs.

## Result

**APPROVE** (with two recorded `fail` checks overridden and routed as triage
candidates — see *Blockers* and *Out-of-scope observations*).

## Handoff compliance

The change does what was ruled. I verified the authority at its source rather
than from the handoff, and this is worth naming because the artifacts disagree:

- The handoff says the human ruled "via the Admiral's frozen launch order".
- `.agent-work/epic-568-510/LAUNCH_ORDER.md` — the launch order *inside this
  worktree* — is the **wave-1** order, and its pre-rulings say the opposite:
  `decision:no-runtime-expansion` — "do not modify trip guards, defaults, verbs,
  or schema", `@grade: settled/human`. `REPLAN_INPUT.json` carries the same hard
  constraint.
- The governing order is `.agent-work/epic-568/LAUNCH_ORDER-wave2-510-engine.md`,
  **outside the worktree**, issued 2026-08-14. Its pre-ruling 1,
  `decision:fix-the-engine-not-the-prose`, settled by the human: "The advisory's
  instruction stands; the engine changes so that instruction becomes true. Do not
  resolve this by editing advisory wording." Base commit `23ed6b70` matches, and
  `spine.json`'s `resume_reason` records the same ruling clearing the float.

The ruling is executed literally: `_trip_advisory`'s wording is byte-for-byte
untouched and the engine yields instead.

## Scope drift

None. Changed files are exactly the three the wave-2 order owns:
`scripts/checklist_engine.py`, `tests/test_checklist_engine.py`, `map/INDEX.md`
(`map/*` is gitignored except `INDEX.md` and `ids.jsonl`; `tests/test_code_map.py`
148 passed, so the map is fresh). No stop condition fired — and that is
*measured*, not inspected: the 1152-state differential sweep below found zero
changes to `advance` semantics, gate lifecycle or production defaults.

## Evidence verdict

All required evidence produced, and each claim independently reproduced.

**Cache-clean full suite** (`__pycache__` cleared immediately before every run,
per pre-ruling 5):

```
2997 passed, 7 skipped, 1129 subtests passed in 123.28s
```

**Assertion-kind census** (AST over `tests/test_checklist_engine.py`,
`23ed6b70` → working tree):

| kind | before | after | Δ |
|---|---|---|---|
| assertEqual | 614 | 632 | +18 |
| assertIn | 237 | 238 | +1 |
| assertNotIn | 78 | 82 | +4 |
| assertRaises | 100 | 103 | +3 |
| assertTrue / assertFalse / assertIs / assertIsNone / assertIsNotNone / assertIsInstance / assertGreater / assertGreaterEqual / assertLess / assertNotEqual / assertAlmostEqual / assertNotAlmostEqual | — | — | 0 |

Test methods 441 → 449: **0 removed, 8 added**. Skip/xfail markers 2 → 2 (none
added). Whole-string advisory equality assertions 8 → 10, and every re-pinned one
is still `assertEqual(self._advisory(...), <full expected string>)` — none
downgraded to `assertIn`. Only 3 of the 5 re-aimed tests changed their assertion
mix, and two of those *added* an assertion.

One assertion was removed anywhere in the file: `assertTrue(msg.endswith("g2 ->
in-progress"))` in
`test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line`,
because that test now exercises `reopen` rather than `start`. The state assertion
it guarded (`assertEqual` on the gate's resulting status) is retained and is the
stronger of the two, and the test still pins its guarantee at 5 `assertEqual`.
Recorded as an observation, not a weakening.

**Red/green.** I reverted **only** `scripts/checklist_engine.py` (copied the
after-version aside, `git checkout HEAD -- <file>`, restored byte-identically —
the final `git diff` matches the pre-experiment diffstat exactly):

- new class alone → `3 failed, 5 passed`, failing with
  `AssertionError: 'begin-released' != 'begin-instructed'` and
  `'TRIP LEDGER:' unexpectedly found in ...`. Behaviour failures carrying real
  rendered output — **not** import or fixture errors. The 5 that stay green are
  the narrowness controls, which is correct: they pin behaviour the change does
  not alter.
- whole engine test file against the reverted engine → `6 failed, 444 passed`
  (3 new + 3 re-aimed expectations), so the re-aims are behaviour-driven.
- restored → `450 passed`.
- honesty baseline: `23ed6b70` with **both** files at HEAD fails exactly 1 test,
  the documented deliberately-failing one. This change also closes that red.

**My own reproduction** (`.agent-work/epic-568-510/g2-engine-review/reviewer_probe.py`,
written by me): reproduces the change in-process *and* through the real CLI — the
persisted `trip_ledger` on disk reads `begin-instructed` and the next `current`
no longer prints `TRIP LEDGER:` / `TRIP HISTORY`.

## Claims, one by one

**1. Confined to that one branch — could not falsify.** The engine diff is 6
executable lines inside the already-existing release branch (one boolean, one
conditional expression, one changed argument to the existing `_append_trip_entry`
call), plus a 24-line comment and two docstring edits. Both compliance selectors
are untouched and still filter on `("begin-refused", "begin-released")`, which is
precisely why a third outcome needs no selector change.

**3 + 4. The exemption is narrow, and `begin-released` is still branded — could
not falsify, and this is the strongest evidence in the review.** Two independent
sweeps over the same 1152-state grid (verb × target gate × active-gate status ×
refresh-request presence/keying × `why_exempt` × gauge band × checklist type):

- *Implication sweep* — compute the advisory the agent would have seen **before**
  dispatching the verb, then assert `outcome == "begin-instructed"` ⟹ the advisory
  literally contained ``begin THIS guarded gate (`start <that same target>`)``.
  **Zero counterexamples.** Every exempted state is exactly
  `(start, the active gate, pending, gated, over-hard)` with a matching pending
  request — nothing else.
- *Differential sweep OLD (`23ed6b70`) vs NEW* — **zero** states differ in whether
  the verb raised, how many ledger entries were appended, or the three gates'
  resulting statuses. Exactly **3** states relabel `begin-released` →
  `begin-instructed`, and those same 3 are the only ones whose compliance
  selectors change. The change cannot widen *who is released*; it only changes
  *how one instructed subset is labelled*.

Every named probe came back negative: `reopen` never exempted; `start` at a
non-active gate never exempted; `start` at an in-progress or blocked gate never
exempted; a survey checklist writes no ledger at all; an absent gauge writes
nothing; a well-formed reading that predates the session's claim writes nothing.
`begin-released` remains reachable and branded (`reopen` over the line, verified
in my own probe: `TRIP HISTORY` still renders), and `begin-refused` still raises
and still populates the live selector.

One probe row I had to chase down and will state plainly: a `why_exempt` gate
(live why id `None`) holding a refresh-request with a **stale** `why_ref` **is**
exempted, because `has_pending_refresh_request` degrades to a gate-only match when
`wid is None`. That degradation is documented pre-existing #190 behaviour shared
by *both* sites, so the advisory instructs that `start` too and the implication
holds — and the OLD engine already **released** that same begin, so this change
relabels it rather than newly permitting it.

**2. No test weakened — could not falsify.** Census above.

**5. Red/green real — could not falsify.** Above.

**6. Nothing else depends on the old semantics — PARTIALLY FALSIFIED.** See
*Blockers*. Repo-wide grep hits only: the engine (26), its tests (137), derived
and gitignored map artifacts, `docs/CHECKLIST_SCHEMA.md` (21), and one unrelated
prose match in a fixture. `skills/` and the rest of `docs/` are clean. The
handoff's caveat checks out: **no test asserts on that doc's trip content** — the
only test that parses `docs/CHECKLIST_SCHEMA.md` reads its `## Task` field table
(#476); the other two references are docstring prose.

**7. AST call-graph pin holds — could not falsify.** Verified with my own AST
walk, not by trusting the repo's test: `_append_trip_entry` has exactly one caller
(`_trip_hard_gate`), and exactly three functions name `trip_ledger`
(`_append_trip_entry`, `begin_over_line_records`,
`begin_over_line_records_historical`). The repo's own pin is green in the full
suite.

## Code/doc quality

Minimal and in-idiom. Full Fowler pass recorded at
`.agent-work/epic-568-510/FOWLER_PASS.json`; `scripts/verify_fowler_pass.py`
exits 0 (12 smells, 1 flagged, 7 overridden with logged standard + reason, 4
absent).

The one **flagged** smell is worth the Commander's attention: the guard's
`instructed` predicate duplicates the state condition `_trip_advisory` renders its
instruction from — the same test written twice, ~200 lines apart, in two functions
with no call relationship. They agree today (proven above), and the new positive
control `test_the_advisory_really_does_instruct_this_start` pins one fixture, but
nothing enforces the invariant, so a later edit to the advisory's pending branch
could silently widen the exemption. Out of scope here under pre-ruling 2; routed
as triage candidate `tc2`.

Two overrides rest on a fact I confirmed empirically rather than assumed: the trip
guard runs **before** `_run_verb` validates the id, so the defensive
`cl.get("tasks", {}).get(iid, {}).get("status")` chain is load-bearing — the
module's own `task()` accessor raises `no such item` and would surface the wrong
error from the wrong place.

## Map impact verdict

No implementer `Map Impact` notes exist to check — there is no g2 implementer
handoff or result artifact in `crew-handoffs/`, and the lane's named findings file
`.agent-work/epic-568-510/FINDINGS-wave2-engine.md` (wave-2 order, *Data
Locations*) was never written. I am not blocking on that: the diff is a 6-line
local behaviour change with no structural, capability or event impact, and the
wave-2 order addresses those artifacts to the Commander, whose result step comes
after this review. Flagging it so it is not lost — pre-ruling 3's enumeration and
the return-shape report are still owed.

The derived map is fresh (`map/INDEX.md` regenerated; `tests/test_code_map.py`
148 passed).

## Reconciliation check

The engine now diverges from its own recorded contract.
`docs/CHECKLIST_SCHEMA.md` is the document agents drive this engine from, and its
trip-ledger section still closes the outcome vocabulary at two values — line 448
`outcome | begin-refused or begin-released`, elaborated at 457–465, with the
selector sections at 474+ and 515+ describing the two-value filter. A third
outcome is now written to real spines, so a reader of the contract would classify
a `begin-instructed` entry as malformed.

Not editing that file is **correct** — it is outside this lane's File Ownership
and the wave-2 order's Stop Conditions require reporting rather than reaching.

## Blockers

Recorded as `fail` on `r5-reconciliation` and `r4f-no-stale-deps`; overridden at
consolidation and routed as triage candidates rather than softened. Neither bars
the change.

- **The schema-doc float is not on the record.** The handoff states the staleness
  "is floated to the Admiral". I could not reproduce that claim at its source:
  it appears on no spine `triage_candidates` entry (the spine holds `tc1`
  shared-string evidence sufficiency and `tc2` MCP door binding, plus one archive
  blocker about push/PR fencing), in no `ADMIRAL_LOG.md` entry, and
  `FINDINGS-wave2-engine.md` does not exist. Per inherited doctrine a claimed
  side-effect I cannot reproduce is a finding, not an accepted fact. I have routed
  it durably myself as `tc1` on this survey so it reaches Commander through the
  engine rather than through handoff prose — **Commander should carry it to the
  Admiral before this lane closes.**

## Out-of-scope observations

- `tc1` — `docs/CHECKLIST_SCHEMA.md` outcome vocabulary is stale (above).
- `tc2` — extract the shared "is this the state the pending-HARD advisory is
  rendered from" predicate so `_trip_advisory` and `_trip_hard_gate` cannot drift
  (`checklist_engine.py` ~1731–1738 and ~1961–1966).
- `tc3` — **pre-existing #467 behaviour found while probing, present in both the
  old and new engine.** Over the hard line, a `start` aimed at a gate id that does
  not exist writes a `trip_ledger` row for that nonexistent gate
  (`gate: "nope", outcome: "begin-refused"`) and raises the trip refusal,
  shadowing the engine's own `no such item` error. The append-only ledger
  accumulates rows for gates that were never in the checklist, and the agent is
  told to attach a refresh-request against an id that cannot hold one. Belongs to
  #467, not #510.

## Workflow Feedback

- **Handoff gaps:** the "What was changed and why" section cites "the Admiral's
  frozen launch order" without a path, and the launch order physically present in
  the worktree is the **wave-1** one, whose `settled/human` pre-rulings forbid
  exactly this change. I had to search the parent repo to find
  `.agent-work/epic-568/LAUNCH_ORDER-wave2-510-engine.md`. A reviewer who trusted
  the in-worktree artifact would have blocked the change as a scope violation.
  Name the governing order by absolute path in the handoff.
- **Context rediscovered:** the base-commit red state. The handoff calls
  `test_live_line_is_absent_after_the_offenders_own_close...` "deliberately
  failing" but does not say the lane's baseline was therefore 1-red, so I could
  not tell a real regression from the known one until I ran `23ed6b70` with both
  files at HEAD myself. State the baseline counts in the handoff.
- **Instructions improvised around:** the handoff prescribes `git stash` for the
  red/green. I used copy-aside + `git checkout HEAD -- <file>` + restore instead,
  because a stash in a worktree that also holds live `.agent-work/` state is
  needlessly recoverable-only-by-hand if anything fails midway; I verified the
  restore by re-diffing to the exact pre-experiment diffstat. Also: `record
  --finding` text goes through a shell, and unescaped backticks in my findings
  were silently eaten by command substitution — two engine-recorded findings lost
  a code-span literal each (the full text is in this document). Worth a note in
  the reviewer skill.
- **Rail misfit worth fixing (new, and it fires at every crew's exit):** when I
  finished — survey consolidated, result written, my own lease released — the stop
  hook refused the turn with `SPINE MID-FLIGHT: gate execute is still open`, and
  handed me the **Commander's** execute-gate imperative: reload
  `constellation-commander`, write `STATE_NOTE.md`, dispatch crews via
  `run_crew.py`. That is my parent's work, not mine. The cause is mechanical: my
  `SPINE_FILE` was **empty** (I am a dispatched crew with no bound spine, so I
  built my own survey per the reviewer skill), and with nothing bound the hook
  falls back to the work-id's spine — `.agent-work/epic-568-510/spine.json`, whose
  `execute` gate is held by a **live, heartbeating** lease belonging to
  `constellation/epic-568-510/g3-engine/commander/attempt-1`. Obeying it would
  have meant seizing an active session's lease and driving another agent's plan,
  against "One agent, one plan". I did not: I verified my own survey reports
  `DONE: no open items`, confirmed the deliverable exists, and stopped. The hook's
  escape hatches do not fit either — there is nothing to `block` (my survey has no
  open items, and my parent's gate is not blocked, it is simply waiting on this
  result), and waiving would need a human authority I do not have and a check that
  is not mine. **The process table settles it, and it inverts the hook's
  premise.** My shell's ppid is PID `3731876` = `claude -p "You are the
  constellation reviewer crew for session
  constellation/epic-568-510/g2-engine/reviewer/attempt-1 ..."` — I am the
  headless crew process. Its parent shell `3731846` is running
  `timeout 3500 python scripts/run_crew.py --gate g2-engine --role reviewer
  --parent constellation/epic-568-510/g3-engine/commander/attempt-1`, launched
  from the Commander's own Bash tool call. `run_crew.py` is **foreground and
  blocking**, so the Commander (a separate live process, ~8h elapsed) is parked
  on it right now. The hook says "ending your turn now abandons an active run";
  the truth is the reverse — **the active run cannot resume until I exit.** Worse,
  the `timeout 3500` means that if I keep taking turns to satisfy the hook I will
  eventually be killed at 58 minutes and the Commander will record a timed-out
  crew run for a review that finished clean with an APPROVE. **Suggested fix:**
  the mid-flight guard must compare the open gate's lease holder against the
  current session and stay silent when they differ (or skip entirely when
  `SPINE_FILE` is unset). As written it fights `run_crew.py`'s own blocking
  contract and pushes every correctly-finished crew toward either seizing its
  Commander's lease or dying on the dispatch timeout.
- **Unrelated, noticed while checking:** `crew-runs.json` lists
  `g2-repair/commander` and `g3-engine/commander` as `status=running` with
  `pid=None`, and holds no entry for this `g2-engine/reviewer` run. Those are
  exactly the shape `recover_crews.py` flags as unresolved before a dispatch.
  Commander's to reconcile, not mine.
- **What would have made this easier:** one line in the handoff giving the
  absolute path of the governing launch order and the baseline suite counts.

## Return status

`complete`
