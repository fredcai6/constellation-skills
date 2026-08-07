# Implementation Result

## Assigned gate
`g1` — issue #440, epic-418 workstream A2. Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, branch `epic-418/a2-440-binding-cwd`, base `cbd9aee`.

## Completed slice
`scripts/hooks/spine_rail.py` no longer joins a relative `--file` onto the payload's `cwd` and trusts the result. It walks an ordered ladder of candidate roots, takes the first that **validates as a checklist**, records which rung won as `path_source`, and **binds nothing** when none validates. `release` resolves against its own recorded binding first, so it still removes what its claim wrote even after the spine file is gone.

| Rung | Base | `path_source` |
|---|---|---|
| 0 | `--file` already absolute | `absolute` |
| 1 | absolute `--worktree <dir>` in the observed command | `worktree_opt` |
| 2 | last `cd` / `pushd` / `Set-Location` target in the command text | `cd_target` |
| 3 | payload `cwd` (the old behaviour) | `payload_cwd` |
| 4 | a git worktree root registered against `project_dir` | `git_worktree` |
| 5 | `project_dir` | `project_dir` |

## Scope
**Files changed:**
- `scripts/hooks/spine_rail.py` — +281/−13
- `tests/test_spine_rail.py` — +614

No new test module. The rung-4 integration test lives in `tests/test_spine_rail.py` because that file's own module docstring already documents a deliberate real-subprocess exception (`test_session_start_real_engine_claim_produces_real_binding_diff`, `lesson:verify-harness-field-and-drive-real-writer`, #261) — the new test is the same kind of proof for the same reason, and splitting it out would have hidden it from that precedent.

`tests/test_gauge_writer.py` — **not touched**. The pre-authorization was not needed: it builds its own bindings and never asserts an exact entry key set, so the additive `path_source` field did not trip it (67 tests, unchanged, green).

**Specific exclusions touched:** no. `binding_key()` and the key shape are untouched (asserted by `test_post_claim_path_source_is_additive_and_key_shape_untouched`). `gauge_writer_hook.py`, `checklist_engine.py`, and #269 are untouched. The live main checkout's `.spine-rail-binding.json` and every real `.claude/settings*.json` were never read or written — the demonstrations below run against throwaway temp directories.

## Behavior changed
Yes.

1. A claim with a relative `--file` now records the spine of the tree the agent is actually in, not a same-named path in the main checkout.
2. A claim whose `--file` resolves to nothing real writes **no entry at all** (previously it wrote a confident wrong one).
3. Binding entries carry a new `path_source` value field.
4. A `release` removes its own entry even when the spine file has been deleted in between.
5. `handle_post_tool_use` still returns `{}` on every path and never raises; the 3-strike nudge ledger still clears on a top-level release, including one that resolves nothing.

## Map Impact
- **Structural anchors touched:** `scripts/hooks/spine_rail.py` — `_resolve_abs` **deleted** (zero remaining references, verified by grep) and replaced by `looks_like_checklist`, `normalize_shell_path`, `last_cd_target`, `git_worktree_roots`, `_candidate_roots`, `resolve_spine_candidate`, `resolve_recorded_release_target`; `handle_post_tool_use` rewired. `tests/test_spine_rail.py` grew 74 → 102 tests.
- **Capabilities added/changed/affected:** session→spine binding maintenance now resolves per-**tree**, not per-session-launch-directory, and reports its own provenance.
- **Constraints/assumptions touched:** *honored* — PostToolUse never blocks or raises; skip-on-uncertainty; binding key shape unchanged; `CLAUDE_PROJECT_DIR` fixed at session launch. *Newly relied on* — `git` is on `PATH` for rung 4; its absence degrades to rung 5, it does not fail.
- **Constraints/assumptions stressed:** the module docstring's "Stdlib only" and "do NOT subprocess the engine" lines. The docstring is updated: `subprocess` is now imported for exactly one bounded `git worktree list --porcelain` probe, which asks the **filesystem** a question no file in this repo records. It is never the engine.
- **Decision candidates / resolved decisions:**
  - `existence-verified-resolution` (was `guess`) — implemented as specified. Still awaiting the g2 two-arm live fire to settle.
  - **Mine, per the handoff's "Yours to decide":**
    - *Checklist-validity test* — a readable JSON **object with a top-level `items` list**. `tasks` is deliberately not also required: `items` alone already separates a checklist from every leftover this hook can meet (a `gauge.json` has none), and a stricter test only buys new ways to reject a legitimate file. Cross-checked against `load_spine` (dict) and `active_id` (`items` + `tasks`).
    - *An absolute `--file` is **not** validated* — rung 0 is ground truth with nothing to resolve, and validating it would break the case the store most needs to survive: a `release` whose spine is already archived must still be able to name its own entry.
    - *Integration test home* — `tests/test_spine_rail.py`, reason above.
    - *Git probe timeout* — `GIT_PROBE_TIMEOUT_SECONDS = 2.0`. Generous for a warm local `git worktree list` (milliseconds) and short enough that a locked index or a dead network drive costs the turn nothing noticeable.
    - *Rung 4 excludes the main tree* — otherwise rung 5's answer would be relabelled `git_worktree` and the provenance field would lose its meaning. `git_worktree` now says exactly one thing: found in a **different** tree.
