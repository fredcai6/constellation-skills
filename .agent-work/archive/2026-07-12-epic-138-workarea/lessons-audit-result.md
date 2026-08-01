# Lesson Candidates: `epic-138` (corpus-compliance counter-doctrine)

Fresh-context lessons audit at Admiral closeout. Nominations only — the doctrine
edits and issue filings below are **recommend-and-defer** (I have no filing
authority). The one thing I applied: the `retire` delta that **ENDs all 8 active
lessons** in `.agent-work/LESSONS.md`, via `apply_lessons_delta.py` (see the ready
block at the bottom; applied log pasted in my return message).

Audit followed the survey item sequence brief → logs → feedback → crew → telemetry
→ playbook → consolidate. Every candidate cites a grounding line; ungrounded
observations were dropped.

**Headline:** the inbox is 8-for-8 lessons all *added this epic* — there is no prior
lesson to confirm or disconfirm (clean slate going in). So this audit is pure
graduate-and-retire, not a trust/debt re-count. Every one gets a named permanent home
and a paired retire; none stays active.

---

## A. Active-lesson dispositions (all 8 ENDED)

Legend — Home = the permanent doc that owns the operative content · R&D =
recommend-and-defer (Admiral routes; I cannot file/edit-beyond-one-line) · drill =
ripe-doctrine graduation needing a reproduction drill when the edit is authored.

### 1. `doctrine-restoration-spec-must-prename-structural-adaptations`
- **Scope / class:** constellation / design-authoring · **Confidence:** medium (single occurrence, no telemetry beyond the friction bullet)
- **Observed:** A "transcription-grade" restoration spec (D1) told the implementer to "adapt only the role-noun, flag deviations" when stamping Commander-shaped clauses into implementer/reviewer/interrogator — roles with no spine, archive step, or sub-crew. 3 of 5 full-clause targets needed *structural* substitution of clauses 3/4 (release-ordering, wait-loop), not a noun swap, under a no-paraphrase constraint.
- **Cost:** the implementing Commander had to invent + flag six structural adaptations; escalated to a wave-1 checkpoint for human ratification (ADMIRAL_LOG ESCALATION 2026-07-12; ratified "your judgement, go ahead").
- **Grounding:** AGENT_FEEDBACK 2026-07-12 issue-142 Friction bullet 1; commander-142 verdict "Flagged adaptations" §.
- **Corroboration:** corroborated — the ESCALATION + human ratification is telemetry that the gap was real, not merely asserted.
- **Form / Home:** rung 2 (required template slot). Home = **explorer / DESIGN_SPEC spec-authoring doctrine**: a restoration/stamp-into-N-roles spec must pre-name the adapted per-role wording itself (as D1 already did for the shared pointer sentence), not leave structural substitution to the implementer under a transcription constraint.
- **Routing:** R&D (doctrine edit > 1 line) · **drill candidate** (ripe behavioral doctrine — before-arm: a spec that says "adapt the role-noun" vs after-arm: one that pre-names per-role wording).

### 2. `amend-has-no-inflight-fix-for-own-check-text`
- **Scope / class:** constellation / engine-doctrine · **Confidence:** medium
- **Observed:** `execute.json`'s `amend` verb only touches PENDING gates; an in-progress gate whose own postcondition *check command* is discovered wrong mid-flight has no light repair path except `waive`, which is framed as accepting residual risk, not correcting an authoring typo.
- **Cost:** issue-142 waived `g1-integrate.c1` (self-inflicted stale path after a gitignored→tracked test relocation) — a `waive` that reads as "last resort" when the invariant was actually satisfied.
- **Grounding:** AGENT_FEEDBACK 2026-07-12 issue-142 Friction bullet 2; commander-142 verdict Workflow-feedback bullet 2.
- **Corroboration:** corroborated — a real recorded waive (telemetry).
- **Form / Home:** rung 1 (engine verb). Home = **engine issue** — a narrow "correct the check text, not the condition" repair for an in-progress gate, distinct from `waive`. **Bundle with #6** into one engine "mid-run correction surface" issue (both are "the state-transition surface lacks a light, honest path for a mid-run correction, forcing a heavier/mislabeling verb" — the lessons name each other as family).
- **Routing:** R&D new issue (engine).

