# Delta Review Result — A+B follow-up commits (`99a46a08..HEAD`)

## Verdict: APPROVE

## Per-commit verdicts

- `4e13b789` (F2, test restoration): APPROVE
- `ee59a7b9` (F1, doctrine doc): APPROVE
- `8957d925` (map regen): APPROVE

## Scope and base checks

- `git merge-base efe92791 HEAD` = `efe92791d74105164cab64e2aa80f442d4541597` — base confirmed unchanged. `main` has moved three commits ahead (`cd2e1c01`, `5b61d581`, `a0777cfd`, ...) and none of them appear in `git log efe92791..HEAD`. No rebase, no merge.
- `git diff --check 99a46a08..HEAD` exits 0.
- `git diff --stat 99a46a08..HEAD`: exactly three files — `map/INDEX.md` (6 lines), `skills/commander/references/crew-dispatch.md` (10 lines, all additions), `tests/test_crew_launcher.py` (87 lines, all additions). Nothing else moved in this range.

## F2 (`4e13b789`) — mutation test

Confirmed `ParentOptionalForRecoveryVerbsTests` (3 tests: `test_resume_succeeds_with_no_parent`,
`test_bare_abandon_succeeds_with_no_parent`, `test_verify_result_succeeds_with_no_parent`) build
synthetic registry entries by hand and call `RC.main([...])` directly — no `CrewSpec` is
constructed on any of these three paths (confirmed by reading `run_crew.py`: `resume_crew`
replays a prior entry verbatim, `--abandon` alone only flips a registry flag, and
`ExternalBackend.verify` reads the stored entry directly). Not vacuous.

Mutation performed: copied the worktree to a scratch directory (not the reviewed worktree — no
source/tests were edited in `/tmp/constellation-20260821-ab`) and moved `--parent` enforcement
from `CrewSpec.__post_init__` (the current, correct site) to argparse `required=True` on the
`--parent` `add_argument` call — the exact future mistake named in the handoff.

Result:
- Unmutated: `pytest -k ParentOptionalForRecoveryVerbsTests` → 3 passed.
- Mutated (`--parent required=True` in argparse): all 3 FAIL with
  `SystemExit: 2` / `error: the following arguments are required: --parent`, raised by argparse
  before `RC.main` even reaches the registry/resume/abandon/verify logic.

This proves the tests would catch the migration named in the handoff — they are not
mutation-blind and not passing vacuously.

`--verify-result` path: confirmed genuinely exercised, not short-circuited. The test passes
`--accept-mtime-only-risk "<reason>"`; `run_crew.py` threads this into `verify_crew_result`
(around line 2449), which on no spine evidence but an accepted risk reason writes an accept
record and proceeds to mark the entry `"completed"` (lines ~2100–2110). The test asserts both
`code == 0` and that the registry status is now `"completed"` — a real assertion on real state
change, not just an exit code.

## F1 (`ee59a7b9`) — judged as an actionable document

- **Names the literal value**: yes. "Pass your own `SPINE_SESSION` (the identity you were bound
  with, read from your own environment) as `--parent`: `run_crew.py --parent "$SPINE_SESSION" ...`"
  — a copy-pasteable command, not just "a parent is required." This clears the bar the handoff
  set (a value-only requirement would have been a new trap).
- **States the `--resume`/bare-`--abandon` exemption**: yes, explicitly: "`--resume` and a bare
  `--abandon` construct no `CrewSpec` and so need no `--parent` at all."
- **Shape match**: matches the existing "Name a tier" section's shape exactly — refusal site
  (`CrewSpec.__post_init__`) → what to pass → where the value comes from → the
  resume/bare-abandon exemption, in the same order, same "This file used to say nothing about
  X" framing convention as the tier section. Not a competing convention.
- **Factual claim verified**: "`crew-runs.json:parent` is what `verify_declared_dispatch.py`
  checks a crew's dispatch against" — confirmed true by reading
  `scripts/verify_declared_dispatch.py` line 48: `if entry.get("parent") == parent and
  entry.get("model") == model:` against loaded registry entries. True.
- Consistency check: `tests/test_crew_dispatch_doctrine.py` (which pins specific "Name a tier"
  content in this same file) still passes unmodified, 2 passed — F1's addition is a separate
  section and did not disturb it.
- `SPINE_SESSION` is independently established elsewhere in this same file as the correct
  ambient value (the full-suite polling snippet earlier in the file does
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT ...`), so F1's claim that it is "the
  identity you were bound with, read from your own environment" is consistent with the rest of
  the doctrine, not invented for this section.

Judged against the standing criterion (ease of use, honest-agent-about-to-make-a-mistake): this
closes the exact gap the prior review found — a Commander following the doctrine as written
would previously have built a refused command and learned `--parent` only from the refusal.
Now the doctrine states, upfront, the exact flag, the exact value, and the exact exemption.

## Map (`8957d925`)

Read the whole diff. Exactly 3 line-pairs, entity-count only:
- `tests: 95 modules, 5319 entities` → `5323 entities` (twice: summary line + section header)
- `tests.test_crew_launcher` `(338 entities, 259 holes)` → `(342 entities, 262 holes)`

No module added/removed, no link retargeted, no docstring changed. Matches the handoff's
predicted shape exactly. F1's markdown-only doc edit contributes zero delta (`crew-dispatch.md`
is never indexed by `scripts.code_map`), consistent with the commit message's own claim.

## Suite

Ran in the foreground, blocking, from `/tmp/constellation-20260821-ab`:

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python3 -m pytest -q
```

Result: `3472 passed, 6 skipped, 1224 subtests passed in 145.08s (0:02:25)`. Zero failures.
This matches the implementer's reported counts exactly (3472 passed, 6 skipped, 1224 subtests,
zero failures).

Also ran targeted: `tests/test_crew_dispatch_doctrine.py` → 2 passed;
`tests/test_crew_launcher.py -k ParentOptionalForRecoveryVerbsTests` → 3 passed (unmutated).

## Constraints honored

No `mcp__spine__*` tool called. No commit, push, PR, or edit to source/tests made in the
reviewed worktree (`/tmp/constellation-20260821-ab`) — the mutation test was performed against
a separate scratch copy outside that worktree, which was discarded after use.

## Outside scope / workflow feedback

- Nothing outside scope found. File set matches the handoff's named three files exactly; no
  drift, no scope creep.
- Workflow note: an earlier attempt in this same review session ended a turn waiting on a
  `Monitor` completion notification for the full-suite run instead of blocking on it in the
  foreground; that stalls the lane since the notification doesn't resume a stopped turn. Redone
  correctly per the coordinator's redirect — foreground `Bash` call, blocked on directly, timeout
  600000ms. Flagging only so the pattern is known for future full-suite runs in this kind of
  lane: run it in the foreground and block, don't background/Monitor it.
