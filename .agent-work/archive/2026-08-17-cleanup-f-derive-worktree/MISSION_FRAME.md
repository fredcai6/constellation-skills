# Mission Frame — lane F, #609 (absorbing #315)

**Map status: DEGRADED-UNPARSEABLE, discharged.** This repo carries no
`docs/architecture` packet map. `map/ids.jsonl` is 0 bytes and the per-module
`map/<module>/INDEX.md` files the top-level index links to are not checked in,
so no map anchor id exists to cite. This frame is therefore cut from the four
readings the orientation receipt hash-pinned, and cites them by path:

- `.agent-work/cleanup-f-derive-worktree/LAUNCH_ORDER.md` — the frozen design
  input: Mission, Prior-Wave Verdicts, Pre-Rulings, Inherited Latitude.
- `map/INDEX.md` — module-level orientation for the four modules in scope.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project rigor deltas.
- `docs/agents/GLOSSARY.md` — the one-name-for-one-thing baseline (`spine`,
  `gate`, `lease`, `latitude`, `projection`, `scoped null`).

Anchor ids are deliberately absent: in a degraded orientation every map anchor
token is unresolvable by construction, so citing one would be a same-breath
assertion rather than a reading. Named rulings below are written without the
anchor-token spelling for that reason; their governing text is the launch
order's Pre-Rulings section.

## Intent

A spine's worktree becomes a **derived** property of its path. Four outcomes,
not three — an earlier revision of this frame named only the first, second and
fourth, and the cold critic was right that riding the third along unnamed is how
a Stop-hook regression ships unnoticed:

1. **Derive** the worktree lexically from the spine path.
2. **Retire stamp-and-compare** — `origin.worktree` read for a decision, and the
   per-guarded-verb ambient `git rev-parse --show-toplevel` — so there is no
   second source of truth that can disagree with the first.
3. **The worktree stops answering "is this mine."** The Stop hook's
   worktree-as-ownership test is broken by construction once a crew shares its
   Commander's tree; binding-key provenance becomes the only discriminator.
   This is the run's riskiest behaviour change and carries its own gate and its
   own evidence surface.
4. **Thread the derived worktree into command-kind checks as their `cwd`**,
   which is the whole of #315.

**Derivation is lexical only — `normcase` + `normpath`, no `realpath`.** This
revises the launch order's `normalize-once` pre-ruling, which is graded
`settled/measured` and so may be revisited on a contradicting measurement. Three
measurements forced it: the purity test guarding the refusal predicate reads only
that predicate's own `co_names` and is not transitive, so a `realpath` in a
callee would make the predicate impure with the test still green; the hook's
`_is_valid_claim_target` deliberately keeps `resolve()` *outside* the derivation
as a symlink-escape guard, which moving `realpath` inside would make unfailable;
and importing `verify_worktree_isolation.normalize_path` into the engine trips an
exact-set-equality companion guard that would need an installer entry this lane
may not write. Symlink resolution stays outside the derivation on every side —
which is what the refusal predicate's own docstring already says today. New
provenance logged; the idiom is inlined in both copies, as
`scripts/agent_work_root.py:56` already does.

## Affected capabilities (from `map/INDEX.md`, module level)

- `scripts.checklist_engine` (110 entities) — *"Workbench checklist engine: work
  one gated/survey plan through its gates."* Holds the refusal predicate, the
  single impure cwd read, and the command-check runner. **Primary.**
- `scripts.hooks.spine_rail` (62 entities) — *"Claude Code hook suite for the
  Constellation spine rail."* Holds the existing lexical derivation and the
  worktree-as-ownership test. **Primary.**
- `scripts.spine_lifecycle` (20 entities) — *"...a compiled, origin-stamped
  spine."* Writes the stamp; keeps writing it as provenance. **Secondary.**
- `scripts.verify_worktree_isolation` (10 entities) — *"Verify git worktree
  isolation is real."* Owns the normalization definition being reused. **Read
  only; fenced.**

## Structural anchors (paths, verified in tree at `e36e630b`)

- `scripts/checklist_engine.py:102` — the refusal predicate, pure, equality
  since #588.
- `scripts/checklist_engine.py:3573` — the single impure call site: one
  `git rev-parse --show-toplevel` per guarded verb, before `dispatch()`.
