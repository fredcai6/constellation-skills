# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-g` before dispatching the `g4-implement` crew. Replaces
`commander-w4-467-f`'s note wholesale — its content is either carried below or is now done.**

## READ THIS FIRST

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g4-implement` — `in-progress`,
  crew dispatched.** **11/17 complete:** `e0-context`, all three `g1-*`, all three `g2-*`, all three
  `g3-*`, and **`g3b-glossary` (closed by me)**. `amendments: 2`. 17 gates. Remaining 6:
  `g4-implement`, `g4-review`, `g4-integrate`, `g5-acceptance`, `g5-review`, `g5-integrate`.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467`.
- **HEAD:** `9997c32d` (g3b commit). **This is the parent commit of the g4 diff** and the commit
  every baseline below was measured at.
- **engine lease:** **CLAIMED** by `session_01TTKPTbD6nnMt7jFWw9GtjX` on **both** `spine.json` and
  `execute.json`. Every agent in this session shares that id, so `claim` takes the idempotent-resume
  path — claim **without `--force`**. Mutating verbs need
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX`. **Verify with the raw JSON, not with this line.**
- **pid:** none — foreground. Crew backend is `external` (record-only registry + Agent-tool
  subagent), so there is no process to kill or resume.
- **expected artifact:**
  `.agent-work/issue-467-trip-semantics/crew-handoffs/g4-implementer-result.md`
- **next command:** claim both leases, then
  `py .../recover_crews.py issue-467-trip-semantics`. If the g4 implementer is unresolved, recover or
  abandon-and-relaunch it against the **existing**
  `crew-handoffs/g4-implementer-handoff.md` — do not rewrite that handoff.

## What I did this shift

**`g3b-glossary` — CLOSED.** `docs/agents/GLOSSARY.md:13`, the `trip` row's Usage-notes cell, said
*"HARD blocks `advance` until the agent requests a context refresh."* False against the shipped
engine. Replaced with the semantics read out of the code: HARD refuses the **begin-work** verbs
(`start`, `reopen`) until a keyed refresh-request is pending; the `advance` that closes the gate you
are already in is never refused, **only closing it silently is**.

- `c1` is genuinely failable — **exit 1 before the edit, exit 0 after**. I ran both.
- Blast radius measured, not asserted: source-tree diff is exactly `1 1 docs/agents/GLOSSARY.md`,
  one `-/+` pair, and only the fifth cell of that row differs.
- **I added a third clause** beyond the two the imperative named (*"only closing it silently is"*)
  and declared it in the `c3` attestation. Reason: *"advance is never refused"* standing alone
  replaces a false line with a misleading one, since `advance --mechanical` **is** refused at/over
  hard. It stays inside the one sanctioned cell, so it is within the ruling's blast radius, not an
  expansion of it. **The Admiral should confirm or reverse this.**

## THE GAUGE — correcting my predecessor's reading of it

`commander-w4-467-f` stopped at the seam on a genuine trip (its own **20.9%**). When I claimed the
leases, `gauge.json` still held **that** reading, and the engine's `current` was still printing
`CONTEXT 21% (>= hard)` — a reading belonging to a **stopped agent's** session, not mine.

**It resolved itself within minutes: the gauge refreshed to my own 8.8% and the advisory cleared.**
The writer hook is live; it simply had not fired yet in my first minutes.

**I did not file a refresh-request and I did not waive anything — there was no governor stop by the
time I reached the `advance`.** Worth knowing for whoever hits this next: **a fresh Commander can
inherit a stale over-the-line reading at a seam.** Do not react to it as if it were yours, and do not
file a false refresh-request to clear it. Read `gauge.json`'s `observed_at` and check whose session
it belongs to. (Stale readings are discarded at 30 minutes, so it self-clears either way.)

## WHICH ENGINE — Admiral ruling, settled, do not re-litigate

Three engines differ by exactly the thing under test:

```
installed workbench   140170 bytes   NO fix
main                  146457 bytes   NO fix
branch worktree       156060 bytes   HAS the fix
```

- **Drive the spine with `python C:/Programs/constellation-skills/scripts/checklist_engine.py`** —
  main's engine. It is what every launch order in this wave specified and what produced eleven gates
  of evidence. **Do not switch the driving instrument mid-run.** That is plan surgery.
- **`g5-acceptance` is the exception and the point:** it must exercise the **branch worktree** engine
  explicitly and **pin the binary by hash** in its evidence, naming which one it ran. Acceptance
  evidence produced through a pre-#467 bundle proves nothing about the fix.
- **Do not reinstall anything.** Both installed bundles are pre-#467. That goes to closeout after
  merge.

## BASELINES — pinned to the commit they were measured at

Measured by me, in this worktree, at **`9997c32d`**:

| Command | Result |
|---|---|
| `pytest -q tests` | **1833 passed, 2 skipped, 808 subtests passed** (311s) |
| `pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'` | **exit 5**, 384 deselected |

The second is the frozen `g4-integrate` `c2` selector. **Exit 5 today = the check is genuinely
failable**, which is the point.

**Handoff lesson, twice-reported and now applied:** a criterion asking for a suite delta must name
the diff's **parent** commit. The stated baseline `d376b786` earlier in this run spanned 15 commits
and was not the parent, which cost two agents real time chasing a ±1 subtest ghost.

## MODEL TIERS — Admiral ruling, binding

