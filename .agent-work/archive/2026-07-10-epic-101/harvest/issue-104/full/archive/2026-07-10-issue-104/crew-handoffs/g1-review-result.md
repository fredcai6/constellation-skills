# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` (issue #104, constellation-curator, cluster C)

## Result
`APPROVE`

## Handoff compliance
The handoff asked for independent verification that `scripts/curate_corpus.py` (new,
untracked) honors the gate's binding contract: a mechanical-only measurement pass over
the skills corpus, emitting a human table and `--json`, ALWAYS exiting 0 (flags-never-
gates). Every close criterion in the handoff was checked and reproduced (see below).
Stop conditions did not trigger — nothing failed.

## Scope drift
`git status --short` shows only `?? scripts/curate_corpus.py` — a single new,
untracked file. No skill content, no other script, was edited. The `.agent-work/`
plan/state files present are workflow bookkeeping, explicitly permitted by the
handoff, not product scope. S7 exclusion (no baseline/drift machinery) is honored —
confirmed by full-file read and grep; no code reads/writes a prior run's output.

## Evidence verdict
All four implementer-pasted evidence blocks were independently reproduced (not just
re-read):

1. **Real-corpus table run:** `py scripts/curate_corpus.py` → 60 findings, `exit=0`.
   Table format (skill | check | status | detail) matches exactly.
2. **`--json` run:** piped to `json.load` → `json-ok findings= 60`, `exit=0`.
3. **Unparseable dir → row, not crash:** I built my own throwaway broken corpus at
   `/tmp/brokencorpus2` (independent of the implementer's `/tmp/brokencorpus`) with a
   `goodskill` (valid frontmatter + `invoker: agent` + a `Use when` marker), a
   `badfrontmatter` (unterminated `---`), and a `nosskillmd` (no SKILL.md at all):
   ```
   skill           check    status   detail
   --------------  -------  -------  ------
   badfrontmatter  parse    flagged  unterminated YAML frontmatter (no closing '---')
   goodskill       invoker  ok       invoker=agent
   goodskill       size     ok       body 2 lines / 6 words within budget
   nosskillmd      parse    flagged  no SKILL.md

   4 finding(s): 2 flagged, 0 shortlisted (measurement only — this tool never gates; exit 0 always)
   exit=0
   ```
   No traceback, `exit=0`, matches the implementer's claim.
4. **`grep -n "return 1\|sys.exit(1\|exit(1)" scripts/curate_corpus.py`** → zero
   matches (grep exit code 1 = no match). Full read of `main()` confirms a single
   `return 0` at the end and no other exit path.
5. **`py -m pytest tests/ -q`** → `446 passed, 2 skipped, 143 subtests passed` —
   matches exactly.
6. **Duplication detector bite claim:** reproduced on the real corpus in my own run —
   `commander,commander-delegated` row shows 33 shared 8-word shingles;
   `implementer,reviewer` row shows 35 shared 8-word shingles. Matches the
   implementer's pasted numbers exactly.

Every claim I could not take on faith was reproduced from a fresh run of my own
construction, not copy-pasted from the implementer's report.

## Code/doc quality

Per-criterion findings (each independently reproduced/read, not accepted on report):

- **Flags-never-gates enforced in code:** PASS. `main()` (line ~401-424) has exactly
  one `return 0` and no other return/exit statement in the file. Confirmed by full
  read, by grep (zero matches for gating exits), and by running the error path
  (nonexistent root, and the constructed broken corpus above) — `exit=0` in every case.
- **Mechanical-only / T7:** PASS. `check_description`'s person-pronoun check uses
  `STATUS_SHORTLIST` (never `STATUS_FLAGGED`) with detail text explicitly noting "human
  judges" — it never asserts the register is wrong. The exclusion-clause check
  (`_exclusion_present`) is a pure substring/regex presence test; its status is
  `STATUS_INFO` (present) or `STATUS_FLAGGED` (absent, confusable-pairs only) with
  detail text "has no exclusion clause" — it never judges whether an existing clause
  is *correct*. Grepped the whole file for "wrong"/"mismatch"/"incorrect"/"is a
  procedure" — the only hits are in docstrings/comments describing what the code
  *avoids* doing, not emitted verdict strings.
- **Both outputs:** PASS. Default run prints the readable fixed-width table (64
  lines: header, separator, 60 rows-worth of findings, summary line). `--json` emits
  valid JSON (`json.load` succeeds) with 60 structured findings; both exit 0.
- **Unparseable dir → row, not crash:** PASS. Reproduced independently (see evidence
  block 3 above) — parse rows, exit 0, no traceback, and a co-located good skill still
  measures normally.
- **All five checks present:** PASS. Confirmed `check_size`, `check_description`,
  `check_invoker`, `check_references`, `check_duplication` are all defined and all
  wired into `curate()`. Confirmed in the real-corpus table output that every one of
  these check *names* actually appears in emitted findings: `size`,
  `description-length`, `description-when-to-use`, `description-exclusion`,
  `invoker`, `reference-toc`, `duplication`.
- **Constants justified:** PASS. Every threshold/shingle constant
  (`SKILL_WORD_TARGET`, `SKILL_LINE_HARD_FLAG`, `DESCRIPTION_MAX_CHARS`,
  `DESCRIPTION_MAX_WORDS`, `PERSON_PRONOUNS`, `WHEN_TO_USE_MARKERS`,
  `EXCLUSION_MARKERS`/`EXCLUSION_REDIRECT_RE`, `CONFUSABLE_PAIRS`/`CONFUSABLE_SKILLS`,
  `VALID_INVOKERS`, `REFERENCE_TOC_LINE_THRESHOLD`/`TOC_MARKER_RE`,
  `SHINGLE_SIZE`/`MIN_CLUSTER_SKILLS`) sits under a module-level "CURATOR REVIEW
  HEURISTICS" banner with its own comment block explicitly naming it a soft budget /
  curator review heuristic, never a gate — verified verbatim against the file, not
  just against the implementer's quoted excerpts.
- **No baseline/drift machinery (S7):** PASS. Grep for baseline/drift/previous turns
  up only the docstring disclaiming it and an unrelated use of "drift-elimination
  detector" as a label for the cross-skill shingle-duplication check (a different
  sense of "drift" — shared-doctrine duplication across skills, not a diff against a
  prior run). No code path reads or writes a prior run's output; no `--baseline` flag;
  no persisted state file.
