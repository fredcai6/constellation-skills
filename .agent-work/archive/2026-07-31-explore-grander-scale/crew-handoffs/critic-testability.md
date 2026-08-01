# Critic Handoff: `Grander Scale — a shared knowledge substrate and a self-improving instruction system`

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:/Programs/constellation-skills/.agent-work/explore-grander-scale/DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. Do not open any other file in `.agent-work/explore-grander-scale/`. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens:** `testability — can each pathway be exercised and falsified`. Interrogate the Testing pathways section and every testable claim in the Chosen design: can each pathway actually be run as described? Is each falsification condition observable, or does it depend on evidence the design never captures? Are there load-bearing behaviors with no pathway at all? Do any pathways test a proxy instead of the claimed behavior?
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it. Do not pre-censor a finding because it might have been considered; raise it and let triage decide.

## Return format

Write your findings to `C:/Programs/constellation-skills/.agent-work/explore-grander-scale/evidence/critic-testability.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `T`), **Lens** (`testability`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage. Leaving them blank is correct, not incomplete.
