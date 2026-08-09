# Mission Frame — issue #447, finish #308's retirement

**Map status: DEGRADED-NO-MAP.** This repo carries no `docs/architecture/` packet map (receipt:
`.agent-work/epic418-h-447/map-orientation.json`). The frame is therefore cut from the five
hash-pinned substitutes declared at the context step, and every structural anchor below names one of
them. The frame is NOT skipped — the change is doctrine surgery across ~200 shipped sites, the
opposite of trivial.

## Intent

Make the retirement promised by #308 actually true, and keep it true. Both `.agent-work/LESSONS.md`
and `.agent-work/AGENT_FEEDBACK.md` leave the shipped surface entirely — writer, verifiers, skill,
templates, tests, install bundles, pointers — and the learning loop's write path lands on the episode
store as a **record of what happened**, never as a playbook that gets read back as instruction.

## Affected Capabilities

- `capability:run-closeout-learning` — today the Commander/Admiral `feedback` step appends a prose
  retrospective to `AGENT_FEEDBACK.md` and distils a structured delta into `LESSONS.md`, gated by
  `verify_agent_feedback.py` + `verify_lessons_applied.py`. After this run it records episodes through
  `apply_episode_delta.py`, gated by capture.
- `capability:episode-store` — `episodes/{active,retired}`, written only by `apply_episode_delta.py`,
  read by `query_episodes.py`. Currently installs with NO role and is referenced by NO skill.
- `capability:upstream-export` — `CONSTELLATION_FEEDBACK.md` + `collect_feedback.py`. NOT retired;
  touched only where its `Lesson:` identity field dangles on the retired playbook.
- `capability:fenced-worktree-closeout` — `stage_feedback.py` + `verify_agent_feedback.py`'s staged-trio
  branch. Exists only because `.agent-work/` is gitignored. Dissolves with the retirement.

## Examples / Events

- `example:episodes/active/issue-308-001.md` — the migration precedent. A lesson became an episode
  whose prescription was recorded as a `workaround` **observation**, not a rule. This is the exact
  shape the six surviving lessons must take.
- `event:feedback-step-advance` — the engine runs the `feedback` postcondition commands on `advance`.
  Whatever command replaces them must exist on disk in the installed bundle or every future run wedges.

## Structural Anchors

- `struct:docs/EPISODE_STORE.md` — the store's grammar, partition, retirement policy. Doc level.
- `struct:episodes/README.md` — the store's own statement that it is "a raw, append-mostly,
  machine-consumed capture", explicitly "Not to be confused with" the playbook. Directory doctrine.
- `struct:docs/RECURSIVE_IMPROVEMENT_DESIGN.md` — the design record for the loop being replaced;
  carries the largest concentration of retiring-file references (20 sites). Doc level.
- `struct:docs/CONSTELLATION_OVERVIEW.md` — the artifact taxonomy table that routes each artifact to
  its consumer; line 98 already rules the playbook out of the taxonomy. Doc level.
- `struct:README.md` — the shipped repo entrypoint; documents `AGENT_FEEDBACK.md` as the unified run
  retrospective at lines 233 and 254. Doc level.

## Governing Constraints / Assumptions

- `constraint:episodes-are-not-prescriptions` — Tommy, 2026-08-06: *"we shouldn't be reading the
  episodes like lessons, it's a store for things that happened to replace both feedback and lessons."*
  Violated the moment any shipped surface tells an agent to read episodes and condition behaviour on
  them. **This is the constraint the whole run exists to honour.**
- `constraint:doctrine-lives-in-docs-agents` — a rule to follow belongs in `docs/agents/*`, never in
  the store.
- `constraint:record-stores-never-hand-edited` (`docs/agents/CREW_CONTEXT.md`) — episodes are written
  only through `apply_episode_delta.py`. Migration must go through the writer, not through `Write`.
- `constraint:edit-canonical-shared-doctrine` — edit `skills/_shared/global-*.md`, never
  `skills/<role>/references/global-*.md` (install-time copies, silently regenerated).
- ~~`assumption:installed-copy-indirection`~~ — **FALSIFIED by the cold panel, 2026-08-06, and
  re-verified false at source.** I had claimed my spine runs the installed scripts against the MAIN
  CHECKOUT durable root. It does not: `scripts/agent_work_root.py:136-140` redirects `durable_root()`
  to the **fallback — this worktree** whenever an active Admiral epic lease exists, and epic #418 holds
  one. Running the real gate returns exit 1 pointing at *this worktree's*
  `.agent-work/AGENT_FEEDBACK.md`. The stranding trap the launch order named is **real**, not measured
  away. Replaced by `decision:untrack-do-not-delete` (see CRITIC_TRIAGE.md T1): g4 uses
  `git rm --cached`, so the path leaves the index — which is what "shipped" means and what the guard
  checks — while the on-disk copy survives this run's own closeout and dies with the worktree.
  `@grade: settled/measured`
