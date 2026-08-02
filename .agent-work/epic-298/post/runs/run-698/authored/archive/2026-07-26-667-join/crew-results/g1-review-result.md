# Review Result — g1 (issue #667, epic #659, "the join")

## Assigned Gate
`g1` — NEW `src/physics/fingerprint/join.py` + NEW `tests/unit/physics/fingerprint/test_join.py`

## Result
`APPROVE`

## Reproduced evidence (verified against the world, not the claim)

### pytest (18/18, pinned interpreter)
```
$ "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join.py -q
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-667
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 18 items

tests\unit\physics\fingerprint\test_join.py ..................           [100%]

============================= 18 passed in 0.47s ==============================
```

### simplification_limits (the handoff's positional invocation was malformed — argparse needs `--paths`)
```
$ "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" src/utils/simplification_limits.py --paths src/physics/fingerprint/join.py tests/unit/physics/fingerprint/test_join.py
PASS (2 files checked)
EXIT=0
```

## Handoff compliance
Delivered exactly what was asked: a PURE `join_weekend_prior(...)` + `WeekendUtilizationPrior`
normalized-weighted-average join with honest Student-t sigma, plus the 4 T7 invariants + T7-5
general case. No sequence/interaction/bespoke forms (those are #670). Student-t output via
`predictive_t`, no baked-in normality.

## Scope drift
Clean. `git status` shows only the two NEW files (+ this `.agent-work` review area). No committed
`data/*.db`, no map edits, no other-module changes. The linear join IS the prior — the `#670`
exclusion is respected.

## Evidence verdict
Required evidence present and independently reproduced (above). The correctness gate is the T7
invariants + T7-5 general case (a mechanically-broken join can beat a baseline via compensating
errors), not an outcome win — those are asserted EXACTLY in the tests and confirmed by hand below.

## Close-criterion pass/fail

- **Join arithmetic** — PASS. `w_i = comp_i / corner_share` (weights sum to 1); `corner_share =
  math.fsum(comps)`, NOT renormalized to 1.0; `prior_mean = fsum(w*m)/resolved_weight == mu_res`.
- **T7-1 uniform ⇒ unweighted cell mean** — PASS. Test asserts EQUALITY (`pytest.approx`) to
  `sum(means)/len(means)` (=21 for means [10,20,33]); comparator documented as `mean(means)`.
- **T7-2 identical cells ⇒ constant** — PASS (15.0 for any composition).
- **T7-3 single-class ⇒ that cell** — PASS. `mean == 12.0`; `combined_scale == 0.25` (the cell's
  sigma) verified via closed form `scale == 0.25*sqrt(1 + 1/8)`, `n_eff == support 8`.
- **T7-4 soft memberships + corner_share != 1.0** — PASS. `corner_share == 0.6`, weights
  `(0.2/0.6, 0.3/0.6, 0.1/0.6)`.
- **T7-5 distinct shares × distinct means (the broken-join catch)** — PASS, HAND-RECOMPUTED.
  means [10,20,30], comp {.2,.3,.1}, `corner_share = 0.6`, weights (1/3, 1/2, 1/6):
  `mean = 10/3 + 10 + 5 = 55/3 = 18.3333`. The two bugs give DIFFERENT values —
  divide-by-k = `60/3 = 20`, unnormalized-sum = `0.2·10 + 0.3·20 + 0.1·30 = 11` — and the test
  asserts `mean != approx(20)` AND `mean != approx(11)`. Because `corner_share = 0.6 != 1.0`, the
  normalized answer is distinct from both; the numbers genuinely discriminate the bugs. This is the
  load-bearing check and it holds.
- **σ propagation** — PASS. `combined_scale = sqrt(Σ_res w²σ² + (weight_on_thin·σ_unres)²)`;
  `σ_unres = max(cross-class mean spread, max_resolved_σ)` so it CAN EXCEED the resolved σ;
  `n_eff = n_eff_res·(1−weight_on_thin)`, `n_eff_res = 1/Σ(w²/support)`.
- **Numeric thin-widening (guards the cold-critic BLOCKER)** — PASS, HAND-CHECKED. Same inputs,
  flip highest-weight class sev1 resolved→unresolved: `spread = pstdev([10,30]) = 10` ⇒ `σ_unres =
  10` ⇒ `combined_scale ≈ 5.0`, vs all-resolved `≈ 0.064`. STRICTLY WIDER, and the unresolved term
  (~5.0) dwarfs every resolved σ (0.1): the unresolved path FATTENS, it does not cap.
- **Thin surfacing / both channels symmetric** — PASS. All-resolved ⇒ `thin_classes == ()`,
  `weight_on_thin == 0.0`; one unresolved ⇒ `thin_classes == ("sev1",)`,
  `weight_on_thin == 0.3/0.6`. `test_both_channels_symmetric` gives identical priors on
  utilization/energy.
- **Loud refusals** — PASS. Six ValueError tests (missing composition key, corner_share<=0,
  vocabulary_version, channel, driver, class-order) + resolved-cell field guard. Zero-resolved ⇒
  fully-thin `prior=None`/`mean=None`, never fabricated.
- **Purity** — PASS. `join.py` imports only `math`/`statistics`/`dataclass`/`typing` + `student_t`
  + `FingerprintCell`(store)/`ClassVocabulary`; opens no DB connection, no FastF1. `FingerprintCell`
  is used in annotations only (`from __future__ import annotations`). `store.py` transitively pulls
  stdlib `sqlite3` only (no fastf1/f1_data). No new frozen literal minted.
- **simplification_limits** — PASS on both files.

## Flagged adjudications

1. **`_N_EFF_FLOOR = NU_FLOOR - 2.0` (== 1e-6): DERIVED structural guard → APPROVE (not an F12
   concern, does not float to Admiral).** It is algebraically the finite-variance margin that
   `NU_FLOOR` (`2.0 + 1e-6`) already carries — no new magic number is typed, and the `2.0` is the
   Student-t variance-finite threshold (a mathematical fact, ν>2), not a tuned value. Its purpose is
   structural: `predictive_t` rejects `n_eff <= 0`, so this keeps `n_eff` strictly positive (and, for
   a tail rule whose `nu_prior` sits exactly at `NU_FLOOR`, keeps predictive ν just above the floor).
   It bites only in a near-degenerate resolved-weight≈0 case (already handled by the fully-thin
   branch) and then yields the FATTEST/most conservative tail — it never tunes a prediction and
   encodes no empirical/#675 number, so the F12 pre-registration discipline does not apply. It is a
   derived guard, not a minted frozen literal.

2. **Independent-cell σ assumption: stated honestly, NOT over-claimed → APPROVE.** The module
   docstring's "Build-1 simplification (stated honestly)" block explicitly labels `Var = Σ w²σ²` as
   treating the k cells as INDEPENDENT/uncorrelated, notes real cells share a driver and a session
   and "are almost certainly correlated," and calls it "a deliberate Build-1 simplification, not a
   measured claim." No claim of full correlation-honesty is made.
   `test_docstring_states_independent_cell_simplification` pins the caveat present.

## Map impact verdict
The implementer's `Map Impact` notes are accurate and match the diff: NEW leaf pure module + test
(exactly the inbound anchors), capability `weekend-utilization-prior`, both inbound decisions
honored — `decision:join-is-normalized-weighted-average` (settled/inherited) implemented as
specified, `decision:sigma-propagation-quadrature-fat-unresolved` (guess) implemented as the settled
candidate and settled empirically by the thin-widening test. No missing or overstated structural /
capability / constraint / decision impact.

## Refactoring pass (Fowler)
Record: `.agent-work/667-join/g1-review/fowler_pass.json`; `verify_fowler_pass.py` → exit 0
(`smells=12, flagged=[], overridden=['long-parameter-list']`). 11 smells absent; `long-parameter-list`
(join_weekend_prior's 7 params) OVERRIDDEN with a logged standard — global-crew "explicit contracts
at meaningful boundaries" + the deep-module doctrine that a pure function's interface IS its explicit
injected deps (the `rule`/`nu_loss` params are the `predictive_t` seam; a parameter object would hide
that seam).

## Blockers
- None.

## Out-of-scope observations
- NON-BLOCKING (handoff pre-authorized the type import): `join.py` imports `FingerprintCell` at
  runtime (`from src.physics.fingerprint.store import FingerprintCell`), which transitively imports
  stdlib `sqlite3`. It is used in annotations only, so a strict-purity refinement could guard it
  under `if TYPE_CHECKING:`. Harmless (no DB opened, no FastF1), not a defect — noted only as a
  possible future tidy.

## Workflow Feedback
- **Handoff gaps:** The `simplification_limits` verification command was malformed — it passed the
  two files as bare positional args, but the script's argparse requires `--paths <files>` (bare
  positionals raise `unrecognized arguments`). The handoff even warned about an editable-`.pth`
  worktree trap on the `-m` form but not about this flag error. Corrected to
  `simplification_limits.py --paths <files>` (exit 0). Name: "Verification Commands".
- **Context rediscovered:** Had to open `frozen_constants.py` myself to adjudicate the `_N_EFF_FLOOR`
  frozen-literal question against the actual F12 constant set — the handoff flagged the question but
  did not point at the frozen-constant registry that defines what "minted frozen literal" means here.
- **Instructions improvised around:** The reviewer skill notes survey-type `refresh-request` display
  is a known engine gap; not hit this run (no trip fired). None else.
- **What would have made this easier:** Fix the `--paths` flag in the handoff's Verification Commands
  block and cite `src/physics/fingerprint/frozen_constants.py` next to the `_N_EFF_FLOOR` adjudication
  ask.

## Return status
`complete`
