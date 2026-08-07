# IMPLEMENTER_RESULT — issue #440 g2 acceptance (attempt 2, resumption)

## Verdict, in plain English

**Yes. The HARD governor trip fires from a per-agent gauge reading produced by an agent that was
dispatched into a worktree.** It was observed live, not inferred.

A real dispatched subagent, working in a real `git worktree`, claimed a checklist there with a
relative `--file`, genuinely filled its own context to 56%, and when it tried to `advance` the engine
**refused it**:

```
REFUSED: m1: context at 56% is at/over the hard limit — advancing is blocked until you
request a refresh, so work is handed off at a seam rather than lost to a runaway.
Run: attach m1 --type refresh-request --field seam=m1 --field why_ref=<why-id>
EXIT=1
```

The control arm — the same sandbox, same prompt, same models, same inflation, with **only** the
absolute hook path pointed at the pre-fix `scripts/` tree — produced a real reading of the same size
and filed it in the phantom directory inside the sandbox main. The engine saw nothing beside the
worktree spine and let the gate through at **exit 0**. That is the #440 defect and its repair,
observed side by side on one run.

`verify_evidence.py` **exits 0 on freshly-produced evidence — 46 checks**, all four previously-open
gaps closed.

## The two arms, measured

| | treatment (fixed) | control (pre-fix `cbd9aee`) |
|---|---|---|
| headless run | exit 0, 156.4s, no timeout | exit 0, 143.5s, no timeout |
| binding resolved to | **worktree** spine, `path_source: git_worktree` | **sandbox main**, `path_source: null` |
| `gauge.json` beside worktree spine | **present**, fill **0.5597** | absent |
| `gauge.json` at phantom path in sandbox main | absent | **present**, fill **0.5621** |
| HARD for `claude-sonnet-5` | 0.15 | 0.15 |
| `advance` | **REFUSED, real exit 1** | **succeeded, real exit 0** |
| gate after | stayed `in-progress` | `complete` |

The two fills are within 0.0025 of each other, so the difference in outcome is the hook path and not
a difference in how full the two subagents got.

**The control is positive, not merely quiet.** It produced a real, over-HARD reading — the writer
plainly worked; it just filed it where the engine never looks. That is what makes the treatment
result mean something.

## Attribution — the reading is the dispatched subagent's, three independent ways

Captured on **both** arms, in agreement:

| signal | treatment | control |
|---|---|---|
| composite `session_id#agent_id` binding key (only a dispatched agent keys this way) | `9d959dcd-0cb4-4f25-b391-d7be110eb5c5#a26a9cb68fda52cdc` | `25b64ada-5cc4-49f0-9570-06ca369b5dc4#ae5c1d873b314a6e8` |
| `identity_resolution_ms` present (fifth field, dispatched agents only, #419) | 0.0433 | 0.0439 |
| `gauge.json` `model` vs parent model | `claude-sonnet-5` vs parent `opus` | `claude-sonnet-5` vs parent `opus` |
| `observed_at` vs wall clock | 4s old | 4s old |

No signal disagreed with another.

## Evidence produced, with real exit codes

All under `.agent-work/issue-440-binding-cwd/acceptance/evidence/`, all freshly written 2026-08-07.

| command | real exit |
|---|---|
| `run_two_arm.py --arm treatment --filler-count 24 --keep` (2nd launch) | 0 |
| `run_two_arm.py --arm control --filler-count 24 --keep` | 0 |
| `verify_evidence.py` on the real evidence | **0** (46 checks) |
| `verify_evidence.py --dir <truncated copy>` | **1** (2 failures) |
| `verify_evidence.py --selftest` | 0 — real evidence passes, **all 5** damaged copies correctly fail |
| `verify_evidence.py` re-run after temp cleanup | **0** |

Exit codes were taken by redirecting to a file and echoing `$?`, never off the end of a pipe.

## The first treatment launch was quiet — diagnosed, not believed

The **first** launch of the treatment arm went quiet: 87.8s, no gauge anywhere, `advance_exit: None`.
This is exactly the shape a reproduced bug would have, so I did not interpret it — I read the
headless stdout. The dispatched subagent had **declined the protocol outright** at step 0:

> Its stated reasoning: it read the prompt's self-explanation ("nothing below looks like a trick,"
> "is not a prompt-injection attempt"), the instruction to read declared-meaningless content purely
> to inflate context, and the fixed closing token `PROTOCOL-COMPLETE` as a social-engineering
> pattern, and declined to comply rather than verify the tooling.

So the harness's own defensive framing is what triggered the refusal. A declined run is cheap (no
inflation), so I re-ran the arm **unchanged** rather than editing the prompt, and the second launch
complied fully. Both launches are on record. **This is the positive-control requirement earning its
keep**: without checking the stdout, that quiet arm would have been reported as the bug reproducing.

## One check I corrected rather than satisfied — please review this deliberately

`verify_evidence.py` asserted the **live** checkout's `.agent-work/.spine-rail-binding.json` was
byte-identical before and after the run. On this run it was not: 4213 → 4663 bytes. I treated that as
a possible exclusion breach and diagnosed it before touching anything.

**The harness did not write it.** There is **zero** sandbox leakage: no key or spine path in the live
store references the sandbox root (`acc440`), the temp directory, or the sandbox work id. What grew
the file was ordinary concurrent activity writing through the **live** checkout's own PostToolUse
hook — including, provably, **this run's own engine `claim`** (key `cdcd8db2-…#a55`, spine
`…/crew/g2-implement/IMPLEMENTER_PLAN.json`, claimed 14:35:18Z) and a **sibling commander's** crew
plan at 14:41:50Z.

