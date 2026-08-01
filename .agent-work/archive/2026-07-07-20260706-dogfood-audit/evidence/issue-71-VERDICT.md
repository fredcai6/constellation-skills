# VERDICT — issue-71

## 1. Verdict + summary
**APPROVE / complete.** Added a required-slot **"Permission prerequisites"** section to `skills/admiral/templates/LATITUDE_CONTRACT.template.md` (after the Decision Classes table, before Float-Up Routing): per-`delegated`-class external-action inventory + a pre-clearance-or-fallback field, citing this epic's live classifier-refusal-of-a-delegated-`gh pr merge` / "approve now; batch the rest" ruling as the worked example. Added one probe line to `skills/admiral/SKILL.md`'s "Latitude (first bookend)" paragraph pointing to the new section. `skills/interrogator/SKILL.md` confirmed (twice, independently, by implementer and reviewer) to carry no latitude-interview-specific guidance — left untouched. No engine/script changes; Decision Classes table untouched.

## 2. PR URL
https://github.com/fredcai6/constellation-skills/pull/85 (`Closes #71`, not merged, per instructions)

## 3. Test tail
```
....................................................................  [ 19%]
.................................................................................................................................... [ 55%]
........................................................................ [ 74%]
..................................................................  [ 92%]
............s...............                                             [100%]
369 passed, 1 skipped, 18 subtests passed in 9.66s
```
Independently reproduced three times: implementer, fresh-context reviewer, and me at g1-integrate — identical counts each time.

## 4. Isolation confirmation
`verify_worktree_isolation.py --here C:/Programs/constellation-skills-worktrees/issue-71` → `worktree OK` (run at dispatch, before any work started). Branch `constellation/issue-71`, base `origin/main` f1aa9bc, one commit `cc255b6`, working tree clean, pushed.

## 5. Map impact
None. This repo carries no packet map (skill-source repo); reconcile step reasoned a no-op — the change touched neither `docs/CHECKLIST_SCHEMA.md` nor a design doc (grepped `docs/` for `LATITUDE_CONTRACT`/`Decision Classes`/`Permission prerequisites` before deciding — only historical `docs/superpowers/plans|specs/*` hits, no living structural doc to update).

## 6. Triage candidates
None generated this run (`execute.json` and `spine.json` both show empty `triage_candidates`). Reviewer's one incidental observation (engine `append` verb inserts new items at the end of `items` rather than after a logical anchor) was noticed while it was reading engine internals for an unrelated reason, not something this gate's own handoffs hit — recorded as Workflow Feedback below, not a triage candidate.

## 7. Workflow Feedback + AGENT_FEEDBACK entry + lessons-delta

**Per your ruling:** `feedback.c1` and `archive.c1` were waived (`--authority admiral --force`, your exact reason string) rather than run against canonical, since verify_agent_feedback.py's default redirects to the main-checkout `AGENT_FEEDBACK.md` and wave4b-73 is running concurrently. Both are recorded in the spine as `WAIVED`. `feedback.c2` / `verify_lessons_applied.py --file .agent-work/LESSONS.md` needed no action — worktree-relative, no local playbook, passed clean ("no playbook — clear").

**AGENT_FEEDBACK entry (verbatim, for your harvest into canonical `.agent-work/AGENT_FEEDBACK.md`):**

---
## `2026-07-07` — `issue-71`

**Run shape:** `commander` · 11 spine steps, 1 crew gate (`g1`: implement/review/integrate) · sonnet-class implementer + fresh-context sonnet-class reviewer (Agent-tool, `--backend external`)

**Instruction adherence:** `fully followed`
- Drove the full gated spine through the engine end to end; all four `user-decision` checkpoints satisfied in delegated mode by citing the frozen launch order (`LAUNCH_ORDER:Mission` / `:Inherited Latitude` / `:Return Shape`). Used this SOURCE repo's own `skills/commander/templates/COMMANDER_SPINE.template.json` and `scripts/checklist_engine.py` (not the globally-installed skill copy) per the launch order's explicit note that `<commander-skill-dir>/scripts` resolves to top-level `scripts/` here — worth flagging as its own friction point below.
- `context`/`reconcile` used this repo's documented escape hatches cleanly: no `docs/agents/*` overlay → substituted README.md + `docs/CONSTELLATION_OVERVIEW.md`; no packet map → reasoned no-op at reconcile (change touched neither `docs/CHECKLIST_SCHEMA.md` nor a design doc, confirmed by grep before deciding).
- `plan` shrank the mission frame to a one-line "no map, trivial doc change" note per the skill's own guidance for a trivial local edit — did not author a full `MISSION_FRAME.template.md`.
- Genuine mid-run gap floated up rather than guessed: the `feedback` step's `verify_agent_feedback.py` postcondition has no `--root` escape hatch in its hardcoded command and redirects to the Admiral-owned canonical file mid-epic; queried you rather than picking a side unilaterally, since it touches shared epic state across concurrent wave-4b commanders.