- **Claims/evidence produced:** a worktree-dispatched claim produces a worktree-rooted entry (evidence 1 and 2 below, both pre/post).
- **Trust limitations / drift found:** `docs/GAUGE_WRITER_HOOK.md` § "Known limits of the binding store itself (#419)" — its **first bullet is now stale**; it states this defect as live. Docs are outside my allowed scope, so it is left for the Commander (see Out-of-scope observations).

## Test mode
**Required:** `test-first` (TDD) for the resolution ladder.
**Satisfied:** yes. Every rung's tests were written and observed failing before its implementation. Because the failure mode is a *plausible-looking wrong answer*, RED was demonstrated the strong way the handoff asked for — `git stash` the hook change, run the new tests against the **pre-change** code at `cbd9aee`, show the wrong answer it produces, restore.

## Evidence

### 1. Rung 4 — real `git worktree`, fresh subprocess (load-bearing)

`test_post_claim_rung4_real_git_worktree_resolved_in_a_fresh_subprocess` builds a real `git init` repo, `git worktree add`s a second tree, puts a real checklist in the worktree only, and runs `spine_rail.py PostToolUse` as a **separate process**. The payload's `cwd` is the main tree; the command carries **no `cd`** and **no `--worktree`**. The test asserts, in code, that the worktree path appears in no payload field and no environment variable:

```python
assert str(wt) not in json.dumps(payload)
assert "cd " not in payload["tool_input"]["command"]
assert "--worktree" not in payload["tool_input"]["command"]
leaks = [k for k, v in env.items() if isinstance(v, str) and str(wt) in v]
assert leaks == [], "worktree path leaked into env: %r" % leaks
```

**AFTER** (`python -m pytest tests/test_spine_rail.py -q -s -k rung4_real_git_worktree`, exit 0):

```json
{
  "wt-sid": {
    "...\\test_post_claim_rung4_real_git0\\wt-epic418\\.agent-work\\run-wt\\spine.json": {
      "spine": "...\\test_post_claim_rung4_real_git0\\wt-epic418\\.agent-work\\run-wt\\spine.json",
      "engine_session": "eng-wt",
      "worktree": "...\\test_post_claim_rung4_real_git0\\main",
      "claimed_at": "2026-08-06T08:55:31.597451+00:00",
      "path_source": "git_worktree"
    }
  }
}
1 passed, 101 deselected
```

**How I know it can fail** — the same test against the pre-change hook (`git stash push scripts/hooks/spine_rail.py`):

```
E   AssertionError: bound
E     '...\test_post_claim_rung4_real_git0\main\.agent-work\run-wt\spine.json',
E     not the worktree spine
E     '...\test_post_claim_rung4_real_git0\wt-epic418\.agent-work\run-wt\spine.json'
...
FAILED test_git_worktree_roots_lists_a_real_worktree_and_excludes_the_main_tree
FAILED test_git_worktree_roots_never_raises_and_is_bounded
FAILED test_git_probe_does_not_run_when_an_earlier_rung_answers
FAILED test_post_claim_rung4_real_git_worktree_resolved_in_a_fresh_subprocess
4 failed, 92 deselected
```

