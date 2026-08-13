# REVIEW_RESULT

## Verdict

**`APPROVE`**

Scoped as the handoff asked: this is the verdict on **jobs 1 through 7 and the additional checks** — the integrity of the change as built — judged **excluding** the `tests/test_mcp_lifecycle.py` failure, which is the floated collision.

## Merge readiness

**NOT READY.** The failure-set difference against `main`'s 0-failed baseline is exactly `{tests/test_mcp_lifecycle.py}`. I reproduced the full suite twice, before and after my own arming reverts, and got the same single failure both times. The launch order's merge gate is an empty difference, so this change cannot merge until the floated collision is ruled on. A clean `APPROVE` on jobs 1-7 does not make it merge-ready.

## Gate

`g1-review` of `.agent-work/commander-315-native/execute.json` (work-id `commander-315-native`).

Survey driven through the engine at `.agent-work/commander-315-native/g1-review/review.json`, session `g1-review-reviewer-attempt-1`. Seven items, all visited and recorded; consolidated `verdict=APPROVE findings=1`.

Worktree `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`, branch `epic-568/c2-native-isolation`, base `9bb8c1b6`, HEAD `a04d7828`. I never entered `epic-568-315` and never wrote the main checkout.

---

## Job 1 — THE TRAP: not reproduced

The falsified predecessor forwarded a stored root into a subprocess so that both sides derived from the same value. This change does not.

- **No forwarded `cwd`.** The only `cwd=` in the whole production diff is `origin_worktree_refusal(cl, cwd=engine_cwd, verb=args.verb)` at `scripts/checklist_engine.py:3364` — the keyword argument of a pure Python function, not a subprocess. The diff adds no `subprocess`, no `Popen`, no `run(`.
- **Independent sources.** Stored side: `spine["origin"]["worktree"]`, read out of the spine file by `load()`. Measured side: `str(Path.cwd().resolve())` computed in `main()` at `scripts/checklist_engine.py:3363`. Neither derives from the other.
- **The refusing side genuinely fires.** I did not take the implementer's word. I wrote my own probe (`/tmp/rv_probe.py`), built spines by hand in `/tmp`, and drove the real engine as a subprocess with an explicit harness cwd:

```
OK    claim from a foreign tree exits non-zero  -- rc=1
OK    refusal names both sides on stderr  -- REFUSED: claim refused: this spine belongs to the
      worktree /tmp/rv_sandbox/repo, but the engine is running in /tmp/rv_sandbox/elsewhere.
OK    spine byte-identical after refusal  -- 14e3fd788b38 vs 14e3fd788b38
OK    mtime unchanged after refusal
OK    no journal sidecar written
```

## Job 2 — THE ARM: both halves go red under my own reverts

I edited the tree myself and asserted each mutation actually applied before running anything. I did not replay the implementer's transcript.

**(a) Stamp removed from `init_work_area.instantiate_spine`** (deleted the `spine.setdefault("origin", {...})` block; verified `0 occurrences` afterwards):

```
FAILED tests/test_spine_origin_isolation.py::StampsOriginAtInstantiation::test_stamp_keys_are_a_subset_of_the_lifecycle_origin_block
FAILED tests/test_spine_origin_isolation.py::StampsOriginAtInstantiation::test_stamps_exactly_work_id_worktree_and_opened_by
2 failed, 28 passed, 1 skipped, 10 subtests passed in 0.12s
```

The Commander's repro de-arms in the same world: `B  origin spine, cwd = MAIN CHECKOUT -> PASS` / `GATE ARMED: False`.

**(b) `main()` call site removed** (deleted the five-line block; verified `origin_worktree_refusal( occurrences in main(): 0`):

