# Lane L return — finishing wave 3: three bounded changes the human ruled on

Commander: `constellation/567-l/lane-l/commander-delegated/attempt-1`. Branch
`feat/567-j-launcher-declared-defaults` (lane J's, carrying K's merged bookends). Head
**`25bffaba04080ff41751c224c218084cd9046d28`** at time of writing, plus this archive commit on
top. **PR #637** (lane J's, not a new PR).

---

## 1. Verdict

**All three delivered.** No honest-null; all three baselines matched the launch order exactly as
stated, and all three were genuinely undone before this lane.

---

## 2. The three changes, before/after

### 2.1 Unblock J's merge gate

`tests/test_episode_observations.py::RealStoreTests` failed on `567-j-004.a5`: the statement
opened a comma-clause with the bare verb `run`, which the guard's imperative trigger (scoped to
`workaround`/`proposed-remedy`) reads as an instruction.

**Before:**
> A grep of existing test fixtures (model="...") against the new table's populated role/harness
> keys, run BEFORE authoring the handoff rather than discovered by the implementer at the
> pytest-run stage, would have surfaced the full rewrite set up front.

**After** (via `apply_episode_delta.py`'s `restate-assertion` op — `op, id=567-j-004, assertion=a5,
statement, history`, exactly those five fields; original preserved verbatim in `history`):
> A grep of existing test fixtures (model="...") against the new table's populated role/harness
> keys, **if run** before authoring the handoff rather than discovered by the implementer at the
> pytest-run stage, would have surfaced the full rewrite set up front.

One inserted word (`if`) turns the clause from a subjectless imperative reading into an explicit
conditional; no factual content changed. Verified directly against
`verify_episode_observations.triggers_for("workaround", <new text>)` returning `[]` before
touching the store. `guard.EXCEPTIONS` untouched — still 11 entries, not 12.

### 2.2 The commander tier row

**Before:** `"commander": {"default": "sonnet", "allowed": frozenset({"sonnet", "haiku"})}`
**After:** `"commander": {"default": "sonnet", "allowed": frozenset({"sonnet", "opus"})}`

`git diff scripts/run_crew.py` confirms exactly one line changed. `admiral` stays
`{"default": "opus", "allowed": {"opus"}}`; `implementer`/`reviewer`/`critic`/`cartographer` rows
untouched. No existing test pinned `commander`'s `allowed` set specifically (only `implementer`'s
frozenset type and `codex`/`local` emptiness were pinned) — added
`test_commander_tier_is_sonnet_or_opus_haiku_excluded` to
`tests/test_crew_launcher.py::ResolveModelTests` rather than leave the widened row unpinned.

### 2.3 The role-spine-template bookend lint

New `scripts/check_role_spine_bookends.py`, scoped to `skills/*/templates/*_SPINE.template.json`
only. Two triggers: (a) a template that declares zero `"bookend": true` tasks; (b) a template that
declares bookends whose id set differs from the installed corpus copy (including the installed
copy being entirely absent). Does not touch `checklist_engine.py::_is_bookend()` or its
permissive default — a plan with no declaration still reads as not-a-bookend at runtime.

`check_skill_freshness.py`'s `check()` compares a **project's** own
`.agent-work/templates/{.baseline,local}` against installed `upstream`, driven by a per-project
`TEMPLATES_MANIFEST.json`. It has no notion of "this repo's own skill source vs. the installed
corpus" and this repo (the skill source itself) has no reason to carry that manifest — wrong
shape, so it was not reused; a small standalone script was written instead, per the launch order's
own "say so if it does not fit."

**Red-proof / green-proof** (`tests/test_check_role_spine_bookends.py`, 7 tests, synthetic
fixtures under `tempfile.TemporaryDirectory`):
- `test_undeclared_template_is_a_red_proof` — zero bookends declared -> `status: undeclared`, exit 1.
- `test_declared_and_matching_installed_copy_is_a_green_proof` — declared, installed matches ->
  `status: ok`, exit 0.
- plus drift, installed-missing, unreadable-refuses, empty-corpus, and a real-repo sanity check
  that every actual role spine template declares >=1 bookend.

**Live-repo run against the real installed corpus, unmodified by this lane:**
```
$ python3 scripts/check_role_spine_bookends.py --repo-root . --skills-root ~/.claude/skills
! drift              skills/admiral/templates/ADMIRAL_SPINE.template.json -- repo=['closeout', 'init'] installed=[]
! drift              skills/commander/templates/COMMANDER_SPINE.template.json -- repo=['archive', 'init'] installed=[]
! drift              skills/explorer/templates/EXPLORER_SPINE.template.json -- repo=['init', 'route'] installed=[]
3 role spine template(s) undeclared or drifted from the installed corpus.
exit: 1
```
This is exactly the drift the Admiral found minutes after merging K — the lint the human's "B plus
lint" ruling asked for now catches it mechanically.

---

## 3. Suite tally

Full suite, clean detached worktree of commit `25bffaba` (`git worktree add --detach`), env
`-u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`:

```
3417 passed, 6 skipped, 1222 subtests passed in 141.09s
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 3417 passed, 6 skipped
```

Exactly the one accepted exception per pre-ruling `decision:map-index-is-admiral-owned` — nothing
else. Worktree removed after the run (`git worktree remove --force`).

---

## 4. Touched paths

- `episodes/active/567-j-004.md` — `a5` restated
- `scripts/run_crew.py` — one-line commander tier edit
- `tests/test_crew_launcher.py` — one new pinning test
- `scripts/check_role_spine_bookends.py` — new
- `tests/test_check_role_spine_bookends.py` — new
- `episodes/active/567-l-{001,002,003}.md` — this run's own episodes
- `.agent-work/567-l/**` — spine, execute.json, mission frame, REPLAN_INPUT.json, state note,
  triage candidate, episode deltas

Not touched: `map/INDEX.md` (Admiral-owned, per pre-ruling), `guard.EXCEPTIONS` (no growth),
`checklist_engine.py::_is_bookend()`, `admiral`/`implementer`/`reviewer`/`critic`/`cartographer`
tier rows, `docs/agents/*`.

---

## 5. Triage candidates

One, staged recommend-and-defer at
`.agent-work/567-l/triage-candidates/tc1-self-waive-refused-two-occurrences-this-wave.md`: the
engine door unconditionally refuses a session waiving a check on its own bound spine, even when
the check names itself waivable — hit twice in one wave (lane J, then this lane, both at
`plan.c6`). Recommends a first-class handshake verb, or narrowing the refusal for checks that
already declare themselves conditionally waivable, closing filed defects **#632**
(session-id impersonation) and **#369** (force-claim attribution loss) in the same pass if
practical.

---

## 6. My own mistakes

- Initially characterized `map/INDEX.md` as an "unfilled template" when discharging the DEGRADED
  map-orientation receipt, reasoning only from `map_orient.py`'s own diagnostic wording without
  independently checking the file's actual size/freshness. The Admiral corrected this directly:
  `map/INDEX.md` is a fresh, fully built 31KB scan; the actually-empty piece is `map/ids.jsonl`,
  because anchor-id minting has never been authored in this repo at all. Corrected in the mission
  frame before this return was written; recorded as episode `567-l-002` so the distinction (build
  ran vs. build never ran) doesn't get re-conflated by a future run hitting the same DEGRADED
  verdict.
- Tried to self-waive `plan.c6` before checking whether the engine would allow it, costing one
  refused call and a full cross-session round trip with the Admiral (episode `567-l-001`,
  triage candidate `tc1`) — a prior run on this same epic (lane J) had already hit this, which
  I only learned after asking.
- Bundled all of this lane's changes (three code changes plus the full `.agent-work/567-l/`
  workbench) into a single commit rather than committing as each gate closed, departing from
  "commit frequently as gates close." Not incorrect, but coarser-grained history than the doctrine
  asks for.

---

## Head SHA

Reported above; the Admiral gates on the actual head after this archive commit and push, not on
this file's own claim.
