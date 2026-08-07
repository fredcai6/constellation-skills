# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` (issue #104, constellation-curator epic-101 cluster C)

## Completed slice
Built `scripts/curate_corpus.py` — the curator's MECHANICAL-ONLY measurement pass
over the skills corpus. It emits a human findings table and a `--json` machine
record, and ALWAYS exits 0 (flags-never-gates enforced in code). All five spec
checks are implemented: size, description lint, invoker tag, reference TOC, and
duplication-signature clustering. Checks are factored into importable functions
returning structured `Finding` objects so g3 can assert on them without shelling.

## Scope
**Files changed:**
- `scripts/curate_corpus.py` (new file, top-level bundled-script family)

Working-tree only; not committed (Commander/integrate owns the commit). Plan
artifact `.agent-work/issue-104/g1-implement-plan.json` was created/driven by the
engine (workflow bookkeeping, not a product file).

**Specific exclusions touched:** `no` — no baseline/drift machinery (S7), no
semantic verdicts, no edits to any skill or other script, no gate/exit!=0 path.

## Behavior changed
`yes` — a new capability: mechanical corpus measurement. Running
`py scripts/curate_corpus.py` prints a findings table over `skills/`; `--json`
emits the same findings as structured data; `--root <dir>` / a positional path
measures an arbitrary skills dir. Never gates (exit 0 always).

## Map Impact
- **Structural anchors touched:** `struct:scripts/curate_corpus.py — NEW top-level
  bundled-script, module level. Joins the install_constellation/check_skill_freshness
  script family; bundled per-skill by install_constellation.py (no skills/<skill>/scripts/
  dir — follows the top-level precedent).`
- **Capabilities added/changed/affected:** `capability: mechanical corpus
  measurement / flags-never-gates — observable via the two run modes (table, --json).`
- **Constraints/assumptions touched:** `constraint: exit 0 always (invariant #2,
  enforced in code — no non-zero return path exists); constraint: mechanical-only
  (T7 — shortlists candidates, never renders a semantic verdict); constraint: no
  drift-diff (S7) honored.`
- **Decision candidates / resolved decisions:** `decision: heuristic constant values
  (SKILL_WORD_TARGET=400, SKILL_LINE_HARD_FLAG=500, DESCRIPTION_MAX_CHARS=350,
  DESCRIPTION_MAX_WORDS=50, REFERENCE_TOC_LINE_THRESHOLD=100, SHINGLE_SIZE=8,
  MIN_CLUSTER_SKILLS=2) — chosen and justified in code comments as curator review
  heuristics (soft budgets), calibrated against the current corpus so each flag bites
  outliers without flagging everything.`
- **Claims/evidence produced:** `claim: the duplication detector BITES on the real
  corpus — commander/commander-delegated share 33 shingles, implementer/reviewer
  share 35; backed by the pasted table below.`
- **Triage candidates:** none new from this slice (out-of-scope observations below
  are informational for later gates, not triage items).

## Test mode
**Required:** `test-after` (allowed — golden-fixture tests are a SEPARATE gate g3)
**Satisfied:** `yes` — no test file authored here (g3 owns it). The script is made
cleanly testable per the handoff: `--root`/positional path lets g3 point it at a
fixture corpus, and every check is an importable function returning structured
`Finding` objects (`curate`, `check_size`, `check_description`, `check_invoker`,
`check_references`, `check_duplication`, `parse_frontmatter`). Existing suite stays
green (446 passed, 2 skipped).

## Evidence

### 1. Real corpus run + exit code (the human table)

```bash
cd C:/Programs/constellation-wt-104 && py scripts/curate_corpus.py; echo "exit=$?"
```

