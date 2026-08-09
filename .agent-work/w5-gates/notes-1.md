# notes-1 — commander-w5-gates (epic #418 wave 5, crew 1)

Working notes. The authoritative state is the engine: `.agent-work/w5-gates/spine.json`
(read it through `current`, never by hand). The resolved understanding is
`.agent-work/w5-gates/INTERROGATION_RECORD.json` (12 questions, `verify_interrogation.py`
exit 0) and the consolidation summary inside `.agent-work/w5-gates/interrogation.json`.

## Where the run stopped (crew-1 original agent)

Spine complete through `understand`. `start plan` was **refused** by the engine on a HARD
context reading (16% fill against a 0.15 hard band for a 1M window — a real trip, not a stale
gauge). A `refresh-request` is attached to `plan` against why-record `w-3`. The next actor is a
**fresh** Commander cold-starting from `current`, same spine file.

## Where the run is now (refresh agent, session `commander-w5-gates-b-refresh1`)

`plan` is **complete**, all six postconditions met. Artifacts a future refresh should read first:

- `MISSION_FRAME.md` — verifies FRAME-OK against the DEGRADED-NO-MAP receipt. The map is **absent**,
  not stale, so the frame cites no anchor ids and is cut from the four hash-pinned substitutes.
- `execute.json` — four gates: g1 location guard (fix B), g2 stop-boundary (fix A), g3 archive
  (fix C), g4 composition floor. Frozen at `plan`; change it through the engine's `amend`/`reopen`,
  never by hand.
- `PLAN_ALTERNATIVES_BRIEF.md` + `PLAN_ALTERNATIVES_CONVERGENCE.md` — panel of 3, converged hybrid.
- `PLAN_CRITIC_TRIAGE.md` — **read this one.** A cold critic panel of 2 BLOCKed the first draft: g1
  and g3 could each have closed with zero work done. The `-k` selectors and the test naming
  contracts in the gate imperatives are that block's remedy and are load-bearing, not stylistic.

**Two claims in the sections below are corrected by measurement.** Ordering g1 before g2 is *not* a
technical dependency — g2's pytest path reaches the verifier through a tempdir bundle where the
guard passes today, unfixed; the real reasons are same-file serialization and reviewer locality.
And the guard's main-checkout failure is a **wrong-accept** at the guard (the downstream refusal
then names the wrong problem); the outright refusal at the guard is the **worktree** case.

**Measured baselines** (base commit, before any fix): full suite `python -m pytest -q` → 1867
passed, 2 skipped, exit 0, **947s**. The eight-file coupled suite used at each gate boundary → 375
passed, 463 subtests, exit 0, **44s**. All six `-k` selectors exit **5** (zero match) today, which is
what makes them fail closed.

## Where the run is now (second refresh, session `commander-w5-gates-c-refresh2`)

`execute` is **in-progress**. Inside `execute.json`: `e0-context` complete, **`g1-implement` complete**,
`g1-review` pending with its precondition attested and its handoff already written.

- The g1 handoff and result are at `.agent-work/w5-gates/crew-handoffs/g1-implement-{HANDOFF,RESULT}.md`.
  **The g1-review handoff is already written** at `crew-handoffs/g1-review-HANDOFF.md` — a fresh agent
  should dispatch it rather than re-author it.
- I re-measured the structural predicate on disk myself before dispatch, and it separates all three
  locations: main checkout and worktree both have **no own `SKILL.md`** and a parent with no
  `CORPUS.json` and **0** `constellation-*/SKILL.md` children; the installed bundle has its own
  `SKILL.md`, a parent `CORPUS.json`, and **20** sibling bundles.
