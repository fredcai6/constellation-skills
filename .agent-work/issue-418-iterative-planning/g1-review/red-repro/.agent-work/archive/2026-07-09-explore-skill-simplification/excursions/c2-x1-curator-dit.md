# c2-x1 — Curator design-it-twice: comparison and recommendation

Panel: three candidates for `constellation-curator`, each under one named constraint. Full candidates: `c2-x1-curator-dit-minimal.md`, `-scout-analog.md`, `-measurement.md`. Convergence is the human's.

## Comparison (depth / locality / seam / testability)

| Axis | minimal-interface | scout-analog | measurement-first |
|---|---|---|---|
| Shape | human-only; no checklist (triage precedent); one measure script; **edits in place**; report after | audit-only role on scout's spine (census/audit/report via engine); **never edits**; routes all fixes to Triage | thin operator around `curate_corpus.py` (deterministic, baseline-diffable, **flags-never-gates enforced in code**); report-only |
| Depth | high — "run curator" hides six doctrines | high — one verb, whole machine | high — one command hides five checks + drift diff |
| Locality | high; but doctrine lives as prose heuristics in the body | good; doctrine in a TOC'd reference | highest for checks (script) — but *judgment* items stay outside |
| Seam | mechanical-edit vs design-decision (routes design to Triage) — clean, precedented on triage's fix-now ladder | audit vs edit — precedented on scout, but forces a Triage hop even for trivial mechanical fixes | measurement vs repair — crisp, and the soft-budget invariant can't erode (it's in code) |
| Testability | script yes; prose passes only by inspection | report is the test surface; checks exercisable on known-bad input | best — golden-file testable, pure functions over a fixture corpus |
| Main risk | edit-in-place with no pre-edit gate; under-firing soft heuristics | ceremony: engine spine + report + Triage hop to fix a typo-grade description | new invoker-tag marker convention; mechanical lints can't catch mis-tailoring |

## Recommendation: named hybrid — **"measure-then-mend"**

Take the **script core from measurement-first**, the **edit posture from minimal**, and the **routing seam from scout-analog**:

1. **Measure** — `curate_corpus.py` runs first, every invocation: sizes vs soft budgets, description lint, duplication clusters, TOC presence, drift vs `--baseline`. Flags, never gates — enforced in the script, so the heuristic-not-gate invariant can't erode by prose drift. Distribution claims come from the table, never impressions.
2. **Mend** — mechanical, verifiable-by-inspection fixes (description wording, TOCs, terminology, register touch-ups) are applied **in place** by the curator run. Human-invoked + git diff as the review gate; no Triage hop for typo-grade work.
3. **Route** — anything that is a *design decision* (move doctrine to `_shared`, re-scope a skill, kill a section) becomes a Triage recommendation, never a silent curator edit. Exactly triage's fix-now-vs-route ladder.
4. **No engine checklist** — the sweep is a fixed linear pass over a known file set (triage precedent: "no checklist, work the passes directly"). The measurement JSON baseline is the durable cross-run artifact, not workflow state.
5. **Invoker: human only.** Periodic cadence, edits reviewed via git. Dropping the "both" ambition avoids exactly the dual-audience patching x2 flagged on interrogator. (Untaken road: agent-dispatched closeout audit — revivable later by adding a report-only delegated mode.)

Why not the pure candidates: minimal alone leaves the checks as prose heuristics (under-fires; not testable); scout-analog alone adds an engine spine + handoff hop that is ceremony at this scale (14 files, mechanical fixes); measurement-first alone can't fix anything (every trivial fix becomes a second workflow) and can't see judgment-class findings (mis-tailoring).

Open risks carried into the hybrid: shingle/duplication-signature tuning (justify constants in code); first run flags all 14 skills for missing invoker tags (expected — it seeds the convention); judgment items (mis-tailored register) remain a prose pass over the script's shortlist.
