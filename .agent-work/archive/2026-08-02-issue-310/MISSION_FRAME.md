# Mission Frame — issue #310, B2 gate evaluation

**Map status: DEGRADED-NO-MAP.** This repo has no `docs/architecture/` map — all three candidates absent,
recorded at `.agent-work/issue-310/map-orientation.json` before any source file was opened. The frame is
therefore built over the four **hash-pinned substitutes** the receipt committed:
`README.md`, `docs/CONSTELLATION_OVERVIEW.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, `SKILL_INDEX.md`.
Every anchor below cites one of those four. Nothing here is read off a map, because there is none.

## Intent

Assemble the B2 evidence gates so **Tommy can make the kernel-break call**, and so that whichever of the
three outcomes the evidence selects is **attributable** — i.e. the document says which outcome, and on
what number, at what revision. This run **does not** take the break, does not author a fragment
decomposition, and does not rule.

The measured object is the **corpus itself**. That makes this repo's own skill tree the "code" under
study, and `SKILL_INDEX.md` + `README.md` the closest thing to a structural inventory it has.

## Affected Capabilities

- **`README.md` §"Skill set" — the role corpus.** Declares the corpus is **19 skills** and that
  `skills/_shared/` is not one. This is the enumeration the trend measurement must loop over, and the
  count it must assert against. This run **reads** it; it changes nothing.
- **`README.md` §"Repo layout vs. installed layout" — the two shapes.** Repo shape is `skills/<name>/`
  with shared scripts at root; installed shape bundles `SKILL.md` + `scripts/` + `references/` +
  `templates/` into `constellation-<name>/`. **This is load-bearing for the measurement:** the always-loaded
  vs conditionally-loaded split is a claim about the *installed* shape, measured on the *repo* shape.
- **`docs/CONSTELLATION_OVERVIEW.md` §"Context separation" — the layered read.** "each agent reads its
  inherited *global* doctrine (bundled with the skill at `references/global-{everyone,<tier>}.md`) first,
  then the project's thin *local* deltas — layered, never merged." This is the corpus's own statement of
  what a role loads, and it is the nearest thing to an always-loaded contract in the tree.
- **`docs/CONSTELLATION_OVERVIEW.md` §"Relationship Contract" — Skill.md is trigger, boundary, and
  resource pointer; Templates are the interface; References hold doctrine/detail.** This sentence is the
  corpus's own three-bin model, and it is *already* kernel-shaped. It matters to the verdict.

## Examples / Events

- **The `1e8043a` (#107) mode split** — the one prior role decomposition actually executed. Verified
  against the tree: `skills/commander/SKILL.md` 107 lines → stub, `commander-core.md` +121,
  `commander-delegated/SKILL.md` +18, 8 files. It is the **mode** axis, not B2's **content** axis.
- **The `refresh` / job-file-not-agent-file relaunch** (`global-orchestrator.md` §idle-subagent
  adjudication; `global-everyone.md` §reach-up) — a *fresh* agent cold-started from `current` alone,
  mid-spine, no handoff document. **This is Assumption 1 running in production** and it is the only
  role-competence signal available without building the break.
- **#307's PRE-B/POST arm** (`.agent-work/epic-298/preb/`, `.agent-work/epic-298/post/`) — the instruments
  and the method this run must reuse rather than rebuild.

## Structural Anchors

- `README.md` — corpus inventory, the 19-skill count, repo-vs-installed shape. Root level.
- `SKILL_INDEX.md` — per-skill index; the enumeration cross-check against `skills/*/`.
- `docs/CONSTELLATION_OVERVIEW.md` — role graph, relationship contract, context-separation model.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project deltas; **Repo Action Authority** ("Pushes, pull requests,
  and merges to `main`: require explicit human approval") which is why this run opens a PR and hands the
  merge up rather than merging.

## Governing Constraints / Assumptions

- **`assumption: run artifacts carry sufficient state`** (spec Assumption 1, spec line 126) — *"Untested;
  gated — the B2 role-competence test must exercise it before the break proceeds."* This run **cannot**
  discharge it experimentally; it can only report observational evidence and say so.
- **`constraint: always-loaded ≠ installed`** (#393) — a role's always-loaded surface is `SKILL.md` plus
  the `references/` it names; templates and scripts load conditionally, on materialization. Violating this
  overstates always-loaded surface by everything a spine template carries. **Both bins measured separately.**
- **`constraint: no threshold exists`** (spec critic S2) — *"no threshold at which the current shape stops
  working."* Gate (a) asks whether deletion is getting the surface "small enough" and the spec never says
  what that is. **This constraint is what makes the gate unadjudicable by an agent alone.**
- **`constraint: ORCHESTRATOR_CONTEXT Repo Action Authority`** — no merge without explicit human approval.
- **`constraint: rule 9 of the launch order`** — an agent does not get to rule that a finding earned its
  place. Applies directly to the kernel break.

## Decision Anchors & Decision Pressure

**No map exists, so this run records no map-node decision anchors** — `verify-frame` correctly refuses
`decision:<id>` citations under `DEGRADED-NO-MAP`, because there is no inventory for them to be a member
of. The three governing choices are therefore stated as **run-local decisions**, each grounded in a named
hash-pinned substitute or a named prior issue rather than in a map node. They are candidates for the
`reconcile` step to promote into a durable record, not anchors this run inherits.

1. **Always-loaded = `SKILL.md` + the `references/` it names.** The operational bin definition this run
   measures against. Grounded in `docs/CONSTELLATION_OVERVIEW.md` §"Context separation" (the layered
   global-then-local read) and in #393's empirical finding; nothing in the tree declares it.
   `@grade: guess/empirical · leans g1-trends · settle: report both bins separately so a reader who rejects the convention can recombine the numbers arithmetically, without a re-run`
2. **Bytes primary, lines secondary.** Grounded in the confirmed spec's own naming of line endings as an
   irreproducibility source (spec line 140) and in this repo being developed on Windows.
   `@grade: settled/measured · leans g1-trends · settle: line counts hide CRLF and long-line changes; both are reported so neither is load-bearing alone`
3. **Gate (b) is not run in this run, and has n = 0.** *Originally written as "a controlled arm is
   impossible because building the decomposition IS the break", graded `settled/structural`. **That claim
   is WITHDRAWN and the grade was wrong.*** A cold plan critic named a cheaper honest arm: an **ablation**
   — run one mid-spine step with sections of today's monolith *withheld* vs full — which varies the
   treatment and requires **zero authoring**. So the arm is declined for **runway**, not impossibility.
   Separately: this epic's refresh/cold-start relaunches are **not** gate-(b) evidence, because every one
   held the full monolith — **the treatment was never varied**, so gate (b) is n = 0, not weak-n.
   `@grade: guess/structural · leans g2-competence · settle: run the ablation arm; regraded from settled after a cold critic showed the impossibility claim was contested, which is exactly the laundering a grade exists to prevent`

**Decision pressure (no grade — a choice this run forces, not an anchor it inherits):**

- **The threshold for "small enough" does not exist and must be chosen by Tommy.** This run will state
  what threshold would select each of the three outcomes, and will not pick one. Already escalated to the
  Admiral at the `understand` step rather than held to review.
- **Whether the corpus's existing three-bin shape (`SKILL.md` = trigger/pointer, `references/` = doctrine,
  `templates/` = interface) already *is* a kernel-plus-fragments architecture under a different name.**
  If it is, B2's content axis is substantially further along than "unstarted", and the question becomes
  a naming/selector question rather than a re-architecture. This is a durable-structure choice; surfaced,
  not decided.

## Claims / Evidence Surfaces

- `claim: skills/commander/SKILL.md is 16 lines with 0 occurrences of "map"` — **re-verified this run** at
  both `cfa2c40` and `dbd5414`. Holds at both.
- `claim: the #304 map contract lives only in per-task spine imperatives` — **re-verified**: 26 map
  mentions across the spine template's 10 imperatives at `cfa2c40`, 0 in `SKILL.md`. Map counts match the
  order exactly (context 9, plan 11); char counts differ by ≈0.5%, explained as JSON-escaped vs decoded.
- `claim: deletion pressure is or is not shrinking the always-loaded role surface` — **the gate's own
  question, unmeasured until this run.** Evidence surface: `git log` over `skills/*/SKILL.md` and
  `skills/*/references/` at named revisions.
- `claim: run artifacts carry sufficient state (Assumption 1)` — evidence surface: the epic's record of
  refresh-relaunched and cold-started commanders. **Observational; no monolith control arm exists.**

## Map Confidence / Staleness / Disputes

- **Whole map: ABSENT.** Not stale, not low-confidence — *nonexistent*. Discharged as `DEGRADED-NO-MAP`
  with substitutes, unmapped statement, and escalation, at the context step, before any source read.
  **How it alters the plan:** every gate below carries an explicit *assert-the-enumeration* close
  criterion, because there is no map inventory to check a loop against. Rule 3 of the launch order
  (under-inclusive enumeration has bitten this epic five times) is mechanised into the gate plan rather
  than trusted to care.
- **`README.md`'s "19 skills" is an unverified count** — it is prose in a substitute, not a map node.
  **How it alters the plan:** gate 1 verifies it against `ls skills/*/` and reports any mismatch as a
  finding, rather than adopting it.
- **The always-loaded bin definition is a convention, not a recorded fact.** No artifact in the tree
  declares which files a role auto-loads. **How it alters the plan:** both bins are reported separately
  and the arithmetic to recombine them is given, so the verdict survives a reader rejecting the convention.

## Out of Scope

- Authoring any kernel/fragment decomposition, projection generator, or fragment selector.
- Editing any role's `SKILL.md`, `references/`, or `templates/`.
- Choosing the "small enough" threshold.
- Making the kernel-break decision.
- Merging (`ORCHESTRATOR_CONTEXT` Repo Action Authority; launch-order stop condition; `gh pr merge` is
  additionally vetoed by the harness permission classifier, #408).
