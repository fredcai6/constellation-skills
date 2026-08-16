# Plan Critic Findings — cleanup-g-crew-tier (#611)

Adversarial pass against `LAUNCH_ORDER.md`, `MISSION_FRAME.md`, `PLAN_CONVERGENCE.md`, and
`execute.json`, cross-checked line-by-line against the real `scripts/run_crew.py` and
`tests/test_crew_launcher.py` on disk. Factual-accuracy verdict up front: every specific
`file:line` citation I checked (`build_crew_argv` 755-818/813-814, `CrewSpec.__post_init__`
1350-1364, `CliBackend.dispatch`/`.resume` call sites at 1542/1612, `build_entry` 1092-1199/
1193-1196, `main()` 1974-2109, the abandon+relaunch branch 2068-2074 including the exact
asymmetry claimed between `model=args.model` (no fallback) and
`reasoning_effort=args.reasoning_effort or abandoned.get(...)` (fallback), the four named test
line numbers at 955/2588/2605/2623, `crew-dispatch.md` having zero "model" hits, and the
`claude --effort <low|medium|high|xhigh|max>` flag) matched the real file exactly. No drift
found there. The findings below are about the plan's own gaps and reasoning, not citation
accuracy.

## 1. The mission's own "trap" is never referenced or operationalized anywhere in the plan (major)

`grep -in "trap" PLAN_CONVERGENCE.md execute.json MISSION_FRAME.md` returns zero hits. The
launch order gives the trap its own section and treats it as the mission's central hazard:
name a tier for every crew you dispatch from the moment you start, and sequence so a refusal
landing mid-run doesn't lock out your own reviewer dispatch. Neither `g1-implement`'s nor
`g1-review`'s imperative in `execute.json` contains a single word telling the Commander to pass
`--model` when it dispatches *this gate's own* implementer/reviewer crew.

This isn't a paperwork gap — it's live. `crew-dispatch.md`, the doctrine file a Commander
reads before every dispatch, says nothing about model until `g2-doctrine` lands, which the plan
deliberately sequences *after* `g1`. So while `g1-implement` and `g1-review` are running, the
Commander's only doctrine is silent on tier. And the refusal, once `g1-implement`'s code lands
on disk (same worktree, same file), applies uniformly to *every* `CrewSpec` construction —
including the `external` backend's `record_external_attempt`, which `crew-dispatch.md` itself
says is how this harness dispatches implementer/reviewer crews ("dispatch the
implementer/reviewer as synchronous Agent-tool subagents via `--dispatch external`"). So the
literal trap scenario — refusal landing between implement and review, blocking the Commander's
own reviewer launch — is exactly what happens if the Commander dispatches `g1-review`'s reviewer
crew without an explicit `--model`, and nothing in the frozen gate plan reminds it to pass one.

The plan's dispatch-count minimization (one implement/review pair instead of candidate B's six)
reduces *exposure* to this but does not close it, and the convergence doc doesn't claim it does
— it just never raises the trap at all.

**Fix:** add one explicit line to `g1-implement`'s and `g1-review`'s imperatives: "Dispatch this
gate's own crew with `run_crew.py --model <tier>` explicitly — this mission's own trap; do not
inherit or default one, even before the refusal exists."

## 2. Plan-phase dispatches already sit outside the mechanism the mission claims covers "every dispatch"

