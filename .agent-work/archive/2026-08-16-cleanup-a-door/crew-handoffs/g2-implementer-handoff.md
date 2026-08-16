# Implementer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g2` — issue #605, the shipped demo spine is unusable.

## Task

`examples/mcp-interactive-demo/spine.json` is tracked, ships to every install, and carries
**six** absolute paths (lines 20, 28, 78, 86, 109, 117) into
`/home/tommy/projects/constellation-skills-wt/f-424` — a worktree deleted during the
epic-418-followon closeout, on one machine, which never existed anywhere else. So the demo
cannot be run as shipped.

Make the demo runnable where it is installed, on any machine, and add a guard that keeps a
machine-specific absolute path out of a shipped example again.

## Protected intent

A shipped example must run for the person who installed it. Whatever you produce must work
on a machine that has never heard of `/home/tommy`.

## The constraint that overrides the issue's own fix direction — read this before designing

**#605 says "regenerate it with paths relative to the example directory". That cannot
work, and it is measured, not argued.** `scripts/checklist_engine.py:883` runs command
checks as:

```python
proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
```

**No `cwd`.** The check inherits whatever directory the driving process happens to stand
in — through the MCP door that is the bound spine's git toplevel
(`_standing_in_the_bound_spines_worktree` → `_worktree_root_for_lifecycle`,
`scripts/mcp_spine_server.py:600-611`); from the CLI it is the user's own cwd. So a path
relative to the example directory resolves correctly from essentially nowhere.

The surviving generator already recorded this reasoning, and it is why the paths were
absolute in the first place:

```
.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/scratch-mcp/make_scratch_spine.py
  "Command-check paths are ABSOLUTE (the engine runs `command` checks with no `cwd`)."
```

**So settle how a shipped spine addresses its own files at all, before writing one.** Two
candidates — pick one, implement it, and say plainly why you picked it:

- **(a) Ship the generator, not the generated spine.** The demo is produced into a scratch
  or temp directory at demo time, with absolute paths correct for *that* machine. Nothing
  machine-specific is ever committed.
- **(b) Ship a spine whose check text is self-locating**, so it needs no ambient cwd at all.

Judge them on which is smaller and which leaves less to drift — that is exactly what
`decision:demo-spine-is-generated-not-hand-fixed`'s `settle:` clause asks. If you find a
third option that is clearly better, take it and say why.

**Do not hand-edit the six path strings.** Producing the spine from the example's own
directory is the point; hand-editing is what lets it drift back.

## Close criteria

- No absolute or machine-specific path remains anywhere under `examples/`. Enumerate by
  command and **state the count**.
- The demo **drives** — actually run it — from at least **two different working
  directories**, one of which is neither the repo root nor the example directory. The
  driving cwd is the load-bearing variable here, not where the spine was generated.
- A real test in the suite keeps a machine-specific absolute path out of a shipped example,
  and it **fails on the current (pre-fix) content**. Demonstrate that; do not assert it.
- You state where the demo's `<arm>/workspace/` writes land. Regenerating under
  `examples/` would dirty a tracked directory — say what you did about it.
- `tests/test_mcp_spine_server.py:588`
  (`test_mcp_json_referenced_spine_file_exists_and_loads`) **still passes.** It asserts
  `.mcp.json`'s default resolves to a real, loadable spine. If candidate (a) removes the
  shipped spine file, this gate must reconcile that test and say how.
- `examples/mcp-interactive-demo/README.md`'s regeneration command points at a path that
  **exists**. It currently names `.agent-work/epic-418-followon/...`; the generator moved
  to `.agent-work/archive/2026-08-09-epic-418-followon/...`. A dead *relative* path is not
  caught by an absolute-path guard.

## Allowed scope

- `examples/mcp-interactive-demo/**` — including `README.md`.
- `tests/` — the new guard, plus minimal reconciliation of
  `tests/test_mcp_spine_server.py` if your candidate requires it (pre-authorized; say what
  you changed and why).
- A new generator script if candidate (a) needs one — you choose where it lives; justify
  the location.

## Specific exclusions

- `.mcp.json` — **gate g3's** (#603). Do **not** remove or edit the demo default here.
- `scripts/mcp_spine_server.py` — g1's and g3's.
- `README.md`'s opening sentence, "This is the checklist the project-scope `.mcp.json`
  points at" — **still true until g3, and g3 owns changing it.** Leave it.
- `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`,
  `scripts/gauge_reader.py` — **lanes B and C, running concurrently.** Read
  `checklist_engine.py` to understand `:883`; never modify it.
- `scripts/install_constellation.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`.

## Constraints

- **The guard must be able to fail.** Demonstrate it failing on the pre-fix file. A check
  whose output is identical in the healthy and the defective world cannot discriminate —
  and this repo has been bitten by exactly that.
