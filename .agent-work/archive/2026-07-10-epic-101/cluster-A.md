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
