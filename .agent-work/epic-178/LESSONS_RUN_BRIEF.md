# Lessons-Audit Run Brief — epic-178 (Context Governor v1)

## Epic intent
Ship the Context Governor v1 per a CONFIRMED DESIGN_SPEC: a proactive, portable way for constellation agents to hand off cleanly at a good work seam before context death, as a byproduct of continuous why-logging. Four modules: Why-capture (engine schema), Gauge (writer+reader), Trip (two-band gate policy), Refresh (reach-up flow). Posture: experimental-v1, ship minimal, cull from use.

## Outcome
All 5 issues merged green (final main e4e56a3, 828 passed): #179 engine why-capture+refresh primitives, #181 gauge reader, #180 gauge writer, #182 Trip, #183 refresh doctrine. Run driven entirely through the engine (self-maintenance/dogfood run on the constellation-skills repo itself; the new engine even dogfed onto this Admiral's own remaining advances).

## Model tiers used
- Opus: impl-179 + rev-179 (engine surgery); impl-182 + rev-182 (Trip engine policy).
- Sonnet: impl-181/180/183 + rev-181/180/183; drill-fresh.

## Dispatch shape (a ruling worth auditing)
Right-sized to implementer-with-plan + independent clean-room reviewer per issue (NOT full Commander spines) because the DESIGN_SPEC already froze all design-it-twice work — remaining work was implementation + verification. Flatter hierarchy (Admiral → {implementer, reviewer}), more robust on this harness.

## Candidate signals observed this run (for your fresh-context distillation — do not treat as pre-judged; find others)
1. **Delayed subagent notifications (~40 min late).** Completion/idle notifications for all subagents arrived in one batch ~40 min after the work was actually done; the Admiral had already processed everything by ACTIVE in-turn polling of result artifacts. CONFIRMS existing platform doctrine (fleet-doctrine.md "idle sessions do not receive notifications"). Likely a confirm, not a new add.
2. **`gh pr create` / `git log` transient "Blocked by classifier".** Two implementers (#180, #182) hit a transient permission-classifier denial on `gh`/`git` read/create; identical retry succeeded immediately. Recurring across dispatches.
3. **Test-harness concurrency fail-safe (impl-180).** A TF9 concurrency test hung pytest forever: a writer thread died on a transient Windows os.replace sharing violation before setting its stop flag; the non-daemon reader spun forever. Fix: try/except + daemon threads. Lesson: test-harness threads doing real concurrent file I/O need the same fail-safe discipline as the production code they test.
4. **Launch-order doctrine-home path nit (impl-183).** The Admiral's #183 launch order cited global doctrine as `skills/<role>/references/global-*.md`; the canonical SOURCE is `skills/_shared/global-*.md` (copied into each skill's references/ at install by install_constellation.py). Future launch orders citing doctrine homes should cite the _shared source.
5. **Cross-issue integration awareness (positive).** impl-182 (Trip) checked #180's ACTUAL merged writer path rather than blindly keying off cl["work_id"], pairing reader↔writer correctly. Reinforces "verify claimed side-effects / paired interfaces against the real merged code."
6. **Engine mid-run edit hazard, handled (dogfood).** #179 rewrote checklist_engine.py — the engine driving this very spine. Handled by: implement/review in isolated worktree → verify new engine drives the live spine (read + mutating-advance on a copy) BEFORE merge → sync checkout → drive remaining advances on the new engine with --why. Worth capturing as a dogfood-run pattern if not already doctrine.
7. **A bare `git update-ref` to advance local main left a staged-deletion skew** (gauge_reader.py showed as deleted because working tree wasn't updated) that could have silently reverted a merged PR at closeout commit. Fixed via `git restore` (classifier vetoed `git reset --hard`). Lesson: sync the working tree, not just the ref, when advancing local main mid-run.

## Artifacts to read (all under .agent-work/epic-178/)
- ADMIRAL_LOG.md (the run's audit trail — primary input)
- crew-handoffs/{179,180,181,182,183}-result.md (impl results incl. rework sections)
- crew-handoffs/{179,180,181,182,183}-review.md (independent reviews)
- crew-handoffs/drill-fresh-result.md (HITL drill evidence)
- LATITUDE_CONTRACT.md

## Also note
- LESSONS.md Active section was EMPTY at run start — no ripe inbox lessons to pay.
- Cross-project feedback sweep (collect_feedback.py over f1Brainz/network_elo/story_time) run at closeout: "No new or open candidates."
- Two engine-gap fast-follows already filed as GitHub issues: #189 (DIGEST/REFRESH gated-only, survey roles blind), #190 (has_pending_refresh_request why_ref-blind). Do NOT re-file these; they're dispositioned.
- Open triage still to route by the Admiral: tc1 (advance --from-child double-attach non-idempotency, rev-179 LOW), tc2 (docs/CHECKLIST_SCHEMA.md needs why_trail/why_exempt/refresh-request/DIGEST+REFRESH documented).
