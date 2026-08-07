# REVIEW_RESULT — g2-review, issue #440 (epic-418 workstream A2)

**Verdict: APPROVE WITH FINDINGS.**

Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, HEAD `b332287`.
Survey: `.agent-work/issue-440-binding-cwd/crew/g2-review/review.json` — 13 items, all visited,
consolidated `APPROVE-WITH-FINDINGS`, 3 failing checks carried as findings.
Fowler pass: `.agent-work/issue-440-binding-cwd/crew/g2-review/FOWLER_PASS.json`,
`scripts/verify_fowler_pass.py` exit **0** (12 smells, 7 flagged, 3 overridden with logged standards).

The claim survives a hostile read. Both questions answer **yes**, and I settled them by reading the
source and by building my own reproduction from scratch — not by trusting the harness or the crew.
The findings below are real and several are sharp, but none of them overturns the result, because the
load-bearing facts are established independently of the machinery that is weak.

I did not re-run either arm. No file under review was modified.

---

## Q1 — Is the captured trip genuinely the WORKTREE-DISPATCHED agent's own reading?

**Yes.** Six independent lines, four of which I produced myself.

**1. The worktree root appears in nothing the hook reads.**
`evidence/prompt-treatment.txt:51,54,89` — the subagent's engine commands carry a **relative**
`--file .agent-work/sbwork/spine.json`, no `cd`, no `--worktree`, and no environment variable naming
the worktree. `launch()` (`run_two_arm.py:459-466`) sets `CLAUDE_PROJECT_DIR` to the sandbox **main**.
The only worktree-shaped token in the command is the shim script path, and
`spine_rail._candidate_roots` enumerates its five root sources — `--worktree`, a `cd` target, the
payload `cwd`, `git worktree list`, the project dir — none of which is the script token.

**2. My own from-scratch reproduction, which is the check that actually kills the "handed the answer"
hypothesis.** I built a scratch `git init` main plus a real `git worktree add`, planted the spine only
in the worktree, and fired both hook versions on a synthetic payload whose `cwd` is the **main**:

| variant | hook | result |
|---|---|---|
| A1 baseline | HEAD | binds the **WORKTREE** spine, `path_source: git_worktree` |
| A2 baseline | pre-fix `cbd9aee` | binds the **MAIN** path, `path_source: None` |
| **B1 engine script token moved OUT of the worktree into `main/bin`** | HEAD | **still binds the WORKTREE**, `path_source: git_worktree` |
| B2 spine planted in **both** trees | HEAD | **NOTHING BOUND** (g1b ambiguity guard fires) |
| B3 payload has **no** `agent_id` | HEAD | key is the **bare** `session_id`, not composite |
| C1 command contains a `cd` to the worktree | HEAD | `path_source: **cd_target**`, not `git_worktree` |

B1 is decisive: with no worktree-shaped token anywhere in the command, the hook still finds the
worktree. The root is genuinely derived from `git worktree list`. C1 is the converse proof — had the
observed command contained a `cd`, the record would say `cd_target`; it says `git_worktree`, so it did
not. B3 confirms a composite key implies a dispatched agent.

**3. The harness never places a gauge or a binding store.** Every write site in `run_two_arm.py`
(lines 165, 229, 304, 324, 344, 348, 478, 520, 539, 572, 733, 741, 764, 772, 781) writes only settings,
filler, the shim, `spine.json`, logs and evidence. `collect()` (627-700) is read-only. The one direct
hook invocation (line 520) is `preflight`, which runs against its own throwaway `pf-` sandboxes.
The gauge file was not hand-placed.

**4. The reading cannot be the parent's, structurally.** `gauge_writer_hook.py:608-631` — when
`agent_id` is present the reading comes **only** from the derived `subagents/agent-<id>.jsonl`, with an
explicit refusal to fall back to the parent transcript. `find_latest_usage:325` further requires the
line to be `isSidechain` truthy **and** carry `agentId == agent_id`. So `fill_fraction: 0.559655` is
arithmetic over the dispatched agent's own usage records.

**5. `identity_resolution_ms` really is dispatched-only.** `gauge_writer_hook.py:648-657` adds the
fifth field solely under `if acting_agent_id is not None`. It is present on both arms' records.

