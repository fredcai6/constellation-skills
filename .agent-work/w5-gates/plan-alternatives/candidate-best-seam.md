# Candidate gate plan — constraint: `best-seam-placement`

Pushed hard: every boundary below is drawn at a named code seam I can point at in
`scripts/verify_iterative_role_artifacts.py` or `skills/commander/templates/COMMANDER_SPINE.template.json`,
not at a fix-count or a file-count. **Gate count: 3.**

## g1 — Location guard: "where am I running from"

- **Seam:** `_installed_skills_root()` (lines 53–59) plus the new `--skills-root` CLI plumbing it
  needs in `main()` and its three callers (`verify_explorer`, `verify_commander`,
  `verify_admiral_prelaunch`). Fix B.
- **Why this is the real seam, not the file:** this function is the one thing all three modes call
  *before* touching any mode-specific content — it is a single already-named function boundary with
  one job ("resolve the skills root"), cleanly separable from g2's job ("interpret a decision"). A
  reviewer of g1's diff never needs to know what `stop`, `advance`, or `REPLAN_RESULT` mean.
- **Files:** `scripts/verify_iterative_role_artifacts.py` (`_installed_skills_root` + the
  `skills_root` passthrough on its three call sites + `main()`'s new arg) — **not**
  `verify_admiral_prelaunch`'s decision body. New `tests/test_verify_iterative_role_artifacts.py`
  (unit-level, all four branches). One new regression method in
  `tests/test_iterative_planning_doctrine.py::InstalledIterativeRoleRuntimeTests` for the worktree
  manifestation (finding #2 in notes-1.md — in neither issue, this run's own find).
- **Close criteria (exit code only):**
  - Unit suite exits 0 covering: `--skills-root` override wins; structural self-detection succeeds
    for a synthetic installed bundle regardless of its name; a synthetic dir named
    `constellation-skills`-like but **not** structurally installed is refused (kills today's false
    positive); probe-fallback over known user-scope roots succeeds when a root is present; refusal
    when none resolves, naming every root tried.
  - The three live red repros in notes-1.md, re-run, now exit: installed copy `0` (unchanged),
    main-checkout invocation `0` (was `1`, wrong-sibling message), worktree invocation `0` (was `1`,
    wrong-refusal message) — all via the probe fallback, not via widening the guard (pre-ruling 4).
  - Broader suite green.
- **Required evidence:** pytest console (unit + doctrine suites); the three re-run transcripts
  (command + exit code) pasted verbatim; the stderr probe-note string asserted present in a test, not
  eyeballed.
- **Precondition:** none from other gates. Only the trivial "owned files checked out clean."
- **Test commands:**
  ```
  python -m pytest tests/test_verify_iterative_role_artifacts.py -q
  python -m pytest tests/test_iterative_planning_doctrine.py -q
  ```

## g2 — Stop-boundary closure semantics

- **Seam:** `_next_wave()`, `_verify_transition_audit()`, `verify_admiral_prelaunch()`'s decision
  body — the single concern "what must a `stop` transition prove to close its gate." Fix A.
- **Why this is the real seam:** functionally downstream of g1 (`verify_admiral_prelaunch` calls
  `_replan_verifier(_installed_skills_root())` once, then never touches location again), but that is
  a call-graph fact, not a review-unit fact. g2's reviewer treats g1's contract as a black box ("I
  get a working root or a clean refusal") and reviews only decision semantics: the `launch_id`
  requirement going conditional on `decision`, and the authorization clause being skipped under
  `stop` while G2 validation, the audit match, the render, and the two writes still run.
- **Files:** `scripts/verify_iterative_role_artifacts.py` (`_next_wave`, `_verify_transition_audit`,
  `verify_admiral_prelaunch` bodies only). `tests/test_iterative_planning_doctrine.py` — extend
  `test_admiral_prelaunch_refuses_until_transition_is_unique_verified_and_rendered` or add a sibling
  `stop`-path method, **plus** the mandatory mutation test (pre-ruling 2, NOT OVERRIDABLE) seeded from
  a **copy** of the live `w4-to-close` fixture (`.agent-work/epic-418-redux/transitions/w4-to-close/`,
  `ADMIRAL_LOG.md:3242`) — never the live packet.
- **Close criteria (exit code only):**
  - Pytest exits 0 and, within it: `stop` + empty `launch_id` + G2-valid packet + unique verified
    audit + nonempty render closes (`0`, previously impossible); the same fixture mutated (decision
    flipped, render body emptied, or audit mismatch) still refuses (`!=0` — proves the check isn't
    vacuous under `stop`); `advance`/`replan` regression-covered unchanged; `repair` still refuses
    regardless of `launch_id` (untouched, out of scope per pre-ruling 6).
  - Broader suite green.
- **Required evidence:** pytest console showing the stop-green case and the mutation-red case in the
  same run; a diff/listing proving the fixture was copied, not mutated in place; broader-suite run.
- **Precondition:** g1 closed. **Stated honestly, this is not a hard test-execution dependency** —
  the existing/extended tests run against a synthetic tempdir-installed layout
  (`InstalledIterativeRoleRuntimeTests`) that already satisfies either guard implementation, so g2's
  tests would pass even run before g1. The precondition is enforced for two real reasons instead:
  (a) **same-file serialization** — g1 and g2 both edit the one file; sequencing removes the risk of
  two concurrent implementer dispatches clobbering each other's hunks, rather than trusting a clean
  merge; (b) **review locality** — a reviewer diffing g2 against a file g1 already stabilized sees
  only decision-logic churn, never guard churn mixed in.
- **Test commands:**
  ```
  python -m pytest tests/test_iterative_planning_doctrine.py -q -k admiral_prelaunch
  python -m pytest tests/test_iterative_planning_doctrine.py tests/test_verify_iterative_role_artifacts.py -q
  ```

## g3 — Archive reachability postcondition

- **Seam:** `archive.c2b`'s `check.command` in `COMMANDER_SPINE.template.json`. Fix C.
- **Why this is the real seam:** the cleanest boundary of the three — different file, different
  mechanism (a JSON-carried shell command string, not Python control flow), different defect class
  (unquoted `<` as shell redirection, plus an OPEN-only state test) from g1/g2's Python guard and
  decision logic. g3 shares nothing runtime-wise with g1/g2; the only thing it shares is crew file
  ownership.
- **Files:** `skills/commander/templates/COMMANDER_SPINE.template.json` (`archive.c2b.check.command`
  only). New `tests/test_spine_archive_check.py` (or an addition to
  `test_iterative_planning_doctrine.py`) exercising the rewritten command via `sh -c` against real
  branch states. `scripts/init_work_area.py` is **read**, not written — one assertion that
  `_RESOLVER_OWNED_TOKEN_RE` still does not own a `<branch>`-style token, so a future edit can't
  silently reclaim it without this gate noticing.
- **Close criteria (exit code only):**
  - The rewritten command (`<repo-root>` substituted, count compared in the shell) run via `sh -c`
    against the four states from notes-1.md exits: no-PR → `1`, MERGED → `0`, CLOSED-unmerged → `1`,
    MERGED → `0`.
  - Trap regression: the same command against a nonexistent branch must exit nonzero — not print
    `false` and exit `0` (the defect both source issues' suggested fixes reproduce verbatim).
  - `init_work_area.py` has a zero-line diff for this gate (scope fence, captured as evidence, not
    as the gate's pass/fail signal).
- **Required evidence:** pytest console for the four-state run; the literal final `check.command`
  string in the gate evidence; `git diff --stat scripts/init_work_area.py` showing nothing.
- **Precondition:** none from g1/g2 — independent code, independent file, independent runtime path.
  Sequenced last **purely for reviewer locality** (the two Python-guard gates read as one story, the
  template gate as a separate self-contained one) — an editorial choice, not a technical dependency,
  flagged as such rather than dressed up as one.
- **Test commands:**
  ```
  python -m pytest tests/test_spine_archive_check.py -q
  python -m pytest tests/test_iterative_planning_doctrine.py -q
  ```

## Why 3, under this constraint

Pushed hard, best-seam-placement produced exactly one gate per independently-nameable code concern in
the two owned artifacts: "which skills root" (g1), "what a stop transition must prove" (g2), and "is
there a PR carrying this work, correctly parsed" (g3). That it numerically equals "one gate per fix"
is a coincidence of this particular defect set, not a rule I applied — I verified via the existing
`InstalledIterativeRoleRuntimeTests` fixture that g1's and g2's code paths are already independently
exercisable, so if the guard's resolution bug had actually been *causing* the stop-boundary bug, they
would have collapsed into one gate. They don't.

## The one seam I considered and rejected

**Cutting by defect-class** (a horizontal red-repro gate, a horizontal fix gate, a horizontal
mutation-floor gate, each crossing all three fixes) — rejected. That shape is `most-testable`'s
natural territory, not mine, and it fails my own bar worse than a file-cut would: a "red-repro" gate
has no code to review at all (a repro only proves the bug exists, it proves nothing about a fix), so
its reviewer has nothing coherent to hold in their head. I also considered cutting by **file**
(`verify_iterative_role_artifacts.py` as one gate for both A+B) and rejected it for the reason argued
above under g1/g2: A and B share a file only by accident of the script being a single-file utility;
combining them forces a reviewer to hold "location resolution" and "decision semantics" in one head
at once, which is exactly what best-seam-placement forbids.

## Biggest weakness of this candidate

**Under `smallest-diff`:** g1 and g2 touch the same file with only an editorial (not technical)
precondition between them — nothing observably breaks if they're combined into one gate, since I
found no real test-execution dependency. `smallest-diff` would call the g1/g2 split churn for its own
sake: two gate-close cycles, two evidence bundles, two review passes, over one file that could ship as
one diff with no loss of correctness.

**Under `most-testable`, secondarily:** g3's "`init_work_area.py` has a zero-line diff" criterion is a
scope fence, not a test that goes red on a broken input in the usual sense — it's closer to a lint
assertion than an exercised code path. `most-testable` would want it reframed as a test that actively
proves the token *cannot* be silently reclaimed (e.g. a test that adds a `<branch>` token to the
resolver's pattern and asserts something downstream now fails), not a diff-emptiness check.
