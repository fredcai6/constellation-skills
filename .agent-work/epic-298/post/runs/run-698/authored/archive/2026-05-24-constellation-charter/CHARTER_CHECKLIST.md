# Charter Checklist: F1Brainz Constellation Context

## Allowed writes

```text
.agent-work/2026-05-24-constellation-charter/CHARTER_CHECKLIST.md
.agent-work/CHARTER_OPEN_QUESTIONS.md
docs/agents/ORCHESTRATOR_CONTEXT.md
docs/agents/CREW_CONTEXT.md
docs/agents/GLOSSARY.md
```

## Run state

**Work ID:** `2026-05-24-constellation-charter`  
**Charter scope:** Whole repo  
**Compile mode:** final  
**Current gate:** Gate 6 (Closeout)  
**Current next question:** n/a — final compile complete  
**Why this question matters:** n/a  
**Recommendation/default:** n/a  
**Waiting on user:** no

## Scales

**Quality:** `strong | usable | weak | unresolved | not-material`  
**Authority:** `user decision | accepted default | unconfirmed default | repo artifact | assumption`  
**Posture:** `rigorous-default | relaxed | strengthened | mixed | not-applicable`  
**Projection:** `orchestrator | crew | both | glossary | checklist-only`  
**Projection reason:** `planning/framing | gating/evidence | authority/scope | implementation | verification | review/blocking | stop/report | terminology | local traceability`

---

## Gate 0: Bootstrap — COMPLETE

**Scope:** Whole repo.  
**Charter trigger:** Brownfield; capturing `docs/PROJECT_PHILOSOPHY.md` and `docs/AGENT_GUIDE.md` so those can be reduced or deleted.  
**Authoritative references:** `docs/PROJECT_PHILOSOPHY.md`, `docs/AGENT_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/artifact_policy.md`, `README.md`, `CLAUDE.md`.  
**Exemplars:**
- Code shape: `src/evo_predictor/scorer.py`, `src/evo_predictor/data_adapter.py` (DB-only, typed, fail-fast)
- Test style: `tests/unit/evo_predictor/`, `tests/regression/`
- Documentation: `docs/PROJECT_PHILOSOPHY.md` (principles), `docs/AGENT_GUIDE.md` (workflow)
- Workflow: Cautious with worktree + gated breakdown comment + subagent review
- Review evidence: Subagent reviewer blocker list (from AGENT_GUIDE §Reviewer prompts)

---

## Gate 1: Operating Context — COMPLETE

**Project type:** F1 race prediction research tool (Python, SQLite, PyTorch/ML).  
**Users:** Developer + AI agents working in the repo.  
**Output authority:** Predictions = user-facing probabilistic claims; DB = canonical record; artifacts (reports, manifests) = derived canonical baseline when promoted.  
**Failure consequence:** Wrong (silent bad predictions), stale (docs drift from code), misleading (silent fallback masks missing data), unreproducible (non-deterministic training or broken artifact chain), maintenance erosion (untracked technical debt).  
**Execution contexts:** data pipeline, analysis, test infrastructure, exploratory.

| Subsystem | Rigor profile | Execution context | Relaxed rules | Strengthened rules | Reason |
|---|---|---|---|---|---|
| whole repo | rigorous durable system | analysis + data pipeline | none | DB-only data access; explicit compromise tracking | predictions influence real decisions; data silences are correctness bugs |
| evo_predictor | rigorous durable system | analysis | none | calibrated evaluation against stable baselines | probabilistic claims need stable metrics |
| physics | rigorous durable system | analysis | none | truth-anchored tests (L1–L4); units/bounds explicit | physics outputs feed downstream predictions |
| data layer | rigorous durable system | data pipeline | none | none | DB is single source; schema is authoritative |
| exploratory (notebooks) | pragmatic internal tool | exploratory | test-led not required | none | not promoted; machine-checkable evidence still preferred |

---

## Gate 2: Engineering Rubric — COMPLETE

### Axis 1: Correctness posture → D (high assurance)

