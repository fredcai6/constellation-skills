# Implementer Handoff

## Gate
`g1-implement` (from `.agent-work/commander-315/execute.json`)

## Working root

`/home/tommy/projects/constellation-skills-wt/epic-568-315` — a **linked git
worktree** on branch `epic-568/c1-check-cwd`. Work only here. Never write to
`/home/tommy/projects/constellation-skills` (the main checkout); it is read-only
to this wave.

## Task

In `scripts/checklist_engine.py`, make a `command`-kind check run where the
spine lives instead of wherever the launching process stood.

`_run_check_command` (lines 775-799) calls:

```python
proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
```

with **no `cwd=`**. Meanwhile `base_dir` — the spine file's own directory,
computed in `main()` as `path.parent` (line 3299) — is already threaded all the
way down to `_check_condition(cond, t, base_dir)` (line 802) and is already
consumed by the `git-change-policy` branch (line 862). Only the `command`
branch (line 831) drops it.

Do three things:

1. Add a helper that resolves a **repo/worktree root** from a starting
   directory: walk UP from the start looking for a `.git` entry, accepting
   **both** a directory (plain checkout) and a **file** (linked worktree —
   `.git` is a file containing `gitdir: ...`). Return the first directory that
   has one. Return `None` if none is found before the filesystem root.
2. Thread `base_dir` into `_run_check_command` and pass the resolved root as
   `cwd=` to the existing `subprocess.run` call.
3. Add regression tests to `tests/test_checklist_engine.py`.

## Protected Intent

A postcondition check must be **falsifiable**: a gate must refuse when the thing
it checks is genuinely absent, and pass when it is genuinely present — regardless
of which directory the agent, hook, or MCP door that invoked the engine happened
to be standing in. This is the verification layer of the epic's thesis that
engine state knows whose it is.

## Test Mode

**Test-after allowed, but the red-first proof is mandatory.** Each new test must
be shown to FAIL against the pre-fix engine, not merely to pass after. Use
`git stash` or a copy of the pre-fix function to demonstrate it, and paste both
outputs. A test that passes both before and after is not a regression test.

## Resolution target — already decided, do not re-litigate

**`cwd` resolves to the repo/worktree root ENCLOSING the spine, NOT to
`base_dir` itself.**

`base_dir` is `.agent-work/<work-id>/`, two levels below the root. This was
settled by measurement, not preference: across the shipped template corpus,
**zero** command checks are authored relative to the spine directory and **all
17** cwd-dependent ones are authored relative to the repo root. Setting
`cwd=base_dir` would break all 17 at once. Corroborating prior art in-repo:

- `docs/CHECKLIST_SCHEMA.md:39-41` records this defect and states the corpus
  workaround is anchoring commands `cd <repo-root> && ...`.
- `scripts/generate_spine.py:946` already probes candidate checks with
  `cwd=str(repo_root)`.

If you believe this is wrong, **stop and report** — do not change it silently.

## Close Criteria

- `_run_check_command` passes `cwd=<resolved repo root>` to `subprocess.run`.
- When no `.git` is found walking up from `base_dir`, and when `base_dir` is
  `None`, the call passes `cwd=None` — byte-for-byte today's behavior.
- The root walk accepts `.git` as a **file** as well as a directory. Verify
  against this very worktree: `/home/tommy/projects/constellation-skills-wt/epic-568-315/.git`
  is a FILE; `/home/tommy/projects/constellation-skills/.git` is a DIRECTORY.
- A linked worktree resolves to **the worktree itself**, never to the main
  checkout.
- The repro at `.agent-work/commander-315/repro_315.py` goes from exit **1** to
  exit **0**. Run it; paste both.
- `py -m pytest tests/test_checklist_engine.py -q` green (baseline: 441 passed,
  140 subtests).
- `py -m pytest tests/ -q -p no:randomly` green (baseline: 2932 passed, 5
  skipped, 1121 subtests).

## Allowed Scope

- `scripts/checklist_engine.py`
- `tests/test_checklist_engine.py`

Pre-authorized: if an existing test in `tests/test_checklist_engine.py` builds a
spine inside a directory that turns out to be under a git repo and depended on
the old cwd, you may minimally reconcile that test — but **name it explicitly**
in your result and explain why its old scenario is what this change now forbids.
Do not bulk-edit tests to make them pass.

## Specific Exclusions

