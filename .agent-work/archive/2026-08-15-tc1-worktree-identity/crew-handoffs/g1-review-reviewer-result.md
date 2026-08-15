# Review Result

## Assigned Gate
`g1` — worktree identity by git equality (2026-08-15 worktree-identity ruling)

## Result
`APPROVE`

## Handoff compliance
All three binding ruling parts are implemented exactly as ordered. (1) `main()` resolves `engine_cwd` via `_git(["rev-parse", "--show-toplevel"], base_dir=Path.cwd())` and passes `None` on non-zero returncode or empty stdout; grep confirms exactly one `rev-parse --show-toplevel` call site in the file (L3439). (2) The predicate compares `here == root` with the same `os.path.normcase` folding as before, signature `cwd: str | None`, and stays pure — an AST walk shows only dict reads, `Path` construction, `normcase`, and comparisons. (3) The fail-closed branch sits AFTER the shape fallbacks, so an origin-carrying spine with `cwd=None` refuses while origin-less/malformed spines fall back and never raise (`OriginRefusalFailClosed` covers every guarded verb, the exempt verbs, and all six malformed shapes). The one authorized test migration was executed exactly as scoped: the synthetic subdirectory case now asserts refusal with a docstring pointing at `RefusesAGuardedVerbFromAForeignTree::test_the_same_verb_from_a_subdirectory_of_the_worktree_succeeds`, where the real property is asserted through `main()` against a real git repo — moved, not deleted.

## Scope drift
The diff is exactly the four expected files (`map/INDEX.md`, `scripts/checklist_engine.py`, `tests/test_explorer_templates.py`, `tests/test_spine_origin_isolation.py`), no new/untracked tracked files. Specific exclusions verified untouched via scoped `git status`: `scripts/hooks/spine_rail.py`, `scripts/mcp_spine_server.py`, `.mcp.json` all clean; the modifications visible inside `.worktrees/epic-568-441` are that worktree's own live #441 branch state, not this diff. No `origin.worktree` migration/backfill anywhere (no spine JSON in the diff). `test_it_is_pure` is byte-identical to `HEAD` (method extracted from both revisions: 875 bytes, identical sha256). `OriginRefusalFallback` is byte-identical to `HEAD` (class extracted from both revisions: 2100 bytes, identical sha256) — intent trivially unchanged.

**The weighed judgment call — `tests/test_explorer_templates.py`:** accepted as the right minimal repair, verified empirically, not by trusting the claim. I reverted the hunk and re-ran `ExplorerSpineCrossCheck::test_instantiates_and_engine_can_claim_and_start` against the new engine: it fails with `claim refused: ... no git worktree toplevel could be resolved`, i.e. the new fail-closed rule correctly refuses the bare-tempdir fixture whose instantiated spine carries an origin stamp. The 1-line `git init` makes the fixture honest, is the same class of repair as the `_SpineOnDisk` git-init this gate's own plan ordered, was disclosed by the implementer rather than smuggled, and is strictly smaller than a BLOCK-and-rescope round-trip. Not scope creep.

## Evidence verdict
Every load-bearing claim was independently reproduced, not read off the report:

