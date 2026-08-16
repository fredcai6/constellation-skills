# IMPLEMENTER_RESULT — g2 (#605, the shipped demo spine is unusable)

**Return status:** `complete`

Session `constellation/cleanup-a-door/g2/implementer/attempt-1`.
Plan driven through the engine at
`.agent-work/cleanup-a-door/crew-plans/g2-implementer-plan.json` — six items,
all closed, `DONE: no open items`.

---

## Completed slice

The demo now runs where it is installed, on any machine, and two guards keep it
that way.

**The design call — candidate (b), and it was not close.** #605's own fix
direction (relative paths) is measurably unworkable, as the handoff established.
Between the two remaining candidates, **(a) "ship the generator, not the
generated spine" is excluded by this gate's own boundary, not by taste**:
`tests/test_mcp_spine_server.py:588` asserts `ROOT / <.mcp.json's SPINE_FILE
default>` `.is_file()` and json-loads it, and that default is
`examples/mcp-interactive-demo/spine.json`. Not committing the generated spine
fails that test, and the only reconciliation is editing `.mcp.json`'s default —
g3's file, and an explicit stop condition. So (a) could not be done here without
reaching into g3 and inverting the gate order.

(b) is also the smaller change: one generator plus one regenerated file, no test
reconciliation, no cross-gate hazard. And drift — which is (a)'s entire argument
— is closed without (a)'s cost, by a test that imports the generator and asserts
the committed `spine.json` is byte-identical to what it produces. A hand-edit
back to a machine-specific path now fails the suite.

**How the spine addresses its own files.** Every command check and imperative
names the workspace as:

```
${SPINE_DEMO_WORKSPACE:-${TMPDIR:-/tmp}/constellation-mcp-demo-$(id -u)}/workspace
```

The shell that runs the check expands this itself, so it resolves to an absolute
location on any machine **without an ambient cwd** — which is the property
`checklist_engine.py:883` actually requires, since it runs checks with no `cwd`.
`$(id -u)` keeps two users on one host out of each other's demo directory;
`SPINE_DEMO_WORKSPACE` is the override seam. Nothing machine-specific is
committed, and the workspace lands outside the repository.

---

## Files changed

**Committed (staged):**

| File | Change |
|---|---|
| `examples/mcp-interactive-demo/make_demo_spine.py` | **new** — the generator, next to the spine it writes |
| `examples/mcp-interactive-demo/spine.json` | regenerated; 11 lines changed, six machine-specific paths gone |
| `examples/mcp-interactive-demo/README.md` | regeneration command now points at a live path; two dead relative paths removed; new "Where the demo writes" section |
| `examples/mcp-interactive-demo/.gitignore` | **new** — keeps the engine's per-run side-cars out of the tree |
| `tests/test_shipped_examples_are_portable.py` | **new** — 7 tests: the portability guard, the dead-path guard, the anti-drift check, and a drives-from-anywhere regression with a negative control |
| `map/INDEX.md` | rebuilt (`py -m scripts.code_map build --root .`) — the new generator module made it stale |

The six path strings were **not** hand-edited; `spine.json` is generator output.

---

## Test mode satisfied

TDD red → green for both guards; test-after for the rest. Both guards were
**observed failing** on pre-fix content before the fix existed.

---

## Evidence produced

### 1. Load-bearing — the demo actually drives, from two different cwds

Both runs drove the **shipped** `examples/mcp-interactive-demo/spine.json` end to
end. The spine was regenerated and the workspace deleted before each run, so
nothing carried over.

**Run 1 — cwd `/tmp/nowhere-near-the-repo-3112947/deep/dir`** (neither the repo
root nor the example directory, and under neither):

```
--- g1: follow the imperative, then advance ---
g1 -> in-progress
attested g1.c2
g1 -> complete
--- g2: artifact/user-decision postcondition ---
g2 -> in-progress
attached e-g2-1 (user-decision) to g2
g2 -> complete
--- g3: command check left FALSE, satisfied by waive ---
g3 -> in-progress
waived g3.c1 by human -> e-g3-1
g3 -> complete (WAIVED postconditions ['c1'])
--- g4: block/resume cycle, then close out ---
g4 -> in-progress
g4 -> blocked (bubbled to parent)
g4 resumed -> in-progress (blocker resolved: demo resumed)
attested g4.c2
g4 -> complete

DONE: no open items. WAIVED: ['g3.c1']
```

