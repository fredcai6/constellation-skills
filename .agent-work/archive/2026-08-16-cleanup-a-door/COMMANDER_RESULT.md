# COMMANDER_RESULT — lane A, `cleanup/a-door` (#604, #605, #603)

**Verdict: SHIPPED.** One float outstanding, which blocks nothing that shipped.

Session `constellation/cleanup-a-door/execute/commander/attempt-1`, parent `admiral-568-cleanup`.
Base `a69bbac4` → published head `2a1b6c8a` (last code commit `5a626351`).
**PR #614**, FINAL, OPEN. Parked at `archive`; **not merged** — publication is the Admiral's.
Spine terminal: `DONE: no open items. WAIVED: ['plan.c6']`. Lease released as the final journaled action.

---

## 1. Evidence per defect

### #604 — the door dies on its own call log

| | probe result | exit |
|---|---|---|
| pre-fix `a69bbac4` | server never answered; traceback through `_log(rec)` at `:461` | **1** |
| post-fix | answered with the engine's own `FileNotFoundError` truth; drop reported on stderr | **0** |

Same probe, same missing-directory target, both run by me. `tests/test_mcp_door_telemetry.py`
fails **5/7** against a reverted server; the reviewer additionally mutation-tested the guards
three ways (collapse the two guards → 2 fail; reroute the report to stdout → 2 fail; make
`_log` a no-op → 4 fail).

### #603 — unbound door refuses, `spine_open` binds, a real verb succeeds

Reproduced by me in **one process**, `SPINE_FILE` genuinely unset:

```
1) spine_status while UNBOUND    isError=True
   REFUSED: no spine is bound to this door... Call `spine_open` to mint a spine and bind
   this process to it, or relaunch this door with SPINE_FILE set to an existing spine file.
2) spine_open                    isError=False
   {"SPINE_FILE": ".../verify-exit-criterion/.agent-work/.../spine.json",
    "SPINE_SESSION": "constellation/verify-exit-criterion", ...}
3) spine_lease claim (MUTATING)  isError=False
   claimed lease constellation/verify-exit-criterion -> active
4) spine_status                  isError=False
   LEASE active: constellation/verify-exit-criterion ... DONE: no open items.
EXIT 0
```

**Step 3 is the load-bearing one** — `run_engine` omits `--session-id` when `SESSION` is
empty and `checklist_engine.py:1073` refuses `claim` without one, so a transcript stopping at
`spine_status` would not have demonstrated binding. No CLI touched. Throwaway worktree removed.

`tests/test_mcp_door_unbound.py` fails **12/12** against a reverted server. Empty-string
`SPINE_FILE` — the case `${SPINE_FILE:-}` actually produces — returns the same refusal
(pre-fix it was `IsADirectoryError`, exit 0).

**The fenced guard is intact.** `_identity_violation` compares against `SPINE` at *call* time,
so it survives a rebind by construction; 5 tests prove it still refuses a foreign spine after
one. `git diff a69bbac4..HEAD -- tests/test_mcp_lifecycle.py | grep '^-'` → **zero removed
lines**: `:194` and its positive control are byte-identical, and a **strictly stronger**
module-wide AST pin was *added* beside it (assignments to `SPINE`/`SESSION` are exactly
{module scope, one named binder}), with its own mutated positive control. A rebind is refused
while the process holds an active lease.

### #605 — the demo spine driven from a directory it was not generated in

Driven by me from `cwd=/tmp` (`g1 -> in-progress`, command check passed, `g1 -> complete`) and
by the reviewer from `$HOME` with `SPINE_DEMO_WORKSPACE` unset. Zero machine-specific paths
under `examples/` (count 0, by command). Guards fail **3/7** on the pre-fix spine, including
the regenerate-and-compare drift test.

---

## 2. Suite and baseline

| | result |
|---|---|
| **Published head**, clean-env, cache-cleared | **3093 passed, 6 skipped, 1153 subtests, 0 failed** |
| **`main` baseline, re-measured at gate time** (`e36e630b`) | **3103 passed, 7 skipped, 0 failed** |

**Failure-set difference: empty on both sides.** `main` carries more tests because lanes B and
C merged during this run; this branch is behind `main` and will need a merge.

