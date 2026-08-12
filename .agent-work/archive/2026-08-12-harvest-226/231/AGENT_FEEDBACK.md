# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Distill a concrete interface/field/doctrine fix into a lesson carrying a `target`, settled at the Commander `feedback` step's forced apply-or-defer gate; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing. The useful entries name the exact step, field, or instruction that was ambiguous, missing, contradictory, or routinely improvised around. A `none` bullet requires a run-specific reason (`none — confirmed after review: <what you checked>`); entries whose signal sections are all bare `none` fail the feedback invariant check.

Newest entries on top.

NOTE (commander-231, delegated run): this file was created **worktree-local**
(`C:/Programs/constellation-wt-231/.agent-work/AGENT_FEEDBACK.md`), not in the main
checkout's shared log, because `agent_work_root.durable_root()` resolves durability to
the worktree itself while epic-226's Admiral lease is `active` in the main checkout
(`.agent-work/epic-226/spine.json` — see `agent_work_root.py`'s "active epic lease"
exception). This is by-design fencing behavior, confirmed empirically
(`py agent_work_root.py` from this worktree prints the worktree path, not the main
checkout). **The Admiral must harvest this entry into the shared
`.agent-work/AGENT_FEEDBACK.md` before this worktree is swept** — flagged explicitly in
the commander-231 verdict's Workflow feedback section.

---

## `2026-07-24` — `commander-231`

**Run shape:** `commander (delegated, launch-order-driven)` · `init, context, understand, plan, execute (e0-context, g1-vocab, g2-seam, g3-implement/review/integrate), reconcile, triage, review, feedback` · `sonnet throughout (commander + both crew dispatches)`

**Instruction adherence:** `fully followed`
- Drove every spine step through the vendored engine (`scripts/checklist_engine.py`), never hand-edited a checklist JSON. PR-7 re-verified before planning (grepped the three named gaps against current code — all confirmed genuine, no drift since launch-order authoring). PR-6 re-confirmed against `install_constellation.py`'s `_GLOBAL_*` tuples before editing `commander-core.md`. Two reasoning gates (g1-vocab, g2-seam) used the pre-authored invariant-chain pattern from `commander-core.md` §"Doc-only gates" instead of dispatching a crew for prose/template edits; one crew gate (g3) built and reviewed the round-trip regression test, dispatched via `run_crew.py --backend external` + a synchronous Agent-tool subagent + `--verify-result`, mirroring `crew-dispatch.md` exactly.

**Friction / unclear:**
- `--from-child` on the parent spine's `execute` step: the engine REFUSES a `gated` child (no `consolidation` field) even though the imperative text for the `execute` step doesn't itself warn against trying `--from-child` first — the correct recipe (direct `attest` citing per-gate evidence) is documented in `docs/CHECKLIST_SCHEMA.md`'s `advance --from-child` row, not surfaced at the point of the refusal. Cost one extra round-trip to discover.
- `--from-child <path>` resolves the path against the **parent checklist's directory** (dirname of `--file`), not cwd — tripped on this twice (passed a path relative to cwd, got "not found," had to re-read `docs/CHECKLIST_SCHEMA.md` line ~357 to get the resolution rule right). The REFUSED message itself ("child checklist X not found") doesn't hint at the resolution rule, only the doc does.
- `consolidate` on a `gated` checklist (`execute.json`) is refused ("consolidate is for survey checklists") — expected once I thought about it (gated checklists don't carry a single verdict), but the `execute` step's imperative text doesn't say "don't try to consolidate the child," so I attempted it before releasing the child lease. No real cost, just a wasted call.

**Crew-reported friction:**
- g3-implement (IMPLEMENTER_RESULT): the exact `attach --type ... --field K=V` CLI shape and the `why_exempt`/`--mechanical` requirement for a non-exempt gate's `advance` were not called out in the handoff itself; the implementer confirmed them by reading `checklist_engine.py` directly. Suggests: a fixture-building handoff (one that authors a small checklist JSON to drive through the engine) should name `why_exempt` explicitly, since a fresh `gated` task defaults to non-exempt and an unprimed builder hits an unrelated `--why` refusal unrelated to the mechanism actually being proven.
- g3-review (REVIEW_RESULT): the reviewer skill's `append`-for-per-rule-checks pattern lands new sibling checks (`r4a`/`r4b`) at the end of the survey's `items` list rather than immediately after their anchor (`r4-quality`), so `current` surfaced them out of the order they were conceptually grouped in. Reviewer flagged it as a cosmetic journal-order artifact, not a defect — no action taken this run.

**What worked:**
- The pre-authored invariant-chain pattern for doc-only reasoning gates (5 explicit `attest`-able postconditions on g1-vocab, 3 on g2-seam, each citing exactly what must be true) made closing those two gates fast and left no ambiguity about what "done" meant — no crew needed, no quality loss versus a crew gate.
- `tests/test_explorer_templates.py` was a clean, directly-mirrorable pattern for the new `tests/test_prototyper_templates.py` — the implementer cited it once and needed no further guidance to get the real-extraction + real-engine-subprocess shape right on the first pass (5/5 green, no rework).
- `run_crew.py --backend external` + a synchronous Agent-tool dispatch + `--verify-result` worked cleanly for both the implementer and reviewer gates — no registry conflicts, no stale-lease issues, freshness verified both by the wrapper and by the Commander's own independent re-run of the pytest commands.

**Improvement signals:**
- `--from-child`'s parent-relative path resolution and its gated-vs-survey applicability could use one line in the engine's own REFUSED message text (currently only in `docs/CHECKLIST_SCHEMA.md`), so the failure is self-diagnosing without a doc round-trip → disposition: distilled to a lesson-delta `add` this run (see `lessons-delta.json`); `scripts/checklist_engine.py` is fenced this wave (#227 owns it), so this cannot be applied directly — banked for a future engine-owning Commander to consider.
- Fixture-building implementer handoffs (a gate that authors a throwaway checklist JSON to drive through the engine) should name `why_exempt`/`--mechanical` explicitly up front → disposition: mentioned here; not banked as a standalone lesson (single data point, low severity, easily rediscovered by reading the engine source as this run's implementer did).
