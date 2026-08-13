# Reviewer Handoff

## Gate
`g1-review` of `.agent-work/commander-315-native/execute.json` (work-id `commander-315-native`).

Worktree: `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`, branch `epic-568/c2-native-isolation`, base `9bb8c1b6`. **Never enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`** and never write the main checkout.

You are an **independent** verifier. You did not write this change. Reproduce every claim; do not accept a number because the implementer stated it.

## What the change is

A spine now carries its own repo reference from creation, and `checklist_engine.py` enforces worktree isolation **natively** against it, replacing a command check that lived inside one spine template.

- **Write side:** `scripts/init_work_area.py` `instantiate_spine` stamps a top-level `origin` block.
- **Read side:** `scripts/checklist_engine.py` gains the pure `origin_worktree_refusal(spine, *, cwd, verb) -> str | None`, called from one site in `main()` after `load()` and before `dispatch()`.
- **Deletion:** `skills/commander/templates/COMMANDER_SPINE.template.json` `init` precondition `c0`, plus `scripts/verify_worktree_precondition_coverage.py` and the enumeration tests in `tests/test_worktree_precondition_wiring.py` that exercised it.
- **Docs:** `docs/CHECKLIST_SCHEMA.md` documents `origin`.
- **New coverage:** `tests/test_spine_origin_isolation.py`.

The implementer's result is at `.agent-work/commander-315-native/crew-handoffs/g1-implementer-result.md`. The handoff it worked from is `g1-implementer-handoff.md` in the same directory — read it for the frozen constraints.

## Your jobs, in order

### 1. THE TRAP

The falsified predecessor to this change forwarded a stored root into `verify_worktree_isolation.py --here` as `cwd=`, making the comparison `X == X` — because `origin.worktree` and the EXPECTED value inside the check text both derive from the same resolved root at creation.

Prove this change did **not** reproduce that:

- The comparison's two sides come from **independent sources**: the stored side from the spine file, the measured side from the engine's own `Path.cwd()`.
- No `cwd=` is forwarded to any subprocess. Grep the diff for it.
- The refusing side **genuinely fires** — construct the mismatch yourself and watch it refuse. Do not take the implementer's word.

### 2. THE ARM

**This is the load-bearing job.** Every new check must be shown failing in the defective world, not merely passing in the healthy one.

Independently revert each half and confirm the new tests go red:

- Remove the `origin` stamp from `init_work_area.py` → the origin-carrying tests must fail.
- Remove the `origin_worktree_refusal` call site from `main()` → the mismatch tests must fail.

Restore after each. **Do this yourself with `git stash`/manual edit — do not replay the implementer's transcript.** A test that passes in both worlds is not a test, and "a check that cannot fail" is the exact defect class this issue exists to remove.

### 3. THE FALLBACK

Every one of these must take the pre-change behaviour and **none may raise**:

`origin` absent · `origin: null` · `origin` a **string** · `origin` a **list** · `origin: {}` · `worktree` absent · `worktree` empty string · `worktree` not a string.

The string and list cases matter most: `.get` on them raises `AttributeError`, which `main()` does not catch. `scripts/validate_spine.py` guards none of these shapes.

### 4. THE NO-GOS

- No forwarded `cwd`.
- `base_dir` untouched in `checklist_engine.py` — the resolved root is carried in a distinct name.
- **No write on the refusal path.** `main()` saves on the `EngineError` path for every verb except `current`, so a refusal raised inside `dispatch()` would write into the tree the guard protects. Verify by hashing the spine file before and after a refused guarded verb. Judge it on the hash, not on the refusal prose.
- `scripts/spine_lifecycle.py` unchanged (`git diff --stat` must not list it).
- `scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` unchanged.
- `tests/test_worktree_precondition_wiring.py`'s **surviving** assertions not weakened. Read the diff of that file: the removals must be confined to the enumeration tests that exercised the deleted coverage script. Any edit to a surviving test's assertions is a finding.
- `init.c0` and its coverage apparatus **deleted** — this is the Admiral's authorized 2026-08-13 four-file change, so deletion is the expected state, not a breach. Confirm `skills/commander/templates/COMMANDER_SPINE.template.json` `init.preconditions` is `[]` and `scripts/verify_worktree_precondition_coverage.py` no longer exists.

### 5. THE OVERCLAIM

The Admiral **withdrew** the claim that this guard "cannot be lied to by a child process's cwd". It is false: `_run_check_command` passes no `cwd=`, so a check authored as `cd <origin.worktree> && ...` still satisfies the guard.

Search the change and every artifact it produced — code, comments, docstrings, test names, the docs edit, the implementer result — for any restatement of non-forwardability, unforgeability, or immunity to a child's cwd. **Any occurrence is a finding.**

The three properties this change may claim, and only these:

1. **Coverage** — every guarded verb on every spine, not only where a check was wired into a template.
2. **Unbypassability from the spine** — a spine's own text cannot switch it off, because the check is no longer in the spine.
3. **An independent expected side** — from the creation-time stamp, not from a literal inside a check.

Confirm the change claims these accurately, and confirm it does not claim more.

### 6. THE NEW COVERAGE

`tests/test_worktree_precondition_wiring.py` is the merged guard from the prior wave. **Every fixture in it builds an `origin`-less spine by hand**, so it is green *by construction* under this change and structurally blind to the stamped path. It is evidence for the **fallback branch only**.

Confirm:

- `tests/test_spine_origin_isolation.py` exercises a spine that **actually carries `origin`**, on **both** the match and the mismatch side.
- Containment is covered: worktree root passes, a **subdirectory** of it passes, and a **sibling sharing a name prefix** (`/w/repo-2` against `/w/repo`) does **not** pass. Equality instead of containment would be a regression — the superseded check compared `git rev-parse --show-toplevel`, which succeeds from any subdirectory.
- The guarded verb set is asserted **as data**, both membership and non-membership, and derived from `MUTATING_VERBS` so a future verb is guarded automatically. Expected: guarded = `MUTATING_VERBS | {"claim", "heartbeat"}`, exempt = `{"current", "release"}`.
- Nothing in the change or its artifacts cites the wiring test's greenness as proof the new behaviour works.
- Any case-folding assertion is `skipUnless(os.name == "nt")` and does not pretend to prove something on Linux.

### 7. THE IN-PROCESS CALLER

`scripts/mcp_spine_server.py:361` calls `checklist_engine.main(argv)` **in-process** and never `chdir`s, so the guard reads the **MCP server process's** cwd, not the spine's. (`spine_rail.py` never subprocesses the engine; `gauge_writer_hook.py` never calls it. This is the only real cross-tree caller.)

The Commander ruled: **the guard applies here with no exemption, no env override, and no bypass.** Confirm the implementation honours that — specifically that **no** environment variable or flag can switch the guard off, since that would be an off switch outside the spine, recreating the defect one level over.

Confirm the test reproducing the MCP shape exists: `os.chdir` to a foreign directory, then call `checklist_engine.main([...])` **in-process** (not via subprocess) against a spine carrying `origin`, asserting a guarded verb returns non-zero and leaves the spine byte-identical while `current` returns 0.

## Additional checks the Commander wants specifically

- **`instantiate_spine` now re-serializes the spine** with `json.dumps(spine, indent=2)` instead of writing the resolved text verbatim. Check what that changes: `ensure_ascii` defaults to **True**, so any non-ASCII character in any spine template (em dashes, arrows, curly quotes) becomes a `\uXXXX` escape in the written spine. Determine whether any shipped template under `skills/*/templates/` contains non-ASCII, and whether the round-trip alters rendered text, key order, or trailing newline. Report what you find either way — this is a real question, not a leading one.
- Confirm `Path.is_relative_to` is used for containment rather than a string `startswith`.
- Confirm the guard sits **before** the `refusals` arming in `main()` and therefore does not increment or persist that counter.

## Required Evidence

Run and paste:

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/ -q -p no:randomly
python -m pytest tests/ -q -p no:randomly 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
python .agent-work/commander-315-native/repro_native.py
git diff --stat
```

`main`'s Linux baseline is **2934 passed, 5 skipped, 0 failed**. State your numbers against it and name any difference.

`repro_native.py` is the Commander's before/after repro and is **not yours to edit**. If it fails, report the output.

Derive any failure distribution mechanically with the `grep`/`uniq -c` command above — never summarize from a glance at the output tail.

## Out of scope

Do not fix anything. Do not edit production code, tests, or docs. Report findings. If you must modify the tree to run the arming reverts, restore it exactly and confirm `git status` matches what you started with.

## Return Format

Return `REVIEW_RESULT` with a **`Verdict`** field of exactly `APPROVE` or `BLOCK`.

`APPROVE` only if every job above passes on evidence you reproduced yourself. `BLOCK` with a specific, reproducible finding otherwise. A finding must name the file, the line, what is wrong, and how you observed it.

Also carry: what you verified and how; anything you could **not** verify and why; out-of-scope observations; and workflow feedback as what you observed.

**Delivery:** write the full result to `.agent-work/commander-315-native/crew-handoffs/g1-reviewer-result.md` before ending your turn. That write is the delivery.
