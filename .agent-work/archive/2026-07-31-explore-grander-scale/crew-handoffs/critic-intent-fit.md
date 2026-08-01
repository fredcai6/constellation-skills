# Critic Handoff: `Grander Scale — a shared knowledge substrate and a self-improving instruction system`

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:/Programs/constellation-skills/.agent-work/explore-grander-scale/DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. Do not open any other file in `.agent-work/explore-grander-scale/`. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens:** `intent-fit — does the design serve the stated point`. The spec's Intent section states the point; test every element of the Chosen design against it. Does the near-term stratum actually advance the stated purposes? Does anything in Stratum B quietly serve a different goal than the Intent claims? Is "done" as defined actually the thing the Intent wants?
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it. Do not pre-censor a finding because it might have been considered; raise it and let triage decide.

## Return format

Write your findings to `C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/critic-intent-fit.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `IF`), **Lens** (`intent-fit`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage. Leaving them blank is correct, not incomplete.
