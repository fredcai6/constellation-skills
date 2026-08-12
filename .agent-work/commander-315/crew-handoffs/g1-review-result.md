# Review Result

Independent review of `epic-568/c1-check-cwd` (issue #315), commits `b513e6d0..69c503d6`.
Reviewer survey driven through the engine at `.agent-work/commander-315/g1-review/review.json`
(lease `g1-reviewer-01476478`), all 7 items visited and recorded.

## Assigned Gate

`g1` — independent review of the commander-315 branch against seven stated close criteria.

## Result

`APPROVE`

The central claim is true and I reproduced it. The guard is real and I drove it red
myself. Production is untouched. The suite is green. The numbers in the result document
match what I measured, in every cell I checked. Three minor findings, none blocking.

## Evidence I produced

Everything below is my own run in `/home/tommy/projects/constellation-skills-wt/epic-568-315`,
not a restatement of the result document.

### 1. The central claim — VERIFIED

`scripts/verify_worktree_isolation.py` reads the ambient cwd as the check's **subject**:

```python
def current_toplevel() -> str:
    return _git("rev-parse", "--show-toplevel")     # line 122-123
```

`_git()` calls `subprocess.run(["git", *args], ...)` with **no `cwd=`**, so `--show-toplevel`
resolves against whatever directory the process is standing in. `main()` then does
`ok, reason = check_here(actual, args.here)`, and `check_here` is a pure equality on
normalized paths. There is no path-base semantics anywhere in `--here`: cwd *is* the thing
being measured.

The other half of the claim — that a `base_dir`-derived cwd resolves to the same root the
gate compares against — also holds. `scripts/init_work_area.py:148` substitutes
`<repo-root>` -> `Path(root).resolve().as_posix()`, and the shipped check is
`python scripts/verify_worktree_isolation.py --here <repo-root>`. When a Commander
instantiates its spine inside its own worktree, EXPECTED is that worktree root, which is
exactly what a walk up from `<worktree>/.agent-work/<wid>/` finds. The comparison becomes
`X == X`. (In the abnormal case where init ran elsewhere, the gate becomes a permanent
false-red instead — either way it stops measuring where the agent is standing.)

Empirically, `bash .agent-work/commander-315/s1_production.sh`:

```
topology: main=/tmp/tmp.PKtbmFP0Ur/main   worktree=/tmp/tmp.PKtbmFP0Ur/wt
the gate asserts the agent is standing in /tmp/tmp.PKtbmFP0Ur/wt
the LAUNCHER will stand in /tmp/tmp.PKtbmFP0Ur/main -- the wrong place

--- engine_before.py, launched from /tmp/tmp.PKtbmFP0Ur/main ---
REFUSED: init: preconditions unmet ['c0'] ...

--- engine_after.py, launched from /tmp/tmp.PKtbmFP0Ur/main ---
init -> in-progress
```

Reproduced verbatim. The obvious fix disarms a shipped safety gate. **Not a block — this
is the finding the PR rests on, and it stands.**

### 2. The new tests are a real guard — VERIFIED, independently

Unpatched: `py -m pytest tests/test_worktree_precondition_wiring.py -q` -> `7 passed in 0.22s`.

I did **not** reuse the Commander's patcher. I copied `scripts/`, `skills/` and the test file
into a shadow root under my scratchpad, confirmed it green there (`7 passed`), then wrote my
own naive fix — a `.git`-walking `_reviewer_repo_root(base_dir)` helper, `cwd=` threaded onto
the one `subprocess.run`, `base_dir` threaded through the one call site — and re-ran:

```
E       AssertionError: 'c0' not found in '...init -> in-progress\n' : gate did not refuse
FAILED tests/test_worktree_precondition_wiring.py::IsolationGateSurvivesThroughTheCLI::test_gate_refuses_launcher_standing_in_the_main_checkout
1 failed, 6 passed in 0.24s
```

Two things worth stating separately:

- The guard is **non-vacuous**. It goes red under the fix it exists to trap.
- The **5 pre-existing tests stayed green**, including
  `test_start_refused_on_mismatch_then_succeeds_once_fixed`. That independently confirms
  section 4's claim that the old alarm would not have sounded. This is the strongest single
  argument for the PR: without this guard, the disarming fix lands on a fully green suite.

The guard also asserts persisted state (`tasks.init.status == "pending"`), not just a
message string — consistent with `docs/agents/CREW_CONTEXT.md:93-97`.

Repo engine left pristine: `git status --porcelain scripts/` prints **nothing**.

### 3. No production behavior changed — VERIFIED

- `git diff main...epic-568/c1-check-cwd -- scripts/ skills/` -> **empty**.
- `git log main..HEAD -- scripts/hooks/spine_rail.py scripts/agent_work_root.py` -> **no commits**.
- Diff is confined to `tests/test_worktree_precondition_wiring.py` (+107),
  `map/INDEX.md` (mechanical entity counts), `notes-1.md`, and the
  `.agent-work/commander-315/` run record.
- `git worktree list` shows only the two real worktrees — the test's `git worktree add`
  leaves no registration behind.

### 4. Suite green — VERIFIED

`py -m pytest tests/ -q -p no:randomly`:

```
2934 passed, 5 skipped, 1121 subtests passed in 120.56s (0:02:00)
```

Baseline 2932 + exactly the 2 new tests. The diff contains no other test changes, so the
arithmetic is closed.

### 5. The repro is honest — VERIFIED

`py .agent-work/commander-315/repro_315.py` -> `EXIT=1`, and it demonstrates both halves it
claims: `gA` advanced on a decoy file that exists only in the launcher's cwd (fail-open), and
`gB` refused on `real_evidence.txt` that genuinely exists in the project (false-red). The
false-red half is not in the filed issue and is a real addition.

### 6. Enumeration reproducible — VERIFIED, zero discrepancy

| corpus | total | R1 | R2 | cwd-dependent | clean | doc says |
|---|---|---|---|---|---|---|
| `skills/*/templates/*.json` | 22 | 6 | 11 | **17** | 5 | 22 / 6 / 11 / 17 / 5 — match |
| `.agent-work/templates/*.json` | 21 | 5 | 10 | **15** | 6 | 21 / 5 / 10 / 15 / 6 — match |

I also re-derived the source total with my own parser (walking every task's
`preconditions`/`postconditions` for `kind == "command"`): **22**, agreeing independently.

### 7. The result document does not overclaim — VERIFIED

I could not find a number that disagrees with what I measured, nor a claim I failed to
reproduce. Section 4's "no template rewrite recovers it" is correctly reasoned: the engine
would have destroyed the input the check reads, so no edit to the check's *text* can restore
a signal that no longer exists. Section 6's "filed 5, measured 17" is supported, and it is
appropriately careful to say the nearest defensible reading of "five" is 6. Section 9's
"scope of the null" honestly separates what was exercised from what was only read.

One place I would soften, in the code rather than the document — see Finding 2.

## Handoff compliance

The branch did **not** deliver the filed fix, and that is the correct outcome rather than a
shortfall. `g1-implementer-handoff.md` lists "you conclude the resolution target is wrong"
as an explicit stop condition. The run hit it, measured why, and escalated with
`authority_needed: admiral`. The spine agrees: `init`/`context`/`understand` complete,
`plan` **blocked** with the measured blocker, `execute` onward never started, 6 triage
candidates attached, lease released so a resuming Commander can claim without `--force`.

## Scope drift

None. See evidence item 3.

## Evidence verdict

Satisfied, and then some. The load-bearing claim was proven through the real production path
(`main()` -> `base_dir = path.parent` -> `_check_condition` -> `_run_check_command`) in a real
main-checkout-plus-linked-worktree topology, not through an in-process shortcut. The guard was
shown red-first. `docs/agents/CREW_CONTEXT.md:88-92` ("a check that cannot fail is
indistinguishable from one that passed") is honoured twice — once by the Commander, once by me.

## Code/doc quality

Fowler pass recorded at `.agent-work/commander-315/FOWLER_PASS.json`;
`scripts/verify_fowler_pass.py` exits 0 (`smells=12, flagged=[], overridden=['duplicated-code',
'comments-as-deodorant']`). Ten smells absent, two overridden with logged standards:

- **duplicated-code** — the new fixture repeats `EngineDeliberateBreakage`'s git/spine setup
  by ~30 lines. Overridden: the two fixtures are deliberately independent along the exact
  `base_dir` axis the guard measures. A shared builder later threaded with `base_dir` would
  move both together and recreate the blind spot this class exists to close.
- **comments-as-deodorant** — 20-line class docstring. Overridden: the handoff constraint
  asks for docstrings that carry *why*, and the rationale is this guard's entire payload. A
  trap-marker nobody can read is a trap that gets deleted.

No production code in the diff to smell-test.

## Map impact verdict

- **Evidence supports claimed change:** yes. The claimed change is "guard only, production
  untouched", and both halves are verified by command.
- **Constraints not violated:** yes. `preserve-no-posix-shell-behavior` is trivially intact
  (the engine is byte-identical); both forbidden files are untouched by any commit.
- **Notes match the diff:** yes. Section 8 claims map impact "none" because the architecture
  map is `DEGRADED-UNPARSEABLE` (no `docs/architecture/`, empty `map/ids.jsonl`), and it
  correctly distinguishes that from `map/INDEX.md`, which is the mechanical code-map index.
  The `INDEX.md` regeneration is genuinely covered — 47 map/index tests pass.
- **Decision candidates surfaced:** yes, and this is the run's main output. Section 11 gives
  the Admiral three named options with costs and a recommendation.
- **Durable context routed:** yes. Six triage candidates on the spine, including the two
  most valuable non-obvious ones (candidate 3: `main()` never resolves `--file`, so
  `base_dir` is relative on the CLI form every crew member is told to use; candidate 5:
  three different cwd rules coexist inside one `_check_condition` dispatch).

## Reconciliation check

No divergence for Commander to reconcile. The architectural finding — that command checks
come in two kinds, path-relative and environment-observing, and the engine has no contract
distinguishing them — is routed **out** to the Admiral rather than silently absorbed. Prior
art stays consistent: `docs/CHECKLIST_SCHEMA.md:39-41` and `scripts/init_work_area.py:129-134`
still describe the no-cwd behaviour as present fact, which remains true precisely because
production did not change.

## Blockers

None.

## Findings, ranked

**Finding 1 (minor, actionable now).** `.agent-work/commander-315/crew-handoffs/g1-implementer-handoff.md`
is committed and carries, in bold, *"Resolution target — already decided, do not re-litigate:
`cwd` resolves to the repo/worktree root"* — the very target this run measured to be unsafe.
It has no supersession marker (I grepped for supersede/obsolete/blocked; nothing). It is the
only file in `crew-handoffs/`, so it is the first thing a resuming implementer reads, and it
instructs them to build the disarming fix. The guard would catch them, but only after the
work. One header line pointing at `COMMANDER_RESULT.md` section 4 closes this.

**Finding 2 (minor).** The new class's docstring says: *"if you are here because this test
went red while making command checks cwd-independent, the test is right and the change is
wrong."* That is stated more absolutely than the guard can support. Under the result
document's own **recommended** option 1 (engine exports `SPINE_LAUNCH_CWD`,
`verify_worktree_isolation.py` gains `--from`), this test's fixture still writes the bare
`--here EXPECTED` form — so it could go red for a stale-fixture reason while the change is
correct. Either name both cases in the docstring, or design `--from` to default to
`SPINE_LAUNCH_CWD` so the bare form keeps working. Worth fixing because the sentence is
aimed at exactly the agent who will implement the real fix.

**Finding 3 (trivial).** `IsolationGateSurvivesThroughTheCLI` hard-requires `git` **and**
`git worktree add` on the runner, with no `skipIf`. The file already shells to git, so the
git dependency is not new, but the worktree dependency is. A CI lane without git errors
rather than skips.

## Assessment: was guard-without-fix the right call?

**Yes.** I went looking for an in-scope fix rather than assuming there wasn't one, and there
isn't.

The allowed scope was `scripts/checklist_engine.py` and `tests/test_checklist_engine.py`.
Any fix that preserves `init.c0`'s signal must give the isolation check a second input — the
launcher's original cwd — because that information is destroyed the moment the engine sets
`cwd=`. Delivering that input requires either `scripts/verify_worktree_isolation.py` to learn
a new flag (outside the two allowed files) or the template's check text to change (explicitly
excluded: "a separate gate owns the corpus"). An engine-side env export alone would be inert:
the script would still read `os.getcwd()` and still be tautological. So the working fix is
genuinely outside the wave's latitude, not merely inconvenient.

