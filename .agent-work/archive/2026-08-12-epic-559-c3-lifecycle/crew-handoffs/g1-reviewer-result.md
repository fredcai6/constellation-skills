# Review Result

## Assigned Gate
`g1` — open Constellation work in one call (`scripts/spine_lifecycle.py`)

## Verdict
`BLOCK`

## Result
`BLOCK`

## Handoff compliance
`open_work` implements `LIFECYCLE_CONTRACT.md` sections 2–3 in the order specified: validate `work_id`
(reuses `run_crew.validate_work_id`, confirmed by reading the call site — never a second validator);
refuse an occupied worktree path; refuse a `work_id` whose spine carries an active `engine_session`;
`git worktree add`; scaffold via `init_work_area.init_work_area`; compile the spine via `generate_spine`
(imported, never re-implemented — verified this reuses `spec_shape_faults`/`compile_spec`/`probe_spec`
exactly matching `generate_spine.main()`'s steps 2–5; step 1, `tomllib.load`, does not apply because the
caller already hands `open_work` a parsed `spec: dict`); inject `origin` and re-validate; self-verify with
`verify_worktree_isolation.check_distinct_real` in-process; return the crew-binding values. Rollback on
any failure at or after `git worktree add` is scoped to what the call itself created. `close_work` is not
implemented (correct — g2's scope); no MCP door wiring (correct — g3's scope). All required and
confirmatory evidence reproduced independently (see Evidence verdict). Stop conditions were not
triggered by the implementer, correctly (see Blockers for the one I am raising as reviewer).

## Scope drift
None. The committed diff (`63e07251`) touches exactly `scripts/spine_lifecycle.py` (new),
`tests/test_spine_lifecycle.py` (new), `map/INDEX.md` (regenerated) — verified via `git show --stat`.
No `close_work` function exists in the file (grep-confirmed); only the pure `archive_name_for` ships, per
the specific exclusion. `mcp_spine_server.py`, `checklist_engine.py`, `validate_spine.py`,
`generate_spine.py`, `settings.json`, `.mcp.json`, `docs/agents/*`, `skills/**` are all untouched —
verified via `git diff 293b7721..63e07251 -- <those paths>` (empty). Not pushed to `main`; local commits
only on `epic-559/c3-lifecycle`.

## Evidence verdict
All three load-bearing pieces of required evidence reproduced independently, not accepted on the strength
of the report:

1. **Rollback fixtures.** Re-ran `TestOpenWorkRollback` and `TestOpenWorkSelfVerifyForcesRollback`; both
   assert against real `git worktree list --porcelain` / `git branch --list` output, not a string the code
   under test produced. I additionally wrote a standalone script that monkeypatches `sl._rollback` as a spy
   to record whether the worktree/branch existed **at the moment rollback runs** — for both the late
   spec-shape-refusal path and the `check_distinct_real`-says-no path, they did (`worktree_existed_at_rollback_time:
   true`, branch present in `git branch --list` before removal). This closes the handoff's own named
   scepticism: the tests prove **removal**, not merely "never created."
2. **`check_distinct_real` forces rollback despite `git worktree add` exit 0.** Reproduced: `git worktree
   add` genuinely succeeds (worktree exists, `spine.json` not yet written since self-verify runs before the
   write), only the isolation check is faked to return `False`, and the call still rolls back completely.
