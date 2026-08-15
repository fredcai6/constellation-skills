# Launch Order: `commander-315-native — engine-native isolation against a stored spine origin`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

Commanders start cold. Paste, don't point.

## Mission

Make a spine carry its own repo reference from creation, and have the engine **enforce worktree isolation natively against it** — rather than delegating that judgment to a subprocess it would have to mislead.

Three parts, one change:

1. **`init_work_area.py`** — stamp an `origin` block carrying `worktree` when instantiating a spine. Line 148 already computes `Path(root).resolve().as_posix()` and discards it; line ~170 already parses the spine as a validity guard and discards the dict. Both are in hand at the moment of writing. (~8 lines, prior estimate.)
2. **`checklist_engine.py`** — read `origin.worktree`, compare it against the engine's **own `Path.cwd()`** at verb entry, and fall back to inherited cwd when a spine carries no `origin`. (~32 lines across ~3 sites, prior estimate.)
3. **`COMMANDER_SPINE`'s `init.c0` command check** — **delete** it, together with the coverage apparatus that exists to assert its wiring. **Admiral ruling, 2026-08-13:** deleting the check alone takes `verify_worktree_precondition_coverage.py` and three enumeration tests from 7 passed to `3 failed, 4 passed`, because that script asserts exactly the wiring being removed. Retire the script and those three tests with it — once enforcement is engine-native, *per-template coverage of a command check* is the wrong question. This is a four-file structural change and it is **authorized**; you do not need to float it again.

4. **A new test that actually covers the stamped path.** See the amended tripwire note below — the merged guard cannot see your change.

`scripts/spine_lifecycle.py` needs **zero** changes. `build_origin()` and `open_work()` are already correct.

**How it serves the epic intent.** Epic 568's thesis is that engine state carries who it belongs to. This is the same defect one layer over: state that does not know *where it lives*. It is the substrate the rest of the tranche reads from.

## Prior-Wave Verdicts (pasted)

**This supersedes a falsified target. Read this before you touch anything.**

The previous Commander was launched to thread `cwd=` into `_run_check_command`. That is **falsified and must not be revived**:

> `scripts/verify_worktree_isolation.py:100-123` — `_git()` calls `subprocess.run(["git", *args])` with **no `cwd=`**, so `current_toplevel()` measures the **ambient cwd as the check's subject**, not as a path base. Forcing `cwd=<repo-root>` makes the comparison `X == X` and turns `COMMANDER_SPINE`'s `init.c0` into a tautology. The naive fix removes one check-that-cannot-fail by creating another.

**The obvious version of YOUR mission is the same trap.** Storing the root and passing it to the check as `cwd` reproduces the defect byte for byte. Demonstrated live, not argued:

```
origin.worktree stored in the spine : /tmp/tmp.8uTC5OULCX/wt
EXPECTED inside the check text      : /tmp/tmp.8uTC5OULCX/wt
IDENTICAL? True

cwd = launcher's own (today)        : REFUSED  (gate works)
cwd = origin.worktree (direction D) : PASS     (gate disarmed)
```

Both values derive from the same resolved root at creation. **This is why the comparison must be engine-native.**

### AMENDED 2026-08-13 — the Admiral overclaimed; read this instead

The first version of this order said the native comparison "cannot be lied to by a child process's cwd." **That is false, and the previous Commander falsified it.** `_run_check_command` passes no `cwd=` at all, so `--here` already reads the engine's own ambient cwd; the native comparison reads that same value one indirection earlier. A check authored as `cd <origin.worktree> && ...` still satisfies it while the real work happens elsewhere.

**What the change actually delivers — certify these, not non-forwardability:**

1. **Coverage** — enforcement applies to every verb on every spine, instead of only where someone remembered to wire a check into a template.
2. **Unbypassability from the spine** — a spine's own text can no longer switch the check off, because the check is no longer in the spine.
3. **An independent expected side** — the comparison's expected value comes from `origin.worktree`, stamped at creation, rather than from a string inside the check that a spine author can edit.

A reviewer working from the original frame would have certified a property this change does not have. Do not restate the old claim anywhere in your return or PR body.

Measured numbers from the prior wave, all re-verified by the Admiral:

