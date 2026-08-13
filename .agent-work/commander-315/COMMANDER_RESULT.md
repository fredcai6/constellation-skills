# commander-315 — result

**Issue #315** — engine: command-kind checks inherit the launcher's cwd.
**Branch** `epic-568/c1-check-cwd` · **PR** https://github.com/fredcai6/constellation-skills/pull/576

## 1. Verdict

**Blocked on a decision outside latitude, with the reason measured.** The filed
defect is real and reproduces on both halves. The fix as scoped **cannot land**:
forcing a command check's cwd disarms the shipped gate that proves a Commander
is working in its own worktree. Landed instead: the regression guard that makes
that trap visible. The fix is floated.

## 2. Worktree isolation

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
     --here /home/tommy/projects/constellation-skills-wt/epic-568-315
worktree OK: in /home/tommy/projects/constellation-skills-wt/epic-568-315
EXIT=0
```

## 3. The before/after repro

`.agent-work/commander-315/repro_315.py`. A real git project holds the spine at
`proj/.agent-work/w1/spine.json`; the launcher stands in an unrelated `decoy/`.
Two gates, both repo-root-relative: `gA` names a file that exists **only** in
the launcher's cwd, `gB` names a file that exists **in the project**.

**BEFORE (current main, `3e4e07a3`)** — `py .agent-work/commander-315/repro_315.py`, exit **1**:

```
--- gate gA: `test -f decoy_evidence.txt` (file exists ONLY in launcher cwd) ---
    advanced = True   (want False: the gate must REFUSE)
    gA -> complete

--- gate gB: `test -f real_evidence.txt` (file exists in the PROJECT) ---
    advanced = False   (want True: the gate must PASS)
    REFUSED: gB: postconditions unmet ['c1']

REPRO RESULT: FAIL -- issue #315 reproduces
  * FAIL-OPEN: a decoy file in the launcher's cwd satisfied gate gA
  * FALSE-RED: the project's own real_evidence.txt was invisible to gate gB
```

The **false-red** half is not in the filed issue. The defect is not only
permissive; it also fails gates that should pass.

**AFTER** — deliberately **not produced**, because the change that produces it
breaks something worse. Section 4 is that measurement. Per the launch order's
honest-null clause, this is the measured negative on the stated question, with
what was tested and what was not stated in section 9.

## 4. Why the fix cannot land as scoped

`scripts/verify_worktree_isolation.py --here EXPECTED` runs
`git rev-parse --show-toplevel` **from the ambient cwd** (`current_toplevel()`,
line 122) and compares it to EXPECTED. **cwd is the subject of that check, not a
path base.** In a real spine EXPECTED is `<repo-root>`, substituted by
`init_work_area.py` from the same root the spine is written under — so it is by
construction the root any `base_dir`-derived cwd resolves to. Forcing cwd makes
the comparison `X == X`.

Proven through the real engine path — `main()` → `base_dir = path.parent` →
`_check_condition` → `_run_check_command` — in a main-checkout plus linked-worktree
topology with the launcher standing in the wrong one
(`.agent-work/commander-315/s1_production.sh`):

```
topology: main=/tmp/…/main   worktree=/tmp/…/wt   spine=/tmp/…/wt/.agent-work/w1/spine.json
the gate asserts the agent is standing in /tmp/…/wt
the LAUNCHER stands in /tmp/…/main -- the wrong place, which the gate exists to catch

--- engine_before.py (unmodified), launched from /tmp/…/main ---
REFUSED: init: preconditions unmet ['c0']       <-- gate CATCHES it

