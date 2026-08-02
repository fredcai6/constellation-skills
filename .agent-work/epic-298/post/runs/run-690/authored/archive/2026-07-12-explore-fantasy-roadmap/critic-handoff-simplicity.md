# Critic Handoff: Fantasy-League Prediction Push (two-track, live 2026)

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:\Programs\f1Brainz\.agent-work\explore-fantasy-roadmap\DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.
- You MAY read the repository (code, docs, issues) to test the spec's claims against reality — that is verification, not journey context.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled.
- **Assigned lens: simplicity/YAGNI — what can be deleted?** For every workstream, gate, artifact, and metric in the spec: what happens if it is simply not done in this push? Which items are riding along on momentum rather than earning points-per-race? Where does the spec do two things when one would test the same bet? Is the two-track structure itself necessary, or ceremony? Which "hygiene" items are actually blocking and which are displacement activity a week before a race?
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it.

## Return format

Write your findings to `C:\Programs\f1Brainz\.agent-work\explore-fantasy-roadmap\critic-simplicity-findings.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `SY`), **Lens** (`simplicity`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage.
- Also return the same table as your final message text.
