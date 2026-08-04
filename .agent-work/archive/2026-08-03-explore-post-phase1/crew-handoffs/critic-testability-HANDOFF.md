# Critic Handoff: Post-phase-1 consolidation + next step toward target architecture

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens**: `testability — can each pathway be exercised and falsified`
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it. Do not pre-censor a finding because it might have been considered; raise it and let triage decide.

## Return format

Write your findings to `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/evidence/critic-testability-RESULT.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `T` — T1, T2, ...), **Lens** (`testability`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage, choosing one Disposition per finding — `EDIT`, `RE-EXPLORE`, or `REJECT` — with a reason. `verify_spec_confirmed.py` refuses to let confirm open while any Disposition cell is empty, so leaving them blank is correct, not incomplete.

Example row (Disposition/Reason left for the human):

```
| T1 | testability | MAJOR | <the weakness, stated so a reader can act on it> |  |  |
```

Final return message: one line — finding count by severity + the result path. Do not modify the spec or any other file.