```
skill                                                                                           check                    status   detail
----------------------------------------------------------------------------------------------  -----------------------  -------  ------
admiral                                                                                         description-exclusion    info     exclusion clause present (confusable-pair skill)
admiral                                                                                         invoker                  flagged  missing invoker tag (expected one of human/agent/both)
admiral                                                                                         reference-toc            flagged  fleet-doctrine.md is 172 lines (> 100) without a '## Contents' TOC
admiral                                                                                         size                     flagged  body 1370 words > target 400
admiral,cartographer,charter,implementer,interrogator,lessons-auditor,reviewer,scout,workbench  duplication              flagged  3 shared 8-word shingle(s); e.g. "compliance engine drive rule inherited see references global"
admiral,charter,interrogator                                                                    duplication              flagged  1 shared 8-word shingle(s); e.g. "rule inherited see references global everyone md drive"
admiral,commander-delegated                                                                     duplication              flagged  5 shared 8-word shingle(s); e.g. "inherited delegate not replacement doctrine see references global"
admiral,interrogator                                                                            duplication              flagged  1 shared 8-word shingle(s); e.g. "inherited see references global everyone md drive the"
admiral,lessons-auditor                                                                         duplication              flagged  6 shared 8-word shingle(s); e.g. "disposition template delta playbook delta charter nomination constellation"
cartographer                                                                                    description-exclusion    flagged  confusable-pair skill has no exclusion clause (e.g. 'not', 'instead of', 'for X use Y')
cartographer                                                                                    invoker                  flagged  missing invoker tag (expected one of human/agent/both)
cartographer                                                                                    reference-toc            flagged  map-model.md is 273 lines (> 100) without a '## Contents' TOC
cartographer                                                                                    size                     ok       body 23 lines / 300 words within budget
charter                                                                                         invoker                  flagged  missing invoker tag (expected one of human/agent/both)
charter                                                                                         reference-toc            flagged  engineering-rubric.md is 149 lines (> 100) without a '## Contents' TOC
charter                                                                                         reference-toc            flagged  interrogation-protocol.md is 159 lines (> 100) without a '## Contents' TOC
charter                                                                                         reference-toc            flagged  scenario-bank.md is 205 lines (> 100) without a '## Contents' TOC
charter                                                                                         size                     ok       body 27 lines / 275 words within budget
charter,implementer,interrogator,lessons-auditor                                                duplication              flagged  5 shared 8-word shingle(s); e.g. "engine scripts checklist engine py workbench references checklist"
charter,implementer,interrogator,lessons-auditor,reviewer                                       duplication              flagged  6 shared 8-word shingle(s); e.g. "installed skill s bundled engine scripts checklist engine"
charter,implementer,interrogator,lessons-auditor,reviewer,workbench                             duplication              flagged  2 shared 8-word shingle(s); e.g. "absolute path to this installed skill s bundled"
charter,scout                                                                                   duplication              flagged  1 shared 8-word shingle(s); e.g. "template json as a gated checklist through the"
commander                                                                                       description-exclusion    info     exclusion clause present (confusable-pair skill)
commander                                                                                       invoker                  flagged  missing invoker tag (expected one of human/agent/both)
commander                                                                                       size                     ok       body 12 lines / 200 words within budget
commander,commander-delegated                                                                   duplication              flagged  33 shared 8-word shingle(s); e.g. "context understand plan execute reconcile triage review feedback"
commander-delegated                                                                             description-exclusion    info     exclusion clause present (confusable-pair skill)
commander-delegated                                                                             description-length       flagged  397 chars / 63 words > budget 350 chars / 50 words
commander-delegated                                                                             invoker                  flagged  missing invoker tag (expected one of human/agent/both)
commander-delegated                                                                             size                     ok       body 14 lines / 317 words within budget
docent                                                                                          invoker                  flagged  missing invoker tag (expected one of human/agent/both)
docent                                                                                          size                     flagged  body 960 words > target 400
explorer                                                                                        description-exclusion    flagged  confusable-pair skill has no exclusion clause (e.g. 'not', 'instead of', 'for X use Y')
explorer                                                                                        description-when-to-use  flagged  no when-to-use marker (e.g. 'Use when ...')
explorer                                                                                        invoker                  flagged  missing invoker tag (expected one of human/agent/both)
explorer                                                                                        size                     flagged  body 1621 words > target 400
explorer,prototyper                                                                             duplication              flagged  2 shared 8-word shingle(s); e.g. "inherited doctrine see references global everyone md scoped"
implementer                                                                                     invoker                  flagged  missing invoker tag (expected one of human/agent/both)
implementer                                                                                     size                     ok       body 18 lines / 250 words within budget
implementer,lessons-auditor                                                                     duplication              flagged  1 shared 8-word shingle(s); e.g. "template md reference workbench references checklist engine md"
implementer,reviewer                                                                            duplication              flagged  35 shared 8-word shingle(s); e.g. "instruction that was ambiguous missing or improvised around"
interrogator                                                                                    description-exclusion    flagged  confusable-pair skill has no exclusion clause (e.g. 'not', 'instead of', 'for X use Y')
interrogator                                                                                    invoker                  flagged  missing invoker tag (expected one of human/agent/both)
interrogator                                                                                    size                     flagged  body 415 words > target 400
lessons-auditor                                                                                 description-when-to-use  flagged  no when-to-use marker (e.g. 'Use when ...')
lessons-auditor                                                                                 invoker                  flagged  missing invoker tag (expected one of human/agent/both)
lessons-auditor                                                                                 size                     flagged  body 903 words > target 400
prototyper                                                                                      invoker                  flagged  missing invoker tag (expected one of human/agent/both)
prototyper                                                                                      size                     flagged  body 799 words > target 400
reviewer                                                                                        invoker                  flagged  missing invoker tag (expected one of human/agent/both)
reviewer                                                                                        size                     ok       body 20 lines / 328 words within budget
scout                                                                                           description-exclusion    flagged  confusable-pair skill has no exclusion clause (e.g. 'not', 'instead of', 'for X use Y')
scout                                                                                           invoker                  flagged  missing invoker tag (expected one of human/agent/both)
scout                                                                                           size                     ok       body 32 lines / 310 words within budget
triage                                                                                          invoker                  flagged  missing invoker tag (expected one of human/agent/both)
triage                                                                                          size                     flagged  body 504 words > target 400
workbench                                                                                       invoker                  flagged  missing invoker tag (expected one of human/agent/both)
workbench                                                                                       reference-toc            flagged  checklist-engine.md is 114 lines (> 100) without a '## Contents' TOC
workbench                                                                                       size                     ok       body 41 lines / 268 words within budget

60 finding(s): 49 flagged, 0 shortlisted (measurement only — this tool never gates; exit 0 always)
exit=0
```