The pre-change hook wrote the phantom main-tree path — the exact 60-of-64 shape measured on 2026-08-05.

### 2. Worktree-dispatched claim → worktree-rooted entry (load-bearing)

A fresh-subprocess run of the real hook using **this run's own worktree** and **this run's own `IMPLEMENTER_PLAN.json`** as the `--file`. The "main checkout" is a throwaway temp directory carrying a **same-named decoy plan**, so the wrong answer is available and the test can distinguish "right" from "did not crash". The live main checkout is not involved.

Command: `cd /c/Programs/constellation-skills-wt/epic418-a2-440 && python scripts/checklist_engine.py --file .agent-work/issue-440-binding-cwd/crew/g1-implement/IMPLEMENTER_PLAN.json claim --session-id impl-440-g1 --claimed-by implementer --worktree .`
Payload: `cwd` = the temp main checkout, `agent_id` = `a8f0a946eaaa2fe6c` (a dispatched crew agent).

**AFTER** — `hook exit=0  stdout=''  stderr=''`, script exit **0**:

```json
{
  "demo-parent-sid#a8f0a946eaaa2fe6c": {
    "C:\\Programs\\constellation-skills-wt\\epic418-a2-440\\.agent-work\\issue-440-binding-cwd\\crew\\g1-implement\\IMPLEMENTER_PLAN.json": {
      "spine": "C:\\Programs\\constellation-skills-wt\\epic418-a2-440\\.agent-work\\issue-440-binding-cwd\\crew\\g1-implement\\IMPLEMENTER_PLAN.json",
      "engine_session": "impl-440-g1",
      "worktree": "C:\\Users\\fredc\\AppData\\Local\\Temp\\fake-main-checkout-d47dzkdr",
      "claimed_at": "2026-08-06T08:54:57.723591+00:00",
      "path_source": "cd_target"
    }
  }
}
VERDICT worktree-rooted=True  path_source='cd_target'  decoy-avoided=True
```

**BEFORE** — identical script, hook stashed back to `cbd9aee`, script exit **1**:

```json
{
  "demo-parent-sid#a8f0a946eaaa2fe6c": {
    "C:\\Users\\fredc\\AppData\\Local\\Temp\\fake-main-checkout-701kbw_c\\.agent-work\\issue-440-binding-cwd\\crew\\g1-implement\\IMPLEMENTER_PLAN.json": {
      "spine": "C:\\Users\\fredc\\AppData\\Local\\Temp\\fake-main-checkout-701kbw_c\\.agent-work\\issue-440-binding-cwd\\crew\\g1-implement\\IMPLEMENTER_PLAN.json",
      "engine_session": "impl-440-g1",
      "worktree": "C:\\Users\\fredc\\AppData\\Local\\Temp\\fake-main-checkout-701kbw_c",
      "claimed_at": "2026-08-06T08:55:06.347333+00:00"
    }
  }
}
```

Same input, same command, one line different in the answer, and that line is the whole issue. The demo script is at `<scratchpad>/demo_worktree_claim.py` (throwaway, not committed).

### 3. Targeted suite — real exit code

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q > /tmp/g1.txt 2>&1; echo "EXIT=$?"; tail -20 /tmp/g1.txt
```

```
EXIT=0
........................................................................ [ 42%]
........................................................................ [ 85%]
.........................                                                [100%]
169 passed in 3.05s
```

Redirected to a file and `$?` echoed directly, so this is the pytest exit code, not `tail`'s.

**Test counts** (re-derived by `--collect-only -q`, not trusted from the handoff):

| file | at `cbd9aee` | now |
|---|---|---|
| `tests/test_spine_rail.py` | 74 | **102** (+28) |
| `tests/test_gauge_writer.py` | 67 | **67** (untouched) |

The full suite was **not** run — the Commander runs it at g3.

### 4. Wiring grep

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
grep -rnE "looks_like_checklist|normalize_shell_path|last_cd_target|git_worktree_roots|resolve_spine_candidate|resolve_recorded_release_target|_candidate_roots|GIT_PROBE_TIMEOUT_SECONDS|_CD_RE|PATH_SOURCE_[A-Z_]+" --include=*.py ./scripts | grep -vE "def (looks_like_checklist|normalize_shell_path|last_cd_target|git_worktree_roots|resolve_spine_candidate|resolve_recorded_release_target|_candidate_roots)"
```