I tested one narrower hack the Commander did not consider — set `cwd=` on **postconditions**
only, leaving preconditions alone, which would preserve `init.c0` since it is a precondition.
It does not survive contact. Splitting the corpus by slot gives: 3 preconditions, 19
postconditions, and the two cwd-dependent `verify_state_note.py` checks are *preconditions*,
so they would stay broken. It would also be an arbitrary, undocumented rule that leaves the
engine's cwd contract incoherent — the same identity check could be authored in either slot.
A worse outcome than blocking.

The deeper point in the Commander's favour: the decision it was told not to re-litigate was
itself the product of a measurement that **structurally could not see** the failure. The
enumerator classifies by path-token shape and argparse default; `cwd`-as-identity is a third
class neither probe models. "17 of 22, zero repairs" read as complete while carrying a false
negative in the highest-consequence row. When a frozen decision's basis is falsified, stopping
is the correct move, and the handoff said so.

What makes this land rather than merely stop is that the guard is a **real artifact**, not a
consolation prize. Before this branch, the disarming fix passed the whole suite. After it, the
suite refuses. That is the durable output of the run, and it is worth more than the one-line
change would have been.

Two caveats I will state so the approval is not read as broader than it is. First, `init.c0`
is a weaker signal than its prose suggests — it samples the launcher's cwd at a single moment,
so an agent that stands in the right place for `start init` and works elsewhere afterwards
passes it. Protecting it is still correct (a weak signal beats a tautology), but nobody should
treat it as proof of sustained isolation. Second, #315 remains **open and unfixed**; the
guard makes the trap visible, it does not remove it. Finding 1 matters for exactly that reason.