**Result:** `pass` — table printed, `exit=0`.

### 2. `--json` run + validity + exit code

```bash
py scripts/curate_corpus.py --json | head -40         # (head shows valid JSON prefix)
py scripts/curate_corpus.py --json | python -c "import sys,json;d=json.load(sys.stdin);print('json-ok findings=',len(d['findings']))"; echo "exit=$?"
```

```
{
  "root": "skills",
  "heuristics": {
    "SKILL_WORD_TARGET": 400,
    "SKILL_LINE_HARD_FLAG": 500,
    "DESCRIPTION_MAX_CHARS": 350,
    "DESCRIPTION_MAX_WORDS": 50,
    "REFERENCE_TOC_LINE_THRESHOLD": 100,
    "SHINGLE_SIZE": 8,
    "MIN_CLUSTER_SKILLS": 2,
    "CONFUSABLE_SKILLS": [
      "admiral", "cartographer", "commander", "commander-delegated",
      "curator", "explorer", "interrogator", "scout", "write-a-skill"
    ]
  },
  "findings": [
    { "skill": "admiral", "check": "size", "status": "flagged",
      "detail": "body 1370 words > target 400", "words": 1370, "lines": 59 },
    ...
  ]
}
json-ok findings= 60
exit=0
```

**Result:** `pass` — `json.load` succeeds, 60 structured findings, `exit=0`. Each
duplication finding also carries `skills`, `shingle_count`, `example` fields for g3
to assert on; size/description/reference findings carry their numeric measures.

### 3. Unparseable / broken-dir behavior + exit code

Built a throwaway corpus in the scratchpad with three dirs: one good skill, one with
malformed (unterminated) frontmatter, one with no SKILL.md at all.

```bash
py scripts/curate_corpus.py --root /tmp/brokencorpus; echo "exit=$?"
```

```
skill           check    status   detail
--------------  -------  -------  ------
badfrontmatter  parse    flagged  unterminated YAML frontmatter (no closing '---')
goodskill       invoker  ok       invoker=agent
goodskill       size     ok       body 2 lines / 2 words within budget
nosskillmd      parse    flagged  no SKILL.md

4 finding(s): 2 flagged, 0 shortlisted (measurement only — this tool never gates; exit 0 always)
exit=0
```

**Result:** `pass` — each unparseable skill becomes a `check="parse"` flagged ROW
(malformed frontmatter → the parse error text; missing file → "no SKILL.md"). No
traceback, `exit=0`. The good skill still parses and is checked normally.

### 4. Deliverable path check (rides into the diff)

