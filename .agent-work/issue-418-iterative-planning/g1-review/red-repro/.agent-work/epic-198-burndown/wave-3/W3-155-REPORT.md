# W3-155 Report — epic-138 doc/doctrine graduation batch

**Commander:** commander-docs (delegated, sonnet) · **Branch:** `docs/doctrine-batch-155` (base `1f3417f`) · **PR:** https://github.com/fredcai6/constellation-skills/pull/211 (NOT merged — Admiral merges) · **Date:** 2026-07-19

## Worktree isolation
```
worktree OK: in C:/Programs/cs-wt-docs
```
(`py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-docs`, run before any git op.)

## Verdict — per item

| # | Item | Verdict |
|---|---|---|
| 1 | `skills/_shared/windows.md` headless-probe recipe | **LANDED** — new §6, positive-recipe form |
| 2 | `skills/implementer/SKILL.md` engine-ref pointer + sibling audit | **HONEST NULL** — already correct on current main |
| 3 | `docs/CHECKLIST_ENGINE_DESIGN.md` `_rail()` surface | **LANDED** — new section, verified against source |
| 4 | Harvest epic-id-stamp convention | **NOT EDITED** — no clean home in this wave's fence; routed to triage (`tc1`) |
| 5 | State-note-precondition framing | **DEFERRED** per Admiral ruling — triage-noted (`tc2`), not touched |

### Item 1 — `skills/_shared/windows.md`
Added `## 6. Headless hook-probe: verifying a settings.json hook actually fires`, matching the file's existing 5-section positive-recipe house style (Works / Fails / Grounded). Content: `claude -p ... --allowedTools "Bash"` (real, non-bypass permission mode) fires PreToolUse/PostToolUse and SessionStart/Stop headlessly; `--dangerously-skip-permissions`/`bypassPermissions` is classifier-refused headless (process never launches, no hook fires at all); a bare `claude -p` fires SessionStart/Stop but every tool action is silently denied (no interactive approver headless), so it can never exercise PostToolUse. Grounded: lesson `headless-hook-probe-allowedtools`, #141/PR #150 (both confirmed CLOSED/MERGED via `gh`).

### Item 2 — implementer engine-ref pointer (HONEST NULL, evidence)
Grepped all 19 `skills/*/SKILL.md` files for a bare, unqualified `references/checklist-engine.md` pointer:
```
grep -rn "checklist-engine\.md" skills/*/SKILL.md
```
Every cross-skill mention already reads `workbench `references/checklist-engine.md`` (charter, cartographer, admiral, scout, interrogator, lessons-auditor, explorer, implementer) or a fuller equivalent phrasing (`reviewer/SKILL.md`: "the constellation-workbench skill's bundled `references/checklist-engine.md` under the installed workbench skill directory"). The only bare, unqualified `references/checklist-engine.md` occurrence is inside `workbench/SKILL.md` itself — correct, since workbench is the owning skill (self-referential, resolves relative to its own directory). `git log -p --follow` on `skills/implementer/SKILL.md` confirms this "workbench `references/checklist-engine.md`" phrasing predates this wave by many commits — it was never drifted. **No edit made.** Independently reproduced by the fresh-context reviewer (see below).

### Item 3 — `docs/CHECKLIST_ENGINE_DESIGN.md` `_rail()` surface
Added `## The rail: engine-carried doctrine at decision points (_rail(), #140)` between "Bounding rework" and "Evidence: gate on type/shape, not quality." Read `scripts/checklist_engine.py` directly (lines 160–229 plus `dispatch()` ~1753–1799 and `main()`'s `EngineError` handling ~1924–1949) to document accurately: the 6 railed verbs (`RAIL_VERBS`), the 5 frozen decision-point strings (`_RAIL_STRINGS`: early/mid-flight/check-failure/near-terminal/terminal), the position-derivation rules (`_rail_position`), the check-failure trigger (keyed on the `EngineError` refusal path in `main()`, not derivable from spine `items` state — the one point that isn't), the gated-only scope (a `survey` gets no rail), and the canonicality relationship to `skills/_shared/global-everyone.md`'s "Completion enforcement" section (table wins on conflict). Independently cross-checked by the reviewer against the same source ranges — no discrepancy found.