## Out-of-scope observations

- Result-document section 5 already self-flags the `gh pr list` check as an undercount (its
  `git -C <repo-root>` half is pinned, its `gh` half resolves the repo from cwd). Correct call,
  and worth carrying into whichever issue inherits the fix.
- Triage candidate 3 on the spine — `main()` never resolves `--file`, so `base_dir = path.parent`
  is relative whenever `--file` is — is the highest-value non-obvious find in this run. Any
  future `base_dir`-derived path walk silently no-ops on the CLI invocation form the skills
  instruct every crew member to use. It deserves its own issue regardless of how #315 is ruled.
- Ironic and real: this survey's own `r6-fowler` postcondition is
  `python scripts/verify_fowler_pass.py .agent-work/<work-id>/FOWLER_PASS.json` — an R1
  cwd-dependent check. It passed only because I happened to be standing at the repo root.

## Workflow Feedback

- **Handoff gaps:** the review task said "run `py -m pytest ...` (expect 7 passed)" and
  "confirm they go RED under the naive fix", but gave no instruction for *where* to apply the
  naive patch while honouring "work read-only; do not modify files". Those two directives
  collide. I improvised a shadow root in the scratchpad (copying `scripts/`, `skills/` and the
  test file) so the repo tree was never touched — which is better evidence than patching and
  restoring anyway, since it removes any chance of leaving the engine dirty. Say so explicitly
  next time; a less careful reviewer patches in place and races the `git status` check.
