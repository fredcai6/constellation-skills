# Ideas Board — `explore-design-thrust`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed. Keep it current — it is what survives a reopen cascade.

## The point

DRAFT (from the human's opening statement, 2026-07-24 — to be sharpened by cycle-1 starting questions):
A melange of related process concerns, suspected to share one unifying design thrust:

1. **Agents over-read structure.** The engine exists so agents don't have to think about workflow mechanics, yet agents read the raw machinery (whole spine.json, schema docs) anyway. Effort should concentrate on the actual hard problems, not on ingesting scaffolding. (Live evidence: this very session read all 270 lines of spine.json to find two condition ids. Related: #217 "reduce agent read", #220 CLI ergonomics.)
2. **Design cycles pretend the plan is perfect.** Current flow spends heavily producing a "definitely perfect (wink)" plan, then executes it. Missing: a gradation of fixedness — "this part is settled" vs "this is the current guess, revisit allowed." (Related: #172 "revisit epic planning".)
3. **Prototyping is weak as an information tactic.** Simple versions of ideas should be built to buy information; a null result means "not immediately right," not "wrong." Premature null verdicts observed. (Related: #224 "encourage more prototype spike forward exploration"; scoped-nulls doctrine exists but may not be reaching the prototyping moment.)
4. **Vertical slices arrive too late.** Slice-at-a-time is currently pushed at the implementer level; planning AND prototyping should themselves proceed one vertical slice at a time. (Related: #172, #171, #219 thread 2 — issues/specs ↔ architecture interplay.)

Suspected connection (hypothesis, untested): all four are symptoms of a waterfall-shaped pipeline — full plan → full execution — where the fix is an iterative core: plan/prototype/execute per slice, with explicit confidence grades on design decisions, and structure delivered to agents just-in-time instead of read wholesale.

**Done feels like** (human, cycle-1 q-a, 2026-07-24): agent picks up an epic and works it slice by slice — plan the slice, prototype its risky unknown, execute, then commit to the next slice — with design decisions carrying explicit settled-vs-guess markers so revisiting a guess is a normal move, and agent context spent on the problem, not the scaffolding. **With the human's amendments:**
- **Vertical slices are a tool, not dogma.** The real ask is multidimensional problem decomposition, exploiting multiple agents to break problems apart; slices are one decomposition in the toolbox, and the system must be *able* to work that way, not forced to.
- **Two-phase shape: solve forward, then step back.** During the epic, solve issues in a cycle-ish way. At epic end, a deliberate step-back pass: (1) given the way this was actually implemented, what refactorings should happen — an *architectural-level* refactor review, above the per-diff view today's reviewer has (→ #216); (2) are the tests honest, complete, and covering integration/performance (→ #225, #171)?
- **The overarching connection (human's own framing):** slice-by-slice behavior is now reliable; the system must learn to *take a step back* — tackle problems more holistically. Context management is part of that step-back capability.

## Kill condition

(human, cycle-1 q-b, 2026-07-24): **There is no global kill condition, because there is no load-bearing unification.** The concerns are grouped because they arrived together and are loosely related. "The grand unifying theory is a fiction — just a viewpoint": if synergies exist, take them; if not, work the concerns as a loosely correlated issue set. No individual concern is unwarranted merely because it fails to attach to a unifying theory. Individual ideas die on their own merits only.

## Current candidates

Consolidated from cycle-1 shotgun (human reviewed all 28; 1–21 accepted as straightforward; see Verdicts/Rejected for the rest). Four packages:

**A. Engine answerability quick-wins (trivial batch — "one fell swoop" candidate).** *(cycle-2 additions from x3/x4: launcher resolve-at-install (the `py` hardcode fix, x4-assessed, connects #220); wire CI on the existing 906-test suite + coverage floor; close the git-collector test gap + glob/cascade property tests; #205 atomic-meta fix; batched plan-conflict pre-flight (idea 29); return-thin/write-fat dispatch contract (idea 31); stale doc-drift one-liner in run_skill_eval.py docstring.)* The over-read evidence (x1) shows the worst scaffolding reads are the engine's fault: terse REFUSED with no recovery hint, truncated `current --verbose`, no `explain`/unblock affordances. Package: `explain` verb (idea 2), recovery-hint text on every REFUSED, fix truncation, engine-output-only doctrine line (idea 1), plus small template/doctrine edits — three-valued prototype verdicts (12), prototype-as-primary-source worktree disposition (28, human: keep prototype as worktree reference until done), understand→prototyper handoff seam (27 reframed), guess-grading in plan templates (6+7+10 merged: fixed/guess/placeholder tags + guess ledger + provenance). Absorbs #217, #220; touches #224.

**B. Step-back phase (design-heavy).** Epic retrospect at closeout: architectural refactor review (20) + refactor-spawned cleanup gates (21) + test honesty audit (20) + map-diff fed by cartographer (22) — with 22 reframed by the human: this is where the unused **scout** skill should loop in practically; the edge exists because we don't use information we already have. Absorbs #216, #225, #171; depends on #156 (initial self-map). 

**C. Slice-wise planning (design-heavy).** Rolling-wave planning (8) + plan expiry (9) + decomposition menu (16) + multi-agent decomposition probe (17) + slice-shaped specs (18) + wave=slice (19) + **regenerate-don't-reread (25, human: full agreement)** — human's elaboration folded in: agents should be told "the current state and the thing to do," not the history of paths not taken; negative space (what NOT to redo) is the duty of higher-tier agents, surfaced only where it prevents repeating a mistake. Absorbs #172; relates #215.

**D. Conductor inversion arc (the deep thread).** Human names this the core: "the way we're using agents to run the engine is fundamentally backwards — the engine should be running the agents," bounded by what the subscription harness allows. Conductor-lite (23) — engine dispatches step-back reviewers at closeout — is the first probe; full arc is #139. The more dispatch moves into the engine, the better.

Enforcement follow-ons (sequenced after their mechanisms): scaffolding gauge ratio (3), structure-blindness eval (5), spike budget (13), rail-ify remaining skills (4), idea nursery (15), spike-inside-interrogation (14 — largely satisfied by A's handoff seam).

## Cycle-1 shotgun (raw one-liners, 2026-07-24)

Wild entries sanctioned; culls at consolidation keep their reasons. Clusters: [read] over-read structure, [fix] fixedness grading, [proto] prototyping-as-information, [decomp] decomposition/slices, [back] step-back phase, [wild].

1. [read] **Engine-output-only rule** — agents may consume engine state ONLY via engine stdout; opening spine/cycle JSON is a lintable violation.
2. [read] **`explain` verb** — the engine answers questions about its own state ("what's left on gate X?", "what are the condition ids?") so there is never a reason to open the file.
3. [read] **Scaffolding budget on the gauge** — the context gauge (#178) tracks tokens spent on scaffolding vs problem; exceeding a ratio trips a warning.
4. [read] **Rail-ify the skills** — move remaining mechanism prose out of SKILL.md bodies into engine-served just-in-time strings (generalize the #140 rail pattern; the engine already proved it works).
5. [read] **Structure-blindness eval** — a per-skill eval (#136 style) that FAILS if the agent reads engine internals during a run; makes over-read measurable and regression-proof.
6. [fix] **Confidence-tiered decisions** — every plan/spec decision tagged `fixed | working-guess | placeholder`; revisiting a guess is free, revisiting fixed requires a reopen with reason.
7. [fix] **Guess ledger** — plans carry an explicit "things we are knowingly guessing" table; each guess names the cheapest experiment that would settle it.
8. [fix] **Rolling-wave planning** — plan the current slice in detail; later slices exist only as sketches; detail crystallizes at the last responsible moment.
9. [fix] **Plan expiry** — plan sections beyond the current slice are stale-by-default; the executing agent re-affirms them against current reality rather than obeying.
10. [fix] **Decision provenance** — each fixed decision records WHY it is fixed (human ruled / measured / inherited constraint), so agents know what is actually load-bearing vs merely written down.
11. [proto] **Prototype-gate on load-bearing guesses** — a `working-guess` that the current slice leans on triggers a prototyper dispatch before implementation, by rule.
12. [proto] **Three-valued prototype verdicts** — pass / fail / **"not immediately right"** (parked with a named revive condition) — kills premature nulls structurally.
13. [proto] **Spike budget per epic** — each epic reserves N cheap spikes; an epic that used zero spikes is flagged (we guessed without buying information).
14. [proto] **Spike inside interrogation** — commanders may prototype during the understand step (per #224's hunch that exploration belongs in interrogation, not after it).
15. [proto] **Idea nursery** — a durable board of parked "not-yet-right" ideas with revive conditions, swept at epic close (the cull-that-can-come-back, made a first-class artifact).
16. [decomp] **Decomposition menu** — epic planning explicitly CHOOSES a decomposition dimension (vertical slice / risk-first / data-flow / interface-first) instead of defaulting; slices as tool, not dogma.
17. [decomp] **Multi-agent decomposition probe** — N agents each propose a DIFFERENT decomposition of the same epic; human picks or hybridizes (design-it-twice applied to decomposition itself).
18. [decomp] **Slice-shaped specs** — DESIGN_SPEC carries a fixed core + per-slice open-question sections, so planning detail is per-slice, not epic-uniform.
19. [decomp] **Wave = slice** — to-issues cuts so each admiral wave IS one vertical slice through the stack, making plan→prototype→execute per slice the natural rhythm.
20. [back] **Epic retrospect gate** — mandatory closeout step: architectural refactor review (#216) + test honesty audit (#225/#171) run over the WHOLE epic diff, above the per-issue reviewer's altitude.
21. [back] **Refactor-spawned gates** — the refactor reviewer's verdict can append N cleanup gates to the run mid-flight (from #216), so step-back findings become work, not notes.
22. [back] **Map-diff retrospect** — cartographer diffs the architecture map at epic close (#156 prerequisite); the diff feeds the refactor review with what structurally changed.
23. [wild] **Conductor inversion lite** — the step-back phase is conducted BY the engine (#139): closeout dispatches the reviewers itself instead of trusting doctrine prose to make an agent do it.
24. [wild] **Plans as calibrated bets** — decisions carry literal confidence numbers; the system measures calibration across epics (are our "90% sure" decisions right 90% of the time?).
25. [wild] **Regenerate-don't-reread** — after each slice, the plan for the next slice is regenerated fresh from board+map+diff; nothing stale exists to be obeyed.

From excursion x2 (Pocock deltas, added post-dispatch):

26. [proto] **Task-type excursion** — a fourth off-ramp type: manual do-work that unblocks a decision (provision access, sign up, move data) — the one excursion that *does* rather than decides.
27. [proto] **Commander prototype off-ramp** — port the explorer's excursion machinery (brief, background dispatch, on-ramp) into the Commander's understand step, so mid-interrogation spikes are structured, not informal (#224's concrete gap).
28. [proto] **Prototype-as-primary-source disposition** — "captured to throwaway branch + pointer on the issue" as a first-class prototype disposition, alongside deleted/absorbed/parked.

From excursion x3 (superpowers scan, cycle 2, adopt-on-merit):

29. [fix][read] **Batched plan-conflict pre-flight** — lint a plan for internal contradictions + completeness (TBD/placeholder hunt) and surface ALL objections as ONE upfront question before execution (revives #219's dormant pre-flight-scan thread).
30. [wild] **Capability-escalation loop primitive** — any bounded retry loop escalates model capability before its cap, then adjudicates (park-with-ruling / escalate), never flat-retries to exhaustion.
31. [read] **Return-thin/write-fat dispatch contract** — subagents return only a structured summary (status/commits/tests/concerns); full detail goes to a file. Context hygiene for every dispatch.
32. [wild] **Recursive-delegation guard (D constraint)** — conductor-inversion design must decide upfront whether engine-dispatched agents may themselves dispatch, and enforce it.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Ideas 1–21 accepted as straightforward | Human review of one-liners; NOT yet designed or sized | cycle-1 consolidation |
| Over-read is substantially an engine-answerability problem | 6 recent transcripts sampled; archive + f1brainz NOT examined | excursion x1 |
| Pocock July pivot ~80% already embodied; 3 deltas real | Primary SKILL.md sources; the exact #224 video NOT watched | excursion x2 |
| 27 reframed: understand→prototyper handoff seam, NOT heavyweight excursion machinery in commander | Human ruling: excursions must stay cheap | cycle-1 consolidation |
| 22 reframed: step-back is where the unused scout skill loops in practically | Human ruling; scout NOT yet exercised in anger — that test still pending | cycle-1 consolidation |
| Engine robustness fear falsified: 906 tests / 91% / every verb exercised | Line+verb coverage measured by command; assertion QUALITY not audited; git-collector + glob/cascade residue named | excursion x4 |
| Full per-skill behavioral-eval matrix: not worth building as a gate now; eval-on-change instead | Cost/governance analysis; does NOT kill #136's per-skill goal — re-scopes it to on-change | excursion x4 |
| Testability cross-cutting constraint RESOLVED near-term: CI + launcher-at-install + eval-on-change | Near-term plan only; long-term skill-eval maturity NOT settled | cycle-2 consolidation |
| Package C fork on record: static-fine-grained plans (superpowers) vs rolling-wave/regenerate (ours) | Both coherent; NOT adjudicated — carry to critic/spec | excursion x3 |

## Open threads

- **Cross-cutting constraint (human, cycle-2): testability rides along everything we pick.** The engine itself must be extremely robust at minimum. If skills-as-tested-artifacts proves impractical near-term, the weekly iterative cleanup cadence is an acceptable fallback — but anything cheap that validates "what we're doing makes sense" is wanted now.
- **Excursion x3 LANDED** (2026-07-24, result: `excursions/x3-superpowers-RESULT.md`, registry-verified). Superpowers 5 (2026-03) scanned against the four packages, adopt-on-merit only. Adoptables: **batched plan-conflict surfacing** (lint the plan for internal contradictions + completeness, surface ALL objections as ONE upfront question — matches #219's dormant "pre-flight plan-conflict scan" thread; feeds A+C); **capability-escalation on stuck bounded loops** (retry escalates model capability before adjudication/cap, instead of flat retry — general loop-control primitive); **return-thin/write-fat dispatch contract** (subagent returns only structured summary, detail parked to file); **task-sizing heuristic** (smallest unit carrying its own test cycle + worth a fresh review gate — useful inside a slice); **file-growth/single-responsibility as continuous inline smell** (complements, doesn't replace, epic-close step-back). **Honest fork surfaced for C:** superpowers holds plans *static and fine-grained upfront* — the coherent opposite of our rolling-wave/regenerate bet; theirs pays in stale-plan drift, ours in regeneration cost. **For D:** they reached for a controller/teams model and closed it "not planned" citing teams-API instability — our conductor inversion goes further than they'd ship; named risk. Also a D design constraint from their scar tissue: decide upfront whether engine-dispatched agents may themselves dispatch (recursive-delegation guard). **B validated as differentiator:** their verification gate is, by their own docs, blind to test adequacy/tautology — exactly where our test-honesty audit is strongest. Scoped nulls in the result file.
- **Excursion x4 LANDED** (2026-07-24, result: `excursions/x4-testability-RESULT.md`, registry-verified, all counts command-derived). **Headline: the engine is already the robust part** — 906 tests green in ~30s, 91% line coverage on checklist_engine.py, EVERY verb exercised; the "engine must be extremely robust" constraint is largely already met (scoped: line/verb coverage measured, assertion *quality* not audited). The real gaps, ranked: (1) **no CI — 906 green tests gate nothing** (~1hr GitHub Actions fix, grade A, do first; verify windows-latest has git-bash before building); (2) **launcher portability: recommend resolve-at-install** — installer probes py→python3→python once on the real host and stamps the resolved interpreter into installed SKILL.md copies; zero per-invocation token burn; env-var and wrapper options assessed and rejected for skill bodies (grade A-); (3) engine hardening residue: the impure git collector `_collect_changed_files` is the top untested surface, + property tests for glob/reopen-cascade (B+); (4) **full per-skill behavioral-eval matrix: honestly NOT worth building now** (grade D as a gate — 13.5–30+min/run makes it a batch instrument; governance already says "curator instrument, not a merge gate"); instead **eval-on-change**: one scenario per orchestrator-tier skill when it's touched anyway, building the scripted-principal seam (#136) once, on first need; weekly curator cadence + green suite is genuinely good enough for the rest; (5) #205 atomic-meta fix, cheap (B). Prior art confirms the field's three-layer model (unit / behavioral / graded) — constellation matches the shape; the gap is *enforcement*, not methodology.

- Which open issues does this thrust absorb vs leave standalone? Candidates: #217, #224, #172, #171, #216, #225, #219(2), #215.
- ~~Is there ONE unifying thrust?~~ Answered q-b: unification is a viewpoint, not a premise; take synergies where real.
- **Excursion x1 LANDED** (2026-07-24, result: `excursions/x1-overread-RESULT.md`, registry-verified, counts command-derived): sampled the 6 most-recent transcripts; the 3 engine-driven runs averaged **~884 scaffolding lines ≈ ~8,800 tokens/run** of structural over-read. Ranked causes: (1) **engine UX gaps drive the worst reads** — an agent hit a mis-applied block, got terse REFUSED with no recovery hint, read `checklist_engine.py` SOURCE twice hunting for an unblock verb, then **hand-edited spine.json via inline Python to flip status** (the exact bypass doctrine forbids); (2) `current --verbose` output truncates mid-sentence, forcing fallback to raw spine.json reads (2 sessions, same pattern); (3) template/reference reads are mostly by-design, NOT the real problem. Scoped null: sample = 6 recent transcripts only; archive and f1brainz not examined. Implication: over-read is substantially an **engine answerability/ergonomics** problem (supports ideas 1–2, connects #220), not just agent discipline.
- **Excursion x2 LANDED** (2026-07-24, result: `excursions/x2-pocock-RESULT.md`, registry-verified): Pocock's July-2026 "wayfinder" pivot (spike-forward exploration) is ~80% already embodied in constellation, often more strictly (mechanical gates, durable dispatch, design-it-twice). Scoped null: the exact #224 video wasn't watchable; worked from his actual SKILL.md sources on GitHub + his own posts. Two genuine deltas: (a) a **task-type excursion** (manual do-work that unblocks a decision — provision access, move data) which constellation lacks; (b) **Commander interrogation has no real prototype off-ramp** — only the informal code-answers convention and feasibility probe; explorer's excursion machinery doesn't reach the understand step. Minor delta: (c) prototype disposition "captured-to-throwaway-branch + issue pointer" as a first-class flavor (Pocock keeps prototypes as primary sources; we default delete-or-absorb). Notable contradiction surfaced: Pocock reversed his June spec-first, anti-spike stance within ~6 weeks — #224 tracks the July pivot.

## Rejected ideas (with reasons)

- **24 Plans as calibrated bets** — culled by human at cycle-1 consolidation: no actionable mechanism under the current harness. Would revive if we ever accumulate per-decision outcome metrics at volume.
- **26 Task-type excursion** — parked, not rejected: motivation (decision blocked on a real-world *action*, often human-only) is mostly covered by escalate-to-human. Would revive if manual-unblock steps start appearing untracked in runs.
- **27 (original framing) heavyweight excursion machinery inside commander** — excursions must stay cheap; survives only as the understand→prototyper handoff seam (package A).

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun | 28 one-liners across 6 clusters; 2 background excursions (over-read measurement, Pocock/#224) | Human reviewed all 28: 1–21 straightforward, 24 culled, 26 parked, 27 reframed cheap, 22 reframed to loop in scout, 25 strongly endorsed. Consolidated into 4 packages: A engine-answerability quick-wins, B step-back phase, C slice-wise planning, D conductor-inversion arc. Next move: human decides — down-select / cycle 2 / converge. |
| 2 | refine (human-directed) | 2 excursions: x3 superpowers scan, x4 testability; py-hardcode + testability constraint fed in | x3: ideas 29–32 added, C fork surfaced (static vs regenerate), D risk + recursive-delegation constraint, B validated as differentiator. x4: engine already robust (fear falsified); real gaps = CI enforcement + launcher-at-install + small hardening; eval matrix honestly declined, eval-on-change instead. Package A grew into a well-evidenced ~10-item batch. B/C/D unchanged in shape, richer in critic material. Awaiting human: converge / another cycle / down-select. |