- `scripts/checklist_engine.py:898` / `:927` / `:883` — `base_dir` in scope, not
  passed on, `subprocess.run` with no `cwd=`. This is #315.
- `scripts/hooks/spine_rail.py:712` — `_worktree_from_spine`, already lexical,
  too narrow (fixed one-level shape).
- `scripts/hooks/spine_rail.py:693` — the worktree-as-ownership test. The launch
  order cites `:639`; the actual line is `:693`. Drift, recorded.
- `scripts/hooks/spine_rail.py:1411`, `:1546` — its two call sites.
- `scripts/verify_worktree_isolation.py:47` — `normalize_path`, the
  realpath+normcase definition to reuse rather than mint a second one.

## Governing constraints and assumptions

- **Stdlib-only hook.** `scripts/hooks/spine_rail.py` imports stdlib and nothing
  else, deliberately — a hook that fails takes the turn with it. Verified: zero
  cross-module imports, and no `SCRIPT_RUNTIME_COMPANIONS` entry of its own in
  `scripts/install_constellation.py`. **Consequence: any placement of a shared
  definition outside `spine_rail.py` requires a new companion entry, i.e. an
  edit to lane A's file. The single-definition placement is therefore closed to
  this wave.**
- **Fenced files.** Lane A: `scripts/mcp_spine_server.py`, `.mcp.json`,
  `examples/**`, `scripts/install_constellation.py`,
  `skills/commander/templates/**`. Lane E: `scripts/run_crew.py`,
  `scripts/recover_crews.py`, `tests/test_crew_launcher.py`. Also fenced:
  `scripts/verify_worktree_isolation.py` (#610's).
- **Normalize once**, at the derivation boundary only, and **lexically** —
  `normcase` + `normpath`, **no `realpath`**. Never at call sites. This
  supersedes the launch order's original wording ("realpath plus normcase,
  reusing `verify_worktree_isolation.normalize_path`"), which was graded
  `settled/measured` and was revisited on three contradicting measurements — see
  Intent above for the three. The correct in-repo precedent for the inlined
  lexical idiom is `scripts/hooks/spine_rail.py:677` `_same_path`, **not**
  `scripts/agent_work_root.py:56`, which an earlier draft of this frame cited:
  that line uses `realpath`, the very call the measured constraint forbids. It
  is precedent for *inlining rather than importing*, and for nothing else.
- **Nearest, not outermost.** 27 tracked paths carry two `.agent-work`
  segments; the inner one belongs to a nested sandbox project. Outermost would
  derive the real repo as the root of a sandbox spine.
- **Fail closed.** No `.agent-work` ancestor at all means unowned — refuse the
  guarded verb rather than guessing a root.
- **Windows.** Path handling is exactly where Windows differs and CI is one
  red-at-baseline `windows-latest` job, so local Linux is the only real signal.
  Say what was done about separators and case regardless.
- From `docs/agents/ORCHESTRATOR_CONTEXT.md`: a mechanism or workflow behavior
  change needs targeted automated tests **plus** the relevant broader suite.

## Rulings already made (launch order Pre-Rulings — not this run's to remake)

- derivation-authoritative-stamp-becomes-provenance — derivation is
  authoritative immediately; `origin.worktree` keeps being written and is read
  by nothing for a decision; pin with a test.
  `@grade: settled/human · leans g2-implement`
- worktree-is-location-spine-path-is-identity — derived worktree is location
  (cwd for checks, where git runs), never ownership. Ownership is the lease;
  among spines sharing a tree the discriminator is binding-key provenance.
  `@grade: settled/human · leans g1-implement,g2-implement,g3-implement,g4-implement`
- nearest-ancestor-fail-closed — nearest `.agent-work` ancestor, take its
  parent, arbitrary depth; none means unowned.
  `@grade: settled/human · leans g1-implement`
- normalize-once — realpath + normcase at the derivation boundary only.
  `@grade: settled/measured · leans g1-implement`
- not-a-weaker-guard — removing the origin comparison removes no guard; the
  lease was always the guard. A genuine counter-case is a finding, not
  something to ship around.
  `@grade: settled/human · leans g2-implement`
- one-definition-or-a-pinned-equivalence — placement is this run's to decide
  under a hard constraint; duplication without an equivalence test is not
  acceptable.
  `@grade: guess · leans g1-implement · settle: try the single-definition placement first and report what it would require; float rather than editing the installer`

## Decision pressure this run forces

- **Where the derivation function lives.** Measured answer, from the constraint
  above: the single-definition placement cannot be taken without editing lane
  A's installer, so the ruling's second branch applies — the engine gets the
  definition, `spine_rail.py` keeps its own generalized copy, and a shared
  table of cases pins the two equal in a test. Reported as the settle-experiment
  result the ruling asked for, not as a fresh design choice.
- **What replaces the worktree-as-ownership test in the Stop hook.** Its two
  call sites differ: one decides mid-flight blocking, one picks a binding entry
  to resume from. Binding-key provenance is already computed at the first site.
  Surfaced as a decision candidate for reconcile.
- **The tripwire collision, and the false premise under it.** The launch order
  states that `verify_worktree_isolation` has zero occurrences in any template or
  spec, and concludes that threading `cwd` disarms nothing that ships. Measured
  against the tree, both halves are false: a live `command`-kind precondition in
  the project-local `COMMANDER_SPINE` overlay carries it, and the shipped Admiral
  launch-order template both instructs it and rules that forcing `cwd` disarms it
  and that it is "distinct from, not superseded by, the engine-native guard."
  Separately, `IsolationGateSurvivesThroughTheCLI` goes red by construction, and
  its own docstring names a third road the order does not mention and orders it
  first: land an explicit contract for a check that observes its environment,
  *then* teach the fixture. **Floated to the Admiral** — the launch order
  reserves this there twice, and the premise failure is not this lane's to rule
  on.
- **The fail-closed blast radius.** Refusing a guarded verb on a spine path with
  no `.agent-work` ancestor refuses 362 of the 429 guarded-verb invocations the
  current suite makes, across 125 tests — three of which sit in a file fenced to
  lane E. The gate would have to break three tests it may not fix while its own
  postcondition demands a green suite. **Floated to the Admiral**; the ruling is
  graded `settled/human`, so narrowing it is not this lane's call, and the
  obvious narrowing (fail closed only for a stamp-carrying spine) is closed
  anyway because it reinstates reading the stamp for a decision.

## Evidence surfaces each gate must re-confirm

- Derivation: a table of paths and the worktree each derives — a spine at the
  root, a spine in a worktree, a crew area nested under a Commander's, the deep
  archived case, the nested-sandbox double-segment case, and a path with no
  `.agent-work` ancestor at all.
- Retirement: the guarded-verb path exercised before and after, the ambient git
  call gone, and an enumeration by command — with the count stated — of every
  remaining read of the stamp.
- Ownership-not-tree: the #549 shape exercised directly, with a Commander and an
  in-tree implementer sharing one worktree, where the parent's Stop must not be
  answered with its crew's gate; before/after stated per call site; and what
  newly blocks enumerated, since removing a skip makes the Stop hook block more.
- #315: red-before / green-after for both the fail-open decoy case and the
  false-red case.
- Every gate: one cheap **targeted** check that goes red on an empty diff — the
  suite alone is a regression floor, not a close criterion, and a plan whose only
  check is a suite that is already green cannot fail on a gate that did nothing.
  Then the full clean-env, cache-cleared suite, plus a `main` baseline
  **re-measured at gate time** with the failure-set difference stated, plus an
  explicit statement of what the gate did about Windows separators and case
  folding.

## Map confidence, staleness, disputes

- **No packet map exists.** Recorded as unmapped in the receipt and carried to
  triage as a map hole. It alters this plan concretely: no gate may assume a
  map fact, and every structural claim above is pinned to a line read in tree at
  `e36e630b` instead.
- **`map/INDEX.md` is generated and freshness-tested**, and conflicts on every
  parallel branch (#544). If entities change, regenerate — never hand-merge.
- **One order-vs-tree drift found and recorded** (`spine_rail.py:639` vs `:693`),
  which is why no gate is anchored to a line number the order supplied without
  re-reading it.

## Out of scope

`scripts/run_crew.py`'s own worktree computation (lane E first, then a separate
wave); retiring `--here` as a launch-order step and its gate mode (#610);
`scripts/verify_worktree_isolation.py` itself; any installer or template edit;
publication and merge.