- **17 of 22** command checks in `skills/*/templates` are cwd-dependent (6 literal-relative, 11 cwd-defaulting). The issue's filed "five" is wrong. **None of the 17 need editing** — all are repo-root-relative and the stored root *is* that root.
- "394 checks already immune" **counted archived run scrap**: 1649 of 1733 tracked command checks sit under `.agent-work/archive/` and will never run again. The live template corpus is **64 checks, zero immune**. Do not carry the immunity number forward.
- **108 spines carry no `origin`** on the prior branch, 107 on main (the branch added one — pin the number to the tree). **106 are archived dead runs; the live backfill population is 2.**

## Pre-Rulings

- `decision:engine-native-not-forwarded-cwd` — the engine compares its **own** `Path.cwd()` to `origin.worktree`. It does **not** forward a cwd to a subprocess check. Reviving the forwarded-cwd shape is the falsified fix.
  `@grade: settled/measured · leans implementation`
- `decision:both-halves-one-change` — the write side (stamp) and read side (native check) land **together**. The engine must fall back to inherited cwd for `origin`-less spines, so the read side alone is **inert** — a change that reports green while doing nothing. Cutting them apart is a no-go, not a preference.
  `@grade: settled/human · leans implementation`
- `decision:delete-not-repair-init-c0` — `init.c0`'s command check is deleted, not repaired.
  `@grade: settled/measured · leans implementation`
- `decision:door-not-a-prerequisite` — do **not** route through `open_work()` and do not treat the dead `spine_open` door as a blocker. `open_work` requires a compiled spec and only 2 exist against 12 role templates; `init_work_area.py` reaches all 12 without a door or a spec.
  `@grade: settled/measured · leans scope`
- `decision:root-distinct-from-base-dir` — inside `checklist_engine.py`, the resolved root must be a parameter **distinct from `base_dir`**. `base_dir` is also the gauge path and the `--from-child` base; overloading it will break those.
  `@grade: settled/measured · leans implementation`
- `decision:backfill-is-two` — the live backfill population is 2 spines. Either backfill them or leave them to the fallback; both are defensible at n=2. State which you chose.
  `@grade: guess · leans implementation · settle: decide during implementation and say why`

## Honest-Null Clause

A measured negative is a **complete, successful deliverable**. If the native comparison proves wrong — for instance if read-only verbs are legitimately run from elsewhere and refusing them breaks real workflows — report that with the measurement rather than forcing the change. Scoped nulls: state what you tested **and what you did not**.

## Inherited Latitude

**You may exercise:** how the root is threaded inside `checklist_engine.py`; where the native comparison sits; whether it applies to every verb or only mutating verbs; whether the 2 live spines are backfilled; issue filing; bounded fix-now triage **outside** the engine-core files.

**You must float to the Admiral:** architecture or structural change; scope change; **any edit to `scripts/hooks/spine_rail.py` or `scripts/agent_work_root.py`**; production defaults or user-visible behavior; anything out-of-taxonomy.

The Admiral is reachable and answers context queries in place. Asking up is always sanctioned.

## File Ownership

Your working-notes file: **`notes-1.md`** in your worktree, sole writer. Never a basename containing "findings" — the `Write` tool refuses it.

## Workspace

- Worktree: `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`
- Branch: `epic-568/c2-native-isolation`
- Base: **`9bb8c1b6`** — current `main`, which already carries the merged guard
Provisioned and verified. `git worktree list` at dispatch time:

```
/home/tommy/projects/constellation-skills                         3e4e07a3 [main]
/home/tommy/projects/constellation-skills-wt/epic-568-315         bcc99f07 [epic-568/c1-check-cwd]
/home/tommy/projects/constellation-skills-wt/epic-568-315-native  9bb8c1b6 [epic-568/c2-native-isolation]
```

Note the Admiral's main checkout reads `3e4e07a3` — it has not pulled the merge. **Your base
`9bb8c1b6` is correct and already carries the guard**; the main checkout being behind is the
Admiral's housekeeping, not your concern. Do not "fix" it.

First action, before any git operation:
`py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/epic-568-315-native` — must exit 0. Paste the output in your return.

**This is a fresh worktree, not the previous Commander's.** Its worktree (`epic-568-315`) still exists and holds artifacts pending harvest at closeout. Do not enter or reuse it.