```
FAILED ...RefusesAGuardedVerbFromAForeignTree::test_claim_from_a_foreign_tree_is_refused_and_writes_nothing
FAILED ...RefusesAGuardedVerbFromAForeignTree::test_no_journal_sidecar_is_written_by_a_refusal
FAILED ...RefusesAGuardedVerbFromAForeignTree::test_start_from_a_foreign_tree_is_refused_and_writes_nothing
FAILED ...RefusesAGuardedVerbFromAForeignTree::test_the_refusal_names_both_trees_on_stderr
FAILED ...TheInProcessMcpDoorShape::test_a_guarded_verb_is_refused_in_process_from_a_foreign_cwd
FAILED ...TheGuardIsReachedFromExactlyOneSite::test_main_calls_the_predicate_exactly_once
FAILED ...TheGuardIsReachedFromExactlyOneSite::test_the_call_site_is_before_dispatch
7 failed, 23 passed, 1 skipped, 10 subtests passed in 0.17s
```

Repro again de-arms: `GATE ARMED: False`.

**Restored after each**, `git status --porcelain scripts/ tests/ skills/ docs/ map/` empty, and `33 passed, 1 skipped, 10 subtests passed`.

**One extra measurement the handoff's job 6 asked about, which I took here because the world was already defective:** under arm (b), `tests/test_worktree_precondition_wiring.py` still reports `3 passed`. So that file really is blind to the new behaviour, exactly as the handoff warned — it is evidence for the fallback branch and nothing else.

## Job 3 — THE FALLBACK: eleven shapes, none raises

Driven through the real engine as a subprocess (`claim`, a guarded verb, from a foreign cwd), not through the predicate in isolation. All returned `rc=0` with no `Traceback`:

`origin` absent · `origin: null` · `origin` a **string** · `origin` a **list** · `origin: {}` · `worktree` absent · `worktree` empty string · `worktree: null` · `worktree` an int · `worktree` a list · `worktree` a dict.

The string and list cases — where a naive `.get` raises `AttributeError` that `main()` does not catch — are the ones that mattered, and both fall back cleanly. `isinstance(origin, dict)` guards them at `checklist_engine.py:146`.

## Job 4 — THE NO-GOS: all hold

| no-go | how I observed it |
|---|---|
| No forwarded `cwd` | job 1 above |
| `base_dir` untouched | `git diff 9bb8c1b6 -- scripts/checklist_engine.py \| grep -c '^-[^-]'` → **0 removed lines**. The change is purely additive, so `base_dir` cannot have been touched. The root is carried as `engine_cwd`. |
| No write on the refusal path | Judged on the file, not the prose: sha256 and mtime both identical across a refused `claim`, no `.json.journal` sidecar. The guard returns `1` at `checklist_engine.py:3367` without reaching `dispatch()` or `save()`. |
| `scripts/spine_lifecycle.py` unchanged | absent from `git diff --stat 9bb8c1b6` |
| `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py` unchanged | absent from the same diff |
| wiring test's surviving assertions unweakened | The file's **entire** diff is the docstring rewrite, the `COVERAGE_SCRIPT` constant, `REAL_TEMPLATE`/`TEMPLATE_REL_PATH`, the `_run_coverage_script` helper, and the three enumeration classes. No hunk touches `EngineDeliberateBreakage` or `IsolationGateSurvivesThroughTheCLI`. |
| `init.c0` and its coverage apparatus deleted | `init.preconditions == []`; `scripts/verify_worktree_precondition_coverage.py` absent from disk **and** from `git ls-files` |

## Job 5 — THE OVERCLAIM: nothing to report

I swept code, comments, docstrings, test names, the docs edit, the implementer result and `repro_native.py` for `cannot be lied` / `non-forwardable` / `unforgeable` / `unfakeable` / `cannot be forged|faked|spoofed` / `immune` / `tamper-proof` / `impossible to fake|forge|bypass`.

Every hit is either an explicit **negation** of the withdrawn claim or the sanctioned claim 2:

