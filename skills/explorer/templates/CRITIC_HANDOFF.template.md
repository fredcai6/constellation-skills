# Critic Handoff: `<spec title>`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`GLOSSARY.md`).

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `<path to DESIGN_SPEC.md>`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens** (or **full-adversary** in single-critic mode): `<intent-fit — does the design serve the stated point | testability — can each pathway be exercised and falsified | simplicity/YAGNI — what can be deleted | full-adversary — all of it, no lens>`
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it. Do not pre-censor a finding because it might have been considered; raise it and let triage decide.

## Return format

Return your findings as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID**, **Lens**, **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage, choosing one Disposition per finding — `EDIT`, `RE-EXPLORE`, or `REJECT` — with a reason. `verify_spec_confirmed.py` refuses to let confirm open while any Disposition cell is empty, so leaving them blank is correct, not incomplete.

Example row (Disposition/Reason left for the human):

```
| F1 | testability | MAJOR | <the weakness, stated so a reader can act on it> |  |  |
```