### 3. `implementer-skill-engine-ref-path-drift`
- **Scope / class:** constellation / crew-dispatch · **Confidence:** high
- **Observed:** `constellation-implementer` names its engine ref as `references/checklist-engine.md`; the installed path is `skills/workbench/references/checklist-engine.md`. A dispatched implementer had to Glob for it.
- **Cost:** one rediscovery/Glob per implementer dispatch. Same family as the older `reviewer-skill-workbench-path-wording` (CONSTELLATION_FEEDBACK 2026-07-06/07) — a **recurrence** of the workbench-ref-path drift in a sibling role skill.
- **Grounding:** AGENT_FEEDBACK 2026-07-12 issue-140 Crew-reported friction; commander-140 verdict lesson §.
- **Corroboration:** corroborated by the sibling-skill recurrence in prior exports.
- **Form / Home:** rung 2/mechanical. Home = **skills/implementer/SKILL.md** (fix the pointer) **+ a sweep of every role skill** for the same drift (reviewer already flagged historically). The multi-file sweep is why this is deferred, not a one-line self-apply.
- **Routing:** R&D (skill-doc fix + sibling audit). Non-ripe (factual path correction) — **drill-exempt**.

### 4. `headless-hook-probe-allowedtools`
- **Scope / class:** constellation / live-probe · **Confidence:** high
- **Observed:** To live-probe hooks/tools headless on this box, `claude -p ... --allowedTools "Bash"` (non-bypass allowlist) works; `--dangerously-skip-permissions` is refused by the auto-mode "Create Unsafe Agents" classifier. A plain `claude -p` fires SessionStart/Stop but can't run a tool for PostToolUse.
- **Cost:** none this run — it's a *positive* recipe the run proved (issue-141 got a full headless Stop-block end-to-end with it). Value is forward: saves the next probe author the bypass-refusal detour.
- **Grounding:** AGENT_FEEDBACK 2026-07-12 issue-141 Improvement-signals; commander-141 verdict probe log (firing sequence pasted).
- **Corroboration:** corroborated — live probe log with the exact firing sequence.
- **Form / Home:** rung 3 (positive recipe). Home = **skills/_shared/windows.md** next to the `claude -p` probe notes.
- **Routing:** R&D (doctrine addition). Non-ripe (reference recipe) — **drill-exempt**.

### 5. `gate-script-fix-cannot-self-verify`
- **Scope / class:** constellation / delegated-commander-shipping-a-gate-script-fix · **Confidence:** high
- **Observed:** When a run ships a fix to a gate-condition script the spine invokes (issue-143 fixed `verify_agent_feedback.py`), its own frozen spine still runs the INSTALLED pre-fix copy, so it can't close its own gate via the not-yet-installed behavior and must transitionally force-waive.
- **Cost:** a forced waive on feedback.c1 + archive.c1 (recorded FORCED — no override_policy), ratified by the Admiral (ADMIRAL_LOG RULING 2026-07-12, float answered).
- **Grounding:** commander-143 verdict FLOAT §; ADMIRAL_LOG 2026-07-12 "commander-143's one-time transitional force-waive RATIFIED"; **already exported** to CONSTELLATION_FEEDBACK 2026-07-12 issue-143.
- **Corroboration:** corroborated — a recorded forced waive + an Admiral ratification.
- **Form / Home:** rung 1 (engine/harness). Home = **engine/harness design** — either let a dogfooding spine point gate commands at the *worktree's* own script, or standardize the documented transitional waive as the accepted closeout for fix-shipping runs. Recurrence identity is carried by the existing CONSTELLATION_FEEDBACK export.
- **Routing:** R&D (harness/engine design question). Retire is clean — export already durable. Code-targeted — **drill-exempt**.