- `scripts/checklist_engine.py:126` — "It does **NOT** make the comparison unforgeable. The engine reads its ambient cwd, so a check command authored as `cd <origin.worktree> && ...` still satisfies it. That claim was withdrawn deliberately; do not restate it."
- `docs/CHECKLIST_SCHEMA.md:124` — the same, in prose.
- `.agent-work/.../g1-implementer-result.md:45` — states the non-claim as not-claimed.
- `checklist_engine.py:902-903` uses "immune", but that is pre-existing colour-handling text, not in this diff (0 removed lines, first added hunk at line 83).

The three permitted claims — coverage, unbypassability from the spine, an independent expected side — are each stated in the docstring (`checklist_engine.py:119-127`) and in the docs, accurately, and **nothing exceeds them**.

## Job 6 — THE NEW COVERAGE: adequate

- **A spine that really carries `origin`, both sides.** `RefusesAGuardedVerbFromAForeignTree` writes a real spine with an `origin` block to disk and covers both the mismatch side (`claim` and `start` refused, spine byte-identical, `engine_session` still `None`, `g1` still `pending`) and the match side (`test_the_same_verb_from_the_worktree_itself_succeeds`, which asserts the lease really went `active`). A gate that never opens would be caught.
- **Containment, at two levels.** Predicate tests pin root, three subdirectories, `/w/repo-2`, `/w/repo-2/scripts`, and the parent `/w`; an end-to-end test drives `claim` from `.agent-work/w1`. My own probe reproduced all of it through the real CLI: `repo` passes, `repo/scripts` passes, `repo-2` refuses, unrelated tree refuses. `Path.is_relative_to` is used; `startswith` does not appear in the function.
- **The verb set as data, both ways, derived.** `test_guarded_is_the_mutating_set_plus_claim_and_heartbeat` asserts `ORIGIN_GUARDED_VERBS == MUTATING_VERBS | {"claim","heartbeat"}` plus explicit membership and non-membership. A second test enumerates the **live argparse verb list** and asserts it partitions exactly into guarded ∪ exempt with an empty intersection, so a future verb cannot default to unguarded. Measured: guarded is the 16 expected verbs, exempt is `{current, release}`.
- **Nothing cites the wiring test's greenness.** Both module docstrings say the opposite explicitly, and I measured the claim independently (arm (b), above).
- **Case folding** is `@unittest.skipUnless(os.name == "nt")` at `tests/test_spine_origin_isolation.py:291` and claims nothing on Linux. It is the `+1 skipped` in the suite count.

## Job 7 — THE IN-PROCESS CALLER: honoured, no bypass exists

`TheInProcessMcpDoorShape` (`tests/test_spine_origin_isolation.py:460-493`) reproduces the shape exactly: `os.chdir` to a foreign directory, then `checklist_engine.main([...])` **in-process**, against a spine carrying `origin`, cwd restored in `finally`. It asserts `start` returns 1 with the spine byte-identical, `current` returns 0, and `release` returns 0. All three go red under arm (b), so they are real tests.

**No off switch exists.** The diff adds no `os.environ`, no `getenv`, no `add_argument`. The predicate's only inputs are the spine dict, `cwd` and `verb` — confirmed off its compiled code object, whose `co_names` is `('ORIGIN_GUARDED_VERBS','get','isinstance','dict','str','Path','os','path','normcase','is_relative_to')`. There is nothing to switch off with, so the defect cannot be recreated one level over.

## Additional checks the Commander asked for

### The `ensure_ascii` question — measured, and the answer is yes, with a bigger effect alongside it

**Yes, shipped templates contain non-ASCII, and yes, the round trip escapes it.** Three of the spine templates `instantiate_spine` consumes carry non-ASCII: `COMMANDER_SPINE` (34 chars), `EXPLORER_SPINE` (13), `ADMIRAL_SPINE` (12) — em dashes and middle dots. Instantiating the Commander spine both ways:

