# Critic Handoff: `<spec title>`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

A cold, full-adversary review of a shaped-design spec. You receive **the spec only** — no exploration record, no ideas board, no rationale for how it got here. That is deliberate: a critic who knows the journey defends it. You do not.

## What you receive

- **The spec, and nothing else.** `<path to DESIGN_SPEC.md>`
- You do **not** get the ideas board, the cycle log, the excursion results, or any account of what was tried and rejected. If the spec's correctness depends on that context, the spec is under-specified — say so as a finding.
- **The repository is off-limits — with one exception.** Every lens works from the spec text alone, except `claim accuracy`, which is required to read the tree. If you are not on that lens, do not go verifying claims yourself; a finding that the spec *might* be factually stale belongs to that arm.
- **Deliberate latitude is not under-specification.** A spec may hand a decision down to the agent who will execute it, and where it does, it says so. Do not file "this does not say how" against a decision the spec explicitly leaves open. Ask the sharper question instead: **is the boundary in the right place?** Name anything left open that needed settling here, and anything fixed that should have been left to the executor. A boundary drawn in the wrong place is a real finding; an open decision that is labelled open is not.

## Your posture

- **Nothing is sacred.** You may attack any decision, including ones the spec presents as deliberate or settled. A decision the authors made on purpose is still fair game if it does not hold up cold.
- **Assigned lens** (or **full-adversary** in single-critic mode): `<intent-fit — does the design serve the stated point | testability — can each pathway be exercised and falsified | done-condition fidelity — does each section's done-condition actually test that section's own work | claim accuracy — do the spec's factual claims still hold against the tree | simplicity/YAGNI — what can be deleted | full-adversary — all of it, no lens>`
- **On `done-condition fidelity`:** read each section's *work* and its *done-condition* side by side, and ask whether satisfying the second requires doing the first. A done-condition that tests something merely adjacent to the work — a count, a label, the existence of an artifact — can be fully met while the section's real work never happens. That is a check that cannot fail sitting in the plan rather than in the code, and it is invisible to every other lens because each one reads the two halves separately.
- **On `claim accuracy`:** this lens alone reads the repository, and is required to. A spec's measured claims — counts, file states, "X does not render", "N templates carry Y" — are load-bearing, and they go stale as the tree moves under them. Verify each at the tree and report every one that no longer holds, naming the command you ran. A claim you could not check is itself a finding.
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
