# Cold plan critic — triage (delegated: Commander triages against launch order + latitude)

Critic was a fresh-context subagent reading only execute.json + PLAN.md + UNDERSTAND.md +
issue #102. 12 findings. Disposition below; accepted findings folded into execute.json
BEFORE the plan freezes.

| # | Sev | Disposition | Action taken in execute.json |
|---|---|---|---|
| 1 | HIGH | ACCEPT | Word-count evidence was missing from every gate. Wired into g7-implement (before/after per-skill table, SKILL.md bodies AND _shared buckets, command-derived) + g7-integrate c1. |
| 1b | HIGH | ACCEPT | Honesty caveat added: relocated always-read doctrine is relocated-not-removed from a role's installed total; PR reports SKILL.md bodies AND bucket growth, not body-only. |
| 2 | HIGH | ACCEPT | Residual test now globs **/SKILL.md ONLY (excludes ALL references/, not just the bucket). Named the deliberately-retained role refs (checklist-engine.md, measurement/ui.md, fleet-doctrine.md) that a naive "non-bucket references" scope would false-fail. |
| 3 | HIGH | ACCEPT | g1/g2 implement must FIRST emit a command-derived exact carrier list with a DRIFT-ROBUST stem (not the pristine verbatim string); before-count from that command, not the ~10/~11 estimate. PLAN confidence overclaim noted here (moves 1,2 counts were deferred to implement, not "grep-confirmed"). |
| 4 | MED | ACCEPT-PARTIAL | Move 8 destination (global-everyone) is RULED by the launch order pre-ruling and kept; but g4 now flags it as a deliberate scope-broadening (injects into crew tier), surfaced not silent. Not overriding the ruling — no contradicting evidence, and the delegate-not-replacement memory supports universality. |
| 5 | MED | ACCEPT | g6 move 9: admiral does not bundle lessons-auditor and its harvest substep 4 applies the rule operationally — so admiral keeps a MINIMAL inline decision-rule reminder + pointer, not a bare pointer that strands the sweep. Home stays lessons-auditor per the ruling; pointer phrasing is my latitude. |
| 6 | MED | ACCEPT | g4 move 5: commander (own dispatch) vs reviewer (implementer's claims) may be semantically distinct — reconcile carefully; if distinct, keep a role-specific tail / honest-null and LOG, never force-merge. |
| 7 | MED | ACCEPT | g2 given the same role-specific-tail allowance as g1 (workbench owns the engine; survey vs gated). |
| 8 | MED | ACCEPT | g7-review must EXECUTE >=1 falsification per test class (drop a bucket line -> content-pin red; re-insert an inline copy -> residual red) and report observed red — not just reason (T5 detector/fix same author). |
| 9 | MED | RESOLVED-NOW | Checked charter for a drifted second banner: grep of RIGOROUSLY/STRICTLY/bold-caps stems finds only ONE banner (line 31); line 29 is inline emphasis, not a banner. The launch order's "charter twice" is definitively not borne out — 6 banners total, one per file. No hidden variant to evade the delete/residual. |
| 10 | LOW | ACCEPT | g7 adds a content-pin that the design-it-twice canonical still ships in the orchestrator bundle after move 10 cuts its last local restatements. |
| 11 | LOW | ACCEPT | g4-review given an explicit per-move sub-checklist so move 4 (the semantic partial-move) isn't rubber-stamped inside the batch. |
| 12 | LOW | RESOLVED-NOW + ACCEPT | Repo has 16 test files / 444 tests, not just the 36 in test_install_constellation.py. Full baseline = 442 passed, 2 skipped. Every integrate check broadened from `tests/test_install_constellation.py` to `tests/` (~13s/run, acceptable). |

Panel-vs-single (surfaced): single cold critic, because this is a mechanical-relocation plan
whose moves' safety was pre-verified by the epic's c2-x2 (not architecture-spawning). The
critic nonetheless surfaced 3 HIGH findings that materially hardened the plan — good ROI on a
single critic; no panel escalation judged necessary.

No finding required floating to the Admiral: all sit within inherited latitude (wording,
test placement, pointer phrasing, gate structure) or are ruled by the launch order (moves 8, 9
destinations kept per pre-ruling, with the mechanism concern addressed in phrasing).
