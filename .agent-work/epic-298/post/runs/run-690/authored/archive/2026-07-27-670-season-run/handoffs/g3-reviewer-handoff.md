# Reviewer Handoff

## Gate
`g3` — instrument panel over the full 2023 corpus (#670)

## Survey State Location
`.agent-work/670-season-run/g3-review/review.json`

## What Was Implemented
NEW `scripts/run_season_panel_670.py` — runs all 4 landed instruments over the consolidated season slice (20 covered circuits). The ONE generalization: the cross-circuit split scheme is now a ROTATING-BLOCK (circle-method) deterministic, seed-free, balanced split-half over the N circuits: circuits sorted to a canonical order; for k=0..(n/2-1), half_a = contiguous window [k..k+n/2-1] mod n, half_b = complement → K=n/2 distinct balanced partitions (K=10 for 20 circuits); r is averaged over the partitions and the imported `decide_channel_from_mean_r` is re-applied. NEW `tests/unit/physics/instrument_panel/test_panel_corpus.py`. Implementer result: `.agent-work/670-season-run/crew-results/g3-implementer-result.md`.

## How to Inspect the Diff
Both files are NEW/untracked — inspect directly (`git status --porcelain`, then read `scripts/run_season_panel_670.py` and the test file). Not `git diff main...HEAD`.

## Task Statement
Generalize ONLY the split scheme to the corpus, re-applying frozen replication rules byte-unchanged; build no new instrument/model. Full task: `.agent-work/670-season-run/handoffs/g3-implementer-handoff.md`.

## Close Criteria (each a review check)
- **ADJUDICATE THE NEW-METHOD LINE (Admiral-required, do NOT merely confirm labeling):** Does the rotating-block deterministic-averaged split scheme cross into NEW STATISTICAL METHOD (forbidden by ruling 4), or is it a legitimate read-adapter generalization of the landed exhaustive-2v2-AVERAGED scheme? State a reasoned verdict. Key questions: is the r-computation itself (`compare_channels_by_class`, double-centering, r_floor, tie margin, coverage) IMPORTED and byte-unchanged? Does the scheme only change HOW circuits are partitioned + average over K balanced partitions (faithful to the landed averaging), or does it alter the statistic? **If you judge it CROSSES into new method, that is a BLOCK and must be FLOATED to the Admiral before commit — say so explicitly in your result.**
- The split is DETERMINISTIC (no `random`/seed — grep-confirm), balanced (each partition splits circuits into equal halves), AVERAGED over K>1 partitions (not a single split), and the report states K + the exact construction.
- Every frozen rule/threshold is IMPORTED from `replication.py`/`frozen_constants.py`, none re-minted or re-derived (grep for local `def r_floor`/threshold literals → none).
- Circuit set = the 20 COVERED circuits (Bahrain error-rows + absent Saudi correctly EXCLUDED); drivers per circuit from the slice.
- OFFLINE; official laps read from the SCRATCH f1 DB, never the tracked one; the committed #668 report/script untouched; `src/physics/instrument_panel/*` untouched; Student-t σ preserved.
- Tests real (deterministic split, frozen-rules-imported, synthetic multi-circuit slice, reproduce-identical); re-run yourself.

## Allowed Scope
NEW `scripts/run_season_panel_670.py`, `tests/unit/physics/instrument_panel/test_panel_corpus.py`. (Imports from #668 script + `src/physics/instrument_panel/*` are the sanctioned read-adapter reuse.)

## Specific Exclusions (flag if touched)
No edit to `src/physics/instrument_panel/*`, `frozen_constants.py`, or the committed #668 report/script; no `random`/seed; no new instrument; no docs/architecture/* edit.

## Constraints
OFFLINE; frozen rules byte-unchanged; no new method; Student-t σ preserved; pinned 3.14 interpreter.

## Map Anchors (inbound)
- **Structural:** `run_season_panel_670.py::enumerate_rotating_half_partitions` (the new split); imported `replication.py` rules.
- **Decision anchors:** decision:panel-corpus-split-scheme — deterministic balanced averaged, seed-free.
  `@grade: guess · leans g3-implement · Admiral-endorsed as a scaling read-adapter PROVIDED frozen rules byte-unchanged; you adjudicate the new-method line and FLOAT if it crosses.`
- **Evidence expectations:** frozen rules imported; reproduce-identical; small/unresolved replication is an HONEST result (no-frame-kill), not a defect.

## Evidence Produced
`test_panel_corpus.py -q` → 10 passed; `instrument_panel -q` → 67 passed; pyright 0; `run_season_panel_670.py` real run → all 4 instruments, K=10, reproduce byte-identical. Re-run to confirm. Target integrate postcondition: `g3-integrate.c1`.

## Suggested Model Tier
`stronger` — reason: the new-method adjudication is a judgment call the Admiral explicitly delegated to review.

## Stop Conditions
BLOCK if: a frozen rule was re-derived/modified; the split is random-seeded or a single split; the committed #668 report was overwritten; official laps read from the tracked DB; OR you judge the scheme crosses into new method (and FLOAT to the Admiral).

## Return Format
Write REVIEW_RESULT to `.agent-work/670-season-run/crew-results/g3-reviewer-result.md` (verdict APPROVE or BLOCK, the explicit new-method adjudication verdict + reasoning, per-check findings, blockers, workflow feedback). Then SendMessage cmdr-670 a thin pointer (verdict + new-method verdict + path) before ending your turn.