- Verified in my own hands after the crew returned: `guard_location` **10 passed / 13 deselected**,
  exit 0; `guard_mutation` **1 passed / 22 deselected**, exit 0; coupled suite **386 passed / 480
  subtests, 38.9s**, exit 0 (base was 375/463, so the delta is exactly this gate's additions).
- The two `M` files under `.agent-work/epic-418-redux/transitions/close-to-w5/` are a **CRLF stat
  artifact** — `git diff` is empty for them and their blob OIDs match HEAD. Leave them unstaged; they
  are the Admiral's.
- A g1 **reviewer registration was created and then explicitly abandoned** without ever being
  dispatched, because the trip landed between registration and dispatch. `recover_crews.py` reports
  **0 unresolved**; relaunch a fresh reviewer normally.

**Line-reference correction for g2.** The plan cites the negative assertion to invert at
`tests/test_iterative_planning_doctrine.py:461-462`. On the pre-g1 tree it is actually at **:465** —
`self.assertNotEqual(0, refused.returncode, "stop cannot authorize NEXT_WAVE")`, inside the
`with self.subTest(launch_authority="stop")` block at :464. g1 added ~366 lines to that file, so the
line number has moved again. **Find it by its text, not its line number.** The plan's identification
of *which* assertion is correct; only the coordinate is stale.

## Launch order

`C:/Programs/constellation-skills/.agent-work/epic-418-redux/launch-orders/LO-w5-c1-gates.md`.
**It is not in this worktree** — it landed in `197ad5b0`, which post-dates the base `ea854471`.
Read it from the main checkout.

## The three fixes, as resolved

**A — #506.** `verify_admiral_prelaunch` becomes decision-aware, **keeping the mode name
`admiral-prelaunch`**. A `stop` packet is blocked by **two** clauses, not the one pre-ruling 1
names:

- `_next_wave()` (`verify_iterative_role_artifacts.py:115`) requires a **nonempty** `launch_id`;
- lines 145–148 require `decision in {advance, replan}`.

So #506's options 1 and 2 are not alternatives — option 1 needs option 2 to be implementable at
all. Under `stop`: the artifact may express "no launch authorized", the authorization clause is
skipped, and G2 validation, the unique-audit-entry match, the render, and the
`CURRENT_TRUTH`/`WAVE_REVIEW` writes all still run. Option 3 (a separate `admiral-boundary` mode)
is declined because `ADMIRAL_SPINE.template.json`'s `execute.c3` names the mode string, and that
template is not this run's file. `repair` stays refused — out of scope, and it is a real
authorization question.

Mutation test on the **stop** path is required and **not overridable** (pre-ruling 2).

**B — #501 + #468.** Replace the name test with a structural one: a directory is an installed
bundle when it carries its own `SKILL.md` **and** its parent is a skills root (the installer's
`CORPUS.json` marker, or a `constellation-*/SKILL.md` sibling). Measured on disk — true for
`~/.claude/skills/constellation-admiral`, false for both `C:/Programs/constellation-skills` and
this worktree. Then: `--skills-root` wins if given; else the installed parent; else probe the
known user-scope roots and print a **visible** stderr note naming the root resolved; else REFUSE
naming the real problem and every root tried.

**C — #439 + #484 + #446.** Rewrite `archive.c2b` to derive its own branch through the existing
`<repo-root>` token and to accept `{OPEN, MERGED}` while still rejecting CLOSED-unmerged, with the
count compared in the shell so the **exit code** carries the verdict:

```
test "$(gh pr list --head "$(git -C <repo-root> rev-parse --abbrev-ref HEAD)" --state all --json state --jq '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length')" -gt 0
```

Verified against four real branches: no-PR → 1, MERGED → 0, CLOSED-unmerged → 1, MERGED → 0.

No new resolver token. `init_work_area.py` is untouched, because the branch is **not guaranteed to
exist** when the spine is instantiated — init's own imperative instantiates the spine first and
starts the branch after.

## The three findings that go UP, not into the code

1. **`archive.c2b` does not fail the way #439 and #484 say it does.** The engine runs check text
   through `sh -c`, and unquoted `<` is an input redirection:
   `sh: line 1: branch: No such file or directory`, exit 1. `gh` is never invoked. More important:
   the engine's verdict is **returncode-only** (`checklist_engine.py:832`), and
   `gh pr list --head 'no-such-branch-xyz' --state open --json number --jq 'length > 0'` prints
   `false` and **exits 0**. So the fix both issues suggest converts a check that cannot pass into
   **a check that cannot fail**. #484's suggested replacement command has this defect verbatim.
2. **The same guard breaks `execute.c2` in every Commander worktree.** A worktree directory is not
   named `constellation-*`, so the current guard refuses outright there — and `COMMANDER_SPINE`'s
   own `execute.c2` runs the vendored copy from exactly there. In the main checkout the guard
   wrongly passes; in a worktree it wrongly refuses. Neither answer is about whether an installed
   corpus is reachable. This manifestation is in neither issue.
3. **#501's boundary-freshness sub-ask is deferred with a falsification, not skipped.** The
   stateless variant (refuse unless `NEXT_WAVE.boundary_id` is the last verified `TRANSITION` in
   `ADMIRAL_LOG.md`) is **green in exactly the world it was written to catch**: when the check is
   run early, the new boundary has not been logged yet, so the stale boundary *is* the last entry.
   Staleness is a mismatch with the caller's intent, and the caller's intent is in no artifact — so
   #501's other variant (caller passes the expected `boundary_id`) is the only sound one, and it is
   inert unless `ADMIRAL_SPINE.template.json` passes it, which this run does not own. Route as
   `recommend-and-defer` at triage. #501's stated Acceptance is met without it.

## Duplicate collapses — confirmed against the BODY (pre-ruling 3, not overridable)

- **#501 ≡ #468** on the primary defect. Both quote `_installed_skills_root()` and the
  `startswith("constellation-")` predicate passing from the repo. **Not total:** #501 carries the
  freshness sub-ask #468 never mentions — in its Suggested Fix, not its Acceptance.
- **#439 ≡ #484.** Same file, same postcondition, same literal token, both proved by running the
  command with and without substitution. Suggested fixes diverge; the defect does not.
- **#446 is distinct**, same postcondition. It never mentions `<branch>`. Neither fix subsumes the
  other: substituting the branch leaves `--state open`, and accepting MERGED leaves the literal.

## Red repros captured (re-run these to confirm the fix)

```
# B, main checkout (cwd = C:/Programs/constellation-skills) — byte-identical to #501's quoted output
$ python scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
REFUSED: installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py
exit=1
# B, installed copy, same packet
$ python ~/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
iterative role artifact ok: admiral-prelaunch (epic-418-redux)   exit=0
# B, third manifestation — from this worktree
$ python scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
REFUSED: role verifier must run from an installed constellation-* skill   exit=1
# C, shipped check
$ sh -c "gh pr list --head <branch> --state open --json number --jq 'length > 0'"
sh: line 1: branch: No such file or directory   exit=1
# C, the trap
$ sh -c "gh pr list --head 'no-such-branch-xyz' --state open --json number --jq 'length > 0'"
false   exit=0
```

Live `stop` fixture for fix A already exists: `.agent-work/epic-418-redux/` carries
`transitions/w4-to-close/` and `ADMIRAL_LOG.md:3242`
`- TRANSITION | boundary=w4-to-close | decision=stop | verified`. Copy it into a test fixture; do
not mutate the live epic's packet.

## Interpreter — use `python`, never `py`, and match the gate

Under the Bash tool `py` and `python` are **different interpreters**. Reproduced in this worktree:

```
py     -> C:\Users\fredc\.cache\codex-runtimes\...\python.exe            3.12.13   no pytest
python -> C:\Users\fredc\AppData\Local\Python\pythoncore-3.14-64\...     3.14.3    pytest 9.0.2
py -m pytest --version      exit=1   ModuleNotFoundError: No module named 'pytest'
python -m pytest --version  exit=0   pytest 9.0.2
```

`py -m pytest` fails with a **nonzero exit**, which reads exactly like a red suite. It is not — the
tests never ran. Run the suite as `python -m pytest`.

Two consequences beyond the suite:

- **The version skew is its own hazard.** 3.12 vs 3.14 is not only a pytest difference. A stdlib
  behaviour change between them could let a verifier script pass by hand and fail at the gate.
- **The spine's own command postconditions invoke `python`**, not `py` — `execute.c2` is
  `python scripts/verify_iterative_role_artifacts.py commander --work-id w5-gates`. So hand
  verification must use `python` to predict what the gate will do. Every red repro above was
  **re-derived under `python` (3.14.3)** and is identical to the `py` run — worktree refusal,
  main-checkout refusal, installed-copy exit 0. No finding in this file depends on the interpreter.

## Fences

Do not touch `scripts/checklist_engine.py` or `tests/test_checklist_engine.py` (crew 4),
`scripts/install_constellation.py` (crew 2), handoff templates (crew 3), `docs/CREW_CONTEXT.md` or
`docs/TREND_SNAPSHOT.md` (crew 5). Never `findings-1.md` as a basename — the harness `Write` tool
refuses it.