**6. The models separate the two agents.** `evidence/headless-treatment.log` shows the parent launched
with `--model opus`; the gauge record says `claude-sonnet-5`. HARD for `claude-sonnet-5` is
`150_000 / 1_000_000 = 0.15`, confirmed at source (`scripts/gauge_reader.py:84`), so 0.5597 is ~3.7x
the threshold.

**And the trip itself is real, not narrated.** `advance_exit: 1` was parsed from an `EXIT=$?` the
subagent's own shell wrote immediately after the redirect (`prompt-treatment.txt:89`) — a real exit
code, not taken off the end of a pipe. `m1_status_after` is `in-progress`, so the gate genuinely did
not advance.

---

## Q2 — Do the two arms differ ONLY in the hook path?

**Yes in substance, with one provenance caveat I am recording rather than blocking on.**

Verified by me, not read off the recorded output:

- **Whole trees, not a curated subset.** `build_arms` (`run_two_arm.py:165-177`) builds treatment by
  `copytree` of the repo's `scripts/` and control by `git archive cbd9aee scripts` — complete trees.
  `arm_diff` (`:185-187`) runs `diff -rq <control>/scripts <treatment>/scripts` over those whole trees,
  and `arm-diff.txt` names exactly one differing file, `scripts/hooks/spine_rail.py`. Independently
  corroborated: `git diff --stat cbd9aee HEAD` shows `spine_rail.py` and `tests/test_spine_rail.py` as
  the only non-`.agent-work` changes, and `tests/` is not copied into an arm.
- **Settings.** I diffed the two files directly: exactly two differing lines, both
  `arms/treatment` → `arms/control` inside a hook command. `env`, `permissions`, matchers and hook
  order are identical, and `build_settings` (`:190-231`) generates everything but the two absolute
  paths from a single loop.
- **Prompts.** Raw diff shows only `run-treatment` vs `run-control` in sandbox paths. After
  normalising the arm name, `diff` exits **0** — byte-identical.
- **Everything else is one code path.** Models (`PARENT_MODEL`/`SUBAGENT_MODEL`), spine (`SPINE`
  literal), filler (`random.Random(4400)`, fixed seed), command sequence.
- **The one deliberate constant is correct.** `build_sandbox` copies HEAD's `checklist_engine.py` and
  `gauge_reader.py` into **both** sandboxes. That holds the observer fixed, which is right — and those
  two files are identical at `cbd9aee` anyway.

**Caveat (finding F3 below): the arms came from two separate harness invocations.** `main()` writes
`arm-diff.txt` and the settings files *before* any arm runs, so an `arm-diff.txt` newer than
`prompt-treatment.txt` can only mean a second invocation. mtimes: `prompt-treatment.txt` 07:38:30 →
(+156.4 s) `arm-treatment.json` 07:41:07; then `arm-diff.txt`/`settings-*.json` 07:41:48,
`preflight-arms.json` 07:41:49, `prompt-control.txt` 07:41:50 → (+143.5 s) `arm-control.json` 07:44:13.
The crew discloses this (`IMPLEMENTER_RESULT.md:66-67`). Consequence: the committed `arm-diff.txt` and
`settings-treatment.json` are run 2's rebuild, not the artifacts in force during the treatment run.
Both are deterministic, so they are the same content — but they are a reconstruction, not a capture.

**On whether the fills carry the argument:** they do, more strongly than the crew claims. 0.559655 vs
0.562149 is 0.44% apart, but the real point is that **both** are ~3.7x HARD. The outcome difference
therefore cannot be an inflation difference under any reading — it is purely which directory the file
landed in.

**Not excluded by design:** with n=1 per arm and treatment always run first, an order or time confound
is not ruled out statistically. I do not think it matters here, because the difference is categorical
(a file at path A vs path B) and mechanistically explained by a one-file code diff I reproduced myself.

---

## Findings

### F1 — BLOCKER-CLASS for the verifier, not for the result: `verify_evidence.py` has eight uncovered silent-pass holes
`.agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py` — coverage, not correctness.

`--selftest` exits 0 and all five bundled mutations are caught. I then wrote eight of my own against
copies; **all eight still exit 0**:

