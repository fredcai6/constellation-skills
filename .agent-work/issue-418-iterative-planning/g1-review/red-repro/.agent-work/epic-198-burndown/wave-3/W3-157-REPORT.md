# W3-157 Report — spec-prename + eval-latitude-preclearance graduations (with drills)

**Commander:** commander-drill (delegated, opus) · **Branch:** `docs/drill-graduations-157` (base `0f354ed`) · **PR:** https://github.com/fredcai6/constellation-skills/pull/210 (NOT merged — Admiral merges) · **Date:** 2026-07-19

## Verdict — both graduations LANDED (no honest-null)

Honest-null search up front confirmed **neither** graduation was already present in the corpus. Both are genuine additions, each shipped with a fresh-auditor reproduction drill that genuinely fails against the pre-edit text and passes against the edited text.

### Graduation 1 — explorer spec-authoring: pre-name adapted per-role wording
- **Home:** `skills/explorer/SKILL.md` "Spec phase" (primary doctrine) + point-of-use reminder in `skills/explorer/templates/DESIGN_SPEC.template.md` "Chosen design".
- **Rule:** when a DESIGN_SPEC directs transcription-grade / verbatim, no-paraphrase restoration of role-specific doctrine into structurally different roles, the spec must pre-name the adapted per-role wording itself (spell out each divergent target's clause), not pre-rule only a role-noun swap and leave structural substitutions to the implementer. Grounded #142.

### Graduation 2 — admiral latitude: eval/measurement-mission pre-clearance
- **Home:** `skills/admiral/SKILL.md` "Latitude (first bookend)" ONLY. `LATITUDE_CONTRACT.template.md` (#118) untouched — its cross-reference deferred to triage (see below).
- **Rule:** for an eval or measurement mission, the Permission Prerequisites table must pre-clear, at contract time, the harness invocations the delegated commander must run AND any sanctioned corpus-surgery edits its measurement requires — else the auto-mode classifier vetoes the mission's core loop at execute time. Grounded #145.

## Evidence

### Drills (fresh auditors, distinct from the editor and from each other)
- **`docs/superpowers/drills/spec-prename-per-role.md`** — auditor **auditor-g1** (fresh general opus; arms run as genuine fresh **sonnet** sub-agents, doctrine text the sole variable, verbatim capture). **Verdict PASS.** Fail-pre: before-arm under-restores the two structurally-divergent roles (Reviewer 0/4, Implementer 2/4 completion clauses). Pass-post: after-arm pre-names every divergent clause; all four land in all five roles. Honest caveat recorded: reproduced the *drop/under-restore* branch, not the *improvise-silently* branch — both are failures the after-arm fixes.
- **`docs/superpowers/drills/eval-latitude-preclearance.md`** — auditor **auditor-g2** (distinct fresh agent; real sonnet arms). **Verdict PASS.** Fail-pre: before-arm pre-clears only push/issue/merge, omits harness + corpus-surgery. Pass-post: after-arm pre-clears both a harness-execution row and a corpus-fixture-surgery row. Documented a decontamination round (both auditors independently hit the same contamination trap).
- I independently re-verified each drill: exists, records a real PASS, differential driven solely by the doctrine text, no fabrication.

### Independent reviewer (fresh, distinct from editor + both auditors)
- Dispatched via `run_crew.py --backend external` + `--verify-result` (fresh: completed). **Verdict APPROVE.** Ran the pointer greps, read both drills, confirmed no out-of-scope file, and **re-ran the full suite himself: 888 passed, 2 skipped**. Also independently confirmed #142/#145 are real CLOSED issues matching their grounding.

### Full suite
- Baseline (pre-change): **888 passed, 2 skipped**. Post-change (reviewer + engine g5-integrate postcondition): **888 passed, 2 skipped**. All pre-existing tests stay green.

### Worktree isolation
```
worktree OK: in C:/Programs/cs-wt-drill
EXIT: 0
```
(`py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-drill` — exit 0, run before any git op.)

## Map impact
Skill-source repo — no `docs/architecture` packet map. Reasoned no-op: doctrine edits fold into the role SKILL.md sources in place (the structural record for doctrine); both drills sit in the established flat `docs/superpowers/drills/` home (no index file to update). No code structure/boundary touched.

## Triage candidates
- **TR-1 (recommend-and-defer → #118):** add an eval/measurement-mission pre-clearance pointer to `skills/admiral/templates/LATITUDE_CONTRACT.template.md` Permission Prerequisites (point-of-use cross-reference to the graduated SKILL doctrine, mirroring how G1 added a DESIGN_SPEC.template reminder). That file is owned by the #118 commander this wave and a new issue exceeds my latitude — deferred. Full recommendation in the archived work area `TRIAGE_RECOMMENDATIONS.md`.
- Non-candidates recorded (not filed): dangling `config_ref` to a non-existent `docs/agents/engine-config.json` (sanctioned degradation, by-design); grounded-issue titles absent from the reviewer handoff (handoff nicety → feedback).

## Workflow feedback (staged trio + FENCE)
`.agent-work/` resolves (git-common-dir) to the MAIN checkout, which my launch order fences me from writing. Per fenced-closeout doctrine I **staged** the durable trio worktree-locally at `.agent-work/staged-feedback/157-drill/` (AGENT_FEEDBACK.md, lessons-delta.json, CONSTELLATION_FEEDBACK.md) + `FENCE.md` citing this launch order — `verify_agent_feedback.py` accepts it in lieu of the durable-root write. **Please harvest that trio into the shared root before sweeping the worktree.**

Two constellation-scoped exports for the epic lessons audit:
1. **drill-scenario-decontamination** (high confidence, independently rediscovered by both auditors): state a reproduction-drill scenario positively / by-outcome; never pre-itemize or alarm-flag the failure trigger — a contaminated scenario passes both arms and proves nothing. Proposed home: repro-drill doctrine / lessons-auditor.
2. **delegated-commander-in-team-synchronous-crew:** inside a team harness a delegated Commander cannot dispatch named or background subagents — crew runs synchronously and unnamed; but nested spawning by the crew itself IS available (which is what let the auditors run genuine two-arm sub-dispatches). Proposed home: `references/crew-dispatch.md`.

Minor: the engine's RAIL banner floods every mutating call's stdout, so `| tail -1` often shows a RAIL line rather than the verb result — had to grep for `complete|REFUSED|in-progress`.

## Spine provenance
Full spine driven init→context→understand→plan→execute→reconcile→triage→review→feedback→archive through the engine; execute.json (7 items) driven to DONE; both leases released after the terminal advance. Archived work area: `.agent-work/archive/2026-07-19-157-drill/` (in the worktree).