- **Do not make the guard vacuous.** It must assert what it looped over and must not pass
  on an empty set. State the count of files it examined.
- **Scope the guard to shipped examples.** Do not sweep paths the repo legitimately carries
  — installed absolute skill paths in `.agent-work/` spines, test fixtures, the archived
  generator. An over-broad guard that fails on legitimate content will be turned off.
- **Clear `__pycache__` before every measurement**
  (`find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +`). Stale
  bytecode from a relocated worktree fabricates failures that look exactly like defects
  (#597).
- If you add or rename an entity, run `py -m scripts.code_map build --root .` and commit
  the result, or the `map/INDEX.md` freshness test fails on a file you did not think you
  touched.

## Map anchors (inbound)

- **Map entry point: none.** `map/ids.jsonl` is tracked but **empty (0 bytes)**, so no map
  anchor resolves anywhere in this repo (triage candidate). Work from source.
- **Structural:** `examples/mcp-interactive-demo/spine.json:20,28,78,86,109,117`;
  `examples/mcp-interactive-demo/README.md`; `scripts/checklist_engine.py:883` (**read
  only** — this is *why* relative paths cannot work);
  `.agent-work/archive/2026-08-09-epic-418-followon/commander-424/crew-plans/scratch-mcp/make_scratch_spine.py`
  (the surviving generator); `tests/test_mcp_spine_server.py:588`.
- **Capability:** shipped example — must run where it is installed, on any machine.
- **Constraints/assumptions:**
  `constraint:shipped-content-must-not-carry-machine-specific-absolute-paths`;
  `constraint:engine-runs-command-checks-with-no-cwd` — measured at
  `checklist_engine.py:883`.
- **Decision anchors:** `decision:demo-spine-is-generated-not-hand-fixed` — produce it from
  the example's own directory so it cannot drift back.
  `@grade: guess · leans g2-implement · settle: whichever is smaller once the example's build is read`
  Decision pressure this gate resolves: **how a shipped spine addresses its own files** —
  relative-to-example is measurably unworkable; (a) vs (b) above is yours to call, with
  your reason recorded.
- **Evidence expectations:** `claim:605-demo-unusable` — drive the demo from two different
  cwds, one neither the repo root nor the example directory.

## Deliverable path check

- **Committed** — `examples/mcp-interactive-demo/**`, your new test, any generator script.
  `git check-ignore examples/mcp-interactive-demo/spine.json` exits **1** (not ignored),
  verified at dispatch.
- New files are untracked until staged: `git diff` will show fewer files than you changed;
  the new ones appear in `git status`.
- **Local-only** — anything under `.agent-work/`; do not expect it in the diff.

## Required evidence

**Load-bearing — prove rigorously:**

1. **The demo actually drives**, from two different cwds, one of which is neither the repo
   root nor the example directory. Paste both transcripts, including a gate advancing.
2. **The new guard fails on pre-fix content.** Show the failure. (`git stash` the fix, or
   run the guard against the original file content — your call, but *demonstrate* it.)
3. **Zero machine-specific absolute paths under `examples/`**, by command, with the count.

**Confirmatory — a spot-check suffices:**

4. `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_mcp_spine_server.py tests/test_wire_mcp_interpreter.py tests/test_install_constellation.py`
5. `map/INDEX.md` freshness still passes.

## Wiring grep

**Required.** If you add a generator or a guard helper, one command naming each new symbol
showing a call site outside its own definition and outside any `--self-test` path, with
**the count of call sites found**. Zero external call sites is a stop condition. Write
`none — <reason>` only if this slice adds no callable symbol.

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
grep -rn "/home/\|constellation-skills-wt\|f-424" examples/ ; echo "exit=$?"
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_mcp_spine_server.py tests/test_wire_mcp_interpreter.py tests/test_install_constellation.py
```

## Suggested model tier

`stronger` — the issue's own stated fix direction is measurably wrong, so this gate has a
real design call to make (candidate (a) vs (b)) before any code, and it must reconcile a
guard test that exists specifically to catch this class of defect.

## Authority

Already decided, not yours to revisit: relative-to-the-example-directory is out (measured);
the demo must not carry machine-specific absolute paths; `.mcp.json` and README's opening
sentence belong to g3. **Yours to decide, with the reason recorded:** candidate (a) vs (b);
where a generator lives; where `workspace/` writes land; the guard's implementation and
scope; how `test_mcp_spine_server.py:588` is reconciled if your candidate requires it.

## Stop conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched;
the guard cannot be made to fail on pre-fix content; reconciling
`test_mcp_spine_server.py:588` would require editing `.mcp.json` (that is g3's, and the
ordering would then be wrong — say so rather than reaching into g3); or a decision outside
the given authority is needed.

## Return format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope | failed`,
**lowercase** — the Commander copies it verbatim and the postcondition matches exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g2-implementer-result.md` **before ending your
turn** — that write is the delivery.