| property | old (verbatim resolved text) | new (`json.dumps(..., indent=2) + "\n"`) |
|---|---|---|
| non-ASCII characters in the written bytes | 34 | **0** |
| `\uXXXX` escapes | 0 | **34** |
| parsed content | — | **identical** (ignoring the new `origin` key) |
| key order | — | **preserved**, `origin` appended last |
| trailing newline | exactly one | exactly one |
| rendered text after parsing | — | **identical characters** |
| file size | 30801 | 34660 |

Two things follow, and the second is the larger one:

1. **Rendered text does not change.** JSON unescapes on load, so what the engine prints and what an agent reads is character-for-character what it was. Key order and the trailing newline survive.
2. **The written spine is also reflowed, and that dominates.** The escapes account for only ~170 of the 3859-byte growth. The templates hand-format condition dicts on one line (`{"id": "c1", "statement": ..., "check": {...}}`); `json.dumps(indent=2)` expands each onto multiple lines. So an instantiated spine is now escaped **and** reformatted.

**Does it break anything today? No.** I looked for consumers that read a written spine as raw text: no script does (`scripts/*.py`, `scripts/hooks/*.py` all go through `json.load`), and no shipped template's check command greps `spine.json`. The suite is green on this point. It is a real behaviour change worth recording rather than a defect: any future raw-text grep, byte-diff or line-diff over an instantiated spine now sees escaped, reflowed JSON.

### The other two

- **`Path.is_relative_to`, not `startswith`** — confirmed by reading the function source; `startswith` does not appear in it, and my `repo-2` probe confirms the segment-wise behaviour end to end.
- **The guard sits before the `refusals` arming** — the call site is `checklist_engine.py:3363-3367`, and the `#427` arming block begins at 3368, immediately after. So a refusal neither increments nor persists that counter. The byte-identical spine after a refused `claim` is the observed confirmation.

---

## The known open collision — audited, not re-litigated

- **The failure reproduces, and it is the only one.** Two independent full-suite runs (before and after my arming reverts, on a tree I confirmed clean in between): `1 failed, 2959 passed, 6 skipped, 1130 subtests passed`. Mechanical distribution both times: `1 FAILED tests/test_mcp_lifecycle.py`.
- **Reason #1 is indeed false as stated.** `run_crew.launch_process` (`scripts/run_crew.py:676`) is `subprocess.run(argv, input=stdin, stdout=out, stderr=err, env=env)` — no `cwd=`. `cwd` appears exactly once elsewhere in that 1500-line module, as an unrelated `--root` help string. A dispatched crew inherits the **dispatcher's** cwd, whatever that happens to be.
- **Verb scope cannot resolve it.** The Commander's reading is correct, and I checked it against the failing test rather than against the ruling. Door B drives `claim → start → attach → advance → release`. `start`, `attach` and `advance` are all in `MUTATING_VERBS`. Dropping `claim` from the guarded set would move the failure from `spine_lease` to `spine_start`, one call later.
- **Would having the door supply its own binding (`SPINE.parent`'s toplevel) as the measured side be a real fix? No.** I measured it rather than reasoning about it. For a spine `init_work_area` created at `<root>/.agent-work/<id>/spine.json`, `git rev-parse --show-toplevel` from `SPINE.parent` returns **exactly** the stamped `origin.worktree`. The two sides are equal by construction, because both derive from the same creation act — and `spine_lifecycle.build_origin` stamps the same way.

  It is not *literally* the falsified `X == X`: one side is stored text, the other a filesystem fact, so it would catch a spine file later **moved** between trees. But that is the only thing it could ever catch, and it stops measuring **where the actor is** — which is the protected intent in the handoff's own words ("an agent must not drive a spine's state from a tree that is not the spine's own"). It converts a guard on the actor into a guard on the file's location, which is a check that cannot fail in any normal world. Not a real fix.
- **Any honest fix inside the allowed scope that both missed? I found none.** Every fix that preserves the protected intent changes **who sets cwd** — either `run_crew.launch_process` passing `cwd=<the spine's worktree>`, or the door `chdir`-ing around its in-process `main()` call. Both files are excluded from the implementer's scope. Inside `checklist_engine.py` alone, the engine has no way to distinguish "a door correctly driving its own bound spine" from "an agent standing in the wrong tree" without a signal from the caller, and any such signal is the off switch outside the spine that the ruling forbids. I also considered and rejected keying the guard on `origin.opened_by` (guard only `init_work_area` spines): that would leave every real crew spine — the ones `spine_open` creates — unguarded, which is a producer-keyed off switch wearing different clothes.

  Worth naming for the Admiral: `origin` was **already** being stamped by `spine_lifecycle.build_origin` before this change. The collision is a pre-existing write side meeting a new read side, not something this change invented.

---

## What I could not verify

- **The 2-subtest delta.** My counts match the implementer's exactly on passed/skipped/failed, but I report 1130 subtests to their 1128. Some tests enumerate the live `.agent-work` tree (`tests/test_episode_capture.py`'s `resolve_roots`, `tests/test_code_map.py`), and my own survey artifacts landed there, which is a plausible explanation — but I did not establish it, and I am not asserting it. It changes no pass/fail verdict.
- **Windows behaviour.** `os.path.normcase` is the identity on POSIX, so the case/separator-folding branch is unexercised here. The test that covers it is correctly `skipUnless(os.name == "nt")` and claims nothing on Linux; I am repeating its scope, not extending it.
- **Whether `main`'s stated baseline (2934 / 5 / 0) is current.** I took it from the handoff and did not check out `main` to re-measure it. Every number I state is measured on this worktree at `a04d7828`.

