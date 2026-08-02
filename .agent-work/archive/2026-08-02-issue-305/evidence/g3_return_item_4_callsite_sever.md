# Return item 4 — "evidence that #300's acceptance test can now fail"

Launch-order return item 4. **No prior gate delivered it**, and no state note claimed it — it was
unowned in the same shape #327 was. Delivered here by the Commander (`commander-305d`), because it
is a claim about the *wiring* g1 shipped, and g1 is closed.

## Method: break the CALL SITE, not the callee

The standing invariant is *to test whether wiring is real, break the CALL SITE, not the callee.*
`episode_capture.emit_step_manifest` is left working perfectly; what is severed is the engine's
**use** of it — the binding `checklist_engine.start()` / `reopen()` resolve. That is precisely the
thing #305 added and #300 never had.

**Non-destructive.** No repository file was modified. Editing the engine source was blocked (and it
would have been the wrong tool anyway); the sever is done by an opt-in `sitecustomize.py` on
`PYTHONPATH`, which Python imports at interpreter startup and which therefore reaches the
**subprocess** engine runs that an in-process monkeypatch cannot. `git status --porcelain` over
`scripts/` was empty before, during and after.

Artifacts: `sitecustomize.py` (subprocess sever, gated on `SEVER_SEAM=1`) and
`break_the_callsite.py` (pytest plugin, in-process sever) — both reproduced at the bottom.

## Result — the honest, two-part answer

**Part 1 — YES, the criterion is now falsifiable.** With the seam severed in subprocesses, the #305
negative control goes **RED**:

```
8 failed, 5 passed in 4.00s
FAILED test_claimed_parent_topology_yields_the_full_mechanical_group
FAILED test_unclaimed_child_topology_refuses_only_role_and_refusals
FAILED test_the_seam_emits_the_same_group_unasked
FAILED test_every_field_has_a_named_independent_source
FAILED test_red_proof_blunt_hardcoded_composer
FAILED test_red_proof_sharp_drops_exactly_one_derivation
FAILED test_red_proof_sharp_fabricated_role
FAILED test_red_proof_sharp_inflated_reopens
```

Sever confirmed genuinely active before trusting the red (the mutation-that-did-not-apply trap):
`emit_step_manifest is: <function <lambda> at 0x...>`.

Before #305, `produce()` had **zero callers**, so #300's AC1 — *"a manifest is produced on every
deterministic assembly"* — was true **definitionally, over zero assemblies**, and no mutation could
falsify it. It can now be falsified. **Return item 4 is satisfied.**

**Part 2 — but the falsifiability lives in #305's control, NOT in #300's own tests.**

With the same call site severed **in-process**:

```
tests/test_context_manifest.py + tests/test_episode_capture.py
94 passed, 63 subtests passed in 7.55s
[break_the_callsite] severed call site was reached 0 time(s) in-process
```

**All 94 stay green, and the call site is never reached at all.** Those files exercise the
**callee** — `build_manifest`, `write_manifest`, `emit_step_manifest` invoked directly — and never
drive `checklist_engine.start()` in-process. So #300's own acceptance test *still* cannot fail from
a broken seam; what can now fail is #305's negative control.

That distinction matters for anyone reading `main` later: **do not delete or weaken
`tests/test_episode_negative_control.py` believing `test_context_manifest.py` covers the wiring.**
It does not. The reached-count of `0` is the measurement, not an inference.

## A weakness worth recording (not a blocker)

The severed-seam red is a **crash**, not a diagnosis: `FileNotFoundError` at
`test_episode_negative_control.py:308`, rather than a named per-field mismatch. The control is
falsifiable, but for a *missing seam* it reports "a file was not where I looked" — which is the same
shape as the #360 path-derivation mistake that cost this gate its one red round-trip. A reader
debugging a severed seam would have to know that already. Candidate follow-up, not a defect in the
capability.

## Reproduce

```bash
cd "C:/Programs/constellation-skills-wt/e298-305"
export PYTHONPATH=<dir holding the two scripts below>

# subprocess sever -> the control goes RED
SEVER_SEAM=1 python -m pytest tests/test_episode_negative_control.py -q

# in-process sever -> #300's own tests stay GREEN and never reach the call site
python -m pytest tests/test_context_manifest.py tests/test_episode_capture.py -q -p break_the_callsite
```

### `sitecustomize.py`

```python
import os
if os.environ.get("SEVER_SEAM") == "1":
    import sys
    from pathlib import Path
    scripts = Path("C:/Programs/constellation-skills-wt/e298-305/scripts")
    if scripts.is_dir():
        sys.path.insert(0, str(scripts))
    try:
        import episode_capture
        episode_capture.emit_step_manifest = lambda *a, **k: None
    except Exception:
        pass
```

### `break_the_callsite.py`

```python
import sys
from pathlib import Path

def pytest_configure(config):
    scripts = Path("C:/Programs/constellation-skills-wt/e298-305/scripts")
    if scripts.is_dir():
        sys.path.insert(0, str(scripts))
    import checklist_engine
    calls = {"n": 0}
    def severed(*_a, **_k):
        calls["n"] += 1
        return None
    checklist_engine.emit_step_manifest = severed
    config._severed_calls = calls

def pytest_unconfigure(config):
    calls = getattr(config, "_severed_calls", {"n": 0})
    print(f"severed call site reached {calls['n']} time(s) in-process")
```