| mutation | why it should fail | verifier |
|---|---|---|
| `treatment-binding-points-at-MAIN` | the fix did **not** work | **exit 0** |
| `treatment-path_source-null` | the provenance the fix is about is erased | **exit 0** |
| `stale-by-30-hours` (both timestamps shifted coherently) | evidence carried forward | **exit 0** |
| `treatment-headless-exit-1` | the run crashed | **exit 0** |
| `parent-and-subagent-same-model` | attribution signal 3 becomes vacuous | **exit 0** |
| `treatment-gauge-ALSO-in-main` | the binding was ambiguous | **exit 0** |
| `skip-sidecar-present` | the writer was uncertain | **exit 0** |
| `arm-prompts-differ-in-substance` (control told to read 2 filler files, not 24) | Q2 violated | **exit 0** |

The first is the serious one: **the verifier would green-light a treatment arm that reproduced the
bug**, because `check_treatment` (lines 134-156) never looks at `binding_entries` or `binding_store`
at all. `path_source == "git_worktree"` — the single most load-bearing fact in the whole claim — is
asserted only for the **preflight** (`check_preflight`, :296-299), never for the live arm. The last is
the Q2 gap: `prompt-*.txt` is never read by the verifier.

This is a direct miss against a documented repo standard —
`docs/agents/CREW_CONTEXT.md` §Verification Discipline: *"Pair it with adversarial fixtures authored to
make the tool return a wrong answer: a false FAIL on valid input, a silent PASS on invalid input."*

**None of these describes the actual evidence.** I checked every one of those facts by hand against the
real files and they are all correct. This is a defect in the checker, not in the result.

### F2 — The freshness check cannot detect staleness, and one stale file was carried forward
`verify_evidence.py:202-217`. It compares `observed_at` against `wall_clock_at_collect` — **both
written by the same `collect()` call** — so it only proves the gauge was sampled seconds before
collection, never that collection was recent. My `stale-by-30-hours` mutation shifts both coherently
and passes. The R2 handoff's claim (`IMPLEMENTER_HANDOFF_R2.md:87-89`) that *"a gauge from attempt 1 is
~28 hours old and will fail that"* is **wrong about this checker**; whatever failed attempt 1 was
something else.

I settled freshness independently, by filesystem mtimes, and **the evidence is genuinely fresh** — the
timings above chain exactly through the recorded `elapsed_s` of each arm.

**One stale file did come forward:** `evidence/probe.json` is dated `2026-08-06T03:19` and records
`filler_chars: 240000` with verdict `TRUNCATED`, contradicting the harness's current
`FILLER_CHARS = 28_000` and its own comment (`run_two_arm.py:80-87`) claiming a whole filler file
arrives untruncated. `verify_evidence.py` never reads `probe.json`. Not load-bearing — both arms
demonstrably inflated past HARD — but it is committed evidence that does not support what it is cited
for.

### F3 — The arm-difference evidence for the treatment arm is a post-hoc rebuild
`evidence/arm-diff.txt`, `evidence/settings-treatment.json` (mtimes 07:41:48, three minutes *after* the
treatment run finished at 07:41:07). See Q2 above. Deterministic and therefore correct in content, but
it is a reconstruction rather than a capture, and `live-checkout-untouched.json`'s `before` fingerprint
was likewise taken at run 2's start (07:41:47) — **its window does not cover the treatment arm at all.**

