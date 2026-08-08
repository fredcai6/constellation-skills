# notes-1 — commander-w5-gates (epic #418 wave 5, crew 1)

Working notes. The authoritative state is the engine: `.agent-work/w5-gates/spine.json`
(read it through `current`, never by hand). The resolved understanding is
`.agent-work/w5-gates/INTERROGATION_RECORD.json` (12 questions, `verify_interrogation.py`
exit 0) and the consolidation summary inside `.agent-work/w5-gates/interrogation.json`.

## Where the run stopped

Spine complete through `understand`. `start plan` was **refused** by the engine on a HARD
context reading (16% fill against a 0.15 hard band for a 1M window — a real trip, not a stale
gauge). A `refresh-request` is attached to `plan` against why-record `w-3`. The next actor is a
**fresh** Commander cold-starting from `current`, same spine file.

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
# B, main checkout — byte-identical to #501's quoted output
$ py scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
REFUSED: installed public verifier is missing: C:\Programs\constellation-replan\scripts\verify_replan.py
exit=1
# B, installed copy, same packet
$ py ~/.claude/skills/constellation-admiral/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
iterative role artifact ok: admiral-prelaunch (epic-418-redux)   exit=0
# B, third manifestation — from this worktree
$ py scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-418-redux
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

## Fences

Do not touch `scripts/checklist_engine.py` or `tests/test_checklist_engine.py` (crew 4),
`scripts/install_constellation.py` (crew 2), handoff templates (crew 3), `docs/CREW_CONTEXT.md` or
`docs/TREND_SNAPSHOT.md` (crew 5). Never `findings-1.md` as a basename — the harness `Write` tool
refuses it.