Sonnet by default; **Opus needs a named reason in the dispatch**.

- **`g4-implement` — Opus**, reason named in the dispatch: an engine-only append-only trip ledger at
  mutating chokepoints is **engine-semantics work where being subtly wrong is invisible**.
- **`g4-review`, `g5-review` — Opus** (adversarial-review carve-out).
- Anything more mechanical — **Sonnet**.

## CARRY INTO g4 AND g5 OR THE FIX IS VERIFIED AGAINST NOTHING

1. **#431 is instruction-conformance, not a deadlock.** The pre-fix engine **permits** the advance
   while telling the agent not to run it. A test worded *"the advance is no longer blocked"* passes
   in **both** worlds. **Verify on what the agent is TOLD.**
2. **DC6's observable is "did anyone BEGIN work while over the line"**, never "did a handoff artifact
   appear" — that second one is true by construction.
3. **Rebuild the pre-change engine** (`git show 38f0b448^`) and run the new tests against it rather
   than trusting saved RED files.
4. **Attack equivalent-mutant claims.** The g3 BLOCK came from exactly that and found a code path
   with **zero coverage**.
5. **A negative-only test cannot fail.** g3's M5 dead-coded the resolver and all twelve negative
   assertions still passed.
6. **The gauge is discarded if `observed_at` is in the future (clock skew) or older than 30 minutes**
   — it collapses to "no gauge" and any scenario built on it goes **vacuously green**. Generate
   fixture timestamps from the clock.
7. **The printed `<why-id>` placeholder is literal** — attaching it verbatim exits 0 and silently
   does nothing. Read the real id from the raw `why_trail`.
8. **Write reviewer handoffs in `APPROVE` / `BLOCK`.** That is what every `*-integrate.c3` matches.

## HANDOFF DOCTRINE — both defects now fixed in the g4 handoff

1. **Name the diff's parent commit** on any suite-delta criterion. Done — `9997c32d`, stated twice.
2. **Sanction ONE method for re-running mutations.** "Do not modify `scripts/`" versus "re-run at
   least two mutations yourself" caught two reviewers in a row. The g4 implementer handoff sanctions
   one route explicitly: commit first, mutate in place, run the named test, revert with
   `git checkout -- <file>`, confirm `git diff --stat` clean before the next. Carry the same
   sanction into the g4 reviewer handoff.

## TRUST ORDER

**`execute.json` (`tasks` + `amendments` + per-task `evidence`) is the only projection correct end to
end.** Note the shape: `execute.json["tasks"]` is a **dict keyed by id**; `["items"]` is a list of id
**strings** giving the order. Iterating `items` gives you strings, not tasks — two agents have now
lost a minute to that.

1. The raw task JSON and `current` — **authoritative**.
2. This note — a *pointer*, correct only as of its timestamp.
3. `MISSION_FRAME.md`, `LO-467.md` — **stale until proven otherwise**.

## OPEN, for the Admiral — carry these up, do not decide them

- **The third glossary clause** I added at `g3b` (above) — confirm or reverse.
- **Whether `commander-w4-467-f`'s live #431 trip can be cited as `g5` acceptance evidence.** A real
  round trip already happened, to the Commander, on the real spine, through the engine that **has**
  the bug. `g5`'s scope is frozen, so this is not the Commander's call. **Still unanswered.**
- **The stale installed engine bundles** — reinstall at closeout, or rule that the run continues on
  them deliberately. Either way `g5` must pin the engine by hash.
- **`decision:execute-gate-reserve-value` (30000) is `@grade: guess` and its authored settle
  experiment is NOT RUNNABLE** — confirmed independently four times. `gauge.json` keeps only the
  latest reading. **Cheaper replacement, ready to route:** log `(gate, fill_fraction)` at each gate
  boundary; after a handful of runs the number becomes measurable.
- **`docs/CHECKLIST_SCHEMA.md` under-documents the Task object by one optional key**
  (`context_headroom_tokens`). Natural home is this run's `reconcile` step, not a new gate.

## TRIAGE CANDIDATES — do NOT lose these at the `triage` step

`execute.json` carries six (`tc1`–`tc6`). **`tc1` is CLOSED** (it was `g3b-glossary`, now shipped).
**`tc3` is RESOLVED** (the parent-commit baseline, above). Live: `tc2` mid-gate handoff channel,
`tc4` `block()`'s missing status guard — **pre-existing, not ours, and the M15 kill now DEPENDS on
that state, so whoever tightens `block()` must know a test guards it** — `tc5` the reopen-path
advisory/guard divergence, `tc6` the survey sidecar collision.

**The review surveys carry seven more that are NOT on `execute.json`** and will be missed unless read
directly:

- `g3-review/review.json` — **5 candidates**, including `thresholds_for`'s docstring claiming its
  guarantee holds "for every input", which is false for non-real-number arguments (unreachable from
  any shipped path — reword to "every real-number input", do not add a guard); plus a duplicated-code
  flag, `thresholds_for(model, _gate_headroom_tokens(...))` written twice at `:1486` and `:1543`.
- `g3-rework-review/review.json` — **2 candidates**.

## If you trip

Commit at the seam, file the `refresh-request` with the **concrete** why-id read from the raw
`why_trail` (never the literal `<why-id>`), rewrite this note, release **both** leases, go idle.
Eight predecessors have now done this cleanly and none lost work. Do not push through, and **do not
`start` new work over the line**.
