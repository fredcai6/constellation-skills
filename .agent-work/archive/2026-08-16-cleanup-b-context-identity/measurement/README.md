# Which world does each artifact describe?

Written at `g1-integrate`, because a measurement artifact that outlives the world
it measured is worse than no artifact: someone re-runs it, gets a confident
verdict, and the verdict is about a world that no longer exists.

`#600` is commit `3bc87e93`. Everything here is either BEFORE it or AFTER it.

## The cross-key collision probe

| artifact | world | how to read it |
|---|---|---|
| `probe_cross_key.py` | **AFTER #600**, and it ASSERTS that world | Runnable. Exits 0 when each agent keeps its own reading, 1 when the collision returns or a reading is lost. On a tree that predates #600 it refuses to run and says so, rather than dying obscurely or printing a verdict about the wrong world. |
| `probe_cross_key.pre-fix.out` | **BEFORE #600** | The record the design was cut from. `VERDICT: CANDIDATE 2 CONFIRMED`. **Not reproducible** — the defect it captured is fixed. Read it; do not try to re-create it. |
| `probe_cross_key.post-fix.out` | **AFTER #600** | `probe_cross_key.py` run at the merged branch. `VERDICT: EACH AGENT KEPT ITS OWN READING`. |
| `probe_cross_key.lane-c-remeasure.out` | **#549 present, #600 absent** | The lane C re-measurement — see below. |

### Why the probe had to be updated at all

Before this update the probe watched `gauge.json` alone. Post-fix that file is
never written, so the probe took its `after_sub is None` branch and printed:

```
VERDICT: NEITHER — the dispatched agent's write was skipped.
```

Nothing was skipped. Both agents wrote — to owner-keyed files the probe was not
looking at. The artifact would have told a future reader that #600 had silenced
the governor, which is the opposite of what it did.

### One thing the red run taught us

Running the updated probe against the pre-fix tree exposed a real fragility in
the probe's own module loader: it did not register the loaded module in
`sys.modules`, which `@dataclass(frozen=True)` field resolution needs. It only
ever worked because the post-fix hook loads `gauge_reader` first and registers it
as a side effect. Fixed, with the reason written at the call site.

## The lane C re-measurement

The question `g1-integrate` asks: lane C's **#549** (`915daefa`, merged to `main`
in `df6f951b`) — did it remove the collision, making #600 unnecessary?

Measured rather than assumed, which is what the gate required. `main` at
`d7b911a7` is the clean isolate: it **has** #549 and does **not** have #600.
Running the **original** (pre-fix) probe there:

```
VERDICT: CANDIDATE 2 CONFIRMED. The orchestrator's own fill (0.9) OVERWROTE the
dispatched agent's (0.02) at the same path. Two distinct keys, one gauge file,
no guard.

  observed_at > claimed_at : True
  -> _reading_predates_claim is False -> #477/#601 guard does NOT fire
```

**The collision reproduces unchanged with #549 present.** The Admiral's reading
in `ADMIRAL_NOTE-lane-C-landed.md` — that #549 removes one *route* into the
collision but not the *mechanism* — is confirmed by measurement. #600 was still
load-bearing after lane C landed.

## The rest

| artifact | world | what it is |
|---|---|---|
| `demo_owner_keyed_gauge.py` + `.before.out` / `.after.out` | spans both | The fresh-process red/green demonstration for #600, driving the real reader and real gauge files. The reviewer re-ran both directions. |
| `gauge-at-T0.json`, `gauge-at-T1.json`, `gauge-oscillation.log` | **BEFORE #600** | The oscillation measurement from `g0-measure` — one gauge file changing owner under a live run. |
| `main-binding-at-T0.json`, `worktree-binding-at-T0.json`, `worktree-binding-at-T1.json` | **BEFORE #600** | Binding-store snapshots showing multiple harness keys against one spine. |
| `probe_payloads` fixture (in `tests/fixtures/`) | both | The real payload shapes the harness sends, which is what lets these probes claim "nothing is patched". |
| `suite-head.txt` | **BEFORE the leg 3 merge** | A superseded suite reading. The gate-time figures are in `REPLAN_INPUT.json`: branch 3104/6/0 at `ccb8b8d8`, `main` 3089/7/0 at `d7b911a7`. |
