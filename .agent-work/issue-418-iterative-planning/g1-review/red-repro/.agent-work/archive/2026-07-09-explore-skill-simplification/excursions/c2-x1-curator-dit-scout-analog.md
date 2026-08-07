# Candidate: scout-analog

`constellation-curator` as an evidence-first audit role, built to the shape of `scout`: measure → audit against doctrine → ranked cited report → triage handoff. Curator finds and ranks; the edits flow out.

## Frontmatter draft

```yaml
name: constellation-curator
description: Audit the constellation skills corpus against skill-authoring doctrine and report ranked, cited fix candidates. Use on a periodic maintenance cadence to consolidate accreted lessons — description fields, invoker tagging, terminology drift, word-budget bloat, missing reference TOCs, cross-skill duplication. Does not edit skills, set hard gates, or prevent re-accretion; it measures, ranks, and hands off.
```

## Invoker class: both (human-cadence primary)

Mirrors scout exactly. A human runs it periodically ("the corpus feels bloated / it's been N epics"); an Admiral/Commander may dispatch it as a maintenance subagent. Register is **agent-facing** like scout and lessons-auditor — it produces a report for a downstream fixer, not prose a human executes.

## The interface (deep-module terms)

**Trigger:** periodic corpus-maintenance cadence, not a scheduler and not per-run (that is lessons-auditor). One verb for the caller: *run curator on the corpus, get ranked cited candidates.*

**Spine** — `templates/CURATOR.template.json`, a `gated` checklist through the engine (workbench `references/checklist-engine.md`), three steps echoing scout's `context/audit/report`:

1. **census** — measure first, like scout loads the map first. Per-skill line/word counts and duplication greps (signature-phrase `grep -c`, `uniq -c`), an x2-style corpus survey. This is the evidence, produced by command.
2. **audit** — walk each skill against six doctrine checks (`references/curator-doctrine.md`, TOC'd — dogfoods its own rule): (a) description = third-person + what + when + exclusion clause; (b) invoker class declared and body register matches it; (c) consistent-terminology (one term per concept); (d) soft word budgets — **flag as review candidate, never a gate**; (e) reference files >100 lines carry a TOC; (f) duplication → factor-to-`_shared` candidate.
3. **report** — write `.agent-work/CURATOR_REPORT.md`, ranked candidates, then route to Triage.

**Evidence contract:** every candidate cites `file:line`; every *distribution* claim ("boilerplate in 10 files") cites its command output, not an impression — the scout "challenge the map with code" rule, and the user's derive-from-command discipline.

**Outputs:** `CURATOR_REPORT.md` (rank, class, anchor, measured evidence, fix direction, confidence, disposition), plus issue-ready `TRIAGE_RECOMMENDATION` candidates. No durable truth written; no edits.

**Seams:** reuses Triage (same handoff scout uses) and the shared engine. Unlike scout it has **no Cartographer arm** — the corpus has no architecture map, so *all* dispositions route to Triage/Commander. Against **lessons-auditor**: auditor *adds* per-run; curator *consolidates* periodically. Clean add-vs-consolidate split.

## Deliberately does NOT

Edit skills · set hard word-count gates (budgets are heuristics) · **prevent re-accretion** (no standing enforcement — it cleans up after accretion by design) · audit product code or the architecture map (scout/cartographer) · nominate run-lessons (lessons-auditor) · author the doctrine (it applies x1 best-practices).

## Self-assessment

- **Depth** — high. One trigger hides the whole measure+six-check machine; caller learns one verb.
- **Locality** — strong. Corpus-doctrine knowledge lives in one skill instead of scattered as reminders across every SKILL.md. Deletion test: remove curator and consolidation discipline reappears ad hoc everywhere → it earns its keep.
- **Seam placement** — audit|edit, exactly where scout draws it; the report is verifiable without any edit landing.
- **Testability** — the report is the test surface: each candidate falsifiable against its citation, each distribution claim against its command; each doctrine check exercisable on a known-bad input.

## Open risks

1. Curator↔lessons-auditor (consolidate vs add) is a **single-adapter** seam — a guess until one epic runs both without overlap/gap.
2. Soft budgets are a letter-vs-spirit dodge zone — a run could quietly harden them into gates or ignore them; the report must mark the reading advisory.
3. Doctrine drift — curator encodes external best-practices; if that shifts, the checklist goes stale. Reference-not-inline mitigates but does not solve.
4. Windows: census greps/counts must be POSIX-form via the Bash tool (`windows.md`).
