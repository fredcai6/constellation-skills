# Implementer Handoff

Concise fragments. Paste, don't point — you start cold.

## Gate
`g1-implement` (issue #104, constellation-curator epic-101 cluster C)

## Task
Build `scripts/curate_corpus.py` — the curator's MEASUREMENT pass over the skills
corpus. It performs MECHANICAL-ONLY checks and emits a human findings table plus a
`--json` machine record. It is a measurement/flagging tool, NOT a linter that fails
a build: it ALWAYS exits 0.

Repo: `C:\Programs\constellation-wt-104` (branch constellation/issue-104). Scripts
live top-level in `scripts/` and are bundled per-skill by `install_constellation.py`
(there are no `skills/<skill>/scripts/` dirs — follow the top-level precedent).

## Protected Intent
The curator's invariant #2 is FLAGS-NEVER-GATES: soft budgets cannot erode into
build gates. This is enforced IN CODE by always returning exit 0, so no future prose
drift can turn a heuristic into a blocker. And invariant of decidability-honesty
(T7): the script reports only mechanically-decidable facts and NEVER claims a
semantic verdict (e.g. "register mismatches the tag", "this clause is a procedure").
It may SHORTLIST candidates for a human to judge; it never renders the judgment.

## Test Mode
`test-after allowed` — the golden-fixture tests are a SEPARATE gate (g3). Do NOT
write the test file here. DO make the script cleanly testable: accept a
`--root <path>` (or positional path) pointing at any `skills/` directory so g3 can
run it over a fixture corpus, and factor the checks into importable functions
returning structured findings (so g3 can assert on them without shelling out only).

## Close Criteria (each proven in your IMPLEMENTER_RESULT)
- `scripts/curate_corpus.py` exists and runs: `py scripts/curate_corpus.py` (default
  root `skills/`) prints a findings table and exits 0.
- `--json` emits a machine-readable record (findings as structured data) to stdout;
  exits 0.
- `--root <dir>` / positional path lets it measure an arbitrary skills dir.
- ALWAYS exits 0 — including when a skill dir is unparseable (missing/malformed
  SKILL.md frontmatter): that skill becomes a findings ROW (e.g. check="parse",
  status flagged, detail=the error), never a crash/traceback and never a nonzero exit.
- Checks implemented (all MECHANICAL), each producing findings rows:
  1. **Size:** per-skill SKILL.md line count and word count vs soft-budget CONSTANTS.
     Flag over-budget. Constants declared at top with a comment naming them CURATOR
     REVIEW HEURISTICS (soft budgets, never gates). Suggested seeds (you choose final
     numbers, justify in comment): SKILL.md word target ~400, hard line-flag > 500.
  2. **Description lint** (from SKILL.md YAML frontmatter `description:`):
     - length vs a char/word budget (flag over-long);
     - PERSON: presence of first/second-person pronoun tokens ("I", "you", "your",
       "we", "our", "us") as whole words → shortlist "person-check candidate"
       (mechanical presence only; do NOT assert it IS wrong — third-person is the
       convention but the human judges);
     - WHEN-TO-USE marker: presence of a triggering-condition clause, detected by a
       marker like "Use when" / "Use to" / "Use for" / "Use during" (case-insensitive).
       Absence → flag "no when-to-use marker".
     - EXCLUSION-CLAUSE marker: presence/absence of an exclusion marker (e.g. "not",
       "do NOT use", "for ... use <other>", "instead of"). Only FLAG ABSENCE for the
       known confusable-pair skills; for others, absence is fine (report presence as
       info at most). Confusable pairs (from the epic cross-cutting rule 1):
       scout/cartographer, explorer/interrogator, admiral/commander,
       curator/scout+write-a-skill, commander-delegated/admiral. Encode this pair set
       as a CONSTANT with a comment. (Mechanical presence/absence only — never judge
       whether the clause is CORRECT.)
  3. **Invoker tag:** presence of a frontmatter `invoker:` key whose value is one of
     human/agent/both. Absence → flag "missing invoker tag". (On the current corpus
     only curator will have one — every other skill flags here; that is EXPECTED and
     is how the convention gets seeded. Not your concern to fix.)
  4. **Reference TOC:** for each `skills/<name>/references/*.md` longer than 100 lines,
     presence of a table-of-contents marker (e.g. a "## Contents" heading). Absence →
     flag "reference >100 lines without TOC". (100 is a CONSTANT with a comment.)
  5. **Duplication-signature clustering** (corpus-level): tokenize each SKILL.md body
     (strip frontmatter), compute k-word shingles (k = a SHINGLE_SIZE constant,
     justified in a comment — e.g. 8-word shingles catch pasted doctrine sentences
     while tolerating small edits), and report shingles that appear across >= 2
     DISTINCT skills as duplication clusters (which skills share which signature).
     This is the drift-elimination detector — the core one. Normalize whitespace;
     you may lowercase. Justify k and the min-cluster threshold in comments.
- Output: a readable findings table (columns e.g. skill | check | status | detail)
  AND `--json`. Both paths exit 0.
- NO baseline/drift-vs-previous-run diff — that is v2 (spec ruling S7). Do not build it.

## Allowed Scope
`scripts/curate_corpus.py` (new file only). You may read any `skills/**` and
`install_constellation.py` to understand the corpus shape, but change NO other file.
No test file (that is g3). No edits to any skill.

## Specific Exclusions
- No baseline/drift machinery (S7 — owned by a future v2, not this issue).
- No SEMANTIC verdicts — only mechanical shortlisting.
- Do not modify any skill's content or any other script.
- Do not add gate/exit-code!=0 behavior anywhere.

## Constraints
- Python 3, standard library only (no new deps). Match the repo's existing script
  style (see `scripts/install_constellation.py`, `scripts/check_skill_freshness.py`).
- `from __future__ import annotations`; type hints; a `main(argv)->int` returning 0;
  `if __name__ == "__main__": raise SystemExit(main())`.
- Every threshold/shingle constant is a NAMED module-level constant with a comment
  calling it a curator review heuristic (soft budget), never a gate.
- Windows: the repo runs under `py`. Read files with `encoding="utf-8"`.

## Map Anchors (inbound)
- **Structural:** `scripts/curate_corpus.py` — NEW, top-level bundled-script family.
- **Capability:** mechanical corpus measurement; flags-never-gates.
- **Constraints:** exit 0 always; mechanical-only (T7); no drift-diff (S7).
- **Decision anchors:** SHINGLE_SIZE and budgets are curator review heuristics —
  justify each in a comment; do not present them as gates.
- **Evidence expectations:** the duplication detector must be able to BITE (g3 proves
  it on fixtures) — design it to actually cluster shared shingles.

## Deliverable Path Check
- **Committed** — `scripts/curate_corpus.py`; `git check-ignore scripts/curate_corpus.py`
  exits 1 (not ignored), verified before dispatch. It rides into the diff.

## Required Evidence (paste into IMPLEMENTER_RESULT)
- The EXACT stdout AND exit code of `py scripts/curate_corpus.py` run over the REAL
  `skills/` corpus (the human table). Prose "it exits 0" is NOT sufficient — paste
  the run and show `echo $?` = 0.
- The EXACT stdout + exit code of `py scripts/curate_corpus.py --json | head` (show
  it is valid JSON and exits 0).
- A run over a deliberately-broken skill dir (or describe how an unparseable dir
  becomes a row) showing exit 0, no traceback.
- The list of named constants with their justifying comments (quote them).

## Verification Commands
```bash
cd C:/Programs/constellation-wt-104
py scripts/curate_corpus.py; echo "exit=$?"
py scripts/curate_corpus.py --json | python -c "import sys,json;json.load(sys.stdin);print('json-ok')"; echo "exit=$?"
py -m pytest tests/ -q   # existing suite must stay green (you add no tests here)
```

## Suggested Model Tier
`stronger — reason: new module, mechanical/semantic boundary discipline (T7) and the
shingle detector need judgment to get right`

## Authority
Design decisions already made (do not revisit): mechanical-only; exit 0 always; no
drift-diff; top-level script location; `invoker:` frontmatter key is the tag format.
You DECIDE: exact constant values (justify in comments), table format, JSON schema
shape, function decomposition, shingle normalization details.

## Stop Conditions
Stop and return if: a spec-named check cannot be done mechanically without a semantic
judgment (report the boundary honestly — do not fake determinism); you would need to
edit a file outside `scripts/curate_corpus.py`; required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied,
evidence produced (the pasted runs above), assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback. WRITE your full IMPLEMENTER_RESULT as
your final message AND to the result path you are given, before going idle.
