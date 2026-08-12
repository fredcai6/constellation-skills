## `2026-07-28` — `governor-262`

**Run shape:** commander (delegated, frozen Admiral LAUNCH_ORDER, no reachable human) · 10 spine steps + 8 execute.json items (3 gates) · 4 commits · subagent tiers: sonnet (3 design-it-twice candidates, cold plan critic), opus (2 implementers, 2 reviewers)

**Instruction adherence:** minor deviations
- Engine drove everything: spine lease claimed at `init`, every step `start`/`attest`/`advance`d, both crew gates dispatched through `run_crew.py` with `recover_crews.py` checked before each launch. No hand-edited checklist state.
- Ran the design-it-twice panel at **N=3** rather than the minimum 2, and ran the cold plan critic — both bias-to-yes calls. Both paid: the critic returned four findings applied before the plan froze, and the panel's *convergence* turned out to be its most valuable output rather than any single candidate.
- **Ratified a crew self-amendment.** The g2 implementer's own plan demanded `verify_skill_registered.py` exit 0, which became unsatisfiable when its fix un-masked a true pre-existing failure. It escalated to me twice; I was idle *waiting on its result*, so waiting would have deadlocked. It used `amend --op retext-check` to align its check text with what my handoff actually required and left one auditable entry. Right call, and I ratified it.
- **Fixed a reviewer finding myself rather than filing it** (`g2-integrate`): free env-token expansion could report an unrelated `%VAR%` entry as `wired`. That is a defect in the exact piece the Admiral ranked most-protected, so a fix-now beat a filing. Self-reviewed, and disclosed as such in the PR.

**Friction / unclear:**
- **`SendMessage` addressing:** the agent name my own launch order assigns (`governor-262`) is **not** a reachable SendMessage address; the reachable one is `commander-262`. Three separate crews independently hit this and each lost a step to it. My g1 handoff carried the wrong address; g2's were corrected.
- **No gauge, by construction.** The wiring exists only in the main checkout's gitignored `settings.local.json`, so I had no gauge writer and could not measure my own context fill. The Admiral's after-the-fact calibration from four prior Commanders (183K–354K against a 150K HARD band, none aware) was the only instrument-substitute available, and it shaped how I sequenced the back half.
- **The paper trail has two places to record a decision grade and no check that they agree.** `mission-frame.md` still said `guess` where `execute.json` said `settled/admiral`. Clerical, caught by the Admiral rather than by anything mechanical.
- **The engine has no authority value for "the frozen launch order says so"** (reported by the g2 implementer) — which is the actual authority behind most decisions in a delegated run.

**Crew-reported friction:**
- **g1 implementer:** the handoff named three source-resolution seams; a **fourth** existed in the test file. Suggested handoffs add "grep the tests for the same pattern too". Also: the handoff should have stated the writer module is import-safe (`__main__` guard), which is what makes a real-loader test possible — it had to read the module to establish that.
- **g1 reviewer:** handoff lacked a **Survey State Location** field (it derived the path) and did not say the change was **uncommitted working-tree state** (`git diff main...HEAD` is empty). Flagged that close criterion 4's "**both** call sites" phrasing is exactly what makes a *third* site easy to miss — then found a third site. Both gaps fixed in the g2 handoffs.
- **g2 implementer:** **test mode** was never named as a handoff field; a handoff conditional pointed at a file existing under a non-obvious name (`tests/test_write_a_skill.py`) that neither gate command runs.
- **g2 reviewer:** its first moved-install reproduction was **invalid** (the install re-created the tree at the original path); it caught and corrected this itself, and redid it two ways. Recording as a positive — a reviewer disclosing its own bad reproduction is what makes a verdict worth anything. Also measured 1196 full-suite passes where the implementer's result claimed 1195.

**What worked:**
- **The `-k` filter gate construction.** Scoping a gate postcondition to a pytest name filter exploits exit-5-on-no-match so the gate is *structurally unable* to close on an empty test set — stronger than requiring "named tests", which renaming can weaken. The Admiral independently verified at base that both filters collected 0 of 61, so neither could pass vacuously.
- **Design-it-twice at panel width.** Three opposed constraints landing independently on the same answer was worth more than any candidate's argument, and portability-first *conceding against its own constraint* (refusing to assume `$HOME` expansion it had not verified) was the single most informative moment in the run.
- **Requiring reviewers to reproduce rather than read.** Both gates' real defects were of the silent-degradation class, invisible in a diff. Both were caught by someone running something.

**Improvement signals:**
- Handoff templates should state the **reachable reply address** explicitly rather than assuming the dispatching agent's name routes. → disposition: distilled to a lesson (`sendmessage-name-in-the-launch-order-is-not-the-reachable-address`), **banked** — cannot yet tell if the aliasing is a stable harness rule or an epic-specific artifact.
- The escalation model has **no exit for a crew blocked on a Commander who is blocked on that crew.** → disposition: distilled to a lesson (`crew-blocked-on-a-commander-blocked-on-that-crew-has-no-exit`), **banked** — the crew's improvised exit was sound, but the case that matters is a crew with worse judgement in the same corner.
- A `-k`-scoped gate must always be paired with an unfiltered suite run, because the filter is **structurally blind** to anything named otherwise — confirmed twice in this run, in both gates. → disposition: distilled to a lesson (`name-scoped-test-filter-gates-are-strong-but-structurally-blind`), **banked** — the remedy is not yet clear between three candidates.
- The **IMPLEMENTER_HANDOFF template lacks a `test mode` field**, and would benefit from a "grep the tests for the same pattern" prompt when a change touches a resolution rule. → disposition: **needs human** — it is a template working copy, and a delegated run does not self-apply project doctrine.

---
