# Cold plan critic result — #644

Dispatched a no-authoring-context subagent to independently re-verify the plan's 5 load-bearing
claims against source and critique Candidate A.

## Verification claims — all 5 CONFIRMED against source
1. `run.py:26-38` guard shape confirmed exactly as described.
2. `src/physics/__init__.py` imports submodules that pull in numpy/pandas/scipy transitively;
   inserting the guard at the top runs before those imports. Confirmed.
3. No `import torch` anywhere under `src/physics/`. Confirmed (grep empty).
4. `scripts/nuisance_sensitivity.py` imports `src.physics.longitudinal_fit`. Confirmed.
5. Python parent-package-first import order reasoning (Candidate B's correctness gap) is
   correct. Confirmed.

## Findings

- **[import-order-correctness] BLOCKING, re-scoped after wider verification — disposition:
  resolve empirically, not by design change, per Pre-Ruling 3.** `scripts/
  nuisance_sensitivity.py` does `import numpy as np` (line 27) BEFORE `from src.physics.
  longitudinal_fit import MASS_KG` (line 29). Commander follow-up widened the check with a
  repo-wide scan (`grep -n` numpy/pandas-import-line vs `src.physics`-import-line across every
  `scripts/*.py`): **the pattern is NOT isolated to nuisance_sensitivity.py — 48 of the
  physics-touching scripts under `scripts/` import numpy/pandas before any `src.physics`
  submodule.** The critic's narrower "patch this one file" framing (my first-pass disposition)
  rested on a false premise (unverified claim that other scripts don't share the pattern) and
  is corrected here.
  Whether the ordering matters turns on ONE fact: does OpenBLAS/MKL spin up its native thread
  pool at `import numpy` (eager — Candidate A would need to run before literally every
  `import numpy`, which none of these scripts satisfy, and Candidate A would be broadly
  insufficient), or lazily on the first heavy BLAS-call (matching `run.py`'s own comment on
  torch's lazy first-forward-pass init) — in which case script-preamble import order among
  numpy/pandas/physics is irrelevant, because none of these scripts do heavy linear algebra
  during their import preamble; real computation always starts after all imports finish,
  which is after the physics-package guard has already set the env vars.
  **Disposition: do not patch per-script.** Settle this with the mandated empirical
  before/after reproduction (Pre-Ruling 3) on the named repro target
  (`scripts/nuisance_sensitivity.py`, which already has the worst-case ordering — numpy
  imported soonest before physics of the named entrypoints). If post-fix repro completes, that
  is real evidence the lazy-init model holds and Candidate A alone is sufficient for the whole
  region regardless of per-script import order. If the post-fix repro still hangs, Candidate A
  is proven insufficient and gate 1 must stop short of claiming FIXED — diagnose the true
  blocking call and float a wider recommendation per the Honest-Null Clause rather than
  silently falling back to Candidate B for 48 files.
- No other blocking findings. [intent-fit]/[testability]/[simplicity] all pass: the shared
  guard solves the stated deadlock class, is testable via one import-time env-var assertion,
  and is not over-built (no new abstraction, mirrors the shipped `run.py` pattern exactly).

## Verdict
Candidate A approved, WITH the narrow addition above folded into the gate plan (not a
redesign) — the critic's finding sharpened the plan rather than overturning it.
