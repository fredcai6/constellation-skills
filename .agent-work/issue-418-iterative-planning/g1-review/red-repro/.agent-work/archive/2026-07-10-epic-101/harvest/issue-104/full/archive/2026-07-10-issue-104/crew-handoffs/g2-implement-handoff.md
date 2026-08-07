# Implementer Handoff

Concise fragments. Paste, don't point — you start cold.

## Gate
`g2-implement` (issue #104, constellation-curator, epic-101 cluster C)

## Task
Create `skills/curator/SKILL.md` — the new `constellation-curator` skill (SKILL.md
ONLY; no references/ or templates/ dir). AND make the one green-at-boundary test-fixture
edit described under "Green-at-boundary fix" so the suite stays green the moment the new
skill dir exists.

Repo: `C:\Programs\constellation-wt-104` (branch constellation/issue-104). The curator
is a HUMAN-ONLY-invoked, periodic corpus-maintenance skill: measure -> mend -> route.
Its measurement pass is the script built in G1: `scripts/curate_corpus.py` (read it and
its report at `.agent-work/issue-104/crew-handoffs/g1-implement-result.md` so the SKILL.md
matches the tool's ACTUAL behavior).

## Protected Intent
The SKILL.md must read as ONE deliberately-written document (single-pass absorbable),
tailored to a human invoker, and must correctly describe the measure-then-mend-then-route
lifecycle without contradicting `curate_corpus.py`. It seeds the invoker-tag convention.

## Reference examples (read these for house style)
- `skills/scout/SKILL.md` — the closest sibling (periodic, human-cadence,
  measure->report-candidates->route). Match its register and shape.
- `skills/triage/SKILL.md` — the route/fixed-linear-pass precedent ("No checklist. Work
  through the candidates directly."). Curator's mend pass is the same shape.
- Frontmatter of `skills/admiral/SKILL.md` and `skills/commander-delegated/SKILL.md` —
  note how the `description:` carries an exclusion clause for a confusable sibling.

## Close Criteria (each proven in your IMPLEMENTER_RESULT)
1. **Frontmatter** with exactly these keys:
   - `name: constellation-curator`
   - `description:` — THIRD-PERSON (no "I"/"you"/"we"), states WHAT it does + WHEN to use
     it (must contain a "Use when ..." triggering clause), and carries an EXCLUSION CLAUSE
     distinguishing it from its confusable siblings **scout** and **write-a-skill**
     (write-a-skill is an out-of-corpus sibling — word the clause generically, e.g.
     "...not architecture-map auditing (scout) or authoring a new skill (write-a-skill)").
     Keep it under ~350 chars / 50 words so it passes the curator's own description-length
     heuristic.
   - `invoker: human` — this seeds the convention (cross-cutting rule 4). It must be a
     frontmatter key so `curate_corpus.py`'s mechanical invoker-tag check detects it.
   - DOGFOOD CHECK: after writing, run `py scripts/curate_corpus.py --root skills` and
     confirm the `curator` rows show invoker=ok, a when-to-use marker present, and an
     exclusion clause present (info, not flagged). Size within budget.
2. **Body** (rule-plus-why register; emphasis only at mechanism-backed gates) covering:
   - **Trigger:** a human runs it as periodic corpus maintenance ("run the curator");
     NEVER scheduled, NEVER a code-change reaction, NEVER agent-dispatched. (Note the
     untaken road: a report-only delegated mode, revivable later — one line.)
   - **Invariant #1 — measure before mend:** every invocation BEGINS by running
     `scripts/curate_corpus.py` over `skills/`. Name what it measures (size, description
     lint, invoker-tag presence, duplication-signature clusters, reference TOC) and state
     the decidability-honesty rule (T7): the script checks only mechanical properties and
     shortlists candidates; SEMANTIC judgments (is this clause a procedure? does the
     register match the tag?) are the HUMAN mend pass's job, never the script's verdict.
   - **Invariant #2 — flags never gates:** the script always exits 0; findings are rows,
     not failures; the soft-budget rule cannot erode into a gate. Distribution claims come
     from the table, never impressions.
   - **Mend:** mechanical, verifiable-by-inspection fixes (description wording, TOCs,
     terminology, register touch-ups, boilerplate that re-accreted since last run) applied
     IN PLACE. Git diff is the review gate. NO engine checklist — a fixed linear pass
     (triage precedent).
   - **Route:** design decisions (move doctrine to `_shared`, re-scope a skill, kill a
     section) become TRIAGE recommendations, never silent curator edits.
   - **Outputs:** `CURATOR_REPORT.md` (findings, mends applied, routes, before/after
     measurement) + the script's `--json` machine record. No durable-truth writes beyond
     the mends themselves. Describe the report's shape INLINE (do NOT ship a template file).
   - **Portfolio duty — OPTIONAL and dormant:** state that it is inactive until the eval
     harness (issue #106) exists, that curator has NO dependency on it, and that curator's
     core (measure/mend/route) stands alone. One short paragraph.
   - **Error modes:** an unparseable skill dir is a report ROW, not a crash; the first run
     flags all skills for missing invoker tags (expected — it seeds the convention).
3. **Green-at-boundary fix (REQUIRED):** `tests/test_install_constellation.py` hardcodes a
   `SKILL_NAMES` list (currently 15 entries) that a full-set install assertion compares for
   equality. `discover_skills()` installs every non-`_` dir under `skills/`, so the moment
   `skills/curator/SKILL.md` exists the installed set becomes 16 and that assertion reds.
   Add `"constellation-curator"` to the `SKILL_NAMES` list so the assertion stays green.
   (This is install-fixture maintenance FORCED by the new dir — it is NOT the G4 install-
   wiring feature, which adds curator's script/reference BUNDLE entries and dedicated
   curator install tests. Do not add bundle entries or new install tests here.)
4. `py -m pytest tests/ -q` is GREEN.

## Allowed Scope
- `skills/curator/SKILL.md` (new).
- `tests/test_install_constellation.py` — ONLY adding `"constellation-curator"` to the
  `SKILL_NAMES` list (the green-at-boundary fixture edit). Touch nothing else in that file.

## Specific Exclusions
- Do NOT create `skills/curator/references/` or `skills/curator/templates/`.
- Do NOT edit `install_constellation.py` (that is G4 — bundle wiring).
- Do NOT add curator install tests or bundle entries (G4).
- Do NOT retro-tag or edit any OTHER skill's SKILL.md.
- Do NOT ship a CURATOR_REPORT template file.

## Constraints
- Third-person description; rule-plus-why body register; one-hop (no deep reference chains).
- Match existing SKILL.md house style (frontmatter `---` block, `# Constellation Curator`
  heading).
- The `description:` must be a single-line YAML scalar (the installer's frontmatter parser
  reads flat `key: value` lines — no block scalars).

## Map Anchors (inbound)
- **Structural:** `skills/curator/SKILL.md` — NEW skill dir.
- **Capability:** human-invoked measure-then-mend-then-route.
- **Constraints:** human-only invoker; no scheduling/agent-dispatch; no engine checklist.
- **Decision anchors:** DC2 invoker-tag = frontmatter `invoker: human`; DC3 no report
  template (describe inline). (DC1 reference-bucket is G4's concern, not yours.)
- **Evidence:** the description passes curator's own description checks (dogfood).

## Deliverable Path Check
- **Committed** — `skills/curator/SKILL.md`; `git check-ignore` exits 1 (not ignored),
  verified before dispatch.
- **Committed** — `tests/test_install_constellation.py` (already tracked; you edit one list).

## Required Evidence (paste into IMPLEMENTER_RESULT)
- The full `skills/curator/SKILL.md` content.
- The dogfood run: `py scripts/curate_corpus.py --root skills` output rows for `curator`
  (showing invoker ok, when-to-use present, exclusion present, size ok), with exit code.
- The one-line diff to `SKILL_NAMES`.
- `py -m pytest tests/ -q` tail showing green.

## Verification Commands
```bash
cd C:/Programs/constellation-wt-104
py scripts/curate_corpus.py --root skills | grep -i "^curator" ; py scripts/curate_corpus.py --root skills >/dev/null; echo "exit=$?"
py -m pytest tests/ -q
py scripts/install_constellation.py --agent codex --scope user --dest /tmp/curator-install-check --skills curator --dry-run  # discovers curator
```

## Suggested Model Tier
`stronger — reason: authored doctrine document; register + boundary discipline matter`

## Authority
Decided (do not revisit): human-only invoker; invoker tag = frontmatter `invoker: human`;
no report template; SKILL.md-only (no references). You DECIDE: exact wording, section
order, the description sentence (within the constraints above).

## Stop Conditions
Stop and return if: you would need to edit a file outside the allowed scope; the
description cannot satisfy both the length budget and the exclusion-clause requirement;
required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, evidence (pasted runs above),
assumptions, stop conditions hit, out-of-scope observations, workflow feedback. WRITE the
full IMPLEMENTER_RESULT as your final message AND to the result path you are given, before
going idle.
