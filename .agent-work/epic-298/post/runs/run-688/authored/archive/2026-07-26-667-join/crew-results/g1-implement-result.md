# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` (issue #667, epic #659 Wave 4a — "the join")

## Completed slice
Built the pure weekend-utilization-prior join and its T7 gating tests, driven through the
engine as a 4-item gated plan (m0-context -> m1 refusals/thin -> m2 T7 join+sigma -> m3
verify), TDD red->green on each implementation slice.

- `join_weekend_prior(composition, cells, vocabulary, *, as_of_round, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule(), map_version=None) -> WeekendUtilizationPrior`
- Join = NORMALIZED WEIGHTED AVERAGE: `w_i = comp_i / corner_share` (corner_share = Σ comp_i, NOT renormalized to 1.0); `prior_mean = μ_res`, unresolved cells fall back to μ_res so the mean never silently shifts.
- σ propagation (pinned quadrature): `combined_scale = sqrt(Σ_res w_i²σ_i² + (weight_on_thin·σ_unres)²)`, `σ_unres = max(cross-class spread of resolved means [pstdev, range/2 if <2], max_resolved_σ)` so an unknown class WIDENS (can exceed resolved σ), never caps. `n_eff = n_eff_res·(1−weight_on_thin)` with `n_eff_res = 1/Σ_res(w_i²/support_i)`, floored so `predictive_t` stays valid. Wrapped in `predictive_t` (Student-t, no baked-in normality).
- Zero-resolved (no resolved weight) => fully-thin prior (`prior=None`, `mean=None`, `weight_on_thin=1.0`, `thin_classes=all`), surfaced loudly.

## Scope
**Files changed:**
- `src/physics/fingerprint/join.py` (NEW, ~215 lines)
- `tests/unit/physics/fingerprint/test_join.py` (NEW, 18 tests)