### 6. `engine-no-unblock-verb-after-resolved-block`
- **Scope / class:** constellation / engine-doctrine · **Confidence:** high
- **Observed:** No verb returns a `blocked` gate to `in-progress` after its blocker clears: `start` refuses a blocked gate, `reopen` requires `complete`, only exit is `skip`. A delegated commander that correctly `block`s to float a blocker (doctrine-blessed) is then forced to `skip`-OBE the resolved step — a false record.
- **Cost:** issue-145 skipped plan+execute as OBE after the human resolved the classifier block — mislabels real, resolved work as overtaken-by-events.
- **Grounding:** commander-145 verdict "Engine gap" + AGENT_FEEDBACK 2026-07-12 issue-145; **already exported** to CONSTELLATION_FEEDBACK 2026-07-12 engine entry.
- **Corroboration:** corroborated — recorded skip-OBE on a resolved block.
- **Form / Home:** rung 1 (engine verb). Home = **engine issue** — a narrow `resume`/`unblock` verb (or `start` re-entering a blocked gate whose blocker the parent cleared), distinct from `reopen`/`skip`. **Bundle with #2.**
- **Routing:** R&D new issue (engine). Code-targeted — **drill-exempt**.

### 7. `auto-mode-classifier-blocks-delegate-eval-arms`
- **Scope / class:** constellation / delegated-measurement · **Confidence:** high
- **Observed:** A delegated auto-mode commander cannot execute the corpus eval harness's core actions — the classifier refuses a direct headless `claude -p` ("Create Unsafe Agents") AND a sanctioned scratch `_rail()` disable ("Auto Mode Bypass", read as bad-faith evasion of the first refusal). Correct move is to float, not work around; the human then runs the arms interactively (the classifier's own named remedy). Also: describing the harness's Popen-spawn as a route "past the classifier" itself trips the classifier.
- **Cost:** a blocked-return round-trip; the whole wave-2 measurement had to run outside the delegate's spine, in the human's session.
- **Grounding:** commander-145 verdict Blocker-history §; ADMIRAL_LOG 2026-07-12 ESCALATION + CHECKPOINT (human ruled option (a)); AGENT_FEEDBACK 2026-07-12 issue-145 Friction.
- **Corroboration:** corroborated — two recorded classifier denials + a human-in-loop resolution logged.
- **Form / Home:** rung 3 (positive recipe / planning contract). Home = **eval-measurement launch-order + Admiral latitude-contract practice**: plan eval-measurement missions to execute in a human-reachable session; **pre-clear eval-harness invocations in the latitude contract** (the Admiral retrospective already names this as the next-time fix); describe harness architecture factually.
- **Routing:** R&D (doctrine + latitude-contract-template guidance). Behavioral — light **drill candidate** (before-arm: a delegate handed an eval-measurement mission with no pre-clearance; after-arm: the pre-clearance clause present).

### 8. `eval-harness-bundles-engine-from-invoking-checkout`
- **Scope / class:** constellation / eval-arm-construction · **Confidence:** high
- **Observed:** In `run_skill_eval.py`, an arm's bundled engine comes from `REPO_ROOT/scripts/` of the checkout that INVOKES the harness (`install_constellation.install_skills` copies from there), NOT from `--worktree` (which only selects the skills' markdown/templates). So corpus-only vs +rail is built by running the harness FROM the rail-suppressed checkout; swapping `--worktree` alone leaves the engine's rail unchanged. Verify arm construction behaviorally (grep RAIL lines: 0 vs 1), not by a source-marker grep.
- **Cost:** none realized — traced from source before building; without it the run would have built two identical +rail arms (a silent-null measurement).
- **Grounding:** commander-145 verdict Arm-construction record + Improvement-signals; AGENT_FEEDBACK 2026-07-12 issue-145 What-worked.
- **Corroboration:** corroborated — behavioral RAIL-line verification (0 vs 1) recorded.
- **Form / Home:** rung 3 (reference contract). Home = **eval-harness docs** (the `run_skill_eval.py` / corpus-eval reference): document the invoking-checkout engine-bundling fact + the behavioral arm-construction verification.
- **Routing:** R&D (doc addition). Non-ripe (reference fact) — **drill-exempt**.

---

## B. Existing-Lesson Reconciliation
- **No `confirm` / `disconfirm` ops.** All 8 active lessons were *added this epic*; there is no prior-cycle lesson for this run's evidence to re-validate or contradict. Checked the full Active list both ways.
- **Family bundling, not new slugs:** #2 + #6 are one engine "mid-run correction surface" family → routed to a single engine issue, but retired under their own ids (distinct defects: check-text repair vs resume-after-block). #3 recurs the older `reviewer-skill-workbench-path-wording` drift in a sibling skill — retired as its own crew-dispatch lesson, noted as the same family for the sweep.

