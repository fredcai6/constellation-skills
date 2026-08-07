# Mission frame — issue #299

## Intent

Capture the pre-change arm of the epic-298 map-first measurement: five plan-stage runs
against f1Brainz at pin `3541d292`, with a falsifiable grading rubric frozen and committed
before any run executes.

**Frame deliberately SHRUNK, and here is why.** `constellation-skills` has no
`docs/architecture/` packet map — verified: the directory does not exist in this repo. So
there is no map to frame this plan against, and commander doctrine's own reconcile clause
already names this repo's shape ("a skill-source repo with no `docs/architecture` map") as
the sanctioned degraded case. The architecture artifacts that *do* matter to this run belong
to **f1Brainz**, and they are the **object of measurement**, not context for my plan —
reading them to plan with would be a category error.

## Affected capabilities

- New: mechanically extract an orientation-ordering measure from a headless run's
  `stream-json` transcript (`extract_ordering.py`).
- New: launch a measured subject at a pinned commit with a frozen brief and a fingerprinted
  corpus (`capture_baseline.py`), reusing `run_skill_eval.launch_agent` rather than
  reinventing the Windows process-tree/drain/heartbeat machinery.
- Unchanged: no production skill, template, or script behaviour is touched. This run adds
  measurement apparatus and data under `.agent-work/epic-298/baselines/` only.

## Structural anchors

- `.agent-work/epic-298/baselines/` — archive + harness home (`decision:baseline-artifacts-live-here`).
- `scripts/run_skill_eval.py` — the existing, battle-tested launcher seam. Imported, not copied.
- `skills/` at base `c2e16a87` — the PRE-#304 corpus under measurement, fingerprinted with
  `stable_corpus_id` so #307 can prove the post arm differs only by #304.

## Governing constraints and assumptions

- Measured runs stop at plan; nothing is implemented, committed, pushed, or merged in f1Brainz.
- No `gh` write against `fredcai6/f1Brainz`. Read-only.
- Every run at pin `3541d292`; one fresh worktree per run.
- The subject must not know it is measured.
- The rubric freezes before any run — proven by commit order, not asserted.

## Decision anchors

- `decision:corpus-is-f1brainz` `@grade: settled/human`
- `decision:baseline-task-set` `@grade: settled/human`
- `decision:plan-stage-only` `@grade: settled/human`
- `decision:rubric-frozen-before-runs` `@grade: settled/human · settle: none`
- `decision:baseline-artifacts-live-here` `@grade: settled/human`
- `decision:baseline-is-informal-map-not-no-map` `@grade: settled/human` — **reality
  contradiction found.** Its "no canonical entrypoint" half is false: f1Brainz's auto-loaded
  `CLAUDE.md:7` already names `docs/architecture/index.md`. Per decision-fixedness doctrine,
  `settled/human` means STOP and float — floated to the Admiral as F1, **not** overridden here.
- `decision:measured-subject-is-a-commander` — the subject runs with the pre-#304 corpus
  installed rather than bare, because #304 lands its contract *in* commander doctrine and a
  bare-agent baseline could not be paired with the post arm.
  `@grade: settled/inherited · leans g1-capture` (instrumentation, delegated to me by the order)

## Decision pressure

- Whether briefs carry issue bodies (realistic, but 3 of 5 bodies give the path away) or
  titles only (preserves the order's grain reasoning, but fabricates the brief). Resolved to
  bodies + honest power declaration; floated as F3.
- Replication k. Resolved to k=1 now with the limitation declared; floated as F2.

## Claims / evidence surfaces

- `claim:capturable` — `claude -p --output-format stream-json --verbose` emits ordered
  `tool_use` blocks with target paths. **Probed, exit 0, 6 calls, both trees distinguishable.**
- `claim:floor-real` — the extractor's self-test can fail. **Verified by two deliberate
  mutations** (literal collapse kills 1 check; `command`-only extraction kills 9).

## Map confidence / staleness / disputes

- f1Brainz's map is 5 days stale against a live repo (last reconciled 2026-07-27 at base
  `5f802731`; pin is 2026-08-01). That staleness is **part of what is being measured**, not a
  defect to correct.
- The corpus-size claim in the launch order (5,928) was stale; actual is 6,435. Corrected.

## Out of scope

Re-cutting the task set, re-surveying corpora, re-deciding the pin, the post-#304 arm, the
pairing, and the pathway verdict.

---

## Design-it-twice — panel-vs-single, and the untaken roads

**Choice surfaced: SINGLE candidate + mandatory cold critic, not a panel.** The design space
here was narrowed to near-zero by the launch order's own pre-rulings — corpus, task set, pin,
plan-stage-only, and archive location are all `settled/human`. What remained free was
instrumentation, and its load-bearing fork (bare agent vs corpus-installed Commander) has a
forcing argument rather than a trade-off: #304 lands in commander doctrine, so a bare-agent
baseline is unpairable with the post arm. Generating parallel candidates over an already-forced
choice would have produced a menu, not a comparison.

The **cold critic was run and was not optional** — `lesson:cold-critic-mandatory-for-measurement-dependent-plans`
makes it mandatory for any plan whose acceptance is a before/after measurement, which this is.
It returned findings that changed the instrument materially and is recorded at
`.agent-work/299/PLAN_CRITIC_DISPOSITION.md`.

**Untaken road 1 — bare-agent baseline (no corpus).** Cleaner "no map" control, but
unpairable with the post arm, and the launch order forbids the "no map" framing outright.
Rejected on validity.

**Untaken road 2 — title-only briefs.** Would have preserved the order's per-task grain
reasoning and restored full seam power on 3 tasks. Rejected because no real Commander is
dispatched on a title alone; it would manufacture the result. Floated to the Admiral instead
(F3), with the power loss declared in the rubric rather than engineered away.

**Untaken road 3 — full Commander spine per measured run, driven to archive.** Highest
fidelity, but the ordering measure is decided in the first handful of tool calls while the
spine's expensive tail (design-it-twice, cold critic, execute.json) contributes nothing to it.
Rejected on cost for no measurement gain.