Command: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`, `__pycache__`
cleared before every measurement.

---

## 3. Map impact

`map/INDEX.md` **changed and was rebuilt** (`py -m scripts.code_map build --root .`), twice —
the second time because the first rebuild ran while the new test file was still untracked, and
`code_map` enumerates via `git ls-files`. Freshness is green at the published head.

`map/ids.jsonl` is tracked but **empty (0 bytes)**, so `map_orient.py` resolves no anchor for
any area and orientation came back `DEGRADED-UNPARSEABLE`. Discharged with four hash-pinned
substitutes plus an escalation; `plan.c6` (`verify-frame`) taken as a **recorded waiver**,
since no frame can pass in this repo. Not lane A's to fix.

---

## 4. Triage candidates

**16, all `recommend-and-defer`, none implemented**, in `notes-a.md` §"Triage candidates".
The load-bearing one is not a bug: **the door's binding rule is restated in ~7 places**, and
three of this run's four review BLOCKs were one of those restatements going stale — the final
review then found that correcting one introduced the next imprecision. One source of truth,
not a better sweep.

Two candidates a crew raised were **dropped rather than forwarded**, because the reviewer
refuted them by measurement.

---

## 5. Workflow feedback — staged, and named explicitly

```
.agent-work/staged-feedback/cleanup-a-door/CONSTELLATION_FEEDBACK.md
.agent-work/staged-feedback/cleanup-a-door/FENCE.md
```

Named here rather than trusted to the sweep, because the launch order says the harvest has
failed before. The gate was **not waived**: the durable-root export is denied by the archive
gate's own `git-change-policy` `deny_globs`, so the export is staged complete beside a
`FENCE.md` citing this order. The run's 5 episodes are unaffected —
`episodes/active/cleanup-a-door-00{1..5}.md`, tracked and committed.

---

## 6. Worktree isolation

Run **before** any git operation, per the order's ordering warning:

```
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
EXIT=0
```

Re-run at closeout: same result, exit 0.

---

## For the Admiral — please rule / act

1. **FLOAT (unresolved): the "door-detection change" is undefined.** File Ownership grants
   `scripts/install_constellation.py` and `skills/commander/templates/COMMANDER_SPINE.template.json`
   "for the door-detection change only, which lands last" — but Mission names only three
   defects, none of them touches either file; #603/#604/#605 never mention either file; and a
   grep across `scripts/ skills/ docs/` returns one hit, a false positive. **There is no
   door-detection concept in this repo to change.** I did not invent it: the plausible reading
   (teach the commander spine to detect an unbound door and fall back) collides with a
   must-float item — "any change that makes an agent-facing skill teach the CLI as a default".
   Both files are untouched. **Nothing that shipped depends on this**; the installer never
   seeded the demo default (`rewrite_mcp_config_interpreter` rewrites `command`, never `env`).

2. **MERGE-ORDER HAZARD: three fenced files carry claims this change falsified.** All still
   assert `mcp_spine_server` raises `KeyError` without `SPINE_FILE`/`SPINE_ENGINE`, or reads
   `SPINE_FILE` at module scope — both false since #603:
   `scripts/run_crew.py:468-471`, `scripts/hooks/spine_rail.py:1081`,
   `tests/test_spine_rail.py:2698`. Lanes B/C own them; a lane cannot fix what it cannot
   touch, and the order does not say who sweeps them.

3. **Ownership gap:** `skills/workbench/references/checklist-engine.md` still described the
   old binding. It is outside the order's enumerated ownership list though not fenced; I
   corrected it under `reconcile`'s explicit mandate and flag it here rather than doing it
   quietly.

4. **Two declared departures from the order**, both measured, per "overridable if evidence
   contradicts it": gate order reversed (#605 before #603), so the shipped default never
   points at a broken file at any commit; and #605's own "relative paths" fix direction
   overridden, because `checklist_engine.py:883` runs command checks with no `cwd`.

5. **Two corrections to the order**, neither blocking: this repo **does** have a
   `docs/agents/` overlay (all three files tracked and read); and the order's `main` baseline
   of 3057 measured 3058 at the same commit.

## Run shape

3 crew gates · 1 cold plan critic · 9 crew dispatches · **3 reworks on g3 (cap 3), 4 reviews on g3**.
Every g3 BLOCK was **documentation truth, never behaviour** — the functional change was correct
and green from its first attempt.
