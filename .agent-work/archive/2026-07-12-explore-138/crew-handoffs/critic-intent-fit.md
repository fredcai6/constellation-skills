# Critic Handoff: Design Spec — corpus compliance counter-doctrine (#138)

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:/Programs/constellation-skills/.agent-work/explore-138/DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding. You may read the repo's current code/skills to test the spec's claims against reality, but not `.agent-work/explore-138/` (the exploration record).

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens:** `intent-fit — does the design serve the stated point?` Test every design element (D1–D6) against the spec's own Intent section: does it actually counter the named cheap exits? Is anything load-bearing for the intent missing? Does any element serve something other than the stated point?
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it. Do not pre-censor a finding because it might have been considered; raise it and let triage decide.

## Return format

Write your findings to `C:/Programs/constellation-skills/.agent-work/explore-138/evidence/critic-intent-fit.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `IF`), **Lens** (`intent-fit`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage. `verify_spec_confirmed.py` refuses to let confirm open while any Disposition cell is empty, so leaving them blank is correct, not incomplete.
- If you have zero findings, write the file with an explicit "no findings under this lens" line — an empty file is indistinguishable from a crash.

## Budget

≤20 minutes. Findings-so-far over overrun. No repo changes; the findings file is your only write.
