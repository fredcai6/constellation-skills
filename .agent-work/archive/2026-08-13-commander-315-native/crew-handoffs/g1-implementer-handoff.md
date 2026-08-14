# Implementer Handoff

## Gate
`g1-implement` of `.agent-work/commander-315-native/execute.json` (work-id `commander-315-native`).

Worktree: `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`, branch `epic-568/c2-native-isolation`. Work only here. **Never enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`** (another Commander's tree) and never write the main checkout `/home/tommy/projects/constellation-skills`.

## Task

Make a spine carry its own repo reference from creation, and have `checklist_engine.py` enforce worktree isolation **natively** against it. Then delete the template command check this supersedes, along with the coverage apparatus that exists only to assert that check's wiring.

Four parts, **one commit, one gate** — they are not separable:

1. **Write side.** `scripts/init_work_area.py` — `instantiate_spine` stamps a top-level `origin` block when it writes a spine.
2. **Read side.** `scripts/checklist_engine.py` — a pure refusal-or-`None` function comparing the spine's `origin.worktree` against the engine's **own** `Path.cwd()`, called from **one** site in `main()`.
3. **Deletion.** `skills/commander/templates/COMMANDER_SPINE.template.json` `init` **precondition `c0`**, plus `scripts/verify_worktree_precondition_coverage.py` and its three enumeration tests.
4. **Docs.** `docs/CHECKLIST_SCHEMA.md` documents `origin` as a top-level key.

## Protected Intent

An agent must not drive a spine's state from a tree that is not the spine's own. Today that is enforced by a command check inside one template — so it covers only the templates someone remembered to wire, and a spine's own text can switch it off. After this change the engine enforces it for every spine on every guarded verb, and the expected value comes from the spine's creation-time stamp rather than from a string a spine author can edit.

**What this change delivers — claim exactly these three, nothing more:**

1. **Coverage** — enforcement applies to every verb on every spine, not only where a check was wired into a template.
2. **Unbypassability from the spine** — a spine's own text can no longer switch the check off, because the check is no longer in the spine.
3. **An independent expected side** — the expected value comes from `origin.worktree`, stamped at creation, not from a literal inside a check.

**Explicitly NOT delivered — do not write this anywhere, in code comments, docstrings, tests, or your result:** that the guard "cannot be lied to", is "non-forwardable", or is immune to a child process's cwd. It is not. `_run_check_command` passes no `cwd=`, so `--here` already reads the engine's ambient cwd and the native comparison reads that same value one indirection earlier. A check authored as `cd <origin.worktree> && ...` still satisfies it. The Admiral withdrew this claim on 2026-08-13; restating it is a gate failure.

## Test Mode

**TDD required for the read side and the new coverage.** Every new check must be demonstrated **failing in the defective world and passing in the healthy one**. A guard proven only on its pass side is the defect class this repo names "a check that cannot fail" — and is the exact defect this whole issue exists to remove.

## Close Criteria

- `instantiate_spine` stamps `origin` and the spine it writes still parses.
- `origin_worktree_refusal` exists, is pure, and is called from exactly one site in `main()`.
- The refusal fires from a foreign cwd and **writes nothing** to the spine.
- Containment holds: worktree root passes, a subdirectory of it passes, a sibling sharing a name prefix does not.
- Every origin-less/malformed-origin shape falls back to today's behaviour and none raises.
- `tests/test_spine_origin_isolation.py` exists and covers **both** the match and the mismatch case against a spine that **actually carries `origin`**.
- `init.c0`, `scripts/verify_worktree_precondition_coverage.py`, and its three enumeration tests are gone.
- `docs/CHECKLIST_SCHEMA.md` documents `origin`.
- Full suite green except the pre-authorized reconciliation named below.

## Allowed Scope

- `scripts/init_work_area.py`
- `scripts/checklist_engine.py`
- `skills/commander/templates/COMMANDER_SPINE.template.json` (delete `init` precondition `c0` only)
- `scripts/verify_worktree_precondition_coverage.py` (delete the file)
- `tests/test_worktree_precondition_wiring.py` (delete **only** the three enumeration tests that exercise the deleted coverage script; see "The deletion" below)
- `tests/test_spine_origin_isolation.py` (**new file**)
- `tests/test_explorer_templates.py` (pre-authorized reconciliation, see below)
- `docs/CHECKLIST_SCHEMA.md`
- `map/INDEX.md` — remove the `scripts.verify_worktree_precondition_coverage` line and its packet directory `map/scripts.verify_worktree_precondition_coverage/` if a map-consistency test requires it. If no test requires it, leave the map alone and report it as map impact instead.

## Specific Exclusions

- **`scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` — do NOT edit.** If the change wants either, **STOP and return**. That is a float to the Admiral, not your decision.
- **`scripts/spine_lifecycle.py` — ZERO changes.** `build_origin()` and `open_work()` are already correct. Your stamp must be key-compatible with `build_origin`'s block (a strict subset of its keys).
- **Do not weaken any surviving assertion in `tests/test_worktree_precondition_wiring.py`.**
- Do not route through `open_work()`; do not treat the `spine_open` door as a prerequisite.
- Do not touch `base_dir` in `checklist_engine.py`.

## Constraints

### Shape

A pure function, matching the repo's existing refusal-or-`None` precedent `spine_lifecycle.closeout_refusal`:

```python
def origin_worktree_refusal(spine: dict, *, cwd: str, verb: str) -> str | None:
```

No filesystem, no clock, no subprocess, no `Path.cwd()` inside it. The impure caller lives in `main()`, immediately after `cl = load(path)` (line 3269) and **before** `dispatch(...)`, and passes `cwd=str(Path.cwd().resolve())`.

### Refuse without persisting

`main()` calls `save(path, cl)` on the `EngineError` path for every verb except `current` (lines ~3320-3337). A refusal raised **inside** `dispatch()` would therefore write into the very tree the guard protects, and would clobber a concurrent legitimate writer holding a spine loaded before the refusal. **The guard must print its refusal to stderr and return non-zero without calling `save()`.** Do not raise `EngineError` for it.

Match the existing refusal presentation: `REFUSED: <reason>` on stderr, prefixed by the check-failure rail the way the `EngineError` path does, and return `1`.

### Engine-native, never a forwarded cwd

The engine reads its **own** `Path.cwd()`. It must **not** pass `cwd=` to a subprocess check. Forwarding the stored root into `verify_worktree_isolation.py --here` makes the comparison `X == X`, because `origin.worktree` and the EXPECTED value in the check text both derive from the same resolved root at creation. This is the falsified fix; do not revive it.

### The resolved root is not `base_dir`

Carry it in a name distinct from `base_dir`. `base_dir` is also the gauge path base and the `--from-child` base. Overloading it breaks both.

### Verb scope

```
guarded = MUTATING_VERBS | {"claim", "heartbeat"}
exempt  = {"current", "release"}
```

`current` is the only genuinely read-only verb, and inherited doctrine has an invoker read a subordinate's `current` cross-tree to see a `REFRESH REQUESTED` line. `release` is exempt deliberately as the single recovery escape hatch — a lease on a spine whose worktree was removed at closeout must stay clearable, and a non-owner `release` already demands `--force --reason` on the record. `heartbeat` is guarded because it **writes**.

**Assert the guarded set as data in a test — both membership and non-membership.** Derive it from `MUTATING_VERBS` so a future verb added to that set is guarded automatically.

### Containment, not equality

The refusal fires when cwd is **neither the stored root nor inside it**. Equality would refuse from `<root>/scripts` or `<root>/.agent-work/<id>`, which the check being superseded accepts — `verify_worktree_isolation` compares `git rev-parse --show-toplevel`, which succeeds from any subdirectory.

Use `Path.is_relative_to` (already segment-wise) so a sibling sharing a prefix — `/w/repo-2` against `/w/repo` — is **not** inside. **Pin that sibling case with a test.**

### Normalize both producers

`spine_lifecycle.py:311` stores `str(Path(worktree))` — unresolved, native separators. `init_work_area` stamps `Path(root).resolve().as_posix()`. On Windows those are `C:\a\b` and `C:/a/b` for the same directory. Fold case and separators with `os.path.normcase` inside the pure function. Leave symlink resolution **outside** it (stored side resolved at write time, cwd side at read time) so the function stays pure.

Any case-folding assertion must be `skipUnless(os.name == "nt")` rather than pretending it proves something on Linux.

### Exhaustive fallback

All of these take today's behaviour and must **never raise**:

`origin` absent · `origin: null` · `origin` not a dict (a **string** or a **list** — `.get` raises `AttributeError`, which `main()` does not catch) · `origin: {}` · `worktree` absent · `worktree` empty string · `worktree` not a string.

`scripts/validate_spine.py` guards none of them — probed and confirmed — so the engine handles every shape itself. **One test per shape**, table-driven.

### Never guess a field

`init_work_area.py` does not know branch, base, parent, or the dispatching session. Omit them rather than emitting a plausible wrong value. Stamp **exactly**:

```json
{"work_id": "<work-id>", "worktree": "<Path(root).resolve().as_posix()>", "opened_by": "init_work_area"}
```

`resolve_spine` (line ~148) already computes `Path(root).resolve().as_posix()` and discards it; `instantiate_spine` (line ~170) already parses the resolved spine with `json.loads` as a validity guard and discards the dict. Both values are in hand at the moment of writing — reuse them, do not recompute.

**Preserve an existing `origin` rather than overwriting it** (`setdefault` posture), in case a future template ever carries the block.

The stamp must be written into the parsed dict and re-serialized, or inserted such that `_assert_no_resolver_placeholders` still runs against the resolved text. Keep the existing validity guards effective — do not move the stamp after them in a way that lets a broken spine through.

## The in-process cross-tree caller — Commander decision, follow it

`scripts/mcp_spine_server.py:361` calls `checklist_engine.main(argv)` **in-process** and never `chdir`s, so the guard reads the **MCP server process's** cwd, not the spine's. (`scripts/hooks/spine_rail.py` never subprocesses the engine — its docstring forbids it and its only subprocess is `git worktree list`; `gauge_writer_hook.py` never calls the engine. This is the only real cross-tree caller.)

**Decision: the guard applies to this caller with no exemption, no env override, and no bypass.** Reasons:

1. In the normal crew flow the door's process inherits the dispatcher's cwd, which is the worktree the spine lives in, so the guard passes.
2. When the server's cwd differs from the spine's `origin.worktree`, the door genuinely **is** driving a spine cross-tree. Refusing is the intended semantic, not a regression.
3. `current` is exempt, so `spine_status` keeps working cross-tree — the read path the door is most used for is unaffected.
4. An env-var escape hatch would be an off switch outside the spine, recreating the defect one level over.

**Required:** a test in `tests/test_spine_origin_isolation.py` that reproduces the MCP shape exactly — `os.chdir` to a foreign directory, then call `checklist_engine.main([...])` **in-process** (not via subprocess) against a spine carrying `origin` — and asserts a guarded verb returns non-zero and leaves the spine byte-identical, while `current` returns 0. Restore cwd in a `finally`.

## Known-in-advance breakage — pre-authorized

`tests/test_explorer_templates.py:342-360` **will** go red once the stamp lands: it instantiates a spine into a tmpdir and then runs the engine with **no `cwd=`**, so the engine's cwd is the test runner's, not the tmpdir. Reconciling it is pre-authorized.

Reconcile it **by making the test honest**, not by weakening the guard: either run the engine with `cwd=` set to the instantiated root, or assert the refusal is the expected outcome — whichever matches what that test is actually about. Say in your result which you chose and why.

Any failure **outside** this root cause is a stop condition.

## The deletion

`skills/commander/templates/COMMANDER_SPINE.template.json`, task `init`, **`preconditions`** (not postconditions — `init` has postconditions `c1`/`c2` and no `c0`):

```json
{"id": "c0",
 "statement": "this Commander is operating in the worktree it was provisioned into, ...",
 "check": {"kind": "command", "command": "python scripts/verify_worktree_isolation.py --here <repo-root>"}}
