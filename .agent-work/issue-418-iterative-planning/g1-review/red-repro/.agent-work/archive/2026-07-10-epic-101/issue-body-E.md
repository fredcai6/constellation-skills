### E — Autonomous eval harness (Euler-piloted; tackle last)

Not a skill — a repo tool (a skill wrapper fails the deletion test). Interface:

- **Scenario** (`evals/<name>/`): fixture-repo setup, a task prompt that drives a real constellation workflow (pilot: commander runs "solve Project Euler #N with tests" as a bounded issue, dispatching implementer/reviewer crew), and mechanical checks.
- **Runner** (`scripts/run_skill_eval.py`): installs the candidate skills to a temp target, launches fresh headless agents on the scenario, then executes the checks itself. **Check hierarchy (T3):** the verdict is carried by the *process* checks — engine spine JSON completed its steps, expected artifacts present, tests written and green. **Answer-correctness is a weak signal, never sufficient**: frontier models likely have Euler answers memorized, so a correct number proves nothing about the workflow; a scenario passes only on process checks. **Stochasticity (T4):** one run cannot separate regression from variance — the runner contract specifies N-of-M runs with a pass-rate threshold (defaults set at the runner-contract design gate); "≥1 eval run" in the situational bar means ≥1 *scenario execution*, which is itself N sub-runs. Transcripts are kept for diagnosing failures, not for judging.
- **Portfolio:** a few pilot Euler scenarios at graded difficulty; curator curates growth and mix over time (Euler exercises workflow machinery — spines, handoffs, evidence discipline — but not architecture judgment; the portfolio must diversify).
- **Bar (decided, q3-c2):** situational — new skill or behavior-changing rewrite gets ≥1 fresh-context eval run before install; mechanical edits need only the existing suite + git review. No Iron Law; nothing gates on evals.
- **Why autonomous:** downstream project failures (e.g. f1brainz) do not flow back to this repo; autonomous scenario runs are the substitute signal.

*Design-it-twice note:* shape chosen through explicit human-steered comparison (human-read transcripts vs autonomous checks; skill vs repo tool). The detailed runner contract (scenario schema, check DSL vs plain script, temp-install mechanics) is deliberately deferred to its own design gate at execution — surfaced here as a named decision, not silently.


---
## Epic context (paste, not pointer)

Parent epic: #101 (confirmed shaped design, 2026-07-09). This issue is one cluster of that spec; the spec text above is authoritative — do not re-litigate its dispositioned decisions.

**Cross-cutting conventions (binding on this cluster):**
### Cross-cutting rules (adopted as corpus conventions, applied by A–C and F)

1. **Descriptions:** third-person; state what + when-to-use (triggering conditions); never procedure; exclusion clauses only for the confusable pairs (scout/cartographer, explorer/interrogator, admiral/commander, curator/scout+write-a-skill, commander-delegated/admiral); none for name-dispatched crew skills.
2. **Register:** rule-plus-why default; emphasis only at mechanism-backed gates.
3. **Structure:** doctrine lives once (`_shared` bucket or a role reference); SKILL.md is trigger + boundary + pointers; references one hop deep; >100-line references carry a TOC.
4. **Invoker tags:** every skill declares human/agent/both; body register matches; x2's draft classification ratified as tags land.
5. **Soft budgets:** word/line targets are curator review heuristics, never gates.

- **Per-section approval:** all sections presented 2026-07-09; human named no amendments and directed the spec to critical review. Formal approval is recorded at the confirm gate after critic findings are dispositioned.

**Intent frame:**
## Intent

The constellation skills corpus (14 skills + `_shared`) has grown by accretion: usage lessons landed as inline SKILL.md patches, nothing was deleted or restructured, and measurement (excursion x2) confirms the cost — one compliance boilerplate pasted verbatim into 10 files, the engine-invocation string restated in ~10 with drift, emphatic banners in 6, and a layering epicenter in commander (2,580 words, doctrine stated in up to three places). This pass is **periodic preventive maintenance**, not incident response: consolidate what accreted before agents start struggling, guided by external authoring doctrine (excursion x1: description-field discipline, hard conciseness budgets, one-hop progressive disclosure, invoker tailoring) and by measurement.

Primary beneficiaries are the agents that load these skills. The primary mechanisms are **drift-elimination** (duplication-with-drift is how agents follow stale wording) and **patch-once maintenance** (doctrine changes land in one file, not fourteen). Token reduction is real but narrower than "every duplicated word saved": always-read doctrine moved into a bundled `_shared` reference is *relocated*, not removed, from a role's context — genuine token wins come from the deletions (banners, layering cuts, per-skill diets), and each consolidation PR carries before/after word counts as evidence so the claim stays honest. Workstreams C and E are **lifecycle investments**, not token-cost work: they make each future consolidation run cheap and observable. The cadence itself is deliberately a human habit, not machinery — scheduling and agent-dispatch were considered and left as untaken roads; the accepted risk is that a lapsed habit means a longer (but still tool-assisted) next run. Done feels like: every SKILL.md reads as one deliberately-written document absorbable in a single pass (a judgment criterion, reviewed by humans at PR time, not a falsifiable metric — stated plainly); doctrine lives exactly once with skills pointing at it; each skill is visibly tailored to its invoker; and the tooling exists to repeat this consolidation cheaply — because accrete-then-consolidate, not prevention, is the accepted lifecycle.

**Testing pathways (epic-wide; apply the row for this cluster):**
## Testing pathways

- **Cluster A/B/F (edits to existing corpus):** the existing suite is **structural only** — it pins bundle filename sets, `windows.md` shipping, `_shared` exclusion, and exactly one content string; it does NOT detect a mangled or dropped doctrine (T1). The mechanical net is therefore added by cluster A itself: per-doctrine content-pin tests in the destination buckets + a no-residual-duplicate grep test, plus the *enforced* per-gate grep-evidence contract (T2) and before/after word counts (derive-distribution-claims-from-command). Falsification: drop or truncate a relocated doctrine → its content-pin test fails; leave a stale inline copy → the residual test fails.
- **Cluster C (curator):** `curate_corpus.py`'s mechanical checks → golden-file test over a fixture corpus whose planted flaws are **derived from x2's measured real failure modes** (the boilerplate/engine-string/banner clusters), not invented (T6); flags-never-gates falsified by asserting exit 0 on a maximally-flagged fixture. Post-cleanup quietness of curator's first run is **necessary but not sufficient** acceptance (T5 — detector and fixes share an author): acceptance additionally requires an independent fresh-context sweep (an x2-style survey by an agent given neither the script nor the fix list) reporting no remaining duplication clusters of the measured kinds. Semantic criteria (register-matches-tag, "deliberately-written") are human-judgment at PR review, stated as such, not falsifiable metrics (T9).
- **Cluster E (harness):** self-testing by construction — a pilot scenario run IS the test; falsified by a scenario whose process checks pass with a known-broken skill (checks too weak) or fail with a known-good one (checks too strict), measured over N-of-M runs (T4). Deferred to its own gate: check-schema tests, N/M defaults.
- **Cluster F:** manual fresh-context selection check pre-E (see §F); the delegated-commander eval scenario at E's gate. If E is dropped, selection coverage stays manual — named residual risk (T11).
- **Deferred to later drills:** executing the full test suite on Windows CI parity; measuring real token-cost deltas per role before/after (nice-to-have evidence, not a gate).
