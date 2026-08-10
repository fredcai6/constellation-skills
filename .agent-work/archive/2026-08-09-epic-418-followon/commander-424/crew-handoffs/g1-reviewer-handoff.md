# Reviewer handoff — gate g1: the MCP front door

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g1-review`
**Worktree:** `/home/tommy/projects/constellation-skills-wt/f-424` · **Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch order.

## What was implemented

A second front door on the checklist engine: an MCP stdio server exposing the spine drive loop as
seven typed tools wrapping the engine's own `main(argv)`, plus per-dispatch config generation.

- `scripts/mcp_spine_server.py` — 7 tools covering 13 of 18 engine verbs
- `scripts/gen_mcp_config.py` — per-dispatch config generator keyed `session_id#agentId`
- `.mcp.json` — project-scope, interactive convenience path only
- `tests/test_mcp_spine_server.py` — 24 tests
- `map/` — rebuilt by the Commander after the new scripts made `map/INDEX.md` stale

## How to inspect the diff

```
cd /home/tommy/projects/constellation-skills-wt/f-424
git log --oneline a2ce8669..HEAD
git diff a2ce8669..HEAD
```

The implementer's own result, with its evidence, is at
`.agent-work/epic-418-followon/commander-424/crew-handoffs/g1-implementer-result.md`.
The gate plan is `.agent-work/epic-418-followon/commander-424/execute.json` (gate `g1-*`), and the
mission frame is `MISSION_FRAME.md` in the same directory.

## Task statement — what you are verifying

### The five protected-intent items. A breach of any one is a BLOCK even if everything else works.

1. **No engine logic is duplicated.** Every tool must build an argv and call
   `checklist_engine.main()`. `git diff a2ce8669..HEAD -- scripts/checklist_engine.py` should be
   empty. Look specifically for the subtle form: parsing engine *output* to decide behaviour is
   duplication in disguise.
2. **The gate imperative rides tool results verbatim** — byte-identical to the CLI projection, not
   summarized, truncated or reflowed. The implementer claims a demonstrated-failing negative control
   for this. **Verify the control actually fails**; a check that cannot fail is indistinguishable
   from one that passed.
3. **The CLI door stays**, and every uncovered verb has a documented CLI fallback. The uncovered set
   is claimed to be `skip`, `reopen`, `append`, `amend`, `flag-candidate`. Confirm the table is
   complete against the engine's real verb list — do not take the count on trust; enumerate.
4. **`settings.json` is never written at any scope.** Grep the whole diff.
5. **Each agent gets its own server instance**, keyed by `session_id#agentId`.

### The delivery-path decision — RE-VERIFY IT, do not inherit it

This is the highest-value part of your review, and it is here because a cold critic flagged that all
of this gate's config-generation work rests on a **single unreviewed observation** by the Commander.

The Commander's probe concluded: a project-scope `.mcp.json` is not picked up by a live session, and
on a fresh process it lands in `⏸ Pending approval` and never launches — so it cannot serve a cold or
headless agent, and per-dispatch config generation via
`claude -p --mcp-config <file> --strict-mcp-config --allowedTools ...` is the delivery path.

**Re-run that probe independently and answer one question the Commander did not:**

> Is `Pending approval` a **permanent** state for a project-scope server, or a **one-time first-use**
> state that clears once approved?

If it is one-time — i.e. project-scope `.mcp.json` would serve fine after a single approval — then
the delivery architecture is aimed at the wrong problem and that is a **BLOCK** with your evidence.
If it is permanent for non-interactive dispatch, say so and how you know.

### Ordinary review

Correctness, error handling, test quality (do the 24 tests assert behaviour rather than text
describing it?), and whether any guard that loops asserts what it looped over.

## Close criteria

Your verdict is `APPROVE` or `BLOCK`. `APPROVE` requires: the five protected-intent items hold; the
verbatim-imperative control is proven able to fail; the CLI-fallback table is complete against an
enumerated verb list; and the delivery-path question above is answered with evidence.

## Constraints and exclusions

- **Do not edit** `scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
  `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py` —
  fenced to a concurrent agent.
- **Do not fix** engine bugs #439, #446, #427, #443 — they are held constant across a later gate's
  two measurement arms.
- Do not hand-edit any checklist JSON or anything under `episodes/`.
- Reviewers verify; you do not rewrite the implementation. Findings go in your result.
- Out of scope for this gate: the tracer/measurement, same-gate equivalence as a property, and the
  DC2/DC3 identity tests. All are later gates. Do not review them here.

## Evidence already produced (re-run it; do not take it on trust)

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_spine_server.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Commander's own measurement after rebuilding the code map: **6 failed, 2157 passed, 1061 subtests**.
Those 6 are a pre-existing pinned set owned by a concurrent agent and are **not** this gate's:

```
tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_installed_path_rewritten_template_is_up_to_date
tests/test_feedback_tooling.py::FreshnessPathTokenTests::test_token_working_copy_up_to_date_against_promoted_baseline
tests/test_install_constellation.py::InterpreterProbeTests::test_sidecar_records_resolved_via_for_probe_success_and_fallback
tests/test_install_constellation.py::TemplateBaselineTests::test_seeded_working_copy_reads_up_to_date_against_baseline
tests/test_run_skill_eval.py::test_real_runner_process_death_leaves_resumable_state
tests/test_spine_rail.py::test_same_path_windows_normcase_sep_equivalence
```

The set may **shrink** under you (fine); it must not **grow**.

Host is Linux; corpus text assuming Windows is stale. Both `python` and `py` resolve to one venv
(3.12.3, pytest 9.1.1).

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g1-reviewer-result.md
```

**Write that file before ending your turn — the write is the delivery.** State the verdict as the
literal word `APPROVE` or `BLOCK`. Include the exact commands you ran with their real output, a
finding list with severities, any triage candidates (real findings outside this gate — named, not
fixed), and a `## Workflow Feedback` section saying bluntly where the skills, this handoff, or the
engine cost you attention.
