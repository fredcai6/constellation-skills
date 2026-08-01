# Plan-alternatives (design-it-twice) — gate structure for issue #107

Load-bearing plan (descriptions steer live selection), so alternatives run (bias-to-yes). Panel-vs-single: **two candidates** — the design of WHAT ships was already design-it-twiced and human-ratified at epic confirm (four candidates, issue #107 body); only the gate SEQUENCING is open here, a fairly-easy call → two candidates, remaining option named as an untaken road. Compared on: green-at-every-boundary, review depth per decision-class, crew-vs-reasoning fit, blast radius per gate.

## Candidate A — one-gate-per-decision-class (6 gates)
Split, diet, entries, installer, index, tests, selection each its own gate.
- **Green-at-boundary:** FAILS. Creating `skills/commander-delegated/` in a "split" gate before the "installer"/"tests" gates leaves `discover_skills` + `SKILL_NAMES` red across gate boundaries — a deliberately-red multi-gate window, the exact plan smell doctrine names (a human waiver per gate + a benign-red diagnostic in every review).
- **Review depth:** finest, but most gates are doc edits that doctrine says take inspection-attestation, not crews — six crews would be shallower-not-safer ceremony.

## Candidate B — green-boundary bites (3 gates) — RECOMMENDED
- **g1 (reasoning):** doctrine home + diet + human entry — author `commander-core.md` (mode-neutral) and `crew-dispatch.md` (diet move), rewrite `commander/SKILL.md` to a thin human entry. No new skill dir → suite stays green. Inspection-attestation (quoted before/after + grep + word counts).
- **g2 (crew):** delegated skill + install wiring — create `commander-delegated/SKILL.md`, extend both installer bundle maps, update `SKILL_INDEX.md`, update `SKILL_NAMES` + add per-skill install tests, and the one admiral description line. All land together because the new dir demands the wiring to keep the suite green. Real `pytest` postcondition; implementer + reviewer crews.
- **g3 (reasoning):** fresh-context selection check — cold subagent (one tier down) given only descriptions + three contexts must name commander / commander-delegated / admiral. Attested transcript; iterate descriptions on failure (honest-null clause).

**Why B:** honors green-at-every-boundary (doctrine invariant), puts crews only on the code gate (doctrine: crews for code/independently-verifiable change; doc gates get inspection-attestation per launch order), and keeps each gate a coherent decision-class bite. The "gate each" instruction is met in spirit — installer+index+tests are one green-boundary bite because they MUST co-land; this co-gating is the surfaced compression.

## Untaken roads (surfaced)
- Candidate A (6 gates) — rejected: red-across-boundaries plan smell.
- A hybrid splitting g2 into "stub-valid dir + minimal wiring" then "polish + per-skill tests" — rejected as fragmenting one coherent code change; the minimal-validity rule is satisfied by g2 shipping the complete valid wiring in one bite.
- Bundling the core into commander-delegated via a new per-skill copy mechanism — rejected: the prose-pointer precedent (workbench engine) is the named, lower-risk route and avoids generalized apparatus.

## Convergence
Delegated mode: converge on Candidate B, cite LAUNCH_ORDER:Mission + Pre-Rulings + Inherited Context (green-boundary + doc-gate-attestation lessons). Admiral ratifies at epic return.
