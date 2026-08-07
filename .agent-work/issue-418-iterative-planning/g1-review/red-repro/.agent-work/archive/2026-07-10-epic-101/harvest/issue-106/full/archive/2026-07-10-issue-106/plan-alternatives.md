# Plan-alternatives (design-it-twice, plan-phase) — issue #106 gate structure

## The one thing being designed twice
The **gate structure of execute.json** — how the five launch-order deliverable classes (design, runner, scenarios, unit tests, live acceptance) decompose into gates, and specifically **how the agent-free unit tests couple to the runner code** so verification stays green at every gate boundary.

## Count and panel — surfaced choice
**Single author, 3 named candidates compared (not a parallel fan-out).** Rationale: the plan shape is heavily pre-constrained by the frozen launch order (five *named* deliverable classes, fixed sequence hint "tackle last", explicit gate-each guidance). The only load-bearing variation is tests-to-code coupling and seam ordering — comparable in one pass. Parallel fan-out for plan candidates is a **collapsed untaken road** (below). This scaling call is surfaced per the design-it-twice brief; in delegated mode the Admiral ratifies via the launch order's plan authority.

## Constraints (one per candidate)
- **A — smallest-diff / launch-order-literal:** five gates, one per named class, in the order listed.
- **B — most-testable:** five gates, tests fused to the code they cover; every gate boundary green.
- **C — best-seam-placement:** scenario-schema-first; lock the contract by a real example before the engine reads it.

## Candidates

### A — launch-order-literal (smallest-diff)
G1 design → G2 runner (all logic + live launch) → G3 scenarios → G4 unit tests → G5 acceptance+bar.
- Depth: fine. Locality: fine. Seam: adequate.
- **Testability: FAILS.** G2 ships the runner with no tests; the agent-free unit layer only lands at G4, so G2's integrate has no real green check and the runner is built test-after — global-orchestrator forbids test-after where a test surface exists. A known-untested window spans G2–G3. **Rejected.**

### B — most-testable (RECOMMENDED)
- **G1 — Design gate (reasoning gate):** design-it-twice on the runner contract; converge (my latitude); output the contract note. No crew.
- **G2 — Runner core + agent-free unit tests (crew, TDD):** the runner's PURE logic — scenario schema parse/validate, check-execution engine, N-of-M verdict math, temp-install planning, headless argv construction (reusing `build_crew_argv` form), and a **dry-run mode** — built test-first with `tests/test_run_skill_eval.py` (agent-free, canned fixtures). Closeout: unit layer + full suite green.
- **G3 — Runner live-launch wiring (crew):** the real `claude -p` subprocess launch + temp-install-to-target + transcript capture + corpus-provenance assertion, layered on the tested core behind an **injectable subprocess seam**. Closeout: **fake-subprocess end-to-end tests** drive the whole run (temp-install → launch-seam → transcript → checks → verdict) through pass AND fail transcripts with NO real agent — so the live IO path is genuinely *tested* (not left untested and relabeled), honestly closing the window the cold critic flagged. The *real* agent launch is proven at G5.
- **G4 — Pilot Euler scenarios (crew):** 2–3 graded `evals/<name>/` (fixture setup + task prompt + mechanical checks) + `evals/README.md` (situational bar + named next scenario). Closeout: scenarios parse/validate under the runner in dry-run.
- **G5 — Live acceptance + falsification + bar (reasoning/ops gate):** ONE pilot executed for real, N-of-M, verdict + process-check outputs pasted; a broken variant must fail its checks. Honest-null path if the environment blocks it. No crew (I drive the ops + paste evidence).
- Depth: high (runner core hidden behind a dry-run seam). Locality: contained. Seam: the dry-run/live boundary is drawn exactly where the unit tests want it — every pure pathway is falsifiable agent-free. Testability: **best** — green at every boundary; "unit tests" class co-delivered with the runner core in G2; "runner" class spans G2 (core) + G3 (live wiring); all five classes present.

### C — scenario-schema-first (best-seam-placement)
G1 design → G2 scenario schema + one real Euler scenario authored to it + schema tests → G3 runner engine (parse/check/verdict) run against G2's scenario in dry-run → G4 remaining scenarios → G5 acceptance+bar.
- Depth: fine. Locality: fine. Seam: elegant — the scenario schema is locked by a real example before the runner reads it.
- Testability: good but **weaker at G2**: the checks can't be *exercised* until the runner engine exists (G3), so G2's falsification is schema-shape-only. Front-loads scenario authoring before execution feedback.

## Output — recommendation
**Candidate B (most-testable).** It keeps every gate boundary green (a hard requirement from global-orchestrator's "sequence gates so verification stays green" and the "no known-red window" plan-smell rule), honors test-led doctrine by fusing the agent-free unit layer to the runner core it covers, and still delivers all five named classes. C's schema-first seam is attractive but front-loads un-executable checks; B absorbs C's benefit anyway because the **G1 design gate already fixes the scenario schema**, so the runner and scenarios are both authored against a frozen contract. A is rejected outright (test-after window).

Hybrid taken from C: G1's contract note fixes the scenario schema first (C's seam idea) — so B gets schema-first *specification* without C's premature scenario authoring.

## Untaken-road record (loud skips)
- **Parallel fan-out for the three plan candidates** — collapsed to single-author comparison. Reason: plan shape is pre-constrained by the frozen launch order's five named classes; the sole real variable (tests-to-code coupling) is comparable in one pass. Not judged worth 3 parallel Agent-tool dispatches against the context/usage budget reserved for the live acceptance runs.
- **A separate 6th gate splitting "unit tests" from "runner core"** — not taken. Reason: the runner's pure logic and its unit tests are one TDD module (the interface is the test surface); splitting them manufactures exactly the test-after window candidate A was rejected for.

## Panel-vs-single record
Single author, 3 candidates compared — because the call is fairly-easy and heavily pre-constrained by the frozen launch order. Surfaced here for the Admiral to overturn at ratification; not made silently.
