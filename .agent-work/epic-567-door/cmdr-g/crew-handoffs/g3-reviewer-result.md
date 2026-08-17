# Review Result

## Assigned Gate
`g3` — `finish_work` composition + dispose + CLI. Final gate of 3 (g1 verify+close, g2 reap+child-release, both already reviewed and integrated).

## Result
`APPROVE`

## Handoff compliance
`finish_work` and `open_pr` exist in `scripts/spine_lifecycle.py` at lines 949 and 1108, matching the handoff's part (a)/(b) signatures. The composition order was verified by reading the source directly (:1023–1105), not by trusting the test: verify (`done_refusal`) → release children (`_release_child_plans`) → top-level advance+release (`_advance_and_release`) → reap (`force_reap`) → archive (`close_work`, unmodified) → optional push → optional PR — exactly matching part (a) steps 2–8. `finish_work` never raises for a normal closeout refusal at steps 2/4/6 (`TestFinishWorkRefusals`, 5 tests, re-run and read: each returns a structured dict, never an exception). `open_pr` is called only when `open_pr=True` (spy-confirmed both directions) and its PR body write uses `tempfile.mkstemp` + `--body-file` exclusively — confirmed by source read, never a `--body` string. The CLI (`scripts/spine_done_cli.py`) is thin argument-parsing plus one call into `finish_work`, matching the Allowed Scope description.

The one deliberate deviation the handoff flagged for verification — `finish_work`'s headline signature omitting `tree_clean`/`episodes_captured` even though step 2 and the CLI section both require them — was independently confirmed genuine by reading the handoff myself (part (a)'s headline line vs. its own step 2 and CLI section). The implementer's resolution (adding both as required keyword parameters, documented inline and in Workflow Feedback) is correct handling of an ambiguous handoff field, not a silent guess.

## Scope drift
None. `git status --porcelain` shows only `scripts/spine_lifecycle.py` (M), `tests/test_spine_lifecycle.py` (M), `scripts/spine_done_cli.py` (??, new) — exactly the Allowed Scope. `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` independently re-run: empty. `git diff scripts/spine_lifecycle.py` has zero deletion lines (602 insertions, 0 deletions), which mechanically proves `done_refusal`/`_engine_call`/`_advance_and_release`/`force_reap`/`_release_child_plans`/`close_work`/`closeout_refusal` (all pre-existing g1/g2 primitives) could not have been altered — `finish_work`/`open_pr` are pure appends after `_release_child_plans`. `git check-ignore scripts/spine_done_cli.py` exits 1 (correctly tracked-eligible, not ignored). `finish_work` is not wired as an MCP tool — `mcp_spine_server.py` untouched, matching the Specific Exclusions.

## Evidence verdict
All Required Evidence independently reproduced, not accepted from the report alone:
- **#552 lease-proof end-to-end test** (`TestFinishWorkLeaseProofEndToEnd`): re-run standalone (1 passed) and the test body read in full. It builds a real parent spine + child plan with BOTH `engine_session.status == "active"`, asserts a structural active-lease census goes 2 → 0 across one `finish_work` call, and asserts the archived child's `engine_session.status == "released"`. Genuine, not simulated.
- **Composition-order test** (`TestFinishWorkCompositionOrder`): re-run standalone (1 passed); asserts the exact spy call order `["release_child_plans", "advance_and_release", "force_reap", "close_work"]`, matching the source read above.
- **Fresh-process CLI validation**, reproduced twice: `TestSpineDoneCli`'s 3 tests (genuine `subprocess.run(["python3", ...])` spawns, re-run: 3 passed) AND my own standalone manual run in a fresh `mktemp -d` repo, entirely outside pytest and outside this worktree — observed both the refusal/exit-1 path (structured JSON, no mutation) and, after fixing my fixture's postcondition shape, the ok/exit-0 path with an archive directory genuinely created.
- **Full suite**: independently re-run, 119 passed (104 baseline → 119, +15 new tests), matching the implementer's claimed count exactly.

