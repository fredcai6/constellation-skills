# Review — issue #182 (Trip, two-band gate policy; Module 3 of epic-178)

**VERDICT: APPROVE**

Independent clean-room review. I did not write this code. Worktree `C:/Programs/constellation-wt-182-rev`, detached HEAD at PR tip `05f4e21`, base `e2b8005` (post-Wave-0 main).

---

## Worktree isolation (`--here`)

```
worktree OK: in C:/Programs/constellation-wt-182-rev
EXIT: 0
```

---

## Acceptance criteria — per-criterion result

Thresholds are model-keyed; the shipped table is empty so every model resolves to `DEFAULT_THRESHOLDS = (0.75, 0.90)`. I pinned my probes to the pair the policy actually returns, and separately swept exact boundaries.

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | SOFT fires at/above soft, never below | **PASS** | Sweep: `0.749`→no advisory, `0.75`→`>= soft`, up through `0.8999`→`>= soft`. Below-soft values (0.0–0.749) produce no `CONTEXT` line. |
| 2 | HARD refuses at/above hard, never passes below hard | **PASS** | `0.8999`→advance passes; `0.9`,`0.9001`,`0.95`,`1.0`→advance raises `EngineError`, gate stays `in-progress`. |
| 3 | Missing/stale reading (None) → no advice, never forces | **PASS** | `_read_gauge`→None: `current` has no `CONTEXT` line; `advance` completes. Real stale/absent/malformed files (below) all rc=0. |
| 4 | Falsifiable: SOFT ever forces? HARD ever passes without refresh? | **Both NO** | Full sweep, 0 violations. See falsifiable-pair probe. |

---

## Specific probes (adversarial)

### FALSIFIABLE PAIR — tried to break it
Independent harness (`$TEMP/adv2.py`), loaded the engine by file path, patched `_read_gauge` to a controlled `Reading`, swept fill across `[0.0 .. 1.0]` including the exact boundary neighbourhoods `0.749/0.75/0.751` and `0.8999/0.9/0.9001`. For each fill I ran three things: `current` (advisory?), `advance` with **no** refresh-request (forced?), `advance` **with** a refresh-request present (forced?).

```
soft=0.75 hard=0.9
fill=0.749   advisory=False band=none    force_noref=False force_withref=False
fill=0.75    advisory=True  band=>=soft  force_noref=False force_withref=False
fill=0.8999  advisory=True  band=>=soft  force_noref=False force_withref=False
fill=0.9     advisory=True  band=>=hard  force_noref=True  force_withref=False
fill=1.0     advisory=True  band=>=hard  force_noref=True  force_withref=False
VIOLATIONS: 0
```
- **No fill exists where SOFT blocks.** Across the whole soft band `[0.75, 0.9)`, `advance` succeeds. SOFT rides only the read-only `current` suffix; it never raises.
- **No fill/reading state exists where HARD passes without a refresh-request.** In `[0.9, 1.0]`, `advance` with no refresh always raises; with a refresh-request present it always proceeds. `force_withref` is `False` for every fill (HARD never over-blocks once the remedy exists).

### FAIL-SAFE on None (absent / stale / malformed / clock-skew)
`_read_gauge`→None gives no advisory and never forces (verified). Real gauge files written next to a real spine and read through #181's actual `read()`:

```
NONE: advisory=False forced=False
malformed[corrupt]:  rc=0 status=complete   ("{bad")
malformed[list]:     rc=0 status=complete   ("[1,2]" — non-dict JSON)
malformed[missing]:  rc=0 status=complete   (missing fill_fraction field)
malformed[fill5]:    rc=0 status=complete   (fill_fraction=5.0 out of range)
malformed[future]:   rc=0 status=complete   (observed_at 1h in the future — clock skew)
```
Every degraded reading collapses to None inside the reader and `advance` completes. **A stale/bad gauge never forces a handoff.** PASS.

### HARD refusal leaves state UNMUTATED
The HARD guard `_trip_hard_gate` is called in `dispatch` **before** `_run_verb`, so a refusal never reaches `advance`. Verified `cl == before` (deep copy) after a HARD refusal, with `why_trail is None` — byte/semantically identical, matching #179's clean-refusal discipline. PASS.

Note (not a defect): a *why-capture* refusal (a different refusal, inside `advance`) does mutate — it records the command postcondition's `satisfied=True` + evidence. I confirmed this is **pre-existing #179/postcondition behavior**: it happens identically with **no gauge at all** (HARD absent), and the gate still stays `in-progress` (no status flip). It is not introduced or affected by #182.

### #179-ordering interaction (the Admiral's flagged question)
HARD is a pre-`advance` guard firing **before** postconditions and before #179's why-capture. I traced the full sequence on a NON-exempt gate (requires `--why`) at `fill = hard`:

