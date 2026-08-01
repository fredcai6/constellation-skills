# Candidate: measurement-first

The skill is a thin operator around one bundled script. Prose interprets; the script decides *what* is worth looking at. Every finding is deterministic, re-runnable, and diffable against the last run.

## Frontmatter (ships as-is)

```yaml
name: constellation-curator
description: Measure the constellation skills corpus against authoring doctrine and report drift. Use periodically to consolidate accreted lessons — flags oversized bodies, weak descriptions, missing invoker tags, duplicated boilerplate, and missing reference TOCs across skills/. Not for authoring a single skill (write-a-skill) or changing code.
```

## Invoker class: **both**, human-primary

A human runs it on an accrete-then-consolidate cadence ("the corpus feels heavy"); an Admiral may dispatch it as a closeout audit. Body register is human-first — it presents a report for a human to act on — with one delegated-context line so an agent invoker knows findings route to Triage, not to silent edits.

## Interface (deep-module terms)

- **Trigger:** periodic corpus maintenance, human- or cadence-driven. Never a code-change reaction.
- **Input:** the `skills/` tree + `_shared/`; optional `--baseline <path>` to the prior run's JSON for deltas.
- **The script — `scripts/curate_corpus.py` (the module):** one command, `py scripts/curate_corpus.py skills/ [--baseline last.json] [--json out.json]`. Its interface is the report contract, not its internals:
  - **Checks (each emits `flag`/`ok`, never `fail`):** per-skill SKILL.md line+word counts vs soft budgets (200/500-word review thresholds); description lint (third-person test — rejects "I/you"; presence of a when-to-use clause; presence of an exclusion clause; ≤1024 chars); invoker-tag presence (a `<!-- invoker: human|agent|both -->` marker the sweep expects); duplication signatures (normalized-shingle hashes across SKILL.md bodies — surfaces the mandatory-boilerplate / engine-string families as clusters with file lists); TOC presence for any `references/*.md` over 100 lines.
  - **Output format:** a stable, sorted Markdown table (one row per skill) + a duplication-cluster section + a **drift block** (this-run vs `--baseline`: budgets crossed, new/resolved dupes, descriptions changed). Same input → byte-identical output. `--json` emits the machine record that becomes next run's baseline.
  - **Contract guarantee:** the script **flags, never gates**. Exit 0 always (except its own errors). No threshold blocks the run; soft budgets are columns a human reads, not assertions.
- **Spine (SKILL.md, ~40 lines):** (1) run the script; (2) read the table top-down; (3) for each flag, apply the one-line interpretation rule; (4) route confirmed consolidations to Triage / write-a-skill; (5) save the `--json` as the next baseline. A `gated` checklist through the engine, mirroring scout/cartographer.
- **Evidence contract:** the findings *are* the script output — no hand-counted claims. A distribution claim ("N skills over budget") must be a row count from the table, echoing the derive-from-a-command doctrine.
- **Outputs:** `.agent-work/CURATOR_REPORT.md` (the run) + `curator-baseline.json` (diff anchor). No durable truth; no edits.
- **Seams:** consumes the corpus like Scout consumes the map; disposition routes fixes to write-a-skill / Triage the way Scout routes to Cartographer / Triage. Owns *measurement*, not repair.

## Deliberately does NOT

Edit any skill; enforce budgets (flags only); prevent re-accretion (it measures the pile each run, expecting it to regrow); judge prose quality beyond the mechanical lints; author or rewrite skills.

## Self-assessment

- **Depth:** high — one command hides five heterogeneous checks + diff logic behind `run it, read the table`.
- **Locality:** high — logic lives in one script; the SKILL barely changes as checks are added.
- **Seam placement:** the report contract is the seam, drawn where a human reader acts. Strong; the flag/gate line is enforced *in the script*, so the "soft budget" invariant can't erode by prose drift.
- **Testability:** highest of the family — deterministic output is directly golden-file testable; each check is a pure function over a fixture corpus.

## Open risks

- Duplication-signature tuning (shingle size) is a voodoo-constant hazard — must be justified in-code or it silently over/under-clusters.
- Invoker-tag check assumes a marker convention the corpus doesn't yet carry; first run flags all 14 as missing (correct, but noisy) — needs a "first-run" framing.
- Determinism vs. usefulness: mechanical lints can't catch *mis*-tailoring (interrogator's human-facing prose) — that stays human-judgment, outside the script's reach.
