# Implementer Handoff — g2 attempt 2 (RESUMPTION, narrow)

**Read `IMPLEMENTER_HANDOFF.md` in this same directory FIRST and in full.** It is the governing
handoff: the construction, the positive-control requirement, the three-way attribution, the hard
exclusions, and the stop conditions all still bind unchanged. This file records only what changed.

**Use absolute paths — your shell's cwd resets between bash calls.**

## What happened, and what you are NOT redoing

Attempt 1 **built the harness and it works.** It was killed mid-run by an **account-level weekly
usage limit**, not by any defect in the harness or the fix. The treatment arm's headless log
(`evidence/headless-treatment.log`) reads exactly:

```
EXIT: 1
--- STDOUT ---
You've hit your weekly limit · resets Aug 7, 7am (America/Los_Angeles)
```

**That limit reset at 2026-08-07 07:00 PT. It is now past that.** Re-running is unblocked.

Do **not** rebuild `run_two_arm.py` or `verify_evidence.py`. Do **not** re-derive the construction.
They are correct and already reviewed by the Commander. Your job is to **run the arms to completion**
and close the four open evidence gaps.

## Exactly what is missing — this is your whole scope

`python C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py`
currently exits **1** with **27 PASS and 4 FAIL**. The four:

1. `treatment: 'advance' exit code is non-zero (got None)`
2. `treatment: engine output carries the REFUSED refusal`
3. `treatment: the refusal is the HARD-band message, not some other refusal`
4. `arm-control.json present and parseable`

(1)-(3) are one thing: the treatment subagent **wrote its gauge and then the session was killed
before it reached `advance`**. (4) is the control arm, which never ran at all.

**Your close criterion is precisely: that verifier exits 0 on real, freshly-produced evidence.**

## What attempt 1 already PROVED — carry it, do not doubt it

Do not treat these as open questions; they are measured and on disk. Re-running will reproduce them.

- **`preflight-arms.json`** — a non-agent subprocess drove the engine with a relative `--file` from
  the sandbox main in each arm. Treatment resolved to the **worktree** spine with
  `path_source: "git_worktree"`; control resolved to the **sandbox main** path, which does not exist
  (`spine_present_in_sandbox_main: false`). Both arm trees are complete (both hooks ran, exit 0), so
  neither arm can be silently quiet from a missing sibling import.
- **`arm-diff.txt`** — the recursive `scripts/` tree diff names exactly one differing file,
  `scripts/hooks/spine_rail.py`.
- **Treatment attribution, all three ways, from a real dispatched subagent:**
  composite key `91d573f9-7335-4c92-84fa-d44f8e708151#acbdf9f82f0835f79`;
  `identity_resolution_ms: 0.0774`; `gauge.json` `model: "claude-sonnet-5"` (the subagent) against
  a parent on `opus`.
- **The reading landed in the right place and was over HARD:** `gauge.json` existed **beside the
  worktree spine** at `fill_fraction 0.4066` against a HARD of `0.15` for `claude-sonnet-5`, and the
  phantom path in the sandbox main was **absent**.
- **The live main checkout was untouched** — `.spine-rail-binding.json` byte-identical before/after.

So: on the treatment arm the mechanism is proven end to end **up to but not including the engine's
refusal**. That refusal is the done-condition and it is what you must now observe.

## How to run it