PR integration defaults to **server-side merge**.

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` resolves once at session launch to the **main checkout**, so a Commander in an isolated worktree still runs the main checkout's hooks against the main checkout's state (#269).

**AMENDED 2026-08-13 — the Admiral's claim here was false.** The original order said the wired hooks "both call the engine you are changing" and asked for fresh-process validation on that basis. The previous Commander falsified it: `spine_rail.py`'s own docstring says do **not** subprocess the engine, and it keeps that promise — it reconstructs `current` in-process and its single subprocess is `git worktree list`. `gauge_writer_hook.py` never calls the engine at all. **That validation instruction had no subject; ignore it.**

The real cross-tree caller is **`scripts/mcp_spine_server.py:361`**, which invokes `checklist_engine.main()` **in-process and never chdirs**. That is the caller your change must reason about, and it is a genuine hazard for a cwd-comparing guard: the MCP server's cwd is the server's, not the spine's. Handle it deliberately and say how.

## Inherited Context

- **`tests/test_worktree_precondition_wiring.py` — AMENDED 2026-08-13. The Admiral was wrong about this.** The original order called it your tripwire and said a green run proves both halves landed. **It does not.** Every fixture in it builds an `origin`-less spine by hand, so it is green **by construction** and blind to the stamped path entirely. It is evidence for the **fallback branch only**. Keep it green and do not weaken it — but do not treat its greenness as coverage of your change. **You owe a new test that exercises a spine actually carrying `origin`**, covering both the match and the mismatch. Without it this change ships with a guard that cannot fail, which is the defect class this epic exists to remove.
- **The `spine` MCP door is not trustworthy** — `.mcp.json` defaults `SPINE_FILE` to a demo spine when unset, and the Admiral's door is bound under `constellation-skills-wt/f-424/`, which is not even a registered worktree. `spine-epic` is dead. **Call `spine_status` and confirm it names YOUR gates before trusting any door call.** The CLI always works.
- **Backticks in a double-quoted engine `--finding`/`--note` are shell-substituted** (#551).
- **`main`'s CI is red and it is not you.** Pre-existing Windows breakage: 76 failures on main (path separators, unset git identity on the runner). The merge gate for this epic is **no new failures against the `main` baseline**, not a green run. Measure your PR's failure set against main's and report the set difference.
- Applying an episode delta leaves the tree dirty and `test_episode_negative_control.py` reads that as failure (handoff U4); staging clears it. Not a defect in your change.
- On Windows, write PR bodies to a file and use `gh pr create -F <file>`.
- The repo cannot orient itself — `map_orient.py` returns `DEGRADED-UNPARSEABLE`, anchor count 0. Use file paths, not map anchors.

## Pre-empted Steps

Cite this order rather than redoing these:

- **The defect, the falsification, and the trap are all established.** You do not need to re-derive that `cwd`-forwarding disarms the gate; the demonstration is pasted above and the guard is merged.
- **The direction is ruled by the human** and the costing is done. You are implementing, not choosing.
- **The blast radius is measured**: 17 checks, none needing edits; backfill population 2.
- **Base freshness verified** at `9bb8c1b6`.

## Data Locations

Everything you need is tracked. The prior Commander's costing is at
`/home/tommy/projects/constellation-skills-wt/epic-568-315/.agent-work/commander-315/COSTING-stored-origin.md`
and its trap demo at `d_trap_demo.sh` in the same directory — **read-only, do not work in that tree**.

## Budget

- **Model tier (required):** **Opus**. Engine-core work on a 3352-line module, with a demonstrated trap that a careless cut walks straight into.
- **Compute/time:** one Commander, serialized lane, no concurrent dispatch on the engine-core files.

## Stop Conditions

Stop and return when: the change wants to touch `spine_rail.py` or `agent_work_root.py`; the native comparison proves wrong on evidence; a decision outside your latitude is needed; the merged guard goes red and you believe the guard rather than your change is at fault; or you need context this order does not cover.

## Return Shape

Write your result artifact **before** going idle. Return thin, write fat.

Your return must carry: the verdict; the before/after repro; proof that `init.c0`'s command check is **deleted** and the native refusal fires in the case it used to catch; confirmation the merged guard is **green** (and your reading of why that proves both halves landed); your PR's failure set **diffed against main's baseline** with the set difference stated; the `verify_worktree_isolation.py --here` output; which choice you made on the 2 live spines and why; map impact; triage candidates; and workflow feedback written as what you **observed**, not as a rule for a future agent.

PR against `main`. The Admiral merges on an empty failure-set difference plus an independent reviewer APPROVE — do not merge it yourself.
