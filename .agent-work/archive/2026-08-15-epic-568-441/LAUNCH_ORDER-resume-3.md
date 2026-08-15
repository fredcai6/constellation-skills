# Launch Order: `epic-568-441` — attempt 3, stop delegating and write the code

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER-resume-2.md`; both earlier orders still bind except where corrected here.

## Attempt 2 did the hard part. Do not redo it.

**You captured the RED.** It is at `.agent-work/epic-568-441/evidence/m1-red-observed.txt` and it is
the proof obligation a Codex quota blocked for a full day. It is **attested; do not re-run it as if
unmet.**

It is also **stronger than your plan assumed**, and you should register that before implementing.
Your plan's premise was a lost update:

> the final valid JSON reliably contained only a subset of these entries

What actually happens with 16 spawned production claim writers is that the registry is left **not valid
JSON at all**:

```
json.decoder.JSONDecodeError: Extra data: line 11 column 2 (char 472)
```

Two JSON documents concatenated — a torn write, not a dropped entry. Your converged plan already
prescribes **unique-temp atomic replacement**, which is the right shape for this; the red simply proves
the failure is more severe than the premise stated. **No re-plan is needed.** Note the correction in your
findings and carry on.

## The one instruction that matters this time

**Implement it yourself, in this process. Do not dispatch a crew.**

You have now tried twice. Both children died immediately:

- `crew-runs/g1-implementer-attempt-1.stdout.txt` → `Execution error`
- `crew-runs/g1-implementer-attempt-2.stdout.txt` → `Execution error`

Attempt 2's dispatch did not even leave a registry entry. Meanwhile two sibling lanes are running
implementer crews successfully on this same machine, so this is specific to this lane and **not yours to
debug**. Record it as a finding with those two file paths as evidence and move on.

And to close the loop on attempt 2's sign-off: you wrote that the harness "moved it to background… and
will notify me when it completes." **It will not.** When your turn ends your process exits. There is no
scheduler, no notification, and nothing resumes you. Anything you need done, you do now, in this turn,
or it does not happen.

Your handoff at `crew-handoffs/g1-implementer-handoff.md` is good work — **read it and implement it
yourself.** It is your own instruction set; you do not need a second agent to follow it.

## Remaining work

1. Take over `g1-implementer-plan.json`'s lease — still `previous_session_id: null`, still reading as the
   dead Codex implementer's. The outer two are correctly stamped.
2. Implement the transactional binding store per the frozen convergence: the transaction owns lock
   acquisition, locked reload, safe reap, one mutation callback, unique-temp replace, and release. Claim,
   release and SessionStart stay thin callers. Gauge delegates identity validation to the rail and never
   becomes a store owner.
3. Drive `m1-transaction` → `m2-validation-reap` → `m3-writers-routing` → `m4-verify-report`, then
   `g1-implement`, then `execute`.
4. **Clear the stale blockers as you resolve them.** `spine.json:execute` and `execute.json:g1-implement`
   still carry yesterday's Codex text naming a 2026-08-20 date that today's ruling superseded. While they
   stand, the launcher reports this lane `blocked` no matter what you accomplish.
5. Green the suite and get `m1-red-observed.txt`'s test passing.

## Unchanged

The Codex-quota ruling (proceed now; you are on Claude). The frozen plan and its closed untaken roads.
The four-file ownership scope — `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`,
`tests/test_spine_rail.py`, `tests/test_gauge_writer.py`, `docs/agents/engine-config.json`. The fences on
`scripts/checklist_engine.py`, `scripts/run_crew.py`, `.mcp.json` and `commander-315` — **all three
sibling lanes are live right now**, so those fences are load-bearing, not ceremonial. Fail-open hooks,
stdlib-only advisory locking, no stale-lockfile lifecycle, no backfill. The fence on merging.

**Baseline `main` at `453f8492`: 3002 passed, 7 skipped, 0 failed, 1130 subtests passed**, cache-clean.
You have already merged main and regenerated the map.

## Stop Conditions

Unchanged, plus: **stop and report rather than dispatching another crew.** If the work genuinely cannot
be done in-process, that is a finding worth more than a third dead child.

## Return Shape

What you changed; the **red-to-green transcript** for
`tests/test_spine_rail.py::test_spawn_binding_transaction_red_green`; the concurrency, identity and
retention proofs; the third lease takeover; confirmation the stale blockers are cleared; cache-clean
suite counts; whether the map moved; and your findings, including the dead-child dispatches and the
stale-`running` registry entry from attempt 1.
