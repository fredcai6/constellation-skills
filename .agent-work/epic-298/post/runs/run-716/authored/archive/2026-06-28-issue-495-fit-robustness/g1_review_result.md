# Review Result — G1 Diagnosis (#495 physics fit robustness)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` (`execute.json` `g1-review`) — independent verification of an EVIDENCE-ONLY diagnosis of issue #495. No `src/` diff.

## Result
`APPROVE`

The premise-overturning claim (PR #548 already fixed 18/19; exactly one live bug remains: Saudi Arabia DEV) is **independently reproduced and confirmed**. Every static source claim checked against the tree holds. No `src/` changes. All 11 survey checks pass.

---

## Handoff compliance
Satisfied. The diagnosis delivers every handoff ask: re-measured the current failure population (19 cases re-run, §2 table), root-caused each pattern with real reproduced evidence (NoneType §3, interleaved §4, Saudi DEV §5), enumerated the `fit_status` set from source (§6), and named exact fix loci with `file:line` (§8). The premise-overturn is correctly surfaced as the headline. All within evidence-only scope; no stop conditions triggered.

## Scope drift
None. `git status --short src/` is empty on branch `fix/495-fit-robustness` HEAD `bac0e96b` (independently verified). Reproduction went through public seams; the broad-except was bypassed by calling the inner chain directly from probe scripts, not by editing `src/`. Telemetry store read-only. Only the diagnosis report, result, and throwaway probes were written under `.agent-work/`. No specific exclusions touched.

## Evidence verdict
Satisfied and **independently reproduced** (not accepted on trust). I wrote a fresh probe (`.agent-work/issue-495-fit-robustness/g1-review/rev_probe.py`) and re-ran from scratch on HEAD `bac0e96b`. Log: `.agent-work/issue-495-fit-robustness/g1-review/rev_probe_output.log`.

### PART A — independent re-run of claimed already-fixed cases (≥3 required; ran 4)
All return `fit_status="ok"`, numbers matching the diagnosis §2 table **exactly**:

```
[ok] Bahrain    ALO: n_fly=5 n_samp=1796 err=None
[ok] Japan      PIA: n_fly=4 n_samp=1393 err=None
[ok] Azerbaijan GAS: n_fly=1 n_samp=412  err=None
[ok] Canada     HUL: n_fly=8 n_samp=2591 err=None
```
The "18/19 already fixed" claim is **real, not assumed**. (ALO + HUL were NoneType; PIA + GAS were interleaved — both originally-failing pattern families covered.)

### PART B — independent reproduction of Saudi Arabia DEV (the one live bug)
```
fit_driver: status='error'
  error='zero-size array to reduction operation minimum which has no identity'
  n_fly=0
driver_num(DEV)=21
session-wide pos stream N = 5006
session-wide spd stream N = 0   (EMPTY=True)

raw inner traceback:
  File ".../src/preprocessing/trajectory/calibration.py", line 879, in calibrate_session_hp
    tc_min, tc_max = float(tc.min()), float(tc.max())
  File ".../numpy/_core/_methods.py", line 45, in _amin
    return umr_minimum(a, axis, None, out, keepdims, initial, where)
ValueError: zero-size array to reduction operation minimum which has no identity
```
All three sub-claims confirmed: (a) fails with the named `zero-size array … minimum` error; (b) origin is `calibration.py:879` (`tc.min()` in the `windows=` branch), reached *before* `fit_stint_hp`'s `len(tcs)<1` guard at line 343; (c) DEV's speed stream is genuinely **empty session-wide** (spd N=0 with pos N=5006), so window-widening cannot help → skip-clean is the right call.

### Static source confirmations (verified directly against the tree)
- `calibration.py:877–891` — the `if windows:` block; `tc.min()` at **879** runs on a possibly-empty `tc` before any guard. **Confirmed.**
- `calibration.py:343` — `if len(tps) < 1 or len(tcs) < 1: return None` inside `fit_stint_hp`. **Confirmed** (and confirmed it runs too late for the windows= crash).
- `calibration.py:898–902` — typed `ValueError("no_accel_samples: …")` when `hp is None`. **Confirmed.**
- `session_fit.py` is the only `FitRecord` producer; `fit_status` assigned at exactly two sites: `record_from_params` (:79, `"ok"`) and `_err` (:215, takes `status`). `_err` is called with `no_laps` (:241,:285), `no_accel_samples` (:312, mapped from `ValueError` `startswith("no_accel_samples")` at :310–312), `error` (:314 ValueError catch-all, :317 Exception catch-all). **Valid set = {ok, no_laps, no_accel_samples, error} confirmed.**
- `fit_store.py:34` reads `# "ok" | "error" | "no_laps"` — omits `no_accel_samples`. **STALE, confirmed.**
- `loaders.py:393` — `movc = Vkmh > 0` is the empty-stream source for DEV. **Confirmed.**

## Code/doc quality
Inherited project/section rules met:
1. **Verify-seam-against-source** (CREW_CONTEXT operating discipline): the implementer verified the cited seam and **caught** the handoff's incorrect claim that `fit_session_full` is a per-session batch looper — it is the single-driver P1 diagnostic; `fit_batch.run_batch` is the looper. Exactly the discipline the rule demands.
2. **`py` launcher** used throughout (verified in evidence block and my own re-run).
3. **`constraint:physics_region_no_evo_import`** honored — reproduction stayed in `src/physics` + `src/preprocessing`, no evo import.
4. **Fail-visibly** — the residual bug is a visible crash, correctly identified, not masked.
5. No `simplification_limits` run needed (zero `src/` Python changed); no region tests required (evidence-only, no behavior change).

## Map impact verdict
- **Evidence supports claimed change:** Yes — every Map-Impact claim (18/19 fixed; 1 residual empty-speed-stream bug in the windows= path) is backed by reproduced logs, and I independently re-derived the headline numbers.
- **Constraints not violated:** Yes — `physics_region_no_evo_import` and evidence-only both honored.
- **Notes match the diff:** N/A diff (evidence-only); the structural anchors named in Map Impact all verified against current source (calibration.py:879/343/898, session_fit emitters, loaders.py:393, fit_store.py:34).
- **Decision candidates surfaced:** Yes — typed-skip naming (`no_speed_stream` vs reuse `no_accel_samples`) and the recover-vs-skip boundary are surfaced for the human decide-fix checkpoint, not decided.
- **Durable context routed:** Yes — the handoff's `fit_session_full` mischaracterization is flagged for Cartographer; `fit_store.py:34` drift named as a fix locus.

## Reconciliation check
No architecture divergence requiring Commander reconciliation beyond two correctly-routed items: (a) the handoff/parent-prompt claim that `fit_session_full` is the per-session batch looper is **wrong** (durable-context drift → Cartographer); (b) `fit_store.py:34` docstring drift (named fix locus). Both handled per discipline.

## Blockers
- None.

## Out-of-scope observations
- **Stale OLD store:** `data/physics_fits.db` (built 2026-06-23, pre-#548) is stale; a re-fit of all 2023-Q on current code would shrink recorded failures 19→~2. Rebuild after the fix lands (already anticipated by the G3 lean validation). [triage candidate `tc1`]
- **Thin fits:** several cases now return `ok` with very few flying laps (Azerbaijan GAS `n_fly=1 n_samp=412`; Japan MAG / Azerbaijan DEV `n_fly` 1–3). The decide-fix "no second-class fits" bar may want a minimum-flying-laps / minimum-sample sanity floor. For the human decide-fix checkpoint, not decided here. [triage candidate `tc2`]

## Workflow Feedback
Mandatory section. Workflow signal, not project signal.

- **Handoff gaps:** None in the reviewer handoff itself — it was precise and named the exact independent-reproduction sample (Bahrain ALO, Japan PIA, one Azerbaijan, plus Saudi DEV), the expected error string, the crash line, and the from-source `fit_status` set. The one upstream gap is the *implementer's* handoff (and the parent prompt's "Key seams"): it described `fit_session_full(...)` as the per-session batch looper, which is incorrect (it is the single-driver P1 diagnostic; `fit_batch.run_batch` is the looper). The implementer caught and worked around it; flagging here so the seam description is corrected before the fix gate inherits the same wrong anchor.
- **Context rediscovered:** None material. The handoff carried the file:line anchors I needed; I only had to read the surrounding source to confirm them (expected for a real independent re-derivation, not a gap).
- **Instructions improvised around:** None. The reviewer skill + engine covered the survey-driven flow cleanly; appending the five handoff-specific close-criteria checks (r6–r10) onto the template's r0–r5 was the sanctioned "append one check per inherited rule" path. `flag-candidate` recorded the two out-of-scope items without friction.
- **What would have made this easier:** One concrete change — correct the `fit_session_full`-as-batch-looper description wherever it lives (it propagated from the implementer's seam list into the Map Anchors), and carry forward the note that #548's `windows=` branch is a *new* code path whose own empty-stream pre-guard edge case is exactly where the one residual bug lives. Both would let the fix gate start without re-deriving the seam.

## Return status
`complete`
