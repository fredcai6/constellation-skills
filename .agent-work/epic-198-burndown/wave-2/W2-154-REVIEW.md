# W2-154 Independent Review — PR #203 (`fix/init-placeholder-154`)

**Reviewer:** reviewer-154 (independent, fresh-context) · **Verdict: APPROVE**
**Target:** PR #203, closes #154 (+ dup #114) · worktree `C:/Programs/cs-wt-init` @ commit `6486d07`, base main `d524b41`.
**Survey (engine-driven):** `.agent-work/epic-198-burndown/wave-2/154-review/review.json` — 7/7 checks recorded pass, consolidated APPROVE, 0 open findings.
**Fowler record:** `.agent-work/epic-198-burndown/wave-2/154-review/fowler-pass.json` — `verify_fowler_pass.py` exits 0.

I was handed this as the team-rigor oracle because the authoring commander deliberately skipped an independent reviewer. I graded the work; I did not rubber-stamp it. Every claim below was reproduced from source, not accepted from the report.

## Result: APPROVE

All six review criteria verified independently and reproduced. No blockers.

### 1. Resolver correctness — VERIFIED
Ran `resolve_spine()` against all three real shipped spine templates (root=repo, auto-detect):
- **Admiral** `<admiral-skill-dir>`(5) and `<admiral-session-id>`(2) resolve; after resolution the ONLY surviving `<...>` token is prose `<engine>`. **Zero resolver-owned survivors.**
- **Commander** path byte-identical (only prose `<date>/<engine>/<file>/<path>/<spine-template>` survive). **Explorer** generic `<skill-dir>` resolves (only `<N>/<date>/<engine>` survive).
- **Hyphenated roles**: `<lessons-auditor-session-id>` → `lessons-auditor-<work-id>`, `<lessons-auditor-skill-dir>/scripts/...` resolves correctly. No mis-parse.
- **No over-substitution**: `<my-skill-dir-notes>` left untouched; generic `<skill-dir>` not mis-captured as role `skill`; bare `<session-id>` untouched.

### 2. Hard-check soundness (the KEY RISK) — VERIFIED
- **No false-positive on prose placeholders.** The assertion regex `<(work-id|[A-Za-z0-9-]+-skill-dir|[A-Za-z0-9-]+-session-id)>` was run against all three fully-resolved templates: it does NOT match any of the six shipped prose placeholders (`<engine>`, `<date>`, `<file>`, `<path>`, `<spine-template>`, `<N>`). Enumerated the complete placeholder inventory of every shipped template to confirm this — a false-positive here would break every future scaffold, and there is none.
- **Would have caught epic-138's real defect.** Simulated the pre-fix (commander-only) resolver on the admiral template, then ran `_assert_no_resolver_placeholders` on the output: it RAISES `SystemExit`, naming `<admiral-session-id>, <admiral-skill-dir>`. The check catches exactly the class of defect the issue describes.

### 3. stage_feedback.py — VERIFIED (both phases, live)
Ran `stage_feedback.py` live to write the 4-file trio, then verified its own output with the real `verify_agent_feedback.py`:
- `--phase feedback` → exit 0 (`agent feedback invariant ok`).
- `--phase archive` (with work area swept + archive package present, as the archive-phase negative checks require) → exit 0.

Note (non-blocking): `stage_feedback.py` wraps the caller's feedback body verbatim; it does not itself validate that the body carries bullets under the three signal sections. A content-free body still produces a trio that `verify_agent_feedback` correctly REJECTS downstream. This is by design (documented in the script: content is the caller's responsibility; the tool mechanizes layout). My first live run failed the feedback phase precisely because I passed a prose-only body — operator error on my part, not a script defect; a compliant body passes cleanly.

### 4. Regressions — VERIFIED
`py -m pytest -q` → **887 passed, 2 skipped** (matches report). New files: **36 passed** (23 init + 13 stage_feedback). `git diff main...HEAD` touches **exactly** the 4 owned files; fenced-out `run_skill_eval.py` / `checklist_engine.py` / `hooks/spine_rail.py` untouched. Working tree clean after verification.

### 5. Meaningful tests — VERIFIED
Restored `main:scripts/init_work_area.py` (pre-fix source) and ran the new tests against it: **all 9 new tests FAIL** (14 pre-existing pass) — 5 with `AttributeError: no attribute '_assert_no_resolver_placeholders'`, the rest on the un-generalized resolver. The tests genuinely catch the bug; they are not vacuous.

### 6. Fowler / refactoring pass — 12/12 smells verdicted, rail exit 0
- **flagged (both LOW-severity, non-blocking observations):**
  - `duplicated-code` — token-family knowledge is spread across three regexes (two discovery + one assertion) that must stay in sync when a fourth family is added.
  - `long-parameter-list` — `stage_feedback()` takes ~11 params; mitigated (keyword-only, defaulted, 1:1 with CLI flags, single call site). Worth a dataclass only if it grows.
- **overridden (logged standard + reason):** `data-clumps` and `speculative-generality` — subordinated to global-crew "minimal change / no speculative abstraction" and the #114/#154 handoff intent to prevent recurrence for the defect CLASS.
- All other baseline smells absent. The comment density is high but is genuine WHY-rationale matching the file's existing convention, not deodorant.

## Map impact verdict
Report's map-impact notes match the diff. No architecture packet exists in the skill-source repo (correctly noted). Durable context is routed, not dropped.

## Reconciliation / triage
- **tc1 (route to Triage, non-blocking):** `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (~L443, "Under-epic staging") should name `scripts/stage_feedback.py` as the tool that mechanizes the staged trio. Legitimate recommend-and-defer, outside this wave's file ownership.

## For the Admiral (governance, not a code defect)
The report honestly discloses that this run did **not** drive a `spine.json` / claim an engine lease / dispatch Implementer-Reviewer crews before implementing (tc2). That is a real process deviation, disclosed rather than buried. It is an Admiral/human governance ruling, **not** something that changes the code verdict: the change itself is correct, minimal, tested, and fully reproduced. I flag it for the Admiral's decision; it does not block the merge on technical grounds.

## Blockers
- None.

## Workflow Feedback
- **Handoff gaps:** none — the review handoff was unusually complete (named the KEY RISK, the exact commands, the artifact path, and the "you ARE the independent check" framing). This made grading straightforward.
- **Context rediscovered:** The survey template's `r0-context` imperative points at `docs/agents/CREW_CONTEXT.md`/`GLOSSARY.md`, which do not exist in the skill-source repo; degraded to global-only as `checklist-engine.md` says. Minor, expected.
- **Instructions improvised around:** The reviewer SKILL notes a survey-type checklist cannot surface a `refresh-request` via `current` (a known engine gap) — did not bite here (no trip fired), but confirms the caveat is live.
- **What would have made this easier:** Nothing material. The one genuine friction was self-inflicted (passing a non-bulleted feedback body to my own reproduction of `verify_agent_feedback`); the script's docstring already explains the content contract.

## Return status
`complete`
