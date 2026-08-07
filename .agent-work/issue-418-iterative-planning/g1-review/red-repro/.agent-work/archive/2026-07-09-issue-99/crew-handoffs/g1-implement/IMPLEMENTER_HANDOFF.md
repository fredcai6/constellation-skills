# Implementer Handoff

## Gate
g1 (issue-99)

## Task
Ship the design-it-twice generalization: one new shared contract file, two doctrine edits, a Commander consumption paragraph, a spine plan-task extension, and a one-line installer bundle addition.

1. **NEW `skills/_shared/design-it-twice-brief.md`** — the shared parallel-alternatives contract, spun out of explorer's EXCURSION_BRIEF design-it-twice type (write it fresh in that spirit; do not copy-paste or edit EXCURSION_BRIEF). A fill-in brief for running N≥2 parallel agents, each under ONE named distinct constraint. Must carry:
   - Constraint menus: for interfaces — minimal-interface / max-flexibility / common-caller-first / ports-and-adapters; for plans — smallest-diff / most-testable / best-seam-placement (menus are starting points; a run may name its own constraint).
   - Comparison axes: depth / locality / seam placement / testability.
   - Output rule: opinionated recommendation or named hybrid — never a menu.
   - **Framing block** the orchestrator presents to the human while the agents run: constraints, dependencies, an illustrative sketch **explicitly marked "not a proposal"** — so the human thinks in parallel instead of waiting.
   - **Untaken-road record**: when the run skips alternatives (genuinely-trivial), the skip is named with its reason and surfaced at the approval checkpoint — never silent.
   - **Panel-vs-single record**: the count/panel choice with rationale, surfaced at the approval checkpoint.
   - Register: dense, agent-facing, fill-in fragments like CRITIC_HANDOFF/EXCURSION_BRIEF. Rich template over prose — the mechanism lives HERE, not in skill prose.
2. **`skills/_shared/global-orchestrator.md`** — add a section headed exactly `## Design-it-twice (standard, not optional)`, placed adjacent to the critical-review section and structurally symmetric with it. NORM ONLY (mechanism stays in the brief): trigger — any skill authoring a plan or introducing a load-bearing interface; **bias-to-yes** — run it by default, skip only a genuinely-trivial case, and any skip is surfaced as a named **untaken road** (reason stated, visible at the approval checkpoint); count/panel scaled by weight as a surfaced choice — "when in doubt, panel"; convergence is human-only; names `design-it-twice-brief.md` as the reusable contract and notes explorer's excursion design-it-twice type is the same contract in its design-phase form. Keep it about the size/register of the critical-review section.
3. **Same file, critical-review section** — add the **competitive-critic** human-opt-in option: panel critics told they are judged against each other on serious confirmed findings. MUST state: competition modulates critic *effort*, never disposition — critics still never **self-triage**, the human disposes every finding (this is the erosion guard); and name the tension vs never-bias-the-reviewer explicitly.
4. **`skills/commander/SKILL.md`** — in the "Mission frame" section, supersede the epic-only critic sentence ("A plan at epic weight — ... — gets a cold critical review before the plan-approved checkpoint, per the shared critical-spec-review standard..."). Replacement: a SHORT consumption paragraph — before the plan-approved checkpoint the plan step runs **plan-alternatives** (per the shared design-it-twice standard and `references/design-it-twice-brief.md` contract) and a **cold plan critic** (reads the candidate plan + mission frame only, no authoring context, per the critical-spec-review standard; panel scaled by weight as a surfaced choice), both bias-to-yes with any skip surfaced as a named untaken road. Point at doctrine; do NOT restate the rules. The section must read internally consistent — no surviving contradiction with the old epic-only wording.
5. **`skills/commander/templates/COMMANDER_SPINE.template.json`** — `plan` task only: extend the imperative to name plan-alternatives (via the brief), the cold plan critic, loud-skip (untaken road), and the surfaced panel-vs-single choice; ADD postcondition `c4` with `check: null`, statement: "plan-alternatives run (or skip surfaced as a named untaken road) and cold plan critic run; panel-vs-single choice surfaced at plan approval". JSON must stay valid; do not touch freeze/amend semantics or any other task.
6. **`scripts/install_constellation.py`** — add `"design-it-twice-brief.md"` to the `_GLOBAL_ORCHESTRATOR` tuple (line ~95). One line. `--dry-run` must pass.

## Protected Intent
Two complementary, human-governed mechanisms: constraint-differentiated generation (design-it-twice) and cold refutation (critic), both scaled by weight, human as the only triage/convergence authority. Rigor is the default; opting out is loud.

## Test Mode
Inspection-only + mechanical invariant chain (doc/doctrine gate — no runtime test surface; the frozen grep/JSON/dry-run chain below is the mechanical evidence).

## Close Criteria
- All six deliverables present as specified; doctrine section symmetric with critical-review; commander paragraph points rather than restates.
- The frozen invariant chain (Verification Commands) exits 0 **as written** — do not invent additional check proxies.
- Ruling-traceability table produced (see Required Evidence).
- `git diff --name-only main -- skills scripts docs` shows exactly the five owned files.

## Allowed Scope
Only: `skills/_shared/design-it-twice-brief.md` (new), `skills/_shared/global-orchestrator.md`, `skills/commander/SKILL.md`, `skills/commander/templates/COMMANDER_SPINE.template.json`, `scripts/install_constellation.py` (the one tuple line).

