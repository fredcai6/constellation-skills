# Critic Handoff: Fantasy-League Prediction Push (two-track, live 2026)

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:\Programs\f1Brainz\.agent-work\explore-fantasy-roadmap\DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.
- You MAY read the repository (code, docs, issues) to test the spec's claims against reality — that is verification, not journey context.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens: intent-fit — does the design serve the stated point?** The stated point is in the spec's Intent section (win a ~20-player fantasy league, live 2026, ~7.5 pts/race to find, co-pilot weekly loop). Test every design element against it: does each bet plausibly buy points toward winning? Is anything load-bearing for the goal missing? Does the sequencing serve the "reliable ASAP" clock? Is the north-star metric actually aligned with winning a tournament against ~20 correlated humans?
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it. Do not pre-censor a finding because it might have been considered; raise it and let triage decide.

## Return format

Write your findings to `C:\Programs\f1Brainz\.agent-work\explore-fantasy-roadmap\critic-intent-fit-findings.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `IF`), **Lens** (`intent-fit`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage. `verify_spec_confirmed.py` refuses to let confirm open while any Disposition cell is empty, so leaving them blank is correct, not incomplete.
- Also return the same table as your final message text.
