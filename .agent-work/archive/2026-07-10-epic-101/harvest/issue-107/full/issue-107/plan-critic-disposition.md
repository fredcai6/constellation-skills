# Cold plan critic — findings & delegated triage

Panel-vs-single: single critic (fresh-context general-purpose subagent, plan+frame only). Surfaced choice: single is right-sized — the WHAT was already paneled at epic confirm; only gate sequencing was open. Untaken road: a competitive panel (rejected — not load-bearing enough).

Delegated triage (human unreachable; cite LAUNCH_ORDER; Admiral ratifies at return):

| # | Sev | Finding | Disposition |
|---|-----|---------|-------------|
| 1 | MED | g2-integrate ran only the install test file, narrower than the "suite green" claim | ACCEPTED — broadened c1 to `py -m pytest tests/ -q` (full suite) |
| 4 | MED | SKILL_INDEX.md in scope but unpinned by any test | ACCEPTED — added to g2-review verify list (reviewer owns it) |
| 2 | MED | commander-delegated soft-depends on commander co-install for core+templates | ACCEPTED — delegated SKILL.md names the dependency (workbench-engine precedent); default full-set install satisfies it |
| 3 | MED | "core-pointer resolvable" test is a weak proxy | ACCEPTED — g2 test asserts existence + path-literal, not behavioral resolution |
| 5 | LOW/MED | honest-null clause permits shipping selection UNMET | KEPT — this IS LAUNCH_ORDER's Honest-Null Clause; if triggered I surface a real stop-or-ship to the Admiral in the return, not an automatic ship |
| 6 | LOW | SKILL_SCRIPT_BUNDLES wiring ambiguous vs "ships no scripts" | ACCEPTED — g2 imperative now says OMIT the entry (get() defaults to ()) |
| 7 | LOW | named a non-existent second test list | ACCEPTED — corrected to the single SKILL_NAMES roster |
| 8 | LOW | core.md must carry no skill-dir tokens | ACCEPTED — added g1 constraint |

Critic verdict: sound to execute with #1 + #4 applied first — both applied before plan freeze. Coverage complete (no missed decision-class), green-at-boundary reasoning correct, token-vs-prose-pointer decision correct.
