## What
Two small cleanups in `scripts/accept_quali_anchor_420.py`:
1. `_score_event_production` is 122 lines (> 100 `simplification_limits` limit) — a **pre-existing** violation. Decompose it.
2. The harness prints a `Bundle:` header that always shows the `BUNDLE_NAME` constant regardless of `--bundle-path`; the actual loading-path line is correct, but the header label is misleading in saved acceptance output.

## Why
Pre-existing tech debt; the limits violation blocks clean edits to the file. The header label is misleading in committed acceptance evidence.

## Evidence
- `py -m src.utils.simplification_limits scripts/accept_quali_anchor_420.py` → 1 violation (`_score_event_production`, function_lines=122). Confirmed pre-existing via `git stash` round-trip during the #335 run.
- The `--bundle-path` arg was added in #335 (commit `b9c7039`); the header was not updated to reflect it.

## Acceptance
- `simplification_limits` passes on `scripts/accept_quali_anchor_420.py`.
- The `Bundle:` header reflects the actual `--bundle-path` target.

## Out of scope
The anchor blend math, the §7.6 REF constants, the measurement logic.
