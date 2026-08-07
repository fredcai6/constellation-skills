# Implementer Handoff

## Gate
`g1b` (issue #440, epic-418 workstream A2). Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, branch `epic-418/a2-440-binding-cwd`. Base for this gate: commit `9d44aa6` (g1). **Use absolute paths — your shell's cwd resets between bash calls.**

## Task

Close the one residual an independent reviewer found in g1, in a **bounded** fix.

`scripts/hooks/spine_rail.py` now resolves a relative `--file` by walking an ordered ladder of
candidate roots and taking the first that validates as a checklist:

| Rung | Base | `path_source` | Kind |
|---|---|---|---|
| 0 | `--file` already absolute | `absolute` | **told-truth** |
| 1 | absolute `--worktree <dir>` in the command | `worktree_opt` | **told-truth** |
| 2 | last `cd` / `pushd` / `Set-Location` target in the command text | `cd_target` | **told-truth** |
| 3 | payload `cwd` | `payload_cwd` | *guess* |
| 4 | a registered git worktree root | `git_worktree` | *guess* |
| 5 | `project_dir` | `project_dir` | *guess* |

**The residual:** when the main checkout **and** a worktree both hold a valid checklist at the same
relative path, rung 3 beats rung 4 and the store records the **main checkout's** copy — a *confident
wrong path*, which is the exact failure class this whole issue exists to end. The reviewer built this
on disk with a real `git worktree` and a fresh subprocess; it is not hypothetical. Its reach is real:
`.agent-work/` is **tracked**, so committed checklists sit at identical paths in every tree. It is
masked today only because rung 2 fires first for a dispatched agent, whose shell cwd resets between
calls so the `cd` is always in-command.

**The fix:** make the ladder refuse to guess, exactly the way `resolve_recorded_release_target`
already refuses. Among the **guessed** rungs (3 onward), if more than one candidate root validates
and they name **different** files, **bind nothing**. Skip-on-uncertainty — the store's own posture,
and the reason a missing binding is recoverable while a wrong one silently misattributes one agent's
context reading to another agent's work area.

**Rungs 0, 1 and 2 are told-truth and must keep winning outright.** They are explicit statements by
the caller about where it is, not inferences, so they must short-circuit before any ambiguity check
runs — and in particular an absolute `--file` must never start probing git.

If two guessed candidates resolve to the **same** file (e.g. `project_dir` equals the payload `cwd`),
that is agreement, not ambiguity — bind it, and keep the earliest rung's `path_source`.

## Protected Intent

A missing binding is recoverable; a wrong one is not. Nothing here may make a told-truth rung slower,
able to raise, or able to block — and nothing may put the git probe on the common path.

## Test Mode

**TDD required.** Write the failing test first: it must fail against `9d44aa6` (the current HEAD)
by binding the main checkout's path, and pass after.

## Close Criteria

- Two trees both holding a valid checklist at the same relative path, with **no** told-truth signal
  in the command → **no entry written**, store byte-unchanged.
- The same case **with** a `cd` target, an absolute `--worktree`, or an absolute `--file` → still
  resolves, still to the told-truth answer, with the same `path_source` as before.
- Two guessed candidates resolving to the **same** file → still binds, earliest rung's `path_source`.
- The rung-4 real-`git worktree` test from g1 still passes (single valid candidate → binds it).
- The git probe still does not run when a told-truth rung answers — keep or extend g1's
  `subprocess.run` spy test.
- `handle_post_tool_use` still returns `{}` on every path and never raises.
- `python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` green (169 at `9d44aa6`).
  No existing assertion weakened; **zero deletions** in the test diff is the standard g1 met.

## Allowed Scope

`scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py`. Nothing else.

## Specific Exclusions

- The binding **key** shape and `binding_key()` (#419's, load-bearing interface).
- `scripts/hooks/gauge_writer_hook.py`, `scripts/checklist_engine.py`, and anything needing #269.
- Restructuring the ladder. This is a guard, not a redesign — do not reorder or rename the rungs.
- The live main checkout's `.agent-work/.spine-rail-binding.json` and any real `.claude/settings*.json`
  — a live session is using them. All probes go in temp trees.
- The other known limits in `docs/GAUGE_WRITER_HOOK.md` (no key reaper, no lock, no absolute-`--file`
  validation). Docs are the Commander's at a later gate.

## Constraints

- PostToolUse never blocks and never raises; every new path returns `{}` on failure.
- The git probe stays off the common path and stays bounded (2.0s).
- Use `python`, **never** `py` — `py` here has no pytest and produces fake failures.
- Do not run the full suite; do not commit.
- Scope discipline (settled/human): a corner case you choose not to chase gets a comment at the code
  site naming it and a line in your result — never silence.
- Match the module's register: comments carry issue numbers and say why a tempting alternative was
  rejected.

## Map Anchors (inbound)

No architecture map (`DEGRADED-NO-MAP`); substitute is `docs/GAUGE_WRITER_HOOK.md`, "Known limits of
the binding store itself (#419)".

- **Structural:** `scripts/hooks/spine_rail.py` — the candidate ladder and `handle_post_tool_use`;
  `resolve_recorded_release_target` is the in-module precedent for refusing to guess on ambiguity.
- **Constraints:** PostToolUse never blocks; skip-on-uncertainty; binding key shape unchanged.
- **Decision anchors:**
  - `existence-verified-resolution` — ordered rungs, first validating candidate wins.
    `@grade: guess · leans g1,g1b · settle: the two-arm live fire at g2`
  - `not-fixing-269` `@grade: settled/human`
- **Evidence expectations:** ambiguity among guessed rungs binds nothing; told-truth rungs unaffected.

## Deliverable Path Check

- **Committed** — `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`. Run
  `git check-ignore <path>` on each and record exit **1**.
- **Local-only** — your result file under `.agent-work/`, correctly absent from the diff.

## Required Evidence

**Load-bearing:** the new ambiguity test shown **failing against `9d44aa6`** (stash or
`git show 9d44aa6:scripts/hooks/spine_rail.py`, run, paste the failure, restore and prove restored),
then passing. And `python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` with its
**real** exit code — redirect to a file and echo `$?`, because `cmd | tail` captures `tail`'s code.

**Confirmatory:** the told-truth-still-wins cases, the same-file agreement case, the probe-spy test,
`git diff --numstat` showing zero deletions in the test file.

## Wiring Grep

Required if you add a symbol. One command per new symbol showing a call site outside its own
definition; state the count. **Zero external call sites is a stop condition, not a note.** Write
`none — no new callable symbol` if the change is inline.

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q > /tmp/g1b.txt 2>&1; echo "EXIT=$?"; tail -20 /tmp/g1b.txt
git diff --numstat
```

## Suggested Model Tier
**Stronger (Opus).** Small diff, but the ordering trap is subtle. **No Fable at any tier.**

## Authority

Decided, do not re-open: ambiguity among **guessed** rungs binds nothing; told-truth rungs
short-circuit first; agreement is not ambiguity. Yours: where the check sits in the code, and how
the tests are shaped.

## Stop Conditions

Stop and return if scope must be exceeded, an exclusion touched, evidence cannot be produced, or a
decision outside this authority is needed.

## Return Format

Write `IMPLEMENTER_RESULT` to
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/crew/g1b-ambiguity/IMPLEMENTER_RESULT.md`
**before going idle**, and deliver it as your final message: completed slice, files changed, test
mode satisfied, evidence with real exit codes, assumptions, stop conditions hit, out-of-scope
observations, workflow feedback.