`crew-runs.json` for this run currently holds exactly one entry: the top-level
`execute/commander` (backend `cli`, `model: "sonnet"`). There are no registry entries for
whoever authored `plan-alternatives/candidate-A-smallest-diff.md` /
`candidate-B-most-testable.md`, nor for this critic pass. That means those crews were dispatched
by some path that never touches `run_crew.py`/`build_crew_argv` at all — directly contradicting
`MISSION_FRAME.md`'s Intent line, "the one seam where every dispatch passes through." Return
Shape item 4 in the launch order ("your own dispatch record — the model field on every crew you
launched this run") reads as covering plan-phase dispatches too ("from the moment you start"),
but `execute.json`'s gate list (`e0-context` through `g3-verify`) has no item that captures or
verifies tier for pre-`g1` crews. This may be legitimate (Agent-tool-native subagents predating/
bypassing `run_crew.py` could be out of scope by construction), but the plan should have named
that scoping explicitly rather than silently asserting universal coverage while the evidence in
this very run's own registry contradicts it.

## 3. `g1-integrate`'s machine-checked postcondition omits the mandatory cache-clear step

The launch order's Inherited Context states unconditionally: "Clear `__pycache__` before every
measurement... clear and re-measure rather than investigating whatever it lands on." `g3-verify`
's imperative honors this explicitly ("Clear `__pycache__` repo-wide, then run..."). But
`g1-integrate`'s `c1` postcondition is a literal `"kind": "command"` check —

```
cd .../cleanup-g-crew-tier && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
```

— with no preceding cache clear. This is the one postcondition in the whole plan that is
mechanically re-run by the engine (`advance`, not `attest`, per the gate's own imperative text),
so it's the one place a stale-cache false failure is most likely to be hit blind, cost a rework
cycle, and burn the `override_policy` (human, reason-required) escape hatch that exists on this
exact postcondition — for a failure mode the plan authors clearly knew about (they wrote the
fix into `g3`) but didn't apply here.

**Fix:** prefix the `c1` command with `find . -name __pycache__ -type d -exec rm -rf {} + ;` or
otherwise guarantee a clear cache immediately precedes this specific check.

## 4. The four named "flip this assertion" tests need a second, unstated edit that only the later caller-list survey catches

At least `test_cli_resume_reads_reasoning_effort_from_registry` (~2605) constructs `CrewSpec(...)`
with no `model=` argument at all (only `reasoning_effort="low"`). Once the refusal lands in
`CrewSpec.__post_init__`, this construction raises `CrewLaunchError` from the missing `model`
alone — independent of, and before, the effort-assertion flip the imperative describes for this
test. The imperative's paragraph naming these four tests only talks about the `--effort`
assertion edit and correcting docstrings; it doesn't say "and these constructions also now need
an explicit `model=`." That fix only happens for certain because the *separate*, later-described
caller-list survey step ("run the full suite once, enumerate every failure... a test in
`tests/test_crew_launcher.py` needing an explicit `model=` -- fix directly") will independently
rediscover the same failures. It works, mechanically, but only by accident of the two
instructions overlapping — an implementer who patches exactly what the four-tests paragraph says
and stops there ships a still-red suite, then has to notice the survey step re-flags tests it
already touched. Low severity (self-correcting), but worth tightening so the same fact isn't
split across two disconnected instructions in the same imperative.

## 5. `g2-doctrine`'s evidence is exactly as strong as its own shallow postcondition checks, with no independent check on top

`decision:suggested-tier-becomes-load-bearing` demands the doctrine "make that connection real"
between the handoff's "Suggested Model Tier" field and the `--model` flag. Both machine
postconditions (`c1`: `grep -q -- '--model'`, `c2`: `grep -qi 'Suggested Model Tier'`) and the
imperative's own prescribed "red/green test" check only for *co-occurrence* of the two strings
in the file — not that the prose actually links them into one instruction a Commander follows.
A compliant-on-paper edit could plant two unrelated sentences, one naming `--model`, one naming
"Suggested Model Tier," and pass both checks while doing nothing to connect them. Because `g2` is
a no-crew reasoning gate, there's no independent reviewer (unlike `g1`) confirming the prose does
the actual connecting work — the Commander is sole author and sole grader of whether its own
doctrine edit satisfies the decision. This is defensible under Inherited Latitude ("test
structure" is the Commander's to decide) and matches the pre-ruling's stated preference for the
smaller change, so I'm not calling it a blocking defect — but it's a real asymmetry in rigor
against `g1`, on a gate that implements one of the same five pre-ruled decisions, worth a
reviewer's eyes even briefly rather than pure self-attestation.

## 6. No gate addresses `map/INDEX.md` regeneration

The launch order's Inherited Context flags `map/INDEX.md` as generated, freshness-tested, and
prone to hand-merge conflicts ("regenerate, never hand-merge"). This mission adds a new
`build_crew_argv` parameter, several new tests, and a new doctrine section — all plausible
"entities" changes. None of `e0`/`g1`/`g2`/`g3` mention checking or rebuilding it. If the
freshness test is part of the full suite, `g3-verify` would surface a failure with no gate
assigned to fix it before the stated merge-gate bar ("local Linux green") is met. Given the
launch order flagged this proactively, its absence from every gate's imperative looks like an
oversight rather than a considered omission.

## 7. Minor: the "ruling" on relaunch/`--model` fallback resolves a design tension the current code doesn't actually have

`PLAN_CONVERGENCE.md` frames "relaunch requires an explicit `--model`, no fallback to
`abandoned.get("model")`" as an active decision between two live candidate behaviors. Reading
`main()` at line 2070 shows the current code already does exactly this (`model=args.model`, no
`or abandoned.get(...)`) — only `reasoning_effort` has the fallback today. So this "ruling" is
really "don't add a fallback that doesn't exist yet," not a change to a line of code. The
reasoning given is sound and the outcome is correct, but the convergence doc's framing ("Ruling:
...") could mislead an implementer into looking for a code change at that line when the only
actual effect is indirect (the new upstream refusal now fires there when `model` is absent,
where before it silently proceeded). Cosmetic; flagging only so the ruling's actual leverage
point — the refusal seam, not this line — stays clear to whoever implements it.

## What held up under adversarial pressure

- Refusal seam choice (`CrewSpec.__post_init__` over `build_crew_argv` or `argparse
  required=True`) is correct and well-argued: `--resume` and bare `--abandon` never construct a
  `CrewSpec` (verified directly in `CliBackend.resume` and `abandon_crew`), so the seam exempts
  them by construction, not by a special case that could rot.
- `build_entry`'s existing `if model:`/`if reasoning_effort:` recording genuinely already
  satisfies `decision:record-the-resolved-tier` once `model` is mandatory — confirmed by reading
  the function directly; no new write path is needed, a pinning test is the right amount of work.
- The `--effort` flag exists on the real `claude` CLI exactly as claimed (`--effort <low|medium
  |high|xhigh|max>`), so `decision:reasoning-effort-follows-tier`'s settle condition is genuinely
  resolved, not still open.
- Sequencing code (`g1`) before doctrine (`g2`) before verification (`g3`) is the right macro
  order for making `g2`'s doctrine describe real, shipped behavior rather than aspirational
  prose — that ordering claim in the plan holds. It just doesn't, by itself, protect the
  Commander's *own* dispatches during `g1`, which is finding 1 above.
