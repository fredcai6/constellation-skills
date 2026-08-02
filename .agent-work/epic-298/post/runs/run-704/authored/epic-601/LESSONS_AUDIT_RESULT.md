# Lesson Candidates: `epic-601` (stage-1 physics-as-feature-engine)

Fresh-context closeout audit, 2026-07-24/25. Driven through the checklist engine as a survey
(`.agent-work/epic-601-lessons-audit/audit.json`, lease `lessons-auditor-601`, terminal
`DONE: no open items`, released). **Deltas were APPLIED, not just proposed** — the dispatcher
(team-lead) explicitly authorized this for the lesson-inbox delta mechanism (never for a
doctrine `.md` edit, which stays human-gated; no doctrine `apply` ops were used here). Every
candidate cites a grounding artifact line; nothing ungrounded was applied.

**Playbook before:** 20/20 active (at cap). **Playbook after:** 18/20 active. Applied deltas
live at `.agent-work/epic-601-lessons-audit/delta-*.json` and `trimmed-*.json` (one file per
apply_lessons_delta.py invocation, applied in the order listed below).

## Candidates

### `reap-trap` (theme, not a new slug)
- **Scope:** `constellation`
- **Task-class:** `general-workflow`
- **Observed:** Long single detached completion-watchers (bare Monitor waits, lone background
  pollers) get harness-reaped mid-run, killing the watcher without killing the underlying work
  — the agent then *looks* stalled with nothing to show for it, when the real work was often
  fine. Five independent sightings this epic: Ship H's Wave-7 completion-watcher; PoweredF10's
  launch-step stall; PoweredF10's CLI-smoke death; the Phase-5 G5 implementer reap-looping
  ~80min on a dead pytest proc; ShipJ-629 stalling at commit+PR.
- **Cost:** repeated false-stall diagnoses, Admiral nudges/takeovers, one near-double-writer
  collision (see below), and — per ADMIRAL_LOG's own 2026-07-24 closing note — this was **the
  dominant recurring friction of the session**.
- **Proposal:** bounded chained waiters (each poll window under the reap threshold) or
  foreground in-turn polling instead of one long single waiter; liveness via PowerShell
  `Get-Process` CPU (not git-bash `ps`, an unreliable PID shim); true OS-level detach via
  `Start-Process -WindowStyle Hidden` (not `nohup ... &` in a Bash tool call, still
  harness-tracked).
