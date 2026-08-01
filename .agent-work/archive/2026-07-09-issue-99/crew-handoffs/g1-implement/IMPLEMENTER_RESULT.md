# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1 (issue-99)` — design-it-twice generalization: shared contract + doctrine + commander consumption + spine + installer.

## Completed slice
All six deliverables shipped as specified:
1. NEW `skills/_shared/design-it-twice-brief.md` — the shared parallel-alternatives fill-in contract (written fresh in the EXCURSION_BRIEF/CRITIC_HANDOFF register; not copied).
2. `skills/_shared/global-orchestrator.md` — added `## Design-it-twice (standard, not optional)` adjacent to and structurally symmetric with the critical-review section (norm only; mechanism kept in the brief).
3. Same file, critical-review section — added the **competitive-critic** human-opt-in bullet (effort-not-disposition, self-triage guard, named tension vs never-bias-the-reviewer).
4. `skills/commander/SKILL.md` Mission frame — superseded the epic-only critic sentence with a short consumption paragraph pointing at doctrine + `references/design-it-twice-brief.md`.
5. `skills/commander/templates/COMMANDER_SPINE.template.json` — extended the `plan` task imperative and added `check:null` postcondition `c4`.
6. `scripts/install_constellation.py` — added `"design-it-twice-brief.md"` to the `_GLOBAL_ORCHESTRATOR` tuple (one line).

## Scope
**Files changed:**
- `skills/_shared/design-it-twice-brief.md` (new)
- `skills/_shared/global-orchestrator.md`
- `skills/commander/SKILL.md`
- `skills/commander/templates/COMMANDER_SPINE.template.json`
- `scripts/install_constellation.py`

**Specific exclusions touched:** `no` — no explorer files, no per-skill `references/` mirrors, no engine/schema changes, no other installer logic. Confirmed by `git diff --name-only main -- skills scripts docs` = exactly the four modified files, plus the one new untracked file.

