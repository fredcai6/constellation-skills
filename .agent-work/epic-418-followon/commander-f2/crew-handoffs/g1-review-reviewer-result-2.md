# Review Result

## Assigned Gate
`g1-review` (issue #542/#541, workstream F2, epic-418-followon, commander-f2) — **re-review after rework**, verifying commit `80995760` against the prior reviewer's BLOCK (`g1-review-reviewer-result.md`)

## Result
`BLOCK`

## Handoff compliance

**Prior Finding 1 (undeclared `spine_override` key honoured in `call_tool`, defeating the pin silently).** RESOLVED for the exact case demonstrated, but a residual gap remains — see Evidence verdict and Blockers.

**Prior Finding 2 (`python -m pytest -q` not green — `map/INDEX.md` stale).** RESOLVED, fully reproduced.

**Criterion A (six frozen items).** Re-verified item by item against the current `IDENTITY_TRADE.md` (post-narrowing edit): all six remain present and load-bearing. The narrowing touched only §2's confinement sentence, adding a new paragraph that names the reviewer's falsification and narrows the claim to both the declared **and** runtime halves — this is an addition, not a removal.

**Criterion D (honest-scope claim).** Holds. The two new tests (`test_an_out_of_schema_identity_argument_cannot_redirect_a_live_call`, `test_the_runtime_pin_can_fail`) both use `_load_module` — a direct import of the module under a patched environment — with no subprocess spawn and no Task-tool dispatch. Neither asserts anything about harness-internal MCP client reuse.

**Criterion E (`git diff HEAD~2 -- scripts/` empty).** Holds, both for the rework commit alone (`git show 80995760 --stat` shows zero lines touching `scripts/`) and across the full two-commit window under review.

**`scripts/checklist_engine.py` and `scripts/hooks/spine_rail.py` untouched.** Confirmed via `git diff HEAD~2` against each path — both empty.

## Scope drift
None. HEAD is actually `f414c1f6` (a subsequent chore commit recording `REPLAN_INPUT.json` wave evidence — touches only `REPLAN_INPUT.json` and `crew-runs.json`, no `scripts/` files), sitting on top of the rework commit `80995760` under review. `git diff HEAD~2 -- scripts/` spans both commits and is empty.

## Evidence verdict

**Finding 1 mutation reproduction.** Baseline: `python -m pytest -q tests/test_mcp_identity.py::IdentityBindingPinTests` → **7 passed** (5 original + 2 new). Re-applied the exact prior-reviewer mutation to the real `scripts/mcp_spine_server.py` — in `call_tool`'s `spine_status` branch:

```python
if name == "spine_status":
    if args.get("spine_override"):
        global SPINE
        SPINE = Path(args["spine_override"]).resolve()
    return as_result(run_engine("current", mutating=False))
```

Result: **RED, exactly and only on `IdentityBindingPinTests::test_an_out_of_schema_identity_argument_cannot_redirect_a_live_call`** (1 failed, 6 passed) — `AssertionError` showing the door read the decoy spine instead of the bound one. Matches the commit message's claim precisely. Restored via `git checkout -- scripts/mcp_spine_server.py`; `git diff --stat scripts/` back to 0 lines; suite back to 7 passed.

**Finding 2 reproduction.** `python -m pytest -q` → **2274 passed, 1 skipped, 0 failed, 1079 subtests passed** — matches the commit message's claimed suite result exactly. `python -m pytest -q tests/test_code_map.py::MapTreeFreshnessTests` → 2 passed in isolation. `git status --porcelain` after the full run shows `map/` untouched — the freshness test is a read-only comparison against a genuinely fresh build, not a test that silently regenerates the tracked file to pass itself.

**My own fourth mutation — defeats the pin.** The new runtime test drives exactly one tool (`spine_status`) with exactly five hardcoded literal key names (`spine_override`, `spine_file`, `file`, `session_id`, `engine`) — a finite enumeration, not a universal property. This same file already contains, on the *declared*-schema pin (`test_no_tool_accepts_an_argument_that_could_redirect_the_door`), a substring-marker approach (`IDENTITY_ARG_MARKERS = ("spine", "session", "engine", "checklist_file", "identity")`, matched via `any(marker in lowered for ...)`) that is robust to naming variety — the new runtime test does not reuse that pattern. I mutated `spine_status`'s handler to honour a sixth key name, `target_spine` (chosen specifically to contain the substring `spine`, one of the declared-schema markers, to show the runtime check is strictly narrower than the declared-schema check already sitting in the same file):

```python
if name == "spine_status":
    if args.get("target_spine"):
        global SPINE
        SPINE = Path(args["target_spine"]).resolve()
    return as_result(run_engine("current", mutating=False))
```

Result: **7 passed. Nothing went red.** I then independently confirmed the mutation is a genuine, live redirect — not an inert no-op the test correctly ignored — by driving `call_tool("spine_status", {"target_spine": <decoy path>})` directly outside the suite: the returned text carried `DECOY-MARK`, not `PIN-MARK`. Restored via `git checkout -- scripts/mcp_spine_server.py`; `git diff --stat scripts/` and `git diff HEAD~2 -- scripts/` both back to 0 lines; suite back to 7 passed.

| # | Mutation | Result | Restore confirmed |
|---|---|---|---|
| Baseline | none | 7 passed | — |
| Reviewer's mutation 3 (undeclared `spine_override` on `spine_status`) | **RED**: `test_an_out_of_schema_identity_argument_cannot_redirect_a_live_call` | diff 0 lines; 7 passed |
| Mine (undeclared `target_spine` on `spine_status`) | **7 passed. Nothing went red.** Confirmed live via direct `call_tool` invocation: reads `DECOY-MARK`. | diff 0 lines; 7 passed |

## Code/doc quality
Fowler pass run (`r6-fowler`, recorded to `.agent-work/epic-418-followon/commander-f2/g1-review/fowler-pass-2.json`, `scripts/verify_fowler_pass.py` exits 0): 10 of 12 baseline smells absent; 2 overridden with a logged repo-standard + reason (`divergent-change` and `comments-as-deodorant`, both citing the same standard the prior review logged for this file — its documentation-density convention). No blocking quality finding.

Handoff constraints checked: `python -m pytest` used exclusively (never `python3`); no command piped into `head`/`tail` with its exit code read — all outputs redirected to files, exit codes captured directly; no backticks or command-looking text placed inside any engine `--finding` string; the review checklist JSON driven only through `checklist_engine.py` verbs, never hand-edited.

## Map impact verdict
- **Evidence supports claimed change:** Yes — both prior findings reproduce as resolved; the full suite is genuinely green in my own hands.
- **Constraints not violated:** Yes — allowed scope and specific exclusions respected; `scripts/checklist_engine.py` and `scripts/hooks/spine_rail.py` untouched.
- **Notes match the diff:** Partially. `IDENTITY_TRADE.md`'s narrowed claim ("no tool declares an argument that would let it, and at runtime the dispatch ignores an undeclared one") still overstates what is pinned — a five-key allowlist on one tool, not a universal per-call property. This is the same shape of gap the document's own §2 paragraph names as having happened once already.
- **Decision candidates surfaced:** N/A — staying within the Commander's delegated authority; not re-opening the identity decision.
- **Durable context routed:** Yes — the residual gap is flagged as triage candidate `tc1` in the survey (`.agent-work/epic-418-followon/commander-f2/g1-review/review-2.json`) in addition to being the BLOCK finding here.

## Reconciliation check
`IDENTITY_TRADE.md` remains the durable architecture record this gate is required to produce. The rework's narrowing is a reconciliation *improvement*, not a divergence — it makes the document's claim match what is pinned more closely than before, even though it still overstates coverage on the runtime side. No conflict with `docs/CHECKLIST_ENGINE_DESIGN.md:310-312`, untouched by this rework.

## Blockers
- **Runtime pin is a finite allowlist, not a universal property (my mutation 4).** `test_an_out_of_schema_identity_argument_cannot_redirect_a_live_call` checks five literal key names against one tool (`spine_status`). A sixth key name (`target_spine`, demonstrated live) defeats it while genuinely redirecting the read — the same silent-defeat shape the prior reviewer's mutation 3 found, one layer down. `IDENTITY_TRADE.md`'s narrowed §2 claim ("at runtime the dispatch ignores an undeclared [key]") is still a universal-sounding prose claim backed by an enumerated test. Recommend one of: (a) narrow the prose further to name the allowlist explicitly, mirroring how §2 already narrowed the declared half after the first finding, or (b) widen the runtime pin to reuse the file's own `IDENTITY_ARG_MARKERS` substring-matching pattern across the full `TOOLS` surface (not just `spine_status`) — logged as triage candidate `tc1`.

## Out-of-scope observations
- None beyond the blocker above.

## Workflow Feedback

- **Handoff gaps:** None material. The handoff for this re-review named the exact mutation to reproduce, the exact test id to expect, and explicitly invited a fourth mutation — that invitation is what surfaced this BLOCK, and it worked exactly as designed.
- **Context rediscovered:** The `config_ref` (`docs/agents/engine-config.json`) named in the reviewer survey template does not exist anywhere in this worktree; the engine appears to tolerate its absence (claim/start/record all worked normally). Not a blocker, just an unexplained gap between the template and the repo's actual state.
- **Instructions improvised around:** My chosen `work_id` for this survey (`epic-418-followon/commander-f2/g1-review-2`, distinct from the file's own directory `.../g1-review/review-2.json`) caused the engine's context-logging side effect to create a doubled, nested scratch directory at `.agent-work/epic-418-followon/commander-f2/epic-418-followon/commander-f2/g1-review-2/...`. This is disposable scratch state, not a deliverable, and does not affect the verdict — removed before finishing — but a reviewer instantiating a re-review survey should probably keep `work_id` identical to the original gate's `work_id` (or exactly matching its own file's directory path) to avoid this. Flagging so a future re-review handoff can name the convention explicitly.
- **What would have made this easier:** Naming the expected `work_id` convention for a numbered re-review survey (`review-2.json`) explicitly in the handoff — I inferred it and it produced the directory-doubling side effect above.

## Return status
`complete`
