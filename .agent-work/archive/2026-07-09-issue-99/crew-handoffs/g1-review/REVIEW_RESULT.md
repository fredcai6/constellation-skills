# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1 (issue-99)` — design-it-twice generalization: shared contract + doctrine + commander consumption + spine + installer.

## Result
`APPROVE`

Survey driven through the vendored engine at `.agent-work/issue-99/crew-handoffs/g1-review/review.json`; all 8 items (context + 7 close criteria) visited, all pass, consolidated `verdict=APPROVE findings=0`. Frozen invariant chain re-run independently in my hands → `G1-INVARIANT-GREEN`.

## Handoff compliance
Every deliverable the handoff asked for is present and matches spec, within allowed scope. All seven Close Criteria pass (per-check findings below). Independently reproduced, not taken from the report: re-ran the full frozen invariant chain (green), re-ran `git diff --name-only main` and `git status --porcelain` (scope exact), read all five diffs and the new brief in full, and read the EXCURSION_BRIEF/CRITIC_HANDOFF register sources for the symmetry/register judgments.

## Per-check findings (one per Close Criterion)

1. **Symmetry read — PASS.** Side-by-side, the new `## Design-it-twice (standard, not optional)` section mirrors `## Critical spec review (standard, not optional)`: identical heading pattern, bolded-lead-in norm-only bullets, weight-scaled count ("When in doubt, panel" in both), human-only authority (Acceptance/Convergence is human-only), and both END on their reusable-contract pointer (critical-review → `CRITIC_HANDOFF`; design-it-twice → `design-it-twice-brief.md`). Mechanism kept out of doctrine (norm only). Weight/register match.

2. **Ruling fidelity — PASS.** Traceability table verified against actual text. q1: "Bias-to-yes: run it by default. Skip only a genuinely-trivial case … surfaced as a named **untaken road** … visible at the approval checkpoint." q2: commander SKILL.md "a **cold plan critic** — an adversarial read of the candidate plan and mission frame by a critic with no authoring context … findings triaged by the human", reinforced by critical-review "triaged by the human, every one … a critic never self-triages". q2b: "a fairly-easy call may run two candidates or a single …; a load-bearing interface or architecture-touching plan runs a panel. When in doubt, panel. The count and its rationale are surfaced to the human." Rows accurate; no drift.

3. **Competitive-critic erosion guard — PASS.** "Competition modulates critic **effort**, never **disposition** — the critics still never **self-triage**, and the human disposes every finding (this is the erosion guard)." Human-only triage preserved; competition touches effort only. Tension stated, not implied: "It sits in explicit tension with never-bias-the-reviewer — a critic told to compete is no longer a neutral cold reader — so it is opt-in per run, never the default."

4. **Commander SKILL.md internal consistency — PASS.** The old epic-only critic sentence is fully removed in the diff (not left contradicting). The replacement paragraph names both mechanisms, both bias-to-yes with untaken-road skips, points at doctrine + `references/design-it-twice-brief.md`, and closes "Both point at doctrine — the rules live there, not here." Points rather than restates; section reads coherently.

5. **Brief is a genuine spin-out — PASS.** Written fresh in the EXCURSION_BRIEF/CRITIC_HANDOFF register (angle-bracket fill-in fragments, bolded lead-ins, dense agent-facing), not copied. Covers the contract: N≥2 parallel agents each under one named distinct constraint (interface + plan menus, run may name its own), axes depth/locality/seam-placement/testability, "a recommendation, never a menu". All three new fields present: framing block with illustrative sketch "explicitly marked 'not a proposal' … zero weight at convergence"; Untaken-road record (loud skips); Panel-vs-single record. States both call sites (explorer design-phase / plan-phase) so it is usable by explorer/commander/admiral.

6. **Spine c4 + JSON — PASS.** `plan` task carries new postcondition `c4` (`check: null`): "plan-alternatives run (or skip surfaced as a named untaken road) and cold plan critic run; panel-vs-single choice surfaced at plan approval" — covers alternatives-or-loud-skip + critic + surfaced panel choice. Imperative extended to name the brief, the cold plan critic (plan+frame only), loud-skip, and the surfaced panel-vs-single choice. JSON valid (engine `json.load` + `c4` assertion pass). Diff touches ONLY the `plan` task; freeze/amend semantics and all other tasks untouched.

