# Candidate: minimal-interface

The smallest skill that discharges the six duties. Every element below survived the deletion test; the ones I cut are named under "deliberately does NOT do."

## Frontmatter draft (ships as-is)

```yaml
name: constellation-curator
description: Apply skill-authoring doctrine to the constellation skills corpus itself — description fields, invoker tagging, terminology consistency, soft word budgets, and reference TOCs — after a corpus measurement pass. Use periodically to consolidate drift that has accreted across skills. Not for preventing future accretion, not for auditing code architecture (that is Scout), and not for redesigning a skill's workflow.
```

Third-person, states what + when, carries an exclusion clause (the three "not for" boundaries).

## Invoker class: **human**

Periodic cadence, human-triggered ("run the curator"), like charter/explorer. It edits doctrine files the human owns and stewards; those edits are reviewed. I pick ONE class deliberately — the interrogator's bolted-on "delegated context" paragraph (x2 mis-tailoring flag) is the cost of straddling two audiences. Body register: terse imperative, agent-executing-for-a-human. No delegated mode.

## The interface (deep-module terms)

- **Trigger:** human runs it on a maintenance cadence (after N accretion cycles, or when the corpus feels drifted). Not scheduled, not dispatched.
- **Inputs:** the `skills/` tree + `_shared/`; authoring doctrine inlined as heuristics (from x1); no project context needed — the corpus is self-describing.
- **Evidence step (the one script that earns its keep):** bundled `measure_corpus.py` emits per-skill SKILL.md line/word counts and duplication grep hits (signature-phrase counts across files). It runs FIRST every invocation. Prefer-a-script doctrine applies precisely here: the measurement must be deterministic and re-runnable across periods, so it is code, not prose Claude regenerates. This is a measure→review→fix feedback loop, gated on "measure before you touch."
- **No checklist.** Like triage: `**No checklist. Work the passes directly.**` The six duties are a fixed linear sweep over a known file set; the engine's gated/survey machinery would be ceremony. This is the biggest lean — it drops the workbench engine dependency, the template JSON, and the engine-invocation boilerplate that x2 found copy-pasted into ~10 skills.
- **The six passes (prose heuristics, applied in place):** description field (third-person, what+when, exclusion clause) · invoker tag + body-register match · terminology sweep (one term, never synonyms) · soft word budgets (flag-and-review, never a hard gate) · reference TOC for >100-line files. Mechanical, verifiable-by-inspection edits — applied directly, no routing.
- **Outputs:** (1) edits applied to the skill files in place; (2) a short consolidation report naming fields inline — what changed per skill, the measurement snapshot before/after, and anything routed out.
- **Seams:** anything needing a *design decision* (should this duplicated doctrine move to `_shared`? is this skill mis-scoped?) is future work → a **Triage** recommendation, not a curator edit. Curator applies doctrine; it never decides corpus architecture. No seam with Cartographer/Scout — those own the code map; curator owns doctrine text. Reads `_shared/` but edits it only as an ordinary target.

## Deliberately does NOT do

- No checklist / engine / template / references dir (deleted — triage proves a lean skill needs none).
- No re-accretion prevention: it consolidates what accreted and stops. No gates, linters, or CI hooks to stop future drift — that would fight the human's accrete-then-consolidate model.
- No code/architecture audit (Scout), no map edits (Cartographer), no workflow redesign, no corpus-architecture decisions (→ Triage).

## Self-assessment

- **Depth:** high — one script + one prose sweep hide six doctrines behind "run curator." Little interface, much behind it.
- **Locality:** high — all maintenance labor in one periodic pass instead of scattered across N accretion cycles; the deletion test passes loudly (drop it and drift reappears across every skill).
- **Seam placement:** the mechanical-edit / design-decision line falls exactly where triage already draws fix-now vs route. Clean, precedented.
- **Testability:** the measure script is independently runnable and falsifiable; the report's before/after snapshot is the evidence the passes fired.

## Open risks

- Soft budgets as prose heuristics may under-fire (no gate to force them) — acceptable by constraint, but a real recall cost.
- One script is a maintenance surface; if the corpus grows a `scripts/*` per skill (x2 notes none today), `measure_corpus.py` needs updating.
- "Edit in place, human reviews after" trades a pre-edit approval gate for speed — fine for a human-invoked periodic tool, wrong if it ever became agent-dispatched.