**Specific exclusions touched:** no. No store/DB/FastF1 read inside the join; no new frozen literal (see Assumptions re: the derived `_N_EFF_FLOOR`); no sequence/interaction forms (#670); did not touch the cell-store read API or #668/#670 surface. Did not add an export to `__init__.py` — the package initializer is intentionally import-free (submodules imported directly), so matching convention means NOT re-exporting.

## Behavior changed
Yes — new pure capability: compose a circuit's per-class corner time-share composition
with a driver's fingerprint cells into one per-weekend quali-side utilization prior with
honest Student-t σ. No existing behavior altered (net-new module).

## Map Impact
- **Structural anchors touched:** `src/physics/fingerprint/join.py` (NEW pure module) + `tests/unit/physics/fingerprint/test_join.py` (NEW), exactly the inbound structural anchors.
- **Capabilities added:** `weekend-utilization-prior` — compose circuit composition × driver fingerprint into a Student-t prior; now observable via `join_weekend_prior`.
- **Constraints/assumptions honored:** normalized-weighted-average (forced by T7-1); composition sums to corner share, no renormalize; thin exposure surfaced (`thin_classes`/`weight_on_thin`) not discounted; vocabulary-version pinned with loud refusal; independent-cell (uncorrelated `Var=Σw²σ²`) stated as a Build-1 simplification in the module docstring.
- **Decisions honored:** `decision:join-is-normalized-weighted-average` (settled/inherited) — implemented as specified. `decision:sigma-propagation-quadrature-fat-unresolved` (guess) — implemented the settled candidate form exactly; the numeric thin-widening test settles it empirically (flip resolved→unresolved => strictly wider prior scale).
- **Claims/evidence produced:** 4 T7 invariants + T7-5 general case + σ thin-widening + σ monotonicity + thin surfacing + both-channels-symmetric all pass exactly (see Evidence).
- **Triage candidates:** none new beyond the already-routed follow-ons (#670 sequence/interaction forms; g2 store harness).

## Test mode
**Required:** test-first (TDD strongly preferred — the invariants ARE the spec).
**Satisfied:** yes — RED observed before each implementation slice (m1: ModuleNotFoundError; m2: NotImplementedError on the resolved path), GREEN after. Every Required-Evidence invariant is covered.

## Evidence

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_join.py -q
```

**Result:** pass
```
collected 18 items
tests\unit\physics\fingerprint\test_join.py ..................           [100%]
============================= 18 passed in 0.46s ==============================
```

Tests (18): missing-composition-key / corner_share<=0 / vocabulary-version / channel /
driver / class-order loud refusals; zero-resolved fully-thin; T7-1 uniform=>driver-overall
arithmetic mean; T7-2 identical cells=>constant for any composition; T7-3 single-class=>
combined_scale==cell σ AND mean==cell mean (via closed-form `scale == σ·sqrt(1+1/n_eff)`,
n_eff==support); T7-4 soft memberships flow through, corner_share==Σshares!=1.0; T7-5
distinct shares AND means == hand-computed Σ(comp_i/Σcomp)·m_i to full precision AND !=
÷k-uniform AND != unnormalized-Σcomp·m (the two common bugs can't hide); σ thin-widening
(flip resolved→unresolved => strictly wider scale); σ monotone in a resolved cell σ; thin
surfacing (`thin_classes`/`weight_on_thin`); both channels symmetric; nu<=nu_loss; docstring
states the independent-cell simplification.

```bash
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" src/utils/simplification_limits.py --paths src/physics/fingerprint/join.py tests/unit/physics/fingerprint/test_join.py
```

**Result:** pass
```
PASS (2 files checked)
exit=0
```

Deliverable-path check: `git status --short` shows both files as `??` (untracked, new);
`git check-ignore src/physics/fingerprint/join.py` exits 1 (NOT ignored). Nothing committed
or staged; no `data/*.db` or `docs/architecture/*` touched.

## TDD evidence, if required
- Failing test observed (m1): `ModuleNotFoundError: No module named 'src.physics.fingerprint.join'` (1 error during collection).
- Failing test observed (m2): `NotImplementedError: resolved join arithmetic is implemented in gate m2` — 10 failed, 8 passed.
- Passing test observed: 18 passed.
- Refactor while green: no separate refactor pass needed; code kept small (helpers `_validate_inputs`, `_resolved_prior`; both functions well under the 99-line / CC<20 limits).

## Docs/contracts touched
- none (module + tests only). The independent-cell Build-1 simplification is documented in the module docstring, per the handoff.

## Assumptions
- **`_N_EFF_FLOOR` is DERIVED, not a new frozen literal.** It equals `NU_FLOOR - 2.0` (== 1e-6), reusing the finite-variance margin `NU_FLOOR` already carries, as a strictly-positive floor so `n_eff` never reaches 0 (`predictive_t` rejects `n_eff <= 0`) and, for a tail rule whose `nu_prior` sits at `NU_FLOOR`, the predictive nu stays "just above where nu would hit NU_FLOOR" (the handoff's wording). No value is minted or tuned; it is an expression over an existing constant. If the reviewer judges this a frozen literal, it FLOATs to the Admiral (I did not inline a bare number).
- **"Pure" reconciliation.** `join.py` imports the `FingerprintCell` dataclass from `store.py` and `ClassVocabulary` from `vocabulary.py` as pure value objects (sanctioned by Allowed Scope: "Consume FingerprintCell from ...store"). These imports open no DB and call no FastF1; the join instantiates no store and reads nothing. That is the meaningful sense of the pure constraint. (Transitively, `store.py` imports `sqlite3` at module load, but no connection is ever opened by the join.)
- **"Zero resolved cells" read as "no resolved weight."** I trigger the fully-thin branch on `resolved_weight <= 0` (covers both literally-zero-resolved-cells and the exotic all-resolved-have-zero-share case), since μ_res is undefined without resolved weight. The zero-resolved test constructs all-unresolved cells, matching the handoff exactly.
- **Driver-consistency refusal added** (not in the enumerated list but consistent with "all cells share one channel"): the output carries a single `driver` field, so mixed drivers would be silent corruption. Raised as a loud `ValueError`.
- **T7-3 `combined_scale == cell σ` proven via closed form.** The dataclass field list is a closed enumeration with no raw `combined_scale` field, so the test asserts the equivalent `prior.scale == σ·sqrt(1+1/n_eff)` with `n_eff == support` — algebraically identical to `combined_scale == σ`.

## Stop conditions hit
- none. No frozen literal needed (the floor is derived); the specified σ form satisfied every invariant including the numeric thin-widening; scope was sufficient; no decision beyond authority was required.

## Out-of-scope observations
- none new.

## Workflow Feedback
- **Handoff gaps:** The **Verification Commands** simplification line is wrong two ways: (1) `py -m src.utils.simplification_limits <paths>` passes bare positional paths, but the CLI defines no positional args — it requires `--paths`; (2) the `-m` module form triggers the editable-`.pth` worktree trap (resolves `src.*` to MAIN's checkout, whose `PROJECT_ROOT` would then not contain the worktree files). I ran the equivalent that honors the intent: invoke the worktree's `src/utils/simplification_limits.py` as a file (it imports nothing from `src`, so no trap) from the worktree cwd with `--paths <two files>`. Recommend the handoff use that form.
- **Handoff tension (minor):** Close Criteria says "no store ... import inside it" while Allowed Scope says "Consume FingerprintCell from ...store". Resolved as above (value-object type import is fine; store DB API is not). A one-line note in the handoff would remove the ambiguity.
- **Context rediscovered:** none material — the seam-signature pointers in the launch message were accurate and saved rediscovery. `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR=1.0` is the store's resolved/unresolved boundary; the join treats `status` as authoritative (doesn't re-derive from support), which matches the store contract.
- **Instructions improvised around:** none — the engine template + skill covered the flow; `advance` required `--why`/`--mechanical` (documented in the rail), no surprise.
- **What would have made this easier:** fix the simplification verification command in the handoff template to the `--paths` file-invocation form.

## Return status
`complete`
