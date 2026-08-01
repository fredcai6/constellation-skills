# Verdict — commander-228 · issue #228 (epic-226 item B)

**PR:** [#240](https://github.com/fredcai6/constellation-skills/pull/240) — `feat(install): probe host interpreter at install time, stop hardcoding py (#228)`
**Branch:** `issue-228` (commit `faf7fb6`) · base `main` @ `83a31b1`
**Worktree:** `C:/Programs/constellation-wt-228` · **Model:** sonnet throughout (commander + crew), no Fable at any tier
**Findings file:** `.agent-work/epic-226/evidence/findings-228.md`

**This is a continuation run.** The original commander (`cmd-228`) stalled mid-`g1-review`
after implementing the full change and was confirmed stopped by the Admiral. I
(`commander-228-b`) force-reclaimed the engine lease on both `spine.json` and the
nested `g1-review/review.json` child checklist and resumed from engine state — see
"Predecessor vs. this session" below for the exact split.

---

## Verdict per sub-item

| # | Item | Verdict |
|---|---|---|
| Interpreter-name **selection** (`_platform_interpreter`) | **HONEST NULL — already shipped**, pre-#228. Untouched in behavior (docstring only). |
| SKILL.md-body **stamping** (`rewrite_installed_skill_paths`'s `"python <"` rewrite) | **HONEST NULL — already shipped**, pre-#228. Now driven by the threaded resolution instead of an unconditional `_platform_interpreter()` call, same rewrite mechanics. |
| Real host **probe** (`py`→`python3`→`python`, each `--version` with an explicit 5s timeout) | **SHIPPED** — `probe_host_interpreter()` / `_probe_interpreter_candidate()`. |
| Three-way **fallback chain** + os.name-default last resort | **SHIPPED** — `resolve_interpreter()`. |
| Per-skill **sidecar** (`<skill-install-dir>/interpreter.json`) | **SHIPPED** — `{interpreter, candidates, resolved_via}`, per-skill shape chosen and recorded in `MISSION_FRAME.md`. |

PR-7 re-verification (done by the predecessor at the `understand`/findings step, independently
re-confirmed by me during review): interpreter-name selection and body-stamping were real,
shipped, pre-#228 mechanisms — the launch order's own first-pass finding held exactly. All
effort went to the three genuinely-missing sub-items.

---

## Acceptance evidence (from the launch order's Acceptance line)

**"Installer test asserting the stamped interpreter resolves on the install host"**
`InterpreterProbeTests.test_probe_resolves_a_real_invocable_interpreter_on_this_host` — drives
the real (non-mocked) probe, then independently re-drives the same real `subprocess.run`
call to confirm the returned name is genuinely invocable right now, not just first-by-construction.

**"A simulated `py`-less install names a working interpreter"**
`InterpreterProbeTests.test_probe_falls_through_to_next_candidate_when_py_is_unresolvable` —
genuinely mutates the ambient `os.environ["PATH"]` (via `mock.patch.dict`) to a real,
dynamically-discovered PATH entry on this host that carries `python3`/`python` but no `py`
launcher — **not** a hand-set fixture, **not** a restricted `subprocess.run(env=...)` override
(the implementer verified empirically, two pasted `py -c` transcripts, that Windows
`CreateProcess` resolves an unqualified executable name against the *calling process's real
environment*, not the child `env=` dict — a naive `env=` override would have silently passed
even with a completely broken probe). I independently re-read this test and re-ran it; it was
**not skipped** on this host, confirming a real py-free PATH entry existed and the fallthrough
was genuinely exercised.

**"Existing install/fingerprint tests green (mind #197's path-invariant `corpus_id` behavior)"**
- `tests/test_install_constellation.py -q`: **57 passed, 226 subtests, exit 0** (re-run by me).
- `tests/test_run_skill_eval.py::test_corpus_id_install_path_invariant`: looped **6x** by the
  implementer (flake-proofing since the probe is now a real subprocess call, per the cold plan
  critic's finding), all green; I independently re-ran it **6 more times** myself during
  `g1-integrate` — all green, no flake.
- Full suite, run three separate times across review/integrate by me, always identical:

```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/ -q
........................................................................ [  7%]
........................................................................ [ 15%]
...................................................... [ 21%]
........................................................................ [ 29%]
........................................................................ [ 37%]
........................................................................ [ 45%]
........................................................................ [ 53%]
........................................................................ [ 61%]
.............................................................. [ 67%]
........................................................................ [ 75%]
........................................................................ [ 83%]
........................................................................ [ 91%]
.............................................s........s................. [ 99%]
......                                                                   [100%]
912 passed, 2 skipped, 244 subtests passed in 42.20s
```
Exit code captured explicitly via `$?` immediately after the run (not inferred from the tail
text): **`EXIT_CODE:0`**.

### Worktree isolation
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-228
worktree OK: in C:/Programs/constellation-wt-228
```

### Sidecar content — independently driven, not just read from the diff
I ran a real (non-mocked) `install_skills()` call against a fresh temp target during
`g1-integrate` and read the actual `interpreter.json` files off disk for 2 installed skills:

```
constellation-admiral -> {'interpreter': 'py', 'candidates': ['py', 'python3', 'python'], 'resolved_via': 'probe'}
constellation-cartographer -> {'interpreter': 'py', 'candidates': ['py', 'python3', 'python'], 'resolved_via': 'probe'}
```
Matches the shape decided in `MISSION_FRAME.md` exactly.

### Threading (never a module-level global) — verified by reading the diff
`install_skills(..., interpreter: InterpreterResolution | None = None)` resolves lazily,
at most once per call, into a local (`resolved_interpreter = interpreter`), never a module
global. `main()` resolves once before its `target_roots` loop and passes the same resolution
into every `install_skills()` call, so a `--agent all` run still probes exactly once. All 3
external callers of `install_skills()` checked for compatibility: `run_skill_eval.py`'s
real-install call passes no `interpreter=` kwarg (resolves fresh once per its own call, no
regression, read-only per exclusion honored); `test_write_a_skill.py` and
`verify_skill_registered.py` both pass `dry_run=True`, which returns before the probe is ever
reached.

### Fowler refactoring pass
Recorded to `.agent-work/archive/2026-07-24-228/g1-review/FOWLER_PASS.json`, rail-verified
(`verify_fowler_pass.py`, exit 0): 12 smells rendered, 2 flagged (non-blocking), 0 overridden.
- `long-parameter-list`: `install_skills()` was already at 7 keyword-mostly params pre-diff;
  this adds an 8th (`interpreter`, keyword-only, defaulted). Out of this issue's sole-file
  scope to restructure.
- `speculative-generality`: `probe_host_interpreter()`/`resolve_interpreter()`'s
  `candidates=`/`timeout=` overrides are never exercised with a non-default value anywhere in
  the diff (production or tests) — cheap, harmless, no current consumer.

---

## Honest nulls

1. **Interpreter-name selection + SKILL.md stamping** — already shipped pre-#228 (see table
   above). Tested: confirmed via `git diff` that `_platform_interpreter()`'s return statement
   is byte-identical, only its docstring changed. Not tested: no attempt was made to redesign
   or replace this mechanism — out of scope by the launch order's own framing.
2. **Cross-run corpus-id determinism over calendar time** — the launch order and
   `MISSION_FRAME.md` both name this as an accepted, non-blocking behavior change: a *real*
   probed interpreter means `corpus_id` can now legitimately drift across calendar time on the
   same host if the user's PATH changes between two install runs days apart (impossible before,
   since `os.name` never changes). Tested: `test_corpus_id_install_path_invariant` (same-point-
   in-time, two paths) stays green, 12 runs total across implementer + reviewer/integrator.
   Not tested: cross-calendar-time drift itself (would require a multi-day fixture; the launch
   order's actual invariant does not require it).

---

## Triage candidates

- **Windows Python Install Manager may interact with `probe_host_interpreter()` in an
  untested way.** While driving this review I found ~136MB of untracked debris in the worktree
  (`Python/` directory + `python_install_20260724163007_33756.log`) left by an earlier `py`
  invocation on this host: the log shows Windows' newer Python Install Manager (bundled with
  recent `py.exe` builds) attempting a network fetch of `index-windows.json` when no runtime was
  registered, failing, and writing partial state into the **current working directory**. This
  predates my session (I did not trigger it) and `py --version` now resolves cleanly on this
  host (verified: real interpreter behind it, `Python 3.12.13`, exit 0), so it did **not**
  affect the shipped tests' correctness. But it raises an untested question for a fresh
  Windows box with `py.exe` present but **no registered runtime**: does `py --version`
  short-circuit safely (print the launcher's own version, exit fast) or does it trigger the
  same install-manager flow — and if so, does it write into the *real install target's* cwd, or
  hang close to/past the 5s timeout? One-line recommendation for a future issue: add a test (or
  at least a manual probe on a clean VM) confirming `py --version`'s behavior when only the
  install-manager stub is present, no real interpreter. Not filed as a GitHub issue per
  Inherited Latitude / PR-8 (stay in lane) — flagging here per the Return Shape's Triage
  Candidates requirement; the Admiral or a human should decide whether it warrants a follow-up
  issue.
- Two workflow-friction observations were banked as lesson candidates (not filed as GitHub
  issues, since both are process/tooling, not code-scope out-of-scope items) — see Workflow
  Feedback below.
- Nothing found touching #219's live threads or #220's surviving items.

---

## Predecessor vs. this session

**Predecessor (`cmd-228`) did, before stalling:**
- PR-7 re-verification and findings (`.agent-work/epic-226/evidence/findings-228.md`).
- Authored `MISSION_FRAME.md` (sidecar-shape decision-it-twice comparison) and `execute.json`
  (cold-plan-critic-adjudicated gate plan).
- Drove `e0-context` and the full `g1-implement` gate: dispatched the implementer crew, which
  wrote the entire `scripts/install_constellation.py` / `tests/test_install_constellation.py`
  diff (uncommitted at handoff) and `g1-implementer-result.md`.
- Started `g1-review`: dispatched the reviewer crew, wrote `g1-reviewer-handoff.md`, and the
  reviewer's survey checklist recorded `r0-context` and `r1-handoff` as pass before the session
  stopped (both re-confirmed, not re-litigated, by me).

**This session (`commander-228-b`) added:**
- Forced lease takeover on `spine.json` and the nested `g1-review/review.json`.
- Drove `r2-scope` through `r6-fowler` of the review survey (including authoring and
  rail-verifying the Fowler pass), consolidated the review to **APPROVE**.
- Drove `g1-integrate`: independent side-effect verification (sidecar content off disk,
  threading via diff read, py-less test genuineness), the 6x flake-proof loop, and the full
  suite run (twice via the engine's command-kind postcondition, once more by hand).
- Drove `reconcile` (reasoned no-op, no architecture map exists), `triage` (zero candidates),
  `review` (run summary), `feedback` (staged the fenced trio — see below), and `archive`
  (commit, push, PR #240, work-area archive move, lease release).

---

## Fenced feedback/archive closeout

`LAUNCH_ORDER-228.md`'s Data Locations section marks the main checkout's whole `.agent-work/`
tree **read-only** for this Commander, carving out only the verdict and findings-file paths.
The durable `AGENT_FEEDBACK.md` / `LESSONS.md` / `CONSTELLATION_FEEDBACK.md` are not among
those carve-outs. Per `constellation-commander-delegated`'s fenced-closeout convention, I
staged the trio + a `FENCE.md` citation under
`C:/Programs/constellation-wt-228/.agent-work/staged-feedback/228/` instead of writing the
durable root directly. `verify_agent_feedback.py 228 --phase feedback` and `--phase archive`
both passed by finding the `FENCE.md` marker and validating the staged trio. **The Admiral
needs to harvest this staged trio into the shared durable `.agent-work/` root** — it will not
happen automatically once the worktree is cleaned up.

Two lesson candidates were banked (`add`, not `export` — both first observations, not yet
threshold-ripe) in
`C:/Programs/constellation-wt-228/.agent-work/staged-feedback/228/lessons-delta.json`:
1. `windows-subprocess-env-does-not-shadow-path-resolution` (scope: project) — a restricted
   `subprocess.run(env=...)` override does **not** shadow which executable an unqualified name
   resolves to on Windows; a test must mutate ambient `os.environ["PATH"]` directly.
2. `checklist-engine-from-child-relative-path-and-gated-vs-survey` (scope: constellation) —
   `checklist_engine.py`'s `advance <gate> --from-child <path>` (a) refused a relative path,
   only accepted absolute; (b) only works against a **survey**-type child checklist (has a
   `consolidation`), not a **gated**-type one (execute.json) — the latter needed a plain
   `attest`+`advance` instead. Neither is documented in `--help` or the gate-execution doctrine.

---

## Workflow feedback

Full entry staged at
`C:/Programs/constellation-wt-228/.agent-work/staged-feedback/228/AGENT_FEEDBACK.md`. Headline
points: the `--from-child` relative-path and gated-vs-survey friction above; a continuation
commander taking over a stalled predecessor must reclaim **two** independent engine leases (the
parent spine and any in-progress nested survey child checklist), not just one — worth calling
out explicitly in continuation-commander dispatch instructions; the Fowler-pass rail gave
genuine, non-rubber-stamp signal rather than being a checkbox exercise.

**No blockers, no BLOCK verdicts, no rework cycles this session** (`rework_count` stayed 0 on
every task I touched).
