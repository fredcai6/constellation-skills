# REVIEW_RESULT — g4 (pilot Euler scenarios + bar README)

Session: constellation/issue-106/g4/reviewer/attempt-1
Worktree: C:\Programs\constellation-wt-106 (branch constellation/issue-106)
Review target: UNCOMMITTED working tree (untracked `evals/**`)

## VERDICT: APPROVE

Central decision ruling: **ACCEPT** the sentinel fallback as a bounded, documented FLOOR
limitation (with a required g5-scope caveat, below). All five close criteria reproduce
independently. Nothing out of scope was touched.

---

## Per-check findings (each reproduced by me, not taken from the implementer)

### Close criterion 1 — schema + structural T3 — PASS
- 3 scenarios (`euler-1-multiples`, `euler-2-even-fibonacci`, `euler-5-smallest-multiple`),
  each with `task.md`, `checks/{spine_completed,artifact_present,tests_green}.py` (process,
  gating), `checks/answer/answer_matches.py` (advisory), `fixture/README.md`. No
  `scenario.toml` (defaults). Matches contract §(a) directory-is-schema exactly.
- The three process checks are byte-identical across all three scenarios (md5 confirmed:
  artifact_present `b66a6f…`, tests_green `2001ef…`, spine_completed `0e1b20…`); only
  `answer_matches.KNOWN_ANSWER` (233168 / 4613732 / 232792560) and `task.md`/`fixture`
  differ. Correct: process gating is problem-independent; only the advisory answer is
  problem-specific.
- Structural T3 honored: verdict gate reads `checks/*.py` only; `answer_matches` lives under
  `checks/answer/` and is recorded-not-gating. Verified in `_run_once` (answer_results
  appended to the record after `classify_run`, never fed to it) and observed live: on the
  passing dry-run the advisory answer check can even return EXIT 1 without moving the verdict.

### Close criterion 2 — six dry-run invocations — PASS (all reproduced)
| scenario | `--dry-run` | `--dry-run-fail` |
|---|---|---|
| euler-1-multiples | PASS exit 0 | FAIL exit 1 |
| euler-2-even-fibonacci | PASS exit 0 | FAIL exit 1 |
| euler-5-smallest-multiple | PASS exit 0 | FAIL exit 1 |
All `completed=3 passed=3 fenced=0` (pass) / `completed=3 passed=0 fenced=0` (fail).

**Per-check biting — verified individually, not just in aggregate.** On a captured
`--dry-run-fail --keep-temp` broken run-0 (workspace has only `BROKEN.txt` + an
`{"status":"in-progress"}` spine), each process check returns non-zero on its own:
- `spine_completed` EXIT 1 (parses the spine, rejects non-terminal status — not a mere stat)
- `artifact_present` EXIT 1 (no non-empty solution `.py`, no sentinel)
- `tests_green` EXIT 1 (no test file, no sentinel)
A present-but-vacuous check would have silently passed the broken workspace; none did.

**Primary (real-deliverable) branch — verified the checks are NOT merely sentinel-driven.**
I hand-built a run-dir with a real `solution.py`, a real green `test_solution.py`, an
engine-form terminal spine (`{"tasks":{...:{"status":"complete"}}}`) under
`workspace/.agent-work/`, a corpus template spine under `workspace/.claude/`, and **no
sentinel**. Result: all three process checks PASS off the real artifacts; the corpus
template spine under `.claude/` was correctly ignored (exclusion works); `answer_matches`
observed 233168. Flipping the test red flipped `tests_green` to EXIT 1 — pytest is really
executed against the discovered test path, not faked.