- **`scripts/hooks/spine_rail.py`** — FORBIDDEN this wave (owned by epic 568
  engine-core serialization, not issue #315). If the fix appears to need it,
  STOP and report.
- **`scripts/agent_work_root.py`** — FORBIDDEN this wave, same reason.
- Do **not** call `agent_work_root.durable_root()`. It deliberately redirects a
  linked worktree to the MAIN checkout, which is the exact opposite of what a
  check needs: a check must verify its own worktree's files. Using it would make
  this worktree's gates inspect the Admiral's checkout.
- Do not change any shipped template under `skills/*/templates/` or
  `.agent-work/templates/` — a separate gate owns the corpus.
- Do not "improve" the cwd-defaulting `--root` arguments in other scripts
  (`init_work_area.py`, `verify_state_note.py`, etc.). Recorded as a triage
  candidate; out of scope here.

## Constraints

- **Preserve the POSIX-shell routing and the `no-posix-shell` failure path
  exactly.** `_find_posix_shell()` stays as is. The synthetic
  `subprocess.CompletedProcess(args=command, returncode=127, ...)` branch and
  its stderr text must be unchanged, and the returned marker must still be
  `"posix"` / `"no-posix-shell"`. Add `cwd=` **only** to the branch that already
  calls `subprocess.run`.
- **No new hard dependency on `git` being installed.** Resolve the root by
  filesystem walk (`Path.exists()`), not by shelling out to `git rev-parse`. A
  command check must still run on a box with no git.
- Guard the walk against symlink loops and infinite ascent — stop at the
  filesystem root.
- Never hand-edit any `spine.json` / `execute.json`; this gate's state is driven
  by the Commander through the engine.
- Match the module's existing style: type hints, a real docstring explaining
  **why** (this module's docstrings carry rationale, not restatement).

## Map Anchors (inbound)

- **Map entry point:** the architecture map is **DEGRADED-UNPARSEABLE** (anchor
  count 0, no `docs/architecture/`). Start instead from the hash-pinned
  substitutes recorded at the context step: **`docs/CHECKLIST_SCHEMA.md`**
  (lines 39-41 are the load-bearing paragraph) and
  `docs/CHECKLIST_ENGINE_DESIGN.md`.
- **Structural:** `scripts/checklist_engine.py:775-799` `_run_check_command`;
  `:802-845` `_check_condition` (command branch, line 831, drops `base_dir`);
  `:862` the `git-change-policy` branch that already uses it; `:3299` `main()`
  computing `base_dir = path.parent`.
- **Capability:** command-kind postcondition verification for `gated`
  `advance`/`start` and for `survey` `record --result pass`.
- **Constraints/assumptions:** preserve-no-posix-shell-behavior;
  engine-core-serialized (two forbidden files).
- **Decision anchors:** cwd resolves to the repo/worktree root enclosing the
  spine, not to `base_dir` itself.
  `@grade: settled/measured · leans implementation · settle: already settled — 17 of 17 cwd-dependent shipped checks are repo-root-relative, 0 are spine-dir-relative`
- **Evidence expectations:** the repro flips exit 1 -> exit 0; both suites stay
  green at their stated baselines.
- **Map confidence flags:** map DEGRADED — do not expect anchors; use file
  paths. Blast radius was enumerated by command, not read from the map.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`; `git check-ignore` exit **1**
  (not ignored).
- **Committed** — `tests/test_checklist_engine.py`; `git check-ignore` exit **1**.
- **Committed** — `.agent-work/commander-315/repro_315.py`; `git check-ignore`
  exit **1**. It already exists; you are not creating it. It is untracked until
  staged, so it appears in `git status`, not in `git diff`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. The repro before/after: `py .agent-work/commander-315/repro_315.py` — paste
   the full output at exit 1 (pre-fix) and exit 0 (post-fix).
2. Each new test shown RED against the pre-fix engine, then green. Paste both.
3. The `no-posix-shell` path is untouched: show the diff region and state that
   `returncode 127` and its stderr string are unchanged.

**Confirmatory — a spot-check suffices:**

4. Both suite runs at their baselines.
5. `git diff --stat` showing exactly the two allowed files.
6. `git status` confirming neither forbidden file is modified:
   `git status --porcelain scripts/hooks/spine_rail.py scripts/agent_work_root.py`
   must print nothing.

## Wiring Grep

The slice adds one callable symbol (the root resolver) and changes one
signature. Show a call site for each, outside its own definition:

```bash
grep -rn "_run_check_command\|<your-new-resolver-name>" scripts/ tests/ --include=*.py | grep -v "^scripts/checklist_engine.py:.*def "
```

**State the count of external call sites found.** Zero call sites for the new
resolver is a stop condition — a resolver only its own definition references is
shipped-inert and the whole fix would be a no-op.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315
py .agent-work/commander-315/repro_315.py ; echo "EXIT=$?"
py -m pytest tests/test_checklist_engine.py -q 2>&1 | tail -3
py -m pytest tests/ -q -p no:randomly 2>&1 | tail -3
git status --porcelain scripts/hooks/spine_rail.py scripts/agent_work_root.py
git diff --stat
```

## Suggested Model Tier

**Stronger.** The edit is small but it moves a resolution rule the whole corpus
reads, inside a 3352-line engine module, with two forbidden neighbours and a
load-bearing failure path that must survive intact.

## Authority

Already decided, not yours to change: that `cwd` resolves to the **repo root**
and not `base_dir`; that the fallback when no `.git` is found is **inherited
cwd**; that `durable_root()` is not used; that the two named files are
untouchable.

Yours to decide: the resolver's name and placement, the exact walk
implementation, the test names and structure.

## Stop Conditions

Stop and return if: the fix appears to require editing `spine_rail.py` or
`agent_work_root.py`; a shipped template turns out to need repair to keep the
suite green (that belongs to gate g2, report it rather than fixing it); more
than a couple of existing tests need reconciliation; the repro cannot be made to
pass without weakening the no-posix-shell path; or you conclude the resolution
target is wrong.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope |
failed`, written **lowercase**.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/commander-315/crew-handoffs/g1-implementer-result.md` **before
ending your turn** — that write is the delivery.
