# Launch Order: cmdr-617 - issue #617

## Mission

Run issue #617 end to end: persist FastF1's verbatim classification `Status` through the canonical database ingestion path, expose strict single/batch read APIs with provenance, define a tested consumer-boundary reliability-opportunity taxonomy that keeps unknown statuses explicit, and produce a measured 2022-2026 coverage/null/vocabulary audit. This is truth enablement for #389, not a DNF model. Deliver an independently reviewed ready PR or an honestly scoped blocker/null.

## Prior-Wave Verdicts (pasted)

Issue #606's decomposition gate found the DNF contribution **unidentifiable, not zero**. Across 2,036 race-classification rows for 2022-2026, canonical `session_classifications` had ordinal position but no status column and no P30 sentinel rows. The existing `<90%` lap-completion proxy omits drivers with no timed race lap, misses late retirements, and cannot distinguish mechanical failure from other causes. It must not be substituted for status truth.

Issue #616 then removed a reproducibility blocker: latent-power bundles now load in deterministic eval mode, sampled predict/backtest and race-week public paths require a strict uint32 seed, worker reconstruction and checkpoint identity preserve it, and same/fresh-process regression evidence is stable. PR #619 merged to `origin/main` as `a10912cc`; #616 is closed. This makes later channel measurements reproducible but does not itself identify DNF opportunity.

Issue #389 is explicitly blocked on #617. Its owner comment requires: after verbatim status is persisted and 2022-2026 are backfilled, hand off a season/round status-vocabulary audit and an explicit reliability-opportunity taxonomy with unknowns visible; then rerun the #606 DNF measurement before allocating capacity to #389. Do not tune or capacity-clear a tail from lap-completion proxies or ordinal classifications.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it - say so when overriding.

- The DB remains the only canonical source for analysis. FastF1 may be touched only in the ingestion/collector path.
- Store source status losslessly/verbatim. Do not normalize the persisted field or silently map unknown values.
- Preserve existing ordinal `position` semantics and existing callers. Backwards compatibility is secondary, but one clear strict interface is required.
- Interpretation belongs at a named consumer boundary. A taxonomy must distinguish at least reliability opportunity, non-reliability/non-finish, classified finish, and unknown/unmapped without guessing; exact categories are evidence-led and may be floated if source vocabulary makes the split ambiguous.
- Schema migration must be additive/idempotent for existing DBs and `schema.sql` must match the runtime upgrade path.
- Generated 2022-2026 DB mutations are audit evidence and must not be committed. Snapshot/restore exact tracked DB paths and prove `git diff --exit-code -- data` after any broad or backfill run.
- Do not implement #389's tail, sampling changes, model tuning, or fantasy capacity allocation.
- Test-drive schema/ingest/read contracts before production edits. Include direct malformed-input tests and an integration/validation query surface.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If FastF1 lacks status for a scoped season/session subset, report exact missingness, provenance, and vocabulary; do not invent a fallback or generalize the null beyond the tested data.

## Inherited Latitude

You may decide issue-scoped schema migration, ingestion/upsert, read API, taxonomy implementation, validation commands, documentation/map updates, and non-architectural refactors after alternatives are compared. You may run disposable/read-only backfills and audits. You may commit, push, and open a ready PR. Float to the Admiral before any architecture-boundary change, lossy status normalization, ambiguous taxonomy decision that changes reliability meaning, generated DB commit, scope expansion into #389, merge, issue closure, deletion, or destructive cleanup.

## File Ownership

You are sole writer in `C:/Programs/f1Brainz/.claude/worktrees/617-classification-status`. Own product/tests/docs required for #617 and `.agent-work/cmdr-617/`. Do not write the primary checkout. Stage the feedback trio plus `FENCE.md` under worktree-local `.agent-work/staged-feedback/cmdr-617/` for Admiral harvest. Do not commit `.agent-work` or database artifacts.

## Workspace

Absolute worktree: `C:/Programs/f1Brainz/.claude/worktrees/617-classification-status`

Branch: `codex/617-classification-status`

Base: `a10912cca35c2aaf761c75133c5cc277f1e5dcec` (`origin/main` after PR #619)

Provision command: `git worktree add C:/Programs/f1Brainz/.claude/worktrees/617-classification-status -b codex/617-classification-status origin/main`

First step, before any git operation: run `py C:/Users/fredc/.codex/skills/constellation-commander/scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/617-classification-status` and paste its output into the final report.

PR integration defaults to server-side merge. Do not merge.

## Inherited Context

- Read `docs/AGENT_GUIDE.md`, `README.md`, `TESTING.md`, `docs/architecture/index.md`, `docs/DOCUMENTATION.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, and `docs/architecture/packets/data.md` before planning.
- Python launcher is `py`, never `python`.
- Database is the sole analysis source; only ingestion calls FastF1.
- Data-layer schema/ingestion changes require migration/schema parity, unit tests, and integration/validation queries.
- Strict fail-fast interfaces; explicit missingness; no silent fallback.
- The broad evo suite is known to rewrite tracked DB fixtures. Snapshot/restore exact paths and prove clean data diff.
- Handoff verification commands must cover every file/seam named by close criteria or explicitly identify partial commands.
- Use the Commander engine and `run_crew.py` for implementer/reviewer dispatches; recover crew registry before each launch.

## Pre-empted Steps

The Admiral has confirmed mission ordering, prior-wave verdicts, and this bite's latitude. In delegated `understand`, `plan`, `triage`, and `review` user-decision gates, cite this frozen launch order. You still own map-first understanding, mission frame, design-it-twice alternatives, cold plan critique, TDD gates, reconciliation, triage, feedback, archive, commit/push, and ready PR.

## Data Locations

- Main-checkout live season DBs: `C:/Programs/f1Brainz/data/f1_data_2022.db` through `f1_data_2026.db` (owner state; read/backfill only when necessary, never commit or overwrite without exact backup/restore discipline).
- Worktree tracked DB copies may be stale relative to owner state. Establish the audit input identity explicitly.
- FastF1 cache/config follows existing collector conventions; do not invent an analysis-side source.

## Budget

- **Model tier (required):** high-reasoning/default Codex. Schema migration plus external-source vocabulary, consumer taxonomy, and multi-season audit carry silent-data-loss risk.
- **Compute/time, session-window:** bounded foreground tests and audit probes; do not launch multi-hour collection. If a full backfill would exceed the session window, stop with an idempotent command, exact scope estimate, and durable state note for Admiral-owned detached execution.

## Stop Conditions

Stop and return when scope crosses into #389/modeling; source vocabulary makes a reliability taxonomy ambiguous beyond the pre-ruling; a DB artifact would need committing; an architecture-boundary change is required; current DB/backfill provenance cannot be established; a destructive action is needed; or required evidence would need a multi-hour collector run. Query the Admiral for missing context rather than guessing.

## Return Shape

Write `.agent-work/cmdr-617/COMMANDER_RESULT.md` before going idle. Include: verdict; root cause/current truth; design choice and rejected alternative; files and commit; ready PR URL; exact tests and outputs; schema migration/upsert/read API evidence; 2022-2026 audit identity, season/round coverage, nulls, duplicates, vocabulary, taxonomy counts and unknowns; clean data diff; architecture/map impact; triage candidates; staged feedback location; workflow feedback; and the exact isolation verifier output. Do not merge or close #617.