7. **Scope + non-goals — PASS.** `git diff --name-only main` = exactly the four modified owned files; `git status` shows the fifth (`design-it-twice-brief.md`) untracked — five owned files, nothing else. No `skills/explorer/**`, no `checklist_engine.py`/schema, no per-skill `references/` mirror edits. Installer change is exactly one tuple line (`design-it-twice-brief.md` added to `_GLOBAL_ORCHESTRATOR`); `commander` maps to `_GLOBAL_ORCHESTRATOR` so its `references/design-it-twice-brief.md` pointer resolves. `--dry-run` passes.

## Evidence verdict
Required evidence present and independently reproduced. Test mode is evidence-only (doc/doctrine gate, no runtime surface) — correct for this change; the frozen grep/JSON/dry-run chain is the mechanical evidence and it exits 0 as written in my hands (`G1-INVARIANT-GREEN`). The untracked-new-file caveat the implementer flagged is real and benign: `test -f` covers the brief's existence and `git status` shows it; `git diff` legitimately shows four. Ruling-traceability table checks out against the text.

## Map impact verdict
- **Evidence supports claimed change:** Yes. The doctrine/template edits are exactly what the invariant chain and diffs show; the one executable change (installer tuple) is exercised by the passing `--dry-run`.
- **Constraints not violated:** Yes. Human-only convergence/triage honored; competitive mode modulates effort not disposition; `execute.json` freeze/amend semantics untouched (only `plan` task edited); layering respected — norm in doctrine, mechanism in brief, pointer in SKILL.md, with no rule restated across layers (checked for drift; the SKILL.md paragraph and spine imperative point at the brief rather than re-encoding the menus/axes).
- **Notes match the diff:** Yes. Map Impact notes accurately describe the new shared node, the two call sites, and the touched anchors; nothing overstated or missing.
- **Decision candidates surfaced:** Yes. Human rulings encoded, not decided alone; the plan-task asymmetry is surfaced (not silently resolved).
- **Durable context routed:** Yes. The asymmetry is flagged as a triage candidate rather than dropped.

## Reconciliation check
No new divergence from recorded architecture. The change adds a shared doctrine node and a symmetric norm section consistent with the existing critical-review model; the installer bundles it through the established `_GLOBAL_ORCHESTRATOR` mechanism.

## Blockers
- none

## Out-of-scope observations
- **Critical-review plan-task asymmetry (ALREADY QUEUED — not a new finding):** `plan.c4` co-attests both plan-alternatives and the cold plan critic, but the critical-review norm has no engine-enforced critic postcondition of its own. Per the handoff's Decision anchors this is a queued triage candidate to *confirm stays queued*, not re-derive as a blocker. I searched for any NEW asymmetry introduced by this change and found none. Recorded in the survey as `tc1`.

## Workflow Feedback
- **Handoff gaps:** The reviewer handoff was unusually complete — it pre-empted the one real friction point (the untracked-new-file / `git diff` shows four vs `git status` shows five) directly in "How to Inspect the Diff", so it never cost me a mistrust cycle. The implementer's own workflow feedback independently recommends folding that caveat into the *implementer* handoff too; I concur — the reviewer handoff already carries it, the implementer handoff did not.
- **Context rediscovered:** None material. I did verify one thing the handoff left implicit: that `commander` is an orchestrator-tier skill in `SKILL_REFERENCE_BUNDLES`, so its `references/design-it-twice-brief.md` pointer actually resolves post-install (it does — `commander: _GLOBAL_ORCHESTRATOR`). Naming that resolution in the handoff's installer anchor would save a reviewer the lookup, but it is minor.
- **Instructions improvised around:** None. The engine survey flow, the co-located survey/result path (per lesson `reviewer-handoff-survey-result-paths-split`), and the 7-criteria-as-checks mapping all applied cleanly. The template's generic r0–r5 items were superseded by the handoff's explicit "Close Criteria are your review checks" instruction; I built the survey from the criteria directly (context-load item + c1–c7) — sanctioned by the skill's "append checks the context warrants", not a deviation.
- **What would have made this easier:** Nothing beyond the two minor notes above. The required-tokens list, frozen chain, and explicit per-criterion Close Criteria made this review targetable without guesswork.

## Return status
`complete`