**Default:** C (correctness before speed for promoted behavior)  
**Cost:** Slower; more upfront test/evidence design  
**Decision:** D — explicit invariants, negative cases, regression evidence for all promoted paths  
**Evidence:** Test suite green; regression fixtures; calibrated metrics for evo  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Verify Behavior)

### Axis 2: Canonical inputs → D (DB as single canonical source)

**Default:** C  
**Strengthened:** Analysis code MUST read from the DB. No FastF1 calls from analysis/scorer/predictor/adapter code.  
**Scenario:** Analysis reads FastF1 at runtime → results are unreproducible from a clean DB snapshot  
**Decision:** D — canonical input with validation, provenance, conflict handling  
**Evidence:** No FastF1 import in analysis code; reviewer blocker enforces this  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §The Database)

### Axis 3: Evidence and verification → C/D (automated + regression)

**Default:** C  
**Decision:** C for logic changes (reusable automated tests); D for evo (regression suites + calibration metrics)  
**Evidence:** `pytest tests/unit/...` green; integration tests for cross-component; regression/known-answer for physics and evo  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Verify Behavior; AGENT_GUIDE.md §Verify by region)

### Axis 4: Simplicity → C (small composable units, explicit seams)

**Default:** C  
**Decision:** Accept — small composable functions; one concept per unit; seams obvious  
**Evidence:** New modules follow existing pattern (scorer.py, adapter.py shape)  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Keep Structure Simple)

### Axis 5: Interface contracts → C/D (strict at meaningful boundaries)

**Default:** C  
**Strengthened at meaningful boundaries:** type hints, named params, explicit validation with field+expectation+actual in exceptions  
**Decision:** C for internal helpers; D for public module boundaries  
**Evidence:** Signature shape; validator raises descriptively  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Prefer Explicit Contracts)

### Axis 6: Data semantics → D (unambiguous identity, units, missingness)

**Default:** C  
**Strengthened:** session/season/round/driver/constructor semantics explicit; missingness intentional not guessed; time-dependent lookups state whether fallback allowed  
**Decision:** D — ambiguous identity/units/missingness blocks changes  
**Evidence:** Schema; test fixtures; no silent substitution  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Data Semantics)

### Axis 7: Architecture boundaries → D (deliberate approval + doc update)

**Default:** C  
**Strengthened:** DB is data; physics is physics; evo is evo — crossing boundaries requires explicit approval and doc update  
**Decision:** D — boundary changes require deliberate approval and architecture doc update  
**Evidence:** No cross-boundary imports without explicit design; ARCHITECTURE.md updated  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Keep Structure Simple; ARCHITECTURE.md)

### Axis 8: Failure behavior → C/D (fail fast, fail clear)

**Default:** B  
**Strengthened:** Validate inputs at public AND meaningful internal boundaries; exceptions name field+expectation+actual; silent continuation on invalid input is a defect  
**Decision:** C/D — raise; return status at important boundaries; no silent fallback  
**Evidence:** Descriptive exceptions in code; reviewer blocker for silent fallback  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Fail Fast; AGENT_GUIDE §reviewer prompt)

### Axis 9: State and side effects → C (explicit, testable stateful boundaries)

**Default:** B  
**Decision:** C — stateful DB writes go through explicit methods; side effects obvious and contained  
**Evidence:** DB writes only via DatabaseManager methods; no hidden state mutation  
**Authority:** repo artifact (ARCHITECTURE.md; AGENT_GUIDE)

### Axis 10: Performance and resource posture → B (avoid wasteful; no strict budgets)

**Default:** B  
**Decision:** Accept B — no explicit performance budgets; avoid obviously wasteful behavior; rate-limiting on data collection (inter-session delay, rate-limit detection)  
**Authority:** unconfirmed default (no explicit performance rules in philosophy docs beyond rate-limiting)

### Axis 11: Documentation posture → C/D (freshness is review-blocking)