## C. New candidates from logs / cross-project sweep (R&D — not added to the inbox)
The inbox is transitory and this audit is ENDing it; new signal routes straight to
R&D, not into the inbox I'm clearing.

1. **`init-work-area-placeholder-misses-admiral-check-commands`** — **RECURRENCE across two epics.** `init_work_area.py` does not resolve `<epic-id>` in the admiral spine template's engine `check.command` strings; epic-138 hand-patched 9 placeholders fix-now, epic-101 hit the identical `<epic-id>` gap. Form rung 1 (script fix). *Grounding:* ADMIRAL_LOG 2026-07-12 RULING (fix-now, `<epic-id>`→epic-138); AGENT_FEEDBACK epic-101 "init_work_area.py does not resolve `<epic-id>` in ADMIRAL_SPINE.template.json". **Confidence: high** (2-epic recurrence). → R&D issue: `init_work_area.py` resolves `<epic-id>` (and audits the admiral template's check commands).
2. **`corpus-id-install-path-pollution`** — `rewrite_installed_skill_paths` bakes each install's absolute path into every skill file, so byte-identical corpora hash differently by location; D6's N≥8 "same-corpus-hash rolling accumulation" is invalid across differently-located installs. **MUST precede any N≥8 certification run.** *Grounding:* commander-145 verdict corpus-hash caveat; AGENT_FEEDBACK issue-145 tc1. **Confidence: high.** → R&D issue (canonical-path install or path-normalized hashing), priority-before-certification.
3. **`stage-feedback-helper`** — a `stage_feedback.py` to mechanize the staged trio + FENCE.md from the launch order (symmetric to `apply_lessons_delta.py`); the D5 convention currently relies on the fenced commander hand-writing four files. *Grounding:* commander-143 verdict triage-candidate 1; AGENT_FEEDBACK issue-143. **Confidence: medium.** → R&D issue.
4. **`rail-note-in-checklist-engine-design`** — record the #138 channel-A doctrine rail in `docs/CHECKLIST_ENGINE_DESIGN.md` (engine response text now carries decision-point doctrine). *Grounding:* commander-140 verdict tc1. **Confidence: medium.** → R&D doc edit.
5. **`engine-heartbeat-refresh-on-mutating-verb`** — **cross-project (story_time sweep).** The engine could refresh `last_heartbeat` on any successful mutating verb by the lease-holder (start/advance/attest/attach) so an actively-working session never goes stale mid-run; reserve explicit `heartbeat` for idle waits. *Grounding:* story_time CONSTELLATION_FEEDBACK.md epic-3 `engine-could-auto-heartbeat-on-mutating-verbs`; story_time lesson `admiral-heartbeat-lease-during-long-runs` (lease `admiral-epic-3` went stale at execute→closeout, 2091s > 1800s). **Confidence: medium** (single-project so far, but a clean engine-side fix). → R&D issue (engine).
6. **`state-note-precondition-framing-vs-synchronous-crew`** — the `execute` STATE_NOTE crash-resume precondition frames itself "before any detached process," mismatching a synchronous in-turn Agent-tool crew dispatch (pid recorded "none — foreground"). Hit by issue-140 AND issue-141. *Grounding:* AGENT_FEEDBACK issue-140 Friction; commander-141 verdict / AGENT_FEEDBACK issue-141. **Confidence: low** (minor wording). → R&D (STATE_NOTE template / execute-imperative wording; queue for human review).