The harness is re-runnable and takes per-arm flags. From the worktree root:

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
python .agent-work/issue-440-binding-cwd/acceptance/run_two_arm.py --arm treatment --filler-count 24 --keep
python .agent-work/issue-440-binding-cwd/acceptance/run_two_arm.py --arm control   --filler-count 24 --keep
```

- **Pass `--filler-count 24`** so the harness does not spend an extra headless launch re-running the
  truncation probe. Attempt 1 already probed it (`evidence/probe.json`, verdict `TRUNCATED`), and
  `probe()` returns the constant `FILLER_COUNT = 24` either way. 24 x 28_000 chars clears the
  150_000-token HARD cap even at a pessimistic 4 chars/token. **Do not lower it** — an under-inflated
  subagent produces a false negative wearing the bug's face.
- **Run the arms one at a time**, treatment first, and check the evidence after each. Each arm is a
  headless run with a subagent deliberately inflating past 150K tokens; they are slow and they cost
  real budget. `ARM_TIMEOUT_S` is 3600.
- **`--keep` leaves the temp tree** at `%TEMP%\acc440` so you can diagnose a quiet arm instead of
  guessing. Clean up at the very end (a final `--keep`-less run is NOT how you clean up — just remove
  the temp tree yourself once the evidence is verified and copied).
- Attempt 1's sandbox from the killed run may still be at `%TEMP%\acc440`. `build_sandbox` rebuilds
  per arm, but **check** that you are reading freshly-written evidence and not a stale file: every
  arm JSON carries `collected_at`, and `verify_evidence.py` already checks `observed_at` against the
  reader's 30-minute freshness window. A gauge from attempt 1 is ~28 hours old and will fail that
  check — which is the behavior you want.

## The budget risk you must manage, and what to do when you hit it

The weekly limit is the thing that killed attempt 1. Treat it as a live hazard:

- **Check every headless run's stdout for a limit message** before you interpret its result. A
  limit-killed arm looks like a quiet arm and would masquerade as "the bug reproduced" — which is
  exactly the failure mode the positive-control requirement exists to catch.
- If you hit the limit again, **stop and report it as an environmental block**, with the exact
  message and which arm was in flight. Do not retry in a loop, do not reduce the inflation budget to
  squeeze under it, and do not report a limit-kill as a measured negative. It is neither a win nor a
  null — it is a blocked run, and saying so plainly is the correct deliverable.
- **Prioritize the CONTROL arm if you can only afford one.** Treatment's mechanism is already
  evidenced up to the refusal; the control arm has **zero** evidence and is the one that makes the
  whole comparison mean anything. If you get exactly one arm, get the control.

## Everything else is unchanged

All exclusions from `IMPLEMENTER_HANDOFF.md` still bind, in particular:

- **Do not modify** `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`,
  `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, or any test. If the run shows the fix is
  wrong, **that is a finding to report**, not a thing to patch.
- **Never hand-inject the value being proved.** The hook must derive the worktree root. Do not put it
  into any payload field, fixture, or env var the hook reads back.
- **Never touch** the live `C:/Programs/constellation-skills` — not its
  `.agent-work/.spine-rail-binding.json`, not its `.claude/settings*.json`, not any real worktree.
- Use `python`, **never** `py`.
- **Cap every dispatched model at Opus or lower and name it explicitly. No Fable at any tier** — the
  user's global default is `fable`, so an unspecified model is a violation.
- **Gate on real exit codes.** Redirect to a file, then echo `$?`. `cmd | tail -5; echo $?` captures
  `tail`'s exit code.
- Do not commit. Scope is everything under `.agent-work/issue-440-binding-cwd/acceptance/` plus temp
  directories.

## Required evidence

`verify_evidence.py` exiting **0**, on evidence you freshly produced, plus its demonstration exiting
non-zero on a deliberately truncated copy (attempt 1 may not have shown that — show it).

Report the treatment arm's `advance` output and its **real** exit code verbatim, and the control
arm's positive miss: a real `gauge.json` with `fill_fraction >= hard` at the **phantom path in the
sandbox main**, with `advance` **succeeding**. If the control produces no gauge anywhere, the run is
**inconclusive, not a pass** — say so and diagnose it against the "Skip-on-uncertainty, enumerated"
section of `docs/GAUGE_WRITER_HOOK.md`.

## Return format

Write `IMPLEMENTER_RESULT` to
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/crew/g2-implement/IMPLEMENTER_RESULT.md`
**before you go idle**, and deliver it as your final message: the plain-English verdict first (did the
trip fire from a worktree-dispatched agent's own reading, yes or no), then evidence produced with
real exit codes, stop conditions hit, out-of-scope observations, and workflow feedback.

**An honest measured negative is a complete deliverable. A limit-blocked run is a blocked run, and
neither of those is a thing to dress up as the other.**
