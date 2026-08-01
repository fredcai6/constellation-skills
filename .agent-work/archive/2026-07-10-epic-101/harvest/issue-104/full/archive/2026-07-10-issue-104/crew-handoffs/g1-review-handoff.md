# Reviewer Handoff

Concise fragments. Paste, don't point — you start cold.

## Gate
`g1-review` (issue #104, constellation-curator, cluster C)

## What was implemented
`scripts/curate_corpus.py` — the curator's mechanical-only measurement pass over the
skills corpus. New file, untracked. It emits a human findings table and `--json`, and
ALWAYS exits 0 (flags-never-gates). The full implementer report (with pasted runs and
the constants' justifying comments) is at
`C:\Programs\constellation-wt-104\.agent-work\issue-104\crew-handoffs\g1-implement-result.md`
— read it, then verify its claims YOURSELF against the code and by re-running.

## How to inspect
Worktree `C:\Programs\constellation-wt-104`. Read `scripts/curate_corpus.py`. It is
untracked, so: `git status --short scripts/` shows `?? scripts/curate_corpus.py`; read
the file directly. Re-run the verification commands below.

## Task statement
Independently verify the script honors the gate's binding contract. Do NOT rewrite it;
verify and return a verdict.

## Close criteria to verify (each yes/no with evidence)
- **Flags-never-gates enforced in code:** there is NO code path returning a non-zero
  exit. Confirm by reading (no `sys.exit(1)`, no `return 1`, main returns 0 on every
  branch) AND by running the error path (an unparseable skill dir) and checking exit 0.
- **Mechanical-only / T7:** no check renders a SEMANTIC verdict. The person-check only
  SHORTLISTS; the exclusion-check reports presence/absence only, never correctness.
  Confirm the code never claims "register mismatches" / "this is a procedure" etc.
- **Both outputs:** default run prints a readable findings table; `--json` emits valid
  JSON (parses with json.load) and exits 0.
- **Unparseable dir → row, not crash:** a skill dir with missing/malformed frontmatter
  becomes a findings ROW with exit 0 and NO traceback.
- **All five checks present:** size (line+word vs budgets), description lint (length,
  person, when-to-use, exclusion for confusable pairs), invoker-tag presence,
  reference TOC for >100-line refs, duplication-signature shingle clustering across >=2
  skills.
- **Constants justified:** every threshold/shingle constant is a named module-level
  constant with a comment calling it a curator review heuristic (soft budget), not a gate.
- **No baseline/drift machinery** (S7) — absent.
- **Detectors bite:** the duplication detector actually clusters shared shingles on the
  real corpus (the report shows commander/commander-delegated and implementer/reviewer
  clusters — confirm by re-running).
- **Scope:** only `scripts/curate_corpus.py` changed (plus the implementer's local
  `.agent-work/` plan bookkeeping, which is fine). No skill content or other script edited.

## Constraints
- stdlib only; `main(argv)->int`; exits 0 always.
- The script is a measurement tool; a finding is a row, never a failure.

## Map anchors (inherited from g1-implement)
Structural: `scripts/curate_corpus.py` (new). Constraints: exit 0 always; mechanical-only
(T7); no drift-diff (S7). Evidence: duplication detector must bite.

## Evidence from IMPLEMENTER_RESULT
The implementer pasted: a real-corpus table run (exit 0, 60 findings), a `--json` run
(valid JSON, exit 0), an unparseable-corpus run (parse rows, exit 0, no traceback), and
the full list of constants with justifying comments. Reproduce these; a correct claim
you cannot reproduce is a BLOCK.

## Verification commands
```bash
cd C:/Programs/constellation-wt-104
py scripts/curate_corpus.py; echo "exit=$?"
py scripts/curate_corpus.py --json | python -c "import sys,json;json.load(sys.stdin);print('json-ok')"; echo "exit=$?"
# construct a broken skill dir and confirm exit 0 + a parse row, no traceback
py -m pytest tests/ -q
grep -n "return 1\|sys.exit(1\|exit(1)" scripts/curate_corpus.py   # expect: no gating exits
```

## Suggested Model Tier
`simple bounded — the contract is explicit; verification is re-run + read`

## Stop Conditions
Return BLOCK (not silent rework) if any close criterion fails, with the specific
failing check and reproduction.

## Return Format
Return REVIEW_RESULT with an explicit `verdict: APPROVE` or `verdict: BLOCK`, the
per-criterion findings with reproduced evidence, any out-of-scope observations, and
workflow feedback. WRITE the full REVIEW_RESULT as your final message AND to the
result path you are given, before going idle.