```bash
git check-ignore scripts/curate_corpus.py; echo "check-ignore-exit=$?"   # => 1 (not ignored)
git status --short scripts/                                               # => ?? scripts/curate_corpus.py
```

**Result:** `pass` — not gitignored (`check-ignore` exits 1); tracked as a new file.

### 5. Existing suite stays green (no tests added here)

```bash
py -m pytest tests/ -q      # => 446 passed, 2 skipped, 143 subtests passed; exit 0
```

**Result:** `pass`.

## Named constants with their justifying comments (quoted)

All are declared under a module-level `CURATOR REVIEW HEURISTICS` banner:
> "Every constant below is a SOFT BUDGET a curator uses to decide what to LOOK at
> — never a gate. Over-budget produces a findings row for a human to weigh, never a
> failure. Seed values are calibrated against the current corpus so a flag means
> something (it bites the outliers) without flagging everything."

- `SKILL_WORD_TARGET = 400` / `SKILL_LINE_HARD_FLAG = 500`
  > "SKILL.md body size. The corpus norm is a tight one-screen skill; the long
  > outliers (admiral/docent/explorer) are the ones worth a curator's eye. ~400
  > words is the target a well-scoped skill sits under; 500 lines is a hard line
  > flag well above every current skill (max is docent at 143), so tripping it
  > signals a skill that has grown into a manual and should probably be split or
  > moved to references/."

- `DESCRIPTION_MAX_CHARS = 350` / `DESCRIPTION_MAX_WORDS = 50`
  > "Description register. A skill `description:` is the trigger a router scans; it
  > should read as one or two scannable sentences. The current corpus runs 105-397
  > chars / 16-63 words, so a soft ceiling of 350 chars / 50 words flags only the
  > longest, chattiest descriptions — the ones a curator would tighten."

- `PERSON_PRONOUNS = ("i", "you", "your", "we", "our", "us")`
  > "First/second-person pronoun tokens. Third-person is the description convention,
  > but whether a given \"you\"/\"we\" is actually a register slip is a HUMAN judgment
  > — presence here only SHORTLISTS the description for review; it never asserts the
  > description is wrong (T7 mechanical-only)."

- `WHEN_TO_USE_MARKERS = ("use when", "use to", "use for", "use during")`
  > "When-to-use marker. A description should carry a triggering-condition clause.
  > These lowercase markers detect its PRESENCE mechanically; absence is flagged as
  > \"no when-to-use marker\" (mechanical absence, not a quality verdict)."

- `EXCLUSION_MARKERS` + `EXCLUSION_REDIRECT_RE`
  > "Exclusion-clause markers. A description may carry a \"don't confuse me with X\"
  > clause. These detect its PRESENCE mechanically. Absence is only FLAGGED for the
  > known confusable-pair skills below; for every other skill absence is fine."
  > "...plus the \"for <other-thing> use <X>\" redirect pattern:"

- `CONFUSABLE_PAIRS` / `CONFUSABLE_SKILLS`
  > "Confusable pairs (epic-101 cross-cutting rule 1): skills a router most easily
  > mixes up. ONLY these skills are flagged when their description lacks an exclusion
  > clause — the disambiguation matters most where confusion is likely. Encoded as
  > pairs (documents WHY each skill is here); membership is the union."

- `VALID_INVOKERS = ("human", "agent", "both")`
  > "Invoker tag. The `invoker:` frontmatter key declares who invokes a skill. On
  > the current corpus only curator will carry one — every other skill flags here,
  > which is EXPECTED: the flag is how the convention gets seeded."

- `REFERENCE_TOC_LINE_THRESHOLD = 100` / `TOC_MARKER_RE`
  > "Reference TOC. A references/*.md long enough to need navigation should carry a
  > table-of-contents heading. 100 lines is the soft threshold above which a curator
  > expects a \"## Contents\" anchor; shorter files scroll fine without one."

