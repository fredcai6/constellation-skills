# REVIEW_RESULT — g2 (#605, the shipped demo spine is unusable)

Session `constellation/cleanup-a-door/g2/reviewer/attempt-1`.
Survey driven through the engine at `.agent-work/cleanup-a-door/g2-review/review.json` —
7 items, all visited, all `pass`, `consolidated: verdict=APPROVE findings=0`.

## Assigned Gate

`g2` — make the shipped demo runnable where it is installed, on any machine, and guard
against a machine-specific absolute path reaching `examples/` again.

## Result

**`APPROVE`**

Nothing blocks. Two non-blocking code-smell observations and two triage candidates are
recorded below.

## Handoff compliance

All nine close criteria hold. Every number below is one I produced myself, at the staged
tree (index OIDs pinned in `/tmp/g2-review-backup/staged-manifest.txt`, spine blob
`e9927b40`); I did not carry any figure over from the `IMPLEMENTER_RESULT` or the
Commander's list without re-running it.

**C1 — no machine-specific path under `examples/`. Count: 0, over 5 tracked files.**

```
$ git ls-files -z examples/ | xargs -0 grep -n "/home/\|constellation-skills-wt\|f-424"
exit=123      # no matches
$ git ls-files examples/ | wc -l
5
```

I widened it past the handoff's three patterns, since a guard-shaped grep can miss a class
it was not told about — `/(home|Users|root|srv|opt|mnt|media)/` plus a Windows `X:\` form,
over the same tracked set: **also 0**.

The handoff's verbatim working-tree `grep -rn` returns **3**, all inside
`examples/mcp-interactive-demo/context/g1.json` — git-ignored side-cars from the
Commander's own demo drive, not shipped content. That confirms the implementer's workflow
feedback #3: the tracked-only form is the stable one.

**C2 — the demo genuinely drives, from two different working directories. Run, not read.**

Both drives used the **shipped** `examples/mcp-interactive-demo/spine.json`, not a fixture
copy, and each carried a **negative control** — because an advance that succeeds proves
nothing on its own, whereas an advance that *refuses* before the file exists and *succeeds*
after it does proves the command postcondition really resolved the path.

*Drive A — `cwd=$HOME` (`/home/tommy`), **default** workspace, `SPINE_DEMO_WORKSPACE` unset:*

```
cwd is now: /home/tommy
workspace resolved to: /tmp/constellation-mcp-demo-1000/workspace
g1 -> in-progress
attested g1.c2
g1 -> complete                       <- command check c1 passed
g2 -> in-progress / attached e-g2-1 (user-decision) / g2 -> complete
g3 -> in-progress / waived g3.c1 by human -> e-g3-1 / g3 -> complete (WAIVED ['c1'])
g4 -> in-progress
--- NEGATIVE CONTROL: advance g4 BEFORE SUMMARY.md exists ---
attested g4.c2
REFUSED: g4: postconditions unmet ['c1']
--- now satisfy it, following the imperative verbatim ---
g4 -> complete
DONE: no open items. WAIVED: ['g3.c1']
```

This is the case no test covers: the committed **default** workspace branch, expanded with
nothing set and no setup, from a cwd that is neither the repo root nor the example
directory.

*Drive B — `cwd=/tmp/a demo cwd with spaces/deep dir`, `SPINE_DEMO_WORKSPACE=/tmp/demo ws with spaces`:*

This is the variant the handoff asked me to attack — a path with a space, on both sides at
once.

```
cwd is now: /tmp/a demo cwd with spaces/deep dir
SPINE_DEMO_WORKSPACE=[/tmp/demo ws with spaces]
workspace resolved to: [/tmp/demo ws with spaces/workspace]
--- g1 NEGATIVE CONTROL first: advance before notes.txt exists ---
g1 -> in-progress
attested g1.c2
REFUSED: g1: postconditions unmet ['c1']
--- now follow the g1 imperative VERBATIM from this space-laden cwd ---
g1 -> complete
attached e-g2-1 (user-decision) to g2 / g2 -> complete
waived g3.c1 by human -> e-g3-1 / g3 -> complete (WAIVED ['c1'])
g4 -> complete
DONE: no open items. WAIVED: ['g3.c1']
```

Spaces survive because every occurrence of the expansion is double-quoted, in the check text
and in the imperative alike. Workspace writes landed outside the repo in both drives.

**Spine restored after each drive** — `md5 62b0cf80b01d4d2fb267c9549fb4d8e9`, matching the
index blob, and the full staged-OID manifest diffs clean against its pre-review snapshot.

**C3 — the guard fails on pre-fix content.** `git checkout a69bbac4 -- spine.json README.md`
(I restored the pre-fix README too, which the Commander did not):

```
FAILED ShippedExamplesNameOnlyPathsThatExistTests::test_every_repo_path_a_shipped_example_names_actually_exists
FAILED ShippedExamplesArePortableTests::test_no_machine_specific_absolute_path_in_a_shipped_example
FAILED DemoSpineIsGeneratedNotHandEditedTests::test_committed_spine_is_exactly_what_the_generator_produces
FAILED ShippedDemoDrivesFromAnyDirectoryTests::test_a_gate_advances_from_an_unrelated_working_directory
4 failed, 3 passed, 3 subtests passed
```

Four, not the Commander's three, for that reason. The staged fix was restored afterwards
from the saved index blobs and re-verified byte-identical.

**C4 — the guard is not vacuous.** This is where I spent the most effort, and it survives
everything I could build. Three separate attacks:

*(a) Starve it.* Forced `shipped_example_files()` to return an empty set, then a one-file
set:

```
--> with EMPTY set:    failures=2 errors=0
    AssertionError: 0 not greater than or equal to 3 : guard looped over 0 file(s) ... (floor 3)
    AssertionError: 0 not greater than or equal to 2 : guard examined 0 shipped example file(s); it must not pass on nothing