The default workspace expanded to `/tmp/constellation-mcp-demo-1000/workspace`
with no env var set and no setup.

**Run 2 — cwd = the repo root** (the git toplevel, i.e. what the MCP door
actually stands in), carrying a negative control first:

```
--- negative control: can g1 advance BEFORE notes.txt exists? ---
g1 -> in-progress
attested g1.c2
REFUSED: g1: postconditions unmet ['c1'] Recovery: fix the underlying issue ...

--- now satisfy it and advance for real ---
g1 -> complete
g2 -> complete
g3 -> complete (WAIVED postconditions ['c1'])
g4 -> complete

DONE: no open items. WAIVED: ['g3.c1']
```

The negative control matters: it shows the check is genuinely reading the
filesystem. The healthy and defective worlds differ.

### 2. Load-bearing — both guards fail on pre-fix content

**Portability guard, against the pre-fix tree** — six violations, at exactly the
six lines the handoff enumerated:

```
scanned 3 shipped example file(s) under examples/ and found 6 machine-specific path(s):
  examples/mcp-interactive-demo/spine.json:20:  '/home/tommy' is a POSIX user home directory
  examples/mcp-interactive-demo/spine.json:28:  '/home/tommy' is a POSIX user home directory
  examples/mcp-interactive-demo/spine.json:78:  '/home/tommy' is a POSIX user home directory
  examples/mcp-interactive-demo/spine.json:86:  '/home/tommy' is a POSIX user home directory
  examples/mcp-interactive-demo/spine.json:109: '/home/tommy' is a POSIX user home directory
  examples/mcp-interactive-demo/spine.json:117: '/home/tommy' is a POSIX user home directory
```

**Dead-relative-path guard, against the pre-fix README** — the class an
absolute-path guard is blind to:

```
resolved 6 repo path(s) across 4 shipped example file(s) and found 2 dead:
  examples/mcp-interactive-demo/README.md:13: '.agent-work/epic-418-followon/commander-424/crew-plans/scratch-mcp/make_scratch_spine.py' does not exist
  examples/mcp-interactive-demo/README.md:27: 'scripts/gen_mcp_config.py' does not exist
```

Both state what they looped over and neither can pass on an empty set. After the
fix: **7 passed, 3 subtests passed**.

### 3. Load-bearing — zero machine-specific absolute paths under `examples/`

**In shipped (tracked) content — the thing that reaches another machine: 0, over
5 tracked files.**

```
$ git ls-files examples/ | xargs grep -n "/home/\|constellation-skills-wt\|f-424"
exit=123      # no matches
count: 0  over 5 tracked files
```

Handoff's verbatim command, after clearing the scratch my own two demo drives
left on disk:

```
$ grep -rn "/home/\|constellation-skills-wt\|f-424" examples/ ; echo "exit=$?"
exit=1
count: 0
```

**Worth reading carefully:** before that cleanup the raw `grep -rn` reported
**12** hits. None were shipped content — see "where the writes land" below.

### 4. Confirmatory

- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_mcp_spine_server.py tests/test_wire_mcp_interpreter.py tests/test_install_constellation.py` → **237 passed, 505 subtests**. `test_mcp_json_referenced_spine_file_exists_and_loads` passes **unchanged** — no reconciliation was needed, because (b) keeps the spine committed.
- `map/INDEX.md` freshness → was **stale** (the new generator added `examples: 1 modules, 4 entities`); rebuilt and staged; `tests/test_code_map.py` → 148 passed.
- Full suite → **3072 passed, 6 skipped, 1149 subtests, 0 failures**.
- `__pycache__` cleared before every measurement (#597).

### 5. Wiring grep

All 9 new callable symbols, each with a call site outside its own definition;
neither file has a `--self-test` path.

| Symbol | External call sites |
|---|---|
| `build_spine` | 2 — `spine_text()`; the test's `generator.build_spine()` |
| `spine_text` | 2 — `write_spine()`; the drift test |
| `write_spine` | 1 — `main()` |
| `shipped_example_files` | 2 |
| `load_demo_generator` | 2 |
| `read_text_or_none` | 2 |
| `machine_specific_hits` | 1 |
| `repo_top_level_entries` | 1 |
| `repo_path_tokens` | 1 |

No symbol has zero. No stop condition.

---

## Where the demo's writes land — and the thing the handoff half-anticipated

The handoff asked where `<arm>/workspace/` writes land and what I did about
regenerating dirtying a tracked directory. Driving the demo showed the workspace
was never the risk:

- **Workspace writes** (`notes.txt`, `optional_report.txt`, `SUMMARY.md`) land
  **outside the repo**, at `/tmp/constellation-mcp-demo-$(id -u)/workspace`.
  Verified after two full drives. They never touch the tree.

- **What actually dirties the tree is the engine's own per-run state.** The
  engine writes its side-cars next to whatever spine file it is pointed at — and
  for the shipped demo that is a tracked directory. Two drives produced **nine
  untracked files carrying twelve absolute-path occurrences**:
  `spine.json.journal`, `context/g1..g4.json`, `mechanical/g1..g4.json`. Those
  twelve are the count in evidence 3.

  I added `examples/mcp-interactive-demo/.gitignore` for those three side-car
  paths, with the reason written in it. This is a **deliberate exception** to the
  root `.gitignore`'s stated rule that engine journals are never excluded: that
  rule protects the audit trail of a real run under `.agent-work/`, and this
  spine is a throwaway fixture with no history to protect.

- **`spine.json` itself is still mutated** by driving — gates advance in the
  tracked file. That is inherent to `.mcp.json` binding the tracked path
  directly, and is g3's (#603) bind-on-open territory, so I did not touch it.
  What I could do inside scope, I did: resetting it is now one command
  (`python examples/mcp-interactive-demo/make_demo_spine.py`), which the README
  now says. Before this gate there was no live command to reset it with.

This also drove a **correction to my own plan**, made through the engine
(`amend`, not by hand): `m3.c3` originally asked "no workspace writes under
`examples/`", which was the wrong question and would have passed for the wrong
reason. Retexted to: after a full drive, nothing unstaged or untracked remains
under `examples/`.

---

## Assumptions used

1. **"Shipped" means tracked.** The portability guard lists files via
   `git ls-files examples/`. This was not cosmetic — scanning untracked files
   would have made the guard fail for anyone who ran the demo, since the engine
   side-cars legitimately embed the driver's absolute paths. That is precisely
   the over-broad guard the handoff said would get switched off.
2. **`/tmp` is not machine-specific.** `${TMPDIR:-/tmp}` is POSIX-standard and
   resolves on any machine, so the guard does not flag it. The handoff's own
   verification command takes the same position (it greps for `/home/`,
   `constellation-skills-wt`, `f-424`).
3. **The dead-path guard resolves only paths rooted at this repo's own
   top-level entries.** `examples/sync-constellation-skills.yml` is a workflow
   template for a *consuming* repo, and its `.github/workflows/...` and
   `.constellation-src/...` paths deliberately do not exist here. It is exempted
   by name with the reason recorded, and a second test fails if that exemption
   ever names a file that no longer exists, so the exemption cannot rot silently.
4. **`work_id` changed** from `scratch-mcp-424` to `mcp-interactive-demo`. Grep
   confirmed the only non-archive occurrence was the spine's own line.

---

## Stop conditions hit

**None.** Scope was not exceeded and no exclusion was touched.

Worth stating explicitly, since the handoff anticipated it: the stop condition
"reconciling `test_mcp_spine_server.py:588` would require editing `.mcp.json`"
**did not fire** — but only because candidate (b) was chosen. Under candidate
(a) it would have fired immediately. That is the reason (b) was chosen, not a
happy accident.

Untouched as required: `.mcp.json`; `scripts/mcp_spine_server.py`;
`scripts/checklist_engine.py` (read only, to understand `:883`);
`scripts/hooks/**`; `scripts/run_crew.py`; `scripts/gauge_reader.py`;
`scripts/install_constellation.py`;
`skills/commander/templates/COMMANDER_SPINE.template.json`. The README's opening
sentence ("This is the checklist the project-scope `.mcp.json` points at") is
**verbatim intact** — verified by a command check in my plan, and the README diff
begins at line 10.

---

## Out-of-scope observations (triage candidates)

1. **`scripts/gen_mcp_config.py` was deleted but still recommended.** The shipped
   README told readers to use it for real dispatches. I replaced that with the
   mechanism that actually superseded it (`.mcp.json`'s `${SPINE_FILE:-...}`
   expanded from the caller's environment). Worth checking whether anything else
   in the corpus still recommends the deleted script — I only swept `examples/`.

2. **Driving any spine writes side-cars beside it.** Harmless for `.agent-work/`
   runs, but it means *any* spine committed outside `.agent-work/` will dirty its
   directory when driven. Relevant to g3's bind-on-open work: if the demo is
   copied to a scratch location on open, this disappears and my `.gitignore`
   becomes redundant.

3. **`map/ids.jsonl` is tracked but 0 bytes**, so no map anchor resolves anywhere
   in this repo. The handoff already flagged this as a triage candidate; I worked
   from source. Confirming it is still true.

4. **`examples/mcp-interactive-demo/README.md` line 3 will be false after g3.**
   Left alone as instructed — noting it so g3 does not miss it.

---

## Workflow feedback

1. **No `Test mode` section in the handoff.** The template calls for one and the
   crew skill checks for it. It was unambiguously inferable (the Constraints
   demand a demonstrated red on pre-fix content, which is red-then-green), so I
   proceeded rather than blocking — but I had to infer it.

2. **The bound spine was the Commander's, not mine.** `SPINE_FILE` pointed at
   `.agent-work/cleanup-a-door/spine.json` with `SPINE_SESSION` =
   `.../execute/commander` and the lease held by `commander-cleanup-a-door`, with
   `execute` active. The crew skill says "do not author a plan of your own when a
   spine is already bound", but that binding is the parent's reach-up handle —
   driving it would have meant closing the Commander's own gate. I read it as the
   reach-up binding and built my own plan. Worth disambiguating in the skill: a
   *dispatched crew* is bound to its parent's spine for `spine_halt block`, not
   for driving.

3. **The handoff's own verification command over-reports on a machine where the
   demo has been driven.** `grep -rn ... examples/` cannot distinguish shipped
   content from git-ignored scratch, so it returned 12 after my two drives and 0
   after cleanup. `git ls-files examples/ | xargs grep -n ...` is the stable form
   and is what I would suggest for future handoffs in this class.

4. **Map anchors were accurate and load-bearing.** In particular, naming
   `checklist_engine.py:883` as read-only-and-this-is-why saved the whole design
   from restarting at the relative-path dead end. The "Map entry point: none"
   note was honest and correct.

---

## Map Impact

- **Structural (new):** `examples/mcp-interactive-demo/make_demo_spine.py`
  (`build_spine`, `spine_text`, `write_spine`, `main`);
  `tests/test_shipped_examples_are_portable.py`;
  `examples/mcp-interactive-demo/.gitignore`. `map/INDEX.md` rebuilt — `examples`
  is now a mapped package (1 module, 4 entities), which it was not before.

- **Constraint — satisfied and now enforced:**
  `constraint:shipped-content-must-not-carry-machine-specific-absolute-paths` is
  no longer an assertion; it is a test that has been observed failing.

- **Constraint — re-measured, unchanged:**
  `constraint:engine-runs-command-checks-with-no-cwd` confirmed at
  `checklist_engine.py:871-941`. Note `_check_condition` does take a `base_dir`,
  but it is used **only** by the `git-change-policy` branch — the `command`
  branch calls `_run_check_command`, which never passes `cwd`. So the constraint
  holds exactly as stated, and the `base_dir` parameter is not a latent way out.

- **Decision — resolved:** `decision:demo-spine-is-generated-not-hand-fixed`, and
  its `settle:` clause ("whichever is smaller once the example's build is read")
  is answered: candidate (b). Grade moves from `guess` to **measured** — (a) is
  excluded by `test_mcp_spine_server.py:588` plus the `.mcp.json` exclusion, not
  by preference.

- **New decision anchor candidate:**
  `decision:a-shipped-spine-addresses-its-workspace-by-shell-expansion-not-by-path`
  — the general form of this gate's answer, and the reusable one for any future
  committed spine.

- **Claim — discharged:** `claim:605-demo-unusable`. Driven to `DONE` from two
  cwds, one neither the repo root nor the example directory, with a negative
  control proving the check discriminates.