---

## The one recorded finding — `r2-scope`, recorded `fail`

**`tests/test_shipped_check_commands_resolve.py:97` — `EXPECTED_COMMAND_CHECK_COUNT` `13 → 12` — is outside the implementer handoff's `Allowed Scope` list.**

I recorded this as a `fail` rather than softening it, and took the `APPROVE --override-reason` exit, because the finding is real but does not bar the change:

- It is **mechanically forced** by the Admiral-authorized `init.c0` deletion — that precondition was one of the 13 command-kind checks the census counts.
- The implementer **disclosed** it and asked for ratification rather than burying it.
- **12 is the only correct value, proven.** I mutated the constant to `13` and to `11`; both go red. `12` is green. The tripwire still pins an exact count and is not weakened.

This needs **Commander ratification**, not rework. It is outside jobs 1-7, on which the verdict is scoped.

*(A note on my own method: mutating that constant left a stale pytest assertion-rewrite `.pyc` — `= 11` and `= 12` are the same byte length — which made the restored file read as still-failing until I cleared `tests/__pycache__`. Worth knowing before anyone reproduces this experiment and concludes the tree is dirty.)*

## Fowler / refactoring pass

Record at `.agent-work/commander-315-native/FOWLER_PASS.json`; `python scripts/verify_fowler_pass.py .agent-work/commander-315-native/FOWLER_PASS.json` exits 0 — `smells=12, flagged=['duplicated-code','divergent-change','speculative-generality'], overridden=['large-class','primitive-obsession','comments-as-deodorant']`.

All three flags are **non-blocking observations**, not conditions on this verdict:

- **duplicated-code** — the three-claims paragraph and its withdrawn non-claim are hand-authored in three places (`checklist_engine.py:119-127`, `docs/CHECKLIST_SCHEMA.md:124`, `tests/test_spine_origin_isolation.py:20-25`). Deliberate — the handoff required the non-claim wherever the claims appear — but nothing checks the copies against one another, and CREW_CONTEXT's own rule is that prose is never checked against what runs. A future correction to one copy leaves two stale.
- **divergent-change** — `checklist_engine.py` already changes for gauge, lease, rail, journal and trip reasons; this adds worktree identity as another axis to the same ~3450-line module.
- **speculative-generality** — `ORIGIN_EXEMPT_VERBS` (`checklist_engine.py:98`) has no production consumer: the predicate reads only `ORIGIN_GUARDED_VERBS` (proven off the code object), and grep finds no non-test reference. Partly earned, since the partition test makes it load-bearing against an unclassified new verb, but the shipped code never reads it.