**Default:** C  
**Strengthened:** If docs disagree with code or tests, code and tests win; stale doc fixed in same issue or follow-up issue before close; command-heavy docs need `Last verified` date  
**Decision:** D — documentation freshness review-blocking for changes that alter ownership, interfaces, data flow, or failure meaning  
**Evidence:** `Last verified` dates present; reviewer blocks stale docs  
**Authority:** repo artifact (AGENT_GUIDE.md §Scope; reviewer prompt)

### Axis 12: Dependencies → C (explicit justification + review evidence)

**Default:** B  
**Strengthened:** New dependencies need explicit justification and review evidence  
**Decision:** C  
**Authority:** unconfirmed default (no explicit policy in philosophy docs but aligns with explicit-contracts tenet)

### Axis 13: Security/privacy → B (local tool; protect basics)

**Default:** B  
**Decision:** Accept B — local analysis tool; protect secrets and private data by default; no public API exposure  
**Authority:** accepted default

### Axis 14: Generated artifacts → C (derived; edit sources or regenerate)

**Default:** B  
**Strengthened:** Artifact policy in `docs/artifact_policy.md`; gold cycle artifacts have defined promotion path; ML weights not committed; reports committed when canonical  
**Decision:** C — generated artifacts are derived; edit sources or regenerate; manifests must be repo-relative  
**Authority:** repo artifact (docs/artifact_policy.md)

### Axis 15: Compromise/debt → C (explicit, issue-backed)

**Default:** B  
**Strengthened:** Compromises must be explicit and issue-backed with: reason, scope, exit condition, owner; untracked compromises = process failure  
**Decision:** C — any violation of tenets needs a GitHub issue with reason + exit path when introduced  
**Authority:** repo artifact (PROJECT_PHILOSOPHY.md §Compromises Must Be Explicit)

---

## Gate 3: Implementation Conventions — COMPLETE

| Convention | Rule | Status |
|---|---|---|
| Python invocation | `py` not `python` (Windows Python Launcher) | rule |
| TDD for logic changes | Test first, fail for right reason, then implement; no impl-only logic commits | rule |
| Workflow selection | Quick (single region, human in loop, clear rollback) vs Cautious (arch/schema/multi-region/risky) | rule |
| Branch requirement | Work on a branch; Cautious requires dedicated worktree | rule |
| Issue linkage | Cautious commits must reference issue number | rule |
| Gated breakdown | Cautious: post ordered-gate comment to issue before code | rule |
| Worktree path | `.claude/worktrees/issue-NNN-short-description` | rule |
| Subagent review | Final gate of every Cautious issue; reviewer must not have written the change | rule |
| Region verification | Run full region suite; multi-region = all affected suites | rule |
| Commit state | Commit only after verification passes | rule |
| Push/PR | Ask first unless user explicitly asked to publish | rule |
| Merge/delete/close | Ask first | rule |
| Docs/code conflict | Code and tests win; fix stale doc same issue or create follow-up before closing | rule |
| Success criteria | State done criteria before writing code | rule |
| Scope discipline | Touch only what the task requires; do not opportunistically refactor | rule |
| Config placement | Tunable parameters in config/named constants; not inline | rule |
| Physics tests | Truth-anchored at highest applicable level (L1–L4) | rule |
| DB-only analysis | No FastF1/API calls from analysis/scorer/adapter/predictor code | rule |
| Missingness | Represent intentionally; no silent guessing or substitution | rule |
| Exception shape | Name field + expectation + actual value | rule |

---

## Gate 4: Contradiction Pass — COMPLETE

No contradictions found. All axes resolved from source docs. No weak or unresolved material decisions remain.

---

## Gate 5: Context Compile — COMPLETE

All decisions compiled into ORCHESTRATOR_CONTEXT.md, CREW_CONTEXT.md, GLOSSARY.md.

---

## Gate 6: Closeout — COMPLETE

