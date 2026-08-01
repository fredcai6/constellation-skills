# Problem statement — issue-99

## The ask
Generalize design-it-twice beyond explorer into shared doctrine, and make Commander's plan step consume it — mirroring what #92 did for critical spec review. No new standalone planning skill.

## Confirmed scope
1. **Shared doctrine** (`skills/_shared/global-orchestrator.md`): a design-it-twice standard symmetric with the existing "Critical spec review (standard, not optional)" section — when any skill authors a plan or introduces a load-bearing interface outside explorer, parallel alternatives are generated under distinct constraints before committing; explorer's excursion contract is the reusable pattern.
2. **Commander consumption** (`skills/commander/SKILL.md` + spine/plan wording as needed): at the plan step, plan-alternatives (2–3 parallel agents planning the same issue under distinct constraints) and a cold plan critic, both before the plan-approved checkpoint.
3. **Lift — frame-the-problem-while-agents-run** (Pocock): while parallel alternative agents work, the orchestrator presents the human a framing of the problem space (constraints, dependencies, illustrative sketch explicitly marked "not a proposal") so the human thinks in parallel. Part of the parallel-alternatives contract.
4. **Lift — competitive-critic mode** (J. Vincent, unshipped in superpowers): documented as a human-opt-in option in the critical-review doctrine — panel critics judged against each other on serious confirmed findings — with the tension vs never-bias-the-reviewer stated and human triage as the noise filter.

## Human rulings (interrogation 2026-07-09)
- **q1 — trigger for plan-alternatives:** mission-frame-scaled with **bias to YES** — default is to run it; skip only when genuinely trivial, and any skip is surfaced explicitly as a named **untaken road** (with stated reason, visible at plan approval), never a silent omission.
- **q2 — plan critic:** same dial as q1 ("1 for sure"). Critic reads candidate plan + mission frame only, no authoring context; human triages every finding.
- **q2b — panel scaling (refined):** panels preferred at lower weights too — single critic acceptable only for a fairly easy plan; hard stories get the panel; "when in doubt, panel" stands. Panel-vs-single is a Commander complexity call, and the choice made is always surfaced to the human at plan approval, same loud-choice rule as untaken roads.

## Design calls left to the implementer
- Whether a thin shared handoff/contract template (mirroring CRITIC_HANDOFF) is warranted, or doctrine prose referencing explorer's excursion contract suffices.

## Non-goals
- A new standalone planning skill.
- Changing explorer's own design-it-twice or critic machinery beyond referencing the shared doctrine/option.
- Superpowers-style execution machinery.

## Protected intent
The two mechanisms stay complementary and human-governed: constraint-differentiated *generation* (design/plan-it-twice) and cold *refutation* (critic), both scaled by weight, with the human as the only triage/convergence authority. Bias-to-yes with loud skips: rigor is the default, opting out is visible.