The three overrides each log the standard that wins and why: **large-class** (extracting a one-caller predicate would mint a single-adapter seam, which `global-everyone.md` calls a guess), **primitive-obsession** (str verbs and str paths are the module's idiom throughout), **comments-as-deodorant** (the prose carries *why* — the `X == X` trap, why no `save()`, why `engine_cwd` not `base_dir` — matching the module's own established style, e.g. the adjacent `#427` block).

## Out-of-scope observations (triage candidates)

1. **`run_crew.launch_process` spawns every crew with no `cwd=`** (`scripts/run_crew.py:676`), so a crew's working directory is an accident of whoever dispatched it. Worth fixing on its own merits, independent of this issue.
2. **`EXPECTED_COMMAND_CHECK_COUNT` is a hand-maintained census** that no template edit updates automatically; a deletion elsewhere breaks it silently until the suite runs.
3. **`mcp_spine_server.py` is architected to be cwd-independent** — every path derivation takes an explicit `cwd=` anchored on `SPINE`'s own location, with docstrings saying so. An engine that reads ambient cwd is in standing tension with that invariant, and the tension will recur for any future cwd-sensitive engine behaviour.
4. **`checklist_engine.py`'s reason-to-change count** (see Fowler `divergent-change`) is worth a Cartographer look, even though extraction today would be worse than the status quo.

Recorded in the survey as `tc1`-`tc4`.

## Required evidence, as run

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/ -q -p no:randomly
#   1 failed, 2959 passed, 6 skipped, 1130 subtests passed in 118.74s   (run 1)
#   1 failed, 2959 passed, 6 skipped, 1130 subtests passed in 119.42s   (run 2, after restore)

python -m pytest tests/ -q -p no:randomly 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
#         1 FAILED tests/test_mcp_lifecycle.py

python .agent-work/commander-315-native/repro_native.py     # exit 0
#   A  origin spine, cwd = WORKTREE ROOT -> PASS     (want PASS)
#   B  origin spine, cwd = MAIN CHECKOUT -> REFUSED  (want REFUSED after the change)
#   C  no-origin,    cwd = MAIN CHECKOUT -> PASS     (want PASS in both worlds -- the fallback)
#   D  origin spine, cwd = WT SUBDIR     -> PASS     (want PASS -- containment, not equality)
#   B refused AND took no lease (state fact): True
#   GATE ARMED: True

