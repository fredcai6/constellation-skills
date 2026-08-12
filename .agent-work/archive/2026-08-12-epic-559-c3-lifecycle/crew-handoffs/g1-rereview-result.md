# Review Result — g1 RE-REVIEW (attempt 2)

## Assigned Gate
`g1` — open Constellation work in one call (`scripts/spine_lifecycle.py`), reviewing the rework (attempt 2) after a first review BLOCKed on a confirmed missing `newline="\n"`.

## Verdict
`APPROVE`

## Handoff compliance
The rework did exactly what its own handoff (implied by `g1-rework-result.md`) required: fixed the one write site with `newline="\n"`, audited every other write in the module (independently re-confirmed: `grep -n "write_text"` returns exactly one hit, and `.open(`/`.write(`/`writelines`/`json.dump(` all return zero hits), added a byte-level regression test plus a host-independent AST-level guard with a mutated positive control, and collapsed `_rollback`'s three inline `subprocess.run` calls onto a `_best_effort_git` helper while preserving its never-raises contract. All satisfied — see the four numbered findings below for independent verification of each.

## Scope drift
None. `git diff --stat` vs `HEAD` shows only `scripts/spine_lifecycle.py`, `tests/test_spine_lifecycle.py`, `map/INDEX.md` (regenerated, confirmed idempotent), and Commander's own `.agent-work/epic-559/c3-lifecycle/*` bookkeeping. `checklist_engine.py`, `validate_spine.py`, `settings.json`, `.mcp.json`, `docs/agents/*`, `skills/**` all show empty diffs. `scripts/generate_spine.py` is untouched — confirmed line 910 still carries the identical `newline=` omission, correctly left alone as pre-existing and out of scope. Nothing staged (`git diff --cached --stat` empty, so no `git add -A`). Branch is `epic-559/c3-lifecycle`, not `main`.

## Evidence verdict
Reproduced every claimed number independently, not re-read:
- `pytest -q tests` → **2856 passed, 3 skipped, 1121 subtests** (exact match).
- `validate_spine.py --sweep` → **23** (exact match).
- `map/INDEX.md` regeneration → idempotent (byte-diffed before/after a fresh `code_map build`, no difference).
- The mutation experiment in `g1-rework-result.md` (strip `newline="\n"`, rerun the 4 targeted tests, expect 2 failures) — reproduced independently with my own copy/restore cycle: same `.FF.` pattern, same two tests red, same two green, then restored and reconfirmed 4/4 green.

TDD evidence is real: the AST-level guard (`TestEveryWriteTextPinsNewline`) demonstrably goes red when the fix is removed; the byte-level guard (`TestSpineFileHasNoCRLF`) demonstrably does not, on this host, by design — not a false claim, a documented and verified Linux blind spot.

## Code/doc quality
Minimal, contained, and consistent with house style (`_best_effort_git` mirrors the shape of the pre-existing `_git`, differing only in its no-raise contract; the AST-check pattern matches `tests/test_mcp_adoption.py::_cli_only_verb_violations` as claimed). Fresh Fowler pass on the rework diff: 12/12 baseline smells assessed, 0 flagged, 0 overridden (record: `.agent-work/epic-559/c3-lifecycle/FOWLER_PASS.json`; `verify_fowler_pass.py` exits 0). The one smell the first review flagged — three duplicated inline `subprocess.run` calls in `_rollback` — is resolved by the `_best_effort_git` extraction.

## Map impact verdict
- **Evidence supports claimed change:** yes — `_rollback`/`_best_effort_git` are internals-only (no signature or caller-visible change), matching the rework result's claim.
- **Constraints not violated:** yes — `docs/agents/CREW_CONTEXT.md`'s "every write pins `newline='\n'`" rule is now honored by this module's one write site.
- **Notes match the diff:** yes — the rework result's Map Impact section correctly scopes the change to internal structure only, no new capability.
- **Decision candidates surfaced:** none required for this bounded fix.
- **Durable context routed:** yes — the two out-of-scope items (`generate_spine.py:910`'s identical omission; `episode_capture.py`'s manifest-root path-doubling) remain correctly flagged out-of-scope/triage, not silently dropped or re-litigated here.