--> with ONE file only: failures=2 errors=0
```

Both guards state what they looped over, and neither can go green on nothing.

*(b) Mutate.* An empty-set floor only proves the guard counted; it does not prove it can
still *see*. So I injected a **fresh** violation into a shipped file — seven mutants,
including a portable control:

| injected | result |
|---|---|
| `/home/alice/...` (a different user) | **CAUGHT** |
| `/Users/bob/...` | **CAUGHT** |
| `/root/...` | **CAUGHT** |
| `C:\Users\bob\...` | **CAUGHT** |
| this checkout's own absolute path | **CAUGHT** (2 hits) |
| a newly-dead `scripts/no_such_generator.py` | **CAUGHT** by the dead-path guard |
| control: `${TMPDIR:-/tmp}/demo/workspace` | correctly **not** caught |

So it catches new violations, not only the historical one, and it does not fire on portable
text — which is the failure mode that gets a guard switched off.

*(c) Drift.* The anti-drift check is byte-exact: a hand-edit back to `/home/tommy`
**CAUGHT**, a single-space reflow **CAUGHT**, a removed trailing newline **CAUGHT**. Every
mutated file was restored and re-verified byte-identical.

**C5 — `test_mcp_spine_server.py:588` still passes.** `1 passed` on
`test_mcp_json_referenced_spine_file_exists_and_loads`, unchanged.

**C6 — the README's regeneration command points at a live path.** Run verbatim, not read:
exit 0, output byte-identical (`md5` unchanged), and it also works from `/tmp`, because
`HERE` resolves from `__file__` — so the documented command is not cwd-dependent either.

**C7 — the README's opening sentence is unchanged.** Lines 1–9 diff **empty** between
`a69bbac4` and the staged blob. "This is the checklist the project-scope `.mcp.json` points
at" is byte-intact; g3 still owns changing it.

**C8 — map freshness passes.** `tests/test_code_map.py -k freshness` → `2 passed`.

**C9 — the generator is wired.** External call site at
`tests/test_shipped_examples_are_portable.py:100` (`load_demo_generator`, used by two
tests), plus the `README.md:13` CLI form, which I executed. No `--self-test` path exists
(`grep` exit 1). **Count: 1 code call site outside the definition, 0 self-test paths.**

## Scope drift

**None.** Staged *and* unstaged together:

```
$ git diff HEAD --name-only -- . ':!.agent-work'
examples/mcp-interactive-demo/.gitignore
examples/mcp-interactive-demo/README.md
examples/mcp-interactive-demo/make_demo_spine.py
examples/mcp-interactive-demo/spine.json
map/INDEX.md
tests/test_shipped_examples_are_portable.py
```

Exactly the six named files — checking against `HEAD` rather than the index matters here,
because the change is staged and a worktree-only edit to a fenced file would not show in
`git diff --cached`. Every fenced file is a **0-line diff** against `HEAD`: `.mcp.json`,
`scripts/mcp_spine_server.py`, `scripts/checklist_engine.py`, `scripts/run_crew.py`,
`scripts/gauge_reader.py`, `scripts/hooks/**`.

One thing that looks like an omission and is not: the `map/` rebuild also wrote
`map/examples.mcp-interactive-demo.make_demo_spine/` and
`map/tests.test_shipped_examples_are_portable/`, which are unstaged. `.gitignore:73` is
`map/*`, so those are correctly ignored and only `map/INDEX.md` is tracked by exception.

## Evidence verdict

Sufficient, and independently reproducible — I reproduced all of it.

- Full suite: **3072 passed, 6 skipped, 1149 subtests** — exactly the implementer's figure.
- Handoff suite: **244 passed, 508 subtests** — exactly the Commander's figure.
- Test mode: red→green is genuinely demonstrated, not asserted. I observed both guards
  failing on pre-fix content myself (C3) and on fresh mutants (C4b), which is the stronger
  claim: a guard that only fails on the historical string is a string-match, not a rule.
- The handoff carried **no `Test mode` section** — see Workflow Feedback.

Constraints honoured: `__pycache__` cleared before every measurement (#597); the suite run
under `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`; and because the change is
**staged, not committed**, I copied the index blobs aside before every mutation and
restored the full staged manifest afterwards, verified by OID diff.

## Code/doc quality

Sound. The design call for candidate (b) is correct, and I checked its stated reason rather
than accepting it: `tests/test_mcp_spine_server.py:588` does `json.loads` the `.mcp.json`
`SPINE_FILE` default, and that default is
`examples/mcp-interactive-demo/spine.json` (`.mcp.json:9`). So candidate (a) really would
have forced an edit to g3's fenced file. The reasoning holds.

The mechanism is the right shape: the spine does not need a working directory *at all*,
rather than needing a different one. I confirmed the two properties that makes it depend on —
that the expansion is absolute from nowhere, and that quoting survives spaces — by driving
it, not by reading it.

Fowler pass: all 12 baseline smells given a verdict, `verify_fowler_pass.py` exits 0
(`.agent-work/cleanup-a-door/FOWLER_PASS.json`). Four overrides, each naming the documented
standard that wins and why; the load-bearing one is **long-method** — `build_spine()` is 81
lines, but it is a single branch-free data literal, and `global-crew.md`'s split trigger is
blurred intent rather than line count. Two smells flagged, both non-blocking, both listed
under Out-of-scope observations.

## Map impact verdict

- **Evidence supports claimed change:** Yes. `claim:605-demo-unusable` is discharged by two
  full drives with negative controls, not by inspection.
- **Constraints not violated:** Confirmed at source. `constraint:engine-runs-command-checks-with-no-cwd`
  holds exactly as stated — `_run_check_command` (`scripts/checklist_engine.py:881-883`)
  calls `subprocess.run([shell, "-c", command])` with no `cwd`, and I checked the
  implementer's specific reassurance too: `_check_condition`'s `base_dir` really is used
  only by the `git-change-policy` branch, so it is not a latent way out.
  `constraint:shipped-content-must-not-carry-machine-specific-absolute-paths` is now an
  executable rule I have observed failing.
- **Notes match the diff:** Yes, with **one correction**. The notes describe the engine
  running checks under a POSIX shell and the new test proving expansion under `bash`. But
  `_find_posix_shell` returns `shutil.which("sh")` on POSIX and prefers `bash` only on
  Windows — on this host the engine used `/usr/bin/sh`, which is `dash`. I re-verified the
  nested `${A:-${B:-c}}` and `$(id -u)` expansion under `dash` directly and it is identical,
  so the design is correct on both shells and **nothing is broken**. The test's hardcoded
  `bash` is a fidelity gap, filed as triage candidate 2.
- **Decision candidates surfaced:** Yes. `decision:demo-spine-is-generated-not-hand-fixed`
  regraded `guess` → `settled/measured` on a reason I reproduced, which earns the regrade.
  The new `decision:a-shipped-spine-addresses-its-workspace-by-shell-expansion-not-by-path`
  is a fair generalization and worth carrying to Cartographer.
- **Durable context routed:** Yes — four out-of-scope observations named rather than acted
  on, and the two I added are recorded as engine triage candidates on the survey.

## Reconciliation check

No divergence from the recorded architecture that Commander must reconcile. The one
structural change — `examples` becoming a mapped package (1 module, 4 entities) — is
reflected in `map/INDEX.md` and freshness passes.

The `.gitignore` exception is defensible as written. Root `.gitignore:8` states "Engine
journals are NOT excluded - they are the tamper-evident audit trail"; the new file departs
from that for `spine.json.journal`, `context/`, `mechanical/` under this one directory. No
test enforces the root rule, the departure is scoped to a throwaway fixture regenerable by
one command, and the reason is written in the file at the site of the departure. I verified
it works: after my drives the side-cars showed as `!!` (ignored), and tracked content stayed
clean.

## Blockers

- **None.**

## Out-of-scope observations

1. **No test exercises the demo's default workspace branch.** Both
   `ShippedDemoDrivesFromAnyDirectoryTests` methods set `SPINE_DEMO_WORKSPACE`
   (`tests/test_shipped_examples_are_portable.py:309`), so the committed default
   `${TMPDIR:-/tmp}/constellation-mcp-demo-$(id -u)` is only asserted for absoluteness,
   never driven. I drove it end to end from `$HOME` and it works, so this is a coverage gap
   rather than a defect. Cheapest fix: one more drive case with the variable unset, pointed
   at a `TMPDIR` the test controls. *(Triage candidate `tc1` on the survey.)*

2. **The expansion test uses a shell the engine does not use on POSIX.**
   `tests/test_shipped_examples_are_portable.py:289` expands via `bash -c`, but the engine
   resolves `sh`. Harmless today — verified identical under `dash` — but it would miss a
   future bashism. Cheapest fix: call `checklist_engine._find_posix_shell()` instead of
   hardcoding `bash`. *(Triage candidate `tc2` on the survey.)*

3. **Fowler, non-blocking — the vacuity floor is spelled two ways.**
   `MIN_SHIPPED_FILES = 3` is a named constant with a comment explaining why it is a floor
   (`:44`), while the sibling guard hardcodes a bare `2` for the same purpose at `:201` with
   no name and no comment. Same concept, and the unnamed one is the easier to weaken by
   accident. A one-line fix whenever this file is next touched.

4. **Fowler, non-blocking — an unused generality in the generator.**
   `make_demo_spine.py:161-164` accepts an optional `argv[1]` target directory, advertised
   at docstring line 6 as "write a copy elsewhere". Nothing exercises it: no test, no README
   instruction, no other caller in tracked content (verified by grep). There is a fair
   counter-argument that it mirrors the archived `make_scratch_spine.py` it replaces.

5. **Pre-existing, confirming the implementer:** `map/ids.jsonl` is tracked but 0 bytes, so
   no map anchor resolves anywhere in this repo. Already a triage candidate on the
   Commander's spine (`tc1`).

6. **A note on state, so nothing surprises you:** the Commander's earlier demo drive had
   left git-ignored side-cars under `examples/mcp-interactive-demo/` (`context/`,
   `mechanical/`, `spine.json.journal`). My own drives regenerated them; I removed them
   during cleanup, so that directory now holds tracked content only. No tracked file was
   affected.

## Workflow Feedback

- **Handoff gaps:** No **`Test mode`** field, which the implementer also reported. I could
  infer it (the Constraints demand a demonstrated red on pre-fix content, which is
  red-then-green), but both of us had to infer the same missing field, which is a sign it
  should be a template requirement rather than a deduction. Separately, the handoff's own
  **Verification commands** block hands the reviewer a command that over-reports:
  `grep -rn ... examples/` returned 3 hits on a machine where the demo had been driven, all
  git-ignored scratch. The implementer had already flagged this and proposed the stable
  form; the handoff still shipped the unstable one. That is worth closing the loop on — the
  first thing a reviewer runs should not be the thing that looks like a failure.

- **Context rediscovered:** Which shell the engine actually uses. The handoff and the
  implementer's notes both point at `checklist_engine.py:883` for the no-`cwd` property, and
  that is accurate, but the *shell selection* eleven lines above it (`_find_posix_shell`,
  `:852-868`) is what decides whether the new test's `bash` matches production — and nothing
  pointed there. It is the difference between a test that guards the real path and one that
  guards a neighbouring one.

- **Instructions improvised around:** Two.
  (1) **The bound spine was the Commander's, not mine** — `SPINE_FILE` pointed at
  `.agent-work/cleanup-a-door/spine.json`, type `gated`, lease held by
  `commander-cleanup-a-door` with `execute` active. The reviewer skill says "do not author a
  survey of your own when a spine is already bound", but driving that one would have meant
  closing the Commander's own gate, and `spine_survey_result` refuses a gated plan anyway. I
  read the binding as the reach-up handle for `spine_halt block` and authored my own survey
  at the skill's documented convention path. This is the **identical** friction the g2
  implementer reported in its own feedback #2 — two crews in one gate improvising around the
  same sentence is a skill defect, not two coincidences.

  **The same root cause has a second, sharper symptom: the stop hook.** On finishing — survey
  consolidated, lease released, result artifact written — the `Stop` hook fired
  `SPINE MID-FLIGHT: gate execute is still open`, quoting the *Commander's* `execute`
  imperative and instructing me to reload the commander skill, rewrite `STATE_NOTE.md` and
  dispatch crews through `run_crew.py`. That is my parent's gate, not mine. The hook resolves
  `SPINE_FILE` and reports on whoever's spine is bound, with no notion of which role the
  current process is — so **every dispatched crew will be told it abandoned a run at the exact
  moment it correctly completed one.** The instruction it offers as the honest exit ("use the
  engine's `block` verb to bubble the blocker to the parent") is also unavailable: the lease on
  that file is held by `commander-cleanup-a-door`, so every mutating verb from my session is
  refused on ownership, and taking it by force to inject a blocker into my parent's run would
  be well outside review authority. I did neither, and reported instead. Suggested fix: the
  hook should compare the bound spine's `engine_session.session_id` against the current
  session and stay silent when they differ — a crew that does not own the lease cannot be the
  one abandoning the run.
  (2) **`FOWLER_PASS.json` is pinned to one path per work-id**, but a work-id has many
  gates. g1's record was already there. I copied it to
  `.agent-work/cleanup-a-door/g1-review/FOWLER_PASS.json` before writing mine, so the g1
  audit trail is not lost — but the template's postcondition command resolves the path from
  `<work-id>` alone, so the second gate to run silently overwrites the first. A `<gate>`
  segment in that path would fix it.

- **What would have made this easier:** Have the handoff state the **restore recipe** for a
  staged change, not just the warning. It correctly says `git stash` and
  `git checkout HEAD --` will not behave and to "copy files aside first", but the reliable
  form is specific and worth spelling out once:
  `git show :<path> > backup` to capture the index blob, `git ls-files -s <paths>` to pin
  the OIDs, then restore and `git add`, and diff the manifest to prove you put it back. I
  had to derive that, and getting it wrong destroys the gate's work — `git checkout <sha> --`
  overwrites the index as well as the worktree, so criterion 3's own recipe is the dangerous
  one.

## Return status

`complete`