git diff --stat        # no production file; only .agent-work run artifacts
```

Against `main`'s stated Linux baseline of **2934 passed, 5 skipped, 0 failed**: **+25 passed**, **+1 skipped** (the `skipUnless(nt)` case-folding test), **+1 failed**. The failure-set difference is exactly `{tests/test_mcp_lifecycle.py}` — verified, as the handoff asked.

`repro_native.py` is unedited; `git status` shows it clean.

## Tree state

I modified `scripts/init_work_area.py`, `scripts/checklist_engine.py` and `tests/test_shipped_check_commands_resolve.py` to run the arming reverts and the census mutation, and restored each with `git checkout --` immediately after. `git status --porcelain scripts/ tests/ skills/ docs/ map/` is empty. The only files I added are my own sanctioned artifacts under `.agent-work/commander-315-native/`: `g1-review/review.json`, `FOWLER_PASS.json`, and this result. All my scratch fixtures live in `/tmp`.

## Workflow Feedback

*What I observed, not what I recommend.*

- **The handoff was the most useful I have worked from, and the reason is specific: it named the failure mode before the check.** "Prove this change did not reproduce that", "a test that passes in both worlds is not a test", "judge it on the hash, not on the refusal prose" — each told me what a *fake* pass would look like, so I could build the falsifying experiment instead of confirming the claim. The two jobs that took the longest (the arm, the no-write hash) were also the two where a lazy reviewer would most plausibly have accepted the implementer's numbers.
- **Job 6's "structurally blind" claim was stated but not assigned a check.** The handoff told me the wiring test is green by construction; it did not ask me to prove it. I measured it anyway (green under arm (b)) because the claim is load-bearing for how much weight the wiring file carries. If a handoff asserts a property of the *evidence*, it is worth naming the measurement that would falsify it — otherwise the reviewer inherits it as an assumption, which is the shape this issue exists to remove.
- **The `ensure_ascii` question was framed honestly ("a real question, not a leading one") and that framing changed my answer.** I found the escaping the question anticipated, but the larger effect — the whole-file reflow from one-line condition dicts to expanded ones — was not in the question, and I would likely have stopped at the escapes had the question been leading. The framing bought a finding.
- **One genuine ambiguity: the survey template's Fowler-record path.** `r6-fowler`'s postcondition resolves to `.agent-work/<work-id>/FOWLER_PASS.json`, which puts a reviewer artifact at the Commander's work-area root rather than under the review's own `g1-review/` directory, next to the survey it belongs to. I followed the convention as written rather than improvising a path the postcondition would not find. Worth noting for whoever owns the template: with two crews under one work-id, that path is not per-review.
- **The engine CLI wants `--file` before the verb.** `checklist_engine.py <verb> --file ...` fails with a bare argparse error that does not say so. Minor, but it cost me two round trips at claim time, and a crew cold-starting from the handoff hits it first thing.
- **`flag-candidate` takes `--from` and `--statement`, not `--note`.** Same shape of friction: the refusal names the missing arguments, so it is self-correcting, but neither the skill nor the handoff shows the form.

## Return fields

- **`Verdict`: `APPROVE`** — on jobs 1 through 7 and the additional checks, excluding the floated collision.
- **`Merge readiness`: NOT READY** — while `tests/test_mcp_lifecycle.py::FullStdioRoundTripTests::test_open_drive_close_round_trip_names_branch_commit_and_ready_to_pr` stands. The failure-set difference against `main` is exactly `{tests/test_mcp_lifecycle.py}`.

One recorded `fail` (`r2-scope`) is carried through `consolidate --override-reason` rather than softened; it needs Commander ratification, not rework.

---

## Run-state note for whoever resumes this Commander

Recorded by the reviewer crew at exit, because the Commander process is still gone — the same hazard the implementer flagged, now one gate further on.

- **Nothing is driving `commander-315-native`.** `spine.json` holds a lease for session `commander-315-native` (`status: active`, `claimed_by: commander-delegated`) whose last heartbeat is `2026-08-13T05:20:52Z` — held by a dead process, so it is reclaimable by staleness; a same-id re-claim is idempotent.
- **`execute.json` has not moved.** `engine_session: None`; `g1-implement` is `in-progress` and **`g1-review` is still `pending`**. The review gate was never `start`ed, so the plan does not record that a reviewer ran.
- **The hazard, repeated for this gate.** A resumed Commander reading `execute.json` alone sees `g1-review: pending` and may dispatch a **second reviewer** over a review that is already complete. Before dispatching anything for `g1-review`, check three things: this result artifact, the consolidated survey at `.agent-work/commander-315-native/g1-review/review.json` (`verdict: APPROVE`, all seven items visited, lease released), and `crew-runs.json` — whose attempt-1 entry reads `running` only until my launcher (`run_crew.py`, pid 710547) records my exit.
- **Do not re-run the reviewer.** The review is complete and its lease released. What is outstanding is not review work: it is the Commander's ruling on the floated `test_mcp_lifecycle.py` collision, and ratification of the one out-of-scope line (`EXPECTED_COMMAND_CHECK_COUNT 13 → 12`).

I did not drive `execute.json` myself. I am a dispatched crew with no bound spine; the gate belongs to the Commander, and seizing that lease from inside a crew is the two-controlling-agents failure the lease exists to prevent.