- **Detectors bite:** PASS. Reproduced on the real corpus, independently — the two
  biggest clusters (`commander,commander-delegated` = 33 shared shingles;
  `implementer,reviewer` = 35 shared shingles) appear exactly as claimed.
- **Scope:** PASS. Only `scripts/curate_corpus.py` changed (new/untracked); no skill
  content or other script touched.

Code reads as stdlib-only, `main(argv) -> int` signature honored, minimal and
well-commented; naming and structure consistent with the sibling scripts
(`install_constellation.py`, `check_skill_freshness.py`) already in `scripts/`.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the mechanical-measurement capability
  (table + `--json`, exit 0 always) is exactly what's observed running the script.
- **Constraints not violated:** Yes — exit-0-always, mechanical-only (T7), and
  no-drift-diff (S7) are all honored in code, not just claimed in prose.
- **Notes match the diff:** Yes — the implementer's structural-anchor note ("joins
  the `install_constellation`/`check_skill_freshness` script family... no
  `skills/<skill>/scripts/` dir") checks out: `scripts/` at the repo top level holds
  `install_constellation.py`, `check_skill_freshness.py`, `curate_corpus.py`, and
  several sibling scripts side by side, confirmed by listing the directory.
- **Decision candidates surfaced:** Yes — the heuristic constant values were
  surfaced and justified in-code as this gate's own decision, appropriately scoped
  (no authority beyond this file was needed).
- **Durable context routed:** Yes — the implementer correctly flagged the `invoker:`
  convention-seeding and the `--json` schema as forward-looking context for g2/g3
  rather than trying to resolve them itself.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation beyond
what the implementer already surfaced (invoker: convention seeded for g2 to fill in
on curator's own SKILL.md; `--json` schema as a de-facto contract for g3's
golden-fixture tests). Both are correctly scoped as follow-on gate work, not this
gate's responsibility.

## Blockers
- none

## Out-of-scope observations
- All 15 current skills flag `missing invoker tag` — expected and by design per the
  handoff (the flag seeds the convention; curator gets the first tag in g2). Not a
  defect; confirmed by inspection of the real-corpus run.
- Duplication rows widen the `skill` column considerably when many skills share a
  cluster (e.g. the 9-skill cluster). Readable but wide — implementer already noted
  this as a possible v2 polish item for g5/curator, not actionable here.
- The duplication detector's real findings (commander/commander-delegated,
  implementer/reviewer) are strong, useful signal validating epic-101's premise —
  worth carrying forward into g2's curator narrative, not a defect to fix here.

## Workflow Feedback
- **Handoff gaps:** None material. The handoff was complete: gate, scope, per-check
  spec, constraints, verification commands, and stop conditions were all present and
  specific enough to drive independent reproduction without guessing. One small
  omission carried over from the implementer's own feedback (not new to this
  review): the finding `status` vocabulary (`flagged`/`shortlist`/`info`/`ok`) is
  implied by the handoff's prose but not enumerated as a closed set; I did not need
  it for this review's pass/fail judgment (the code+comments were self-consistent),
  but g3's golden-fixture tests will need it named somewhere shared.
- **Context rediscovered:** None beyond what the handoff already pointed at. The
  handoff's "How to inspect" and "Verification commands" sections were sufficient to
  reproduce every claim without digging elsewhere.
- **Instructions improvised around:** The survey template's `r4-quality` item says
  "Append a check per rule" as a single umbrella imperative; I appended eight
  sibling leaves (`r4a`..`r4h`, one per handoff close-criterion) and recorded the
  umbrella `r4-quality` itself as a pass-through pointer to them, per the engine
  doc's guidance on appending siblings to group per-criterion checks. No real
  friction — the engine doc anticipated this pattern (`append r4a..r4f and attest an
  umbrella item separately`), I just used `record` on the umbrella rather than
  `attest` since a survey item, not a gated attest condition, was in play.
- **What would have made this easier:** Nothing specific to this handoff — it was
  unusually well-specified for a "simple bounded" gate. Carrying forward the
  implementer's own suggestion (name the finding-status vocabulary as a closed set
  in a shared curator contract) would help g3's reviewer, not this one.

## Return status
`complete`