3. **Origin round-trip through a real engine drive.** `TestOriginRoundTrip::test_origin_survives_claim_start_attest_advance`
   calls `checklist_engine.claim`/`start`/`attest`/`attach`/`advance` **directly on the dict** — this is the
   real engine, not a simulated drive (the handoff's own named scepticism point). Reran standalone: 1
   passed. `origin` is byte-for-byte (dict-equality) unchanged after the drive.

Confirmatory, reproduced exactly: full suite `2852 passed, 3 skipped, 1121 subtests` (baseline `2824` + 28
new); sweep `23`; `git check-ignore` exits `1` for both new files (not ignored).

Mutation checks (handoff: "mutate the code and prove it," reverted after each): disabling the
occupied-worktree-path guard turned `TestOpenWorkOccupiedRefusal::test_violating_refuses_when_worktree_path_exists`
red; disabling the `except: _rollback(...); raise` clause turned all four rollback-dependent tests red. Both
guards restored via `git diff --stat` showing no change afterward.

## Code/doc quality
One **confirmed, blocking** defect (finding 1 below). Otherwise minimal and well-factored: pure helpers
are genuinely pure (verified by source-string checks the tests themselves run, and by direct reading —
no `Path`/`open`/`subprocess`/clock reads inside `worktree_path_for`/`branch_name_for`/`archive_name_for`/`build_origin`);
`_compile_spine`, `_git`, `_rollback`, `_chdir` are sensibly extracted; naming and step-numbered comments
trace cleanly back to `LIFECYCLE_CONTRACT.md`'s own numbered order. Fowler baseline pass (`r6-fowler`,
`.agent-work/epic-559/c3-lifecycle/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0): 10 of 12 smells
absent; 1 flagged (non-blocking — see finding 2); 1 overridden with a logged standard (`build_origin`'s 6
keyword params mirror `LIFECYCLE_CONTRACT.md` §3's frozen `origin` schema 1:1).

## Map impact verdict
- **Evidence supports claimed change:** yes — `map/INDEX.md`'s diff shows `scripts.spine_lifecycle` (13
  entities, 3 holes) and `tests.test_spine_lifecycle` (52 entities, 50 holes), matching the implementer's
  claim exactly (verified via `git show 63e07251 -- map/INDEX.md`). Regeneration is idempotent — re-running
  `python -m scripts.code_map build` produces no further diff.
- **Constraints not violated:** yes, see Scope drift.
- **Notes match the diff:** yes — "new module, no production caller yet, door wiring is g3" matches the
  diff exactly; nothing overstated.
- **Decision candidates surfaced:** yes. `SPINE_SESSION`'s exact derivation
  (`f"constellation/{work_id}"`) is correctly flagged as open — `LIFECYCLE_CONTRACT.md` and the handoff are
  both genuinely silent on the formula, and no close criterion tests the exact value. I agree this is a
  legitimate judgment call for g3/g4 to confirm or revise, not a defect here.
- **Durable context routed:** yes, plus one item the implementer could not have seen: while driving my own
  review survey I incidentally reproduced an out-of-scope engine bug (`episode_capture.manifest_root`
  path-doubling — see Out-of-scope observations). Flagged to triage (`tc1` in my survey), not blocking g1.

## Reconciliation check
No divergence from recorded architecture. New capability, no caller yet, consistent with
`LIFECYCLE_CONTRACT.md` §8's explicit deferral list (door wiring, `close_work`, etc., all out of this
gate's scope by design).

## Blockers

**1. CONFIRMED — `scripts/spine_lifecycle.py:258` writes the compiled spine without `newline="\n"`.**

```python
spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8")
```

Evidence: `docs/agents/CREW_CONTEXT.md` §"Writing Files On Windows" requires `encoding='utf-8',
newline='\n'` explicitly **on every write**, naming exactly one sanctioned exception
(`checklist_engine.py`'s byte-faithful `save()`) that does not cover this file. The established current
convention in this repo's own newer writers — `context_manifest.py:447`, `episode_capture.py:530`,
`map_orient.py:1180`, `file_issue_set.py:214`, `verify_iterative_role_artifacts.py:53`,
`verify_epic_418_demo.py:66` — all pass `newline="\n"`. `context_manifest.py:441`'s own docstring states
why: "without it Python translates every `\n` to `\r\n` on write." `.github/workflows/ci.yml:23` runs this
suite on `windows-latest`, so this is not theoretical.

Consequence if it ships: on Windows CI, every `open_work` call writes a CRLF `spine.json`. No test in
`tests/test_spine_lifecycle.py` or elsewhere asserts the byte content or newline convention of the written
file, so this would not turn CI red — it is a silently-wrong write, the exact class of defect this wave's
review standard exists to catch ("does the mechanism work, and is the value it carries correct" — the
write mechanism works; the bytes it produces on Windows are wrong). It later surfaces as the "spurious
diffs and byte-level comparison failures" `CREW_CONTEXT.md` names as the direct consequence.

Mitigating: one-line fix (`, newline="\n"`); it repeats rather than invents an existing anti-pattern
(`generate_spine.py:910` has the identical omission, pre-existing and out of this gate's scope).

Confirmed, not suspected — I read the exact line, confirmed the sanctioned-exception list excludes it,
and confirmed the CI matrix runs Windows.

## Out-of-scope observations
- **`episode_capture.manifest_root()` (`scripts/episode_capture.py:181-213`) doubles the work-id path
  segment** when a checklist lives in a subdirectory of its own work-id dir that does not itself end in the
  work-id — e.g. exactly `.agent-work/<work-id>/<gate>-review/review.json`, the path shape this reviewer
  skill's own convention recommends. Reproduced live this session: claiming/starting `r0-context` on my own
  `review.json` at `g1-review/review.json` wrote
  `.agent-work/epic-559/c3-lifecycle/epic-559/c3-lifecycle/{context,mechanical}/r0-context.json` instead of
  `.agent-work/epic-559/c3-lifecycle/{context,mechanical}/r0-context.json`. The function's own docstring
  documents the limitation ("those keep the historical parent-of-base_dir answer exactly") but does not
  flag that this is exactly the shape a reviewer survey produces. Out of scope for g1 — `episode_capture.py`
  is untouched by this gate's diff. Flagged as `tc1` in my survey; the stray nested directory is left in
  place (untracked, engine-written provenance — not mine to delete).
- **Minor, non-blocking (Fowler pass): `_rollback()` (`spine_lifecycle.py:146-153`) repeats
  `subprocess.run(["git", ...], cwd=str(root), capture_output=True, text=True)` three times inline** rather
  than reusing `_git()` or a small best-effort sibling. Worth a follow-up refactor, not worth reworking g1
  over.

## Workflow Feedback

- **Handoff gaps:** none of substance. One small friction: `crew-runs.json` records `"spine": null` for my
  own crew entry, which is how I confirmed nothing was bound as my own checklist and I should build a
  `REVIEW_SURVEY.json` per the skill rather than drive the door (which stays bound to the Commander's own
  `execute.json`, inherited ambiently into my process). That inference took a few tool calls to establish
  confidently; naming "no --spine was passed, so build your own survey" explicitly in the handoff (mirroring
  what the implementer's own Workflow Feedback already reported for the same disambiguation) would save the
  next reviewer the same detour.
- **Context rediscovered:** the same disambiguation the implementer already reported — the inherited
  `SPINE_FILE`/`SPINE_SESSION` point at the Commander's `execute.json`, not a dedicated g1 checklist,
  because per-gate MCP door binding is g3's own deliverable (this epic's own subject).
- **Instructions improvised around:** building my own `REVIEW_SURVEY.json` at
  `.agent-work/epic-559/c3-lifecycle/g1-review/review.json` (the skill's stated convention) triggered the
  `episode_capture.manifest_root` path-doubling bug described above as a side effect of the engine's own
  `start` verb — an artifact of the survey location, not of my review actions. I left it in place rather
  than deleting engine-written files by hand, and flagged it to triage instead.
- **What would have made this easier:** the reviewer handoff could state up front (as this run's implementer
  handoff apparently did not either, per their own Workflow Feedback) whether a dedicated survey spine is
  bound via `--spine`, so a reviewer does not have to infer it from `crew-runs.json`.

## The single most likely way this gate produces a green run that is wrong

**A reviewer trusts that "suite green + sweep 23 + rollback tests pass" means the write path is correct,
without checking the write call itself against the project's own documented Windows-write rule** — because
every test in this suite runs on Linux (or in a Linux-hosted review), the missing `newline="\n"` produces
zero observable signal locally. The only way to see it is to read `docs/agents/CREW_CONTEXT.md`'s specific
rule and then grep the new file's one write call against it — a check that is easy to skip because it is
not named in any close criterion and does not fail any command. This is the "invisible because absent"
shape the review standard warns about: nothing is wrong-looking in the diff; a keyword argument is simply
not there.

## Return status
`complete`
