# x1 shared core — read this first (identical for designers A/B/C)

## The one question you are designing an answer to

**How does the checklist engine reach the agent at each decision point** — step entry (`advance`/`current`),
check-FAILURE, turn-end, post-compaction, and terminal release — so a cheap model finishes the workflow
honestly? Three delivery channels are on the table: engine response text, Claude Code hooks
(SessionStart-on-compact, Stop-hook turn-end refusal), and a conductor loop (the engine owns the loop and
spawns step-scoped agents). Your handoff assigns YOUR channel constraint.

You are ONE of THREE parallel designers, each under a different named constraint. Design the SAME
interface. Do not hedge toward a generic middle — push your constraint hard; the contrast is the
deliverable.

## Ground truth you design against (all field-measured, do not re-derive)

- Repo: `C:\Programs\constellation-skills` (read-only for you — design docs only, NO code changes; the
  engine is fenced during design). Engine source: `scripts/checklist_engine.py`. Skill corpus:
  `skills/`. Shared doctrine: `skills/_shared/global-everyone.md`. Eval harness:
  `scripts/run_skill_eval.py`, scenarios under `evals/`.
- Baseline failure: a cheap model (sonnet) given the dieted corpus skipped/theatered/fabricated the
  workflow in ~2/3 of runs. Catalogued shades: skip, theater, quit-early, fabrication (hand-written
  spine), completion-theater-at-the-finish (false "released" claim), wait-by-ending-turn.
- Four wording clauses in ONE skill (commander-delegated) took it to 3/3 strict terminal completion:
  (1) engine-first entry ritual; (2) "the solution is the MIDDLE, not the end"; (3) release-after-
  final-advance ordering at archive; (4) wait-loop (never end your turn to wait). These prove WORDING
  AT THE DECISION POINT works — the design question is delivering that force from the engine/harness
  side so all skills inherit it without nine hand-maintained copies.
- Bare one-line pointers to doctrine files do NOT fire at load time for cheap models (simplification
  review, `.agent-work/dispatch-126-127/SIMPLIFICATION_REVIEW.md`).
- Provenance machinery that already exists (understand it before designing): session lease
  (claim/heartbeat/release), journal sidecar `<state>.json.journal` (hash-chained verb log), eval
  checks that cross-verify lease window vs journal; "release is the LAST journaled action" is a
  test-pinned invariant.
- SETTLED IN SESSION (do not redesign): the engine-emitted `work-complete.txt` sentinel is DEAD —
  that file is part of the eval TASK (customer deliverable), not the workflow; the journal already is
  the unfakeable completion record. Do not propose the engine writing task artifacts.
- Cold-start economics: crew/agent cold-starts ≈ 23 min of a 29-min honest run; spine ceremony ≈ 3 min.
  Any design that multiplies cold-starts must say where that cost is paid and why it's affordable.
- Issue #134 (gate-vs-fence reconciliation) folds into this design — read it (`gh issue view 134`).
- Timing hazard: an alongside research excursion is verifying whether hooks fire for Agent-tool
  subagents and headless `claude -p` runs. If your design depends on that answer, state the dependency
  and design the fallback.

## Hard constraints (standing human decisions — violating any is a failed design)

- Eval `task.md` prompts carry ZERO test-awareness and ZERO workflow coaching. The skill + engine must
  carry the agent.
- Superpowers is a competitor: no imported doctrine, no citing it, constellation-native framing.
- Proportionality may change HOW a step is done (inline vs crew), never WHETHER a step runs.
- Any turn-end refusal / nudge mechanism MUST have an escape hatch (engine `block`/`waive` verbs, a
  bounded nudge counter) — a stuck agent must be able to stop honestly, never loop-burn.
- No prevention-of-lesson-capture machinery.

## Deliverable (write to the exact result path in your handoff)

A design doc containing:
1. The contract: at EACH decision point (step entry, check-failure, turn-end, post-compaction,
   terminal release) exactly what the agent sees or is forced to do under your channel — concrete
   example payloads/outputs, not descriptions.
2. Where the doctrine text lives (engine strings? template fields? hook script? shared file?) and who
   owns updating it.
3. Eval-check implications: what the #129 harness checks would need to change, if anything, and
   whether that makes the measured bar stricter/weaker/unchanged — be explicit.
4. Failure-shade coverage table: for each catalogued shade, does your design prevent it (mechanism),
   deter it (wording at the moment), or leave it to doctrine?
5. Axis self-assessment: depth, locality, seam placement, testability — honest, including where your
   constraint hurts.
6. What you deliberately did NOT solve (scoped, for the comparison).

Budget: ≤30 minutes. Report a partial design rather than overrun. Your final message must state the
result file path and a 5-line summary. The result FILE is the deliverable — write it before idling.
