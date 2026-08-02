# Critic Handoff: Fantasy-League Prediction Push (two-track, live 2026)

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `C:\Programs\f1Brainz\.agent-work\explore-fantasy-roadmap\DESIGN_SPEC.md`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.
- You MAY read the repository (code, docs, issues) to test the spec's claims against reality — that is verification, not journey context.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled.
- **Assigned lens: testability — can each pathway be exercised and falsified?** Interrogate the Testing pathways section and every claim elsewhere: are the falsification conditions real and mechanically checkable, or vibes? Can "simulated league placement" be computed leakage-free, and what would silently corrupt it? Is the Belgium shakedown a genuine test or a demo? Are the A/B gates (DNF channel, #513→#450, retrain) specified tightly enough that a motivated builder cannot pass them by accident or flexibility? What pathway has NO falsification path at all?
- Attack the design, not the wording. A finding names a real weakness a reader could act on.
- Relitigation noise is expected and fine — the human filters it.

## Return format

Write your findings to `C:\Programs\f1Brainz\.agent-work\explore-fantasy-roadmap\critic-testability-findings.md` as rows for the spec's structured findings table, using these exact columns:

```
| ID | Lens | Severity | Finding | Disposition | Reason |
```

- Fill **ID** (prefix `TS`), **Lens** (`testability`), **Severity** (`BLOCKING | MAJOR | MINOR`), and **Finding**.
- Leave **Disposition** and **Reason** EMPTY. **The critic never self-triages.** The human fills those at triage.
- Also return the same table as your final message text.