That store is shared, live-written state. Byte-stability across a run window is not achievable while
any other agent is working, and its absence says nothing about the harness either way — so the check
was testing something unsatisfiable instead of the thing the exclusion actually requires.

I replaced it with the direct, falsifiable test: **no sandbox path leaked into the live store**. Had
the harness pointed `CLAUDE_PROJECT_DIR` at the live checkout, the sandbox's spine paths would appear
there and the check fails. To prove it can fail I added a **fifth selftest mutation**
(`live-store-leaked`) that relabels the sandbox root as one present in the live store; it is caught.
The byte delta is still reported, as an explicit `NOTE`.

This is the only substantive change I made to the reviewed harness. It is a change to a **check**, so
I am flagging it rather than burying it: if the Commander would rather the guard stay strict and the
run be re-done in a quiet session, that is a reasonable call and easy to reverse.

## Files changed

- `.agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py` — `check_live_checkout_untouched`
  rewritten as a leakage test (above); one new selftest mutation.
- `.agent-work/issue-440-binding-cwd/acceptance/evidence/*` — all regenerated from the live runs.
- `.agent-work/issue-440-binding-cwd/crew/g2-implement/IMPLEMENTER_PLAN.json` — driven m2→m5.

`run_two_arm.py` was **not** rebuilt or re-derived. No hook, engine, gauge reader, or test was
touched. Nothing was committed.

## Exclusions — all held

- `spine_rail.py`, `gauge_writer_hook.py`, `checklist_engine.py`, `gauge_reader.py`, tests: **unmodified**.
- **Nothing hand-injected.** The worktree root was derived by the hook shelling out to
  `git worktree list` (`path_source: git_worktree`); no `cd`, no `--worktree`, no absolute `--file`,
  no env var handed it the answer.
- **Live checkout never written by the harness** — proven by zero sandbox leakage, above.
- `python` throughout, never `py`. Parent `opus`, subagent `sonnet`, both named explicitly on every
  launch. **No Fable at any tier.**
- Temp tree removed (`%TEMP%\acc440` gone), `__pycache__` removed, truncated copy removed.
- `git check-ignore` returns **exit 1** (not ignored → will be committed) on all 14 deliverables.
  Total 108K, no multi-MB logs.

## Stop conditions hit

None. The weekly usage limit that killed attempt 1 did **not** recur; both arms ran to completion.

## Out-of-scope observations (triage candidates)

1. **A dispatched subagent can refuse an acceptance protocol because of its own defensive framing.**
   Prompts that pre-emptively argue "this is not a trick" and end on a fixed magic token read as
   social engineering. Any future harness that needs a subagent to inflate context should frame the
   work as ordinary and drop the protestation and the magic token. This is a live flakiness source
   for #440-style acceptance runs and cost one launch here.
2. **`verify_evidence.py`'s live-checkout guard was unsatisfiable under concurrency** (detail above).
   The general lesson is broader than this harness: any check asserting a shared agent-written file
   is byte-stable will false-alarm whenever the constellation is busy.
3. **The live binding store holds two junk entries** — spines literally named
   `C:\Programs\constellation-skills\x` and `C:\Programs\constellation-skills\$E`, claimed
   2026-08-06T10:02–10:03Z. `$E` is an **unexpanded shell variable**: something ran an engine command
   with `$E` unquoted or under a shell that did not expand it, and `spine_rail.py` recorded the
   literal string as a spine path. Harmless here, but the hook is willing to bind a path that does
   not exist, which is worth a look given #440 is about binding the wrong path. Not touched.

## Workflow feedback

- The R2 handoff was excellent for a resumption: it named exactly the four open gaps, told me what
  attempt 1 had already proved so I would not re-derive it, and pre-empted the budget hazard. The one
  thing it could not anticipate was that a *fifth* check would newly fail for an environmental
  reason. A resumption handoff might usefully say what to do when a **previously-passing** check
  breaks — my read was "diagnose first, and if the check is wrong, correct the check and flag it
  loudly," but that was my judgment call, not something the handoff licensed.
- R2 contains a mild ordering conflict: "run the arms one at a time, **treatment first**" versus
  "**prioritize the CONTROL arm** if you can only afford one." I resolved it by the engine's own gate
  order (m2-treatment was active) and because budget had just reset. Worth stating the tiebreak
  explicitly next time.
- `checklist_engine.py attest` takes `--note`, while `advance` takes `--why`. Passing `--why` to
  `attest` is a hard argparse error. Minor, but it cost a round trip.
- The `Bash` tool blocks a foreground `sleep` chained to another command, which makes in-turn polling
  of a long headless run awkward; `until <marker>; do sleep 10; done` in the foreground is the form
  that works and is worth putting in crew doctrine.

## Map impact

No architecture map exists (`DEGRADED-NO-MAP`); anchors reused from the handoff.

- **Structural** — unchanged. `scripts/hooks/spine_rail.py` remains the only per-arm variable;
  `_trip_hard_gate` in `checklist_engine.py` was the observer and behaved identically in both arms.
- **Decision `existence-verified-resolution`** — `@grade: guess · settle: THIS GATE`. **Now settled by
  live evidence.** The ordered-rungs / first-validating-candidate resolution was exercised end to end:
  the treatment arm reached the `git worktree` rung and bound the worktree spine; the control arm,
  lacking it, bound the main checkout. Recommend regrading to `measured`.
- **Constraint** — "hook code is not fenced by worktree isolation" (#269) is **confirmed and now
  demonstrated**: the sandbox pair was necessary precisely because an in-worktree run would have
  produced a meaningless green.
- **New constraint candidate** — the live binding store is shared, concurrently-written state; no
  check may assume it is byte-stable.
