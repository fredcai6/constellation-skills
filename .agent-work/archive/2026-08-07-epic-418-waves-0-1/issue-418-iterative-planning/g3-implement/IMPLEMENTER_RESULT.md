# G3 Implementer Result — Evidence Repair

`gate_id: g3`  
`change_type: tests-only evidence repair`  
`mutation_red_exit: 1`  
`green_exit: 0`  
`diff_digest: sha256:e087a982015aa0796554604746f759532b616e9390df5bff1cb6acb5b59d6070`

## Outcome

Repaired only the causal construction of the zero- and multiple-transition audit tests in `tests/test_iterative_planning_doctrine.py`. Production behavior remains exactly as approved by review 4.

Both audit-cardinality cases now use an otherwise-valid, applicable `advance` result and audit lines whose decision matches `advance`:

- zero matching transition entries must refuse;
- two matching transition entries must refuse.

Because `advance` is launch-authorized, these cases reach `_verify_transition_audit` instead of short-circuiting on the intentional `repair` hold. The accumulated launch table is unchanged and still exercised: applicable `advance`/`replan` authorize; `repair`, `stop`, and `applicable:false` refuse.

## Causal mutation evidence

After changing the fixtures, I temporarily removed only the call to `_verify_transition_audit`, ran the exact focused suite, and observed both named assertions fail because prelaunch incorrectly returned success:

```text
uv run python -m pytest -q tests/test_explorer_templates.py tests/test_iterative_planning_doctrine.py
2 failed, 36 passed, 6 subtests passed in 2.01s
```

The two failures were independently reported as:

```text
audit_cardinality='zero': AssertionError: 0 == 0
audit_cardinality='multiple': AssertionError: 0 == 0
```

The exact production audit call was then restored. The same suite passed:

```text
36 passed, 8 subtests passed in 1.94s
```

This proves each assertion is sensitive to audit enforcement and cannot pass through an earlier authorization refusal.

## Required verification

```text
uv run python -m pytest -q tests/test_install_constellation.py
108 passed, 379 subtests passed in 14.36s

uv run python -m pytest -q tests/test_initial_issues.py tests/test_replan.py tests/test_init_work_area.py
62 passed, 59 subtests passed in 0.37s
```

The reviewer-3 installed matrix was rerun. It passes path, installed-command, Explorer/Commander artifact, generic G2 variant, audit-cardinality, and repair-drift checks before reaching its intentionally obsolete assertion that repair should authorize; it exits there with `REFUSED: only advance or replan may authorize NEXT_WAVE`. Review 4 already approved that production behavior, and the focused real-install test is the current full matrix with causal authorized audit inputs.

All three role spine JSON files parse. Scoped `git diff --check` passed. Canonical path audit found no old source-only sibling names. The restored helper remains standard-library-only with no network, tracker, subprocess, or direct `gh` seam.

## Review identity

Digest algorithm: ordinal-sort the exact inventory, then SHA-256 the concatenation of `UTF-8(path)`, NUL, raw file bytes (or `<deleted>`), NUL for each path. `G3_DIGEST_PATHS.txt` and `recompute_g3_digest.ps1` persist the inventory and algorithm.

Inventory (9 paths):

```text
scripts/install_constellation.py
scripts/verify_iterative_role_artifacts.py
skills/admiral/SKILL.md
skills/admiral/templates/ADMIRAL_SPINE.template.json
skills/commander/references/commander-core.md
skills/commander/templates/COMMANDER_SPINE.template.json
skills/explorer/SKILL.md
skills/explorer/templates/EXPLORER_SPINE.template.json
tests/test_iterative_planning_doctrine.py
```

## Scope and map impact

There is no new structural, capability, authority, or constraint impact. This repair changes test inputs only so existing exact-one audit enforcement has causal regression evidence. No production, doctrine, schema, engine, tracker/network, history, or unrelated file was changed. Unrelated dirty-worktree changes were preserved.

## Workflow feedback

The evidence-repair handoff was complete and sharply scoped. The mutation requirement was especially useful: a green negative test is not evidence until bypassing its named guard makes it red. Future decision-table changes should re-audit every downstream negative fixture for earlier-branch short circuits.

Fresh independent G3 evidence review remains required.
