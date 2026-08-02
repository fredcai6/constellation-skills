# Design-it-twice: where the thread-cap guard lives

## The one thing being designed twice
The seam placement for the headless thread-cap guard that unblocks
`scripts/nuisance_sensitivity.py`, `src/physics/session_fit.py` (`load_quali_session`), and
`src/physics/layer2/estimate_store.py`-adjacent fit paths.

## Count and panel — a surfaced choice
**2 candidates, single-author (not parallel subagents).** This is a fairly-easy call per
`design-it-twice-brief.md` §Count ("a fairly-easy call → 2, or a single with the alternatives
named as untaken roads") — one load-bearing decision (seam placement) with an obvious
precedent (`run.py`'s existing #623 fix) to mirror, on a bounded/mechanical fix (Pre-Ruling 1
forbids estimator/fit-logic changes, shrinking the design space to "where does an
environment-cap block go"). Both candidates authored directly rather than dispatched to two
parallel subagents, given the low ambiguity; a cold critic with no authoring context reviews
the converged pick below to backstop that judgment (see CRITIC_RESULT.md).

## The constraints (one per candidate)

**Candidate A — best-seam-placement:** one shared guard at the lowest common import point
every fit path passes through.

**Candidate B — smallest-diff:** patch each named fit entrypoint script individually with its
own copy of the guard, touching only the files the launch order names.

## Candidate A — shared guard in `src/physics/__init__.py`

Add the guard (env-var `setdefault` × 4 + defensive `torch.set_num_threads(1)`) at the very
top of `src/physics/__init__.py`, before its existing submodule imports. Every
`src.physics.*` import — direct or transitive — executes this first, because Python always
runs a parent package's `__init__.py` before any of its submodules.

- **Depth:** high — callers get the fix for free; no caller needs to know it exists.
- **Locality:** single file changed; the fix lives exactly once.
- **Seam placement:** matches the region boundary in `docs/agents/ORCHESTRATOR_CONTEXT.md`
  (physics is its own architecture region) — the guard becomes a property of "importing the
  physics region," not of any one script.
- **Testability:** one test (import `src.physics`, assert env vars set) covers every current
  and future fit entrypoint; a regression test at `scripts/nuisance_sensitivity.py` alone
  would miss `session_fit.py` called directly, or a future third entrypoint.
- **Risk:** every physics import now pays the cap, including interactive/non-headless
  callers — but the cap is `setdefault`-based (never overrides an operator's explicit
  setting) and single-threaded BLAS is the existing behavior of `run.py`'s already-shipped
  evo path, so this is consistent with precedent, not a new risk class.

## Candidate B — per-entrypoint patches

Add the same guard block redundantly to the top of `scripts/nuisance_sensitivity.py`,
`src/physics/session_fit.py`, and `src/physics/layer2/estimate_store.py`.

- **Depth:** low — the fix is a caller-side responsibility repeated N times; a new fit
  entrypoint written tomorrow silently lacks it (exactly the failure mode that let #644 recur
  after #623 supposedly fixed the class).
- **Locality:** fans out across 3+ files today, more as new entrypoints are added; a future
  edit to the cap values (e.g. widening thread count) needs an N-way find-and-replace.
- **Seam placement:** puts an import-order concern in each leaf script rather than at the
  package boundary; also incorrect for `session_fit.py`/`estimate_store.py`, which are
  imported as *library modules* by other code (e.g. `src/physics/__init__.py` itself imports
  `apex_extract`, `braking_fit`, etc.) — patching only session_fit.py's own top would not run
  before *its own* imports of numpy/pandas happen at `src/physics/__init__.py` import time if
  the caller imported the package first, since Python only runs each module body once, at its
  own import point, not retroactively before earlier-imported siblings.
- **Testability:** needs a test per patched file, and every future entrypoint needs its own
  test too.

## Compared and converged: **Candidate A**

Depth and locality both favor A outright, and B has a load-bearing correctness gap:
`src/physics/__init__.py` already imports several submodules (`apex_extract`, `braking_fit`,
`traction_fit`, `capability_envelope`, …) at package-import time, so any B-style patch placed
inside `session_fit.py` or `estimate_store.py` would run *after* `src/physics/__init__.py`'s
own submodule imports already happened when the physics package is imported first (the common
case for every named entrypoint) — B does not reliably run before the risky numpy/scipy
thread-pool init it is meant to guard. A closes that gap by construction (parent-first import
order is a Python guarantee, not a convention) and matches the "single shared import-time
guard in a low-level physics module every fit path imports" instruction in the launch order
verbatim. Recommendation: **Candidate A**, no hybrid needed.

## Untaken-road record
- No 3rd/4th seam-placement candidate (e.g. a `conftest.py`-style auto-import hook, or a
  `sitecustomize.py` process-wide hook) was generated — judged genuinely out of proportion for
  a bounded, single-package fix; a process-wide hook would silently affect non-physics code
  too, which is broader than Inherited Latitude ("no production-default change beyond
  threads") supports without a separate decision.
- Parallel-subagent authorship of A and B (rather than single-author) was skipped as
  genuinely-trivial for this fairly-easy call; the cold critic substitutes for the missing
  independent-authorship check.

## Panel-vs-single record
Single-author, 2 candidates, per the "fairly-easy call" scaling rule — restated here for the
plan-approval checkpoint. A human/Admiral may overturn this scaling and demand a parallel
panel; none is expected given the bounded, single-decision nature of the fix.

## Post-critic correction (see CRITIC_RESULT.md)
The cold critic surfaced, and a repo-wide follow-up scan confirmed, that MOST
physics-touching `scripts/*.py` (48 of them, not just `nuisance_sensitivity.py`) import
numpy/pandas before any `src.physics` submodule — so Candidate A's guard fires after numpy is
already imported in nearly every script. This does not change the recommendation (still
Candidate A, not Candidate B): the open question is whether OpenBLAS/MKL's thread pool inits
eagerly at `import numpy` or lazily at first heavy BLAS call, and execute.json g1's empirical
before/after reproduction on the named repro target is the check that settles it, per
Pre-Ruling 3. A hang that survives the fix falsifies Candidate A for the whole region and is
grounds to float per the Honest-Null Clause rather than silently expanding to per-script
patches.
