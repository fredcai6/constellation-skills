# RESULT — w2-basis (epic 569 wave 2)

## Verdict

**Shipped.** A new, report-only `basis` sibling field on `Condition` (`scripts/checklist_engine.py`) lets a plan author declare, at plan-authoring time, a resolvable locator (`file` or `evidence_ref`) for a `check: null` condition. The engine renders it (`render_human`, populated-only) and resolves-and-durably-records it at `attest` via an always-attached `basis-check` evidence item — never blocking. Authored on exactly three conditions (`plan.c2`, `plan.c4`, `plan.c5`) in the shipped `skills/commander/templates/COMMANDER_SPINE.template.json` as proof against real corpus content, per `decision:engine-first-backfill-where-it-earns-it`. The riskier check-kind-promotion batch (`plan.c1`/`reconcile.c1`/`archive.c2`/`init.c1`) is **deliberately deferred**, not shipped — real, well-evidenced work that needs an Admiral adjudication for its live-blocking behavior change, which this run did not have in hand.

PR: **#653**, `epic-569/w2-basis` → `main`, OPEN. https://github.com/fredcai6/constellation-skills/pull/653

## The alternatives pass and why the loser lost

Design-it-twice panel (N=3, per "touches the engine → panel"): `structured-field` (new sibling field, 5 locator kinds), `statement-convention` (fold into `statement` text, no schema change), `artifact-conversion` (reuse the existing `check: {kind: artifact}` machinery verbatim, zero new engine code). All three independently converged on the same structural split against the real 19 `check: null` conditions in `COMMANDER_SPINE.template.json`: at most 11/19 (58%) express any real locator at all; 9 of those 11 need no new mechanism (a direct check-kind promotion already gives them everything); only 2 (`plan.c4`, `plan.c5`) get genuinely unique value from a new field, because a real artifact exists but the actual claim (convergence, triage quality) is a judgment call no mechanical check can make.

**`statement-convention` lost outright**: its one advantage (zero render code) was matched by `artifact-conversion` at zero render code AND zero attest code, and its own write-up recommended against its `command` locator kind and against forcing the 8 degenerate conditions — hollowing out most of its own scope claim.