- `SHINGLE_SIZE = 8` / `MIN_CLUSTER_SKILLS = 2`
  > "Duplication-signature clustering (the drift-elimination detector). We shingle
  > each SKILL.md body into k-word windows and report shingles shared across distinct
  > skills. k=8 is long enough that a match is a genuinely shared doctrine sentence
  > (not an incidental short phrase like \"through the engine\") yet short enough to
  > still match after small edits around it. A cluster needs the same shingle in >= 2
  > DISTINCT skills to report."

## Docs/contracts touched
- none — scope was `scripts/curate_corpus.py` only. (The `--json` schema shape and
  the `invoker:` convention are new de-facto contracts introduced by this file; g2
  seeds `invoker:` on curator's own SKILL.md and g4 wires the bundling.)

## Assumptions
- **Skill-dir identity:** an immediate subdirectory of `--root` whose name does NOT
  start with `_` or `.` is a candidate skill. This skips `skills/_shared` (not a skill)
  while still flagging a genuine skill dir that is missing its SKILL.md. Justified in
  the `_skill_dirs` docstring.
- **Frontmatter shape:** the corpus uses flat single-line `key: value` scalars, so a
  minimal stdlib parser (no PyYAML dep) is sufficient; block scalars / nested maps are
  not expected and a key it cannot parse is skipped, not treated as fatal. Missing or
  unterminated frontmatter IS fatal-per-skill → a parse row. Noted in `parse_frontmatter`.
- **Exclusion detection is presence-only** (marker substrings + a `for ... use` regex);
  per T7 it never judges whether the clause is CORRECT, only whether one exists.
- **Duplication grouping:** shared shingles are grouped by the exact frozenset of
  sharing skills so the human table shows one row per shared-signature pattern rather
  than one row per shingle; the raw per-cluster counts + an example shingle are kept in
  the `extra` fields for machine consumers.

## Stop conditions hit
- none. Every spec-named check was expressible mechanically without a semantic
  judgment. The two checks that flirt with semantics (person-register, exclusion-clause
  correctness) were kept strictly mechanical: person-register only SHORTLISTS (status
  `shortlist`, never `flagged`/verdict), and exclusion only reports presence/absence,
  never correctness — honoring the T7 boundary rather than faking determinism.

## Out-of-scope observations
- **All 15 current skills flag `missing invoker tag`** — expected and by design (the
  handoff calls this out: the flag seeds the convention; curator gets the first tag in
  g2). Not a defect.
- **Table width:** the duplication rows widen the `skill` column because they join many
  skill names (e.g. the 9-skill `Compliance engine drive rule inherited...` cluster). It
  is readable but wide. A future v2 could render duplication clusters in a separate
  section from per-skill findings — noting for g5/curator polish, not acting on it here
  (would be scope creep).
- **The duplication detector confirms the epic's premise:** the two biggest clusters are
  commander/commander-delegated (33 shared shingles) and implementer/reviewer (35) —
  exactly the shared-doctrine drift epic-101 targets. Useful signal for the curator
  skill's own narrative (g2), surfaced for Commander.

## Workflow Feedback
- **Handoff gaps:** The handoff was unusually complete — task, protected intent (the two
  invariants), per-check spec, exclusions, evidence, stop conditions, and an explicit
  "you DECIDE" list were all present. One genuinely underspecified point: the **status
  vocabulary** for findings (flagged vs shortlist vs info vs ok) was implied by the prose
  ("shortlist" for person-check, "flag" elsewhere, "info at most" for exclusion) but never
  enumerated as a closed set. I inferred a 4-value set (`flagged`/`shortlist`/`info`/`ok`).
  g3 will assert against these strings, so naming the exact vocabulary in the handoff (or
  in a shared curator contract) would remove a guess at the g1/g3 seam.
- **Context rediscovered:** I had to measure the corpus myself (SKILL.md line/word counts,
  description char/word spread, which references exceed 100 lines, which already carry a
  `## Contents`) to calibrate the constants so flags bite without flagging everything. The
  handoff gave seed numbers but the calibration data was mine to gather. A one-line "current
  corpus: N skills, descriptions 105-397 chars, longest body ~1600 words, 7 refs >100 lines,
  only commander-core has a TOC" in the handoff would have saved the measurement pass —
  though gathering it was cheap and arguably my job.
- **Instructions improvised around:** The IMPLEMENTER_PLAN template's `m1` imperative is
  written around a TDD red/green flow; for a `test-after` mode where g3 owns the tests, I
  collapsed to the single green/observable postcondition exactly as the template's own note
  permits ("collapse to the single green/observable postcondition"). No real friction — the
  template anticipated this case.
- **What would have made this easier:** Enumerate the finding `status` vocabulary as a
  closed set in the handoff (or a tiny shared curator-contract fragment both g1 and g3
  read), so the measurement tool and its golden-fixture tests agree on the exact strings
  by construction rather than by g3 reverse-engineering g1's choices.

## Return status
`complete`
