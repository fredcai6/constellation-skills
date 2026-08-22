# Reviewer Handoff

## Gate
g3 (g3-review)

## Survey State Location
`.agent-work/w2-basis/g3-review/review.json`.

## What Was Implemented
A dated addendum to `docs/CHECK_SCRIPT_CENSUS.md`'s `generate_spine.py` disposition section, and a `python -m scripts.code_map build --root .` re-run refreshing `map/INDEX.md`. Full implementer account: `.agent-work/w2-basis/crew-handoffs/g3-implementer-result.md` — note it found and explained a real discrepancy: `grep -c '"because"'` against the shipped template now returns 3, not 0, because the new `basis` objects' optional `because` rationale sub-field is a literal key-name collision with the unrelated top-level `because` convention the census originally measured. Verify this explanation, don't just accept it.

## How to Inspect the Diff
Uncommitted working tree — `git status --porcelain` then `git diff`. Expect `docs/CHECK_SCRIPT_CENSUS.md` and `map/INDEX.md` changed; `map/ids.jsonl` unchanged.

## Task Statement
Update the census doc's counts to reflect this wave's change and keep the map fresh — inspection-only, no code/template changes.

## Close Criteria
- Independently re-run `grep -c '"because"' skills/commander/templates/COMMANDER_SPINE.template.json` and `grep -c '"basis"' ...` yourself — confirm 3 and 3, and confirm the addendum's explanation for the "because" count is actually correct (i.e., genuinely open the file and check: are the 3 `"because"` hits nested inside the 3 `basis` objects, or is one of them a stray/unrelated top-level `because`? This is a real correctness check, not a formality — a wrong explanation here would mislead a future reader of the census doc).
- Confirm the addendum doesn't rewrite or contradict any of the census doc's PRIOR committed findings (the `generate_spine.py` disposition, `#368/#444`) — it should only append new, dated information.
- Independently re-run `python -m scripts.code_map build --root .` yourself, confirm it's deterministic (same output/diff as the implementer's claim), and confirm `git status --porcelain map/` matches what's already staged/changed (no further drift after your own re-run).
- Reproduce the map-freshness test result (`tests/test_code_map.py`, `tests/test_map_orient.py` or whichever the suite runs) — green.
- Reproduce the FULL local suite (`pytest -q`, no path filter) yourself — confirm the claimed `3642 passed, 6 skipped` (or close; a few tests may be nondeterministic in count if the environment differs slightly — flag materially if your count differs, don't silently accept a different number as "close enough" without checking why).

## Allowed Scope
`docs/CHECK_SCRIPT_CENSUS.md`, `map/INDEX.md`, `map/ids.jsonl`.

## Specific Exclusions
Everything from g1/g2 (`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, the template + overlay copies, `tests/test_checklist_engine.py`) — flag as BLOCK if any of these changed further in this gate's diff.

## Constraints the Implementation Must Respect
Dated, SHA-pinned addendum; no rewrite of prior prose.

## Map Anchors (inbound)
- **Structural:** `docs/CHECK_SCRIPT_CENSUS.md:108-152`, `map/INDEX.md`.
- **Evidence expectations:** the census's own originally-cited grep commands, re-measured.

## Evidence Produced
Full IMPLEMENTER_RESULT at `.agent-work/w2-basis/crew-handoffs/g3-implementer-result.md`. Target postcondition for your verdict: `g3-integrate.c2` (reviewer verdict = APPROVE). This is also this wave's final crew gate before the Commander drives `reconcile`/`triage`/`review`/`feedback`/`archive` — your APPROVE closes out the last piece of engineering work in this wave.

## Suggested Model Tier
simple bounded — reason: mechanical re-derivation of grep counts and a suite run; the one substantive judgment call (is the `because`-count explanation actually correct) is narrow and checkable directly.

## Stop Conditions
Return BLOCK if: the `because`-count explanation is wrong on inspection, any excluded file changed, the map build isn't reproducible/deterministic, or the full suite doesn't come back clean.

## Return Format
Return REVIEW_RESULT to `.agent-work/w2-basis/crew-handoffs/g3-reviewer-result.md` before ending your turn.
