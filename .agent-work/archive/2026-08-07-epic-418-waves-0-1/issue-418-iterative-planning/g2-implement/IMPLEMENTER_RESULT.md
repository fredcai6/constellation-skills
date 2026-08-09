# G2 Implementer Result

`gate_id: g2`  
`red_exit: 1`  
`green_exit: 0`  
`diff_digest: sha256:0c8223f5d01de36dd476672f3bfb593e08f61bb0c7ee42895ba320b85b688aff`

## Outcome

Minted the lean `constellation-replan` skill with one strict, offline v1 input/result path. The verifier accepts exactly four exits (`advance`, `repair`, `replan`, `stop`), requires complete unique discrepancy and unlaunched-item dispositions, preserves open launched issues, holds the current wave and forecast on repair, permits a null current wave only on stop, and makes every fixed-boundary proposal inapplicable pending typed human escalation. Reviewer rework now also refuses multi-fixed-boundary proposals under the singular escalation schema, keeps launched and unlaunched issue identities disjoint, accepts repeated nonempty values wherever G1 does, and validates rewritten issues in the assembled result graph. The renderer emits nonempty wave-review and revised-epic Markdown.

`constellation-write-a-skill` shaped this as a lean judgment skill: action-leading steps, explicit negative space and completion, one mechanical rail, and a required fresh independent semantic review. Registration includes the installer script/reference bundles and canonical public indexes.

## TDD evidence

### Reviewer rework 1

The four adversarial regressions were added before verifier edits. The identical frozen command failed once for each reproduced P1:

```text
uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py
4 failed, 133 passed, 407 subtests passed in 13.97s
```

The failures were causal: a multi-fixed-boundary packet and launched/unlaunched collision were accepted, while exact-G1 duplicate parked values and a valid dependency on a result-wave issue were refused. After the minimal verifier and contract-prose correction, the identical command passed:

```text
uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py
137 passed, 410 subtests passed in 13.68s
```

The reviewer-authored probe now reports:

```text
REFUSED two fixed deltas with only one escalation
REFUSED launched/unlaunched identity collision
ACCEPTED exact G1 parked shape with duplicate nonempty values
ACCEPTED G1 issue replacement whose dependency exists in the result wave
{'multi_fixed_missing_escalation_accepted': False, 'launched_unlaunched_collision_accepted': False, 'exact_g1_duplicate_parked_refused': False, 'valid_contextual_issue_dependency_refused': False}
```

The graph regression additionally proves genuinely dangling and cyclic assembled graphs still fail.

### Initial implementation

Tests were authored before production behavior. The identical frozen command first failed causally on absent replanning behavior and registration, not import/path/setup:

```text
uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py
3 failed, 117 passed, 13 skipped, 364 subtests passed in 13.90s
```

The explicit load-bearing failure was: `missing replanning behavior: strict verifier/renderer and v1 templates are not minted`.

After the minimal implementation, the identical command passed:

```text
uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py
133 passed, 407 subtests passed in 13.78s
```

Confirmatory registration evidence:

```text
uv run python scripts/verify_skill_registered.py --skill replan
skill ok: replan is registered, mechanically clean, and installs (--dry-run)
```

The tests cover all four exits, repair preservation, stop nullability, cross-partition identity collisions, complete and classification-matched dispositions, evidence-only/drop restrictions, discriminated replacements in an assembled dependency graph, launched-issue stability, every one of the five typed fixed-boundary escalations, singular escalation cardinality, exact-G1 repeated strings, strict unknown/type failures, rendering, offline execution, installation, and corpus registration. Scoped searches confirmed executable call sites for `verify_replan_input`, `verify_replan_result`, `render_replan_markdown`, and `main`.

## Review identity

Digest algorithm: sort the exact inventory with ordinal comparison, then SHA-256 the concatenation of `UTF-8(path)`, NUL, raw file bytes (or `<deleted>`), NUL for each path. The persisted inventory and recomputation helper are `G2_DIGEST_PATHS.txt` and `recompute_g2_digest.ps1` beside this result.

Inventory (11 paths):

```text
README.md
SKILL_INDEX.md
scripts/install_constellation.py
skills/replan/SKILL.md
skills/replan/references/contracts.md
skills/replan/scripts/verify_replan.py
skills/replan/templates/REPLAN_INPUT.template.json
skills/replan/templates/REPLAN_RESULT.template.json
tests/test_install_constellation.py
tests/test_replan.py
tests/test_write_a_skill.py
```

Generated `skills/replan/scripts/__pycache__` was removed and contract tests suppress source-tree bytecode generation. `git diff --check` passed for the inventory.

## Scope and map impact

The change adds the public `skills/replan/**` capability and its installer/index registration. Rework 1 changed only `tests/test_replan.py`, `skills/replan/scripts/verify_replan.py`, and `skills/replan/references/contracts.md` within that existing 11-path identity. It reads G1 shapes through the existing `verify_issue_set.py` seam without changing that schema. No architecture map exists; direct current-interface verification covered the structural anchors. Explorer, Commander, and Admiral lifecycle prose remains deliberately unwired for G3. No tracker API, compatibility alias, archive/history, provenance, or network write was added. Unrelated dirty-worktree changes were preserved.

## Workflow feedback

The reviewer exposed that the original handoff's “any fixed delta requires escalation” wording did not explicitly resolve multiple fixed surfaces against the frozen singular `escalation` object. The rework handoff supplied the missing decision: fail fast when a packet crosses more than one distinct fixed boundary. It also made the cross-partition identity and assembled-graph rules explicit. Those clarifications were sufficient and required no schema or authority change. Separately, the write-a-skill registration guidance still suggests some manually maintained corpus membership that current tests derive from live skill directories; aligning that wording with the actual rail would reduce author uncertainty.

No stop condition fired. Fresh independent semantic review remains the G2 reviewer gate.
