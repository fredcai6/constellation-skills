# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-review` (issue #104, constellation-curator)

## Result
`APPROVE`

verdict: APPROVE

## Handoff compliance
The handoff asked for `skills/curator/SKILL.md` (new, SKILL.md-only) plus the one
`SKILL_NAMES` fixture line in `tests/test_install_constellation.py`. Both are present and
match. Driven through the engine as a survey
(`.agent-work/issue-104/g2-review/review.json`, 11 items, all recorded pass, consolidated
`verdict=APPROVE`).

## Scope drift
None. Reproduced `git status --short`:
```
 M tests/test_install_constellation.py
?? skills/curator/
```
`ls skills/curator/` -> `SKILL.md` only (no `references/`, no `templates/`). No
`install_constellation.py` edit, no bundle entries, no new curator install tests, no other
skill touched, no report template shipped.

## Evidence verdict
All required evidence reproduced independently and matches the implementer's report:

1. **Frontmatter** — `name: constellation-curator` present; `invoker: human` present.
   Description scanned for `PERSON_PRONOUNS` (i/you/your/we/our/us) — none present
   (third-person). Contains `"Use when a human runs a corpus-health pass"` (when-to-use
   marker). Contains `"not architecture-map auditing (scout) or authoring a new skill
   (write-a-skill)"` — names both `scout` and `write-a-skill` by name and matches the
   `EXCLUSION_MARKERS` `"not "` token.

2. **Dogfood.** Reproduced:
   ```
   $ py scripts/curate_corpus.py --root skills | grep -i "^curator"
   curator   description-exclusion    info     exclusion clause present (confusable-pair skill)
   curator   invoker                  ok       invoker=human
   curator   size                     ok       body 40 lines / 400 words within budget
   ```
   No `description-when-to-use` flag row, no `description-length` flag row, no `parse`
   row for curator. Full run exit code = 0 (confirmed separately).

3. **Body coverage.** Read `SKILL.md` against `scripts/curate_corpus.py` source
   line-by-line. All 8 required topics present and consistent with the tool's actual
   behavior: Trigger (human-only, never scheduled/agent-dispatched/code-change-reaction —
   matches `invoker: human`), Invariant #1 measure-before-mend (starts with
   `curate_corpus.py`; T7 mechanical/semantic split matches the script's docstring
   verbatim), Invariant #2 flags-never-gates (exit 0, rows not failures — matches the
   script's hardcoded `return 0`), Mend (in-place mechanical, git-diff review gate, fixed
   linear pass / no engine checklist), Route (design decisions -> Triage), Outputs
   (`CURATOR_REPORT.md` + `--json`, inline, no template — matches script's `--json` flag),
   Portfolio duty (optional/dormant until #106, no dependency), Error modes (unparseable
   dir = row `check="parse"`, first-run flags all invoker tags = expected — matches
   script's `CorpusParseError` handling and `VALID_INVOKERS` comment). No contradictions
   found.

4. **Green-at-boundary.** Reproduced:
   ```
   $ git diff tests/test_install_constellation.py
   +    "constellation-curator",
   ```
   Exactly one insertion, nothing else changed in that file.
   ```
   $ py -m pytest tests/ -q
   446 passed, 2 skipped, 150 subtests passed in 15.25s
   ```
   Matches the implementer's reported baseline (446 passed / 2 skipped; subtests rose
   143->150 from the 16th skill iterating the parametrized full-set install test).

5. **Scope.** Confirmed above (Scope drift section).

## Code/doc quality
SKILL.md reads as a tight single-pass doctrine document, matches house style of sibling
skills, and does not contradict `curate_corpus.py`'s actual mechanics anywhere checked.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the dogfood run and pytest tail both back
  the claimed behavior exactly.
- **Constraints not violated:** Yes — `invoker: human` seeded only on curator (all 15
  other skills still flag missing, by design per Error modes section); no engine
  checklist for mend (per doctrine); no report template shipped.
- **Notes match the diff:** Yes — Map Impact notes (struct/capability/constraint/decision/
  claims) in the implementer result correspond exactly to the two changed paths; no
  overstated or missing structural/capability impact.
- **Decision candidates surfaced:** N/A for authority beyond what the handoff's Authority
  block already delegated (description wording/section order) — correctly noted as the
  implementer's own call.
- **Durable context routed:** Yes — the `invoker:` convention rollout to the rest of the
  corpus is correctly deferred as a future Triage candidate, not silently done here.

## Reconciliation check
No architecture divergence. One informational (non-blocking) observation flagged as a
triage candidate via the engine (`tc1`): `curate_corpus.py`'s own duplication check flags
a shared-boilerplate cluster (`admiral,cartographer,charter,curator,implementer,
interrogator,lessons-auditor,reviewer,scout,workbench`) sharing the line
`"Compliance/engine-drive rule: inherited — see references/global-everyone.md."` This is
a pre-existing corpus convention curator's SKILL.md correctly follows (not introduced by
this change); a future curator run may fold it into `_shared` per its own Route doctrine.

## Blockers
- none

## Out-of-scope observations
- (informational, not blocking) The corpus-wide `Compliance/engine-drive rule: inherited`
  boilerplate line is now shared by 10 skills including curator — flagged via
  `flag-candidate` (`tc1`) in the review survey for Triage's awareness, not a defect in
  this change.

## Workflow Feedback
- **Handoff gaps:** None. The handoff was concise and complete — five close criteria,
  explicit verification commands, exact scope list. Every command reproduced cleanly on
  the first try with no ambiguity about what "pass" meant.
- **Context rediscovered:** None beyond what was pointed at — the handoff named exactly
  the two files to read (`SKILL.md`, `curate_corpus.py`) plus the diff command, and that
  was sufficient to verify all 5 criteria without further digging.
- **Instructions improvised around:** The generic `r4-quality` survey item's imperative
  ("Append a check per rule") maps loosely onto 5 named close criteria rather than
  discrete "project rules"; I appended `r4a`..`r4e` as flat siblings (one per close
  criterion) mirroring the g1-review precedent already in this worktree
  (`.agent-work/issue-104/g1-review/review.json`), which resolved the ambiguity cleanly.
- **What would have made this easier:** Nothing concrete — this was a clean, fast
  verification with no dead ends. If anything, the handoff's numbered close-criteria list
  translated almost 1:1 into survey items, which is a good pattern to keep.

## Return status
`complete`