- **Grounding:** ADMIRAL_LOG.md 2026-07-19 CORRECTION (Ship H); 2026-07-24 "POWERED F10 —
  pre-flight PASS + stall recovery"; 2026-07-24 INCIDENT "powered-run CLI smoke DIED"; 2026-07-24
  "INCIDENT + RECOVERY (Phase-5 G5 stall)"; 2026-07-24 "MERGE + PHASE 5 COMPLETE" (ShipJ-629);
  2026-07-24 "LESSON (recurring, now dominant this session)" (the Admiral's own synthesis).
- **Corroboration:** 5 independent telemetry-backed sightings in one epic, plus the Admiral's
  own closing-note synthesis — strongly corroborated, not assertion-only.
- **Confidence:** high
- **Routing:** `confirm`+`amend` **sibling** `lesson:crew-idle-strands-deliverable` (per the run
  brief's explicit instruction — **not** a new slug). Applied: amended the statement to fold in
  the root-cause diagnosis + concrete fix, confirmed (recurrences 3→4), re-exported with the
  richer diagnosis.

### `false-stall-diagnosis` (merged from two sightings, per the run brief's instruction)
- **Scope:** `commander`
- **Task-class:** `general-workflow`
- **Observed:** A background job that *looks* stalled may be healthy-but-slow or
  completed-but-sleeping. Ship H's batch-poll read raw row counts as a stall signal without
  accounting for smoke-run leftover rows and round-1's instant error rows under `strictly_pre`.
  Ship I's G7 real-telemetry smoke *and* its illustrative demo both stalled at the start line
  with no live process, yet code was committed afterward — a "completed-but-sleeping" trap that
  could have let the verdict imply real-data validation that never happened.
- **Cost:** a wasted diagnostic round on Ship H's side; on Ship I's side, a near-miss on an
  overclaimed verdict (caught by the reviewer, held for a minimal real pass before merge).
- **Proposal:** distinguish valid-vs-error/leftover rows and confirm CPU is actually climbing
  (not just row-count) for a resumable batch; for a claimed-complete deliverable, verify the
  producing process reached a real terminus (a captured verdict or traceback), not just that
  code was committed afterward.
- **Grounding:** `STAGED_CLOSEOUT_LESSONS.md` "Ship H" item 3; ADMIRAL_LOG.md 2026-07-19
  "RULING (G7 real-telemetry stall — quality gate)".
- **Corroboration:** two independent sightings, one with a concrete near-miss consequence
  (overclaim risk caught by review).
- **Confidence:** medium (two occurrences; the exact diagnostic checklist may need refinement
  against more job shapes — bank_reason says so explicitly)
- **Routing:** `add` (new lesson, no existing sibling found). Applied.

### `stale-map-reconcile-verify-against-final-commit`
- **Scope:** `commander`
- **Task-class:** `general-workflow`
- **Observed:** Ship I's Phase-4 (#513) cartographer reconcile ran against the PR's original
  base (`27b6eac9..HEAD`) and missed a post-review expansion (`a83d843a`/`807556b7`), leaving a
  false "real extractor not built" Known Limit in the architecture map after merge.
- **Cost:** a stale, actively-misleading architecture-doc claim that persisted from merge until
  a later consolidated pass caught and fixed it.
- **Proposal:** either (re)run the reconcile as the very last pre-merge step against the final
  diff, or do a consolidated post-merge pass that explicitly diffs the reconcile's covered
  commit range against the actual merged range before trusting it.
- **Grounding:** ADMIRAL_LOG.md 2026-07-24 "RECONCILE COMPLETE"; `POST_MERGE_MAP_RECONCILE_NOTES.md`.
- **Corroboration:** one occurrence, but with a concrete artifact-level consequence (a wrong doc
  claim caught and fixed) — not assertion-only.
- **Confidence:** medium (single occurrence; brief explicitly flagged as a candidate theme)
- **Routing:** `add` (new lesson). Applied.

### `admiral-message-queue-latency-coordination-hazard` (merges "Admiral-steered implementer" + the ShipJ-629 routing finding; G5 double-writer routed separately below)
- **Scope:** `admiral`
- **Task-class:** `general-workflow`
- **Observed:** A SendMessage to a delegated commander/implementer queues until that agent's
  own turn boundary — not delivered instantly. Three distinct epic-601 consequences of this
  ONE mechanism: (a) Wave-6 (#644): the Admiral steered/adjudicated the implementer directly,
  bypassing ShipG-644, which then polled superseded work for ~40min and mis-concluded a
  duplicate fix had shipped; (b) the G5 near-collision (below) shares this exact latency —
  the "stand down" message hadn't landed before the commander revived; (c) ShipJ-629 appeared
  to silently diverge from an explicit Admiral ruling and ignore two direct re-pings — the
  actual cause was message queuing, not non-compliance (confirmed after the fact).
- **Cost:** ~40min of wasted polling + a mis-read incident report (a); a near-double-writer
  collision (b, see below); an incorrectly-suspected non-compliance investigation (c).
- **Proposal:** when steering/adjudicating a commander's own implementer directly, either drive
  the change through the commander instead, or explicitly drain/notify it (one line) when
  taking over its gate mid-run. Before concluding a commander silently ignored a ruling, confirm
  the message was actually seen — expect ruling latency to scale with the commander's own turn
  length.
- **Grounding:** ADMIRAL_LOG.md 2026-07-19 "INCIDENT/LESSON-CANDIDATE (Wave 6 closeout,
  coordination gap)"; 2026-07-24 "ROUTING FINDING + σ-WIDENING RULING (ShipJ-629)"; 2026-07-24
  "RULING UPDATE (Phase-5 module layout...)".
- **Corroboration:** three independent sightings of the same underlying platform property in
  one epic — strong for a first observation.
- **Confidence:** medium-high (real, repeating, but the *mitigation* is untested — bank_reason
  says re-observe whether it actually prevents recurrence)
- **Routing:** `add` (new lesson, no existing sibling). Applied.

### `G5 double-writer` (near-miss)
- **Scope:** `admiral`
- **Task-class:** `general-workflow`
- **Observed:** Believing the Phase-5 G5 implementer's commander dead (stall symptoms), the
  Admiral TaskStop'd the stuck child and spawned a fresh replacement implementer (G5Finish).
  The commander then **revived** (any SendMessage wakes an idle agent) and began the identical
  work in the identical worktree — caught before any file writes; the replacement was dropped.
- **Cost:** a near-miss, not an actual collision — but it was close, and the existing lesson's
  "do NOT kill and relaunch" clause did **not** by itself prevent it, because the Admiral hadn't
  killed anything; it spawned a *parallel* writer while treating post-stand-down silence as
  equivalent to confirmed death.
- **Proposal:** before spawning a replacement writer into a believed-dead commander's worktree,
  either definitively confirm death (not just idle/unresponsive), or prefer unsticking the
  existing commander (TaskStop only its stuck child, then a wake message) over spawning a
  parallel writer.
- **Grounding:** ADMIRAL_LOG.md 2026-07-24 "NEAR-COLLISION + LESSON (Phase-5 G5 double-writer)".
- **Corroboration:** one live near-miss directly testing an existing lesson's exact clause —
  strong, not assertion-only.
- **Confidence:** high
- **Routing:** `confirm`+broaden **sibling** `lesson:idle-artifact-completeness-distinguisher`
  (the existing lesson already says "do NOT kill and relaunch... two-agents-in-worktree risk" —
  this is a direct, sharper re-validation, not a new slug). **Mechanical note:** this lesson had
  already auto-expired via the engine's own 10-run dormancy mechanism partway through this
  audit's harvest sequence (see Engine Mechanics below) before its confirm could land — recovered
  by re-adding fresh with the broadened statement and the G5 grounding as its initial citation.

### `CI-infra-failure-camouflages-gate-miss`
- **Scope:** `commander`
- **Task-class:** `ci-tooling`
- **Observed:** Phase 6 (#630)'s PR showed the pyright check red — but that job died at *setup*
  (infra failure), never running `scripts/pyright_baseline_diff.py`. The reflex "pre-existing red
  on main too, safe to merge" would have shipped 2 genuinely NEW pyright baseline errors that the
  gate exists to catch; caught only because the Admiral independently ran pyright locally.
- **Cost:** would have been a silent regression through the merge gate if not independently
  re-derived.
- **Proposal:** when a CI job that runs a self-test/baseline-diff gate infra-fails, re-derive the
  gate's verdict LOCALLY before merging — "the check ran and passed" and "the check never ran"
  are different claims, and a dead job proves neither.
- **Grounding:** ADMIRAL_LOG.md 2026-07-24 "PHASE 6 #630 VERDICT PASS + MERGE-GATE HOLD (2 new
  pyright errors)" + the paired "LESSON (→ closeout, real content)" entry.
- **Corroboration:** command-check-backed (2 concrete new pyright errors caught), not
  assertion-only.
- **Confidence:** high
- **Routing:** `add`+broaden **sibling** `lesson:ci-gate-selftest-in-ci-environment` (same
  underlying gate, `scripts/pyright_baseline_diff.py`, a second independent failure mode
  months apart — env-mismatch at 509-w3, infra-camouflage here). **Mechanical note:** like the
  G5 case, this lesson auto-expired via dormancy mid-harvest before the epic-601 grounding could
  land; recovered by re-adding fresh with the broadened statement, referencing its prior history.

### Frozen-methodology compute estimates must factor the thread cap
- **Scope:** `admiral` / `commander` (folded, see Routing)
- **Task-class:** `general-workflow`
- **Observed:** #644's blanket single-thread BLAS cap roughly doubled per-case fit time
  against a frozen ~28s/case estimate that predated the cap (Ship H's Phase-4 driver-utility
  batch: ~40min estimated, ~2h actual).
- **Cost:** a runtime surprise during live batch monitoring (resolved without harm — the
  Admiral recalibrated the guardrail in-turn rather than treating it as a stall).
- **Proposal:** factor a standing thread-cap guard into runtime estimates before trusting a
  frozen-methodology number.
- **Grounding:** `STAGED_CLOSEOUT_LESSONS.md` "Ship H" item 2 (explicitly noted "already in
  Phase-4 launch notes" by its own author — i.e. already self-corrected in-run).
- **Corroboration:** one occurrence, self-corrected same-run.
- **Confidence:** medium
- **Routing:** folded into the `admiral-owns-long-batch-compute` amendment below (same domain —
  compute-batch sizing/execution — rather than a standalone lesson for an already-self-corrected,
  narrow finding).

### PowerShell `-ArgumentList` multi-word argv tokenization
- **Scope:** `commander`
- **Task-class:** `general-workflow`
- **Observed:** `Start-Process -ArgumentList` did not reliably preserve a multi-word element
  (`"Great Britain"`) as one argv token; it silently arrived as two separate weekend ids,
  producing a wrong `n_weekends=3` count in the powered-F10 smoke run (gracefully caught, not a
  crash, but a real correctness bug in the launch mechanism).
- **Cost:** one silently-wrong smoke-run parameter, caught by comparing expected vs. actual
  weekend count rather than by any launch-time signal.
- **Proposal:** prefer the script's own in-code default/tuple (immune to shell tokenization)
  over `-ArgumentList` for multi-word values where possible; verify the receiving process's
  actual argv, not just launch success, when it can't be avoided.
- **Grounding:** `POWERED_F10_STATE.md` ("Caught bug (launch-mechanism, not code)" section).
- **Corroboration:** one occurrence, mechanically documented with before/after evidence.
- **Confidence:** medium
- **Routing:** folded into the `admiral-owns-long-batch-compute` amendment below (same domain —
  detached-process launch mechanics — rather than a standalone lesson).

### Self-authored full-suite regression checks need cost-sizing before freezing (625, 627)
- **Scope:** `commander`
- **Task-class:** `general-workflow`
- **Observed:** Both 625-segmentation-substrate and 627-unified-basis independently folded a
  self-authored full-repo/full-suite regression check into a gate's closing postcondition
  without sizing it first; both got reaped/ran 20-90+min under multi-agent contention and had
  to be waived to a diff-affected-import-graph subset at the worst possible time (finalization).
- **Cost:** two emergency float-and-waive cycles at closeout, in two different sub-runs of the
  same epic.
- **Proposal:** grep the real import graph of changed files FIRST and scope the check to actual
  importers rather than a blanket "run everything" command.
- **Grounding:** 625-segmentation-substrate's own `scope-self-authored-regression-to-import-graph`
  add (applied as its own lesson, see below) + 627-unified-basis's `AGENT_FEEDBACK.md`/
  `CONSTELLATION_FEEDBACK.md` item 3 (`integrate-fullsuite-vs-fast-gate-under-contention`).
- **Corroboration:** two independent sub-runs, same epic, same failure shape.
- **Confidence:** high (for the pattern); the standalone lesson 625 authored keeps its own
  `medium` self-rated confidence (n=1 from ITS perspective; this audit corroborates it with 627
  as a second, independent sighting)
- **Routing:** 625's own `add scope-self-authored-regression-to-import-graph` applied as
  authored (harvested faithfully). 627's matching CONSTELLATION_FEEDBACK.md item is corroborating
  grounding folded into the `admiral-owns-long-batch-compute` amendment (same underlying domain);
  not double-banked as a third lesson.

## Existing-Lesson Reconciliation

- `retire lesson:py-launcher` — graduated: verbatim in `CLAUDE.md`, `docs/agents/engine-config.json`, `docs/agents/CREW_CONTEXT.md`.
- `retire lesson:worktree-untracked-data` — graduated: verbatim in `docs/agents/CREW_CONTEXT.md`.
- `retire lesson:handoff-cite-exact-seam-signature` — graduated: verbatim in `docs/agents/CREW_CONTEXT.md` + `docs/agents/ORCHESTRATOR_CONTEXT.md`.
- `retire lesson:diagnose-first-decide-fix` — graduated: verbatim in `docs/agents/ORCHESTRATOR_CONTEXT.md`; re-validated this epic by 638-f12-stability-rework's G1 diagnosis overturning the launch order's hypothesis.
- `retire lesson:state-note-before-detach` — graduated: verbatim in the bundled `references/global-everyone.md`.
- `retire lesson:verify-claimed-side-effects` — graduated: verbatim in the bundled `references/global-everyone.md`; re-validated 3× this epic (625, 638, 627).
- `retire lesson:spine-lease-stale-long-crew` — graduated: documented in the bundled `constellation-workbench references/checklist-engine.md` "Session lease" section; not hit even once across 6 sub-runs.
- `resolve lesson:compact-step-skip` — verified fixed-upstream: `COMMANDER_SPINE.template.json` has no standalone compact step (folded into `execute.p1`), matching the 07-17 curator note; corroborated by zero sightings across 6 epic-601 sub-runs.
- `resolve lesson:run-crew-cli-launcher-misfit` — verified fixed-upstream: `run_crew.py`'s `BACKEND_EXTERNAL` is real and shipped, matching the 07-17 curator note; corroborated by 4 clean epic-601 uses. Noted the residual "3-step choreography" ergonomic complaint (630-phase6) as narrower and not itself re-banked.
- `export` (with discrepancy flag, **not** `resolve`) `lesson:engine-artifact-attest` — the 07-17 curator note's claim does NOT match installed `checklist_engine.py` source (`attest` still refuses artifact-kind postconditions); kept pinned/exported, not resolved. See CONSTELLATION_FEEDBACK.md for the full discrepancy writeup.
- `confirm lesson:loo-residual-diagnostic-over-self-weighted-predictor` — wave4-626's own op, applied as authored (g3/g5 LOO discipline, F1 signal-preservation guard).
- `confirm lesson:shared-files-not-on-mission-branch` — 624-phase0 + 630-phase6-bt-injection's own ops, applied as authored (the fencing exception fired for real in 630-phase6 — concurrent Admiral epic-lease in the main checkout).
- Auto-expired via the engine's own 10-run dormancy mechanism mid-harvest (not a deliberate audit choice): `disjoint-physics-channel-fencing`, `frontier-characterize-v-source` — no epic-601 grounding found for either, left retired rather than artificially resurrected. `admiral-close-after-merge-verified`, `idle-artifact-completeness-distinguisher`, `ci-gate-selftest-in-ci-environment` — DID have epic-601 grounding but expired before this audit's harvest-order reached their confirming trio; all three recovered via a fresh `add` with the epic-601 grounding folded in (see Engine Mechanics below for why).

## Applied Deltas (already run via `apply_lessons_delta.py`, not just proposed)

In order:
1. `delta-0-retire-graduated.json` — 7 retires (graduation).
2. `trimmed-624-phase0.json` — harvested (2 confirms already-relevant + 3 adds; 4 ops referencing
   already-retired lessons stripped before applying).
3. `trimmed-625-segmentation-substrate.json` — harvested (3 confirms + 1 add; 1 op stripped).
4. `trimmed-wave4-626.json` — harvested (2 confirms; 3 ops stripped).
5. `trimmed-638-f12-stability-rework.json` — harvested (1 confirm + 1 add; 2 ops stripped, 1 op's
   `task-class` key fixed to `task_class` — the sub-commander's authored JSON had a hyphen/underscore
   bug that would have failed for it too).
6. `trimmed-627-unified-basis.json` — harvested (2 confirms + 1 add; 4 ops stripped, including one
   ref to a lesson auto-deleted moments earlier by trio #3's tick).
7. `trimmed-630-phase6-bt-injection.json` — harvested (1 confirm + 2 exports; 2 ops stripped).
8. `delta-final-consolidation.json` — 2 amend+confirm, 3 re-add (dormancy recovery), 3 new add,
   1 retire, 2 resolve, 1 export.
9. `delta-export-from-child.json` — 1 export (queuing `from-child-refuses-on-gated-checklist`
   upstream, which step 2 had added but not yet exported).

All files live under `.agent-work/epic-601-lessons-audit/`. `.agent-work/LESSONS.md` was never
hand-edited — every mutation went through `apply_lessons_delta.py`.

## Engine Mechanics Worth Flagging (for the next audit, not a lesson candidate itself)

Applying 8 separate real-run deltas in one sitting, each with `tick: true`, advanced the
dormancy clock 7 times in quick succession (`run-tick` 25→32). Several lessons sitting at
`runs-since-confirmed: 9` (one tick from expiry) at the start of this audit — because they
hadn't been reconfirmed since 509-w3/509-w4/tire-age — expired via the engine's own dormancy
mechanism *before* a later-in-my-application-order staged trio's confirm could reach them
(non-constellation lessons are not pinned against dormancy the way constellation ones are).
Three of these had genuine epic-601 grounding and were recovered by re-adding fresh (losing
their prior confirm history/counters, though their substance and a pointer to that history is
preserved in the new grounding text); two had no epic-601 grounding and were left retired. This
is a real mechanical property of front-loading a graduation-retire pass before harvesting —
worth the next auditor front-loading confirms for near-dormant, epic-relevant lessons *before*
any batch of retires/ticks that might push them past the threshold, or applying all real-run
confirms in a single combined-ops delta (one tick) rather than N sequential single-trio deltas.

## Queued for Human Review

- The `engine-artifact-attest` discrepancy (07-17 curator claim vs. installed source) — needs a
  human/curator to re-verify which specific improvement actually shipped and correct either the
  curator note or the lesson's framing. Not self-resolved here (constellation doctrine is a
  human/Charter call).
- `admiral-close-after-merge-verified` — flagged as a graduation *candidate* for the *next*
  audit (10 clean merges this epic, zero violations) but not graduated now, since no existing
  doc currently states its exact Admiral-tier merge sequence verbatim (unlike the 7 lessons
  retired this audit, which had a verified pre-existing home). A human/Charter pass could choose
  to write it into a durable Admiral doctrine doc and then retire it.
- `init-work-area-root-nests-agent-work` — retired from the capped bank (single observation) but
  the underlying script defect is real and cheap to fix (`init_work_area.py --root` should refuse
  or normalize a path already ending in `.agent-work`); recorded in `CONSTELLATION_FEEDBACK.md`
  for whoever next touches that script.

## Addendum (2026-07-24, second pass): harvest-gap candidate + re-check of newly-merged content

team-lead found, after this audit's first pass closed, that all six fenced-commander trios
(624-phase0, 625-segmentation-substrate, wave4-626, 627-unified-basis, 638-f12-stability-rework,
630-phase6-bt-injection) had been staged under `.agent-work/staged-feedback/` but never actually
merged into the durable `.agent-work/AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md` — their source
worktrees were already swept, so staging was the sole surviving copy. team-lead fixed this by hand
(12 entries appended with provenance comments; `verify_agent_feedback.py --phase feedback` now
passes) and asked this audit to (1) confirm each staged trio's `lessons-delta.json` had actually
been applied, (2) re-read the newly-merged durable content for candidates or sibling sightings this
audit's first pass missed, and (3) route the harvest gap itself as a candidate.

**(1) Staged deltas — all six were already applied.** Diffed all six `staged-feedback/*/lessons-delta.json`
files against the `trimmed-*.json` copies and the dispositions recorded above — every op matches
(confirms/adds already reflected in the Applied Deltas list and Existing-Lesson Reconciliation
sections). Nothing needed re-applying.

**(2) Re-read of the newly-merged `AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md` tail** (all six
trios' full prose, not just their structured delta ops) turned up nothing that changes an existing
disposition and one minor finding not worth banking: two independent commanders (wave4-626 and,
per the durable log's pre-existing Ship I/#513 entry, ShipI-513) both hit "naming the dispatching
commander's own identity as a synchronous Agent-tool crew's SendMessage-result target is a
self-send no-op" — mechanical, self-corrected in both cases, and each commander's own "Improvement
signals" section already dispositions it as a template-wording fix ("drop the SendMessage
instruction for Agent-tool crews") rather than something needing re-observation. Noted here for
completeness; not banked as a LESSONS.md entry.

**(3) Harvest-gap candidate — routed.**
- **Scope:** `constellation` (shared Admiral-skill machinery, not project-specific — the doctrine
  itself states "platform doctrine, not project lore").
- **Task-class:** `general-workflow`
- **Observed:** `constellation-admiral/SKILL.md` Closeout step 4 already states, almost verbatim,
  the risk team-lead described — "harvest first, **then** remove — a worktree swept before its
  trio is collected silently drops that run's learning" — so the doctrine text was not the gap.
  What failed is enforcement: a fenced commander's own `feedback`/`archive` gate verifies only that
  its trio reached the **staging** copy (`verify_agent_feedback.py` against `staged-feedback/<id>/`),
  which looks identical to "harvested into the shared root" from the outside. Nothing checked the
  difference before the six worktrees were swept.
- **Cost:** six commanders' full retrospectives (friction, what-worked, improvement signals) were
  invisible to this audit's first pass and to every future one, until caught by a human re-check
  after closeout — exactly the failure mode the doctrine text warns about, now confirmed real
  rather than hypothetical.
- **Proposal:** a mechanical harvest-completeness check (extend `verify_agent_feedback.py` or add a
  sibling script) that, for every `staged-feedback/<work-id>/` directory still present at closeout,
  confirms its content actually landed in the durable files before permitting that work-id's
  `git worktree remove`.
- **Grounding:** `.agent-work/epic-601/ADMIRAL_LOG.md` Closeout section, INCIDENT + FIX entry dated
  2026-07-24; `constellation-admiral/SKILL.md` Closeout step 4; direct confirmation all six staged
  trios were absent from the durable log pre-fix.
- **Confidence:** high (mechanically confirmed, not assertion-only).
- **Routing:** `add lesson:harvest-collected-not-verified-merged` — **not** graduated directly to a
  permanent doc, because the doctrine already covers the intent almost verbatim but no enforcement
  mechanism exists yet for the lesson to graduate *to*. Applied via
  `.agent-work/epic-601-lessons-audit/delta-harvest-gap.json`. Full writeup (with the concrete
  verification-script proposal) added to `CONSTELLATION_FEEDBACK.md` for a human/curator to pick up
  the actual script work. Playbook after this add: 18/20 active, run-tick 33 (one lesson,
  `compact-step-skip`, aged out via the engine's own dormancy mechanism on this tick — expected:
  it was already marked `fixed-upstream` at this audit's first pass and fixed-upstream lessons are
  designed to age out rather than be tracked indefinitely).

## Workflow Feedback

- **Brief gaps:** the compiled `CLOSEOUT_RUN_BRIEF.md` was substantively complete (intent, all 6
  artifact paths verified present, candidate themes named) but did not follow
  `RUN_BRIEF.template.md`'s exact shape — no explicit "Project-Customized Templates" section
  (I had to independently check `.agent-work/templates/TEMPLATES_MANIFEST.json` myself) and no
  explicit model-tier table (model tiers were recoverable from ADMIRAL_LOG's per-wave prose, but
  a compiled table would have been faster to consume).
- **Artifact gaps:** two of the six staged `lessons-delta.json` files had authoring bugs that
  would have failed for their own sub-commander too: 638-f12-stability-rework used the key
  `task-class` instead of the schema's `task_class` on its `add` op; 638's and one other trio's
  deltas also referenced `editable-install-pth-worktree-trap`, a lesson that exists only in the
  user's personal `MEMORY.md`, never in the project's `LESSONS.md` bank — both would have hard-
  failed `apply_lessons_delta.py` (all-or-nothing) had the originating commander tried to apply
  its own delta rather than staging it for harvest.
- **What would have made this audit easier:** a run brief that pre-flags which staged deltas
  reference lessons likely to be graduated/retired in the same audit cycle, so the harvest order
  can be planned to avoid the dormancy-expiry race described above — front-loading confirms for
  near-dormant lessons before any retire-heavy delta, rather than discovering the race mid-run.