- `constraint:no-fable` — every dispatch capped at Opus, model named explicitly.

## Decision Anchors & Decision Pressure

- `decision:guard-is-not-optional` — a shipped guard keeping the retirement true is part of the
  deliverable, not a nice-to-have.
  `@grade: settled/human · leans g4 · settle: n/a — ruled by Tommy via the launch order`
- `decision:episodes-replace-both` — one store of observations replaces two inboxes plus a playbook;
  no successor playbook is created.
  `@grade: settled/human · leans g2,g3`
- `decision:retire-the-lessons-auditor-role` — `skills/lessons-auditor/` exists to distil
  prescriptions from runs. Under `constraint:episodes-are-not-prescriptions` that job IS the retired
  thing, so the role retires with it rather than being repointed at `episodes/`. Repointing it is the
  named failure mode of this mission.
  `@grade: settled/structural · leans g2 · settle: falsified if any consumer needs a distilled
  prescription that docs/agents/* cannot hold`
- `decision:fencing-mechanism-dissolves` — `stage_feedback.py` and the staged-trio branch exist only
  because `.agent-work/` is gitignored; `episodes/` is tracked, so a fenced commander commits to its
  own branch and the mechanism has no remaining job.
  `@grade: settled/structural · leans g2 · settle: falsified if any fenced-run scenario still cannot
  record an episode`
- `decision:capture-gate-checks-capture-only` — the replacement gate asserts that this run RECORDED
  what happened; it must NOT assert that anything was read, applied, or paid. Ripeness, apply-or-defer
  and dormancy are playbook concepts and retire with the playbook.
  `@grade: settled/structural · leans g3`
- **Decision pressure (surfaced, not decided):** `AGENT_FEEDBACK.md` carries 2056 lines of prose
  retrospectives. Migrating them would mean synthesising structured assertions from unstructured prose
  — fabrication the store's own doctrine forbids. Candidate disposition: drop-with-reason, git history
  retains it. Surfaced to the Admiral in RETURN.md.
- **Decision pressure:** `CONSTELLATION_FEEDBACK.md`'s `Lesson:` field dangles once lesson ids stop
  existing. Candidate: accept an episode id there instead. Minimal, in-scope, one field.

## Claims / Evidence Surfaces

- `claim:no-shipped-reader` — no shipped surface instructs an agent to read either retired file.
  Checked by the guard's forbidden-name sweep over `skills/ scripts/ tests/ docs/agents/` + entrypoint docs.
- `claim:no-shipped-writer` — `apply_lessons_delta.py`, `verify_lessons_applied.py`,
  `verify_agent_feedback.py`, `stage_feedback.py` are gone from the tree and from every install bundle.
  Checked by the guard + `test_install_constellation.py`.
- `claim:episodes-not-prescriptive` — no shipped surface tells an agent to read episodes as guidance.
  Checked by the guard's forbidden-phrase sweep over `skills/**`.
- `claim:guard-fails-on-purpose` — the guard is run against a deliberately-wrong decoy and observed to
  FAIL before it is observed to pass. **Required evidence, not optional** — this run's own playbook
  carries `lesson:falsify-a-check-against-a-decoy-before-trusting-it`, twice-observed, and shipping an
  unfalsified guard here would be the third instance in the very run that retires the lesson.
- `claim:suite-not-regressed` — `python -m pytest -q` strictly better than the 1688 passed / 2 skipped
  baseline, net of tests deleted with their subjects (the deletion lowers the count legitimately, so
  the claim is stated as "no failures", with the delta explained by name).

## Map Confidence / Staleness / Disputes

- **No packet map exists.** Plan alteration already taken: the blast radius was enumerated BY COMMAND
  (`git grep -n` over the shipped surface, counts recorded) rather than read off a map, and that
  enumeration is the plan's scope-of-record. This directly applies
  `lesson:enumerate-the-sites-by-command-before-editing-a-claim`.
- `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` is a **stale design record** describing the loop as built,
  not as it will be. It is history, not doctrine — it gets a superseding header, not a rewrite.
  Distinguishing "doc that instructs" from "doc that records" is a live judgement in this run and is
  called out in the gate that touches docs.

## Out of Scope

- Episode-store hardening (cluster K3: #399, #342, #360, #361, #379, #405) — pre-ruling
  `decision:store-hardening-out-of-scope`.
- `collect_feedback.py`'s upstream sweep beyond the single dangling identity field.
- Re-running `install_constellation.py` to propagate to `~/.claude/skills/` — a user-machine action.
- Issue #285 — pre-ruling `decision:285-premise-is-false`; the Admiral's to handle.
- Automated episode capture wiring (#305) — the store's own doc rules it deliberately agent-initiated.
