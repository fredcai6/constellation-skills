# x3 — Superpowers competitor scan: adoptable ideas for the four packages

**Excursion type:** research (external prior-art scan).
**House stance applied:** superpowers is a competitor, never an authority. Every verdict below stands on its own merit argument; "superpowers does X" is nowhere used as a reason.

---

## 1. What superpowers currently is, and what changed recently

**Superpowers** (github.com/obra/superpowers, Jesse Vincent / "obra") is a composable-skills framework + opinionated SDLC methodology for coding agents. Created Oct 2025, accepted into the Anthropic plugin marketplace Jan 15 2026, now the most-installed Claude Code plugin. It runs across many harnesses (Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI, OpenCode, etc.).

It ships ~14 skills organized as a 7-stage pipeline: **brainstorming → using-git-worktrees → writing-plans → subagent-driven-development / executing-plans → test-driven-development → requesting/receiving-code-review → finishing-a-development-branch**, plus meta-skills (writing-skills, using-superpowers) and support skills (systematic-debugging, root-cause-tracing, verification-before-completion, dispatching-parallel-agents).
- Repo tree + skill list: https://github.com/obra/superpowers/tree/main/skills

**Superpowers 5 (released 2026-03-09)** — the substantive recent shift ([blog.fsck.com/2026/03/09/superpowers-5](https://blog.fsck.com/2026/03/09/superpowers-5/), release trail [v5.0.6 2026-03-25](https://blog.fsck.com/releases/2026/03/25/superpowers-v5-0-6/)):
- **Subagent-driven development is now the default** when the harness supports subagents ("dramatically more capable than the old way").
- **Cheapest-capable-model per subagent** — implementers told to use e.g. Haiku where sufficient.
- **A "spec review" loop** — a subagent reads the planning docs for sanity/completeness before execution, to kill "TBD" sections that caused downstream failures.
- **Recursive-delegation mitigation** — subagents were spawning their own subagents; SP5 adds a guard.
- **File-size / single-responsibility as a review trigger** — "files growing large" reframed as a design smell, not style.
- Earlier 2026 releases removed the old nested subagent-review loops in favor of inline self-review to cut execution time.

**Load-bearing architectural fact:** in superpowers the **lead agent is always the dispatcher**. There is no engine/harness-level orchestrator. Parallelism is "issue N dispatch calls in one response." They *considered* a team-based controller+peer-messaging model (issue #469, opened 2026-02-13) and **closed it as "not planned," deferred until the Claude Code teams API stabilizes** (https://github.com/obra/superpowers/issues/469).

---

## 2. Per-mechanism verdicts

| # | Mechanism (source) | Package | Verdict | Merit reason |
|---|---|---|---|---|
| 1 | **`scripts/task-brief` → file; fresh implementer gets brief-path + report-path; returns only status/commits/test-summary/concerns, full report written to file** (subagent-driven-development) | A, D | **adapt** | The return-thin / write-fat discipline is good context hygiene independent of who dispatches. But note the axis mismatch: this is *agent-writes-file-for-agent*, the opposite of our A thesis (*engine emits state*). Adopt the "return only a structured summary, park the detail" contract; do not adopt file-passing as the state channel. |
| 2 | **Batched conflict surfacing: lead reads plan once, surfaces all tasks that contradict each other or Global Constraints as ONE question before execution** (subagent-driven-development) | A, C | **adopt** | Merit: collapses N mid-run human interrupts into one upfront gate; catches plan-internal contradictions before any code is written. This is exactly the "refusal carries recovery info, batched, early" ergonomic in A — and it's cheap. |
| 3 | **Global-Constraints-into-every-dispatch; "a fresh subagent needs its task, the interfaces it touches, and the global constraints. Nothing else."** | A | **already-have-stronger** | Our handoff/commander scoping already enforces minimal, explicit context per dispatch. No delta. |
| 4 | **Task-scoped review loop: rounds 1–5, resume same implementer rounds 1–3, dispatch fresh implementer on a *more capable model* rounds 4–5, park-with-ruling or escalate BLOCKED at cap** | B | **adapt (the loop-control, not the altitude)** | This is *per-task* review, not epic step-back — wrong altitude to substitute for B. But two sub-mechanics have independent merit: (a) a hard round cap with explicit adjudication (park-with-ruling / escalate) instead of unbounded retry; (b) **capability escalation on a stuck loop** rather than blind retry. Both worth lifting. |
| 5 | **Spec-review loop: subagent reads plan for completeness/sanity, flags TBD/placeholder before execution** (SP5) | C | **adapt** | An independent completeness lint of the plan before execution has merit as a cheap gate. Distinct from our C thesis — it validates a *static* plan; it is not rolling-wave. Adopt as a pre-flight linter, not as the planning philosophy. |
| 6 | **writing-plans: extremely detailed upfront, 2–5 min tasks, inline code samples; "a task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate"** | C | **already-have-stronger (philosophy) / adopt (one heuristic)** | Their plan-everything-to-fine-detail-upfront is the *waterfall* posture our C deliberately rejects (detail per slice, coarse later, regenerate). Do not adopt the posture. **Do** adopt the task-sizing heuristic: size a task as the smallest unit that carries its own test cycle and earns a fresh reviewer's gate — that's a good sizing rule *inside* a slice regardless of rolling-wave. |
| 7 | **executing-plans: "plans are neither re-read nor regenerated during execution; the same plan document guides the entire workflow"** | C | **already-have-stronger / contradiction surfaced** | This is the direct opposite of our C bet (plans regenerated, not re-read). Superpowers made a *coherent* opposite choice: static plan is consistent with their fine-grained-upfront planning. Our regeneration bet is consistent with rolling-wave. Surface the fork honestly — neither is free; theirs pays in stale-plan drift on long runs, ours pays in regeneration cost. |
| 8 | **File-structure-first; "escalate if a file outgrows its intended scope"; file-size + single-responsibility as review triggers** (SP5, writing-plans) | B | **adapt** | A *continuous, cheap* structural-drift signal (file growth, SR violations) that complements — not replaces — our epic-close architectural step-back. Merit: catches architecture rot between reviews at near-zero cost. Adapt as an inline smell check; keep the deeper step-back at epic close. |
| 9 | **dispatching-parallel-agents: lead issues multiple dispatches in one response; isolation over active management; post-hoc integration + full-suite run** | D | **skip (as inversion) / differentiator confirmed** | Explicitly *not* conductor inversion — "no engine-level orchestrator; parallel dispatch is a language-model capability." Confirms our D is a genuine differentiator. Nothing to adopt for D; their post-hoc "verify fixes don't conflict, run full suite, integrate" is table stakes we already do. |
| 10 | **Issue #469: controller-agent + peer SendMessage + shared task list for true parallel plan execution — CLOSED "not planned," deferred pending teams-API stability** | D | **skip / merit-relevant risk signal** | Not authority, but a real data point: the leading competitor reached for a teams/controller model, judged the underlying **teams API too unstable to depend on**, and backed off. Our D (engine dispatches agents) goes *further* than they were willing to ship. Proceed with eyes open — we would inherit the same API-maturity risk they cited. Worth a named risk line in the D package. |
| 11 | **verification-before-completion: run the FULL command fresh, read exit code, count failures; "skip any step = lying." Explicitly does NOT audit weakened/deleted/tautological/skipped tests or coverage adequacy** | B | **already-have-stronger / gap in theirs is our differentiator** | Their gate catches "claimed pass without running" but is, by their own docs, blind to test *adequacy*, removed tests, and tautological assertions. Our B test-honesty audit is strongest exactly where they are blind. This validates B as a real, defensible differentiator — the gap is concrete and named, not imagined. |
| 12 | **Cheapest-capable-model per subagent** (SP5) | (outside) | **already-have-adjacent** | We already run the inverse guardrail (cap subagents at opus, no Fable subagents). Same instinct, opposite failure mode they optimize for (cost) vs ours (capability ceiling). No delta. |

---

## 3. Genuinely new ideas outside the four packages (flagged for the board)

1. **Capability-escalation on a stuck bounded loop** (from #4). Most retry loops re-run the same agent at the same capability. Superpowers escalates to a *more capable model* at rounds 4–5 before hitting the cap. Generalizable pattern: *bounded retry that escalates capability, then adjudicates, rather than retrying flat then giving up.* Worth adding to our board as a loop-control primitive — applies well beyond code review (any drill/gate with a retry budget).

2. **Pre-execution plan-consistency gate as a first-class, batched, one-shot human question** (from #2/#5). Not "review the plan" generically — specifically: lint the plan for internal contradictions + completeness, and surface *all* objections in a single upfront question. A distinct ergonomic worth naming separately from the planning package.

3. **Recursive-delegation guard** (SP5). They hit subagents spawning their own subagents and had to add an explicit mitigation. Relevant to package D: if the *engine* dispatches agents, we must decide up front whether dispatched agents may themselves dispatch, and guard it — a failure mode a conductor-inversion design will meet early. Flag as a design constraint for D, not a feature to adopt.

---

## 4. Scope statement — what was and was NOT surveyed

**Surveyed (primary sources):** the obra/superpowers repo tree and README; raw SKILL.md for subagent-driven-development, executing-plans, writing-plans, dispatching-parallel-agents, requesting-code-review, verification-before-completion; the Superpowers 5 launch post (2026-03-09) and v5.0.6 release note (2026-03-25); GitHub issue #469 (agent teams, closed not-planned). Secondary commentary used only to locate these primaries.

**NOT surveyed:**
- The actual source of `scripts/task-brief` and other helper scripts (only their described behavior, from the SKILL that calls them).
- receiving-code-review, finishing-a-development-branch, brainstorming, systematic-debugging, root-cause-tracing, writing-skills full texts (read only via summaries / not fetched in full).
- Matt Pocock's skills ecosystem — that is excursion x2's scope, deliberately excluded here to avoid overlap.
- claudepluginhub.com skill pages returned HTTP 403 and could not be read; substituted with GitHub raw sources.
- Any private/Discord/community discussion, and any changes after ~2026-03-25 that are not reflected in the repo main branch as fetched.
- I did not independently verify superpowers' star counts or install-rank claims (immaterial to the verdicts).

**Contradictions surfaced, not smoothed:** superpowers deliberately holds plans *static and fine-grained* (#6, #7) — the opposite of our rolling-wave/regenerate bet in package C. Both postures are internally coherent; the fork is real and is noted rather than reconciled.