### Close criterion 3 — README governance — PASS
`evals/README.md` contains: the situational bar transcribed **verbatim** ("new skill or
behavior-changing rewrite → ≥1 scenario execution … nothing gates on evals. No Iron Law.");
run command + full exit-code table (0/1/2/3); N-of-M as a regression-vs-variance smoke, NOT
a statistical guarantee (§(iii) language); both stated limitations (limitation 1 = FLOOR-not-
ceiling, limitation 2 = Euler tests machinery not architecture judgment); the named-but-NOT-
built delegated-commander selection scenario; and the transcripts-for-diagnosis-only note.

### Close criterion 4 — suite green + evals not agent-launching tests — PASS
- `py -m pytest -q` → **513 passed, 2 skipped, 152 subtests passed**. Reproduced.
- `evals/` contains no `test_*.py` / `*_test.py` files and is not referenced by any pytest
  config (no pyproject/pytest.ini/conftest wiring) nor by `.github/`. pytest does not collect
  it; no eval launches an agent at collection time.

### Close criterion 5 — committed, not ignored — PASS
`git check-ignore` exits 1 (committed) for `evals/README.md`, `evals/euler-1-multiples/task.md`,
and a process check; the defensive `evals/**/_runs/` ignore correctly returns 0 for a `_runs/`
path only. Correct.

---

## CENTRAL REVIEW DECISION — ruling: ACCEPT (documented FLOOR limitation)

**I independently confirmed the hole exists.** A run-dir with the sentinel
(`eval-complete.txt`) + a terminal spine but NO real solution and NO test PASSES all three
process checks (`artifact_present` and `tests_green` take their sentinel fallback;
`spine_completed` passes on the terminal spine). So a live run that drives the spine to
terminal and writes the sentinel but produces no deliverable would score PASS.

**Why ACCEPT, citing the contract:**

1. **The frozen contract designed exactly this floor/ceiling split.** Contract §"`--dry-run`
   and `--dry-run-fail`" states verbatim: "`--dry-run-fail` is the FLOOR and the live broken
   corpus is the CEILING," and it names candidate C's *own worst weakness* — "dry-run can mask
   live-vs-real artifact skew" — as "exactly what the g5 live broken-variant run validates."
   The residual hole is not a smuggled defect; it is the contract's explicitly deferred item.

2. **A strict check is incompatible with the FROZEN runner, and the runner is out of this
   gate's scope.** `dry_run_launch` (frozen, lines 472–483) synthesizes only
   `eval-complete.txt` + `{"status":"done"}` — no `solution.py`, no `test_*.py`. A strict
   `artifact_present`/`tests_green` demanding a real solution and a real green test could not
   PASS `--dry-run`, directly violating the contract's requirement that `--dry-run` "synthesizes
   a passing workspace … [where] process checks pass" and is "caller #2's live target." Closing
   the hole therefore *requires* editing the frozen runner (make `dry_run_launch` synthesize a
   minimal real `solution.py`+`test_*.py` AND drop the fallback). The handoff scopes this gate
   to `evals/**` with "Runner/tests read-only." The implementer stayed in scope and made the
   checks compatible with the frozen seam while still validating the REAL deliverable on the
   primary branch — which I verified works and correctly excludes the corpus copy.

3. **The hole is narrow and partially guarded.** It requires a terminal spine AND a sentinel AND
   no deliverable simultaneously. `spine_completed` has NO fallback and bites strictly — it is
   the contract's strict primary gate and it independently rejects the g5 named broken variant
   (spine template removed → non-terminal → FAIL). The design-it-twice graft's structural
   process/answer split (killing answer-only vacuous-PASS) is intact; the sentinel fallback is a
   softer, documented residue at the artifact/test level only.

4. **The docs state the hole honestly** (handoff's precondition for ACCEPT). Both
   `artifact_present.py` and `tests_green.py` docstrings name "the residual 'sentinel written
   without a real solution' hole is exactly what the g5 live broken-variant CEILING covers," and
   README limitation 1 states "a subtly-regressed corpus that still completes the spine can still
   pass." No overclaim.

BLOCK is defensible (the harness's core purpose is catching a broken corpus, and "spine completes,
no deliverable" is a plausible regression), but it would (a) reopen a FROZEN g1 seam, (b) exceed
this gate's allowed scope, and (c) close at g4 a gap the contract already scheduled for g5. Given
an explicit contractual floor/ceiling architecture and honest documentation, ACCEPT is the
better-grounded call.

### Required g5 focus (condition attached to this ACCEPT — Commander please carry forward)
The contract's *named* g5 broken variant is "spine template removed → `spine_completed` fails."
That variant is caught by `spine_completed` and does **not** exercise the sentinel-without-
deliverable hole this fallback opens. So the g5 CEILING as currently named does NOT actually
cover the residual hole. **g5 must add a broken variant that drives the spine to terminal AND
writes the sentinel BUT produces no solution/test** — otherwise the hole the fallback opens is
never validated by any gate, and this ACCEPT's "g5 covers it" rationale would be hollow. This is
recorded here as a load-bearing g5 acceptance item, not merely a suggestion.

---

## Blockers
None.

## Out-of-scope observations (not acted on)
- The runner's `dry_run_launch` synthesizing a stub `solution.py` + passing `test_*.py` (so the
  agent-free floor also exercises the primary branches and the fallback can be dropped) is the
  clean long-term fix. It is a runner-gate change, correctly deferred by the implementer. If the
  curator later wants strict checks, route it as a bounded runner rework — pair it with the g5
  variant above.

## Workflow feedback
- The handoff's instruction to reproduce all six invocations and to independently build both the
  broken and the real-deliverable run-dirs was decisive: the biting proof and the "not merely
  sentinel-driven" proof are only convincing when the reviewer fabricates the run-dirs, and doing
  so is what surfaced the g5-coverage gap in the contract's *named* ceiling variant.
- The implementer's own out-of-scope note already anticipated the runner-enhancement path; the
  handoff's central-decision framing was accurate and well-scoped. Good chain of custody from
  contract → implementer assumptions → check docstrings → README.

Target postconditions satisfied: `g4-integrate.c1` (dry-run validate + suite green) and
`g4-integrate.c2` (this APPROVE), with the g5 broken-variant coverage item attached.