External production call sites, per symbol (test-file references excluded — a helper referenced only by its own tests is shipped-inert, and none of these is):

| symbol | external production call sites | where |
|---|---|---|
| `looks_like_checklist` | 1 | l.612 |
| `normalize_shell_path` | 2 | l.556, l.563 |
| `last_cd_target` | 1 | l.563 |
| `git_worktree_roots` | 1 | l.579 |
| `_candidate_roots` | 1 | l.607 |
| `resolve_spine_candidate` | 1 | l.699 |
| `resolve_recorded_release_target` | 1 | l.697 |
| `GIT_PROBE_TIMEOUT_SECONDS` | 1 | l.500 |
| `_CD_RE` | 1 | l.536 |
| `PATH_SOURCE_ABSOLUTE` | 1 | l.606 |
| `PATH_SOURCE_WORKTREE_OPT` | 1 | l.558 |
| `PATH_SOURCE_CD_TARGET` | 2 | l.567, l.569 |
| `PATH_SOURCE_PAYLOAD_CWD` | 1 | l.573 |
| `PATH_SOURCE_GIT_WORKTREE` | 1 | l.580 |
| `PATH_SOURCE_PROJECT_DIR` | 1 | l.583 |

**Zero external call sites for no symbol.** The stop condition is not hit. `_resolve_abs` is deleted; `grep -rn "_resolve_abs" --include=*.py .` returns nothing (exit 1).

### 5. Deliverable path check

```
git check-ignore scripts/hooks/spine_rail.py  -> EXIT=1  (not ignored, will be committed)
git check-ignore tests/test_spine_rail.py     -> EXIT=1  (not ignored, will be committed)
```

`git status --short`: ` M scripts/hooks/spine_rail.py`, ` M tests/test_spine_rail.py`, `?? .agent-work/issue-440-binding-cwd/`.
`git diff --stat`: 2 files, 895 insertions, 13 deletions. No new test module, so `git diff` and `git status` show the same two tracked files. `IMPLEMENTER_RESULT.md` is under `.agent-work/` by design and is correctly absent from the diff.

### 6. Confirmatory spot-checks

- **Per-rung units** — all six rungs covered and each fails against pre-change code. Rungs 1–2 (11 tests) all RED under stash: the headline test bound the main-checkout decoy `...cd_into_worktr0\.agent-work\run1\spine.json` instead of `...-worktree\.agent-work\run1\spine.json`. Rungs 0/3/5 + bind-nothing (7 tests) all RED.
- **No-raise fuzz** — `test_post_tool_use_never_raises_on_junk`: 16 degraded payloads (missing/None `tool_input`, unbalanced quote, `cd` with no target, NUL byte in a `cd` target, non-string `cwd`, 500-char `--file=`) all return `{}` without raising.
- **`release` after the spine is deleted** — `test_post_release_removes_its_own_entry_after_the_spine_file_is_deleted`, RED against the m3 code (the entry leaked), green now.
- **`release` recorded-lookup beats a validating decoy**, **ambiguity falls through to the ladder**, **`run1` does not match `run11`**, **an unresolvable release still clears the nudge ledger** — all covered.
- **Probe is off the common path** — `test_git_probe_does_not_run_when_an_earlier_rung_answers` monkeypatches `git_worktree_roots` to record calls and asserts it is never invoked for an ordinary claim or an absolute `--file`. **Bounded** — `TimeoutExpired` and `OSError("no git")` both return `[]`, and `0 < GIT_PROBE_TIMEOUT_SECONDS <= 5` is asserted.

## TDD evidence
- **Failing test observed:** yes, at every gate, against real pre-change code. m1: 7 failed. m2: 11 failed under `git stash` of the hook. m3: 4 failed under stash, with the wrong path printed verbatim. m4: 3 failed against the then-current code.
- **Passing test observed:** yes — 81 → 92 → 96 → 102 green, and 169 green across both target files.
- **Refactor while green:** yes — extracting `git_worktree_roots` and the docstring update were done with the suite green.