### F4 — `probe()` computes a verdict, writes it, and discards it
`run_two_arm.py:548-579`. The docstring promises *"a TRUNCATED verdict is reported, not silently worked
around"* and the trailing comment (`:577-579`) describes a two-branch policy (`FULL: 6 x 200_000
chars` … `Otherwise assume ~30_000 chars per call and take 30 calls`), but the body ends in an
unconditional `return FILLER_COUNT`. The comment describes behaviour the code does not have.

### F5 — `py` vs `python`, and the preflight's blind spot
`run_two_arm.py:215, 221` wire both hooks with `py`, while `preflight` invokes the same hook with
`python` (`:520`). `docs/agents/CREW_CONTEXT.md` §Python Invocation says use `python`, not `py`, and on
this box they are different interpreters (3.12.13 vs 3.14.x). Not a Q2 confound — both arms use `py` —
and demonstrably harmless, since both arms' hooks ran and wrote their stores. But preflight's stated
purpose #1, *"the arm tree is COMPLETE"*, was established under an interpreter the live arms never
used.

### F6 — Fowler pass: seven flagged smells
Full record in `FOWLER_PASS.json`. The one that is more than cosmetic is **shotgun-surgery**: the
evidence schema is declared nowhere, so `collect()` records `skip_sidecar_wt`, `skip_sidecar_main`,
`uncalibrated_wt`, `binding_entries[].path_source` and `headless.exit` that **no check ever asserts** —
that is the mechanism behind five of the eight holes in F1. Also worth naming:
**speculative-generality** (F4), **primitive-obsession** (arm identity is a bare string tested by
substring, `verify_evidence.py:111,115`), and **message-chains** (`verify_evidence.py:257`
`Path(m).parent.parent.name` silently yields a wrong root if the sandbox layout changes, after which
the leakage test searches the live store for the wrong string **while still reporting PASS**).
`duplicated-code`, `feature-envy` and `comments-as-deodorant` are **overridden** with logged repo
standards — the checker's documented refusal to import the producer (`verify_evidence.py:34-36`), and
the in-repo convention of carrying experimental rationale in comments.

---

## The rewritten check — adjudicated

**Ruling: a legitimate correction of the exclusion, and a genuine weakening of the window. Both should
be on the record.**

Legitimate, three ways:

1. **The original was unsatisfiable, not merely inconvenient.** It asserted byte-identity of
   `C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json` across the run. Every
   concurrently-running agent rewrites that file through the live checkout's own PostToolUse hook. I
   confirmed this at the source rather than taking it on trust: the store is **4561 bytes now**, versus
   4213 before and 4663 after the run, and it currently contains **my own** `review.json` under key
   `cdcd8db2-…#a5a`, put there by my engine `claim` minutes ago. A check that any bystander can fail
   carries no information about the harness.
2. **The harness structurally cannot write it.** `launch()` sets `CLAUDE_PROJECT_DIR` to the sandbox
   main (`run_two_arm.py:460`), and `git_worktree_roots` probes that sandbox repo, which has exactly
   one worktree. No rung can reach the live checkout.
3. **The replacement is falsifiable and is demonstrated to fail**, via the new fifth selftest mutation.

**Verified independently, as the handoff required:** the live store contains no `acc440`, `sbwork`,
`AppData`, `Temp`, `run-treatment`, `run-control` or `pf-treatment` substring. All 12 entries name real
repository paths. **No sandbox path leaked.**

**The weakening, stated plainly:** the leakage test reads the live store at **verification** time, not
run time. A sandbox entry that leaked and was later removed by a `release` would go undetected, and the
check drifts further from the event with every re-run. The before/after fingerprint it replaced was at
least contemporaneous. Combined with F3 — that the `before` fingerprint did not cover the treatment arm
anyway — the exclusion is now supported by a weaker instrument than the one it replaced. I still judge
the swap correct, because a check that cannot pass is worse than one that can, and because the
structural argument (2) does the real work.

---

## The quiet first launch — adjudicated

**Ruling: a declined run that complied on an identical re-run. Not a garden of forking paths.**

The handoff asked me to confirm this from `headless-*.log`, and **that is not possible** — the harness
writes `TMP/logs/<arm>.log` and copies it over `evidence/headless-<arm>.log` on every invocation, so the
surviving `headless-treatment.log` (07:41:07) is the **second** launch only, and `TMP` has been deleted.
The crew's account of the decline (`IMPLEMENTER_RESULT.md:75-89`) is uncorroborated prose. That is
finding F7 in effect, and triage candidate tc4.

What *is* checkable settles the question anyway: the prompt is a pure function of harness constants
(`subagent_prompt`/`parent_prompt`, `run_two_arm.py:360-444`), and `run_two_arm.py`'s on-disk mtime is
**2026-08-06 03:26 — before both Aug-7 launches** — with `git status` reporting it unmodified. The
prompt generator could not have been touched between the quiet launch and the compliant one, and
`--filler-count 24` matches the file's own `FILLER_COUNT` default. The arm was re-run **unchanged**.

Residual: at least three invocations ran on 2026-08-07 (quiet treatment, compliant treatment, control)
and only two are on record.