## Behavior changed
`no` (doctrine/template surface only). The only executable touched is the installer tuple; its behavior is verified by `--dry-run` passing (the new reference now bundles into every orchestrator-tier skill's `references/`).

## Map Impact
- **Structural anchors touched:** `skills/_shared/global-orchestrator.md` (new norm section, symmetric with critical-review); `skills/commander/SKILL.md` Mission frame (consumption paragraph); `COMMANDER_SPINE.template.json` `plan` task (imperative + c4); `install_constellation.py` `_GLOBAL_ORCHESTRATOR` tuple. New shared contract node `skills/_shared/design-it-twice-brief.md`.
- **Capabilities added/changed/affected:** design-it-twice generalized from explorer-local (excursion design-phase form) to a tier-wide orchestrator norm consumed at Commander plan time (plan-phase form) — same contract, two call sites.
- **Constraints/assumptions touched:** human-only convergence/triage honored; competitive mode modulates effort, never disposition; `execute.json` freeze/amend semantics untouched (only `plan` task edited); shared `_shared/` single source, mirrors are install-time artifacts.
- **Decision candidates / resolved decisions:** encodes the human rulings (shared spun-out contract; norm-in-doctrine / mechanism-in-brief / pointer-in-SKILL layering; c4 kept despite critical-review's plan task lacking a symmetric critic postcondition).
- **Claims/evidence produced:** frozen invariant chain exits 0 (`G1-INVARIANT-GREEN`); diff scope is exactly the owned files.
- **Triage candidates:** see Out-of-scope observations.

## Ruling-traceability table

| Ruling | What it requires | Encoded at |
|---|---|---|
| **q1** — bias-to-yes with named untaken roads | Run by default; skip only genuinely-trivial; every skip named as an untaken road and surfaced at the approval checkpoint, never silent | `global-orchestrator.md` Design-it-twice §, **Bias-to-yes** bullet ("run it by default. Skip only a genuinely-trivial case, and a skip is never silent — it is surfaced as a named **untaken road** … visible at the approval checkpoint"). `design-it-twice-brief.md` intro **Bias to yes** para + **Untaken-road record — loud skips** section. `COMMANDER_SPINE` `plan` imperative ("both bias-to-yes — any skip is surfaced as a named untaken road") + postcondition `c4`. `commander/SKILL.md` ("both **bias-to-yes** with any skip surfaced as a named untaken road"). |
| **q2** — critic reads candidate plan + mission frame only; human disposes every finding | Cold read, no authoring context; the human dispositions every finding (critic never self-triages) | `commander/SKILL.md` ("a **cold plan critic** — an adversarial read of the candidate plan and mission frame by a critic with no authoring context … findings triaged by the human"). `global-orchestrator.md` critical-review § ("triaged by the human, every one … a critic never self-triages") reinforced by the new **competitive-critic** bullet ("the critics still never **self-triage**, and the human disposes every finding — this is the erosion guard"). `COMMANDER_SPINE` `plan` imperative ("a cold plan critic (reads the candidate plan + mission frame only, no authoring context)"). |
| **q2b** — panel preferred; single only for fairly-easy; choice surfaced at approval | Panel is the default lean; single reserved for a fairly-easy call; the count/panel choice is surfaced to the human, overturnable | `global-orchestrator.md` Design-it-twice §, **Count/panel scaled by weight, a surfaced choice** bullet ("a fairly-easy call may run two candidates or a single … a load-bearing interface or architecture-touching plan runs a panel. When in doubt, panel. The count and its rationale are surfaced to the human, not chosen silently"). `design-it-twice-brief.md` **Count and panel — a surfaced choice** + **Panel-vs-single record** sections. `commander/SKILL.md` ("panel scaled by weight as a surfaced choice"). `COMMANDER_SPINE` `plan` `c4` ("panel-vs-single choice surfaced at plan approval"). |

## Test mode
**Required:** `evidence-only` (inspection + mechanical invariant chain; no runtime test surface).
**Satisfied:** `yes` — frozen invariant chain exits 0 as written; diff scope exact; JSON validity confirmed by the chain's `json.load` + `c4` assertion; installer `--dry-run` passes (validates the new reference resolves in `skills/_shared/`).

## Evidence

```bash
# Frozen invariant chain (handoff Verification Commands, run verbatim)
grep -Eqi 'design.it.twice \(standard, not optional\)' skills/_shared/global-orchestrator.md && grep -Eqi 'untaken road' skills/_shared/global-orchestrator.md && grep -Eqi 'not a proposal' skills/_shared/global-orchestrator.md && grep -Eqi 'competitive.critic' skills/_shared/global-orchestrator.md && grep -Eqi 'self.triage' skills/_shared/global-orchestrator.md && grep -Eqi 'when in doubt, panel' skills/_shared/global-orchestrator.md && grep -Eqi 'bias.to.yes' skills/_shared/global-orchestrator.md && grep -Eqi 'design-it-twice-brief' skills/_shared/global-orchestrator.md && test -f skills/_shared/design-it-twice-brief.md && grep -Eqi 'not a proposal' skills/_shared/design-it-twice-brief.md && grep -Eqi 'untaken road' skills/_shared/design-it-twice-brief.md && grep -Eqi 'panel' skills/_shared/design-it-twice-brief.md && grep -Eqi 'plan.alternatives' skills/commander/SKILL.md && grep -Eqi 'plan.critic' skills/commander/SKILL.md && grep -Eqi 'untaken road' skills/commander/SKILL.md && grep -Eqi 'untaken road' skills/commander/templates/COMMANDER_SPINE.template.json && grep -q 'design-it-twice-brief.md' scripts/install_constellation.py && python -c "import json;d=json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json'));assert any(c['id']=='c4' for c in d['tasks']['plan']['postconditions'])" && test -z "$(git diff --name-only main -- skills scripts docs | grep -Ev '^(skills/_shared/global-orchestrator\.md|skills/_shared/design-it-twice-brief\.md|skills/commander/SKILL\.md|skills/commander/templates/COMMANDER_SPINE\.template\.json|scripts/install_constellation\.py)$')" && python scripts/install_constellation.py --agent codex --scope user --dry-run >/dev/null && echo G1-INVARIANT-GREEN
# -> G1-INVARIANT-GREEN

git diff --name-only main -- skills scripts docs
# -> scripts/install_constellation.py
#    skills/_shared/global-orchestrator.md
#    skills/commander/SKILL.md
#    skills/commander/templates/COMMANDER_SPINE.template.json
git status --porcelain -- skills   # -> ?? skills/_shared/design-it-twice-brief.md  (new, untracked — the fifth file)
```

**Result:** `pass` — chain exits 0 (`G1-INVARIANT-GREEN`); diff scope is exactly the four modified owned files; the fifth (new) file is present and untracked (I commit nothing — Commander owns git); none of the five is gitignored (`git check-ignore` exit 1 for each).

## TDD evidence, if required
Not required (evidence-only test mode, no runtime surface). Each implementer plan gate carried its own green command postcondition; all seven gates advanced clean through the engine (`.agent-work/issue-99/crew-handoffs/g1-implement/implementer-plan.json`).

## Docs/contracts touched
- `skills/_shared/global-orchestrator.md` (doctrine), `skills/_shared/design-it-twice-brief.md` (new contract), `skills/commander/SKILL.md` (skill prose pointer), `COMMANDER_SPINE.template.json` (template).

## Assumptions
- Placed the new `## Design-it-twice (standard, not optional)` section immediately **after** the critical-review section (before Handoff completeness) as the "adjacent + symmetric" placement, and mirrored the critical-review bullet register (bolded lead-ins, norm-only, departures-only).
- The competitive-critic bullet lives as the penultimate bullet of the critical-review section (before the `CRITIC_HANDOFF` contract line), so the section still ends on its reusable-contract pointer.
- Read `references/design-it-twice-brief.md` (in the commander paragraph and spine imperative) as the installed mirror path — the installer bundles `skills/_shared/design-it-twice-brief.md` into each orchestrator-tier skill's `references/`, matching how the paragraph already cites `references/global-orchestrator.md`.

## Stop conditions hit
- `none` — confirmed after review: allowed scope was sufficient, no exclusion needed touching, all required evidence produced, and every ruling fell within the handoff's stated authority (no layering/engine/explorer decision was forced).

## Out-of-scope observations
- **Critical-review plan task asymmetry (already-queued triage candidate):** the `plan` task now carries `c4` (`check:null`) attesting both plan-alternatives and the cold plan critic ran, but the doctrine's critical-review norm has no engine-enforced critic postcondition of its own on the plan step — `c4` co-locates both mechanisms under one attest. The handoff's Decision anchors note this follow-up triage candidate is already queued; I did not alter the split. Flagging so Commander confirms it stays queued rather than re-derived.

## Workflow Feedback
- **Handoff gaps:** The frozen invariant chain's diff-scope check (`test -z "$(git diff --name-only main … grep -Ev …)"`) only proves **no unexpected** tracked file changed; it does **not** assert the new `design-it-twice-brief.md` is present in the diff, because an untracked new file never appears in `git diff` until staged. The chain still passes correctly and `test -f` covers the file's existence, but a reviewer reading "diff shows exactly the five owned files" against a 4-line `git diff` output could momentarily mistrust it. A one-line note in the handoff ("the new file is untracked until Commander stages it; `git diff` will show four, `git status` shows the fifth") would remove that friction.
- **Context rediscovered:** Had to confirm from `install_constellation.py` (`validate_required_references`, lines 211-220) that the new reference file must **exist** in `skills/_shared/` for `--dry-run` to pass — so gate ordering had to author the brief before the installer check. The handoff's `--dry-run` requirement implied this ordering but did not state the dependency; the Map Anchor pointed at the tuple line, not the validation gate. Minor — I ordered the gates correctly — but naming the "file must exist before dry-run" dependency would save a re-derivation.
- **Instructions improvised around:** None. The implementer plan template's TDD-red guidance did not apply (evidence-only mode); I collapsed each gate to a single green command postcondition per the template's own "test-after/inspection run" branch — sanctioned, not improvised.
- **What would have made this easier:** The two notes above folded into the handoff (untaked-new-file diff caveat; brief-must-exist-before-dry-run ordering). Everything else was fully specified — the required-tokens list and frozen chain made the doctrine wording targetable without guesswork.

## Return status
`complete`