- **Context rediscovered:** whether `<repo-root>` in the shipped check resolves to the worktree
  or the main checkout is the hinge of the whole tautology argument, and neither the result
  document nor the mission frame cites where the substitution happens. I had to find
  `scripts/init_work_area.py:148`. One line — "`<repo-root>` is `Path(root).resolve()`, and
  `root` is the directory init ran in" — would have saved the dig and would have strengthened
  section 4.
- **Instructions improvised around:** the reviewer skill says to instantiate the survey at
  `.agent-work/<work-id>/<gate>-review/review.json`, and the Fowler postcondition resolves its
  record path from `<work-id>` alone. With `work-id = commander-315` those two conventions
  disagree about depth: the survey sits one level deeper than the Fowler record. The engine's
  context capture then wrote `.agent-work/commander-315/commander-315/{context,mechanical}/r0-context.json`
  — a doubled path segment that is now untracked scratch in the worktree. Harmless here, and
  the files are engine provenance so I left them rather than delete them, but a closeout sweep
  will see an orphan. Worth a template fix.
- **What would have made this easier:** ship the naive patch as a standalone, committed script
  (`.agent-work/commander-315/naive_fix.py` applying to a *copy*) alongside `s1_production.sh`.
  The Commander clearly built one; it lives inline in a heredoc inside the shell script. As a
  separate file it becomes re-runnable evidence any future reviewer can point at the guard,
  rather than something each reviewer re-derives.

## Return status

`complete`
