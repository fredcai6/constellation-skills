# Simplification review — what #101 stripped that was load-bearing (2026-07-11, read-only analysis agent)

(Verbatim final report; commands and quotes are the agent's, command-derived.)

Diff range: base 2696769 (pre-#108) -> 6b24609 (#113); restoration under study PR #128 (84169cc).
Key derivation: at base NINE skills carried an in-context "Mandatory, no exceptions: drive [workflow] to completion through the engine" clamp; on current main that text survives only in _shared/global-everyone.md, reachable from each skill only via the bare pointer "Compliance/engine-drive rule: inherited — see references/global-everyone.md".

RANKED INVENTORY (restore-via-machinery unless noted):
1. Crew roles implementer + reviewer lost their full "drive to completion through the engine... reporting misfit is compliance" clamp (commit 062dc3b and twin) -> bare pointer. Guards skip/theater/fabrication one tier below Commander. HIGHEST. (Caveat: same-mechanism inference; crews not independently eval-proven.)
2. commander-core.md has NO completion clamp; #128's "MIDDLE not the end / do not end your turn" exists ONLY in commander-delegated/SKILL.md — one-mode-deep. Human commander entry inherits nothing. Restore in commander-core.md (mode-neutral).
3. Admiral entry clamp -> pointer (8483e13). Lower exposure.
4. Interrogator "drive the survey to completion" -> pointer (5712299).
5. "FOLLOW THIS SKILL STRICTLY" banner deletion (0b32e87, 6 skills): do NOT restore as-is — absorb its function into the restored entry ritual.

Relocated-but-weakened: global-everyone.md kept the "Mandatory" sentence but has NONE of #128's three proven forces (entry ritual, anti-quit-early, anti-fabrication "work the engine never saw did not happen"). The relocation kept the least behaviorally-active half.

Removals judged CORRECT (do not re-bloat): scoped-nulls single-homing; reviewer world-verification consolidation; idle-adjudication + unchanged-tree -> global-orchestrator (point-of-use is right); detemporalization; design-it-twice extraction; the all-caps banner TEXT.

No entry OR completion clamp at all: implementer, reviewer, interrogator, cartographer, scout, lessons-auditor, charter, workbench, admiral, commander-core (hence human commander). Completion clamp exists in exactly ONE corpus file. Explorer is the healthy exception (kept domain clamps).

Surprises: restoration was one-mode-deep and one-role-deep (matched the eval's blast radius, not the mechanism); the pointer wording is character-identical across 9 skills = clean mechanical restore target; the clamp's own first clause ("once a role skill is loaded") names a load-time trigger that pointer-delivery defeats by construction.
