---
name: constellation-curator
description: "Periodic human-run maintenance of the skills corpus: measure with curate_corpus.py, mend mechanical issues in place, route design decisions to Triage. Use when a human runs a corpus-health pass; not architecture-map auditing (scout) or authoring a new skill (write-a-skill)."
invoker: human
---

# Constellation Curator

Keep the skills corpus healthy on a human cadence: **measure -> mend -> route** — mend mechanical drift in place, route judgment onward.

The standard for what "healthy" means is shared with the authoring skill: `_shared/skill-goodness.md`. Curator maintains against the same criteria `write-a-skill` mints against — `curate_corpus.py` measures its mechanical subset (below); its semantic subset is what Route hands to Triage rather than silently mending.

Drive every step through the checklist engine and finish its sequence — final `advance`, then `release`, as journaled actions. Work the engine never saw did not happen. Full completion doctrine: `_shared/global-everyone.md`.

## Trigger

Human-only, periodic ("run the curator") — after a batch of edits, before a release, or when doctrine drifts. Never scheduled, never a code-change reaction, never agent-dispatched. `invoker: human` declares this, and seeds that convention. *(Untaken road, revivable: a report-only delegated mode — deliberately unbuilt.)*

## Invariant #1 — measure before mend

Every invocation begins by running `python <skill-dir>/scripts/curate_corpus.py --root skills`. It measures five mechanical properties per skill: body **size**; **description** lint (length, person tokens, when-to-use + exclusion markers); **invoker-tag** presence; reference **TOCs**; and **duplication-signature** clusters (the drift detector).

Decidability honesty (T7): the script measures mechanical facts and shortlists candidates; it never renders a semantic verdict. Whether a flagged clause is really a procedure is the **human mend pass's** job — not the script's.

**Two-sided acceptance (detector-self-confirmation guard).** A corpus finding is accepted only when it survives *both* sides: the detector's own run (`curate_corpus.py`) **and** an independent fresh-context sweep by a reader who did not run the detector. The script shortlists mechanical candidates; the semantic verdict is the fresh reader's — the detector never confirms itself.

## Invariant #2 — flags never gate

The script always exits 0. Findings are rows, not failures; soft budgets say where to look and must never harden into a gate. Distribution claims come from a row count, never an impression.

## Mend

Apply mechanical, verifiable-by-inspection fixes in place: tighten a description, add a TOC, normalize terminology, cut re-accreted boilerplate. **No engine checklist — a fixed linear pass** (the triage precedent): work the flagged rows directly. **The git diff is the review gate**; a fix not obviously correct from the diff is a route, not a mend.

**Broad-first dedup-move sequencing.** When clearing a duplication-signature cluster, make the **broad move first** — lift the shared doctrine to its single `_shared/` home (a Route) — and only **then** cut the now-redundant inline copies (a Mend); cutting the narrow copies first leaves the broad move re-touching the same rows and re-opening closed diffs.

## Route

Design decisions — move doctrine to `_shared`, re-scope or kill a section, change a budget — become **Triage recommendations** (`constellation-triage`), never silent curator edits. The curator mends; it does not redesign.

## Outputs

`CURATOR_REPORT.md`, shaped inline: *Findings*, *Mends applied* (fix + git diff), *Routed to Triage*, *Measurement before/after*. Keep the `--json` record alongside; no durable-truth writes beyond the mends; no template ships.

## Portfolio duty — optional, dormant

A future portfolio pass (the right *set* of skills — gaps, overlaps) is inactive until the eval harness exists (issue #106); the curator has **no dependency** on it and stands alone today.

## Error modes

An unparseable skill dir is a report ROW (`check="parse"`), not a crash. The first run flags every skill for a missing invoker tag: expected — the curator is seeding the convention. Do not retro-tag the whole corpus; route the rollout to Triage.