## D. Already-routed / do-not-re-file
- **Stop-hook misattribution (#151)** — the merged #150 Stop hook fired on the Admiral session because an Agent-tool subagent shares the parent `session_id`; binding keyed by session_id alone can't distinguish parent from subagent. **Already filed as #151** (ADMIRAL_LOG INCIDENT 2026-07-12). Confirm routed; **do NOT re-file.** The Admiral retrospective notes the hook otherwise fired exactly as designed.
- **`attest --which preconditions` before `start` / null-precondition attest** (issue-141 Friction bullet 1) — a member of the long-running `attest-postcondition-which-flag` engine-ergonomics family already exported repeatedly and scheduled into the #48 engine track. Not a new slug; noted here so the sweep counts the recurrence, not re-filed.

## Queued for Human Review
- C6 (`state-note-precondition-framing`) — low confidence, minor wording; do not propagate silently.
- The **reproduction-drill obligation** for the ripe-doctrine graduations (#1, #7): I did not author before/after drills because the doctrine edits are deferred (a drill needs the edited text to exist, and the auditor — not the editor — writes it). When the Admiral authors those edits, a fresh-context drill should follow before they count as landed. #3/#4/#5/#6/#8 and all C-items are non-ripe or code-targeted — **drill-exempt.**

## Workflow Feedback
- **Brief gaps:** none — confirmed after review: the run brief named every artifact path, the model tiers, the queued triage candidates, the standing constraints, and the cross-project sweep roots; I never had to guess "template-wrong vs project-customized" (it stated no TEMPLATES_MANIFEST customizations).
- **Artifact gaps:** minor — the durable `AGENT_FEEDBACK.md` interleaves the epic-138 entries out of newest-on-top order (issue-141/142 at the head, but issue-140/143/145 appended at the tail by the harvest), so I had to grep for the six work-ids rather than reading the head. Not blocking; worth the harvest appending in-order.
- **What would have made this audit easier:** one concrete change — have the harvest step stamp each durable `AGENT_FEEDBACK` entry it appends with the epic id in a consistent position so a closeout audit can pull "all entries for epic-N" with a single grep, instead of reconciling head-vs-tail insertion order.

---

## Playbook Delta (applied by me via apply_lessons_delta.py — retire-only, ENDs the inbox)

```json
{
  "work_id": "epic-138-audit",
  "tick": true,
  "ops": [
    {"op": "retire", "id": "doctrine-restoration-spec-must-prename-structural-adaptations",
     "reason": "graduated to R&D spec-authoring doctrine (explorer/DESIGN_SPEC: restoration specs must pre-name adapted per-role wording); routed in epic-138 lessons-audit-result.md A.1 — drill candidate. Single occurrence, medium confidence."},
    {"op": "retire", "id": "amend-has-no-inflight-fix-for-own-check-text",
     "reason": "graduated to R&D engine issue (narrow correct-the-check-text repair for in-progress gates), bundled with engine-no-unblock-verb into one mid-run-correction issue; routed in lessons-audit-result.md A.2."},
    {"op": "retire", "id": "implementer-skill-engine-ref-path-drift",
     "reason": "graduated to R&D skills/implementer/SKILL.md pointer fix + sibling role-skill drift sweep; routed in lessons-audit-result.md A.3. Non-ripe/factual."},
    {"op": "retire", "id": "headless-hook-probe-allowedtools",
     "reason": "graduated to R&D skills/_shared/windows.md probe-recipe addition; routed in lessons-audit-result.md A.4. Non-ripe reference recipe."},
    {"op": "retire", "id": "gate-script-fix-cannot-self-verify",
     "reason": "graduated to R&D engine/harness design (worktree-script gate commands or standardized transitional waive); recurrence identity already carried by the CONSTELLATION_FEEDBACK issue-143 export; routed in lessons-audit-result.md A.5."},
    {"op": "retire", "id": "engine-no-unblock-verb-after-resolved-block",
     "reason": "graduated to R&D engine issue (narrow resume/unblock verb), bundled with amend-has-no-inflight-fix; recurrence identity carried by the CONSTELLATION_FEEDBACK engine export; routed in lessons-audit-result.md A.6."},
    {"op": "retire", "id": "auto-mode-classifier-blocks-delegate-eval-arms",
     "reason": "graduated to R&D eval-measurement launch-order + latitude-contract practice (run eval missions in a human-reachable session; pre-clear harness invocations); routed in lessons-audit-result.md A.7 — drill candidate."},
    {"op": "retire", "id": "eval-harness-bundles-engine-from-invoking-checkout",
     "reason": "graduated to R&D eval-harness docs (bundled engine comes from the invoking checkout's REPO_ROOT/scripts, not --worktree; verify arm construction behaviorally); routed in lessons-audit-result.md A.8. Non-ripe reference fact."}
  ]
}
```