## Docs/contracts touched
- `scripts/hooks/spine_rail.py` module docstring — the "Stdlib only" line now names `re` and `subprocess` and states that the one subprocess is a bounded `git` probe, never the engine. Changing behaviour without changing the contract it violates would have left the file lying about itself.
- No other doc touched (out of allowed scope) — see Out-of-scope observations.

## Assumptions
- `git` is on `PATH`. If it is not, rung 4 yields nothing and the ladder falls to rung 5 — the same answer as before this change, never an error.
- The Bash tool on this box is git-bash, so `cd` targets arrive MSYS-style. Both forms are handled and unit-tested.
- Pre-existing entries in a live store have no `path_source`. Readers use `.get`-style access and none require the field, so old entries stay readable.

## Stop conditions hit
None. No allowed scope exceeded, no exclusion touched, no decision needed beyond the granted authority, and every piece of required evidence was produced.

## Out-of-scope observations
1. **`docs/GAUGE_WRITER_HOOK.md` is now stale.** § "Known limits of the binding store itself (#419)", first bullet, states this defect as live, including the "60 of 64 live entries" measurement. Docs were not in my allowed scope so I did not edit it. It needs to be rewritten as fixed-in-#440, with the remaining three bullets left standing. Recommend the Commander do this at integrate, or file it.
2. **The live store still holds the wrong-shaped entries.** Nothing migrates them, and there is still no reaper for abandoned keys (a named exclusion). The store self-heals only as sessions re-claim under the fixed writer. A one-time sweep may be worth an issue.
3. **The fourth known limit is now partly addressed as a side effect.** "The recorded path is not validated" — a shell-mangled `--file` like the literal `$E` or `x` found in the 2026-08-05 sweep can no longer enter the store on a **relative** path, because it will not validate. An **absolute** mangled path still can, by rung 0's deliberate design. Worth noting when that limit is next reviewed; I did not chase it.
4. **Corner cases named at the code site, not silently dropped** (per the scope-discipline constraint): an earlier `cd` in the same command is not a fallback when the last one fails (comment on `last_cd_target`); an MSYS bare drive root `/c` is not converted (comment on `normalize_shell_path`). Both are commented in the source and neither has been observed in a real engine invocation.
5. **`resolve_recorded_release_target` sits next to the no-reaper limit.** A release that resolves nothing still leaves its key. That is the named-and-excluded abandoned-key problem; I left it and did not widen it.

## Workflow Feedback

- **Handoff gaps:** the **Allowed Scope** field lists only source and test files, but the change makes `docs/GAUGE_WRITER_HOOK.md` factually wrong — and that same doc is named in **Map Anchors** as the hash-pinned substitute for the missing architecture map. So the handoff points at a document as the authority on the defect while excluding the ability to correct it once the defect is gone. It needs one line either way: "update the doc" or "leave the doc, Commander does it."
- **Context rediscovered:** nothing about the source. But the handoff's **Close Criteria** say "no existing test's assertion is weakened," and it turned out **14 existing tests** claim spines that were never created on disk — so validate-or-bind-nothing broke all of them. Making each fixture write a real spine file is *strengthening* the fixture, not weakening an assertion, but that is a judgment call the handoff did not anticipate and it is the single biggest chunk of the diff. A one-line heads-up ("existing claim tests use fictional spine paths and will need real files") would have saved the discovery.
- **Instructions improvised around:** the implementer plan template pairs a `check: null` TDD-red postcondition with a `command` green check on the **same gate**, which assumes each gate's tests are written and turned green within that gate. That works, but it means a gate whose implementation shares code with the previous gate cannot show an incremental red. I handled it by demonstrating red against the **pre-change** code with `git stash` — stronger evidence than incremental red, and the honest thing given the defect shape — and recorded that in each `attest --note` rather than quietly claiming a red I had not seen.
- **What would have made this easier:** name the pre-existing test-fixture debt in the handoff. When a change tightens a validity rule, the tests most likely to break are the ones whose fixtures were never valid in the first place, and only someone who has already read those tests knows that.

## Return status
`complete`