## Specific Exclusions
- NO explorer files (`skills/explorer/**`) — owned by gate g2 of this run.
- NO per-skill `references/` mirrors — `skills/_shared/` is the single source; mirrors are install-time artifacts.
- NO engine/schema changes (`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`); no other installer logic.

## Constraints
- Doctrine register: dense, agent-facing, departures-only; match surrounding prose.
- Required tokens (tolerant greps are case-insensitive; `.` matches hyphen/space): "untaken road", "not a proposal", "competitive-critic" (hyphenated), "self-triage", "when in doubt, panel", "bias to yes" or "bias-to-yes", heading "Design-it-twice (standard, not optional)".
- Human rulings to encode faithfully (q1/q2/q2b): bias-to-yes with named untaken roads; critic reads candidate plan + mission frame only; panel preferred, single only for fairly-easy, choice surfaced at approval.

## Map Anchors (inbound)
- **Structural:** `skills/_shared/global-orchestrator.md` (critical-review section = symmetry model); `skills/commander/SKILL.md` Mission frame; spine template `plan` task; installer `_GLOBAL_ORCHESTRATOR` tuple (install_constellation.py:94-113).
- **Capability:** shared orchestrator doctrine baseline; Commander per-issue planning; installer reference bundling.
- **Constraints/assumptions:** human-only convergence/triage — competitive mode modulates effort, never disposition; execute.json freeze/amend semantics unchanged; rich shared template over skill prose (human ruling).
- **Decision anchors:** shared spun-out contract (human ruling — not commander-local, not EXCURSION_BRIEF reuse); c4 kept despite critical-review asymmetry (follow-up triage candidate already queued).
- **Evidence expectations:** ruling-traceability table; frozen invariant chain; reviewer will do a side-by-side symmetry read.
- **Map confidence flags:** none — propagation path verified at plan time.

## Deliverable Path Check
- **Committed** — all five paths; verified `git check-ignore <path>` exit 1 for each on 2026-07-09 (design-it-twice-brief.md, global-orchestrator.md, commander/SKILL.md, COMMANDER_SPINE.template.json, install_constellation.py).

## Required Evidence
- **Ruling-traceability table**: one row per ruling — q1 bias-to-yes + untaken road; q2 critic reads plan+frame only, human disposes every finding; q2b panel preferred / single-if-easy / choice surfaced — mapped to the exact sentence(s) encoding it in `_shared` doctrine (and the brief where applicable). Include in IMPLEMENTER_RESULT.
- Output of the full Verification Commands chain (exit 0).
- `git diff --name-only main -- skills scripts docs` output (exactly the five files).

## Verification Commands

```bash
grep -Eqi 'design.it.twice \(standard, not optional\)' skills/_shared/global-orchestrator.md && grep -Eqi 'untaken road' skills/_shared/global-orchestrator.md && grep -Eqi 'not a proposal' skills/_shared/global-orchestrator.md && grep -Eqi 'competitive.critic' skills/_shared/global-orchestrator.md && grep -Eqi 'self.triage' skills/_shared/global-orchestrator.md && grep -Eqi 'when in doubt, panel' skills/_shared/global-orchestrator.md && grep -Eqi 'bias.to.yes' skills/_shared/global-orchestrator.md && grep -Eqi 'design-it-twice-brief' skills/_shared/global-orchestrator.md && test -f skills/_shared/design-it-twice-brief.md && grep -Eqi 'not a proposal' skills/_shared/design-it-twice-brief.md && grep -Eqi 'untaken road' skills/_shared/design-it-twice-brief.md && grep -Eqi 'panel' skills/_shared/design-it-twice-brief.md && grep -Eqi 'plan.alternatives' skills/commander/SKILL.md && grep -Eqi 'plan.critic' skills/commander/SKILL.md && grep -Eqi 'untaken road' skills/commander/SKILL.md && grep -Eqi 'untaken road' skills/commander/templates/COMMANDER_SPINE.template.json && grep -q 'design-it-twice-brief.md' scripts/install_constellation.py && python -c "import json;d=json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json'));assert any(c['id']=='c4' for c in d['tasks']['plan']['postconditions'])" && test -z "$(git diff --name-only main -- skills scripts docs | grep -Ev '^(skills/_shared/global-orchestrator\.md|skills/_shared/design-it-twice-brief\.md|skills/commander/SKILL\.md|skills/commander/templates/COMMANDER_SPINE\.template\.json|scripts/install_constellation\.py)$')" && python scripts/install_constellation.py --agent codex --scope user --dry-run >/dev/null && echo G1-INVARIANT-GREEN
```

## Suggested Model Tier
Stronger — doctrine wording governs every future run; register-matching and faithful ruling encoding carry ambiguity.

## Authority
Decided (human): shared spun-out contract; doctrine = norm only, brief = mechanism, SKILL.md = pointer; c4 kept; bias-to-yes/untaken-road/panel rulings. You must NOT decide alone: any change to explorer files, engine semantics, other installer logic, or the layering split. If the frozen invariant chain is wrong (a check cannot legitimately pass), STOP and return rather than bending content to a broken check.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, a decision outside the given authority is needed.

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/issue-99/crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md`: completed slice, files changed, test mode satisfied, evidence produced (incl. the ruling-traceability table and invariant-chain output), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
