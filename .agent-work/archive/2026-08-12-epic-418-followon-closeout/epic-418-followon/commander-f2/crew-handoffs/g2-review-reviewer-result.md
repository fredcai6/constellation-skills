# Review Result

## Assigned Gate
`g2-review` (issue #541, friction capture — epic-418-followon, wave 2, commander-f2)

## Result
`BLOCK`

## Handoff compliance
Verified against commit `ef4b13c1` (`e2b8f04e..ef4b13c1`). The capture mechanism itself does
what the handoff asked: all 15 in-scope `_tool_error(...)` call sites in `call_tool()`/`main()`
now carry `tool=`/`rejection_class=` — 10 of 10 real `_require()` call sites
(`missing-required-argument`), 4 of 4 unknown-`action` branches (`spine_lease`,
`spine_evidence`, `spine_halt`, `spine_survey_result`), 1 `unknown-tool` site in `main()`. The
sole bare `_tool_error` call (`main()`'s `except KeyError` fallback) is confirmed genuinely
unreachable: `TOOL_NAMES` is exactly the 7 names `call_tool()`'s `if`-branches handle, and
`main()` already refuses any name not in `TOOL_NAMES` before calling `call_tool()`, so
`call_tool()`'s own `raise KeyError(name)` can never fire. Reproduced `seed_rejections.py`
myself (3 rejections through a real subprocess, 3 records with the exact classes claimed) and
`verify_episode_captured.py epic-418-followon/commander-f2 --store-root episodes` independently
(exit 0, 1 episode found). Stop conditions: none hit, matches the implementer's report.

## Scope drift
None. `git diff e2b8f04e ef4b13c1 --stat` touches only `scripts/mcp_spine_server.py`,
`tests/test_mcp_friction_capture.py`, `episodes/active/...`, `map/INDEX.md`, and
`.agent-work/epic-418-followon/commander-f2/**` bookkeeping/evidence. All 5 excluded files
(`scripts/checklist_engine.py`, `scripts/apply_episode_delta.py`, `scripts/episode_capture.py`,
`docs/EPISODE_STORE.md`, `scripts/hooks/spine_rail.py`) show a 0-line diff across the same
range, confirmed by command.

## Evidence verdict

**Close criterion 2 (fail loud, every occurrence — N≥2) holds up as a genuine property, not an
enumeration.** `tests/test_mcp_friction_capture.py::LoudFailureOnCaptureWriteTests::test_three_induced_write_failures_in_one_process_yield_three_messages`
induces **3** write failures across **3 different classes in one process** and asserts exactly
**3** occurrences of `"REJECTION CAPTURE FAILED"` in stderr via `assertEqual` (not `assertIn`),
plus per-occurrence content checks (`teleport`, `condition_id`, `does_not_exist` each present) —
this is the N≥2/N-separate-messages shape the handoff demanded, not a single-induced-failure
test standing in for "every."

**Mandatory mutation — passed the way it should.** Silenced the `OSError` branch in
`_log_rejection` (removed the stderr write, bare `except OSError: pass`). Result:
`tests/test_mcp_friction_capture.py::LoudFailureOnCaptureWriteTests::test_three_induced_write_failures_in_one_process_yield_three_messages`
went **RED** (`AssertionError: 3 != 0`, `1 failed, 6 passed`). Restored from a pre-mutation
backup (`md5sum` identical, `git diff -- scripts/mcp_spine_server.py` 0 lines); re-ran:
`7 passed`.

**Self-invented mutation — found a real, closeable test-suite coverage gap (not a live
defect).** Added a module-level `(tool, rejection_class)` dedup set inside `_log_rejection` so a
**second identical** door-own rejection in the same process is silently dropped. Result: the
**entire** `tests/test_mcp_friction_capture.py` suite stayed **7 passed, 0 failed** — no test in
the file induces the *same* door-own rejection twice in one process, so the literal "not one per
run" half of close criterion 1 is untested. Live-reproduced independently outside pytest: two
identical `spine_lease action=teleport` calls in one process against the **mutated** code wrote
only **1** record (expected 2); the identical repro against the **clean, unmutated** code
(confirmed `git diff` 0 lines before mutating) correctly wrote **2** records. So the shipped
implementation is not defective — only the suite's proof of that specific clause has a gap.
Restored (`md5sum` identical, `git diff` 0 lines); re-ran: `7 passed`. Flagged as triage
candidate `tc1` in the survey (add a repeated-identical-rejection test).

**Separate, independent defect that blocks on its own: the full suite is not 0 failed at
HEAD.** `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
fails: a fresh `python -m scripts.code_map build` shows `tests: 66 modules, 3741 entities`, but
the committed `map/INDEX.md` shows `tests: 65 modules, 3721 entities` — missing
`tests/test_mcp_friction_capture.py`'s contribution entirely, despite the implementer's claim
of "map rebuilt and fresh... 2 passed." A/B-verified this is a **regression introduced by this
gate's own commit**, not pre-existing: built a detached `git worktree` at the prior commit
`e2b8f04e` and `MapTreeFreshnessTests` passed there (`2 passed`); reproduced the failure again
at `ef4b13c1` in isolation (`1 failed, 1 passed`). Consequently `python -m pytest -q` at HEAD is
**`1 failed, 2282 passed, 1 skipped, 1079 subtests passed`**, not the `0 failed` the handoff
requires as evidence and not what the implementer's own result claims for this same commit.

## Code/doc quality
Fowler pass recorded to `.agent-work/epic-418-followon/commander-f2/g2-review/fowler-pass.json`;
`python scripts/verify_fowler_pass.py .agent-work/epic-418-followon/commander-f2/g2-review/fowler-pass.json`
exits 0 (`smells=12, flagged=[], overridden=['long-method', 'duplicated-code',
'primitive-obsession', 'shotgun-surgery', 'comments-as-deodorant']`). Every override cites a
logged repo standard: the module's own "Grouping decision" docstring; the g1 choke-point pin
(`tests/test_mcp_identity.py::IdentityBindingPinTests::test_call_tool_can_only_produce_content_two_ways`)
that forced the repeated inline `_tool_error(...)` shape over a wrapper (a wrapper was tried and
produced 14 pin offenders, per the episode's own `a2`–`a4`); the file's existing all-string
action vocabulary; and the same file-level documentation-density standard four prior g1 Fowler
passes already applied to this exact file. No new blocking quality finding from this pass — the
substantive defects are the map staleness and the dedup coverage gap above.

## Map impact verdict
- **Evidence supports claimed change:** Mostly. The behavior/capability claim (door-own
  rejections now durably logged, one record per occurrence, loud on write failure) is genuinely
  backed. The "map rebuilt, entity count +1" claim is backed for the `scripts` package
  (1070→1071, matches) but **not** for `tests` (stayed 65/3721 instead of the true 66/3741) —
  see Evidence verdict.
- **Constraints not violated:** Yes — the choke-point pin was stressed, not weakened (confirmed
  via the Fowler pass's duplicated-code/shotgun-surgery overrides), and no unowned file was
  touched.
- **Notes match the diff:** Mostly, with the one gap above (map staleness not caught by the
  implementer's own claimed rebuild step).
- **Decision candidates surfaced:** N/A — no new authority-requiring decision in this diff.
- **Durable context routed:** Yes — the episode's `artifact-ref` lines and the `tc1` triage
  candidate for the doubled-path defect in `episode_capture.manifest_root()` were carried
  forward correctly by the implementer; this review adds one more triage candidate (the dedup
  coverage gap).

## Reconciliation check
Close criterion 6 (episode is a record, never a rule): read
`episodes/active/epic-418-followon_commander-f2-001.md` in full — grepped every assertion
(`a1`–`a5`, `d1`) for should/must/anyone/future-agent/expect-the-same/always/never-do/
remember-to/be-sure-to language: zero matches. Cross-checked mechanically:
`scripts/verify_episode_observations.py --strict` over the whole `episodes/` store reports **0
unlisted offenders** (551 statements examined, 11 pre-existing exceptions from other issues,
none from this episode). Note (not a finding): the implementer's own
`g2-implement-implementer-result.md` Workflow Feedback contains one prescriptive sentence
("Anyone doing follow-on work at this call site should expect the same pin") — that lives in a
crew-handoff artifact, not `episodes/`, so it is outside the Retired Learning Playbook's scope.

Close criterion 5 (coverage boundary honesty): the implementer's table correctly states the
client-side schema rejection is structurally uncapturable server-side and does not imply
otherwise; it also correctly carries forward the handoff's confidence flag (zero counted
fumbles is a reading of this instrument, not evidence that fumbles do not occur).

## Blockers
- `tests/test_code_map.py::MapTreeFreshnessTests` fails at HEAD (`ef4b13c1`) — `map/INDEX.md`
  was not actually kept fresh despite the implementer's claim; `python -m pytest -q` is
  `1 failed, 2282 passed, 1 skipped`, not `0 failed`. Fix: rerun
  `python -m scripts.code_map build --root .` and commit the result.
- `tests/test_mcp_friction_capture.py` has no test inducing the *same* door-own rejection twice
  in one process — a per-`(tool, class)` dedup mutation passes the whole file green while
  silently dropping every repeat after the first (live-reproduced; shipped code is currently
  correct). Fix: add one test asserting 2 separate records for 2 identical induced rejections.

## Out-of-scope observations
- `tc1` (this survey): the repeated-identical-rejection test gap above, routed to Triage.
- Carried forward from the implementer's own report: `episode_capture.manifest_root()` /
  `context_manifest.manifest_path()` doubles the path one level deeper for a 3-segment work-id
  (already flagged `tc1` in the implementer's own plan) — not independently re-verified by me,
  reported as received.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's "Survey State Location" and close-criteria
  table were internally consistent and matched what `scripts/checklist_engine.py` expected once
  instantiated.
- **Context rediscovered:** the committed `map/INDEX.md` staleness was not flagged anywhere in
  the handoff or the implementer's result as a risk, and the implementer's own evidence
  (`2 passed` for `MapTreeFreshnessTests`) actively asserts the opposite of what HEAD now shows —
  I only found it because "Required in your result: `python -m pytest -q` at 0 failed" forced me
  to run the full suite myself rather than trust the implementer's quoted output. Worth naming
  explicitly in a future handoff: rerun the full suite yourself, do not trust a quoted count from
  an evidence section, even when it looks precise (exact numbers, subtests included).
- **Instructions improvised around:** none — the mandatory-mutation instruction was followed
  literally (silence the write-failure path), and "invent one of your own" was read as licence to
  target a different dimension of the same claim (repetition-of-identical-rejection) rather than
  a second variant of the same write-failure path, since the write-failure path was already
  well-covered by the shipped test.
- **What would have made this easier:** the handoff could name that `python -m pytest -q` is
  itself a required check on the reviewer, not just a report field — it already does
  ("Required evidence from you... `python -m pytest -q` at 0 failed"), and that framing is
  exactly what caught this. No change needed; noting it worked as intended.

## Return status
`complete`

---

## Survey / engine evidence

- Survey: `.agent-work/epic-418-followon/commander-f2/g2-review/review.json`, driven through
  `scripts/checklist_engine.py` claim → start/record (r0–r6) → flag-candidate (tc1) →
  consolidate(BLOCK) → release. Per-item verdicts: `r0-context` pass, `r1-handoff` pass,
  `r2-scope` pass, `r3-evidence` **fail**, `r4-quality` pass, `r5-reconciliation` pass,
  `r6-fowler` pass. 6 pass / 1 fail (5 fail-counted items — `r0,r1,r2,r4,r5,r6` — versus 1 fail,
  `r3-evidence`). Overall verdict `BLOCK` (no `--override-reason` used — the fail is a real
  blocker, not an out-of-scope finding being waved through).

### Mutation evidence (exact test ids, restore proof)

1. **Mandatory mutation.** Change: `scripts/mcp_spine_server.py` `_log_rejection`'s
   `except OSError as exc: sys.stderr.write(...)` replaced with `except OSError: pass`.
   Test: `tests/test_mcp_friction_capture.py::LoudFailureOnCaptureWriteTests::test_three_induced_write_failures_in_one_process_yield_three_messages`.
   RED: `AssertionError: 3 != 0`, `1 failed, 6 passed`. Restore proof:
   `md5sum scripts/mcp_spine_server.py` → `5b2e783031c8c0aafc4f7cdc92db2422` both before and
   after; `git diff -- scripts/mcp_spine_server.py` → 0 lines. GREEN after restore: `7 passed`.

2. **Self-invented mutation.** Change: added `_ALREADY_LOGGED: set[tuple[str, str]] = set()` at
   module scope and, at the top of `_log_rejection`, `key = (tool, rejection_class); if key in
   _ALREADY_LOGGED: return; _ALREADY_LOGGED.add(key)`. Test suite result: `tests/test_mcp_friction_capture.py`
   full file → **7 passed, 0 failed** (did not catch it). Independent live repro (not a pytest
   test id — a standalone subprocess script): 2 identical `spine_lease action=teleport` calls in
   one server process → **1** record written under the mutation, **2** records written against
   the clean code. Restore proof: `md5sum` → `5b2e783031c8c0aafc4f7cdc92db2422` both before and
   after; `git diff -- scripts/mcp_spine_server.py` → 0 lines. GREEN after restore: `7 passed`.

### `python -m pytest -q` (final, at HEAD, post-restore)
```
1 failed, 2282 passed, 1 skipped, 1079 subtests passed in 100.92s (0:01:40)
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```

### `git status --porcelain` (this worktree, at end of review)
```
?? .agent-work/epic-418-followon/commander-f2/g2-review/
```
(Only my own new survey/evidence directory, created under the issue workbench per the handoff's
Survey State Location. `scripts/mcp_spine_server.py` is byte-identical to HEAD — confirmed via
`git diff` 0 lines and matching `md5sum` immediately above.)