- **Red/green (the single most load-bearing item):** stashed the engine change only, ran the two `NestedWorktreeRegression` tests → **2 failed**, with the red output showing the pre-change engine ADVANCING the guarded verb from inside a nested worktree (`g1 -> in-progress`, exit 0 — the ruling's measured bug, live). Popped the stash, re-ran → **2 passed**. Test mode satisfied: genuine red on the unmodified engine, green after.
- **Targeted file:** `tests/test_spine_origin_isolation.py` → 37 passed, 1 skipped, 16 subtests — matches the claim.
- **Cache-clean full suite** (pycache purged, `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`): **3010 passed, 6 skipped, 0 failed, 1135 subtests** — ≥ baseline 3002/7/0/1130, and 0 failures.
- **The `env -u` rationale:** confirmed independently. `test_mcp_identity.py::DC3InheritanceMechanismTests` fails with the ambient SPINE vars set and passes without them, on this tree AND on an unchanged `HEAD` tree in a throwaway worktree — environment-caused, not diff-caused.
- **Skip delta 7→6, mechanically explained (better than the implementer's own explanation):** the seventh skip is `tests/test_spine_lifecycle.py:161`, conditional on the checkout NOT sitting directly under `.worktrees/`. A `HEAD` worktree at `/tmp` yields 7 skips including it; this tc1 worktree sits under `.worktrees/` so the test runs and the count is 6. Checkout-location-dependent, not diff-dependent.
- **Map:** `python -m scripts.code_map build --root .` reproduces the diffed `map/INDEX.md` exactly (entity counts 4574→4588); `map/ids.jsonl` unchanged.
- **Door tests (`decision:forgery-stays-open`):** `test_mcp_door_engine_cwd.py` + `test_mcp_lifecycle.py` + `test_mcp_adoption.py` → 202 passed, 2 skipped. The chdir-based door mechanism is unbroken.

## Code/doc quality
Minimal and maximally local: one predicate, one call site, and the tests that pin them. The updated docstrings carry the ruling's provenance and the ordering constraint (fail-closed AFTER the shape fallbacks) — recorded architecture in the code now matches the new semantics. Fowler pass recorded at `.agent-work/tc1-worktree-identity/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0: zero smells flagged, one logged override (primitive-obsession — the `cwd: str | None` signature is the ruling's own binding close criterion and the repo's documented refusal-or-`None` convention; a wrapper type would add interface without behavior).

## Map impact verdict
- **Evidence supports claimed change:** yes — the capability claim (equality guard covering the #585 nested layout) is backed by the reproduced red/green pair.
- **Constraints not violated:** yes — `test_it_is_pure` and `OriginRefusalFallback` byte-identical; no migration; exclusions untouched.
- **Notes match the diff:** yes — structural anchors, capability, and decision anchors listed in the implementer's Map Impact match exactly what the diff touches, nothing missing or overstated.
- **Decision candidates surfaced:** n/a — all three inbound decisions were `settled/human`; none required new authority, and none was unsettled.
- **Durable context routed:** yes — two triage candidates routed (below), also flagged in my survey via `flag-candidate`.

## Reconciliation check
No divergence for Commander to reconcile. `map/ids.jsonl` remains empty repo-wide (pre-existing DEGRADED state, discharged at plan context) — nothing to update there.

## Blockers
- none

## Out-of-scope observations
- Triage candidate (implementer's, verified real): the lexical-vs-git worktree-derivation split (`spine_rail.py::_worktree_from_spine` vs `mcp_spine_server.py::_worktree_root_for_lifecycle`) is ruled deliberate but documented nowhere durable; the ruling names it a documentation deliverable, deferred while #441 owns `spine_rail.py`.
- Triage candidate (implementer's, reproduced on unchanged HEAD): `DC3InheritanceMechanismTests` fails inside any `run_crew.py`-dispatched crew because of the ambient `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` dispatch envelope; an explicit skip-or-scrub would stop crew full-suite gates tripping on their own envelope.
- Observation, no action required: `_git()` would raise `FileNotFoundError` if the `git` binary itself were absent, so a git-less host crashes rather than fails closed. This is the pre-existing behavior of the shared `_git` helper everywhere it is used, git is a hard dependency of this repo's tooling, and the ruling's fail-closed clause addresses "no toplevel resolvable", not "no git installed" — noted for completeness only.

## Workflow Feedback
- **Handoff gaps:** none material. One inherited-environment surprise the handoff could not have known: this crew's `SPINE_FILE`/`SPINE_SESSION` were bound to the *Commander's* `execute` spine (SPINE_SESSION == SPINE_PARENT), so the skill's default "drive the bound spine through the MCP door" path was wrong for this dispatch; the handoff's explicit "create your survey at `.agent-work/<work-id>/g1-review/review.json`" line is what disambiguated. If `run_crew.py` can bind the crew's own survey path into `SPINE_FILE` instead, the ambiguity disappears.
- **Context rediscovered:** which stash granularity produces the red run — the handoff says "git stash the diff" but stashing all four files would also stash the new tests; the implementer's `g1-red.txt` showed the real recipe (stash `scripts/checklist_engine.py` only). One clause in the handoff ("stash the engine file only") would have saved the inference.
- **Instructions improvised around:** the exclusion check "`git status --porcelain` showing none of these paths" cannot be run against `.worktrees/epic-568-441/` from inside a sibling worktree (`fatal: outside repository`); I checked that worktree from the primary checkout instead and attributed its dirt to the live #441 branch.
- **What would have made this easier:** the handoff was exceptionally good — reproduction commands, expected counts, and the one judgment call pre-framed with its decision criteria. Nothing else.

## Return status
`complete`
