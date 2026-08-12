# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Distill a concrete interface/field/doctrine fix into a lesson carrying a `target`, settled at the Commander `feedback` step's forced apply-or-defer gate; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing. The useful entries name the exact step, field, or instruction that was ambiguous, missing, contradictory, or routinely improvised around. A `none` bullet requires a run-specific reason (`none — confirmed after review: <what you checked>`); entries whose signal sections are all bare `none` fail the feedback invariant check.

Newest entries on top.

---

## `2026-07-19` — `issue-155`

**Run shape:** `commander (delegated, launch order W3-155-docbatch.md, issue #155)` · `10/10 spine steps closed` · `sonnet`

**Instruction adherence:** `minor deviations`
- Followed the spine/execute.json gate structure fully, but the `g1-implement` gate's edits were made directly by Commander rather than dispatched to a subagent implementer — documented in execute.json's `g1-implement` imperative and reasoned there (bounded doc-only batch, 3 pre-ruled files, no load-bearing design decisions, Commander already held the grounding context from plan authoring). The independent-reviewer gate was NOT skipped (team-lead directive, launch order silent on it either way) and provided real peer-tier verification of the deviation.
- `--from-child` on `advance execute` does not apply to a `gated` child checklist (only `survey` children carry a `consolidation` object; `consolidate` itself refuses on a `gated` file) — dropped `--from-child` and advanced the spine `execute` step directly with a `--why` citing the child's own closed gates. See Improvement signals.

**Friction / unclear:**
- The `init` task's postcondition `c1` is `check: {"kind": "command", "command": "py .../init_work_area.py issue-155"}` with no `--root`/`--spine` flags recorded — re-running it bare (as the check literally does) is idempotent and harmless here, but it does NOT re-verify that the *originally intended* `--spine` template was the one instantiated; a stale/wrong spine template would still pass this check.
- `attest <task> --cond <id>` requires `--which preconditions` to target a `p*` id; the plain form silently assumes `postconditions`, and the CLI error message ("preconditions unmet ['p1']") doesn't itself say to add `--which preconditions` — had to infer it from the `--help` text. A one-line hint on that specific REFUSED message would save a round trip.
- `checklist_engine.py --file <f> <verb> --session-id <id>` errors if `--session-id` is placed as a global flag before the verb — it is a per-subcommand flag, not a top-level one, but the top-level `--help` doesn't make that obvious until you hit the specific subcommand's `--help`.

**Crew-reported friction:**
- From the independent reviewer's `g1-review` REVIEW_RESULT.md Workflow Feedback: the handoff's line-number pointer ("lines 172-229" into `checklist_engine.py`) was close but the doc's claims also depended on `dispatch()` (~1753-1799) and `main()`'s `except EngineError` handling (~1924-1949), sitting far from that range — a future "doc describes mechanism X" handoff should point at all the anchors the doc's claims actually span, not just the primary one. Also noted: running the full 12-smell Fowler pass with honest `absent` verdicts satisfied "visit every item" for a docs-only diff without needing the `rail_exception` skip mechanism at all — a legitimate default, not an improvisation gap.

**What worked:**
- The Honest-Null Clause paid off directly: a full grep audit across all 19 `skills/*/SKILL.md` files found the launch order's presumed "implementer engine-ref drift" item already correct on current main (every reference already qualifies `references/checklist-engine.md` with `workbench`, except the file's own self-referential copy in `workbench/SKILL.md`) — reporting the measured null with the grep evidence was a complete deliverable for that item, no wasted edit.
- The File Ownership fence's explicit exclusions (`docs/RECURSIVE_IMPROVEMENT_DESIGN.md`, "any template") correctly forced the harvest epic-id-stamp item to triage rather than an out-of-fence edit — the fence did its job of preventing a same-wave collision with sibling commanders.
- Dispatching a genuinely fresh-context reviewer (via `run_crew.py --backend external` + Agent tool + `--verify-result`) against the uncommitted working-tree diff caught nothing wrong, but independently re-derived every claim (suite re-run, `_rail()` source cross-check, grep re-run) rather than trusting the handoff's assertions — real peer-tier verification, not rubber-stamping.

**Improvement signals:**
- `advance <spine-step> --from-child <path>` should either accept a `gated` child (deriving an implicit "all terminal" consolidation from `items` state) or its own `--help`/error text should say plainly "only a `survey` child carries `consolidation`; for a `gated` child, advance without `--from-child`" instead of the current two-step discovery (REFUSED "not found" on a relative path, then REFUSED "no consolidation yet" on the absolute path, before the actual cause surfaces via source read) → disposition: distilled to a lesson below (applied nowhere yet — this is an engine ergonomics gap, not a doc fix Commander can make; needs human review of whether `--from-child` should special-case `gated` or whether the doc/help text is the right fix).
- `agent_work_root.py` staleness (named in the launch order's Inherited Context as a known friction) DID bite this run exactly as predicted: `verify_agent_feedback.py issue-155 --phase feedback` with no `--root` override resolved `durable_root` to the **main checkout** (`C:\Programs\constellation-skills\.agent-work\AGENT_FEEDBACK.md`) and refused ("does not mention work id"), even though the worktree-local `.agent-work/AGENT_FEEDBACK.md` (this file) already carried the entry. Adding `--root .` immediately resolved it correctly to the worktree. The launch order's documented workaround is exact and sufficient — confirming it here so a future wave can trust the workaround without re-deriving it, pending the actual fix (installing the post-#118 `agent_work_root.py` into the commander bundle).

---