```

Delete that precondition entirely, leaving `preconditions` as `[]`.

Deleting the check **alone** takes `scripts/verify_worktree_precondition_coverage.py` and the enumeration tests from `7 passed` to `3 failed, 4 passed`, because that script asserts exactly the wiring being removed. So retire the script and those three tests with it. **Admiral ruling 2026-08-13: this four-file structural change is AUTHORIZED. Do not float it.** Once enforcement is engine-native, *per-template coverage of a command check* is the wrong question.

`tests/test_worktree_precondition_wiring.py` references the coverage script at lines 8, 33, 132. Delete the three tests that exercise it and the `COVERAGE_SCRIPT` constant and imports they alone use. **Keep every other test in that file, unweakened.** Run the file and report which tests survive and which you removed, by name.

## Do not lean on the merged tripwire

`tests/test_worktree_precondition_wiring.py` is the merged guard from the prior wave. **Every fixture in it builds an `origin`-less spine by hand**, so it is green **by construction** under this change and is structurally blind to the stamped path. It is evidence for the **fallback branch only**. Keep it green, but do not cite its greenness as proof the new behaviour works. That is why `tests/test_spine_origin_isolation.py` is a required deliverable and not an optional extra.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`, `scripts/init_work_area.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`, `tests/test_spine_origin_isolation.py` (new — untracked until staged, so it shows in `git status`, not `git diff`), `tests/test_worktree_precondition_wiring.py`, `tests/test_explorer_templates.py`, `docs/CHECKLIST_SCHEMA.md`. Deletions: `scripts/verify_worktree_precondition_coverage.py`.
- **Local-only** — `.agent-work/commander-315-native/crew-handoffs/g1-implementer-result.md` (under `.agent-work/`, intentionally not in the diff).

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The arm.** For each half, revert it and show the new tests go **red**, then restore and show **green**. Paste both runs. Specifically: (a) remove the stamp from `init_work_area.py` → the origin-carrying tests must fail; (b) remove the `main()` call site → the mismatch tests must fail. A test that passes in both worlds is not a test.
2. **No write on the refusal path.** Hash the spine file before and after a refused guarded verb and show the hashes are equal. Do not judge this on the refusal prose.
3. **The full suite:** `python -m pytest tests/ -q -p no:randomly`. Report the failure distribution mechanically: `python -m pytest tests/ -q -p no:randomly 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`. `main`'s Linux baseline is **2934 passed, 5 skipped, 0 failed** — state your numbers against it.
4. **The in-process MCP shape** refuses a guarded verb and permits `current`.