```
Scenario A (passing postcond, non-exempt gate, at HARD):
 step1  advance(--why), no refresh    -> HARD refusal; state==before (why_trail None)  [unmutated]
 step2  attach refresh-request         -> ok
 step3  advance(no --why), w/ refresh  -> WHY refusal ("requires a running understanding"), not HARD
 step4  advance(--why),   w/ refresh   -> g1 -> complete; why_trail has exactly 1 real record
Scenario B (FAILING postcond, non-exempt, at HARD, refresh present):
 advance -> "postconditions unmet ['c1']"; gate stays in-progress
Scenario C (fill=1.0 forever): attach is NOT HARD-guarded -> attach, then advance(--why) -> complete
```

Judgment, with evidence:
- **(a) Does a HARD trip skip/corrupt why-capture or why_trail?** No. A HARD trip raises before the verb, so why-capture never runs and `why_trail` is untouched (stays absent). On the eventual successful advance the why is captured normally — exactly one record, no duplication, no skip.
- **(b) Bad interaction with unmet postconditions or a required why?** No. The order after a refresh-request is: HARD (satisfied) → postconditions → why-capture. An unmet postcondition surfaces its own refusal (Scenario B); a missing `--why` surfaces the why refusal (step3). No information is lost — it is deferred by one `advance` and then surfaced. The gate is never left inconsistent.
- **(c) Is "HARD before postconditions" defensible, or can the agent get stuck?** Defensible, and the agent cannot get stuck. `attach` is not HARD-guarded, so `has_pending_refresh_request` can always be made true (Scenario C). Once the refresh-request exists, HARD is satisfied and the normal postcondition+why path runs. There is no fill value or state that makes a gate permanently un-advanceable. Putting HARD first is arguably the *right* order: an out-of-context agent is told to hand off at the seam rather than being invited to push postconditions to completion on a nearly-full context; a fresh agent then completes them.

### Gauge-path pairing with #180's writer
- #180 writer (`scripts/hooks/gauge_writer_hook.py`, `resolve_gauge_path`): writes `Path(entry["spine"]).parent / "gauge.json"` — a **sibling of the spine**.
- #182 reader path: `dispatch` is called from `main()` with `base_dir=path.parent` (`checklist_engine.py:1775`, `path` = the spine file), and `_gauge_path(base_dir)` returns `base_dir / "gauge.json"` = `spine.parent / "gauge.json"`.
- **Identical location.** Pairing is correct. Also confirmed empirically end-to-end by `TripRealGaugeFileWiring.test_fresh_hard_gauge_sibling_of_spine_...`: a real `gauge.json` dropped as the spine's sibling is read by #181's real `read()` and drives a real HARD refusal via `main()`. Not a silent no-read.

### Gate-boundary-only (no mid-gate check)
Only two call sites exist: `checklist_engine.py:1616` (`current(cl) + _trip_advisory(...)`) and `:1631` (`_trip_hard_gate(...)`, guarded by `if v == "advance"`). No other verb is touched; no mid-gate check was added. The SOFT advisory can appear on any `current` (read-only, never forces); the only forcing point is the `advance` gate boundary. Matches the accepted-limit design. PASS.

### File fence
```
git diff e2b8005...HEAD --name-only
  scripts/checklist_engine.py
  tests/test_checklist_engine.py
```
`gauge_reader.py` NOT modified (count 0 in the diff). Fence holds.

---

## Full engine test suite (independent run)

```
PYTHONIOENCODING=utf-8 py -m pytest tests/test_checklist_engine.py -q
........................................................................ [ 39%]
...................................................... [ 69%]
.......................................................                  [100%]
181 passed, 18 subtests passed in 14.07s
```
The two new classes (`TripTwoBandGatePolicy`, `TripRealGaugeFileWiring`) contribute exactly **15** tests (`15 passed` when run alone). `181 − 15 = 166` prior tests — **the 166 pre-existing tests are intact** (the verb functions were kept pure, so exact-equality assertions are unchanged).

---

## Findings

None blocking. Verb purity preserved, fail-safe posture consistent with the rest of the governor, path pairing correct, ordering sound.

Minor / non-blocking observations (no action required for this issue):
- `_trip_hard_gate` keys off the `--id` argument passed to `advance`. If an agent runs `advance g2` while `g2` is `pending` and fill ≥ hard, it gets the HARD "request a refresh for g2" message before the ordinary "g2 is 'pending', must be in-progress" refusal. Cosmetic — the advance would fail regardless — but the message references a non-active gate. Not worth changing.
- The `ROLLOUT CAVEAT` in the code comment (do not exercise HARD in production until #183 tier-skill wiring lands) is correctly scoped as a rollout-ordering constraint, not a build dependency. Noted for the Admiral's sequencing, not a code issue.

**APPROVE.**