## Reconciliation check
No divergence from recorded architecture. No new production caller (door wiring remains g3, per `LIFECYCLE_CONTRACT.md` sec 8's deferral list).

## Findings

1. **Fix completeness — CONFIRMED.** `scripts/spine_lifecycle.py:265` now reads `spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8", newline="\n")`. Independently enumerated every write site in the module (`grep -n "write_text"` → 1 hit; `.open(`/`.write(`/`writelines`/`json.dump(` → 0 hits): the count is 1, and it carries the fix. Not an under-inclusive enumeration — there was only ever one instance to fix, and it is fixed.

2. **Guard falsifiability — CONFIRMED.** I independently stripped `, newline="\n")` from the shipped source (not the implementer's transcript), reran `pytest -k "CRLF or PinsNewline" -v`, and got the same `.FF.` result: `test_the_shipped_module_has_no_violations` and `test_violating_a_mutated_copy_missing_newline_is_caught` went red, the other two stayed green. Restored the file, confirmed `git diff --stat` matched the original rework diff exactly, reran — 4/4 green. This guard can fail, and I proved it myself rather than trusting the reported transcript.

3. **Byte-level test is genuinely byte-level — CONFIRMED, with the implementer's own caveat correct.** `TestSpineFileHasNoCRLF` reads via `Path.read_bytes()`, not a text-mode read — so it is not a check that "cannot fail" by construction. It is, however, inert on this Linux host (`os.linesep == "\n"`, confirmed it stayed green through the mutation in finding 2 above), which is exactly why the AST-level `TestEveryWriteTextPinsNewline` exists as the host-independent layer. Both statements in the rework result are accurate.

4. **`_rollback` still never raises — CONFIRMED.** `_best_effort_git` is a pure extraction of the same `subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)` call shape used by all three original inline calls — no `check=True`, no returncode inspection, identical raise surface (only process-launch failure, e.g. a missing `git` binary, could raise, and that was equally true before the refactor). Verified further: I wrote and ran two ad-hoc spy tests (monkeypatching `_rollback` to record worktree/branch state at the exact moment it fires, for both the late-compile-failure path and the `check_distinct_real`-forced path), confirming the real worktree and branch existed at call time and were then removed — not merely "never created." Deleted the scratch test file before finishing; `git status` is clean of it.

## Gate-as-a-whole re-check
Did not inherit the first reviewer's approval of the untouched parts. Re-verified directly: rollback removal asserted against real `git worktree list --porcelain` / `git branch --list` (not string comparison against code output); `check_distinct_real` returning not-ok forces rollback while `git worktree add` itself still exits 0 for real (only the in-process self-verify is faked); the origin round-trip test calls `checklist_engine.claim/start/attest/attach/advance` directly on the compiled dict — the real engine module, not simulated. All confirmed, no new defects found in previously-approved territory.

## Blockers
- none

## Out-of-scope observations
- `generate_spine.py:910` carries the identical `newline=` omission; confirmed still untouched. Pre-existing, correctly out of scope for g1 (already recorded by the first reviewer and the rework handoff).
- `episode_capture.py`'s `manifest_root()` path-doubling for a reviewer-survey-shaped path (`.agent-work/<work-id>/<gate>-review/review.json`), first flagged by the attempt-1 reviewer as `tc1`, remains open and unrelated to this diff — still a Triage candidate, not touched by this rework.

## Single most likely way this gate produces a green run that is wrong
The AST-level guard (`TestEveryWriteTextPinsNewline`) is the only layer that can actually catch a regression on this Linux CI host — the byte-level test is permanently inert here. That guard works by string-matching `, newline="\n")` in the source text (`_missing_newline_write_text_calls`'s AST walk checks for a `newline=` keyword by name, not by value). If a future edit legitimately needed a *different* newline value, or restructured the write call so the keyword moved off the direct `.write_text(...)` call (e.g., built via `**kwargs` or a wrapper), the guard would either false-negative (miss a real regression) or need updating — and nothing forces that update, since the check only runs on this one module by construction, not project-wide. The gate is sound today; it depends on this module's write call staying in its current direct, literal-keyword shape.

## Workflow Feedback

- **Handoff gaps:** none — the four numbered checks and the gate-as-a-whole re-check list were precise and directly actionable; no ambiguity.
- **Context rediscovered:** the same `SPINE_FILE`/`SPINE_SESSION` disambiguation every prior crew in this gate has independently hit — those env vars point at the Commander's own `execute.json`, not a dedicated checklist for this dispatch (confirmed: `spine_status` returned Commander-level content — `run_crew.py` dispatch instructions, `REPLAN_INPUT.json` — and `crew-runs.json` confirms `"spine": null` for every implementer/reviewer crew record). Built and drove my own survey via `scripts/checklist_engine.py` directly on `g1-review/review.json`, appending eight `rr*` items for this re-review rather than authoring a fresh survey file, per `docs/CHECKLIST_SCHEMA.md`'s worked example (a re-reviewed survey appends new items into the same file rather than starting over). This is now the fourth crew in this gate to independently re-derive the same disambiguation — naming it explicitly in future handoffs, as the rework's own Workflow Feedback already suggested, would save a fifth detour.
- **Instructions improvised around:** the reviewer skill's guidance to "create the checklist at the path the handoff gives" assumes a fresh survey; this was a re-review of an already-consolidated survey (attempt 1, verdict BLOCK, lease released). I appended eight new `rr*` items to the existing `g1-review/review.json` rather than overwriting or creating a second file, preserving the attempt-1 record intact, then consolidated with `--override-reason` explaining that `r4-quality`'s original `fail` is resolved (not downgraded) by this attempt's independent re-verification. This matches `docs/CHECKLIST_SCHEMA.md`'s documented survey-append pattern but the reviewer skill itself doesn't spell out the re-review case explicitly.
- **What would have made this easier:** a one-line note in the reviewer skill on the re-review case (append to the existing survey; consolidate with `--override-reason` citing the resolved fail) would remove the need to reconstruct this from `docs/CHECKLIST_SCHEMA.md`'s worked example.

## Return status
`complete`
