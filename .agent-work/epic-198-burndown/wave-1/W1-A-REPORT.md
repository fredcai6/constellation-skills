# W1-A Report — Context Governor v1 fast-follows (#189 #190 #191 #192)

**Commander:** commander-cg (delegated) · **Verdict: COMPLETE — PR open, awaiting Admiral merge**
**PR:** https://github.com/fredcai6/constellation-skills/pull/199 (branch `fix/cg-fastfollows-198`, base `main`, NOT merged — Admiral merges)
**Worktree:** C:/Programs/cs-wt-cg · **Commits:** `295295f` (engine #189/#190/#191), `e9f8aae` (doc #192)

## Worktree isolation (first action, exit 0)
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-cg
worktree OK: in C:/Programs/cs-wt-cg
EXIT: 0
```

## Per-issue verdict
All four are **fixed** — no honest-nulls; each of the three code defects was verified real and reachable before the fix.

| # | Verdict | What changed |
|---|---|---|
| #189 | fixed | `_why_suffix` (checklist_engine.py): removed the `type != GATED` early-return so `DIGEST:`/`REFRESH REQUESTED:` render for surveys. A survey has no `why_trail`, so only `REFRESH REQUESTED:` shows — the reach-up target for survey roles. Gated output byte-identical. |
| #190 | fixed | `has_pending_refresh_request` gained an optional `why_ref` identity filter (default `None` = unchanged gate-only display). HARD callers `_trip_advisory` (HARD branch) and `_trip_hard_gate` now key release on the current-digest why-record, with a `None`-id fallback to gate-only so all existing Trip tests stay green. Closes the stale-request coattails defect. Display caller left gate-only. |
| #191 | fixed | `advance` from-child seam is dedup-idempotent — skip the attach when an identical `review-result` is already present; attach-before-guards ordering preserved. Closes the refuse-then-retry double-attach (`main()` persists on a refused advance). |
| #192 | fixed | `docs/CHECKLIST_SCHEMA.md` documents all 7 epic-#178 additions (why_trail, why_exempt, --why/--mechanical, DIGEST/REFRESH REQUESTED with survey parity, refresh-request evidence, has_pending_refresh_request why_ref-aware, Trip two-band gauge.json), consistent with the post-fix code. Header `draft/pre-build` → `built/shipped`. |

## Evidence
- **Tests:** `py -m pytest tests/test_checklist_engine.py -q` → **189 passed, 18 subtests passed** (181 pre-existing all green + 8 new; no existing test weakened). Re-run independently by the Commander and by the reviewer.
- **New test classes / methods:**
  - #189 `SurveyWhySuffixReachUp`: `test_survey_shows_no_refresh_line_before_attach`, `test_survey_refresh_request_renders_on_current`, `test_survey_all_visited_renders_no_suffix`
  - #190 `RefreshRequestIdentity`: `test_predicate_identity_filter`, `test_identity_filter_stays_pure`, `test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases`
  - #191 `FromChildAttachIdempotent`: `test_refuse_then_retry_attaches_exactly_one`, `test_cli_refuse_then_retry_persists_exactly_one`
- **Meaningful-test proof:** the g1 reviewer reconstructed the pre-fix engine in scratch and confirmed the #190 coattails test fails pre-fix (`EngineError not raised`) and the #191 idempotency test fails pre-fix (`2 != 1`). The #192 doc was verified symbol-by-symbol against the post-fix engine.
- **Functions changed (scripts/checklist_engine.py):** `has_pending_refresh_request` (signature + body), `_why_suffix`, `_trip_advisory` (HARD branch), `_trip_hard_gate`, `advance` (from-child branch).
- **Review:** both gates reviewed APPROVE by independent opus reviewer crews; zero reopens, zero BLOCK verdicts, zero rework rounds.

## Map impact
No architecture-map change (skill-source repo, no `docs/architecture/` packet map). The structural record IS `docs/CHECKLIST_SCHEMA.md`, reconciled in-PR by #192. `CHECKLIST_ENGINE_DESIGN.md` unaffected (schema-level behavior refinements/bugfix, not a design-level change).

## Triage candidates (all deferred to Admiral — filing is outside inherited latitude)
1. **[float — out of ownership]** `skills/workbench/references/checklist-engine.md` L98-112 "Known gaps" documents the #189 survey-display and #190 coattails gaps as *flagged-not-fixed* — both now CLOSED by this PR. Stale; needs an update outside this run's file ownership.
2. **[defer]** Optional Fowler DRY: the 2-line current-why-id lookup (`_latest_why_record` → id) is duplicated in `_trip_advisory` and `_trip_hard_gate`; a `_latest_why_id()` helper would DRY it. Kept minimal per pre-ruling.
3. **[defer]** Minor display precision: the `REFRESH REQUESTED:` line shows the current `_latest_why_record` id, not the pending request's `payload.why_ref` (they differ only in the stale-request edge #190 addresses) — tighten the display to show `payload.why_ref`, or reword the doc.

## Workflow feedback (staged, fenced closeout)
Durable root resolves to the read-only main checkout, so feedback was staged per the fenced-closeout rule at `C:/Programs/cs-wt-cg/.agent-work/staged-feedback/cg-fastfollows-198/` (AGENT_FEEDBACK.md + lessons-delta.json + CONSTELLATION_FEEDBACK.md + FENCE.md; `verify_agent_feedback.py --phase feedback` → ok). **Please harvest that trio.** Three lessons banked (none ripe):
- `config-ref-absent-skill-source` [commander]: the plan/survey templates' `config_ref: docs/agents/engine-config.json` is absent in skill-source repos; **all 4 crews** rediscovered the inline-config convention. Needs-human apply (template/doctrine) — deferred to you.
- `doc-handoff-anchor-not-line-number` [handoff]: doc handoffs should anchor on symbols/sections, not line numbers.
- `handoff-test-assertion-realizable-per-type` [handoff]: a dictated test assertion must be realizable for the type under test (the #189 handoff's why_ref-pointer assertion overreached for surveys).

What worked: fully-specified per-fix handoffs (line anchors + exact expected behavior + backward-compat constraint + "prove the tests fail pre-fix") yielded correct first-try implementations and rigorous reviews. Driving the spine with the stable installed workbench engine while tests exercised the under-edit repo engine was the right isolation for this meta-run.

## Run shape
Full commander spine init→archive (10 steps) driven through the engine + execute.json (2 crew gates × implement/review/integrate, all closed). 4 crews dispatched at opus (2 implementer, 2 reviewer) via the external backend + Agent-tool subagents + `run_crew.py --verify-result`. c4/c5 plan rigor (alternatives/cold-critic) surfaced as named untaken roads — plan frozen by launch-order pre-rulings; adversarial verification delivered at the gate reviews instead.
