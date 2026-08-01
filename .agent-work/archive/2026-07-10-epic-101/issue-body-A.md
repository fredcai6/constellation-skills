### A — Single-sourcing dedup (10 moves)

Each duplicated doctrine moves to exactly one home; carriers keep a one-line pointer. Verified go/no-go and bucket rules from c2-x2:

| Doctrine | Current carriers | Destination |
|---|---|---|
| Mandatory-compliance boilerplate | 10–12 SKILL.md files | `_shared/global-everyone.md` (cross-tier), one per-role tail line stays local where genuinely different |
| Engine-invocation string | ~10 files, wording drift | `_shared/global-everyone.md`; canonical detail already in workbench `references/checklist-engine.md` |
| "FOLLOW THIS SKILL STRICTLY…" banners | 6 files (charter twice) | **deleted** — free-floating emphasis unattached to a mechanism (register rule, q2-c2) |
| Scoped-nulls doctrine | explorer (orch) + prototyper (crew) | `_shared/global-everyone.md` — tier bucket would drop a carrier |
| World-verification of claimed side-effects | reviewer (crew) + commander (orch) | `_shared/global-everyone.md` — same cross-tier rule |
| Unchanged-tree shortcut | commander + admiral | `_shared/global-orchestrator.md` |
| Crew-idle adjudication | commander + admiral + fleet-doctrine | `_shared/global-orchestrator.md`; fleet-doctrine keeps epic-specific delta only |
| Delegate-not-replacement | commander + admiral | `_shared/global-everyone.md` (the principle applies at every tier) |
| Dedup-sibling-ids | lessons-auditor + admiral | one home (lessons-auditor, the role that executes it); admiral points |
| Design-it-twice restatements | commander + explorer | cut to one pointer line each; canonical text already in `_shared/global-orchestrator.md` + `design-it-twice-brief.md` |

**Constraints (contractual):** append into *existing* bucket files — never create a new `global-*.md` filename (test glob pins bundle composition, test_install_constellation.py:196–208); every move is reconcile-then-cut (inline copies have drifted — reconcile wording first, confirm carrier list by grep against final wording, then cut); after each move, the carrier's remaining pointer must name the shared file so a reader knows where the rule went.

**Mechanical regression net (added at critic triage — T1, T2, IF3):** the existing bundle tests are structural only (filename sets, not content), so cluster A adds its own teeth: (1) a **content-pin test per relocated doctrine** — an assertion that a signature phrase of each moved doctrine is present in the installed destination bucket, modeled on `test_deep_module_vocabulary_ships_into_installed_skill` (test_install_constellation.py:679–690) — plus a **no-residual-duplicate test** that greps installed skills for the retired inline signature and fails if it reappears outside the bucket; (2) the per-move grep evidence is **enforced, not promised** — each dedup gate's evidence contract in the epic's gate plan requires the pasted before/after carrier-count command output, and the gate does not close without it; (3) each consolidation PR records before/after per-skill word counts (command-derived) as evidence.

*Design-it-twice note:* not an interface — mechanical relocations whose safety was established by the c2-x2 verification. Skipped as trivial with that stated reason.


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