### Item 4 — harvest epic-id-stamp convention (routed, not edited)
The natural home is `skills/workbench/templates/AGENT_FEEDBACK.template.md`, but this wave's File Ownership fence explicitly excludes "any template." The Pre-Rulings' suggested alternative, `docs/RECURSIVE_IMPROVEMENT_DESIGN.md`, is also explicitly excluded (just edited by #118). Since both candidate homes are outside this wave's fence and neither of my two owned files (`windows.md`, `CHECKLIST_ENGINE_DESIGN.md`) is a plausible home, this is routed to triage as `tc1` on `execute.json` per the Pre-Rulings' own escape valve ("add elsewhere or note as triage if no clean home"). **Filing a new GitHub issue was explicitly named a FLOAT item in Inherited Latitude**, so it was floated here rather than self-filed.

### Item 5 — state-note-precondition (deferred, triage-noted)
Not edited, per the Admiral's explicit Pre-Ruling (low-confidence, needs human review). Recorded as `tc2` on `execute.json`.

## Process note: documented deviation

The two in-scope edits (items 1, 3) were made directly by Commander rather than dispatched to a separate implementer subagent — recorded in `execute.json`'s `g1-implement` imperative. Reasoning: bounded doc-only batch against 3 pre-ruled files with zero load-bearing design decisions; Commander already held the grounding context (grep audits, `gh issue view 140/141`, reading `checklist_engine.py`) from plan authoring, and dispatching a fresh implementer would force it to redo the identical reads with no bounded low-tier slice to isolate. **The independent-reviewer gate was NOT skipped** and provided the peer-tier verification this deviation would otherwise forgo.

## Evidence

### Independent reviewer (fresh context, distinct from the editor)
Dispatched via `run_crew.py --backend external` (registry: `constellation/issue-155/g1/reviewer/attempt-1`) + Agent-tool subagent + `--verify-result` (verified `fresh (completed)`). **Verdict APPROVE, 0 blockers.** Re-derived every claim independently rather than trusting the handoff: re-ran the full suite (898 passed / 2 skipped / 244 subtests, exact match), re-read `checklist_engine.py`'s `_rail()`/`_rail_position()`/`dispatch()`/`main()` against the new doc section (no discrepancy), re-ran the honest-null grep himself (reproduced exactly), ran the full 12-smell Fowler pass (all `absent` with substantive per-smell reasons, `verify_fowler_pass.py` exit 0). Full result: `.agent-work/archive/2026-07-19-issue-155/g1-review/REVIEW_RESULT.md` (worktree, archived).

### Full suite
- Baseline (pre-edit): `py -m pytest -q` → **898 passed, 2 skipped, 244 subtests** (63.32s).
- Post-edit (reviewer + engine `g1-integrate` postcondition): same — **898 passed, 2 skipped, 244 subtests**. No delta, as expected for a doc-only change.

### Diff scope
`git diff --stat`: `docs/CHECKLIST_ENGINE_DESIGN.md | 33 +++...`, `skills/_shared/windows.md | 19 +++...` — 2 files changed, 52 insertions(+), 0 deletions(-). No other file touched; File Ownership fence respected (`scripts/curate_corpus.py`, `docs/RECURSIVE_IMPROVEMENT_DESIGN.md`, `docs/CHECKLIST_SCHEMA.md`, all templates, and sibling `skills/*/SKILL.md` files all confirmed absent from the diff).

## Map impact
Skill-source repo — no `docs/architecture/` packet map (confirmed at the context step). Reasoned no-op at reconcile: both edited files ARE the structural record for what they document (`windows.md` is its own canonical source; `CHECKLIST_ENGINE_DESIGN.md` is the design doc being updated to match already-shipped code) — no further reconciliation target exists.

## Triage candidates
- **tc1 — harvest epic-id-stamp convention:** needs a future wave/issue with write access to `AGENT_FEEDBACK.template.md` or `RECURSIVE_IMPROVEMENT_DESIGN.md` (or a ruling on an alternative home). Not self-filed as a GH issue (outside Inherited Latitude — floated here instead).
- **tc2 — state-note-precondition framing:** carried forward per the Admiral's existing Pre-Ruling; needs human/Admiral review before any future wave acts on it.

## Workflow feedback (full entry in AGENT_FEEDBACK.md)
Full entry appended to the worktree-local `.agent-work/AGENT_FEEDBACK.md` (dated `2026-07-19`, work-id `issue-155`) — not restated here in full, see that file (archived alongside the run; also copy-pasted below for convenience since `.agent-work/` is gitignored and not part of the PR diff).

**Key finding on the known agent_work_root friction:** unlike a prior wave's report noting `.agent-work/` "resolves (git-common-dir) to the MAIN checkout" and falling back to the staged-feedback/FENCE.md path, I found the **`--root .` workaround named in Inherited Context works exactly as documented** — `verify_agent_feedback.py issue-155 --phase feedback --root .` (and `--phase archive --root .`) both resolve correctly to this worktree and pass, once the worktree-local `AGENT_FEEDBACK.md` entry and the archived work-area package exist. The bare command baked literally into `spine.json`'s postcondition (no `--root` flag) still fails as predicted — I force-waived `feedback.c1` and `archive.c1` with reasoning citing the independently-verified `--root .` pass, per the launch order's own sanctioned workaround, rather than routing to the heavier staged-feedback/FENCE.md path (which is for when the write is genuinely impossible, not just under-flagged by the spine's literal check command).

One new lesson banked (`from-child-gated-consolidation-refusal`, scope `constellation`): `advance <spine-step> --from-child <execute.json>` assumes the child is a `survey` (reads `.consolidation`, set only by `consolidate`, which itself refuses on a `gated` file) — a `gated` execute.json (the normal Commander-execute-plan case) has no `consolidation` key, so `--from-child` REFUSED twice (path-not-found, then no-consolidation-yet) before the real cause was findable only by reading engine source. Banked, not applied — needs a human design call on whether `--from-child` should special-case `gated` children or whether only its REFUSED text should improve, and `checklist_engine.py` is outside this run's file-ownership fence regardless.

## Spine provenance
Full spine driven init→context→understand→plan→execute→reconcile→triage→review→feedback→archive through the engine (lease `commander-issue-155`); `execute.json` (4 items: e0-context, g1-implement, g1-review, g1-integrate) driven to DONE with an independent reviewer dispatch at g1-review. Lease released as the final journaled action after archive's closing advance. Archived work area: `.agent-work/archive/2026-07-19-issue-155/` (in the worktree, gitignored, not part of the PR).
