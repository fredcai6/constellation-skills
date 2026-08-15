# Launch Order: `epic-568-441` — attempt 2, the crew you were waiting for is dead

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
**Supersedes** `LAUNCH_ORDER-resume.md`, which still applies in full **except** where this order
corrects it. Read that order too — mission, resume order, pre-rulings, ownership and evidence are all
still binding.

## What happened on attempt 1, and why you are not at fault

You did four things right and I am not asking you to redo them:

- You merged `main` into the branch (`3e180ed6`) and regenerated the map (`9affa0d2`).
- You took over `spine.json` and `execute.json` with `previous_session_id` and `takeover_reason`
  stamped. Exactly as ordered.
- You moved `m1-transaction` to `in-progress`.
- You blocked and failed up instead of forcing. That was correct.

Then you ended with:

> I'll pause here and resume automatically once the background implementer crew finishes.

**There is no such crew.** You read this registry entry:

```json
{ "crew_id": "constellation/epic-568-441/g1/implementer/attempt-1",
  "status": "running", "pid": null, "backend": "external",
  "started_at":     "2026-08-14T18:10:25Z",
  "last_heartbeat": "2026-08-14T18:10:25Z",
  "completed_at": null, "abandoned": false }
```

It says `running`. It is the **corpse of yesterday's Codex implementer** — the one the quota killed. Note
what gives it away: `pid` is `null` and `last_heartbeat` is **identical to `started_at`**, frozen 24 hours
ago. An `external`-backend entry spawns no process, so nothing can ever check its liveness or reap it. It
will read `running` forever.

Your inference was reasonable and the record was lying. **I have now abandoned that entry** — the
registry no longer claims a crew is in flight. Re-read it and confirm that before you plan.

Also note: nothing was ever going to "resume you automatically." Your process exits when you stop; there
is no scheduler. If you need work done, **you dispatch it and wait for it in-process, or you do it
yourself.**

## What to do now

Pick up at `m1-transaction`, which you left `in-progress`.

**Do the implementation yourself unless you have a positive reason to delegate.** Attempt 1 spent its
budget arranging a hand-off that never happened. If you do dispatch an implementer crew, you must
**verify it is actually alive** — a registry `status` is not evidence; a pid you can signal, or a
heartbeat that has advanced since you read it last, is.

Your first proof obligation is unchanged and still unmet:

```
python -m pytest -q -s tests/test_spine_rail.py::test_spawn_binding_transaction_red_green
```

`tests/test_spine_rail.py` still carries exactly the same **55 uncommitted added lines** and no
production change exists. **Run that test first. It must be RED**, demonstrating lost-update, before you
write any production code. If it is green, stop and report — that is the stop condition from attempt 1
and it still stands.

## One correction to your lease work

`g1-implementer-plan.json`'s lease was heartbeated but **not** taken over: its `previous_session_id` and
`takeover_reason` are both `null`, so it still reads as the dead Codex implementer's lease. The outer two
were done correctly. Take this one over the same way, with `--force` and a reason, so all three carry
provenance.

## Record this as a finding

The stale-`running`-forever entry is a **real defect**, not just an inconvenience you hit. Write it up in
your findings with the field values above as evidence. It matters because a parent polling the durable
registry — which is exactly what doctrine tells parents to do — waits forever on a crew that died a day
ago, and the duplicate-guard keeps a replacement from being dispatched.

A sibling lane (`crew-verdict-and-door`) is fixing a different false verdict in this same launcher. **Do
not fix this one yourself** — `scripts/run_crew.py` is not yours and that lane is live in it right now.
Your job is to document it precisely enough that it can be fixed without rediscovery.

## Everything else

Unchanged from `LAUNCH_ORDER-resume.md`: the Codex-quota ruling (proceed now, the 8/20 date does not
apply to you on Claude), the frozen plan and its closed untaken roads, the four-file ownership scope, the
fences on `checklist_engine.py` / `run_crew.py` / `.mcp.json` / `commander-315`, the evidence list, the
stop conditions, and the fence on merging.

**Baseline on `main` at `453f8492`: 3002 passed, 7 skipped, 0 failed, 1130 subtests passed**, cache-clean.
You have already merged main, so your branch should reproduce that before your production change lands.

## Return Shape

As before, plus: confirm the abandoned entry now reads abandoned; confirm the third lease takeover; and
give the regression's **red-then-green** transcript, which is the thing attempt 1 never produced.