--- engine_after.py (naive cwd fix), launched from /tmp/…/main ---
init -> in-progress                             <-- gate DISARMED
```

This is the `init.c0` precondition on the shipped `COMMANDER_SPINE` — the same
gate that produced this run's own first piece of evidence. Under the fix it
would have been meaningless.

**No template rewrite recovers it.** The engine would have destroyed the input
the check reads. Resolving this needs an engine-to-check contract for
environment-observing checks — a schema flag, or the launcher's cwd passed into
the check environment. That is an architecture change, outside this wave's
latitude.

**The alarm would not have sounded.** `tests/test_worktree_precondition_wiring.py`
`::test_start_refused_on_mismatch_then_succeeds_once_fixed` calls
`E.start(cl, "init")` directly with **no `base_dir`**, so it takes the
`base_dir is None` path and stays green while production is disarmed.

## 5. Blast-radius enumeration, by command

Enumerator committed at `.agent-work/commander-315/enumerate_checks.py`. It parses
each checklist JSON, walks every `check` with `kind == "command"`, and classifies
the command text.

```
py .agent-work/commander-315/enumerate_checks.py $(git ls-files 'skills/*/templates/*.json')
py .agent-work/commander-315/enumerate_checks.py $(git ls-files '.agent-work/templates/*.json' | grep -v '/.baseline/')
```

Enumerated over: the **shipped source corpus** `skills/*/templates/*.json` (what
installs to users) and this project's **installed mirror**
`.agent-work/templates/*.json`. Archived spines under `.agent-work/archive/` were
swept separately for the `cd`-prefix count only.

| corpus | command checks | R1 literal-relative | R2 cwd-defaulting script | cwd-dependent | clean |
|---|---|---|---|---|---|
| `skills/*/templates/*.json` | **22** | 6 | 11 | **17** | 5 |
| `.agent-work/templates/*.json` | **21** | 5 | 10 | **15** | 6 |

Two classes, because the second is invisible to a grep:

- **R1** — a literal relative path token in the check text (`scripts/x.py`,
  `.agent-work/<work-id>/y.json`, `--store-root episodes`).
- **R2** — no relative token, but the check invokes a script whose project root
  **defaults to cwd**, without pinning `--root`. Measured by reading each
  script's argparse default: `init_work_area.py`, `verify_state_note.py`
  (`default=Path(".")`), `verify_cycles.py` (`default="."`),
  `verify_spec_confirmed.py` (`default="."`), `verify_iterative_role_artifacts.py`
  (hardcoded `Path.cwd()`, no `--root`), `map_orient.py` (unless `--root` passed).

### Disposition of every hit

| hit | disposition |
|---|---|
| 6 × R1 in the source corpus | **ruled correct** under a repo-root resolution — all are authored repo-root-relative. Not repaired: the resolution change they would need is blocked. |
| 11 × R2 in the source corpus | **ruled correct** under a repo-root resolution, same reason. Recorded as a triage candidate: pinning `--root` in the templates would remove the dependence at the authoring side regardless of what the engine does. |
| `COMMANDER_SPINE init.c0` (`verify_worktree_isolation --here`) | **RULED NOT REPAIRABLE.** It is an identity check, not a path-relative one. Guarded by a new regression test instead. This is the blocker. |
| 2 × `map_orient.py --root <repo-root>` | clean — root pinned absolutely. |
| 2 × `<exact test command>` | unfilled placeholder the authoring role supplies per run; not measurable from the template. |
| 1 × `gh pr list` check | counted clean by the tool, **flagged as an undercount**: its `git -C <repo-root>` half is pinned, its `gh` half resolves the repo from cwd. |
| **394** checked-in checks with a `cd <abs> &&` prefix | **inert** under any engine `cwd=` — a shell `cd` runs after `cwd=` takes effect and overrides it. `scripts/generate_spine.py:475,482,496,499,595` emits that prefix for everything it generates. |

**Zero repairs were made**, because zero checks are authored spine-dir-relative
(`grep -cE '\.\./|spine\.json|gauge\.json'` over every R1/R2 hit → **0**) and the
one check that genuinely breaks cannot be fixed by editing its text.

## 6. Was "five" right?

**No. Filed: 5. Measured: 17** cwd-dependent command checks in the shipped source
corpus of 22.

If "five" was counting only literal relative path tokens, the nearest defensible
number is **6**, and that reading misses all 11 R2 cases — the ones no reader
finds by grepping for a slash. The filed number understates the exposure by
roughly 3×.

It also mis-frames the problem. The issue title says "silently fragile," which
describes the R1/R2 classes. The check that actually blocks this issue is
neither: it is **silently strong** today and would become silently useless.

## 7. Suite evidence

| command | before | after |
|---|---|---|
| `py -m pytest tests/test_checklist_engine.py -q` | 441 passed, 140 subtests | unchanged (engine untouched) |
| `py -m pytest tests/ -q -p no:randomly` | 2932 passed, 5 skipped, 1121 subtests | **2934 passed, 5 skipped, 1121 subtests** |
| `py -m pytest tests/test_worktree_precondition_wiring.py -q` | 5 passed | **7 passed** |

The guard proven red-first against the naive fix:

```
$ (naive cwd fix applied to the engine) py -m pytest tests/test_worktree_precondition_wiring.py -q
FAILED ...::IsolationGateSurvivesThroughTheCLI::test_gate_refuses_launcher_standing_in_the_main_checkout
AssertionError: 'c0' not found in '... init -> in-progress' : gate did not refuse
1 failed, 6 passed
```

Engine restored to pristine afterwards (`git diff --stat scripts/checklist_engine.py` empty).
`map/INDEX.md` regenerated for the added entities, as its freshness test demands.

## 8. Map impact

**None, as expected.** `map_orient.py` returns `DEGRADED-UNPARSEABLE`, anchor
count 0; `docs/architecture/` is absent, `map/INDEX.md` carries no citable anchor
id and `map/ids.jsonl` is empty. Discharged at the context step with three
hash-pinned substitutes (`docs/CHECKLIST_SCHEMA.md`,
`docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`);
receipt at `.agent-work/commander-315/map-orientation.json`; frame verified
`FRAME-OK`. The blast radius was enumerated by command precisely because the map
could not supply it.

`map/INDEX.md` was regenerated, but that is the mechanical code-map index, not
the architecture map.

## 9. Scope of the null — what was and was not tested

**Tested:** the fail-open and false-red halves, in a real git project, through
the CLI; the disarming of `init.c0`, through the real `main()` path, in a real
main-checkout plus linked-worktree topology; every command check in both shipped
template corpora, by command; the full suite twice at baseline and once after.

**Not tested:** Windows (`no-posix-shell` path unexercised — it is untouched, but
untouched by inspection, not by run); the MCP door path (`spine_status` never
confirmed as naming this run's gates, so the CLI was used throughout, per the
launch order); behaviour under `GIT_CEILING_DIRECTORIES` / `GIT_DIR` /
`safe.directory`, where a filesystem `.git` walk and `git rev-parse` disagree;
the eval-harness configuration (`run_skill_eval.py` builds a **non-git**
workspace root, so a `.git` walk would sail past it into the tool's own repo) —
identified by reading, not exercised.

## 10. Triage candidates

Six recorded in `.agent-work/commander-315/spine.json`:

1. **Identity checks need an explicit engine contract** — the blocker itself.
2. **11 of 22 shipped checks are cwd-dependent only via a `--root` that defaults to cwd** — pinning them in the templates removes the dependence at the authoring side, whatever the engine does.
3. **`main()` never resolves `--file`**, so `base_dir = path.parent` is relative whenever `--file` is; any `base_dir`-derived path walk no-ops on the CLI form every crew member is told to use.
4. **`generate_spine.py` emits `cd <repo-root> &&` on every generated command**, and 394 checked-in checks already carry it; whether the generator keeps emitting it is an open decision any cwd fix must settle.
5. **Three cwd rules coexist in one `_check_condition` dispatch** — `command` inherits the launcher's cwd, `git-change-policy` uses `base_dir`, `load_config` resolves `config_ref` against `Path.cwd()` first. `load_config` decides `rework_cap` and the trip band, so a spine driven from elsewhere loads its rigor config from a stranger's directory.
6. **Two contract docs state the no-cwd behaviour as present fact** (`docs/CHECKLIST_SCHEMA.md:39-41`, `scripts/init_work_area.py:129-134`) and cite **#341** as its tracking issue. No test asserts either, so they go stale silently the day a cwd fix lands — and nobody has said whether #315 closes #341.

## 11. What the Admiral must rule on

1. **Engine exports the launcher's cwd into the check environment** (e.g. `SPINE_LAUNCH_CWD`) and `verify_worktree_isolation.py` gains an explicit `--from`. Preserves the signal and fixes path resolution. Costs: a new engine-to-check contract, a script interface change, a template edit.
2. **A schema flag marks environment-observing checks exempt** from relocation. Cleaner conceptually, larger blast radius (schema, validator, generator, docs).
3. **Close #315 as measured-not-worth-it.** Defensible on the numbers: 394 of the checked-in checks are already `cd`-anchored and unaffected, the benefit is confined to ~17 hand-authored template checks, and the cost includes disarming the isolation gate.

**Recommendation: (1).** It is the only option that fixes the filed defect
without weakening a gate, and it is bounded. But it is materially bigger than
"add `cwd=`" — enough that **wave 1 should probably split**: the guard (landed
here) from the contract (a new issue).

## 12. Workflow feedback — observed, not prescribed

- **The cold plan critic is what saved this run.** The frame had already
  converged on "repo root, zero repairs" with a measurement behind it, and the
  measurement was correct as far as it reached. The critic found the row the
  enumerator was structurally unable to see, because the enumerator classified by
  *path-token shape* and *argparse default* and the blocking check belongs to a
  third class — cwd-as-identity — that neither probe models. The lesson observed:
  an enumerator's confidence is bounded by the classes it can represent, and
  "17 of 22, zero repairs" read as complete while carrying a false negative in
  the highest-consequence row.
- **Waiting on the critic cost real time with nothing to do.** It ran ~9 minutes
  and fanned out its own Explore subagents. Running headless, ending the turn is
  fatal, so the wait was filled with baseline suite runs that were useful but not
  on the critical path. Roughly a third of the run's wall clock was spent
  manufacturing work to stay alive while blocked on a subagent.
- **`flag-candidate` refused my first six calls** because I passed `--note`,
  which is what `attest` takes; it wants `--from` and `--statement`. The refusal
  named the right flags, so it cost one round trip, not more.
- **The frame verifier reads `decision:<slug>` as a map-anchor citation.** Quoting
  the launch order's own pre-ruling ids in the mission frame made `verify-frame`
  refuse, since a DEGRADED orientation has no map for them to be members of.
  Rewording the same references as plain quoted strings passed. The launch
  order's vocabulary and the frame checker's anchor grammar collide.
- **The gauge printed `CONTEXT 9% (>= soft)`** and advised handing off, from the
  first `current` call onward, while actual context use was low. It was advisory
  and I proceeded, but a hand-off prompt that fires at 9% is noise that a less
  confident run might have obeyed.
- **The launch order's warning about hook code not being fenced turned out not to
  bite**, because no engine behaviour was changed. Had the fix landed, the
  fresh-process `CLAUDE_PROJECT_DIR` validation it demands would have been
  necessary — and the S1 harness built here (a real main-checkout plus
  linked-worktree topology driven through the CLI) is the shape that validation
  would need.

## 13. Engine state

Spine `.agent-work/commander-315/spine.json`: `init` and `context` and
`understand` complete; `plan` **blocked** with the blocker above and a stated
next action; `execute` onward never started. Six triage candidates attached.
The lease was released after blocking, so a resuming Commander can claim it
without `--force`.