**Friction / unclear:**
- Two different copies of `COMMANDER_SPINE.template.json` exist and can diverge: the globally-installed skill (`~/.claude/skills/constellation-commander/templates/...`, still lists a separate `compact` item) vs. this repo's own source copy (`skills/commander/templates/...`, already folds `compact` into `execute`'s precondition — the escape-hatches commit). Invoking the Skill tool loads the installed doctrine/instructions, but the actual engine-driven spine should come from the repo's own template when dogfooding on this very repo. Nothing in the skill invocation flags which copy governs; I had to notice the discrepancy by diffing the two files myself. Confirms the friction issue-61 already reported in passing ("the skill doc and the repo spine describe the step list differently") — recurrence, not new, but never promoted to a durable lesson until now.
- The `feedback` step's two engine-checked postconditions behave inconsistently under a linked worktree without it being obvious from the spine text: `verify_lessons_applied.py --file .agent-work/LESSONS.md` (hardcoded relative path) resolves worktree-local because explicit `--file` always wins in that script, while `verify_agent_feedback.py <work-id> --phase feedback` (no `--root` given) resolves via `durable_root()` to the main checkout. Both scripts share the same "PR #84" durable-root mechanism, but only one of the two hardcoded commands actually exercises it — I had to read both scripts' source to tell them apart.

**Crew-reported friction:**
- None reported by either crew member — both handoffs were followed with zero rework, zero BLOCK verdicts. Implementer: "unusually complete handoff, no gaps." Reviewer (fresh-context): "unusually complete handoff" — its only note was the engine `append`-verb ordering quirk noticed incidentally while reading engine internals for an unrelated survey, not something this gate's handoffs hit.

**What worked:**
- The required-slot handoff (exact placement, exact close criteria enumerated as a checklist, the worked example spelled out so the implementer didn't have to go hunting for the ADMIRAL_LOG entry) meant the diff matched the ask on the first pass — no rework cycle.
- `run_crew.py --backend external` + `--verify-result` + `recover_crews.py` pre-dispatch check kept both crew dispatches durable and duplicate-free; `recover_crews.py` correctly reported the implementer attempt as `COMPLETE — recoverable/complete; do not rerun` before the reviewer dispatch.
- Independent reviewer re-running the exact same verification command (`python -m pytest -q`) and reproducing the implementer's reported numbers exactly gave real confidence beyond just trusting the reported evidence.

**Improvement signals:**
- State explicitly, in the commander skill's Delegated/autonomous mode section (or the spine's own `init`/`context` imperative), that a Commander dispatched INTO the constellation-skills source repo itself must drive the engine from that repo's own `skills/*/templates/*` and `scripts/*`, not the globally-installed skill copy that the Skill tool loads. → disposition: distilled to a new lesson `commander-template-source-vs-installed-divergence` (no existing lesson id matched — issue-61's note was only ever a raw AGENT_FEEDBACK bullet, never promoted).
- Give the `feedback` step's two hardcoded postcondition commands consistent worktree-under-epic behavior (both `--root`-parameterized, or both explicit-relative), so a Commander doesn't have to read both scripts' source to discover only one of them redirects. → disposition: reinforces (does not duplicate) the still-open `commander-worktree-local-durable-writes-under-epic` lesson from issue-74 — recommend the Admiral's harvest fold this as corroborating grounding into that lesson rather than opening a third variant.

---

**lessons-delta.json** (staged at `.agent-work/archive/2026-07-07-issue-71/lessons-delta.json`, `tick=true`, validated via `--dry-run` against a scratch snapshot, NOT applied to canonical):
- `confirm dogfood-context-paths-absent` — grounded in this run's context-step substitution.
- `add commander-template-source-vs-installed-divergence` — new lesson, grounded in this run + issue-61's prior (unpromoted) mention.

All archive artifacts (execute.json, crew handoffs/results, STATE_NOTE, AGENT_FEEDBACK.entry.md, lessons-delta.json, pr-body.md) are under `.agent-work/archive/2026-07-07-issue-71/` in this worktree for your harvest.