---

## Triage candidates

- **tc1** — Close the gap between what `collect()` records and what `verify()` asserts (F1).
- **tc2** — Make the freshness check a real one (compare `collected_at` to the verifier's own clock);
  retire or regenerate `evidence/probe.json` (F2).
- **tc3** — `spine_rail.py` will bind a spine path that does not exist when it comes from a told-truth
  rung: the live store holds entries for `C:\Programs\constellation-skills\x` and
  `C:\Programs\constellation-skills\$E`, the latter an unexpanded shell variable recorded verbatim. I
  read both directly. Given #440 is about binding the wrong path, a hook willing to record a
  nonexistent one deserves an issue. (Independently found by the crew; confirmed by me.)
- **tc4** — Do not overwrite the previous launch's headless log; timestamp it per launch.

---

## Reconciliation note for the Commander

No architecture map exists (`DEGRADED-NO-MAP`); the change is confined to `.agent-work/`. The
implementer's Map Impact notes check out against the diff. **One precision:** the requested regrade of
decision `existence-verified-resolution` from `guess` to `measured` is justified but should be
**scoped**. The live arms exercised only rung 4 (`git_worktree`) succeeding and rung 5 (`project_dir`)
failing to validate. The told-truth rungs 0-2 and the g1b two-guesses-disagree refusal were **not**
exercised by this acceptance — they remain unit-tested only. My own reproduction did exercise the
ambiguity guard and the `cd_target` rung, so evidence for those now exists, but it is mine, not the
harness's. Recommend regrading the guessed-rung path to `measured` and leaving the told-truth path as
it stands.

---

## What I could not settle

1. **Whether the declined first treatment launch was truly identical.** Its log is gone. I settled the
   forking-paths concern by a different route (the harness source predates both launches and is
   unmodified), which I consider sufficient — but the direct evidence the handoff asked for does not
   exist and cannot be recovered.
2. **Whether a leak into the live binding store occurred and was later released.** The current check
   reads the store now, not during the run, and the contemporaneous fingerprint did not cover the
   treatment arm. The structural argument says a leak was impossible; I could not close it empirically.
3. **Order/time confounding between the arms.** n=1 per arm, treatment always first, never randomised.
   Settling it would require re-running the arms in the opposite order, which is out of scope and, in
   my judgment, not worth the budget given the mechanism is reproduced.

Nothing here required an arm to be re-run, so I did not request one.

---

## Workflow Feedback

- **The repo's `skills/reviewer/templates/REVIEW_SURVEY.template.json` diverges from the globally
  installed copy and ships an unresolved placeholder.** Its `r6-fowler` carries a `command`
  postcondition `python scripts/verify_fowler_pass.py <fowler-pass-record-path>`; the global copy has
  `postconditions: []`, which is why both prior g1 reviews on this issue show `pc []`. The engine
  refused my `record` until I resolved the token. Nothing in the skill or the handoff names this as an
  instantiation step alongside `<work-id>`, and a `command` postcondition cannot be `attest`ed, so
  there is no engine-sanctioned route other than resolving it at instantiation. Worth documenting, or
  worth having the engine substitute a known token.
- **The handoff asserted a mechanism that does not exist.** Check 3 told me `verify_evidence.py`
  checks `observed_at` against a 30-minute window and that attempt 1's stale evidence "correctly
  failed". It does not, and it would not have. A reviewer who took that on trust would have recorded a
  freshness pass that means nothing. This is the good case for the handoff's own instruction to verify
  claims at the source — but the handoff should probably not assert an implementation detail it has
  not run.
- **The `--finding` flag and backticks.** A finding containing backticked identifiers is executed as
  command substitution by the Bash tool before the engine ever sees it; mine spawned two Python REPLs
  and burned a two-minute timeout. Passing long findings via `FIND=$(cat file)` is the form that works
  and is worth putting in crew doctrine next to the existing exit-code guidance.
- **The scope rule "do not re-run the arms" was clear and correct, and it left enough room.** Building
  my own sandbox from scratch cost seconds and produced the single strongest piece of evidence in this
  review (variant B1). A handoff of this shape might say so explicitly: *re-running the expensive thing
  is forbidden, building your own cheap version of it is encouraged.*