**Confirmatory — a spot-check suffices:** the docs edit; the map line; the surviving-test roster in the wiring file.

## Wiring Grep

```bash
grep -rn "origin_worktree_refusal" --include=*.py . | grep -v "def origin_worktree_refusal" | grep -v "\.agent-work/archive"
```

State the count of call sites found. **Zero external call sites is a stop condition**, not a note — the read side must be reached from `main()`, or the change is shipped-inert and reports green while doing nothing.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/test_spine_origin_isolation.py -q -p no:randomly
python -m pytest tests/test_worktree_precondition_wiring.py -q -p no:randomly
python -m pytest tests/ -q -p no:randomly
python .agent-work/commander-315-native/repro_native.py
python -c "import sys,os,json; d=json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json')); pre=d['tasks']['init'].get('preconditions') or []; sys.exit(0 if not [c for c in pre if c['id']=='c0'] and not os.path.exists('scripts/verify_worktree_precondition_coverage.py') else 1)"
```

`repro_native.py` is the Commander's before/after repro and is **not yours to edit**. If it fails, report the output — do not adjust it to pass.

## Map Anchors (inbound)

The repo cannot orient itself — `map_orient.py` returns `DEGRADED-UNPARSEABLE`, anchor count 0. **Use file paths, not map anchors.** Decision anchors that govern you, carried from the frozen launch order:

- `decision:engine-native-not-forwarded-cwd` — `@grade: settled/measured · leans implementation`
- `decision:both-halves-one-change` — `@grade: settled/human · leans implementation`
- `decision:delete-not-repair-init-c0` — `@grade: settled/measured · leans implementation`
- `decision:root-distinct-from-base-dir` — `@grade: settled/measured · leans implementation`

None of these are yours to unsettle. If implementation reality contradicts one, **stop and return** — that is a float.

## Suggested Model Tier

**Stronger (Opus).** Engine-core work on a 3352-line module with a demonstrated trap that a careless cut walks straight into.

## Authority

Already decided, not yours to revisit: the engine-native direction; the four-file deletion; the verb scope; containment over equality; the `main()` placement; the no-bypass ruling on the MCP in-process caller; and that non-forwardability is **not** claimed.

Yours: the internal shape of the pure function and its tests, the `test_explorer_templates.py` reconciliation, and the wording of the refusal message.

## Stop Conditions

Stop and return if: the change wants `spine_rail.py` or `agent_work_root.py`; `spine_lifecycle.py` needs a change; a failure appears outside the `test_explorer_templates.py` root cause; the wiring grep finds zero external call sites; or a decision outside the authority above is needed.

**Honest null is a complete deliverable.** If the native comparison proves wrong on evidence — for instance if guarded verbs are legitimately run from elsewhere in a real workflow and refusing them breaks it — report that with the measurement rather than forcing it. State what you tested **and what you did not**.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff made the work harder than it needed to be).

`Return status` must be one of `complete | partial | blocked | out-of-scope | failed`, **lowercase** — the Commander copies it verbatim into the gate's evidence and the postcondition matches on exact case.

**Delivery:** write the full result to `.agent-work/commander-315-native/crew-handoffs/g1-implementer-result.md` before ending your turn. That write is the delivery.