- [x] All gates complete.
- [x] No `weak` or `unresolved` material decisions remain.
- [x] Contradiction pass complete.
- [x] `docs/agents/ORCHESTRATOR_CONTEXT.md` updated.
- [x] `docs/agents/CREW_CONTEXT.md` updated.
- [x] `docs/agents/GLOSSARY.md` updated.
- [x] Shared project invariants with `both` projection have role-specific wording.
- [x] Crew context contains every project invariant that can change implementation, verification, review/blocking, or stop/report behavior.
- [x] Orchestrator context contains every project invariant that changes framing, gate design, authority/scope decisions, evidence selection, or stop/ask behavior.
- [x] Crew context verification rules are universal; area-specific commands are handoff requirements.
- [x] Handoff-only details not placed in durable Crew context.
- [x] `.agent-work/CHARTER_OPEN_QUESTIONS.md` absent (no open questions).
- [x] This checklist retained.

---

## Material Decisions

| ID | Gate | Decision | Quality | Authority | Posture | Projection | Projection reason |
|---|---|---|---|---|---|---|---|
| D-001 | 2 | DB is single canonical source for all analysis | strong | repo artifact | strengthened | both | gating/evidence (orch), review/blocking (crew) |
| D-002 | 2 | Correctness: high assurance (D) | strong | repo artifact | strengthened | both | gating/evidence (orch), implementation (crew) |
| D-003 | 2 | Evidence: automated tests + regression suites | strong | repo artifact | strengthened | both | gating/evidence (orch), verification (crew) |
| D-004 | 2 | Interface contracts strict at public + meaningful internal boundaries | strong | repo artifact | strengthened | crew | implementation |
| D-005 | 2 | Data semantics: explicit identity, units, missingness | strong | repo artifact | strengthened | both | gating/evidence (orch), review/blocking (crew) |
| D-006 | 2 | Failure: fail fast, fail clear; no silent fallback | strong | repo artifact | strengthened | both | gating/evidence (orch), review/blocking (crew) |
| D-007 | 2 | Compromise/debt: explicit + issue-backed always | strong | repo artifact | strengthened | both | authority/scope (orch), stop/report (crew) |
| D-008 | 2 | Documentation freshness review-blocking when meaning changes | strong | repo artifact | strengthened | both | gating/evidence (orch), review/blocking (crew) |
| D-009 | 2 | Architecture boundaries require deliberate approval + doc update | strong | repo artifact | strengthened | orchestrator | authority/scope |
| D-010 | 2 | Generated artifacts: derived; edit sources or regenerate; artifact_policy.md governs | strong | repo artifact | strengthened | crew | implementation |
| D-011 | 3 | TDD for logic changes (test-first) | strong | repo artifact | rigorous-default | crew | implementation |
| D-012 | 3 | Workflow selection: Quick vs Cautious by blast radius | strong | repo artifact | rigorous-default | orchestrator | planning/framing |
| D-013 | 3 | Cautious: worktree + gated breakdown comment + subagent review | strong | repo artifact | rigorous-default | orchestrator | planning/framing |
| D-014 | 3 | Region verification: full region suite for every change | strong | repo artifact | rigorous-default | crew | verification |
| D-015 | 3 | Autonomy permissions: push/merge/delete/close require asking | strong | repo artifact | rigorous-default | both | authority/scope (orch), stop/report (crew) |
| D-016 | 3 | Python: `py` not `python` on Windows | strong | repo artifact | not-applicable | crew | implementation |
| D-017 | 3 | Scope discipline: touch only what task requires | strong | repo artifact | rigorous-default | crew | implementation |
| D-018 | 3 | Evo: calibrated evaluation against stable baselines | strong | repo artifact | strengthened | both | gating/evidence (orch), verification (crew) |
| D-019 | 3 | Physics: truth-anchored tests L1–L4 | strong | repo artifact | strengthened | crew | verification |

---

## Compile History

| Date | Mode | Outputs touched | Remaining weak/unresolved |
|---|---|---|---|
| 2026-05-24 | final | ORCHESTRATOR_CONTEXT.md, CREW_CONTEXT.md, GLOSSARY.md | none |
