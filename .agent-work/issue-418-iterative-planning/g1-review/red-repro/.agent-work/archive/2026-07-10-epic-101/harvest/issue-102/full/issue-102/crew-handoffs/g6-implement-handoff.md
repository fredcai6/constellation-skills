# Implementer Handoff

## Gate
g6-implement (issue #102, Moves 9, 10 — single-home + pointer-cut)

## Task
Two single-home relocations. Each its own before/after grep pair. Some of this may already be done by
prior work (#99) — verify first and report honest subsumption where you find it.

### Move 9 — dedup-sibling-ids (single home = lessons-auditor; admiral trimmed to reminder + pointer)
- Single home: `skills/lessons-auditor/SKILL.md` (~line 22, "Dedup sibling ids to a confirm, not a new
  add") — the EXECUTING role. KEEP the full doctrine here (it is already the home).
- `skills/admiral/SKILL.md` (~line 56, harvest substep 4) currently INLINE-restates the full
  sibling-ids rule ("sibling lesson ids ... are confirms ... not new adds — a new slug for the same
  defect forks its identity and breaks recurrence counting"). Trim admiral to a MINIMAL operational
  reminder + pointer: keep the one-sentence operative rule (sibling ids for the same defect = confirm/
  amend, not a new add) so the harvest step is NOT stranded, and point to the lessons-auditor home for
  the full rationale (forks-identity / recurrence-counting / export-fingerprint). Do NOT reduce admiral
  to a bare pointer — admiral applies this rule during harvest and does not bundle lessons-auditor, so
  it needs the operative sentence inline.
- After: lessons-auditor carries the full rule once; admiral carries a one-line reminder + pointer.

### Move 10 — design-it-twice restatements (cut to one pointer line each; canonical pre-exists)
Canonical already lives in `skills/_shared/global-orchestrator.md` §"Design-it-twice (standard, not
optional)" and `skills/_shared/design-it-twice-brief.md`. FIRST verify the current state of the two
carriers — prior work (#99) may have already reduced them to pointers:
- `skills/commander/SKILL.md` (~line 97): appears to ALREADY be a pointer ("per the shared
  design-it-twice standard in references/global-orchestrator.md and the references/design-it-twice-brief.md
  contract ... the rules live there, not here"). If so, no cut needed — report subsumed.
- `skills/explorer/SKILL.md` (~lines 62-63, 76): :63 appears to already point at the canonical home;
  :62 describes explorer's OWN design-it-twice EXCURSION TYPE (its operational excursion mechanic —
  KEEP, it is explorer-specific, not a doctrine restatement); :76 instructs running it (keep).
Cut to ONE pointer line ONLY a genuine DOCTRINE RESTATEMENT (the constraint menus / comparison axes /
untaken-road mechanics duplicated from design-it-twice-brief). Do NOT delete the canonical text, and do
NOT strip explorer's excursion-type operational description. If both carriers are already pointers,
report Move 10 as SUBSTANTIALLY SUBSUMED by #99 with grep proof — that is a complete deliverable.

## Test Mode
Inspection-only; keep suite green (`py -m pytest tests/ -q`). g7 pins move 9 (lessons-auditor) + the
design-it-twice canonical.

## Close Criteria
- Move 9: sibling-ids full doctrine reads once in lessons-auditor; admiral trimmed to operative
  reminder + pointer (not stranded, not full-restatement); before/after grep.
- Move 10: no design-it-twice DOCTRINE restatement remains in commander/explorer beyond a pointer +
  (explorer) its own excursion-type description; canonical intact; before/after grep OR subsumed-by-#99
  finding with grep proof.
- No new global-*.md; full suite green.

## Allowed Scope
skills/lessons-auditor/SKILL.md; skills/admiral/SKILL.md (harvest substep only); skills/commander/SKILL.md
(design-it-twice passage only); skills/explorer/SKILL.md (design-it-twice passages only);
skills/_shared/design-it-twice-brief.md + global-orchestrator.md (READ-ONLY confirm canonical; do not edit).

## Specific Exclusions
Do NOT edit the canonical design-it-twice text (global-orchestrator §Design-it-twice, design-it-twice-brief).
Do NOT touch other gates' doctrine in commander/admiral. Do NOT strip explorer's excursion-type mechanic.
manifest/ROADMAP/repo-root stray (#105).

## Constraints
- Single home for sibling-ids = lessons-auditor; admiral keeps operative reminder + pointer.
- Design-it-twice canonical stays put; carriers point, do not restate doctrine.
- Cite pointers by slug/home-name, not by a title that re-introduces the signature (g4 lesson).
- Register: dense, agent-facing.

## Map Anchors (inbound)
- Structural: lessons-auditor/admiral SKILL.md; commander/explorer SKILL.md; _shared design-it-twice-brief.md + global-orchestrator.md.
- Constraint: suite green; canonical design-it-twice text untouched.
- Decision: sibling-ids -> lessons-auditor; design-it-twice restatements -> pointer lines.

## Deliverable Path Check
- Committed — lessons-auditor/admiral/commander/explorer SKILL.md (tracked).
- Local-only — .agent-work/issue-102/crew-handoffs/g6-implement-result.md.

## Required Evidence
Two per-move before/after grep pairs (or subsumption finding with grep); quotes of admiral's trimmed
reminder + pointer and any design-it-twice pointer; confirmation canonical untouched
(`git status --porcelain skills/_shared/design-it-twice-brief.md` empty); suite tail.

## Verification Commands
```bash
cd C:/Programs/constellation-wt-102
grep -rn "forks its identity\|sibling lesson ids" skills/admiral/SKILL.md skills/lessons-auditor/SKILL.md
grep -rn "design-it-twice\|design it twice" skills/commander/SKILL.md skills/explorer/SKILL.md
git status --porcelain skills/_shared/    # design-it-twice-brief.md + global-orchestrator.md must be absent
py -m pytest tests/ -q
```

## Suggested Model Tier
stronger — judgment about what is already a pointer vs a genuine restatement (avoid over-cutting).

## Authority
Homes ruled (sibling-ids -> lessons-auditor; design-it-twice canonical stays). You decide what counts
as restatement-vs-pointer-vs-role-mechanic, and report subsumption honestly.

## Stop Conditions
Stop if cutting would delete canonical text or explorer's excursion mechanic, or if a carrier entangles
with another gate's doctrine.

## Return Format
Return IMPLEMENTER_RESULT (write to .agent-work/issue-102/crew-handoffs/g6-implement-result.md AND as
your final message): per-move disposition (cut OR subsumed), files changed, two before/after grep pairs,
quotes, canonical-untouched confirmation, suite tail, assumptions, stop conditions, out-of-scope
observations, workflow feedback. Your FINAL MESSAGE must be the complete IMPLEMENTER_RESULT.
