# Implementer Handoff

## Gate
g2 (issue #525)

## Task
Concurrent crews sharing one scratch/evidence area can silently collide under generic filenames (measured: a `g8` reviewer found `r0`-`r6` finding-files left by an *earlier gate's* reviewer, using the same generic names it was about to use). Give `run_crew.py` a way to reserve a namespaced scratch directory per dispatch, keyed on the SAME identity tuple the registry's own duplicate-detection already uses, and expose it to the CLI-backend child via a new env var. A genuine collision on that reservation must raise, never silently overwrite.

## Protected Intent
No evidence loss must ever be invisible. If two dispatches ever do collide on the same reserved directory, that must be a loud, raised error — never a silent overwrite where "the file exists, it parses, it describes someone else's gate" (the exact failure mode #525 was filed over).

## Test Mode
TDD required, in `tests/test_crew_launcher.py`, same conventions as g1.

## Close Criteria
- New function `scratch_dir(work_id: str, gate: str, role: str, worktree: str, attempt: int, root: Path) -> Path`, placed near `run_log_paths` (`:230-234`). **Must key on the FULL `(work_id, gate, role, worktree, attempt)` tuple** — the same tuple `active_duplicate`/`next_attempt` (`:330-390`) actually use for duplicate-detection/attempt-numbering. This is a hard requirement, not a style choice: `next_attempt` scopes attempt numbers PER WORKTREE, so two different worktrees dispatching the same `work_id`/`gate`/`role` can independently reach `attempt=1` — if `worktree` were left out of `scratch_dir`'s key, those two would collide on the identical directory, reintroducing #525 one field narrower. (An earlier draft of this plan made exactly this mistake; it was caught and fixed before this handoff was written — do not repeat it.)
- Path shape: `.agent-work/<work_id>/crew-scratch/<gate>-<role>-attempt-<attempt>-<wtkey>/`, where `<wtkey>` is a short stable hash (e.g. `hashlib.sha256(worktree.encode("utf-8")).hexdigest()[:12]`) of the **raw** `worktree` string exactly as recorded on the registry entry — do NOT resolve it to an absolute path first. `active_duplicate`/`next_attempt` compare `entry.get("worktree") == worktree` as raw strings, so hashing the raw string keeps `scratch_dir`'s notion of identity consistent with the registry's own existing equality semantics (two differently-spelled-but-equivalent worktree args are already treated as different entries today; matching that, not "fixing" it, is in scope here).
- In `CliBackend.dispatch` (`:1357`): before calling `launch(...)`, reserve the directory via `Path.mkdir(parents=True, exist_ok=False)`. A `FileExistsError` here means a fresh attempt number collided — this is the real #525 race (two dispatches racing `next_attempt()` before either saved its registry entry) made visible: catch it and raise `CrewLaunchError` with a message naming the colliding path and the tuple, never silently continue or overwrite.
- In `CliBackend.resume` (`:1403`): the directory for this entry's stored `(work_id, gate, role, worktree, attempt)` should already exist from the original dispatch — get it (compute the same path), do NOT reserve/raise-on-exists here; a resume re-enters the SAME attempt, not a new one, so an existing directory is expected and correct, not a collision.
- New env var `CREW_SCRATCH_DIR`, set in `_crew_door_env`/`crew_env` (`:890-968`) alongside `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`, CLI backend only (matching `door_bound == True` scope — `ExternalBackend` spawns no process and builds no environment, so it gets nothing, same as it gets no `SPINE_FILE` today).
- Record the scratch path on the registry entry via `build_entry` (`:1028-1126`), same pattern as the existing `spine`/`model` optional fields (recorded when present).

## Allowed Scope
`scripts/run_crew.py`, `tests/test_crew_launcher.py`. `scripts/recover_crews.py` only if genuinely needed (expected: no — it is a pure read-side classifier with no scratch-dir awareness needed for this gate; confirm rather than assume, as g1's implementer did for engine-lease state).

## Specific Exclusions
- No change to `run_log_paths` itself — it has a narrower, pre-existing, out-of-scope asymmetry (it doesn't key on `worktree` even though duplicate-detection does) that was found while scoping this gate but is NOT this gate's job to fix; leave it untouched and do not silently "fix" it as a drive-by.
- Do not attempt to make the dispatched crew's own skill (e.g. `skills/reviewer/SKILL.md`) actually WRITE into `CREW_SCRATCH_DIR` — that is a distinct, unowned-files follow-up (already flagged as a triage candidate). This gate closes the collision-avoidance half only: reserve + expose the directory, detect and raise on a genuine collision.
- Fenced files unchanged from g1's list.

## Constraints
- `decision:no-silent-truncation` — a collision is a raised `CrewLaunchError`, never a silent overwrite, never a quiet reuse of a directory that wasn't this exact attempt's own.
- No reaping, expiry, or force-claim.
- Clear `__pycache__` before every measurement.
- Windows: `Path.mkdir(parents=True, exist_ok=False)` behaves identically cross-platform (stdlib, no POSIX-only call) — no new cross-platform seam risk.

## Map Anchors (inbound)
- **Structural:** `run_crew.py:230-234` `run_log_paths` (naming convention to mirror, NOT to also fix); `:330-377` `active_duplicate`, `:380-390` `next_attempt` (the actual 4-field key tuple this gate must match); `:826-843` `crew_cwd` (shows how worktree is normally handled, for reference only — `scratch_dir` uses the raw string, not this resolution); `:890-968` `crew_env`/`_crew_door_env` (env var goes here); `:1028-1126` `build_entry` (registry field goes here); `:1357` `CliBackend.dispatch` (reserve+raise), `:1403` `CliBackend.resume` (get, no raise).
- **Decision anchors:** `decision:namespace-by-assignment` — reuse the registry's own key tuple verbatim (now confirmed 5-field including worktree and attempt); `decision:no-silent-truncation` — collision raises, never overwrites.
- **Evidence expectations:** two dispatches under distinct tuples (varying gate, role, worktree, OR attempt) get disjoint directories; two dispatches sharing `work_id`/`gate`/`role` but DIFFERENT `worktree` get disjoint directories even at the same attempt number (the specific regression this handoff's Close Criteria calls out); a forced identical-tuple collision raises and never overwrites; the env var is present in the CLI-backend child's env and recorded on the registry entry; resume against an existing directory does not raise.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; `git check-ignore -v scripts/run_crew.py` exits 1.
- **Committed** — `tests/test_crew_launcher.py`; `git check-ignore -v tests/test_crew_launcher.py` exits 1.

## Required Evidence
- New test class(es) covering every Evidence expectation bullet above, by name.
- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py` pasted verbatim.
- A concrete before/after demonstration: two crews whose evidence used to collide (same generic scratch path under the OLD scheme — i.e. before this gate, `run_crew.py` reserved no scratch dir at all) now write to disjoint, reserved, tuple-namespaced paths; plus the error surface (exact `CrewLaunchError` message) when a collision is genuinely forced.

## Wiring Grep
```bash
grep -rn "scratch_dir\|CREW_SCRATCH_DIR" --include=*.py . | grep -v "def scratch_dir" | grep -v "^\./tests/"
```
State the count of real call/reference sites outside the definition and outside the test file.

## Verification Commands
```bash
find . -name __pycache__ -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
```

## Suggested Model Tier
stronger — the worktree-hashing/collision-detection correctness has a real regression risk (the exact bug this handoff's Close Criteria narrates as "an earlier draft made this mistake").

## Authority
The mechanism (5-field key tuple including worktree, raw-string hashing, dispatch-reserves/resume-gets, `CrewLaunchError` on collision, `CREW_SCRATCH_DIR` env var name) is already decided per the plan gate's cold-critic-fixed design. Do not re-derive. If genuinely unworkable, stop and report rather than substitute.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, required evidence cannot be produced, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/cleanup-e-crew-tooling/crew-handoffs/g2-implementer-result.md` before ending your turn (start with `Return status: complete` or the appropriate status).
