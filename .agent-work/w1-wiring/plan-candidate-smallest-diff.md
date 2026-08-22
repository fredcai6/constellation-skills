# Plan candidate — constraint: smallest-diff

One gate plan for w1-wiring under the constraint: minimize the number and size of code/doc changes
this run makes, treating the census as the terminal deliverable unless it forces a change.

## Gates

1. **g1 — census (reasoning gate).** Enumerate every `scripts/{verify,check,prove,measure}_*.py`.
   For each, determine live/unwired/dead by grepping `skills/*/templates/*.json` `command` checks,
   `.github/workflows/`, `scripts/hooks/`, `tests/`, and cross-script imports/subprocess calls.
   Commit `docs/CHECK_SCRIPT_CENSUS.md`.
2. **g2 — generate_spine.py + #368/#444 (reasoning gate).** Trace every live spine-instantiation path
   (`init_work_area.py`, MCP `spine_open`, `mcp_spine_server.py`, tests, CI). Re-measure the #368/#444
   field-group counts by grep over the five/seven cited sites. Fold into the same census doc.
3. **g3 — disposition (reasoning gate, conditionally a code gate).** Given g1/g2's evidence: if
   population is mostly dead, delete the dead scripts in this one gate and stop — no lint authored.
   If mostly unwired, author the smallest lint (a pytest test or one `command` check) in this same
   gate rather than a separate implement/review pair, to keep the diff minimal.

## Compared on

- **Depth** — one document carries the whole decision surface; low overhead per finding.
- **Locality** — all work lands in at most two commits (census, then disposition); minimal fan-out.
- **Seam placement** — puts the lint (if any) at whichever existing seam is cheapest (a pytest test
  under `tests/`), not a new script family.
- **Testability** — the lint's failure mode is proved once, in the same gate it is authored, by a
  reproducible negative case.

## Risk

Folding disposition into the census gate risks under-scrutinizing the code-producing half (deletions,
lint) since it is not a separate reviewed gate — mitigated by the mission's own honest-null clause,
which treats a document-only outcome (mostly dead → just delete) as the expected shape, not an
exception.