Test mode was test-after (matching g1/g2's convention); no red step was required and none was claimed.

## Code/doc quality
Constraints verified: no fixture or manual run ever targets a live spine (`grep` for `epic-567-door` across the new/changed files finds it only inside `TestSpineDoneCli`'s own negative-assertion string); `open_pr` never constructs a `--body <string>` call (source read + `test_open_pr_uses_body_file_never_a_body_flag`); POSIX-form commands and `PYTHONIOENCODING=utf-8` used throughout; `py` confirmed working on this host (3.12.3, pytest 9.1.1). Naming and docstring density match the surrounding module's established style (g1/g2, both already reviewed favorably on the same terms).

**Fowler pass** (`r6-fowler`, recorded to `.agent-work/epic-567-door/cmdr-g/g3-review/FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0): zero flagged smells. Two documented overrides — **primitive-obsession** (the plain-dict/`str | None` return shapes are the handoff's own ratified Success/Refusal Return contract, matching this module's pre-existing sibling functions) and **long-parameter-list** (`finish_work`'s 9 params each map 1:1 to a distinct required input of a distinct downstream primitive; the signature is the handoff's ratified Authority-section contract, and a parameter object not asked for would itself violate the no-speculative-abstraction rule) — both consistent with g1-review's/g2-review's identical treatment of this file's sibling functions. **speculative-generality** is genuinely absent (not merely overridden) here: unlike g1/g2 at their own review time, `finish_work` has a real, reachable-today non-test caller in this same diff — `scripts/spine_done_cli.py` — independently exercised as a fresh subprocess.

## Map impact verdict
- **Evidence supports claimed change:** yes — `capability:mechanical-closeout-one-verb` (#574's steps 1–5 reachable via one call/CLI invocation) is backed by the lease-proof test and my independent CLI reproduction.
- **Constraints not violated:** yes — `decision:pr-opening-question-is-not-yours` honored (`open_pr=False` default, floated not ruled); `decision:new-rot-first-old-rot-maybe` untouched (no sweep of the 41 pre-existing stale leases attempted anywhere in this diff).
- **Notes match the diff:** yes — structural anchors (`finish_work`/`open_pr` appended after `_release_child_plans`) match the observed line numbers (949, 1108, following 799–932).
- **Decision candidates surfaced:** none needed beyond what the handoff already floats.
- **Durable context routed:** no triage candidates raised by the implementer; consistent with the decision anchors already scoping the 41 pre-existing stale leases out of this gate.

No `docs/architecture` map exists in this repo (confirmed: DEGRADED-UNPARSEABLE, matching the handoff's own Map Anchors note), so there is no structural baseline to reconcile against.

## Reconciliation check
None. No architecture-baseline drift; the change is additive-only within one already-mapped module.

## Blockers
- none

## Out-of-scope observations
- none beyond what the handoff's own Decision anchors already scope out (the 41 pre-existing stale leases, `decision:new-rot-first-old-rot-maybe`).

## Workflow Feedback

- **Handoff gaps:** the `g3-implementer-handoff.md` part (a) headline signature line for `finish_work` omits `tree_clean`/`episodes_captured`, even though step 2 of the same section and the CLI section both require them as caller-supplied inputs — confirmed genuine by reading the handoff myself, not just accepting the implementer's report. This should be corrected in the source contract before another gate is drafted from the same template.
- **Context rediscovered:** the `r6-fowler` survey-template postcondition (`c1`) carries an unresolved `<work-id>`-substitution defect — it assumes a flat `.agent-work/<work-id>/FOWLER_PASS.json` layout, but this project's actual convention nests review state under `.agent-work/epic-567-door/cmdr-g/<gate>-review/`. This is the third time this exact defect has been hit (g1-review, g2-review, now g3-review) and fixed identically each time via `amend --delta` with a `retext-check` op. The template (`skills/reviewer/templates/REVIEW_SURVEY.template.json`) or the project's own copy should be corrected so a future reviewer does not have to rediscover and re-fix this a fourth time.
- **Instructions improvised around:** none — the reviewer skill's own REPAIR PATH note for this exact situation (amend via `retext-check`, authority the dispatching Commander named in the handoff) applied cleanly.
- **What would have made this easier:** fixing the `r6-fowler` template postcondition once at the source (either parameterize the actual review-state directory into the template instantiation step, or change the convention to a flat `.agent-work/<work-id>/` layout) would remove a now-three-times-repeated amend step from every future reviewer in this project.

## Return status
`complete`