**The winning design is a hybrid**, revised after a cold critic (single agent, no authoring context) found 6 fix-before-execute issues against the first-converged plan:
1. `init.c1`'s promotion cited the wrong candidate and wasn't actually zero-new-code (`state_field` isn't a real engine check kind; `command` would need an unwritten script against the bookend gate of every Commander run in the corpus) — **dropped**.
2. "Not a new refusal surface" conflated mechanism-reuse with behavior-preservation — promoting `plan.c1`/`reconcile.c1`/`archive.c2`/`init.c1` IS a real, un-adjudicated live-blocking change for those specific gates — **the entire check-kind-promotion batch dropped**, deferred to triage.
3. `reconcile.c1`'s proposed `file-diff` conversion was decorative as specified (`_artifact_match_satisfied` never independently verifies the diff) — moot once (2) dropped it.
4. `plan.c2` was missing from the convergence table despite matching `plan.c4`/`c5`'s exact shape — **added** to the authored set.
5. The original promotion trigger ("10 real runs, zero false-refusals") had no persistence to count against — **fixed**: `attest` now always attaches a `basis-check` evidence item, pass or fail, making the trigger genuinely auditable.
6. The two kept locator kinds (`file`/`evidence_ref`) only verify existence — no more than a direct `artifact` promotion would give for free — **reframed honestly**: the field's real value is rollout safety (report-only staging), not expressiveness, since `artifact`-kind checks have no report-only mode to fall back to.

## Evidence

- Base SHA: `9d5aac6daa58a72fc6a665cb39879ee5705f7f71` (matches the launch order's stated base; verified green by the Admiral pre-dispatch).
- Full local suite reproduced independently by this Commander (never trusting a crew's own transcript) at every integration: **3642 passed, 6 skipped, 0 failed**, three separate times across the wave (g1, g2, g3 integrations), plus once more before archive.
- Engine mechanism tests: `tests/test_checklist_engine.py -k Basis` — 17 tests (render + attest guard), red-then-green TDD, red transcript reproduced independently by g1's reviewer via `git stash` + rerun.
- Template integration tests: `tests/test_checklist_engine.py -k CommanderSpineBasisFields` — 3 tests, against the REAL shipped template, pinned to `git rev-parse HEAD` = `9d5aac6daa58a72fc6a665cb39879ee5705f7f71`. Red-proof independently reproduced by g2's reviewer (swap template back to pre-edit content, rerun, confirm 5 failures; restore, rerun, confirm green).
- `GoldenOutputBriefing`/`TemplateOnlyFieldAllowlist` green throughout — confirms no existing shipped template's `current` output or field-shape assumptions changed, including after the first real `basis` field landed in shipped content (g2).
- **Red-proof pinned to the shipped SHA it ships against**: `9d5aac6daa58a72fc6a665cb39879ee5705f7f71` (the base; the PR's actual diff is on top of it, no rebase since).

## Where any new check runs and proof it can fail there

- `attest()`'s new basis-resolution guard: exercised by `tests/test_checklist_engine.py`'s `BasisAttestGuard` class (11 tests) on a throwaway fixture, and by `CommanderSpineBasisFields` (3 tests) on the real shipped template — both run in the ordinary `pytest tests/test_checklist_engine.py` suite, which CI (Windows-only, known-red per doctrine) does not gate but the local suite does, and which every future Commander run through `COMMANDER_SPINE.template.json`'s `plan.c2`/`c4`/`c5` will exercise live.
- Proof it can fail: `BasisAttestGuard`'s red transcript (pre-implementation) shows `TypeError: attest() got an unexpected keyword argument 'base_dir'`, `AttributeError: module 'checklist_engine' has no attribute '_resolve_basis_locator'`, `IndexError: list index out of range` — genuine failures against the unmodified engine, independently reproduced by the reviewer.
- No new standalone `verify_*.py`/`check_*.py`/`prove_*.py`/`measure_*.py` script was added this wave (`decision:no-new-unwired-checker` — n/a, no such script exists to wire).

## PR number and full local suite result

- **PR #653**: https://github.com/fredcai6/constellation-skills/pull/653, `epic-569/w2-basis` → `main`, state OPEN.
- Full local suite at HEAD (`0ee2f771`, the archive-close commit): **3642 passed, 6 skipped, 0 failed** (last full run before archive, at commit `e340fea1`; the archive-close commit `0ee2f771` only touched engine bookkeeping files under `.agent-work/`, no source).
- **Known, benign merge conflict**: `git merge-tree --write-tree` against current `origin/main` (`305b00b3`, which advanced past this branch's base while this run was in flight) shows a real conflict in **`map/INDEX.md` only** — a generated artifact both branches independently rebuilt. No conflict in any authored source, doc, or test file. Per this run's Workspace doctrine, "PR integration defaults to server-side merge. The Admiral merges" — left for the Admiral to resolve (a straightforward `code_map build` rerun post-merge), not resolved by this Commander.

## Map impact

No packet map exists for this repo (`docs/architecture/generated/map.json` empty, `map/ids.jsonl` empty — `map_orient.py orient` returned `DEGRADED-UNPARSEABLE`, discharged with substitutes `map/INDEX.md` + `docs/CHECKLIST_SCHEMA.md`, recorded at `.agent-work/archive/2026-08-22-w2-basis/map-orientation.json`). Per commander-core.md's Architecture bookend ("no packet map" branch), the structural record was reconciled directly:
- `docs/CHECKLIST_SCHEMA.md` — new `basis` row in the Condition table, `basis-check` added to the Evidence type enum/payload docs, new "Basis" subsection (g1, reviewed APPROVE).
- `docs/CHECK_SCRIPT_CENSUS.md` — dated addendum to the `generate_spine.py` disposition section, with corrected `because`/`basis` grep counts and an explanation of the `because`-count collision this wave surfaced (g3, reviewed APPROVE).
- `map/INDEX.md` — refreshed via `python -m scripts.code_map build --root .` (g3); real, non-trivial refresh (`scripts.checklist_engine` 116→118 entities, `tests.test_checklist_engine` 679→705), not a no-op.

## Triage candidates

One candidate flagged (`tc1`): the check-kind-promotion batch (`plan.c1`→`artifact`, `reconcile.c1`→`artifact`, `archive.c2`→`artifact`, `init.c1`→`command`). **Disposition: recommend-and-defer, not filed.** Per the launch order's standing preference ("strong prefer to just fix or write episodes... issues are being saved for high certainty run impacts that can't be immediately fixed"), this is real future work requiring authority this run does not hold (an Admiral adjudication for the live-blocking behavior change, since `artifact`-kind checks have no report-only mode to stage through), not a run defect — fixing it now was not an option, and filing an issue for genuine future work was judged the disfavored exit here too. Recorded in `PLAN_ALTERNATIVES.md`'s Untaken-road record, `PLAN_CRITIC.md` findings 1–3, and `REPLAN_INPUT.json`'s discrepancy D1.

## Workflow feedback (where this order was underspecified)

Full detail is in 4 captured episodes (`episodes/active/w2-basis-001.md` through `-004.md`, applied via `apply_episode_delta.py`, verified via `verify_episode_captured.py`). Summarized:

1. **The HARD context-band trip fired four separate times** (at `plan`, `execute`, `reconcile`, `review`), each refusing `start` on a fresh gate at turn one. The launch order's own Stop Conditions section had already pre-empted this exact scenario in writing ("attach the refresh-request... THEN start, THEN do the work... do not read a HARD advisory as licence to advance and hand off on turn one") — this is the one place the order was *not* underspecified, and it mattered: without that explicit clause, a Commander following the generic rail text literally would likely have gone idle four times, each needing an external relaunch that may not have arrived.
2. **Genuinely underspecified**: the mission frame's map-anchor-citation mechanics under `DEGRADED` orientation. `map_orient.py verify-frame` unconditionally flags ANY `decision:X`/`struct:X`/etc.-styled citation as an unresolvable problem in DEGRADED mode — including a citation of a launch-order pre-ruling, which the mission-frame template's own worked examples model as the natural way to cite a decision. Discovered by trial (FRAME-REFUSED with 9 problems, then FRAME-OK after rewriting every `decision:X` as `ruling-X` prose). No doctrine text flagged this in advance.
3. **Genuinely underspecified**: `execute.json` is driven through `checklist_engine.py`'s own standalone `--file` CLI, entirely separate from the `mcp__spine__*` tools bound to the top-level `spine.json`, and (since no lease is ever claimed on it) needs no `--session-id` on any call — a different mechanism, and a different session-scoping story, than the top-level spine. `commander-core.md`'s text ("drive execute.json gate by gate... using this skill's gate execution instructions") does not state either fact; both were confirmed via `checklist_engine.py --help` directly.
4. **A now-third-observed pattern, worth graduating out of episodes**: all 6 dispatched crews this run (3 gates × implementer + reviewer) independently hit and correctly self-resolved the same `SPINE_FILE` resolves-to-parent / `crew-runs.json`'s `spine: null` situation — the third run (after `w1-verdict` and a sibling wave-2 lane) to record this exact episode. Given the repeat count, this reads like something closer to a rule (crew-dispatch doctrine could name the branch explicitly rather than relying on every crew re-discovering it) than a one-off observation — flagged here for a human to judge, per the episode-store doctrine's own rule that "a rule to follow belongs in docs/agents/* and is a human's call," not this Commander's to promote unilaterally.

No decision was floated to the Admiral this run — every gap the order left was resolvable within inherited latitude (implementation shape, fix-now triage, template/engine editing) without exceeding it.
