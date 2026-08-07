# Agent Feedback Log (staged — see FENCE.md)

This is a STAGED entry, not the durable log. The durable `AGENT_FEEDBACK.md` lives at the main checkout's
`.agent-work/` root; this run staged its entry here instead per the fencing workaround (see `FENCE.md`).
The Admiral harvests this entry into the shared durable log at closeout.

---

## `2026-07-19` — `117-curate`

**Run shape:** `commander (delegated)` · `10/10 spine steps run (init through archive), 2/2 execute.json crew
gates closed (g1, g2)` · `subagent model tier: sonnet throughout (Commander, cold critic, both implementer
crews, both reviewer crews)`

**Instruction adherence:** `fully followed`
- Drove the full spine through the engine (`claim`/`current`/`start`/`attest`/`attach`/`advance` at every
  step), never hand-edited `spine.json` or `execute.json` mid-run. Dispatched implementer/reviewer crews via
  `run_crew.py --dispatch external` (record-only, since this harness has no headless `claude` CLI) followed
  by a synchronous Agent-tool dispatch and independent re-verification of every claimed side-effect (git
  diff, direct interpreter probes, full suite re-runs) before integrating — never accepted a crew's claim on
  its word alone.

**Friction / unclear:**
- **Real, corroborated engine-mechanics gap** (see lesson `command-postcondition-cannot-attest` below): a
  `command`-kind postcondition is REFUSED by `attest` ("engine-checked; cannot attest"); the correct
  sequence is to run the check yourself for your own confidence, then call `advance` directly with `--why`
  — the engine evaluates the command check internally during that single `advance` call. This was hit
  independently by the g1-implementer crew, described explicitly in its Workflow Feedback, AND by me
  (Commander) at both `g1-integrate` and `g2-integrate` — I initially tried to `attest` the command-kind
  `c1` postcondition at each integrate gate and only the artifact-kind `c2` (review-result) accepted an
  `attest --evidence` reference; `c1` (the test-suite command check) was satisfied purely by the subsequent
  `advance` call itself. The spine/plan template imperative phrasing ("Run the step's checks, then `attest`
  and `advance`") reads as if every postcondition needs an explicit attest/attach first; for `command`-kind
  conditions specifically, `advance` IS the check-runner.
- Minor, not lesson-worthy: `docs/agents/` does not exist in this repo (it's the constellation-skills
  source repo, not a project consuming Constellation) — every role (Commander, both implementer crews, both
  reviewer crews) independently and immediately recognized this as sanctioned graceful degradation with no
  wasted search. Worth a passing note only because it recurred identically across 5 separate agent contexts
  in one run.
- `tests/test_install_constellation.py`'s `test_bundled_scripts_carry_their_sibling_imports` regression test
  (and the `SKILL_SCRIPT_BUNDLES` manifest it guards) is a real, sharp constraint on ANY future change that
  adds a new `scripts/*.py` sibling import inside a bundled script — it is easy to design a "single-source
  via a new shared module" fix that looks clean in isolation but breaks this invariant (plus a `sys.path`
  gap in the test's own `importlib` loader) unless the designer already knows to check for it. This run
  avoided the trap only because a cold plan critic independently found and verified it before any code was
  written — see below.

**Crew-reported friction:**
- g1-reviewer: `references/checklist-engine.md`'s guidance to "append siblings r4a..r4f and attest an
  umbrella item separately" reads as if the umbrella survey item needs a different verb than its sub-items;
  in practice `record` (the same verb as every leaf) closes the umbrella too. Minor doc-wording nit, not
  promoted to a lesson (single mention, resolved without real friction, reviewer figured it out unaided).
- g2-implementer: a Close Criteria line phrased as "no change to `EXCLUSION_MARKERS`/`PERSON_PRONOUNS` tuple
  contents" read, in isolation, as forbidding any edit near those tuples — resolved by cross-referencing the
  Allowed Scope section (which explicitly permitted adding a sibling regex constant). Suggested future
  handoff phrasing: state explicitly that a tuple's *literal values* don't change even when the *consuming
  function's logic* may.
- Both implementer crews and both reviewer crews independently reproduced every evidence claim before
  reporting (diffs, direct probes, full suite runs) rather than asserting from memory — worth confirming as
  "what worked," not something to fix.

**What worked:**
- The cold plan critic (single critic, dispatched with zero authoring context, told only the plan's
  substance) caught 3 real, independently-verifiable blockers in the original plan (a `sys.path` import gap,
  an external `verify_skill_registered.py` consumer, and the `install_constellation.py` bundle-manifest
  regression test above) before any code was written — this is exactly the failure class the design-it-twice
  /cold-critic doctrine exists to prevent, and it worked as designed. The revised, zero-new-file plan that
  resulted was simpler AND safer than the original.
- `run_crew.py --dispatch external` + a synchronous Agent-tool dispatch + `--verify-result`-style
  independent re-verification (git diff, direct interpreter probes, fresh full-suite re-runs) caught zero
  discrepancies across 2 implementer + 2 reviewer dispatches — every claim matched what was actually on
  disk. The "verify claimed side-effects against the world" doctrine clause earned its keep.
- `git check-ignore` run before each dispatch correctly confirmed the deliverable paths
  (`scripts/curate_corpus.py`, `tests/test_curate_corpus.py`) were tracked, not gitignored, while
  `.agent-work/` itself IS gitignored — avoided any confusion about what would land in the PR diff.

**Improvement signals:**
- The spine/plan template's `gN-integrate` imperative phrasing ("Run the step's checks, then `attest` and
  `advance`") should clarify that `command`-kind postconditions are evaluated BY `advance` itself, not by a
  prior `attest` — → disposition: distilled to lesson `command-postcondition-cannot-attest` (banked, not
  self-applied — doctrine-wording fix needs human authority in delegated mode; see staged `lessons-delta.json`).
- No other concrete skill/template/engine change identified this run beyond the above.
